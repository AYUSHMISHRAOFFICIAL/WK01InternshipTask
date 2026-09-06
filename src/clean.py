import json
import tldextract
import re
import os

def clean_data(candidates):
    os.makedirs('data/cleaned', exist_ok=True)
    if os.path.exists('data/cleaned/cleaned_candidates.json'):
        with open('data/cleaned/cleaned_candidates.json', 'r') as f:
            return json.load(f)

    cleaned = []
    for c in candidates:
        name = c.get('company_name') or ''
        name = re.sub(r'(?i)(Inc\.|LLC|Corp\.|Ltd\.)', '', name).strip()
        url = c.get('website') or ''
        
        domain = ''
        if url:
            if not url.startswith('http'):
                url = 'https://' + url
            extracted = tldextract.extract(url)
            domain = f'{extracted.domain}.{extracted.suffix}'.lower()
            
        if not name or not domain:
            continue
            
        cleaned.append({
            'company_name': name,
            'website': url,
            'domain': domain,
            'description': c.get('description'),
            'source': c.get('source'),
            'source_url': c.get('source_url'),
            'country': None,
            'city': None,
            'founded_year': None,
            'employees': None,
            'funding_raised': None,
            'latest_funding_round': None,
            'valuation': None,
            'investors': None,
            'models': None,
            'tools_products': None,
            'repositories': None,
            'news': None,
            'videos': None,
            'fundraises': None,
            'social_links': None
        })
    
    with open('data/cleaned/cleaned_candidates.json', 'w') as out:
        json.dump(cleaned, out, indent=2)
    return cleaned
