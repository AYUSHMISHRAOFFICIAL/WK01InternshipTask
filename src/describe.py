import os
import json
import concurrent.futures
import threading
import time
import requests

def describe_data(candidates):
    groq_api_key = os.environ.get('GROQ_API_KEY')
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    
    if not groq_api_key and not gemini_api_key:
        print("LLM credential required for final description generation.")
        print("Stopping pipeline step: describe.")
        for c in candidates:
            c.setdefault('description_generated', False)
            c.setdefault('description_error', 'Missing LLM API Key')
            c.setdefault('ai_classification', 'Unknown')
        return candidates

    use_groq = bool(groq_api_key)
    
    if not use_groq:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-3.5-flash')
        except ImportError as e:
            print(f"Error importing google.generativeai: {e}")
            return candidates
    else:
        print("Using Groq API for ultra-fast enrichment!")

    os.makedirs('data/described', exist_ok=True)
    checkpoint_file = 'data/described/described_candidates.json'
    
    # Checkpoint loading
    described_map = {}
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                for domain, c in saved.items():
                    described_map[domain] = c
        except Exception:
            pass

    # Ensure all have basic keys
    for c in candidates:
        c.setdefault('description_generated', False)
        c.setdefault('description_provider', None)
        c.setdefault('description_error', None)
        if not c.get('ai_classification'):
            c['ai_classification'] = 'Unknown'

    max_workers = 15 if use_groq else int(os.environ.get('GEMINI_MAX_WORKERS', 5))
    
    completed_count = 0
    lock = threading.Lock()

    def process_candidate(c):
        nonlocal completed_count
        domain = c.get('domain')
        
        # Check if already processed
        with lock:
            if domain in described_map:
                if described_map[domain].get('description_generated'):
                    c['description'] = described_map[domain]['description']
                    c['ai_classification'] = described_map[domain]['ai_classification']
                    c['description_generated'] = True
                    c['description_provider'] = described_map[domain]['description_provider']
                    c['description_error'] = None
                    
                    completed_count += 1
                    return c
        
        prompt = f"""
        Company Name: {c.get('company_name')}
        Original Description: {c.get('description', '')}
        
        Generate a strictly factual 30-word description of this company based ONLY on the provided original description. Do not invent any funding, employees, location, products, or other facts.
        Also categorize the company's AI focus into a short classification (e.g., 'Generative AI', 'Computer Vision', 'Robotics', 'Unknown').
        
        Output MUST be valid JSON with this exact schema:
        {{
            "description": "...",
            "ai_classification": "..."
        }}
        """
        
        max_retries = 3
        backoff = 2
        for attempt in range(max_retries):
            try:
                if use_groq:
                    headers = {
                        "Authorization": f"Bearer {groq_api_key}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": "llama3-8b-8192",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                        "response_format": {"type": "json_object"}
                    }
                    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=10)
                    if resp.status_code == 429:
                        raise Exception("429 Too Many Requests")
                    resp.raise_for_status()
                    resp_json = resp.json()
                    resp_text = resp_json['choices'][0]['message']['content'].strip()
                    provider = 'Groq Llama3'
                else:
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.1,
                            response_mime_type="application/json",
                        ),
                        request_options={"timeout": 15}
                    )
                    resp_text = response.text.strip()
                    provider = 'Gemini 3.5 Flash'
                
                result = json.loads(resp_text)
                
                if not isinstance(result, dict) or 'description' not in result or 'ai_classification' not in result:
                    raise ValueError("Malformed JSON structure")
                    
                c['description'] = result['description']
                c['ai_classification'] = result['ai_classification']
                c['description_generated'] = True
                c['description_provider'] = provider
                c['description_error'] = None
                break # Success
                
            except Exception as e:
                err_str = str(e).lower()
                if attempt < max_retries - 1:
                    if '429' in err_str or '503' in err_str or 'timeout' in err_str or 'json' in err_str:
                        if '429' in err_str:
                            time.sleep(10 if use_groq else 60)
                        else:
                            time.sleep(backoff)
                        backoff *= 2
                        continue
                
                c['description_generated'] = False
                c['description_error'] = str(e)
                c['ai_classification'] = 'Unknown'
                break

        with lock:
            if domain not in described_map:
                described_map[domain] = c
                
                with open(checkpoint_file, 'w', encoding='utf-8') as f:
                    json.dump(described_map, f, indent=2)
                
            completed_count += 1
            if completed_count % 100 == 0:
                print(f"Completed {completed_count}/{len(candidates)}")
                
        return c

    print(f"Starting descriptions with {max_workers} workers...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_candidate, candidates))
        
    return results
