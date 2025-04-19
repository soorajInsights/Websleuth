import json
import os
from collections import deque
from pathlib import Path

DEFAULT_CONFIG_DIR = Path.home() / ".websleuth"
DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

class ConfigManager:
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else DEFAULT_CONFIG_DIR
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_state_file(self, name):
        return self.config_dir / name

def save_throttle_state(file_path, data):
    try:
        with open(file_path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"[!] Failed to save throttle state: {e}")

def load_throttle_state(file_path, default_delay, window_size):
    response_times = deque(maxlen=window_size)
    current_delay = default_delay
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                state = json.load(f)
                response_times = deque(state.get("response_times", []), maxlen=window_size)
                current_delay = state.get("current_delay", default_delay)
        except Exception as e:
            print(f"[!] Failed to load throttle state: {e}")
    return response_times, current_delay

class ExponentialBackoffHelper:
    def __init__(self, backoff_factor=1):
        self.backoff_factor = backoff_factor

    def get_backoff_time(self, attempt):
        return self.backoff_factor * 2 ** (attempt - 1)


# base_throttle.py
import random
from collections import deque

class BaseThrottleMixin:
    def __init__(self, base_delay=1, max_delay=10, window_size=5):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.window_size = window_size
        self.response_times = deque(maxlen=window_size)
        self.current_delay = base_delay
        self.retry_attempts = 0

    def update_throttle(self, response_time, success=True):
        if success:
            self.response_times.append(response_time)
            avg = sum(self.response_times) / len(self.response_times)
            self.current_delay = min(self.max_delay, avg + random.uniform(0.1, 0.5))
            self.retry_attempts = 0
        else:
            self.retry_attempts += 1
            self.current_delay = min(
                self.max_delay,
                self.current_delay * (2 ** self.retry_attempts) + random.uniform(0.5, 1.5)
            )
