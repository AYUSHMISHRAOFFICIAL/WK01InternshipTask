import json
from collections import Counter

with open('data/qualified/qualified_candidates.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

qual = [c for c in data if c.get('qualification_status') == 'qualified']
rejected = [c for c in data if c.get('qualification_status') == 'rejected']
needs_review = [c for c in data if c.get('qualification_status') == 'needs_review']

print('--- COUNTS ---')
print(f'Qualified: {len(qual)}')
print(f'Rejected: {len(rejected)}')
print(f'Needs Review: {len(needs_review)}')

print('\n--- BY SOURCE (QUALIFIED) ---')
sources = Counter(c.get('source') for c in qual)
for k, v in sources.items(): print(f'{k}: {v}')

print('\n--- BY ENTITY TYPE (QUALIFIED) ---')
entities = Counter(c.get('entity_type') for c in qual)
for k, v in entities.items(): print(f'{k}: {v}')

print('\n--- BY ENTITY TYPE (ALL) ---')
all_entities = Counter(c.get('entity_type') for c in data)
for k, v in all_entities.items(): print(f'{k}: {v}')

print('\n--- REJECT REASONS ---')
reasons = Counter(c.get('qualification_reason') for c in rejected)
for k, v in reasons.items(): print(f'{k}: {v}')

print('\n--- EXAMPLES OF REJECTED ---')
for c in rejected[:5]:
    cname = c.get('company_name')
    ctype = c.get('entity_type')
    cdom = c.get('domain')
    creason = c.get('qualification_reason')
    print(f"- {cname} | {ctype} | {cdom} | {creason}")

print('\n--- EXAMPLES OF LEGITIMATE PRESERVED ---')
for c in qual[:5]:
    cname = c.get('company_name')
    ctype = c.get('entity_type')
    cdom = c.get('domain')
    print(f"- {cname} | {ctype} | {cdom}")

print('\n--- GITHUB SOURCE STATUS ---')
gh = [c for c in data if c.get('source') == 'github']
gh_qual = len([c for c in gh if c.get('qualification_status') == 'qualified'])
gh_rej = len([c for c in gh if c.get('qualification_status') == 'rejected'])
gh_rev = len([c for c in gh if c.get('qualification_status') == 'needs_review'])
print(f'Total GitHub: {len(gh)}')
print(f'Qualified: {gh_qual}')
print(f'Rejected: {gh_rej}')
print(f'Needs Review: {gh_rev}')
