import pandas as pd
from phishdetector import features, urls, attachments, intent


def make_sample_df():
    return pd.DataFrame([
        {
            'sender': 'foo@bar.com',
            'display_name': 'Foo',
            'subject': 'Test',
            'body': 'Click here http://example.com',
            'attachments': ['doc.pdf'],
        }
    ])


def test_basic_header():
    df = make_sample_df()
    h = features.basic_header_features(df)
    assert 'sender_length' in h.columns
    assert h['sender_equals_display'].iloc[0] == 0
    assert 'spf_pass' in h.columns
    assert 'dkim_pass' in h.columns
    assert 'dmarc_pass' in h.columns


def test_url_features():
    df = make_sample_df()
    u = urls.suspicious_url_features(df)
    assert u['url_count'].iloc[0] == 1

def test_domain_age():
    df = make_sample_df()
    d = urls.domain_age_score(df)
    assert d.iloc[0] >= 0


def test_attachment_features():
    df = make_sample_df()
    a = attachments.suspicious_attachment_features(df)
    assert a['attachment_count'].iloc[0] == 1
    assert a['has_executable'].iloc[0] == 0


def test_intent_features(monkeypatch):
    df = make_sample_df()
    k = intent.count_keywords(df)
    assert k.iloc[0] == 0
    m = intent.is_machine_generated(df)
    assert m.iloc[0] == 0
    # patch transformer pipeline to avoid network / download
    class DummyPipe:
        def __call__(self, text):
            return [{'label': 'POSITIVE', 'score': 0.8}]
    monkeypatch.setattr(intent, '_get_intent_pipeline', lambda: DummyPipe())
    s = intent.sentiment_score(df)
    assert s.iloc[0] == 0.8
    mname = intent.mentions_name(df, names=['foo'])
    assert mname.iloc[0] == 1


def test_assemble_all(monkeypatch):
    df = make_sample_df()
    # define user names so mentions_user returns 1
    monkeypatch.setenv('USER_NAMES', 'foo')
    X = features.assemble_features(df)
    # should contain all feature columns from modules
    assert 'sender_length' in X.columns
    assert 'url_count' in X.columns
    assert 'urgency_score' in X.columns
    assert 'sentiment_score' in X.columns
    assert 'mentions_user' in X.columns
