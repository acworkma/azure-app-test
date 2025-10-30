# locustfile.py
from locust import HttpUser, task, between, events
import os
import random

# Tip: Override the host at runtime with: --host https://www.microsoft.com
DEFAULT_HOST = "https://www.microsoft.com"

# Optional: common headers so the request looks like a normal browser
COMMON_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
}

# Optional: basic response checks and a demo metric
@events.request.add_listener
def _(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    # Add a simple success/failure tag for quick demo commentary
    if exception:
        response_success = 0
    else:
        response_success = 1
    # (You could push custom stats or logs here if desired.)

class MicrosoftSiteUser(HttpUser):
    """
    Simple Locust user that:
      - GETs the Microsoft.com homepage
      - Optionally hits a couple of lightweight secondary endpoints
    """
    wait_time = between(1, 3)
    host = os.getenv("LOCUST_HOST", DEFAULT_HOST)
    stop_timeout = 5

    demo_paths = [
        "/",                       # homepage
        "/en-us",                  # US locale
        "/en-us/microsoft-365",    # M365 landing
        "/en-us/windows",          # Windows landing
        "/en-us/edge",             # Edge landing
    ]

    @task(5)
    def get_homepage(self):
        with self.client.get("/", headers=COMMON_HEADERS, name="GET /", timeout=15, catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"Unexpected status {resp.status_code}")
            elif b"<html" not in resp.content[:200].lower():
                resp.failure("Response did not look like HTML")
            else:
                resp.success()

    @task(3)
    def get_secondary_pages(self):
        path = random.choice(self.demo_paths[1:])  # avoid hitting "/" twice
        self.client.get(path, headers=COMMON_HEADERS, name=f"GET {path}", timeout=15)