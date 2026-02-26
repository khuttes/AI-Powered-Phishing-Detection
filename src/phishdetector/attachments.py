"""Attachment-related feature extraction."""
import pandas as pd


def attachment_count(df: pd.DataFrame) -> pd.Series:
    """Count attachments (assuming "attachments" column is list-like)."""
    return df['attachments'].apply(lambda x: len(x) if isinstance(x, (list, tuple)) else 0)


def suspicious_attachment_features(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    out['attachment_count'] = attachment_count(df)
    # look for executable file types
    def has_exe(lst):
        if not isinstance(lst, (list, tuple)):
            return 0
        for name in lst:
            if isinstance(name, str) and name.lower().endswith(('.exe', '.scr', '.bat', '.js')):
                return 1
        return 0
    out['has_executable'] = df['attachments'].apply(has_exe)
    return out
