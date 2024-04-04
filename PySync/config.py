from collections import deque
import time

TOKEN_COUNT = 0
TIME_INTERVAL = 0

def set_config(max_count,interval):
    TOKEN_COUNT = max_count
    TIME_INTERVAL = interval

def getconfig():
    return TOKEN_COUNT , TIME_INTERVAL



class RateLimiter:
    def __init__(self, max_requests, per_seconds):
        # print("Rate limiter initializer")
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self.requests_log = deque()

    def allow_request(self):
        if not self.max_requests:
            return True

        current_time = time.time()
        # Remove expired requests from the log
        while self.requests_log and self.requests_log[0] <= current_time - self.per_seconds:
            self.requests_log.popleft()

        if len(self.requests_log) < self.max_requests:
            self.requests_log.append(current_time)
            return True
        else:
            return False

    def get_token(self):
        while True:
            if not self.allow_request():
                time.sleep(0.1)
            else:
                break
        return


TOKEN_COUNT,TIME_INTERVAL =  0,0
# Example Usage:
limiter = RateLimiter(max_requests=TOKEN_COUNT, per_seconds=TIME_INTERVAL)
# print("TOKEN_COUNT ",TOKEN_COUNT)
# print("TIME_INTERVAL ",TIME_INTERVAL)

class default_limiter(object):
    count = 0
    def get_token(self):
        self.count += 1
        return
