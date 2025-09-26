"""
Rate limiting utilities for API calls
"""

import time
# from typing import Dict, Optional  # Unused imports
from threading import Lock


class RateLimiter:
    """Simple rate limiter for API calls"""

    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = Lock()

    def can_call(self) -> bool:
        """Check if we can make a call now"""
        with self.lock:
            now = time.time()
            # Remove old calls outside time window
            self.calls = [
                call_time
                for call_time in self.calls
                if now - call_time < self.time_window
            ]

            return len(self.calls) < self.max_calls

    def record_call(self):
        """Record a call"""
        with self.lock:
            self.calls.append(time.time())

    def wait_if_needed(self):
        """Wait if rate limit is exceeded"""
        if not self.can_call():
            # Calculate wait time
            oldest_call = min(self.calls)
            wait_time = self.time_window - (time.time() - oldest_call)
            if wait_time > 0:
                time.sleep(wait_time)


# Global rate limiters
openai_limiter = RateLimiter(
    max_calls=60, time_window=60.0
)  # 60 calls per minute
bybit_limiter = RateLimiter(
    max_calls=120, time_window=60.0
)  # 120 calls per minute
