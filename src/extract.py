import json
import os
import requests
import re
import concurrent.futures
from src.dataset_loader import load_external_datasets

def fetch_url(url):
    local_c = []
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            matches = re.findall(r'\[([^\]]+)\]\((http[s]?://[^\)]+)\)(?: - (.*))?', res.text)
            for match in matches:
                name, link, desc = match
                if len(name) > 2 and not name.startswith('http') and not "github.com" in link:
                    local_c.append({
                        'company_name': name,
                        'website': link,
                        'description': desc.strip() if desc else '',
                        'source': 'github',
                        'source_url': url
                    })
    except Exception:
        pass
    return local_c

def discover_github():
    candidates = []
    urls = [
        "https://raw.githubusercontent.com/steven2358/awesome-generative-ai/main/README.md",
        "https://raw.githubusercontent.com/amusi/awesome-ai-awesomeness/master/README.md",
        "https://raw.githubusercontent.com/Hannibal046/Awesome-LLM/main/README.md",
        "https://raw.githubusercontent.com/fendouai/Awesome-Artificial-Intelligence/master/README.md",
        "https://raw.githubusercontent.com/eugeneyan/open-llms/main/README.md",
        "https://raw.githubusercontent.com/a16z-infra/ai-town/main/README.md",
        "https://raw.githubusercontent.com/ashishpatel26/500-AI-Machine-learning-Deep-learning-Computer-vision-NLP-Projects-with-code/main/README.md"
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for result in executor.map(fetch_url, urls):
            candidates.extend(result)
    return candidates

def discover_yc():
    candidates = []
    url = "https://huggingface.co/datasets/jeffboudier/yc-companies-august-2025/resolve/main/yc-companies-august-2025.csv"
    try:
        import pandas as pd
        df = pd.read_csv(url)
        # Map: 'name' -> 'company_name', 'website', 'long_description' / 'one_liner' -> 'description'
        for _, row in df.iterrows():
            if pd.isna(row.get('website')):
                continue
            name = str(row.get('name', ''))
            desc = str(row.get('one_liner', '')) + " " + str(row.get('long_description', ''))
            candidate = {
                'company_name': name,
                'website': str(row.get('website', '')),
                'description': desc.strip(),
                'source': 'yc_huggingface_snapshot',
                'source_url': url,
                'source_record_id': str(row.get('id', ''))
            }
            # Add extra metadata
            for field in ['industry', 'subindustry', 'tags/0', 'batch', 'all_locations', 'team_size']:
                if field in row and pd.notna(row[field]):
                    candidate[field] = str(row[field])
            candidates.append(candidate)
    except Exception as e:
        print(f"Error fetching YC snapshot: {e}")
    return candidates

def discover_startup_datasets():
    # Using HackerNoon where-startups-trend as a broad discovery source
    candidates = []
    url = "https://huggingface.co/datasets/HackerNoon/where-startups-trend/resolve/main/worldwide%20trending%20startups%20votes.csv"
    try:
        import pandas as pd
        df = pd.read_csv(url)
        for _, row in df.iterrows():
            website = row.get('Startups URL')
            if pd.isna(website):
                continue
            candidates.append({
                'company_name': str(row.get('Startups Name', '')),
                'website': str(website),
                'description': str(row.get('description', '')),
                'source': 'hackernoon_startups',
                'source_url': url,
                'industry': str(row.get('industry', '')),
                'city': str(row.get('city', ''))
            })
    except Exception as e:
        print(f"Error fetching HackerNoon dataset: {e}")
    return candidates

def discover_startupdb():
    # Deprecated/Removed per user instruction to avoid source explosion
    return []

def discover_ai_datasets():
    # Crunchbase removed due to licensing restrictions.
    return []

def extract_data():
    os.makedirs('data/raw', exist_ok=True)
    if os.path.exists('data/raw/raw_candidates.json'):
        with open('data/raw/raw_candidates.json', 'r') as f:
            network_candidates = json.load(f)
        
        stats = {}
        if os.path.exists('data/raw/extract_stats.json'):
            with open('data/raw/extract_stats.json', 'r') as f:
                stats = json.load(f)
                
        # Always reload external datasets
        print("Fetching from external datasets...")
        external_candidates = load_external_datasets()
        stats['external_datasets'] = {'attempted': len(external_candidates), 'retrieved': len(external_candidates), 'failed': 0}
        
        return network_candidates + external_candidates, stats

    all_candidates = []
    stats = {}
    
    modules = [
        ('github', discover_github),
        ('yc', discover_yc),
        ('startup_datasets', discover_startup_datasets),
        ('startupdb', discover_startupdb),
        ('ai_datasets', discover_ai_datasets)
    ]
    
    print("Fetching from external datasets...")
    external_candidates = load_external_datasets()
    stats['external_datasets'] = {'attempted': len(external_candidates), 'retrieved': len(external_candidates), 'failed': 0}
    
    # Track network candidates separately so we can cache just those
    network_candidates = []
    
    for name, func in modules:
        print(f"Fetching from {name}...")
        results = func()
        stats[name] = {'attempted': len(results), 'retrieved': len(results), 'failed': 0}
        network_candidates.extend(results)
        
    with open('data/raw/raw_candidates.json', 'w', encoding='utf-8') as f:
        json.dump(network_candidates, f, indent=2)
        
    with open('data/raw/extract_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
        
    all_candidates = network_candidates + external_candidates
    return all_candidates, stats
