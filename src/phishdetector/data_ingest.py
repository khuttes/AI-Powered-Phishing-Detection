"""Data ingestion utilities for phishing detector."""
import pandas as pd


def load_emails(path: str) -> pd.DataFrame:
    """Load raw email data from CSV or JSON."""
    if path.endswith('.csv'):
        return pd.read_csv(path)
    elif path.endswith('.json'):
        return pd.read_json(path, lines=True)
    else:
        raise ValueError('Unsupported file format')


def clean_headers(df: pd.DataFrame) -> pd.DataFrame:
    """Perform minimal cleaning on headers."""
    # placeholder: drop NA, normalize columns
    return df.dropna(subset=['sender', 'subject'])
