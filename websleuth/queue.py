from collections import deque

class URLQueue:
    def __init__(self):
        # Set to track URLs that have already been added (avoids duplicates)
        self.visited = set()

        # Deque (double-ended queue) to store URLs to be processed
        self.queue = deque()

    def add_url(self, url):
        """
        Add a URL to the queue if it hasn't been visited yet.
        """
        if url not in self.visited:
            self.queue.append(url)     # Add new URL to the end of the queue
            self.visited.add(url)      # Mark URL as visited

    def get_next_url(self):
        """
        Retrieve and remove the next URL from the front of the queue.
        Returns None if the queue is empty.
        """
        if self.queue:
            return self.queue.popleft()  # Get and remove the next URL
        return None

    def has_urls(self):
        """
        Check if there are any URLs left to process in the queue.
        """
        return len(self.queue) > 0
