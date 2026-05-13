import { useState } from "react";
import axios from "axios";

export default function Clinical() {
  const [form, setForm] = useState({
    age: "",
    sex: "",
    cp: "",
    trestbps: "",
    chol: "",
    fbs: "",
    restecg: "",
    thalach: "",
    exang: "",
    oldpeak: "",
    slope: "",
    ca: "",
    thal: ""
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    try {
      setLoading(true);

      const payload = {};
      Object.keys(form).forEach((key) => {
        payload[key] = Number(form[key]);
      });

      const res = await axios.post(
        "http://localhost:5000/api/predict/clinical",
        payload
      );

      setResult(res.data);
    } catch (err) {
      console.log(err.response?.data);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#fffaf0",
        padding: "40px",
        fontFamily: "Arial, sans-serif"
      }}
    >
      <div
        style={{
          maxWidth: "820px",
          margin: "auto",
          background: "#ffffff",
          borderRadius: "20px",
          padding: "30px",
          boxShadow: "0 12px 30px rgba(0,0,0,0.08)"
        }}
      >
        <h1
          style={{
            textAlign: "center",
            color: "#9a3412",
            marginBottom: "10px"
          }}
        >
          Clinical AI Cancer Detection
        </h1>

        <p
          style={{
            textAlign: "center",
            color: "#666",
            marginBottom: "28px"
          }}
        >
          Predict cancer-related risk using patient clinical values.
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "15px"
          }}
        >
          {Object.keys(form).map((k) => (
            <input
              key={k}
              type="number"
              step="any"
              placeholder={k}
              value={form[k]}
              onChange={(e) =>
                setForm({ ...form, [k]: e.target.value })
              }
              style={{
                padding: "12px",
                borderRadius: "10px",
                border: "1px solid #d6d3d1",
                fontSize: "15px"
              }}
            />
          ))}
        </div>

        <button
          onClick={submit}
          disabled={loading}
          style={{
            width: "100%",
            marginTop: "25px",
            padding: "14px",
            border: "none",
            borderRadius: "12px",
            background: "#b45309",
            color: "#fff",
            fontSize: "16px",
            cursor: "pointer"
          }}
        >
          {loading ? "Analyzing..." : "Run Clinical Prediction"}
        </button>

        {result && (
          <div
            style={{
              marginTop: "28px",
              background:
                result.prediction === "High Risk"
                  ? "#fee2e2"
                  : result.prediction === "Mid Risk"
                  ? "#fef3c7"
                  : "#dcfce7",
              padding: "22px",
              borderRadius: "16px",
              color: "#111827",
              border: "1px solid #e5e7eb"
            }}
          >
            <h2
              style={{
                marginTop: 0,
                marginBottom: "14px",
                fontSize: "32px",
                fontWeight: "700",
                textAlign: "center",
                color:
                  result.prediction === "High Risk"
                    ? "#b91c1c"
                    : result.prediction === "Mid Risk"
                    ? "#92400e"
                    : "#166534"
              }}
            >
              {result.prediction}
            </h2>

            <p style={{ fontSize: "20px", margin: "10px 0" }}>
              <strong>Risk Probability:</strong>{" "}
              {result.risk_probability}
            </p>

            <p style={{ fontSize: "20px", margin: "10px 0" }}>
              <strong>Confidence:</strong>{" "}
              {result.confidence}
            </p>

            <p style={{ fontSize: "20px", margin: "10px 0" }}>
              <strong>Model Score:</strong>{" "}
              {result.score}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}