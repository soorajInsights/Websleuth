from collections import deque

class URLQueue:
    def __init__(self):
        try:
            # Set to track URLs that have already been added (avoids duplicates)
            self.visited = set()

            # Deque (double-ended queue) to store URLs to be processed
            self.queue = deque()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize URLQueue: {e}")

    def add_url(self, url):
        """
        Add a URL to the queue if it hasn't been visited yet.
        """
        try:
            if url not in self.visited:
                self.queue.append(url)     # Add new URL to the end of the queue
                self.visited.add(url)      # Mark URL as visited
        except Exception as e:
            raise RuntimeError(f"Failed to add URL '{url}': {e}")

    def get_next_url(self):
        """
        Retrieve and remove the next URL from the front of the queue.
        Returns None if the queue is empty.
        """
        try:
            if self.queue:
                return self.queue.popleft()  # Get and remove the next URL
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to get next URL: {e}")

    def has_urls(self):
        """
        Check if there are any URLs left to process in the queue.
        """
        try:
            return len(self.queue) > 0
        except Exception as e:
            raise RuntimeError(f"Failed to check queue status: {e}")
