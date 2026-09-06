import requests
import json
import os
import concurrent.futures
import re

def verify_single(c):
    url = c['website']
    c['website_verified'] = False
    c['website_reachable'] = False
    c['website_verification_status'] = 'needs_review'
    try:
        res = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        c['website_reachable'] = True
        
        if res.status_code == 200:
            c['website_verified'] = True
            text = res.text
            ai_pattern = r'\b(ai|artificial intelligence|machine learning|deep learning|generative ai|generative model|foundation model|large language model|llm|computer vision|natural language processing|nlp|speech recognition|reinforcement learning|neural network|ai agent|autonomous agent|multimodal|diffusion model|transformer model)\b'
            
            if re.search(ai_pattern, text, re.IGNORECASE):
                c['website_verification_status'] = 'verified'
            else:
                c['website_verification_status'] = 'partially_verified'
        elif res.status_code in [404, 410]:
            c['website_verification_status'] = 'invalid'
        else:
            c['website_verification_status'] = 'needs_review'
            
    except requests.exceptions.ConnectionError:
        c['website_verification_status'] = 'invalid'
    except requests.exceptions.Timeout:
        c['website_verification_status'] = 'needs_review'
    except Exception:
        c['website_verification_status'] = 'needs_review'
        
    return c

def verify_data(candidates):
    os.makedirs('data/verified', exist_ok=True)
    if os.path.exists('data/verified/verified_candidates.json'):
        with open('data/verified/verified_candidates.json', 'r') as f:
            return json.load(f)

    verified = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as executor:
        results = list(executor.map(verify_single, candidates))
        
    for r in results:
        verified.append(r)
        
    with open('data/verified/verified_candidates.json', 'w', encoding='utf-8') as f:
        json.dump(verified, f, indent=2)
    return verified
