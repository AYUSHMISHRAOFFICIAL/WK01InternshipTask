import json
import csv
import os

def export_data(candidates):
    os.makedirs('data/final', exist_ok=True)
    with open('data/final/companies.json', 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2)
        
    if not candidates:
        return
        
    keys = candidates[0].keys()
    with open('data/final/companies.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(candidates)
