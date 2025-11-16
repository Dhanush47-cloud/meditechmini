from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import re
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ------------------------------------------------------------
# LOAD MODELS
# ------------------------------------------------------------

# Department Classification ML model
model = joblib.load("department_classifier.pkl")

# Diagnosis Prediction ML model
#diagnosis_model = joblib.load("diagnosis_model.pkl")

# Load department questions
with open("dept_questions.json") as f:
    dept_questions = json.load(f)

# Ensure folder exists
os.makedirs("patient_records", exist_ok=True)


# ------------------------------------------------------------
# 1️⃣ PREDICT DEPARTMENT + CREATE PATIENT RECORD
# ------------------------------------------------------------
@app.route("/predict_department", methods=["POST"])
def predict():
    data = request.json
    symptoms = data.get("symptoms", "").strip()
    name = data.get("name", "Unknown")
    age = data.get("age", "N/A")

    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400

    if symptoms.isdigit() or len(symptoms) < 3 or len(symptoms) > 150:
        return jsonify({"department": "Invalid symptom"}), 200

    if not re.search("[a-zA-Z]", symptoms):
        return jsonify({"department": "Invalid symptom"}), 200

    try:
        prediction = model.predict([symptoms])[0]

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba([symptoms])[0]
            confidence = max(probabilities)
        else:
            confidence = 1.0

        if confidence < 0.4:
            department = "Unknown"
            questions = []
        else:
            department = prediction
            questions = dept_questions.get(department, {}).get("priority_questions", [])

        # --- Save patient record ---
        patient_data = {
            "patient_id": f"P{int(datetime.now().timestamp())}",
            "name": name,
            "age": age,
            "symptoms": symptoms,
            "department": department,
            "questions": questions,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        file_path = os.path.join("patient_records", f"{patient_data['patient_id']}.json")
        with open(file_path, "w") as f:
            json.dump(patient_data, f, indent=4)

        return jsonify({
            "department": department,
            "confidence": round(float(confidence), 2),
            "questions": questions,
            "patient_id": patient_data["patient_id"],
            "patient_file": file_path
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------
# 2️⃣ SAVE ANSWERS TO EXISTING PATIENT FILE
# ------------------------------------------------------------
@app.route("/save_answers", methods=["POST"])
def save_answers():
    data = request.json
    patient_id = data.get("patient_id")
    answers = data.get("answers", {})

    if not patient_id or answers is None:
        return jsonify({"error": "Missing patient_id or answers"}), 400

    file_path = os.path.join("patient_records", f"{patient_id}.json")

    if not os.path.exists(file_path):
        return jsonify({"error": "Patient record not found"}), 404

    with open(file_path, "r") as f:
        patient_data = json.load(f)

    patient_data["answers"] = answers

    with open(file_path, "w") as f:
        json.dump(patient_data, f, indent=4)

    return jsonify({"message": "Answers saved successfully", "file": file_path})


# ------------------------------------------------------------
# 3️⃣ FETCH APPOINTMENTS FOR EACH DOCTOR
# ------------------------------------------------------------
@app.route("/get_appointments/<department>", methods=["GET"])
def get_appointments(department):
    records = []
    folder = "patient_records"

    for file_name in os.listdir(folder):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder, file_name)
            with open(file_path, "r") as f:
                data = json.load(f)

            if data.get("department", "").lower() == department.lower():
                records.append(data)

    return jsonify(records)


# ------------------------------------------------------------
# 4️⃣ ML-BASED AI DIAGNOSIS
# ------------------------------------------------------------


# ------------------------------------------------------------
# Run server
# ------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
