import pandas as pd
import numpy as np
import re
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'https?://\S+|www\.\S+', ' url ', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' email ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    words = text.lower().split()
    clean_words = [stemmer.stem(w) for w in words if w not in stop_words]
    return " ".join(clean_words)

# Training dataset containing typical spam and ham emails
data = {
    'label': [
        'spam', 'spam', 'spam', 'spam', 'spam', 'spam', 'spam', 'spam',
        'ham', 'ham', 'ham', 'ham', 'ham', 'ham', 'ham', 'ham'
    ],
    'text': [
        'URGENT: Your bank account access has been restricted. Click here to verify your credentials within 24 hours to prevent suspension.',
        'Congratulations! You have won a $1,000 Walmart gift card. Claim your prize immediately by clicking the link.',
        'Action required: Update your payment information immediately or your service will be terminated.',
        'Dear customer, unauthorized login detected. Verify your account password now at our secure portal.',
        'Claim your free prize now! Exclusive offer for lottery winners. Reply with your bank wire account details.',
        'Final warning: Immediate action needed regarding your tax refund. Submit your social security number.',
        'Get rich quick with cryptocurrency investment! Guaranteed 300% returns in 48 hours. Sign up now.',
        'You have received an encrypted message. Click http://verify-secure-auth.biz to view your urgent statement.',
        'Hi Dibakar, please find attached the updated project presentation slides for our lab evaluation on Monday.',
        'Meeting reminder: Faculty department review scheduled tomorrow at 10:30 AM in Conference Hall 2.',
        'Dear students, please submit your machine learning lab reports and code repositories before Friday evening.',
        'Hey, are we still meeting in the college library today to discuss the system architecture diagram?',
        'Prof. Raghubansi Rajput has shared the revised lecture notes on Natural Language Processing and TF-IDF.',
        'Please review the attached SQLite database schema and let me know if any table constraints need updates.',
        'Thanks for sending the assignment details. I will review and get back to you by this afternoon.',
        'The academic calendar for the upcoming semester has been published on the official college notice board.'
    ]
}

df = pd.DataFrame(data)
df['cleaned_text'] = df['text'].apply(clean_text)

# TF-IDF Feature Extraction
tfidf = TfidfVectorizer(max_features=3000, ngram_range=(1, 2))
X = tfidf.fit_transform(df['cleaned_text']).toarray()
y = df['label'].map({'ham': 0, 'spam': 1})

# Train Multinomial Naive Bayes Model
clf = MultinomialNB()
clf.fit(X, y)

# Save artifacts
with open('model.pkl', 'wb') as f:
    pickle.dump(clf, f)

with open('tfidf_vectorizer.pkl', 'wb') as f:
    pickle.dump(tfidf, f)

print("model.pkl and tfidf_vectorizer.pkl created successfully.")