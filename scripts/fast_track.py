import json
import csv
import os
import pandas as pd
from dotenv import load_dotenv
from src.describe import describe_data

load_dotenv()

def fast_track_export():
    print("Loading existing data...")
    # Load qualified candidates
    with open('data/qualified/qualified_candidates.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    qualified = [c for c in data if c.get('qualification_status') == 'qualified']
    
    # Load logos from previously exported CSV
    print("Extracting cached logos from companies.csv...")
    df = pd.read_csv('data/final/companies.csv', low_memory=False)
    logo_map = {}
    if 'logo_url' in df.columns:
        for _, row in df.iterrows():
            if pd.notna(row.get('company_name')) and pd.notna(row.get('logo_url')):
                logo_map[str(row['company_name'])] = str(row['logo_url'])
                
    # Assign logos and pick 1050
    print("Selecting 1050 candidates...")
    fast_track_list = []
    for c in qualified:
        name = c.get('company_name')
        if name in logo_map:
            c['logo_url'] = logo_map[name]
            c['logo_verified'] = True
            fast_track_list.append(c)
            
        if len(fast_track_list) >= 2050:
            break
            
    print(f"Selected {len(fast_track_list)} candidates for ultra-fast enrichment.")
    
    # Run Groq API
    print("Running LLM enrichment via Groq...")
    described = describe_data(fast_track_list)
    
    # Final Export
    print("Generating final CSV...")
    final_records = []
    for item in described:
        if not item.get('website'):
            continue
        desc = item.get('llm_description') or item.get('description')
        if not desc:
            continue
            
        final_record = {
            'Company Name': item.get('company_name', ''),
            'Website URL': item.get('website', ''),
            'Logo URL': item.get('logo_url', ''),
            'Category': item.get('ai_classification', ''),
            'Description': desc
        }
        
        # Clean formatting (newlines, etc.)
        for k, v in final_record.items():
            if isinstance(v, str):
                final_record[k] = v.replace('\n', ' ').replace('\r', ' ').strip()
                
        final_records.append(final_record)
        
    output_file = 'data/final/ai_companies_sheet.csv'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['Company Name', 'Website URL', 'Logo URL', 'Category', 'Description'])
        writer.writeheader()
        writer.writerows(final_records)
        
    print(f"SUCCESS! Generated {output_file} with {len(final_records)} records.")

if __name__ == '__main__':
    fast_track_export()
