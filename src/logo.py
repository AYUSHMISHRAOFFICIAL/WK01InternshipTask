import requests
from bs4 import BeautifulSoup
import concurrent.futures

def fetch_logo(c):
    c['logo_url'] = None
    c['logo_verified'] = False
    if c['website_verified']:
        try:
            res = requests.get(c['website'], timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                icon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
                if icon and icon.get('href'):
                    href = icon['href']
                    if not href.startswith('http'):
                        if href.startswith('/'):
                            href = c['website'].rstrip('/') + href
                        else:
                            href = c['website'].rstrip('/') + '/' + href
                    c['logo_url'] = href
                    c['logo_verified'] = True
        except Exception:
            pass
    return c

def verify_logos(candidates):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for r in executor.map(fetch_logo, candidates):
            results.append(r)
    return results
