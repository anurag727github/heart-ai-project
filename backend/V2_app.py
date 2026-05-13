import os

# 1. HIDE TENSORFLOW LOGS (Must be set before importing tensorflow)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model

app = Flask(__name__)
CORS(app)

# --- Industry Standard Weights ---
# Clinical data is statistically more reliable (65%) than basic image classification (35%)
# for heart disease prediction in hybrid models.
CLINICAL_WEIGHT = 0.65
IMAGE_WEIGHT = 0.35

# --- Robust Model Pathing ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Assumes structure: backend/app.py and models/ sitting in root
CLINICAL_PATH = os.path.join(BASE_DIR, "..", "models", "clinical_model.pkl")
IMAGE_PATH = os.path.join(BASE_DIR, "..", "models", "image_model.keras")

# Load Models with Error Handling
try:
    clinical_model = joblib.load(CLINICAL_PATH)
    image_model = load_model(IMAGE_PATH)
    print("✅ Models loaded successfully from models/ directory")
except Exception as e:
    print(f"❌ Error loading models: {e}")

# ---------------- HOME ----------------
@app.route("/")
def home():
    return jsonify({"status": "Backend Running", "api_version": "1.0.0"})

# ---------------- CLINICAL PREDICTION ----------------
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

        # predict_proba returns probability for both classes [0, 1]
        # We take index 1 for the probability of heart disease
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
            "confidence": f"{conf:.2f}%",
            "raw_probability": prob
        })

    except Exception as e:
        return jsonify({"error": f"Clinical Error: {str(e)}"}), 400


# ---------------- IMAGE PREDICTION ----------------
@app.route("/api/predict/image", methods=["POST"])
def predict_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        img = Image.open(file.stream).convert("RGB")
        img = img.resize((224, 224))

        # Normalize pixel values to [0, 1][cite: 2]
        arr = np.array(img) / 255.0
        arr = np.expand_dims(arr, axis=0)

        # image_model usually returns a single probability in the first index
        pred = float(image_model.predict(arr, verbose=0)[0][0])

        if pred >= 0.5:
            label = "High Risk (Visual Indicators)"
            conf = pred * 100
        else:
            label = "Low Risk (Visual Indicators)"
            conf = (1 - pred) * 100

        return jsonify({
            "prediction": label,
            "confidence": f"{conf:.2f}%",
            "raw_probability": pred
        })

    except Exception as e:
        return jsonify({"error": f"Image Error: {str(e)}"}), 400


# ---------------- LATE FUSION (Hybrid Implementation) ----------------
@app.route("/api/predict/fusion", methods=["POST"])
def predict_fusion():
    try:
        # Fusion uses multipart/form-data to handle both text and image
        data = request.form
        
        # 1. Prepare Clinical Data
        input_data = {
            "age": float(data["age"]), "sex": float(data["sex"]),
            "cp": float(data["cp"]), "trestbps": float(data["trestbps"]),
            "chol": float(data["chol"]), "fbs": float(data["fbs"]),
            "restecg": float(data["restecg"]), "thalach": float(data["thalach"]),
            "exang": float(data["exang"]), "oldpeak": float(data["oldpeak"]),
            "slope": float(data["slope"]), "ca": float(data["ca"]),
            "thal": float(data["thal"])
        }
        df_fusion = pd.DataFrame([input_data])

        # 2. Prepare Image Data
        if "file" not in request.files:
            return jsonify({"error": "Missing image file for fusion"}), 400
        
        file = request.files["file"]
        img = Image.open(file.stream).convert("RGB")
        img = img.resize((224, 224))
        arr = np.array(img) / 255.0
        arr = np.expand_dims(arr, axis=0)

        # 3. Extract Probabilities from both models
        # Clinical Model Probability (Class 1)
        clinical_prob = float(clinical_model.predict_proba(df_fusion)[0][1])
        # Image Model Probability[cite: 2]
        image_prob = float(image_model.predict(arr, verbose=0)[0][0])

        # 4. Apply Weighted Late Fusion Logic
        # This combines the strengths of tabular bio-markers and visual indicators[cite: 1, 2]
        final_prob = (clinical_prob * CLINICAL_WEIGHT) + (image_prob * IMAGE_WEIGHT)

        # 5. Risk Stratification based on Fusion Score
        if final_prob < 0.30:
            risk = "Low Risk"
        elif final_prob < 0.70:
            risk = "Moderate Risk"
        else:
            risk = "High Risk (Immediate Consultation Recommended)"

        return jsonify({
            "prediction": risk,
            "fusion_confidence": f"{final_prob * 100:.2f}%",
            "clinical_contribution": f"{clinical_prob * 100:.2f}%",
            "imaging_contribution": f"{image_prob * 100:.2f}%",
            "status": "Multi-Modal Fusion Success"
        })

    except Exception as e:
        return jsonify({"error": f"Fusion Pipeline Error: {str(e)}"}), 400


if __name__ == "__main__":
    # Host 0.0.0.0 allows connections from other devices on local network
    app.run(debug=True, host="0.0.0.0", port=5000)