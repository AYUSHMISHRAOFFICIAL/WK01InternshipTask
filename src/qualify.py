import json
import os
import tldextract

def get_base_domain(url_or_domain):
    if not url_or_domain:
        return ""
    ext = tldextract.extract(url_or_domain)
    return f"{ext.domain}.{ext.suffix}".lower()

def detect_entity_type(name, desc):
    name_l = name.lower()
    desc_l = desc.lower()
    
    # 1. Article / News
    if any(w in desc_l for w in ['article summarizing', 'article about', 'news story', 'newsletter', 'essay', 'blog post']):
        return 'article'
    if name_l.startswith('how ') or name_l.startswith('why '):
        if len(name.split()) >= 5:
            return 'article'
            
    # 2. Research / Model
    if any(w in desc_l for w in ['research paper', 'pre-trained model', 'language model based on', 'arxiv']):
        return 'research/model'
        
    # 3. Repository / Project
    if any(w in desc_l for w in ['a repository', 'open-source framework', 'curated list', 'awesome list', 'open source project']):
        return 'repository/project'
        
    # 4. Dataset
    if 'dataset' in desc_l and 'curated' in desc_l:
        return 'dataset'
        
    # 5. API / Product
    if 'announcement of the' in desc_l and 'api' in desc_l:
        return 'API/product'
        
    # 6. Company identity language
    if any(w in desc_l for w in ['company', 'startup', 'platform', 'provider', 'enterprise', 'agency', 'inc.', 'llc']):
        return 'company'
    if 'we are' in desc_l or 'our mission' in desc_l or 'our team' in desc_l or 'we help' in desc_l:
        return 'company'
        
    return 'company'

def qualify_data(candidates):
    os.makedirs('data/qualified', exist_ok=True)
    # Temporarily remove short-circuit to force rerun
    # if os.path.exists('data/qualified/qualified_candidates.json'):
    #     with open('data/qualified/qualified_candidates.json', 'r') as f:
    #         return json.load(f)

    qualified_results = []
    
    non_company_domains = {
        'github.com', 'arxiv.org', 'youtube.com', 'medium.com', 
        'nytimes.com', 'wired.com', 'substack.com', 'stanford.edu', 'mit.edu'
    }

    for c in candidates:
        desc = (c.get('description') or '').lower()
        name = (c.get('company_name') or '').lower()
        raw_domain = c.get('domain', '')
        base_domain = get_base_domain(raw_domain)
        
        # Entity type detection
        entity_type = detect_entity_type(name, desc)
        c['entity_type'] = entity_type
        
        # Soft signals
        long_name_signal = len(name.split()) >= 6
        c['long_name_signal'] = long_name_signal
        
        domain_excluded = base_domain in non_company_domains
        c['domain_excluded'] = domain_excluded
        
        # Determine evidence
        ai_product_evidence = bool(any(k in desc for k in ['model', 'generative', 'computer vision', 'robotics', 'agent', 'nlp', 'llm', 'foundation model']))
        ai_technology_evidence = bool(any(k in desc for k in ['machine learning', 'artificial intelligence', 'deep learning', 'neural']))
        ai_business_evidence = bool('ai' in name or 'ai' in raw_domain)
        
        # Source evidence
        legitimate_ai_sources = ['ycombinator', 'github_awesome_lists', 'yc_huggingface_snapshot', 'github', 'Epoch AI Companies']
        source_evidence = bool(c.get('source') in legitimate_ai_sources)
        
        # Website evidence from verification stage
        website_evidence = False
        if c.get('website_verified') and c.get('website_verification_status') == 'verified':
            website_evidence = True

        evidence_count = sum([ai_product_evidence, ai_technology_evidence, ai_business_evidence, source_evidence, website_evidence])
        
        c['qualification_evidence'] = {
            'ai_product_evidence': ai_product_evidence,
            'ai_technology_evidence': ai_technology_evidence,
            'ai_business_evidence': ai_business_evidence,
            'source_evidence': source_evidence,
            'website_evidence': website_evidence
        }
        
        # Qualification Logic
        reject_reason = None
        
        if domain_excluded:
            reject_reason = f"Domain excluded: {base_domain}"
        elif entity_type not in ['company', 'unknown']:
            reject_reason = f"Entity type '{entity_type}' is not a company"
        elif c.get('source') in ['github', 'github_awesome_lists']:
            # GitHub sources require stronger company evidence
            if entity_type != 'company':
                reject_reason = "GitHub source requires explicit company identity"
            elif evidence_count < 3:
                reject_reason = "GitHub source requires >= 3 evidence signals"
        
        if reject_reason:
            c['qualified'] = False
            c['qualification_status'] = 'rejected'
            c['qualification_reason'] = reject_reason
            c['qualification_confidence'] = 'high'
        elif evidence_count >= 2:
            if entity_type == 'unknown' or long_name_signal:
                c['qualified'] = False
                c['qualification_status'] = 'needs_review'
                c['qualification_reason'] = f"Qualified by evidence but requires manual review (unknown entity type or long name)"
                c['qualification_confidence'] = 'low'
            else:
                c['qualified'] = True
                c['qualification_status'] = 'qualified'
                c['qualification_reason'] = f"Found {evidence_count} evidence signals and verified company entity"
                c['qualification_confidence'] = 'high' if evidence_count >= 3 else 'medium'
        else:
            c['qualified'] = False
            c['qualification_status'] = 'needs_review'
            c['qualification_reason'] = f"Insufficient evidence ({evidence_count} signals)"
            c['qualification_confidence'] = 'low'
            
        qualified_results.append(c)
            
    with open('data/qualified/qualified_candidates.json', 'w', encoding='utf-8') as f:
        json.dump(qualified_results, f, indent=2)
        
    return qualified_results
