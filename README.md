# 🕵️ WebSleuth

**WebSleuth** is a lightweight, developer-first Python library that simplifies web scraping. It wraps around common scraping tools like `requests`, `BeautifulSoup`, and `lxml` — adding support for proxy rotation, retry logic, async workflows, and data export — all in a customizable and modular way.

[![PyPI version](https://badge.fury.io/py/websleuth.svg)](https://pypi.org/project/websleuth/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Features

- ✅ Queue-based URL handling with duplicate prevention
- ✅ CSS & XPath parser support
- ✅ User-Agent rotation using `fake-useragent`
- ✅ Proxy rotation with support for list or external APIs
- ✅ Retry logic with exponential backoff
- ✅ Auto-throttling with adaptive delay
- ✅ Synchronous and asynchronous scraping support
- ✅ Export to JSON, CSV, and Excel formats
- ✅ Modular middleware stack architecture
- ✅ Comprehensive logging and error handling
- ✅ Configuration management with persistent state

---

## 📦 Installation

```bash
pip install websleuth
```

## 🧰 Quick Start

### Synchronous Scraping

```python
from websleuth import Scraper

# Initialize a scraper with CSS selectors
scraper = Scraper(parser_type='css', output_file='results.json')

# Add URLs to scrape
scraper.add_url('https://example.com')

# Scrape for data using a CSS selector
results = scraper.scrape('h1')
```

### Asynchronous Scraping

```python
import asyncio
from websleuth import AsyncScraper

async def main():
    # Initialize an async scraper with 5 concurrent requests
    scraper = AsyncScraper(parser_type='css', output_file='results.json', concurrency=5)
    
    # Add multiple URLs to scrape
    scraper.add_urls(['https://example.com', 'https://example.org'])
    
    # Scrape data asynchronously using a CSS selector
    results = await scraper.scrape('h1')
    
    return results

# Run the async scraper
results = asyncio.run(main())
```

## 📚 Documentation

### Core Components

- **URLQueue**: Manages URLs to be scraped with duplicate prevention
- **Parsers**: CSS selectors (BeautifulSoup) and XPath (lxml) support
- **Middleware**: Modular components for request/response handling
- **Exporters**: Data export to JSON, CSV, and Excel formats

### Middleware Components

- **UserAgentMiddleware**: Rotates user agents for each request
- **ProxyMiddleware**: Manages proxy rotation
- **LoggingMiddleware**: Comprehensive request/response logging
- **RetryMiddleware**: Implements retry logic with backoff
- **AutoThrottleMiddleware**: Adaptive request throttling
- **AsyncMiddlewareManager**: Asynchronous middleware processing

### Advanced Usage

#### Customizing Middleware

```python
from websleuth import Scraper
from websleuth.middleware import (
    UserAgentMiddleware,
    ProxyMiddleware,
    LoggingMiddleware,
    RetryMiddleware,
    AutoThrottleMiddleware,
    MiddlewareManager
)

# Create custom middleware stack
middlewares = [
    UserAgentMiddleware(),
    ProxyMiddleware(proxy_list=["http://proxy1.example.com", "http://proxy2.example.com"]),
    LoggingMiddleware(),
    RetryMiddleware(max_retries=5, backoff_factor=2)
]

# Create middleware manager
middleware_manager = MiddlewareManager(middlewares)

# Create scraper with custom middleware manager
scraper = Scraper(parser_type='css')
scraper.middleware_manager = middleware_manager
```

#### Extract Links

```python
from websleuth import Scraper
from websleuth.parser import CSSParser

# Initialize scraper and fetch page
scraper = Scraper()
status, html = scraper.middleware_manager.fetch('https://example.com')

# Extract all links from the page
if status == 200 and html:
    parser = CSSParser(html)
    all_links = parser.extract_links()
    for link in all_links:
        scraper.add_url(link)  # Add discovered links to the queue
```

#### Async Export Example

```python
import asyncio
from websleuth.export import AsyncDataExporter

async def export_data(results):
    async with AsyncDataExporter() as exporter:
        # Export to different formats
        await exporter.export(results, "data.json")  # JSON
        await exporter.export(results, "data.csv")   # CSV
        await exporter.export(results, "data.xlsx")  # Excel

# Export data asynchronously
asyncio.run(export_data(results))
```

## 🛠️ Configuration

WebSleuth supports persistent configuration through a `ConfigManager` that stores settings between sessions.

```python
from websleuth import Scraper
from websleuth.shared_utils import ConfigManager

# Custom configuration directory
config = ConfigManager(config_dir="./my_config")

# Create auto-throttle middleware with custom config
from websleuth.middleware import AutoThrottleMiddleware
throttle = AutoThrottleMiddleware(
    config=config,
    base_delay=1.5,     # Base delay between requests (seconds)
    max_delay=15,       # Maximum delay cap (seconds)
    window_size=10      # Number of requests to consider for average
)
```

## 🔧 Throttling & Backoff

WebSleuth includes smart throttling to avoid server overload and respect rate limits:

```python
from websleuth.shared_utils import ExponentialBackoffHelper

# Create a custom backoff helper
backoff = ExponentialBackoffHelper(backoff_factor=2)

# Get backoff time for each attempt
wait_time = backoff.get_backoff_time(attempt=1)  # 2 seconds
wait_time = backoff.get_backoff_time(attempt=2)  # 4 seconds
wait_time = backoff.get_backoff_time(attempt=3)  # 8 seconds
```

The auto-throttling mechanism automatically adjusts request delays based on response times and success rates, ensuring respectful scraping.

## 📋 Dependencies

- `requests` - HTTP requests for synchronous scraping
- `aiohttp` - Asynchronous HTTP requests
- `beautifulsoup4` - HTML parsing with CSS selectors
- `lxml` - Fast HTML parsing with XPath support
- `fake-useragent` - User agent rotation
- `openpyxl` - Excel file export
- `aiofiles` - Asynchronous file operations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.