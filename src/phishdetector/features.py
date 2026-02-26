"""Feature extraction for phishing classifier."""
import pandas as pd
import numpy as np


def basic_header_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute simple header-based features including authentication results."""
    out = pd.DataFrame()
    out['sender_length'] = df['sender'].astype(str).apply(len)
    out['subject_length'] = df['subject'].astype(str).apply(len)
    # spoof: display vs actual
    out['sender_equals_display'] = df.apply(
        lambda r: str(r.get('sender', '')).lower() == str(r.get('display_name', '')).lower(),
        axis=1
    ).astype(int)
    # authentication columns may be present
    for col in ['spf_pass', 'dkim_pass', 'dmarc_pass']:
        if col in df.columns:
            out[col] = df[col].astype(int)
        else:
            out[col] = 0
    return out


def content_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract text-based features (word counts, etc.)."""
    out = pd.DataFrame()
    out['body_length'] = df['body'].astype(str).apply(len)
    out['num_exclamations'] = df['body'].astype(str).str.count('!')
    return out


from phishdetector import urls, attachments, intent


import os


def assemble_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return combined feature matrix from all modules.

    The feature `mentions_user` will check for names provided in the
    environment variable `USER_NAMES` (comma-separated).
    """
    hdr = basic_header_features(df)
    cnt = content_features(df)
    urlf = urls.suspicious_url_features(df)
    attf = attachments.suspicious_attachment_features(df)
    # user names from environment
    user_names = os.getenv('USER_NAMES', '')
    names_list = [n.strip() for n in user_names.split(',') if n.strip()]
    intentf = pd.DataFrame({
        'urgency_score': intent.count_keywords(df),
        'machine_generated': intent.is_machine_generated(df),
        'sentiment_score': intent.sentiment_score(df),
        'mentions_user': intent.mentions_name(df, names=names_list)
    })
    # add domain age score
    url_age = urls.domain_age_score(df)
    intentf['domain_age_score'] = url_age
    frames = [hdr, cnt, urlf, attf, intentf]
    return pd.concat(frames, axis=1)
