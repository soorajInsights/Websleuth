import requests
from .queue import URLQueue
from .parser import CSSParser, XPathParser
from .export import CSVExporter, JSONExporter
from .utils import get_random_user_agent

class Scraper:
    def __init__(self, parser_type='css', export_type='csv', output_file='output'):
        self.queue = URLQueue()
        self.parser = CSSParser() if parser_type == 'css' else XPathParser()
        self.exporter = CSVExporter(output_file + '.csv') if export_type == 'csv' else JSONExporter(output_file + '.json')

    def add_url(self, url):
        self.queue.add_url(url)

    def scrape(self, selector):
        while not self.queue.is_empty():
            url = self.queue.get_url()
            print(f"Scraping: {url}")

            try:
                headers = {'User-Agent': get_random_user_agent()}
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = self.parser.parse(response.text, selector)
                    self.exporter.export(data)
                else:
                    print(f"Failed to fetch {url} — Status Code: {response.status_code}")
            except Exception as e:
                print(f"Error scraping {url}: {e}")
