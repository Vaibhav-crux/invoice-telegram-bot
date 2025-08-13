from collections import defaultdict
from time import time

class SessionTracker:
    def __init__(self):
        self.requests = defaultdict(list)

    def add_request(self, user_id: str, max_requests: int, window_seconds: int) -> bool:
        current_time = time()
        # Clean up expired timestamps
        self.requests[user_id] = [t for t in self.requests[user_id] if current_time - t < window_seconds]
        
        # Check if within rate limit
        if len(self.requests[user_id]) >= max_requests:
            return False
        
        # Add new request timestamp
        self.requests[user_id].append(current_time)
        return True