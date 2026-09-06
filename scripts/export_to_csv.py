import json
import csv
import os

def write_csv(data, csv_file_path):
    if not data:
        return
        
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())
        
    priority_keys = ['company_name', 'domain', 'description', 'source', 'source_url', 'website_verification_status', 'qualification_status']
    other_keys = sorted([k for k in all_keys if k not in priority_keys])
    header = priority_keys + other_keys
    
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=header, extrasaction='ignore')
        writer.writeheader()
        
        for item in data:
            row = {}
            for k, v in item.items():
                if isinstance(v, str):
                    row[k] = v.replace('\n', ' ').replace('\r', ' ')
                elif isinstance(v, list):
                    row[k] = ', '.join(str(i) for i in v)
                else:
                    row[k] = v
            writer.writerow(row)
    print(f"Successfully generated {csv_file_path} with {len(data)} records.")

def json_to_csv(json_file_path):
    print(f"Loading {json_file_path}...")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if not data:
        print("No data found.")
        return
        
    print(f"Found {len(data)} total records.")
    
    # 1. Write Full Data
    write_csv(data, 'data/ai_companies_collected_full.csv')
    
    # 2. Write Qualified Only
    qualified_data = [c for c in data if c.get('qualification_status') == 'qualified']
    write_csv(qualified_data, 'data/ai_companies_qualified_only.csv')

if __name__ == '__main__':
    json_to_csv('data/qualified/qualified_candidates.json')
