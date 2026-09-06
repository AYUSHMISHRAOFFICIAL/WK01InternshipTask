import sys
import os
import json

# Add parent dir to path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extract import discover_yc, discover_startup_datasets, discover_ai_datasets, discover_github

def run_test():
    print("Testing source adapters independently...")
    print(f"{'Source':<25} | {'Records Discovered':<18} | {'Status'}")
    print("-" * 65)
    
    # 1. YC Snapshot
    try:
        yc_records = discover_yc()
        print(f"{'YC Snapshot':<25} | {len(yc_records):<18} | {'Success' if len(yc_records) > 0 else 'Failed'}")
    except Exception as e:
        print(f"{'YC Snapshot':<25} | {'Error':<18} | {str(e)}")

    # 2. HackerNoon
    try:
        hn_records = discover_startup_datasets()
        print(f"{'HackerNoon':<25} | {len(hn_records):<18} | {'Success' if len(hn_records) > 0 else 'Failed'}")
    except Exception as e:
        print(f"{'HackerNoon':<25} | {'Error':<18} | {str(e)}")

    # 3. Crunchbase AI Slice
    try:
        cb_records = discover_ai_datasets()
        print(f"{'Crunchbase AI':<25} | {len(cb_records):<18} | {'Success' if len(cb_records) > 0 else 'Failed'}")
    except Exception as e:
        print(f"{'Crunchbase AI':<25} | {'Error':<18} | {str(e)}")

    # 4. GitHub
    try:
        gh_records = discover_github()
        print(f"{'GitHub (Awesome AI)':<25} | {len(gh_records):<18} | {'Success' if len(gh_records) > 0 else 'Failed'}")
    except Exception as e:
        print(f"{'GitHub (Awesome AI)':<25} | {'Error':<18} | {str(e)}")

if __name__ == '__main__':
    run_test()
