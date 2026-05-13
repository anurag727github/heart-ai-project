import { useState } from "react";
import axios from "axios";

export default function Imaging() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const selectFile = (e) => {
    const chosen = e.target.files[0];
    setFile(chosen);

    if (chosen) {
      setPreview(URL.createObjectURL(chosen));
    }
  };

  const submit = async () => {
    try {
      if (!file) {
        alert("Please upload an image first.");
        return;
      }

      setLoading(true);

      const fd = new FormData();
      fd.append("file", file);

      const res = await axios.post(
        "http://localhost:5000/api/predict/image",
        fd
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
          maxWidth: "780px",
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
          Imaging AI Cancer Detection
        </h1><br />

        <p
          style={{
            textAlign: "center",
            color: "#666",
            marginBottom: "26px"
          }}
        >
          Upload a medical image and let Artificial Intelligence detect
          suspicious cancer patterns with confidence score.
        </p>

        <div
          style={{
            border: "2px dashed #fdba74",
            borderRadius: "16px",
            padding: "25px",
            textAlign: "center",
            background: "#fff7ed"
          }}
        >
          <input
            type="file"
            accept="image/*"
            onChange={selectFile}
          />
        </div>

        {preview && (
          <div style={{ marginTop: "22px", textAlign: "center" }}>
            <img
              src={preview}
              alt="Preview"
              style={{
                maxWidth: "100%",
                maxHeight: "340px",
                borderRadius: "16px",
                boxShadow: "0 8px 20px rgba(0,0,0,0.08)"
              }}
            />
          </div>
        )}

        <button
          onClick={submit}
          disabled={loading}
          style={{
            width: "100%",
            marginTop: "24px",
            padding: "14px",
            border: "none",
            borderRadius: "12px",
            background: "#b45309",
            color: "#fff",
            fontSize: "16px",
            cursor: "pointer"
          }}
        >
          {loading ? "Analyzing..." : "Run Image Prediction"}
        </button>

        {result && (
          <div
            style={{
              marginTop: "28px",
              background:
                result.prediction === "Cancer"
                  ? "#fee2e2"
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
                  result.prediction === "Cancer"
                    ? "#b91c1c"
                    : "#166534"
              }}
            >
              {result.prediction}
            </h2>

            <p style={{ fontSize: "20px", margin: "10px 0" }}>
              <strong>Confidence:</strong>{" "}
              {result.confidence}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}