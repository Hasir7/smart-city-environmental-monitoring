import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Activity, AlertTriangle, BellRing, CloudSun, Database, Gauge, Leaf, MapPin, Radio } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || "/api";
const INGESTION_BASE = import.meta.env.VITE_INGESTION_BASE || "/ingestion";

function App() {
  const [summary, setSummary] = useState([]);
  const [latest, setLatest] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [status, setStatus] = useState("Loading");

  async function loadData() {
    try {
      const [summaryRes, latestRes, alertsRes] = await Promise.all([
        fetch(`${API_BASE}/metrics/summary`),
        fetch(`${API_BASE}/metrics/latest`),
        fetch(`${API_BASE}/alerts`),
      ]);
      const [summaryData, latestData, alertsData] = await Promise.all([
        summaryRes.json(), latestRes.json(), alertsRes.json(),
      ]);
      setSummary(summaryData);
      setLatest(latestData);
      setAlerts(alertsData);
      setStatus("Live");
      return latestData;
    } catch {
      setStatus("API Offline");
      return null;
    }
  }

  useEffect(() => {
    let reloadId;
    async function initializeDashboard() {
      const latestReadings = await loadData();
      if (Array.isArray(latestReadings) && latestReadings.length === 0) {
        await fetch(`${INGESTION_BASE}/simulate?count=40`, { method: "POST" });
        reloadId = setTimeout(loadData, 1000);
      }
    }
    initializeDashboard();
    const id = setInterval(loadData, 5000);
    return () => {
      clearInterval(id);
      clearTimeout(reloadId);
    };
  }, []);

  const totalReadings = useMemo(
    () => summary.reduce((sum, item) => sum + Number(item.total_readings || 0), 0),
    [summary]
  );

  const formatMetric = (metric) =>
    metric.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

  return (
    <main className="dashboard">
      <header className="hero">
        <div className="hero-copy">
          <div className="brand-mark" aria-hidden="true"><Leaf size={24} /></div>
          <div>
            <p className="eyebrow">Smart City Environmental Intelligence</p>
            <h1>India Smart City Environmental Report</h1>
            <p className="subtitle">Near real-time air quality, noise, temperature, and humidity monitoring across Indian city zones.</p>
          </div>
        </div>
        <div className="hero-meta">
          <div className={`api-status ${status === "Live" ? "live" : ""}`}>
            <span className="status-dot" />{status}
          </div>
          <div className="status-chips" aria-label="Report status">
            <span><Radio size={14} /> Near Real-Time</span>
            <span><MapPin size={14} /> India Zones</span>
            <span><Activity size={14} /> Monitoring Active</span>
          </div>
        </div>
      </header>

      <section className="kpis">
        <article className="kpi-card kpi-blue">
          <div className="kpi-icon"><Database /></div>
          <div><span>Total Sensor Readings</span><strong>{totalReadings.toLocaleString()}</strong><small>Captured in the last 24 hours</small></div>
        </article>
        <article className="kpi-card kpi-green">
          <div className="kpi-icon"><AlertTriangle /></div>
          <div><span>Active Environmental Alerts</span><strong>{alerts.length}</strong><small>Threshold events requiring attention</small></div>
        </article>
        <article className="kpi-card kpi-teal">
          <div className="kpi-icon"><CloudSun /></div>
          <div><span>Metrics Monitored</span><strong>{summary.length}</strong><small>Environmental indicators online</small></div>
        </article>
      </section>

      <section className="content-grid">
        <div className="panel chart-panel">
          <div className="panel-heading">
            <div><p className="section-label">Environmental overview</p><h2>24-Hour Metric Summary</h2></div>
            <span className="period-chip">Average values</span>
          </div>
          {summary.length === 0 ? (
            <div className="empty-state chart-empty"><Activity /><strong>Waiting for metric data</strong><span>The chart will appear as soon as sensor readings arrive.</span></div>
          ) : (
            <div className="chart-canvas">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={summary} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
                  <defs><linearGradient id="metricBar" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#0ea5a4" /><stop offset="100%" stopColor="#2563eb" /></linearGradient></defs>
                  <CartesianGrid stroke="#e5edf3" strokeDasharray="4 6" vertical={false} />
                  <XAxis dataKey="metric" tickFormatter={formatMetric} tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip labelFormatter={formatMetric} cursor={{ fill: "#eff8f7" }} />
                  <Bar dataKey="average_value" name="Average" fill="url(#metricBar)" radius={[8, 8, 2, 2]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="panel alerts-panel">
          <div className="panel-heading"><div><p className="section-label">Attention required</p><h2>Recent Alerts</h2></div><BellRing size={20} /></div>
          {alerts.length === 0 ? (
            <div className="empty-state alert-empty"><Leaf /><strong>All conditions look stable</strong><span>No environmental threshold alerts are active.</span></div>
          ) : (
            <div className="alert-list">
              {alerts.map((alert) => (
                <div className="alert" key={alert.alert_id}>
                  <div className="alert-icon"><Gauge /></div>
                  <div><strong>{alert.zone}</strong><span>{alert.message}</span></div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="panel readings-panel">
        <div className="panel-heading">
          <div><p className="section-label">Live sensor network</p><h2>Latest Sensor Readings</h2></div>
          <span className="reading-count">{latest.length} recent records</span>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Sensor</th><th>Zone</th><th>Metric</th><th>Value</th><th>Time</th></tr></thead>
            <tbody>
              {latest.length === 0 ? (
                <tr className="empty-row"><td colSpan="5"><div className="empty-state"><Radio /><strong>Waiting for sensor readings</strong><span>New readings will appear here automatically.</span></div></td></tr>
              ) : (
                latest.map((reading) => (
                  <tr key={reading.reading_id}>
                    <td><span className="sensor-id">{reading.sensor_id}</span></td>
                    <td><span className="zone-cell"><MapPin size={14} />{reading.zone}</span></td>
                    <td><span className="metric-chip">{formatMetric(reading.metric)}</span></td>
                    <td><strong className="value-cell">{reading.value} <small>{reading.unit}</small></strong></td>
                    <td>{new Date(reading.recorded_at).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
