def validate_data(candidates, final_export=True):
    valid = []
    for c in candidates:
        has_base = bool(c.get('domain') and c.get('company_name'))
        has_llm = bool(c.get('description') and c.get('ai_classification'))
        
        if final_export:
            if has_base and has_llm:
                valid.append(c)
        else:
            if has_base:
                valid.append(c)
    return valid
