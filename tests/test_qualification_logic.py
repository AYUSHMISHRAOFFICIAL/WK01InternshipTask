import pytest
import re
from src.verify import verify_single
from src.qualify import qualify_data

class DummyResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

def test_ai_keyword_detection(monkeypatch):
    c = {'website': 'http://test.com'}
    
    def mock_get(*args, **kwargs):
        return DummyResponse("Welcome to our AI platform.")
    monkeypatch.setattr("requests.get", mock_get)
    
    result = verify_single(c.copy())
    assert result['website_verification_status'] == 'verified'
    
    def mock_get_2(*args, **kwargs):
        return DummyResponse("We build Artificial Intelligence tools.")
    monkeypatch.setattr("requests.get", mock_get_2)
    assert verify_single(c.copy())['website_verification_status'] == 'verified'
    
    def mock_get_3(*args, **kwargs):
        return DummyResponse("machine learning is cool")
    monkeypatch.setattr("requests.get", mock_get_3)
    assert verify_single(c.copy())['website_verification_status'] == 'verified'
    
    def mock_get_4(*args, **kwargs):
        return DummyResponse("We train LLMs and computer vision models")
    monkeypatch.setattr("requests.get", mock_get_4)
    assert verify_single(c.copy())['website_verification_status'] == 'verified'

def test_ai_keyword_false_positives(monkeypatch):
    c = {'website': 'http://test.com'}
    
    def mock_get_main(*args, **kwargs):
        return DummyResponse("This is the main page.")
    monkeypatch.setattr("requests.get", mock_get_main)
    assert verify_single(c.copy())['website_verification_status'] == 'partially_verified'

    def mock_get_email(*args, **kwargs):
        return DummyResponse("email us here")
    monkeypatch.setattr("requests.get", mock_get_email)
    assert verify_single(c.copy())['website_verification_status'] == 'partially_verified'

    def mock_get_available(*args, **kwargs):
        return DummyResponse("seats are available")
    monkeypatch.setattr("requests.get", mock_get_available)
    assert verify_single(c.copy())['website_verification_status'] == 'partially_verified'

    def mock_get_training(*args, **kwargs):
        return DummyResponse("dog training")
    monkeypatch.setattr("requests.get", mock_get_training)
    assert verify_single(c.copy())['website_verification_status'] == 'partially_verified'

def test_qualification_logic(monkeypatch):
    # Mock file operations to not read/write to disk
    import os
    monkeypatch.setattr(os.path, "exists", lambda path: False)
    monkeypatch.setattr(os, "makedirs", lambda path, exist_ok: None)
    
    # Mock open
    from unittest.mock import mock_open
    monkeypatch.setattr("builtins.open", mock_open())
    
    # Test website_verification_status is read correctly
    c_web = {
        'company_name': 'Test1',
        'description': 'A nice startup',
        'website_verified': True,
        'website_verification_status': 'verified',
        'source': 'unknown'
    }
    # It has 1 signal (website), so should be needs_review
    res = qualify_data([c_web])[0]
    assert res['qualified'] == False
    assert res['qualification_evidence']['website_evidence'] == True
    
    # Test verification_status alone does NOT silently override (canonical field is website_verification_status)
    c_wrong_key = {
        'company_name': 'Test2',
        'description': 'A nice startup',
        'website_verified': True,
        'verification_status': 'verified', # WRONG KEY
        'source': 'unknown'
    }
    res = qualify_data([c_wrong_key])[0]
    assert res['qualification_evidence']['website_evidence'] == False
    
    # Test yc_huggingface_snapshot maps to source evidence
    c_yc = {
        'company_name': 'Test3',
        'description': 'A nice startup',
        'source': 'yc_huggingface_snapshot'
    }
    res = qualify_data([c_yc])[0]
    assert res['qualification_evidence']['source_evidence'] == True
    assert res['qualified'] == False # Only 1 signal
    
    # Test github maps correctly
    c_github = {
        'company_name': 'Test4',
        'description': 'A nice startup',
        'source': 'github'
    }
    res = qualify_data([c_github])[0]
    assert res['qualification_evidence']['source_evidence'] == True
    assert res['qualified'] == False # Only 1 signal
    
    # Source evidence + website evidence = 2 signals = qualified
    c_both = {
        'company_name': 'Test5',
        'description': 'A nice startup',
        'source': 'github',
        'website_verified': True,
        'website_verification_status': 'verified'
    }
    res = qualify_data([c_both])[0]
    assert res['qualified'] == True
    assert res['qualification_evidence']['source_evidence'] == True
    assert res['qualification_evidence']['website_evidence'] == True

def test_crunchbase_removed():
    from src.extract import discover_ai_datasets
    res = discover_ai_datasets()
    assert len(res) == 0
