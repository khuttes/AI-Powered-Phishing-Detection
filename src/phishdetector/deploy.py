"""Deployment example: simple Flask inference service."""
try:
    from flask import Flask, request, jsonify, render_template
except ImportError:
    raise ImportError('Flask is required; install via requirements.txt')
import joblib
try:
    import pandas as pd
except ImportError:
    raise ImportError('pandas is required; install via requirements.txt')
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
model = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    df = pd.DataFrame([data])
    # assume schema has same fields
    from phishdetector import features
    X = features.assemble_features(df)
    proba = model.predict_proba(X)[0,1]
    # also return the computed features for inspection
    feature_dict = X.iloc[0].to_dict()
    return jsonify({'phishing_probability': float(proba), 'features': feature_dict})


@app.route('/batch', methods=['POST'])
def batch_process():
    """Endpoint for uploading a CSV/JSON and returning scored file."""
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'no file provided'}), 400
    df = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_json(file, lines=True)
    from phishdetector import features
    X = features.assemble_features(df)
    proba = model.predict_proba(X)[:,1]
    df['phish_prob'] = proba
    output_dir = os.path.join('data', 'processed')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'batch_scored.csv')
    df.to_csv(output_path, index=False)
    return jsonify({'output': output_path})


def load_model(path):
    global model
    model = joblib.load(path)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run inference service or batch prediction')
    parser.add_argument('model', help='Path to trained model')
    parser.add_argument('--serve', action='store_true', help='Start REST API server with UI')
    parser.add_argument('--input', help='Path to CSV/JSON file for batch scoring')
    parser.add_argument('--output', help='Output file for batch predictions')
    args = parser.parse_args()
    load_model(args.model)
    if args.serve:
        app.run(host='0.0.0.0', port=5000)
    elif args.input and args.output:
        import pandas as pd
        df = pd.read_csv(args.input) if args.input.endswith('.csv') else pd.read_json(args.input, lines=True)
        from phishdetector import features
        X = features.assemble_features(df)
        proba = model.predict_proba(X)[:,1]
        df['phish_prob'] = proba
        df.to_csv(args.output, index=False)
        print(f"Wrote predictions to {args.output}")
    else:
        print('Specify --serve to start API or --input and --output for batch scoring')
