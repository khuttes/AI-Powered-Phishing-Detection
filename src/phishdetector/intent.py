"""Basic content and intent analysis utilities."""
import pandas as pd
import re

# placeholder for more advanced NLP (could integrate transformers)

from transformers import pipeline

URGENT_TERMS = [r'urgent', r'immediate action', r'password', r'click here', r'verify', r'account']

# lazy-loaded sentiment/intent classifier (demo)
_intent_pipeline = None

def _get_intent_pipeline():
    global _intent_pipeline
    if _intent_pipeline is None:
        # using a generic sentiment model as stand-in for intent detection
        _intent_pipeline = pipeline('sentiment-analysis')
    return _intent_pipeline



def urgency_score(text: str) -> int:
    text = str(text).lower()
    return sum(1 for term in URGENT_TERMS if term in text)


def count_keywords(df: pd.DataFrame) -> pd.Series:
    return df['body'].astype(str).apply(lambda t: urgency_score(t))


def is_machine_generated(df: pd.DataFrame) -> pd.Series:
    # stub: always 0; real implementation would call an AI detection model
    return pd.Series(0, index=df.index)


def mentions_name(df: pd.DataFrame, names=None) -> pd.Series:
    """Return 1 if the body contains any of the provided names (case-insensitive)."""
    if names is None:
        names = []
    def check(text):
        t = str(text).lower()
        return int(any(name.lower() in t for name in names))
    return df['body'].apply(check)


def sentiment_score(df: pd.DataFrame) -> pd.Series:
    """Use a transformer pipeline to score sentiment, serving as proxy for intent."""
    pipe = _get_intent_pipeline()
    scores = []
    for text in df['body'].astype(str):
        try:
            res = pipe(text[:512])[0]
            # map positive/negative to numbers
            score = res['score'] if res['label'].lower().startswith('pos') else -res['score']
        except Exception:
            score = 0.0
        scores.append(score)
    return pd.Series(scores, index=df.index)
