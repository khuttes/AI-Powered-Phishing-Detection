"""URL and link-based feature extraction."""
import pandas as pd
import re
from urllib.parse import urlparse


def extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc
    except Exception:
        return ''


def count_urls(df: pd.DataFrame) -> pd.Series:
    """Count number of URLs in the body field."""
    return df['body'].astype(str).str.count(r'https?://')


def suspicious_url_features(df: pd.DataFrame) -> pd.DataFrame:
    """Basic URL structure features: length, use of IP, punycode, etc."""
    urls_count = count_urls(df)
    out = pd.DataFrame()
    out['url_count'] = urls_count
    # placeholder: check if body contains IP addresses in URLs
    out['has_ip_url'] = df['body'].astype(str).str.contains(r'https?://\d+\.\d+\.\d+\.\d+', regex=True).astype(int)
    # average url length
    def avg_len(text):
        urls = re.findall(r'https?://[^\s]+', str(text))
        if not urls:
            return 0
        return sum(len(u) for u in urls) / len(urls)
    out['avg_url_length'] = df['body'].apply(avg_len)
    return out


def domain_age_score(df: pd.DataFrame) -> pd.Series:
    """Stub: assign a fake domain age score based on presence of known domains."""
    # in a real system we'd query WHOIS or a database
    def score(text):
        if 'example.com' in str(text):
            return 3650  # 10 years
        return 0
    return df['body'].apply(score)
