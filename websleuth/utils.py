import logging
import re
from fake_useragent import UserAgent
from urllib.parse import urljoin

# =============================
# Logger Setup
# =============================

logging.basicConfig(
    level=logging.INFO,
    format="🕵️ [%(levelname)s] %(message)s"
)

logger = logging.getLogger("WebSleuth")

# =============================
# Helper Functions
# =============================

def clean_text(text):
    """
    Clean up extra whitespace and newlines in scraped text.
    """
    if not isinstance(text, str):
        return text
    return re.sub(r'\s+', ' ', text).strip()

def get_random_user_agent():
    """
    Return a random user-agent string using fake_useragent.
    """
    try:
        return UserAgent().random
    except Exception:
        # Fallback if user-agent service fails
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)

def get_full_url(base_url, relative_url):
    """
    Join a base URL with a relative URL (e.g., convert /path/image.jpg to full URL).
    """
    return urljoin(base_url, relative_url)
