import { Link } from "react-router-dom";

export default function Home() {
  const card = {
    background: "#ffffff",
    borderRadius: "18px",
    padding: "24px",
    boxShadow: "0 10px 25px rgba(0,0,0,0.08)",
    color: "#222"
  };

  const btn = {
    display: "inline-block",
    marginTop: "14px",
    padding: "10px 16px",
    borderRadius: "10px",
    background: "#b45309",
    color: "#fff",
    textDecoration: "none",
    fontWeight: "600"
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg,#fff7ed 0%,#fef3c7 50%,#fde68a 100%)",
        padding: "40px",
        fontFamily: "Arial, sans-serif"
      }}
    >
      <div style={{ maxWidth: "1100px", margin: "auto" }}>
        <div style={{ textAlign: "center", marginBottom: "45px" }}>
          <h1 style={{ fontSize: "42px", color: "#7c2d12", marginBottom: "10px" }}>
            AI Cancer Detection System
          </h1>

          <p
            style={{
              fontSize: "18px",
              color: "#78350f",
              maxWidth: "760px",
              margin: "auto",
              lineHeight: "1.7"
            }}
          >
            Smart healthcare assistant for doctors and patients using
            Artificial Intelligence to detect cancer risk through
            Clinical data, Medical Imaging, and Combined Fusion Analysis.
          </p>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))",
            gap: "25px"
          }}
        >
          <div style={card}>
            <h2 style={{ color: "#9a3412" }}>Clinical Cancer Detection</h2>
            <p style={{ lineHeight: "1.7", color: "#444" }}>
              Predict cancer-related risk using patient medical values,
              symptoms and structured clinical parameters.
            </p>
            <Link to="/clinical" style={btn}>
              Open Clinical Module
            </Link>
          </div>

          <div style={card}>
            <h2 style={{ color: "#9a3412" }}>Imaging Cancer Detection</h2>
            <p style={{ lineHeight: "1.7", color: "#444" }}>
              Upload scans or medical images and let AI analyze
              suspicious patterns with confidence score.
            </p>
            <Link to="/imaging" style={btn}>
              Open Imaging Module
            </Link>
          </div>

          <div style={card}>
            <h2 style={{ color: "#9a3412" }}>Fusion Cancer Detection</h2>
            <p style={{ lineHeight: "1.7", color: "#444" }}>
              Combine Clinical + Imaging AI outputs for stronger,
              more balanced and dependable final prediction.
            </p>
            <Link to="/fusion" style={btn}>
              Open Fusion Module
            </Link>
          </div>
        </div>

        <div
          style={{
            marginTop: "45px",
            background: "#ffffffcc",
            padding: "18px",
            borderRadius: "16px",
            textAlign: "center",
            color: "#6b7280",
            boxShadow: "0 8px 20px rgba(0,0,0,0.05)"
          }}
        >
          Designed for Clinics, Hospitals, Doctors and Patients seeking intelligent support in healthcare decisions. Powered by modern AI technologies for a healthier future.
        </div>
      </div>
    </div>
  );
}