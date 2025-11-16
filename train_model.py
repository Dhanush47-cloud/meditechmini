# train_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib

# 1️⃣ Load dataset
data = pd.read_csv("symptoms_dataset.csv")

# Optional: inspect the first few rows
print("Sample data:\n", data.head())

# 2️⃣ Split features and target
X = data['symptoms']        # Symptoms text
y = data['department']      # Department label

# Split into training and test sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 3️⃣ Create a pipeline: TF-IDF vectorizer + Naive Bayes classifier
model = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', MultinomialNB())
])

# 4️⃣ Train the model
model.fit(X_train, y_train)

# 5️⃣ Evaluate model on test set
accuracy = model.score(X_test, y_test)
print(f"Test Accuracy: {accuracy*100:.2f}%")

# 6️⃣ Save the trained model to a file
joblib.dump(model, "department_classifier.pkl")
print("Model saved as 'department_classifier.pkl'")
