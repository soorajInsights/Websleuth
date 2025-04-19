import aiohttp
import asyncio
from websleuth.middleware import LoggingMiddleware, UserAgentMiddleware, ProxyMiddleware
from websleuth.shared_utils import (
    BaseThrottleMixin,
    ConfigManager,
    save_throttle_state,
    load_throttle_state,
    ExponentialBackoffHelper,
)

class AsyncAutoThrottleMiddleware(BaseThrottleMixin):
    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        self.config = config or ConfigManager()
        self.state_file = self.config.get_state_file("async_throttle_state.json")
        self.response_times, self.current_delay = load_throttle_state(
            self.state_file, self.base_delay, self.window_size
        )

    async def before_request(self):
        print(f"[Async Throttle] Sleeping for {self.current_delay:.2f} seconds...")
        await asyncio.sleep(self.current_delay)

    async def after_response(self, response_time, success=True):
        self.update_throttle(response_time, success)
        save_throttle_state(self.state_file, {
            "response_times": list(self.response_times),
            "current_delay": self.current_delay
        })


class AsyncRetryMiddleware:
    def __init__(self, auto_throttle=None, retries=3, retry_statuses=None, backoff_factor=1, timeout=10):
        self.auto_throttle = auto_throttle
        self.retries = retries
        self.retry_statuses = retry_statuses or [429, 500, 502, 503]
        self.timeout = timeout
        self.backoff = ExponentialBackoffHelper(backoff_factor)

    async def fetch_with_retries(self, session, url, headers=None, proxy=None):
        headers = headers or {}

        for attempt in range(1, self.retries + 1):
            start_time = asyncio.get_event_loop().time()
            try:
                if self.auto_throttle:
                    await self.auto_throttle.before_request()

                async with session.get(url, headers=headers, proxy=proxy, timeout=self.timeout) as resp:
                    response_time = asyncio.get_event_loop().time() - start_time

                    if resp.status not in self.retry_statuses:
                        if self.auto_throttle:
                            await self.auto_throttle.after_response(response_time, success=True)
                        return resp.status, await resp.text()

                    print(f"⚠️ Status {resp.status} for {url} (Attempt {attempt})")
                    if self.auto_throttle:
                        await self.auto_throttle.after_response(response_time, success=False)

            except aiohttp.ClientError as e:
                response_time = asyncio.get_event_loop().time() - start_time
                print(f"❌ Request failed (Attempt {attempt}): {e}")
                if self.auto_throttle:
                    await self.auto_throttle.after_response(response_time, success=False)

            except asyncio.TimeoutError as e:
                response_time = asyncio.get_event_loop().time() - start_time
                print(f"❌ Request timed out (Attempt {attempt}): {e}")
                if self.auto_throttle:
                    await self.auto_throttle.after_response(response_time, success=False)

            except Exception as e:
                response_time = asyncio.get_event_loop().time() - start_time
                print(f"❌ Unexpected error occurred (Attempt {attempt}): {e}")
                if self.auto_throttle:
                    await self.auto_throttle.after_response(response_time, success=False)

            wait_time = self.backoff.get_backoff_time(attempt)
            print(f"⏳ Waiting {wait_time}s before retrying...")
            await asyncio.sleep(wait_time)

        return None, None


class AsyncMiddlewareManager:
    def __init__(self, middlewares=None):
        self.middlewares = middlewares or []

        retry = next((m for m in self.middlewares if isinstance(m, AsyncRetryMiddleware)), None)
        throttle = next((m for m in self.middlewares if isinstance(m, AsyncAutoThrottleMiddleware)), None)
        if retry and throttle and retry.auto_throttle is None:
            retry.auto_throttle = throttle

    async def fetch(self, url):
        headers = {}
        proxy = None
        retry_middleware = None

        for middleware in self.middlewares:
            if isinstance(middleware, UserAgentMiddleware):
                headers['User-Agent'] = middleware.user_agent
            elif isinstance(middleware, ProxyMiddleware):
                proxy = middleware.get_random_proxy()
            elif isinstance(middleware, AsyncRetryMiddleware):
                retry_middleware = middleware

        for m in self.middlewares:
            if isinstance(m, LoggingMiddleware):
                m.log_request(url, headers.get("User-Agent"), proxy)

        async with aiohttp.ClientSession() as session:
            if retry_middleware:
                return await retry_middleware.fetch_with_retries(session, url, headers, proxy)

            try:
                async with session.get(url, headers=headers, proxy=proxy, timeout=10) as resp:
                    return resp.status, await resp.text()
            except aiohttp.ClientError as e:
                print(f"[!] Error fetching {url}: {e}")
                return None, None
            except asyncio.TimeoutError as e:
                print(f"[!] Timeout error fetching {url}: {e}")
                return None, None
            except Exception as e:
                print(f"[!] Unexpected error fetching {url}: {e}")
                return None, None
