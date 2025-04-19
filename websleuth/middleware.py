import time
import random
import requests
from collections import deque
from websleuth.utils import log_info, log_error, get_safe_user_agent
from websleuth.shared_utils import (
    BaseThrottleMixin,
    ConfigManager,
    save_throttle_state,
    load_throttle_state,
    ExponentialBackoffHelper,
)

# ========== COMMON MIDDLEWARE CLASSES ==========

class UserAgentMiddleware:
    def __init__(self):
        self.user_agent = get_safe_user_agent()

    def process_request(self, request_data):
        request_data["headers"]["User-Agent"] = self.user_agent
        return request_data


class ProxyMiddleware:
    def __init__(self, proxy_list=None, proxy_api=None):
        self.proxy_list = proxy_list or []
        self.proxy_api = proxy_api

    def get_random_proxy(self):
        if self.proxy_list:
            return random.choice(self.proxy_list)
        elif self.proxy_api:
            try:
                response = requests.get(self.proxy_api, timeout=5)
                response.raise_for_status()
                proxy = response.text.strip()
                log_info(f"[ProxyMiddleware] Got proxy from API: {proxy}")
                return proxy
            except requests.exceptions.RequestException as e:
                log_error(f"❌ [Proxy API Error] {e}")
        return None

    def process_request(self, request_data):
        proxy = self.get_random_proxy()
        if proxy:
            request_data["proxies"] = {"http": proxy, "https": proxy}
            log_info(f"🕵️‍♂️ Proxy: {proxy}")
        else:
            log_info("🕵️‍♂️ Proxy: None")
        return request_data


class LoggingMiddleware:
    def process_request(self, request_data):
        return self._log_request(request_data)

    def process_response(self, response, request_data):
        url = request_data.get("url")
        if response:
            log_info(f"✅ Received {response.status_code} from {url}")
        else:
            log_error(f"❌ Failed to get response from {url}")
        return response

    def log_request(self, url, user_agent="N/A", proxy="N/A"):
        log_info(f"🌐 Sending request to: {url}")
        log_info(f"🧠 User-Agent: {user_agent}")
        log_info(f"🕵️‍♂️ Proxy: {proxy}")

    def _log_request(self, request_data):
        url = request_data.get("url")
        headers = request_data.get("headers", {})
        user_agent = headers.get("User-Agent", "N/A")
        proxy = request_data.get("proxies", {}).get("http", "N/A")
        self.log_request(url, user_agent, proxy)
        return request_data


# ========== THROTTLING AND RETRY ==========

class AutoThrottleMiddleware(BaseThrottleMixin):
    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        self.config = config or ConfigManager()
        self.state_file = self.config.get_state_file("throttle_state.json")
        self.response_times, self.current_delay = load_throttle_state(
            self.state_file, self.base_delay, self.window_size
        )

    def before_request(self):
        print(f"[Throttle] Sleeping for {self.current_delay:.2f} seconds...")
        time.sleep(self.current_delay)

    def after_response(self, response_time, success=True):
        self.update_throttle(response_time, success)
        save_throttle_state(self.state_file, {
            "response_times": list(self.response_times),
            "current_delay": self.current_delay
        })


class RetryMiddleware:
    def __init__(self, auto_throttle=None, max_retries=3, backoff_factor=1):
        self.max_retries = max_retries
        self.auto_throttle = auto_throttle
        self.backoff = ExponentialBackoffHelper(backoff_factor)

    def send_with_retries(self, request_func, *args, **kwargs):
        retries = 0
        while retries <= self.max_retries:
            start = time.time()
            try:
                if self.auto_throttle:
                    self.auto_throttle.before_request()

                response = request_func(*args, **kwargs)
                response.raise_for_status()
                response_time = time.time() - start

                if response.status_code == 200:
                    if self.auto_throttle:
                        self.auto_throttle.after_response(response_time, success=True)
                    return response
                else:
                    raise Exception(f"Bad status code: {response.status_code}")

            except requests.exceptions.RequestException as e:
                response_time = time.time() - start
                retries += 1
                log_error(f"[RetryMiddleware] Retry {retries}/{self.max_retries}: {e}")
                if self.auto_throttle:
                    self.auto_throttle.after_response(response_time, success=False)

                wait_time = self.backoff.get_backoff_time(retries)
                time.sleep(wait_time)

        return None


# ========== MIDDLEWARE MANAGER ==========

class MiddlewareManager:
    def __init__(self, middlewares=None):
        self.middlewares = middlewares or []

        self.retry_middleware = next(
            (mw for mw in self.middlewares if isinstance(mw, RetryMiddleware)), None
        )

        if self.retry_middleware and self.retry_middleware.auto_throttle is None:
            log_info("⚙️ Auto-injecting AutoThrottleMiddleware into RetryMiddleware")
            self.retry_middleware.auto_throttle = AutoThrottleMiddleware()

    def apply_middlewares(self, url):
        request_data = {"url": url, "headers": {}}
        for middleware in self.middlewares:
            if hasattr(middleware, "process_request"):
                try:
                    request_data = middleware.process_request(request_data)
                except Exception as e:
                    log_error(f"[Middleware Error] {e}")
        return request_data

    def send_request(self, url):
        request_data = self.apply_middlewares(url)

        if self.retry_middleware:
            try:
                response = self.retry_middleware.send_with_retries(
                    requests.get,
                    request_data["url"],
                    headers=request_data.get("headers", {}),
                    proxies=request_data.get("proxies"),
                    timeout=10
                )
            except Exception as e:
                log_error(f"❌ Request failed: {e}")
                response = None
        else:
            try:
                response = requests.get(
                    request_data["url"],
                    headers=request_data.get("headers", {}),
                    proxies=request_data.get("proxies"),
                    timeout=10
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                log_error(f"❌ Request failed: {e}")
                response = None

        for middleware in self.middlewares:
            if hasattr(middleware, "process_response"):
                try:
                    response = middleware.process_response(response, request_data)
                except Exception as e:
                    log_error(f"[Middleware Error] {e}")

        return response
    
    def fetch(self, url):
        response = self.send_request(url)
        if response:
            return response.status_code, response.text
        return None, None
