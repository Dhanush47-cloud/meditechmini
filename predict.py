# predict.py

import joblib

# 1. Load the trained model
model = joblib.load("department_classifier.pkl")

def predict_department(symptoms_text):
    """
    Takes a string of symptoms and predicts the department.
    """
    prediction = model.predict([symptoms_text])
    return prediction[0]

# 2. Test example
if __name__ == "__main__":
    sample_symptoms = "fever, headache"
    dept = predict_department(sample_symptoms)
    print(f"Predicted Department: {dept}")
