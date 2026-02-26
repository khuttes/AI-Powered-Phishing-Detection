import os
import joblib
import pandas as pd
from phishdetector import train, data_ingest, features

def test_training_temp(tmp_path):
    # use sample data
    sample = pd.read_csv('data/raw/sample_emails.csv')
    out_model = tmp_path / 'model.pkl'
    # save sample to temp csv
    tmp_csv = tmp_path / 'sample.csv'
    sample.to_csv(tmp_csv, index=False)

    # run training
    train_args = type('A', (), {'input': str(tmp_csv), 'label': 'is_phish', 'output': str(out_model)})
    train.main(train_args)
    assert out_model.exists()
    clf = joblib.load(out_model)
    X = features.assemble_features(sample)
    preds = clf.predict(X)
    assert len(preds) == len(sample)
