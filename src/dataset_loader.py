import os
import json
import csv

DATASET_CONFIG = {
    'epoch_ai': {
        'url': 'https://epoch.ai/data/ai-companies-documentation/downloads',
        'dataset_name': 'Epoch AI Companies'
    },
    'world_bank_ai': {
        'url': 'https://www.worldbank.org/',
        'dataset_name': 'World Bank AI Startup Dataset'
    },
    'webclaw': {
        'url': 'https://webclaw.io/data/startups',
        'dataset_name': 'Webclaw startup dataset'
    }
}

# Source field -> Target canonical field
FIELD_MAPPINGS = {
    'company_name': 'name',
    'company': 'name',
    'organization': 'name',
    'organization_name': 'name',
    'startup_name': 'name',
    'url': 'website',
    'homepage': 'website',
    'website': 'website',
    'company_url': 'website',
    'domain': 'website',
    'about': 'description',
    'summary': 'description',
    'description': 'description',
    'tagline': 'description',
    'country': 'country',
    'country_name': 'country',
    'headquarters_country': 'country',
    'city': 'city',
    'city_name': 'city',
    'headquarters_city': 'city',
    'founded': 'founded_year',
    'founded_year': 'founded_year',
    'year_founded': 'founded_year',
    'employees': 'employees',
    'employee_count': 'employees',
    'num_employees': 'employees',
    'funding': 'funding',
    'total_funding': 'funding',
    'funding_total': 'funding',
    'investors': 'investors',
    'investor_names': 'investors'
}

def load_external_datasets(directory="data/raw/external"):
    candidates = []
    
    if not os.path.exists(directory):
        return candidates
        
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            continue
            
        source_id = os.path.splitext(filename)[0]
        config = DATASET_CONFIG.get(source_id, {})
        source_url = config.get('url', None)
        dataset_name = config.get('dataset_name', filename)
        
        try:
            if filename.endswith('.csv'):
                candidates.extend(_load_csv(filepath, source_id, source_url, dataset_name))
            elif filename.endswith('.json'):
                candidates.extend(_load_json(filepath, source_id, source_url, dataset_name))
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            print(f"Error loading {filename}: {e}")
    return candidates

def _normalize_record(record, source_id, source_url, dataset_name, record_id=None):
    normalized = {}
    
    # Apply field mappings
    for k, v in record.items():
        if k is None or v == "" or v is None:
            continue
        
        canon_key = FIELD_MAPPINGS.get(k.lower().strip(), k.lower().strip())
        
        if canon_key not in normalized or not normalized[canon_key]:
            normalized[canon_key] = v

    # Add required fields if missing
    if 'company_name' in normalized and 'name' not in normalized:
        normalized['name'] = normalized['company_name']
    
    # We still need `company_name` for existing pipeline compatibility which expects `company_name`
    if 'name' in normalized and 'company_name' not in normalized:
        normalized['company_name'] = normalized['name']
        
    normalized['source'] = source_id
    normalized['source_url'] = source_url
    normalized['source_dataset'] = dataset_name
    
    if record_id:
        normalized['source_record_id'] = record_id
    elif 'id' in normalized:
        normalized['source_record_id'] = str(normalized['id'])
        
    return normalized

def _load_csv(filepath, source_id, source_url, dataset_name):
    candidates = []
    with open(filepath, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            normalized = _normalize_record(row, source_id, source_url, dataset_name, record_id=str(i))
            if normalized.get('name') or normalized.get('company_name'):
                candidates.append(normalized)
    return candidates

def _load_json(filepath, source_id, source_url, dataset_name):
    candidates = []
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Handle single object wrapped
    if isinstance(data, dict):
        if 'data' in data and isinstance(data['data'], list):
            data = data['data']
        elif 'startups' in data and isinstance(data['startups'], list):
            data = data['startups']
        elif 'companies' in data and isinstance(data['companies'], list):
            data = data['companies']
        else:
            data = [data]
            
    if isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                normalized = _normalize_record(item, source_id, source_url, dataset_name, record_id=str(i))
                if normalized.get('name') or normalized.get('company_name'):
                    candidates.append(normalized)
    return candidates
