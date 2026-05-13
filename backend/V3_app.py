from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model

app = Flask(__name__)
CORS(app)

# Load models
clinical_model = joblib.load("models/clinical_modelV3.pkl")
image_model = load_model("models/my_custom_saved_model.keras")

# ---------------- HOME ----------------
@app.route("/")
def home():
    return jsonify({"status": "Backend Running"})


# ---------------- CLINICAL ----------------
@app.route("/api/predict/clinical", methods=["POST"])
def predict_clinical():
    try:
        data = request.json

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

        pred = int(clinical_model.predict(df)[0])

        return jsonify({
            "prediction": "High Risk" if pred == 1 else "Low Risk"
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
        img = img.resize((224,224))

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
