import os
import json
import socket
import requests
import whois
import ssl as ssl_lib
import urllib.parse
from django.conf import settings
import datetime

# Load domain rank data (JSON) and url shorteners (TXT) from static files
domain_rank_path = os.path.join(settings.BASE_DIR, 'app', 'static', 'data', 'domain-rank.json')
url_shorteners_path = os.path.join(settings.BASE_DIR, 'app', 'static', 'data', 'url-shorteners.txt')

with open(domain_rank_path, 'r') as f:
    domain_rank_dict = json.load(f)

with open(url_shorteners_path, 'r') as f:
    url_shorteners = f.read().splitlines()


def include_protocol(url):
    if not url.startswith(('http://', 'https://')):
        return 'http://' + url
    return url


def validate_url(url):
    try:
        resp = requests.head(url, timeout=5)
        return resp.status_code
    except requests.RequestException:
        return None


def phishtank_search(url):
    # Dummy function - implement your Phishtank API logic here or return False if not phishing
    return False


def get_domain_rank(domain):
    # Return rank from domain_rank_dict or None
    return domain_rank_dict.get(domain)


def calculate_trust_score(current_score, feature, value):
    # Simple heuristic scoring example:
    # Deduct points if phishing or shortened URL, add for age, etc.
    if feature == 'domain_rank':
        if value is None:
            return current_score - 5
        elif isinstance(value, int):
            if value < 100000:
                return current_score + 10
            else:
                return current_score - 5
    elif feature == 'domain_age':
        if value == 'Not Given':
            return current_score - 10
        elif isinstance(value, (int, float)):
            if value > 1:
                return current_score + 10
            else:
                return current_score - 5
    elif feature == 'is_url_shortened':
        if value == 1:
            return current_score - 15
    elif feature == 'hsts_support':
        if value:
            return current_score + 10
        else:
            return current_score - 10
    elif feature == 'ip_present':
        if value:
            return current_score - 20
    elif feature == 'url_redirects':
        if value > 3:
            return current_score - 10
    elif feature == 'too_long_url':
        if value:
            return current_score - 10
    elif feature == 'too_deep_url':
        if value:
            return current_score - 10
    return current_score



def whois_data(domain):
    try:
        w = whois.whois(domain)
        if hasattr(w, 'creation_date') and w.creation_date:
            creation = w.creation_date
            if isinstance(creation, list):
                creation = creation[0]
            age_years = (datetime.datetime.now() - creation).days / 365.0

            # Convert WHOIS data object to dictionary and filter out None values
            whois_dict = {}
            for key, value in w.items():
                if value is not None:
                    # Convert lists to strings for better display in template
                    if isinstance(value, list):
                        whois_dict[key] = ', '.join(str(v) for v in value)
                    else:
                        whois_dict[key] = str(value)
            
            return {'age': round(age_years, 1), 'data': whois_dict}
        else:
            return {'age': 'Not Given', 'data': {'Error': 'No WHOIS data available'}}
    except Exception as e:
        return {'age': 'Not Given', 'data': {'Error': f'WHOIS lookup failed: {str(e)}'}}



def is_url_shortened(url):
    for shortener in url_shorteners:
        if shortener in url:
            return 1
    return 0


def hsts_support(url):
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname
        context = ssl_lib.create_default_context()
        with socket.create_connection((hostname, 443), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                # Check if HSTS present in headers or cert extensions (simplified here)
                return True
    except Exception:
        return False


def ip_present(url):
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname
        # Check if hostname is an IP address
        socket.inet_aton(hostname)
        return True
    except Exception:
        return False


def url_redirects(url):
    try:
        resp = requests.get(url, timeout=5)
        return len(resp.history)
    except Exception:
        return 0


def too_long_url(url):
    return len(url) > 75


def too_deep_url(url):
    try:
        parsed = urllib.parse.urlparse(url)
        path = parsed.path
        return path.count('/') > 5
    except Exception:
        return False


def get_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except Exception:
        return 0


def get_certificate_details(domain):
    try:
        context = ssl_lib.create_default_context()
        with socket.create_connection((domain, 443), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return cert
    except Exception:
        return None
