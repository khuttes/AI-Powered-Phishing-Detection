"""Evaluation utilities."""
# check dependencies at runtime
try:
    from sklearn.metrics import classification_report, confusion_matrix
except ImportError:
    raise ImportError('sklearn is required; install via requirements.txt')
import joblib

try:
    import pandas as pd
except ImportError:
    raise ImportError('pandas is required; install via requirements.txt')


def evaluate_model(clf, X, y):
    preds = clf.predict(X)
    print(classification_report(y, preds))
    print('Confusion matrix:')
    print(confusion_matrix(y, preds))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Evaluate phishing model')
    parser.add_argument('--model', required=True, help='Path to trained model')
    parser.add_argument('--data', required=True, help='Path to labeled test data')
    parser.add_argument('--label', default='is_phish', help='Label column name')
    args = parser.parse_args()

    clf = joblib.load(args.model)
    df = pd.read_csv(args.data) if args.data.endswith('.csv') else pd.read_json(args.data, lines=True)
    from phishdetector import features
    X = features.assemble_features(df)
    evaluate_model(clf, X, df[args.label])
