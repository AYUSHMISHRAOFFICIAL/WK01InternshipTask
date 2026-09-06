import tldextract

def deduplicate_data(candidates):
    seen = {}
    
    for c in candidates:
        domain = c.get('domain')
        if not domain:
            continue
            
        if domain not in seen:
            c['sources'] = [c.get('source')]
            c['source_urls'] = [c.get('source_url')]
            c['source_count_per_company'] = 1
            seen[domain] = c
        else:
            existing = seen[domain]
            src = c.get('source')
            if src and src not in existing['sources']:
                existing['sources'].append(src)
                existing['source_urls'].append(c.get('source_url'))
                existing['source_count_per_company'] += 1
                
    return list(seen.values())
