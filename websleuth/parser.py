from bs4 import BeautifulSoup
from lxml import html


class CSSParser:
    """
    A parser using CSS selectors with BeautifulSoup.
    """
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, "html.parser")

    def extract(self, selector):
        """
        Extracts text from elements that match the CSS selector.
        """
        return [el.get_text(strip=True) for el in self.soup.select(selector)]

    def extract_links(self):
        """
        Extracts all 'href' links from <a> tags in the page.
        """
        return [a.get("href") for a in self.soup.find_all("a", href=True)]


class XPathParser:
    """
    A parser using XPath selectors with lxml.
    """
    def __init__(self, html_content):
        self.tree = html.fromstring(html_content)

    def extract(self, xpath_query):
        """
        Extracts text or attributes from elements that match the XPath query.
        """
        return self.tree.xpath(xpath_query)