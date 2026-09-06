import requests
import socket
import time
from urllib.parse import urlparse

endpoints = [
    "https://yc-oss.github.io/api/companies/all.json",
    "https://yc-oss.github.io/api/tags/ai.json",
    "https://yc-oss.github.io/api/tags/artificial-intelligence.json",
    "https://yc-oss.github.io/api/tags/generative-ai.json",
    "https://devasheeshg.github.io/yc-api/companies/all.json"
]

def check_endpoint(url):
    print(f"\\n{'='*50}")
    print(f"URL: {url}")
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    # DNS Resolution
    try:
        ip = socket.gethostbyname(hostname)
        print(f"DNS Resolution: SUCCESS ({ip})")
    except Exception as e:
        print(f"DNS Resolution: FAILED ({type(e).__name__}: {e})")
        return
        
    # HTTP Request
    start_time = time.time()
    try:
        res = requests.get(url, timeout=60, headers={'User-Agent': 'Mozilla/5.0'})
        response_time = time.time() - start_time
        print(f"HTTP Status: {res.status_code}")
        print(f"Response Time: {response_time:.2f} seconds")
        print(f"Content-Type: {res.headers.get('Content-Type', 'Unknown')}")
        
        content = res.content
        print(f"Response Size: {len(content)} bytes")
        
        # JSON Parsing
        if res.status_code == 200:
            try:
                data = res.json()
                print("JSON Parsing: SUCCESS")
                
                # Check structure
                if isinstance(data, list):
                    print(f"Records count: {len(data)}")
                    if len(data) > 0:
                        if isinstance(data[0], dict):
                            print(f"First record keys: {list(data[0].keys())}")
                        else:
                            print(f"First record is not a dict: {type(data[0])}")
                elif isinstance(data, dict):
                    print(f"Records count: {len(data)} (keys)")
                    keys_list = list(data.keys())
                    if len(keys_list) > 0:
                        first_val = data[keys_list[0]]
                        if isinstance(first_val, dict):
                            print(f"First record keys: {list(first_val.keys())}")
                        else:
                            print(f"First record is not a dict: {type(first_val)}")
                else:
                    print(f"Root JSON is not list or dict: {type(data)}")
            except Exception as e:
                print(f"JSON Parsing: FAILED ({type(e).__name__}: {e})")
    except Exception as e:
        response_time = time.time() - start_time
        print(f"Request Exception: {type(e).__name__} ({e})")
        print(f"Failed after {response_time:.2f} seconds")

if __name__ == "__main__":
    import os
    os.makedirs('scripts', exist_ok=True)
    for ep in endpoints:
        check_endpoint(ep)
