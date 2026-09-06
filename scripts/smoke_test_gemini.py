import json
import os
from dotenv import load_dotenv
load_dotenv()
from src.describe import describe_data
from src.validate import validate_data

def run_smoke_test():
    print("Loading qualified candidates...")
    with open('data/qualified/qualified_candidates.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    qualified = [c for c in data if c.get('qualification_status') == 'qualified']
    print(f"Total qualified candidates: {len(qualified)}")
    
    print("\n--- RUNNING GEMINI SMOKE TEST (5 RECORDS) ---")
    described = describe_data(qualified, smoke_test=True)
    
    # describe_data returns the list of all passed-in candidates (which was sliced to 5 internally if smoke_test=True)
    # wait, in my implementation `candidates = candidates[:5]`. So it returns 5.
    
    print("\n--- SMOKE TEST RESULTS ---")
    for i, c in enumerate(described):
        print(f"\nRecord {i+1}:")
        print(f"Company: {c.get('company_name')}")
        # The original description might be overwritten if we didn't preserve it. 
        # Wait, in describe.py I overwrote `c['description'] = result['description']`!
        # The instruction said: "For existing descriptions: old source description -> Gemini grounding context -> new standardized description. Do NOT use: company_name -> hallucinated description"
        # I did pass it to the prompt: `Existing source description: {c.get('description', '')}`
        # Then I overwrote `c['description'] = ...`. That perfectly matches the instruction to use it as grounding and update to standardized description.
        print(f"Generated description: {c.get('description')}")
        print(f"AI classification: {c.get('ai_classification')}")
        print(f"Generated Flag: {c.get('description_generated')}")
        print(f"Error: {c.get('description_error')}")
        print(f"Domain preserved: {c.get('domain')}")
        
    valid = validate_data(described, final_export=True)
    print(f"\nFinal Validation passed: {len(valid)} / {len(described)}")
    
    print(f"\nCheckpoint created: {os.path.exists('data/described/described_candidates.json')}")

if __name__ == '__main__':
    run_smoke_test()
