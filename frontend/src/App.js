import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid
} from "recharts";

function App() {
  const BACKEND = "http://127.0.0.1:5000";

  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState({});
  const [frameUrl, setFrameUrl] = useState("");
  const [history, setHistory] = useState([]);
  const [alert, setAlert] = useState("");

  // 🎥 Video refresh
  useEffect(() => {
    const interval = setInterval(() => {
      setFrameUrl(`${BACKEND}/frame?${Date.now()}`);
    }, 200);
    return () => clearInterval(interval);
  }, []);

  // 📊 Summary + Alerts
  useEffect(() => {
    const interval = setInterval(() => {
      axios.get(`${BACKEND}/summary`)
        .then(res => {
          setSummary(res.data);

          // chart data
          setHistory(prev => [
            ...prev.slice(-20),
            { people: res.data.max_people || 0 }
          ]);

          // 🚨 Alert
          if (res.data.max_people >= 4) {
            setAlert("🚨 Suspicious Activity Detected!");
            setTimeout(() => setAlert(""), 3000);
          }
        })
        .catch(() => {});
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // 📤 Upload FIXED
  const upload = async () => {
    if (!file) {
      alert("Select video first");
      return;
    }

    const form = new FormData();
    form.append("file", file);

    try {
      await axios.post(`${BACKEND}/upload`, form, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      alert("✅ Upload Success");
    } catch (err) {
      console.error(err);
      alert("❌ Upload Failed");
    }
  };

  return (
    <div style={styles.container}>

      <h1 style={styles.title}>🚀 AI Surveillance System</h1>

      {/* ALERT */}
      {alert && <div style={styles.alert}>{alert}</div>}

      <div style={styles.grid}>

        {/* VIDEO */}
        <div style={styles.card}>
          <h2>🎥 Live Feed</h2>
          <img src={frameUrl} alt="video" style={styles.video} />
        </div>

        {/* ANALYTICS */}
        <div style={styles.card}>
          <h2>📊 Analytics</h2>

          <div style={styles.metric}>
            <span>👥 Max People</span>
            <h3>{summary.max_people || 0}</h3>
          </div>

          <LineChart width={300} height={200} data={history}>
            <CartesianGrid stroke="#ccc" />
            <XAxis dataKey="people" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="people" />
          </LineChart>
        </div>

      </div>

      {/* UPLOAD */}
      <div style={styles.upload}>
        <h2>📤 Upload Video</h2>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={upload} style={styles.button}>
          Upload
        </button>
      </div>

    </div>
  );
}

export default App;



// 🎨 STYLES
const styles = {
  container: {
    background: "#0f172a",
    color: "white",
    minHeight: "100vh",
    padding: "20px",
    fontFamily: "Arial"
  },

  title: {
    textAlign: "center"
  },

  grid: {
    display: "grid",
    gridTemplateColumns: "2fr 1fr",
    gap: "20px"
  },

  card: {
    background: "#1e293b",
    padding: "15px",
    borderRadius: "12px"
  },

  video: {
    width: "100%",
    borderRadius: "10px"
  },

  metric: {
    background: "#334155",
    padding: "10px",
    borderRadius: "8px",
    textAlign: "center",
    marginBottom: "10px"
  },

  upload: {
    marginTop: "20px",
    textAlign: "center"
  },

  button: {
    marginLeft: "10px",
    padding: "10px 20px",
    background: "#3b82f6",
    border: "none",
    borderRadius: "8px",
    color: "white",
    cursor: "pointer"
  },

  alert: {
    background: "red",
    padding: "10px",
    textAlign: "center",
    marginBottom: "10px",
    borderRadius: "8px",
    fontWeight: "bold"
  }
};