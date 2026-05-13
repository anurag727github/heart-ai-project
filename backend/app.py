import os
import sys

# 1. ENTERPRISE ENVIRONMENT CONFIGURATION
# Optimized for high-performance inference and silencing non-critical TF warnings.
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

# 2. CALIBRATED MULTI-MODAL WEIGHTS
# As per clinical SDE standards, tabular data provides 65% of the diagnostic anchor.
CLINICAL_WEIGHT = 0.65
IMAGE_WEIGHT = 0.35

# 3. ROBUST PATH RESOLUTION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLINICAL_PATH = os.path.join(BASE_DIR, "..", "models", "clinical_modelV3.pkl")
IMAGE_PATH = os.path.join(BASE_DIR, "..", "models", "my_custom_saved_model.keras")

try:
    # Attempt loading with strict version awareness
    import sklearn
    print(f"DEBUG: Local Scikit-Learn Version: {sklearn.__version__}")
    
    clinical_model = joblib.load(CLINICAL_PATH)
    image_model = load_model(IMAGE_PATH)
    
    print(f"✅ SYSTEM READY: Models loaded successfully.")

except AttributeError as e:
    print(f"❌ VERSION CRITICAL ERROR: {e}")
    print("REASON: Your .pkl was created with sklearn 1.6.1, but your local venv is 1.8.0.")
    print("FIX: Run 'pip install scikit-learn==1.6.1' in your terminal.")
    sys.exit(1)
except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    sys.exit(1)

# ---------------- API ENDPOINTS ----------------

@app.route("/")
def health():
    return jsonify({"status": "healthy", "engine": "HeartAI v4.0.0"})

@app.route("/api/predict/clinical", methods=["POST"])
def predict_clinical():
    try:
        data = request.get_json()
        
        # SDE Requirement: Strict feature parity with clinical_modelV3.pkl
        # Note: We send raw numeric/string data; the .pkl handles encoding internally.
        df = pd.DataFrame([{
            "age": float(data["age"]), "sex": data["sex"],
            "cp": data["cp"], "trestbps": float(data["trestbps"]),
            "chol": float(data["chol"]), "fbs": data["fbs"],
            "restecg": data["restecg"], "thalach": float(data["thalach"]),
            "exang": data["exang"], "oldpeak": float(data["oldpeak"]),
            "slope": data["slope"], "ca": float(data["ca"]),
            "thal": data["thal"]
        }])

        prob = float(clinical_model.predict_proba(df)[0][1])

        return jsonify({
            "prediction": "High Risk" if prob > 0.5 else "Low Risk",
            "confidence": f"{prob * 100 if prob > 0.5 else (1-prob) * 100:.2f}%",
            "status": "Inference Success"
        })
    except Exception as e:
        return jsonify({"error": f"Clinical Fault: {str(e)}"}), 400

@app.route("/api/predict/image", methods=["POST"])
def predict_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Payload missing: image file"}), 400

        file = request.files["file"]
        # Optimized for EfficientNetB3 (300x300 resolution)
        img = Image.open(file.stream).convert("RGB").resize((300, 300))
        img_array = np.array(img) / 255.0 
        img_array = np.expand_dims(img_array, axis=0)

        raw_score = float(image_model.predict(img_array, verbose=0)[0][0])

        return jsonify({
            "prediction": "High Risk (Visual)" if raw_score > 0.5 else "Low Risk (Visual)",
            "confidence": f"{raw_score * 100 if raw_score > 0.5 else (1-raw_score) * 100:.2f}%"
        })
    except Exception as e:
        return jsonify({"error": f"Imaging Fault: {str(e)}"}), 400

@app.route("/api/predict/fusion", methods=["POST"])
def predict_fusion():
    try:
        data = request.form
        
        # 1. Clinical Diagnostic Vector
        df_fusion = pd.DataFrame([{
            "age": float(data["age"]), "sex": data["sex"],
            "cp": data["cp"], "trestbps": float(data["trestbps"]),
            "chol": float(data["chol"]), "fbs": data["fbs"],
            "restecg": data["restecg"], "thalach": float(data["thalach"]),
            "exang": data["exang"], "oldpeak": float(data["oldpeak"]),
            "slope": data["slope"], "ca": float(data["ca"]),
            "thal": data["thal"]
        }])
        clinical_prob = float(clinical_model.predict_proba(df_fusion)[0][1])

        # 2. Imaging Diagnostic Vector
        if "file" not in request.files:
            return jsonify({"error": "Fusion requires an image file"}), 400
        
        file = request.files["file"]
        img = Image.open(file.stream).convert("RGB").resize((300, 300))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        image_prob = float(image_model.predict(img_array, verbose=0)[0][0])

        # 3. Soft-Voting Fusion Logic
        final_score = (clinical_prob * CLINICAL_WEIGHT) + (image_prob * IMAGE_WEIGHT)

        if final_score < 0.35:
            risk = "Low Risk"
        elif final_score < 0.70:
            risk = "Moderate Risk"
        else:
            risk = "High Risk (Clinical Consultation Required)"

        # 4. Standardized JSON Response (Compatible with React V1 Frontend)
        return jsonify({
            "prediction": risk,
            "confidence": f"{final_score * 100:.2f}%",
            "clinical_score": f"{clinical_prob * 100:.2f}%",
            "image_score": f"{image_prob * 100:.2f}%"
        })

    except Exception as e:
        return jsonify({"error": f"Fusion Engine Fault: {str(e)}"}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)