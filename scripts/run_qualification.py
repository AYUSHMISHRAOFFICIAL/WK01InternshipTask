import json
import os
from src.qualify import qualify_data

def run_qualification_only():
    print("Loading verified candidates...")
    with open('data/verified/verified_candidates.json', 'r', encoding='utf-8') as f:
        verified = json.load(f)
    
    # Check old qualified count
    old_qualified_count = 0
    if os.path.exists('data/qualified/qualified_candidates.json'):
        with open('data/qualified/qualified_candidates.json', 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            old_qualified_count = len([c for c in old_data if c.get('qualification_status') == 'qualified'])
            
    print(f"Old qualified count: {old_qualified_count}")
            
    print("Running qualification logic...")
    results = qualify_data(verified)
    
    new_qualified = [c for c in results if c.get('qualification_status') == 'qualified']
    new_rejected = [c for c in results if c.get('qualification_status') == 'rejected']
    new_needs_review = [c for c in results if c.get('qualification_status') == 'needs_review']
    
    print(f"New qualified count: {len(new_qualified)}")
    print(f"New rejected count: {len(new_rejected)}")
    print(f"New needs_review count: {len(new_needs_review)}")
    
if __name__ == '__main__':
    run_qualification_only()
