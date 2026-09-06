import os
import json
import csv
import pytest
from src.dataset_loader import load_external_datasets

def test_csv_ingestion(tmpdir):
    d = tmpdir.mkdir("data")
    
    import os
    d_path = str(d)
    
    with open(os.path.join(d_path, "epoch_ai.csv"), "w", encoding="utf-8") as f:
        f.write("company_name,homepage,about,headquarters_country\nTestAI,https://testai.com,An AI company,USA\n")
    
    with open(os.path.join(d_path, "empty.csv"), "w", encoding="utf-8") as f:
        f.write("company_name,homepage\n")
    
    with open(os.path.join(d_path, "malformed.csv"), "w", encoding="utf-8") as f:
        f.write("just_one_column\nno_data\n")

    candidates = load_external_datasets(directory=str(d))
    
    assert len(candidates) == 1
    c = candidates[0]
    
    assert c['name'] == 'TestAI'
    assert c['website'] == 'https://testai.com'
    assert c['description'] == 'An AI company'
    assert c['country'] == 'USA'
    assert c['source'] == 'epoch_ai'
    assert c['source_dataset'] == 'Epoch AI Companies'
    assert c['source_url'] == 'https://epoch.ai/data/ai-companies-documentation/downloads'
    assert c['source_record_id'] == '0'

def test_json_ingestion(tmpdir):
    d = tmpdir.mkdir("data")
    
    # List of objects
    json_list = d.join("world_bank_ai.json")
    json_list.write(json.dumps([
        {"startup_name": "WB AI", "url": "https://wbai.org", "tagline": "AI for all"}
    ]))
    
    # Wrapped JSON object
    json_wrapped = d.join("webclaw.json")
    json_wrapped.write(json.dumps({
        "startups": [
            {"organization_name": "Webclaw AI", "domain": "webclaw.io", "summary": "Data stuff"}
        ]
    }))
    
    # Malformed JSON
    malformed_json = d.join("malformed.json")
    malformed_json.write("{ bad json ")
    
    candidates = load_external_datasets(directory=str(d))
    
    # We should have 2 candidates
    assert len(candidates) == 2
    
    wb = next(c for c in candidates if c['source'] == 'world_bank_ai')
    assert wb['name'] == 'WB AI'
    assert wb['website'] == 'https://wbai.org'
    
    wc = next(c for c in candidates if c['source'] == 'webclaw')
    assert wc['name'] == 'Webclaw AI'
    assert wc['website'] == 'webclaw.io'
    assert wc['description'] == 'Data stuff'

def test_missing_fields_and_no_fabricated_defaults(tmpdir):
    d = tmpdir.mkdir("data")
    
    import os
    d_path = str(d)
    
    with open(os.path.join(d_path, "test_source.csv"), "w", encoding="utf-8") as f:
        f.write("company_name,url,funding\nTestCompany,,\n")
    
    candidates = load_external_datasets(directory=str(d))
    
    assert len(candidates) == 1
    c = candidates[0]
    assert c['name'] == 'TestCompany'
    assert 'website' not in c or not c['website']
    assert 'funding' not in c or not c['funding']
