# 📦 CHANGELOG

All notable changes to the WebSleuth project will be documented in this file.

---

## [1.0.0] - 2025-04-18

### 🚨 Breaking Changes

- Middleware is no longer auto-loaded — users must define their own middleware stack.
- Scraper now requires explicit `selector=` keyword in `scrape()` method.
- Proxy handling has been refactored to support rotation — old proxy logic is deprecated.
- `AsyncScraper` and `SyncScraper` are now distinct, modular components.
- Removed implicit `output_file` type inference — extensions must now be defined.

---

### ✨ New Features

- ✅ Queue-based URL handling with **duplicate prevention**.
- ✅ Support for both **synchronous and asynchronous scraping**.
- ✅ **Auto-throttling** middleware with adaptive delay control.
- ✅ **Modular middleware stack architecture** with per-request control.
- ✅ Enhanced **proxy rotation** using list or proxy API services.
- ✅ New **Excel export format** (`.xlsx`) support via `DataExporter`.
- ✅ **Configuration management** with persistent state tracking.
- ✅ Improved **logging and error handling** for production use.
- ✅ Fully refactored `MiddlewareManager` for async/sync compatibility.

---

### ✅ Improved

- CSS and XPath parser support is now more stable and configurable.
- Retry logic upgraded with better exponential backoff + jitter.
- Logging middleware now includes timestamps, severity levels, and custom tags.
- ProxyMiddleware now works with both sync and async modes seamlessly.

---

### 🐛 Bug Fixes

- Fixed URL queue not preserving order when adding in async mode.
- Fixed export bug where `.csv` and `.json` output could conflict.
- Addressed race condition in async retry mechanism.
- Improved compatibility with Python 3.11 and 3.12.

---

## [0.1.3] - 2025-03-30

### 🧰 Initial Features

- ✅ Queue-based URL handling
- ✅ CSS & XPath parser support
- ✅ User-Agent rotation using `fake-useragent`
- ✅ Basic proxy support
- ✅ Retry logic with exponential backoff
- ✅ Export to JSON and CSV
- ✅ Basic custom parser middleware support
