from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model

app = Flask(__name__)
CORS(app)

# Load Models
clinical_model = joblib.load("../models/clinical_model.pkl")
image_model = load_model("../models/image_model.keras")


# ---------------- HOME ----------------
@app.route("/")
def home():
    return jsonify({"status": "Backend Running"})

# ---------------- CLINICAL ----------------
@app.route("/api/predict/clinical", methods=["POST"])
def predict_clinical():
    try:
        data = request.get_json()

        df = pd.DataFrame([{
            "age": float(data["age"]),
            "sex": float(data["sex"]),
            "cp": float(data["cp"]),
            "trestbps": float(data["trestbps"]),
            "chol": float(data["chol"]),
            "fbs": float(data["fbs"]),
            "restecg": float(data["restecg"]),
            "thalach": float(data["thalach"]),
            "exang": float(data["exang"]),
            "oldpeak": float(data["oldpeak"]),
            "slope": float(data["slope"]),
            "ca": float(data["ca"]),
            "thal": float(data["thal"])
        }])

        prob = float(clinical_model.predict_proba(df)[0][1])

        if prob < 0.35:
            risk = "Low Risk"
            conf = (1 - prob) * 100
        elif prob < 0.65:
            risk = "Mid Risk"
            conf = prob * 100
        else:
            risk = "High Risk"
            conf = prob * 100

        return jsonify({
            "prediction": risk,
            "confidence": f"{conf:.2f}%"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ---------------- IMAGE ----------------
@app.route("/api/predict/image", methods=["POST"])
def predict_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        img = Image.open(file.stream).convert("RGB")
        img = img.resize((224, 224))

        arr = np.array(img) / 255.0
        arr = np.expand_dims(arr, axis=0)

        pred = image_model.predict(arr)[0][0]

        if pred >= 0.5:
            label = "Cancer"
            conf = pred * 100
        else:
            label = "Not Cancer"
            conf = (1 - pred) * 100

        return jsonify({
            "prediction": label,
            "confidence": f"{conf:.2f}%"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

# ---------------- FUSION ----------------
@app.route("/api/predict/fusion", methods=["POST"])
def predict_fusion():
    try:
        data = request.form

        # Clinical dataframe
        df = pd.DataFrame([{
            "age": float(data["age"]),
            "sex": float(data["sex"]),
            "cp": float(data["cp"]),
            "trestbps": float(data["trestbps"]),
            "chol": float(data["chol"]),
            "fbs": float(data["fbs"]),
            "restecg": float(data["restecg"]),
            "thalach": float(data["thalach"]),
            "exang": float(data["exang"]),
            "oldpeak": float(data["oldpeak"]),
            "slope": float(data["slope"]),
            "ca": float(data["ca"]),
            "thal": float(data["thal"])
        }])

        # Clinical probability
        clinical_prob = float(clinical_model.predict_proba(df)[0][1])

        # Image prediction
        if "file" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["file"]

        img = Image.open(file.stream).convert("RGB")
        img = img.resize((224, 224))

        arr = np.array(img) / 255.0
        arr = np.expand_dims(arr, axis=0)

        image_prob = float(image_model.predict(arr)[0][0])

        # Weighted fusion
        fusion_score = (clinical_prob * 0.55) + (image_prob * 0.45)

        if fusion_score < 0.35:
            risk = "Low Risk"
        elif fusion_score < 0.65:
            risk = "Mid Risk"
        else:
            risk = "High Risk"

        return jsonify({
            "prediction": risk,
            "confidence": f"{fusion_score * 100:.2f}%",
            "clinical_score": f"{clinical_prob * 100:.2f}%",
            "image_score": f"{image_prob * 100:.2f}%"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)