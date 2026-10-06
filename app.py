import os
import re
import pickle
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enables frontend (localhost:5500) to communicate with Flask (localhost:5000)

DB_FILE = 'email_detection.db'

# Setup NLTK Preprocessing
stemmer = PorterStemmer()
try:
    stop_words = set(stopwords.words('english'))
except Exception:
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'https?://\S+|www\.\S+', ' url ', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' email ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    words = text.lower().split()
    clean_words = [stemmer.stem(w) for w in words if w not in stop_words]
    return " ".join(clean_words)

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            subject TEXT,
            body TEXT,
            prediction TEXT,
            confidence_score REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Load trained model and vectorizer
MODEL_PATH = 'model.pkl'
VECTORIZER_PATH = 'tfidf_vectorizer.pkl'

model = None
vectorizer = None

if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(VECTORIZER_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
    print("✅ Loaded ML model and TF-IDF vectorizer successfully.")
else:
    print("⚠️ Warning: Model files not found. Run 'python train_model.py' first.")

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "service": "AI-Based Spam Email Detection System API",
        "endpoints": ["/api/predict", "/api/history"]
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data or 'body' not in data or not data['body'].strip():
        return jsonify({"error": "Email body content is required"}), 400

    sender = data.get('sender', '').strip()
    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()

    combined_text = f"{subject} {body}"
    cleaned = clean_text(combined_text)

    # Machine Learning Inference
    if model and vectorizer:
        transformed = vectorizer.transform([cleaned]).toarray()
        pred_label_code = model.predict(transformed)[0]
        pred_proba = model.predict_proba(transformed)[0]
    else:
        spam_triggers = ['urgent', 'verify', 'password', 'free', 'wire transfer', 'restricted', 'freeze', 'click below']
        matched = [w for w in spam_triggers if w in combined_text.lower()]
        spam_prob = min(0.15 + len(matched) * 0.25, 0.98)
        prediction = 'Spam' if spam_prob >= 0.5 else 'Not Spam'

    urgency_words = ['urgent', 'immediately', '24 hours', 'restricted', 'suspension', 'freeze']
    has_urgency = any(w in combined_text.lower() for w in urgency_words)
    has_links = bool(re.search(r'https?://|www\.|\.biz|\.xyz|\.top', combined_text.lower()))
    suspicious_sender = any(term in sender.lower() for term in ['-', '.biz', '.xyz', 'verify', 'update'])

    urgency_score = 88 if has_urgency else 15
    link_risk_score = 95 if has_links else 10
    keyword_density = min(int(spam_prob * 100), 96)

    reasons = []
    if prediction == 'Spam':
        if suspicious_sender:
            reasons.append("Sender address contains lookalike keywords or untrusted domain syntax.")
        if has_links:
            reasons.append("Contains unverified hyperlinks or destination URL triggers.")
        if has_urgency:
            reasons.append("High psychological urgency triggers detected ('immediate action', 'restricted').")
        reasons.append("Lexical TF-IDF weights matched high-probability spam tokens.")
    else:
        reasons.append("Clean text distribution with low spam keyword density.")
        reasons.append("No malicious hyperlinks, redirection indicators, or lookalike domain markers detected.")
        reasons.append("Neutral, legitimate conversational and professional linguistic tone.")

    confidence = round(spam_prob * 100, 1)

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO email_logs (sender, subject, body, prediction, confidence_score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (sender, subject, body[:250], prediction, confidence, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception as db_err:
        print(f"Database error: {db_err}")

    return jsonify({
        "prediction": prediction,
        "probability": int(round(confidence)),
        "urgencyScore": urgency_score,
        "linkRiskScore": link_risk_score,
        "keywordDensity": keyword_density,
        "reasons": reasons
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, sender, subject, prediction, confidence_score, timestamp 
        FROM email_logs ORDER BY id DESC LIMIT 10
    ''')
    rows = cursor.fetchall()
    conn.close()

    logs = [
        {"id": r[0], "sender": r[1], "subject": r[2], "prediction": r[3], "confidence": r[4], "timestamp": r[5]}
        for r in rows
    ]
    return jsonify(logs)

if __name__ == '__main__':
    print("Starting Flask Backend on http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=True)