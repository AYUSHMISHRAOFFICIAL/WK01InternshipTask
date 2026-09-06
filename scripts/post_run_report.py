import json
import csv
import os

def generate_report():
    input_file = 'data/described/described_candidates.json'
    csv_file = 'data/final/ai_companies_sheet.csv'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # data is a dict if it's the checkpoint file from described_map (wait! let's check describe.py)
    # Ah, in describe.py, the checkpoint file is a dict: described_map[domain] = c
    if isinstance(data, dict):
        records = list(data.values())
    else:
        records = data
        
    total_input = 4022
    processed = len(records)
    success = sum(1 for c in records if c.get('description_generated') and c.get('description'))
    failed = sum(1 for c in records if not c.get('description_generated') and c.get('description_error'))
    missing = sum(1 for c in records if not c.get('description') or not c.get('ai_classification'))
    
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        final_rows = list(reader)
        
    validation_failures = 0
    for r in final_rows:
        if not r.get('Company Name') or not r.get('Website URL') or not r.get('Description'):
            validation_failures += 1
            
    print("=== FINAL ENRICHMENT REPORT ===")
    print(f"* 4,022 input records")
    print(f"* processed records in checkpoint: {processed}")
    print(f"* successful descriptions: {success}")
    print(f"* failed records: {failed}")
    print(f"* missing categories/descriptions: {missing}")
    print(f"* validation failures: {validation_failures}")
    print(f"* checkpoint status: {'OK' if os.path.exists(input_file) else 'MISSING'}")
    print(f"* final CSV path: {csv_file}")
    print(f"* final row count: {len(final_rows)}")

if __name__ == '__main__':
    generate_report()
