import json
import random
from collections import Counter
import re

print("Loading candidates...")
with open('data/qualified/qualified_candidates.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

qualified = [c for c in candidates if c.get('qualified')]
needs_review = [c for c in candidates if not c.get('qualified')]

# 1. Audit qualified companies
print("--- 1. AUDIT 643 QUALIFIED ---")
print(f"Total qualified: {len(qualified)}")
print("Confidence distribution:", dict(Counter(c.get('qualification_confidence') for c in qualified)))
print("Source distribution:", dict(Counter(c.get('source') for c in qualified)))
print("Verification-status distribution:", dict(Counter(c.get('website_verification_status') for c in qualified)))

ev_counts = {
    'ai_product_evidence': 0,
    'ai_technology_evidence': 0,
    'ai_business_evidence': 0,
    'source_evidence': 0,
    'website_evidence': 0
}
for c in qualified:
    ev = c.get('qualification_evidence', {})
    for k in ev_counts:
        if ev.get(k): ev_counts[k] += 1
print("Evidence signal hits across qualified:", ev_counts)

# 2. Audit needs_review population
print("\n--- 2. AUDIT NEEDS_REVIEW (Sample 200) ---")
sampled_nr = random.sample(needs_review, min(200, len(needs_review)))
reasons = {
    'genuinely non-AI': 0,
    'website inaccessible / invalid': 0,
    'AI evidence exists but not detected': 0,
    'AI evidence in source metadata but website failed': 0,
    'homepage too sparse / no AI keywords': 0,
    'other': 0
}

ai_keywords = ['model', 'generative', 'computer vision', 'robotics', 'agent', 'nlp', 'llm', 'foundation model', 'machine learning', 'artificial intelligence', 'deep learning', 'neural', 'ai']

for c in sampled_nr:
    desc = (c.get('description') or '').lower()
    name = (c.get('company_name') or '').lower()
    has_ai_desc = any(re.search(rf'\b{kw}\b', desc) for kw in ai_keywords)
    
    if c.get('website_verification_status') in ['invalid', 'needs_review']:
        if has_ai_desc:
            reasons['AI evidence in source metadata but website failed'] += 1
        else:
            reasons['website inaccessible / invalid'] += 1
    elif c.get('website_verified') and c.get('website_verification_status') == 'partially_verified':
        if has_ai_desc:
            reasons['AI evidence exists but not detected'] += 1
        else:
            reasons['homepage too sparse / no AI keywords'] += 1
    elif not has_ai_desc:
        reasons['genuinely non-AI'] += 1
    else:
        reasons['other'] += 1

print(f"Analyzed {len(sampled_nr)} needs_review candidates. Distribution:")
for k, v in reasons.items():
    print(f"  {k}: {v} ({(v/200)*100:.1f}%)")

# 4. Audit the 18,089 "website verified" candidates
print("\n--- 4. AUDIT WEBSITE VERIFIED ---")
website_verified = [c for c in candidates if c.get('website_verified')]
print(f"Total website_verified: {len(website_verified)}")

wv_nr = [c for c in website_verified if not c.get('qualified')]
print(f"Website-verified but needs_review (didn't qualify): {len(wv_nr)}")

wv_ai_keywords = [c for c in wv_nr if c.get('website_verification_status') == 'verified']
print(f"Have AI keyword hits on website (status='verified') but DID NOT qualify: {len(wv_ai_keywords)}")

wv_source_ai = [c for c in wv_nr if c.get('website_verification_status') == 'partially_verified' and any(re.search(rf'\b{kw}\b', (c.get('description') or '').lower()) for kw in ai_keywords)]
print(f"Have AI-related source metadata but website evidence was missing/sparse: {len(wv_source_ai)}")

print(f"\nEstimate of potential recoverable pool from website-verified: {len(wv_ai_keywords) + len(wv_source_ai)}")
