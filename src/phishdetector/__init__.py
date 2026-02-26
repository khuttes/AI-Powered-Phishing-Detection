"""Top-level package for phishing detector."""

from . import data_ingest, features, model, train, evaluate, deploy, urls, attachments, intent

__all__ = [
    'data_ingest', 'features', 'model', 'train', 'evaluate', 'deploy',
    'urls', 'attachments', 'intent'
]
