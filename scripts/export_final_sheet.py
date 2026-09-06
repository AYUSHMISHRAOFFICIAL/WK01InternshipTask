import json
import csv
import os

def export_final_sheet():
    input_file = 'data/described/described_candidates.json'
    output_file = 'data/final/ai_companies_sheet.csv'
    
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return
        
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if isinstance(data, dict):
        data = list(data.values())
        
    # We only want to export records that have been described by LLM
    final_records = []
    for item in data:
        # Check if the record has the required clean fields
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
        
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['Company Name', 'Website URL', 'Logo URL', 'Category', 'Description'])
        writer.writeheader()
        writer.writerows(final_records)
        
    print(f"Successfully generated {output_file} with {len(final_records)} records matching the required format.")

if __name__ == '__main__':
    export_final_sheet()
