"""Training script for phishing model."""
import argparse
import joblib
import os

# dependencies are imported within main to provide clearer error messages


def main(args):
    try:
        import pandas as pd
    except ImportError as e:
        print('Missing dependency:', e)
        print('Run `pip install -r requirements.txt` before training.')
        raise

    from phishdetector import data_ingest, features, model


def main(args):
    df = data_ingest.load_emails(args.input)
    df = data_ingest.clean_headers(df)
    print(f"loaded {len(df)} records from {args.input}")
    X = features.assemble_features(df)
    y = df[args.label]
    print(f"feature matrix shape: {X.shape}")

    clf = model.build_classifier()
    clf.fit(X, y)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    joblib.dump(clf, args.output)
    print(f"Model saved to {args.output}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train phishing detector')
    parser.add_argument('--input', required=True, help='Path to labeled email data')
    parser.add_argument('--label', default='is_phish', help='Label column')
    parser.add_argument('--output', default='models/phish_model.pkl', help='Output model path')
    args = parser.parse_args()
    main(args)
