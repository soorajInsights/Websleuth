import time
import random
import requests
from fake_useragent import UserAgent
from websleuth.utils import log_info, log_error


class MiddlewareManager:
    def __init__(self, middlewares=None):
        self.middlewares = middlewares or []
        self.retry_middleware = next(
            (mw for mw in self.middlewares if isinstance(mw, RetryMiddleware)), None
        )

    def apply_middlewares(self, url):
        request_data = {"url": url, "headers": {}}
        for middleware in self.middlewares:
            if hasattr(middleware, "process_request"):
                request_data = middleware.process_request(request_data)
        return request_data

    def send_request(self, url):
        request_data = self.apply_middlewares(url)

        if self.retry_middleware:
            response = self.retry_middleware.request_with_retry(request_data)
        else:
            try:
                response = requests.get(
                    request_data["url"],
                    headers=request_data.get("headers", {}),
                    proxies=request_data.get("proxies"),
                    timeout=10
                )
                response.raise_for_status()
            except Exception as e:
                log_error(f"Request failed: {e}")
                response = None

        for middleware in self.middlewares:
            if hasattr(middleware, "process_response"):
                response = middleware.process_response(response, request_data)

        return response


class RetryMiddleware:
    def __init__(self, retries=3, delay=2):
        self.retries = retries
        self.delay = delay

    def process_request(self, request_data):
        return request_data

    def request_with_retry(self, request_data):
        for attempt in range(1, self.retries + 1):
            try:
                response = requests.get(
                    request_data["url"],
                    headers=request_data.get("headers", {}),
                    timeout=10,
                    proxies=request_data.get("proxies")
                )
                response.raise_for_status()
                return response
            except Exception as e:
                log_error(f"Attempt {attempt} failed for {request_data['url']}: {e}")
                time.sleep(self.delay)
        return None


class UserAgentMiddleware:
    def __init__(self):
        self.ua = UserAgent()

    def process_request(self, request_data):
        request_data["headers"]["User-Agent"] = self.ua.random
        return request_data


class ProxyMiddleware:
    def __init__(self, proxy_list=None):
        self.proxy_list = proxy_list or []

    def process_request(self, request_data):
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            request_data["proxies"] = {"http": proxy, "https": proxy}
            log_info(f"Using proxy: {proxy}")
        return request_data


class LoggingMiddleware:
    def process_request(self, request_data):
        url = request_data.get("url")
        headers = request_data.get("headers", {})
        user_agent = headers.get("User-Agent", "N/A")
        proxy = request_data.get("proxies", {}).get("http", "N/A")

        log_info(f"🌐 Sending request to: {url}")
        log_info(f"🧠 User-Agent: {user_agent}")
        log_info(f"🕵️‍♂️ Proxy: {proxy}")
        return request_data

    def process_response(self, response, request_data):
        url = request_data.get("url")
        if response:
            log_info(f"✅ Received {response.status_code} from {url}")
        else:
            log_error(f"❌ Failed to get response from {url}")
        return response
