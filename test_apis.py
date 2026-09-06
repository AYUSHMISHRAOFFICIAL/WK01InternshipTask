import requests
import json

def test_yc():
    try:
        r = requests.get('https://yc-oss.github.io/api/companies/all.json')
        if r.status_code == 200:
            print("YC-OSS success:", len(r.json()))
        else:
            print("YC-OSS failed:", r.status_code)
    except Exception as e:
        print("YC-OSS Exception:", e)

def test_startupdb():
    try:
        r = requests.get('https://startupdb.com/api/startups', headers={'User-Agent': 'Mozilla/5.0'})
        print("StartupDB:", r.status_code, len(r.content))
    except Exception as e:
        print("StartupDB Exception:", e)

test_yc()
test_startupdb()
