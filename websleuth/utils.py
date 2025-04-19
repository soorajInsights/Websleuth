import logging
import re
import random
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
    try:
        if not isinstance(text, str):
            log_debug(f"clean_text: Input is not a string: {text}")
            return text
        cleaned = re.sub(r'\s+', ' ', text).strip()
        log_debug(f"clean_text: Cleaned text: {cleaned}")
        return cleaned
    except Exception as e:
        log_error(f"clean_text: Error cleaning text - {e}")
        return text

# List of commonly used browser languages
accept_languages = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.9",
    "fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4",
    "de-DE,de;q=0.9,en;q=0.7",
    "es-ES,es;q=0.9,en;q=0.8",
    "en-IN,en;q=0.9",
    "en-US;q=0.8,en;q=0.7"
]

def get_safe_user_agent():
    """
    Generate a safe user-agent string (desktop only).
    """
    try:
        ua = UserAgent()
        for _ in range(10):  # Avoid infinite loops
            agent = ua.random
            log_debug(f"get_safe_user_agent: Trying agent - {agent}")
            if all(device not in agent for device in ["Mobile", "iPhone", "Android"]):
                log_info(f"get_safe_user_agent: Selected agent - {agent}")
                return agent
        raise ValueError("Couldn't find a desktop user-agent after multiple tries.")
    except Exception as e:
        fallback = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        log_error(f"get_safe_user_agent: Failed to get user agent - {e}. Using fallback: {fallback}")
        return fallback

def get_request_headers():
    """
    Return randomized headers for requests.
    """
    try:
        headers = {
            "User-Agent": get_safe_user_agent(),
            "Accept-Language": random.choice(accept_languages),
            "Referer": "https://www.google.com/"
        }
        log_debug(f"get_request_headers: Generated headers - {headers}")
        return headers
    except Exception as e:
        log_error(f"get_request_headers: Error generating headers - {e}")
        return {}

def get_full_url(base_url, relative_url):
    """
    Join a base URL with a relative URL (e.g., convert /path/image.jpg to full URL).
    """
    try:
        full_url = urljoin(base_url, relative_url)
        log_debug(f"get_full_url: Base - {base_url}, Relative - {relative_url}, Full - {full_url}")
        return full_url
    except Exception as e:
        log_error(f"get_full_url: Error joining URLs - {e}")
        return relative_url

# =============================
# Logging Shortcuts
# =============================

def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)

def log_debug(message):
    logger.debug(message)
