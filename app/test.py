import json
from config import ANYTHING_API_BASE, ANYTHING_API_KEY
import requests
import re
import os

print("Running AnythingLLM API Test...")

url = f"{ANYTHING_API_BASE}/workspace/test/thread/new"
HEADERS_JSON = {
    "Authorization": f"Bearer {ANYTHING_API_KEY}",  
    "accept": "application/json",
}
payload = {
    "name": "new_thread",
    "slug": "12345678910"
}

res = requests.post(url, headers=HEADERS_JSON, json=payload)





