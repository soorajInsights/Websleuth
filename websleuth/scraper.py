import logging

from .queue import URLQueue
from .parser import CSSParser, XPathParser
from .export import DataExporter

from .middleware import (
    MiddlewareManager,
    LoggingMiddleware,
    ProxyMiddleware,
    RetryMiddleware,
    UserAgentMiddleware,
    AutoThrottleMiddleware
)

class Scraper:
    def __init__(self, parser_type='css', output_file=None):
        self.queue = URLQueue()
        self.parser_type = parser_type
        self.output_file = output_file  # Can be None

        # Setup middleware
        self.middleware_manager = MiddlewareManager([
            UserAgentMiddleware(),
            ProxyMiddleware(),
            LoggingMiddleware(),
            RetryMiddleware()
        ])

        # Auto-inject AutoThrottleMiddleware into RetryMiddleware
        for middleware in self.middleware_manager.middlewares:
            if isinstance(middleware, RetryMiddleware):
                middleware.auto_throttle = AutoThrottleMiddleware()

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def add_url(self, url):
        self.queue.add_url(url)

    def scrape(self, selector):
        results = []

        while self.queue.has_urls():
            url = self.queue.get_next_url()
            try:
                status, html = self.middleware_manager.fetch(url)

                if status == 200 and html:
                    try:
                        if self.parser_type == 'css':
                            parser = CSSParser(html)
                        elif self.parser_type == 'xpath':
                            parser = XPathParser(html)
                        else:
                            raise ValueError(f"Unsupported parser_type: {self.parser_type}. Choose 'css' or 'xpath'.")
                        data = parser.extract(selector)
                        results.extend([{"url": url, "content": item} for item in data])
                    except Exception as parse_error:
                        self.logger.error(f"Error parsing content from {url}: {parse_error}")
                        
                else:
                    self.logger.warning(f"❌ Failed to scrape: {url} (Status: {status})")
            except Exception as fetch_error:
                self.logger.error(f"Error fetching {url}: {fetch_error}")
        
        # Export results using the updated DataExporter
        if results:
            try:
                exporter = DataExporter()
                exporter.export(results, self.output_file)
                self.logger.info(f"Results exported to {self.output_file}")
            except Exception as export_error:
                self.logger.error(f"Error exporting data to {self.output_file}: {export_error}")

        return results
