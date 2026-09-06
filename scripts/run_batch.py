import json
import os
import time
from src.describe import describe_data
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

def run_batch():
    with open('data/qualified/qualified_candidates.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    qual = [c for c in data if c.get('qualification_status') == 'qualified']
    
    # 1. Verification
    print("--- DATASET VERIFICATION ---")
    print(f"Total qualified records: {len(qual)}")
    domains = [c.get('domain') for c in qual if c.get('domain')]
    dupes = len(domains) - len(set(domains))
    print(f"Duplicate domains: {dupes}")
    print(f"All qualified=True: {all(c.get('qualified') for c in qual)}")
    print(f"All website_verification_status intact: {all(c.get('website_verification_status') for c in qual)}")
    
    if len(qual) != 4022:
        print("ERROR: Expected 4022 records!")
        return

    # 2. Select 20 mixed records
    # Let's get 7 YC, 7 Hackernoon, 6 Github
    yc = [c for c in qual if c.get('source') == 'yc_huggingface_snapshot']
    hn = [c for c in qual if c.get('source') == 'hackernoon_startups']
    gh = [c for c in qual if c.get('source') == 'github']
    
    batch = yc[:7] + hn[:7] + gh[:6]
    
    print(f"\n--- RUNNING GEMINI BATCH ({len(batch)} records) ---")
    # Temporarily remove described_candidates.json if it exists so we start fresh for the 20
    if os.path.exists('data/described/described_candidates.json'):
        os.remove('data/described/described_candidates.json')

    os.environ['GEMINI_MAX_WORKERS'] = '5'
    
    start_time = time.time()
    described_batch = describe_data(batch)
    print(f"Batch completed in {time.time() - start_time:.2f}s")
    
    print("\n--- RESUME CHECK ---")
    start_time2 = time.time()
    described_batch_resume = describe_data(batch)
    print(f"Resume completed in {time.time() - start_time2:.2f}s (should be very fast)")
    
    print("\n--- BATCH RESULTS ---")
    success = sum(1 for c in described_batch if c.get('description_generated'))
    fails = sum(1 for c in described_batch if not c.get('description_generated'))
    classifications = Counter(c.get('ai_classification') for c in described_batch if c.get('ai_classification'))
    
    lengths = [len(str(c.get('description', '')).split()) for c in described_batch if c.get('description_generated')]
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    out_of_bounds = sum(1 for l in lengths if l < 25 or l > 35)
    
    print(f"Successful generations: {success}")
    print(f"Failed generations: {fails}")
    print(f"Classifications: {dict(classifications)}")
    print(f"Average word count: {avg_len:.1f}")
    print(f"Outside 25-35 words: {out_of_bounds}")
    
    print("\n--- GENERATED RECORDS ---")
    for c in described_batch:
        cname = c.get('company_name')
        source = c.get('source')
        desc = c.get('description')
        ai_class = c.get('ai_classification')
        print(f"{cname} | {source} | {ai_class} | {desc}")
        print("-" * 40)

if __name__ == '__main__':
    run_batch()
