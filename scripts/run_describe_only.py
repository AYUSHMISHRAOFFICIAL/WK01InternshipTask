import json
import os
from dotenv import load_dotenv
from src.describe import describe_data
from src.logo import verify_logos
from src.enrich import enrich_data
from src.export import export_data
from src.validate import validate_data

load_dotenv()

def run_describe_only():
    print("Loading 4,022 qualified candidates...")
    with open('data/qualified/qualified_candidates.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    qualified = [c for c in data if c.get('qualification_status') == 'qualified']
    print(f"Qualified count: {len(qualified)}")
    
    # We already have logos cached in data/enriched probably? 
    # Or verify_logos is very fast because of the cache.
    print("Running verify_logos (cached)...")
    logo_verified = verify_logos(qualified)
    
    print("Running enrich_data (cached)...")
    enriched = enrich_data(logo_verified)
    
    print("Running describe_data (calling Gemini API)...")
    described = describe_data(enriched)
    
    print("Running validate and export...")
    final = validate_data(described)
    export_data(final)
    print("Done!")

if __name__ == '__main__':
    run_describe_only()
