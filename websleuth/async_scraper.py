import asyncio
import logging
from .queue import URLQueue
from .parser import CSSParser, XPathParser
from .async_middleware import (
    AsyncMiddlewareManager,
    AsyncRetryMiddleware,
    AsyncAutoThrottleMiddleware
)
from .middleware import UserAgentMiddleware, ProxyMiddleware, LoggingMiddleware
from .export import AsyncDataExporter  

class AsyncScraper:
    def __init__(self, parser_type='css', output_file=None, concurrency=5):
        self.queue = URLQueue()
        self.parser_type = parser_type
        self.output_file = output_file  # Can be None
        self.concurrency = concurrency

        # Throttle middleware instance
        self.auto_throttle = AsyncAutoThrottleMiddleware()

        # Middleware setup
        self.middleware_manager = AsyncMiddlewareManager([
            UserAgentMiddleware(),
            ProxyMiddleware(),
            LoggingMiddleware(),
            AsyncRetryMiddleware(auto_throttle=self.auto_throttle)
        ])

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def add_url(self, url):
        self.queue.add_url(url)

    def add_urls(self, urls):
        for url in urls:
            self.queue.add_url(url)

    async def _scrape_url(self, url, selector):
        try:
            status, html = await self.middleware_manager.fetch(url)
            
            if status == 200 and html:
                try:
                    parser = CSSParser(html) if self.parser_type == 'css' else XPathParser(html)
                    data = parser.extract(selector)
                    return [{"url": url, "content": item} for item in data]
                except Exception as parse_error:
                    self.logger.error(f"Error parsing content from {url}: {parse_error}")
                    return []
            else:
                self.logger.warning(f"❌ Failed to scrape: {url} (Status: {status})")
                return []
        except Exception as fetch_error:
            self.logger.error(f"Error fetching {url}: {fetch_error}")
            return []

    async def scrape(self, selector):
        results = []

        while self.queue.has_urls():
            batch = []
            while len(batch) < self.concurrency and self.queue.has_urls():
                url = self.queue.get_next_url()
                if url:
                    batch.append(self._scrape_url(url, selector))

            if batch:
                try:
                    batch_results = await asyncio.gather(*batch)
                    for items in batch_results:
                        results.extend(items)
                except Exception as batch_error:
                    self.logger.error(f"Error in scraping batch: {batch_error}")

        if results:
            try:
                exporter = AsyncDataExporter()
                await exporter.export(results, self.output_file)
                self.logger.info(f"Results exported to {self.output_file}")
            except Exception as export_error:
                self.logger.error(f"Error exporting data to {self.output_file}: {export_error}")

        return results
