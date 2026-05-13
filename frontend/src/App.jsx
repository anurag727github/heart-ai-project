import { Routes, Route, NavLink } from "react-router-dom";
import Home from "./pages/Home";
import Clinical from "./pages/Clinical";
import Imaging from "./pages/Imaging";
import Fusion from "./pages/Fusion";

export default function App() {
  const linkStyle = ({ isActive }) => ({
    textDecoration: "none",
    padding: "10px 16px",
    borderRadius: "10px",
    fontWeight: "600",
    color: isActive ? "#ffffff" : "#7c2d12",
    background: isActive ? "#b45309" : "transparent"
  });

  return (
    <div>
      <nav
        style={{
          display: "flex",
          justifyContent: "space-between",
          padding: "18px 30px",
          background: "#fff7ed",
          borderBottom: "1px solid #fed7aa"
        }}
      >
        <h2 style={{ margin: 0, color: "#9a3412" }}>
          AI Cancer Detection
        </h2>

        <div style={{ display: "flex", gap: "10px" }}>
          <NavLink to="/" style={linkStyle}>Home</NavLink>
          <NavLink to="/clinical" style={linkStyle}>Clinical</NavLink>
          <NavLink to="/imaging" style={linkStyle}>Imaging</NavLink>
          <NavLink to="/fusion" style={linkStyle}>Fusion</NavLink>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/clinical" element={<Clinical />} />
        <Route path="/imaging" element={<Imaging />} />
        <Route path="/fusion" element={<Fusion />} />
      </Routes>
    </div>
  );
}