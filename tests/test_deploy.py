import pytest
import os
import joblib
import pandas as pd
from phishdetector import deploy, train, features


@pytest.fixture(scope='module')
def trained_model(tmp_path_factory):
    # train a small model using sample data
    tmpdir = tmp_path_factory.mktemp('model')
    model_path = tmpdir / 'm.pkl'
    df = pd.read_csv('data/raw/sample_emails.csv')
    train_args = type('A', (), {'input': 'data/raw/sample_emails.csv', 'label': 'is_phish', 'output': str(model_path)})
    train.main(train_args)
    return str(model_path)


def test_predict_endpoint(trained_model):
    deploy.load_model(trained_model)
    client = deploy.app.test_client()
    payload = {
        'sender': 'test@example.com',
        'display_name': 'Test',
        'subject': 'hello',
        'body': 'please click http://example.com'
    }
    resp = client.post('/predict', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'phishing_probability' in data
    assert 'features' in data


def test_batch_endpoint(trained_model, tmp_path):
    deploy.load_model(trained_model)
    client = deploy.app.test_client()
    # create a small csv using sample data
    df = pd.read_csv('data/raw/sample_emails.csv')
    file_path = tmp_path / 'in.csv'
    df.to_csv(file_path, index=False)
    with open(file_path, 'rb') as f:
        resp = client.post('/batch', data={'file': (f, 'in.csv')}, content_type='multipart/form-data')
    assert resp.status_code == 200
    json = resp.get_json()
    assert 'output' in json
    assert os.path.exists(json['output'])
