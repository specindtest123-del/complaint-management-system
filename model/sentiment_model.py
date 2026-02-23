import nltk
from textblob import TextBlob
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

class SentimentAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.priority_classifier = None
        
    def clean_text(self, text):
        """Clean and preprocess text"""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def analyze_sentiment(self, text):
        """Analyze sentiment using TextBlob"""
        clean_text = self.clean_text(text)
        blob = TextBlob(clean_text)
        
        # Get polarity score (-1 to 1)
        polarity = blob.sentiment.polarity
        
        # Classify sentiment
        if polarity > 0.1:
            sentiment = "Positive"
        elif polarity < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
            
        return sentiment, polarity
    
    def train_priority_model(self):
        """Train a simple priority prediction model"""
        # Sample training data
        complaints = [
            ("urgent issue system down", "Critical"),
            ("minor problem with interface", "Low"),
            ("payment not working properly", "High"),
            ("need help with feature", "Medium"),
            ("security breach detected", "Critical"),
            ("slow performance sometimes", "Low"),
            ("data loss occurred", "High"),
            ("suggestion for improvement", "Low"),
            ("account hacked", "Critical"),
            ("billing error", "High")
        ]
        
        X_text = [self.clean_text(c[0]) for c in complaints]
        y = [c[1] for c in complaints]
        
        # Vectorize text
        X = self.vectorizer.fit_transform(X_text)
        
        # Train classifier
        self.priority_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.priority_classifier.fit(X, y)
        
        # Save model
        if not os.path.exists('models'):
            os.makedirs('models')
        joblib.dump(self.vectorizer, 'models/vectorizer.pkl')
        joblib.dump(self.priority_classifier, 'models/priority_model.pkl')
        
    def predict_priority(self, title, description):
        """Predict priority based on complaint text"""
        if self.priority_classifier is None:
            # Load or train model
            try:
                self.vectorizer = joblib.load('models/vectorizer.pkl')
                self.priority_classifier = joblib.load('models/priority_model.pkl')
            except:
                self.train_priority_model()
        
        # Combine title and description
        combined_text = self.clean_text(title + " " + description)
        
        # Vectorize and predict
        X = self.vectorizer.transform([combined_text])
        priority = self.priority_classifier.predict(X)[0]
        
        return priority

# Initialize analyzer
analyzer = SentimentAnalyzer()