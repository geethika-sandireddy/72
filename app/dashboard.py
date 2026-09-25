"""INDRA Earth Operations console.

This is an original, premium dashboard shell for the thunderstorm/lightning
nowcasting prototype. It intentionally keeps synthetic data clearly labelled and
never presents it as live or replay data. The layout is designed for operational
weather workstations with an Earth-first hazard display and review flow.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"
HORIZONS = ["5", "15", "30", "60", "180"]
INDIA_BOUNDS = {"lat_min": 6.0, "lat_max": 38.0, "lon_min": 68.0, "lon_max": 98.0}

st.set_page_config(
    page_title="INDRA Earth Operations",
    page_icon="⛈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
      --bg: #06121d;
      --bg-2: #0b1b2b;
      --panel: rgba(13, 28, 42, 0.88);
      --panel-strong: rgba(17, 34, 48, 0.96);
      --line: rgba(117, 158, 197, 0.28);
      --text: #edf7ff;
      --muted: #9ebad1;
      --cyan: #63e4f6;
      --amber: #ffc857;
      --red: #ff6b6b;
      --green: #7ef0b0;
      --violet: #9a8cff;
      --shadow: rgba(0, 0, 0, 0.38);
    }

    html, body, [data-testid="stAppViewContainer"] {
      background:
        radial-gradient(circle at top left, rgba(47, 155, 200, 0.12), transparent 30%),
        linear-gradient(180deg, var(--bg) 0%, #07151e 100%);
      color: var(--text);
      font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
      background: rgba(7, 19, 29, 0.96);
      border-right: 1px solid var(--line);
    }

    [data-testid="stHeader"] {
      background: rgba(6, 18, 29, 0.72);
      backdrop-filter: blur(10px);
    }

    .block-container {
      max-width: 1880px;
      padding-top: 1rem;
      padding-left: 1.2rem;
      padding-right: 1.2rem;
      padding-bottom: 2rem;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      border-bottom: 1px solid var(--line);
      padding: 0 0 1rem 0;
      margin-bottom: 1rem;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 0.9rem;
    }

    .brand-badge {
      width: 46px;
      height: 46px;
      border-radius: 14px;
      display: grid;
      place-items: center;
      font-size: 1.35rem;
      background: linear-gradient(135deg, rgba(98, 228, 246, 0.9), rgba(18, 102, 188, 0.9));
      box-shadow: 0 0 28px rgba(98, 228, 246, 0.28);
      border: 1px solid rgba(152, 231, 246, 0.72);
    }

    .brand-title {
      font-size: 1.18rem;
      letter-spacing: 0.16em;
      font-weight: 800;
      text-transform: uppercase;
      margin: 0;
    }

    .brand-sub {
      margin-top: 0.18rem;
      color: var(--muted);
      font-size: 0.72rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }

    .clock {
      text-align: right;
      font-family: 'JetBrains Mono', monospace;
      color: var(--muted);
      font-size: 0.72rem;
      line-height: 1.55;
    }

    .panel {
      background: linear-gradient(180deg, rgba(15, 29, 42, 0.96), rgba(9, 19, 28, 0.96));
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: 0 12px 28px var(--shadow);
      padding: 0.9rem 1rem;
      margin-bottom: 0.9rem;
      backdrop-filter: blur(10px);
    }

    .panel-title {
      color: var(--muted);
      font-size: 0.68rem;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      font-weight: 700;
      margin-bottom: 0.7rem;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 82px;
      padding: 0.35rem 0.7rem;
      border-radius: 999px;
      font-size: 0.64rem;
      font-weight: 800;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      border: 1px solid transparent;
    }

    .pill-synthetic { color: #f9d497; background: rgba(78, 53, 16, 0.8); border-color: rgba(154, 117, 42, 0.8); }
    .pill-live { color: #aaf0c2; background: rgba(10, 62, 41, 0.8); border-color: rgba(58, 124, 87, 0.9); }
    .pill-replay { color: #b8d2ff; background: rgba(16, 42, 68, 0.9); border-color: rgba(76, 114, 174, 0.9); }

    .metric-card {
      background: rgba(18, 38, 53, 0.9);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.75rem 0.8rem;
      min-height: 88px;
      box-shadow: inset 0 0 0 1px rgba(151, 186, 213, 0.05);
    }

    .metric-label {
      color: var(--muted);
      font-size: 0.62rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-weight: 700;
      margin-bottom: 0.45rem;
    }

    .metric-value {
      font-size: 1.5rem;
      font-weight: 800;
      line-height: 1.1;
      letter-spacing: -0.04em;
    }

    .metric-sub {
      color: var(--muted);
      font-size: 0.7rem;
      margin-top: 0.25rem;
    }

    .map-shell {
      padding: 0.3rem 0.3rem 0.1rem 0.3rem;
    }

    .status-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.5rem 0.2rem;
      border-bottom: 1px solid rgba(117, 158, 197, 0.18);
      font-size: 0.77rem;
    }

    .status-row:last-child { border-bottom: none; }

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      display: inline-block;
      margin-right: 0.5rem;
      vertical-align: middle;
      box-shadow: 0 0 12px currentColor;
    }

    .dot-ok { background: var(--green); color: var(--green); }
    .dot-warn { background: var(--amber); color: var(--amber); }
    .dot-bad { background: var(--red); color: var(--red); }

    .kicker {
      color: var(--muted);
      font-size: 0.68rem;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      font-weight: 700;
    }

    .mini-btn {
      border-radius: 10px;
      border: 1px solid var(--line);
      background: rgba(18, 38, 53, 0.9);
      color: var(--text);
    }

    .stTabs [role="tablist"] {
      gap: 0.5rem;
    }

    .stTabs [role="tab"] {
      background: rgba(16, 36, 49, 0.8);
      border: 1px solid var(--line);
      border-radius: 10px 10px 0 0;
      padding: 0.55rem 0.8rem;
    }

    .stTabs [aria-selected="true"] {
      background: linear-gradient(180deg, rgba(29, 53, 71, 0.95), rgba(15, 28, 42, 0.95));
      border-color: rgba(99, 228, 246, 0.5);
    }

    .risk-tag {
      display: inline-block;
      padding: 0.38rem 0.7rem;
      border-radius: 999px;
      font-size: 0.64rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      border: 1px solid rgba(255,255,255,0.15);
    }

    .risk-low { background: rgba(70, 128, 86, 0.2); color: #baf0cb; }
    .risk-mod { background: rgba(107, 91, 32, 0.25); color: #f8d67a; }
    .risk-high { background: rgba(134, 72, 37, 0.28); color: #ffbf74; }
    .risk-sev { background: rgba(122, 39, 39, 0.35); color: #ff9ba0; }

    [data-testid="stMetricValue"] {
      font-family: 'JetBrains Mono', monospace;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _risk_tag(prob: float) -> str:
    if prob >= 0.8:
        return "SEVERE"
    if prob >= 0.6:
        return "HIGH"
    if prob >= 0.35:
        return "MODERATE"
    return "LOW"


def _backend_forecast(mode: str, case_id: str, district: str, state: str) -> Dict[str, Any] | None:
    payload = {
        "provenance": mode,
        "case_id": case_id,
        "district": district,
        "state": state,
        "radar_field": [
            [20, 30, 40, 42, 25],
            [18, 36, 52, 60, 26],
            [16, 34, 58, 65, 29],
            [12, 28, 44, 50, 22],
        ],
    }
    try:
        response = requests.post(f"{API_URL}/forecast", json=payload, timeout=8)
        if response.ok:
            data = response.json()
            data.setdefault("case_id", case_id)
            return data
        st.warning(f"API request failed with {response.status_code}: {response.text[:250]}")
    except requests.RequestException as exc:
        st.warning(f"API not available at {API_URL}. Running with demo shell only. ({exc})")
    return None


def _make_demo_payload(case_id: str, district: str, state: str, provenance: str = "SYNTHETIC") -> Dict[str, Any]:
    base = {
        "provenance": provenance,
        "case_id": case_id,
        "district": district,
        "state": state,
        "latency_ms": 42.8,
        "storm_cells": [
            {"cell_id": 1, "centroid_y": 1.4, "centroid_x": 2.6, "area": 14, "max_reflectivity": 62.0, "motion_x": 0.7, "motion_y": -0.4, "area_growth": 0.31, "provenance": provenance},
            {"cell_id": 2, "centroid_y": 3.0, "centroid_x": 1.7, "area": 10, "max_reflectivity": 58.0, "motion_x": 0.5, "motion_y": 0.2, "area_growth": 0.18, "provenance": provenance},
        ],
        "lad_state": {"pressure": 1.82, "accumulation": 0.71, "discharged": False, "gamma": 0.95, "rho": 0.8, "proxy": 0.72, "provenance": provenance},
        "alert_context": {"district": district, "state": state, "ndma_actions": "Take shelter if outdoors; avoid open fields and isolated tall objects; follow local emergency instructions."},
        "forecast": {},
        "sensor_health": [
            {"source": "Radar", "status": "OK", "provenance": provenance, "latency_minutes": 1.2},
            {"source": "Satellite", "status": "OK", "provenance": provenance, "latency_minutes": 3.0},
            {"source": "Lightning", "status": "WARN", "provenance": provenance, "latency_minutes": 11.0},
            {"source": "NWP", "status": "OK", "provenance": provenance, "latency_minutes": 5.0},
        ],
    }
    for h in HORIZONS:
        p = float({"5": 0.48, "15": 0.61, "30": 0.66, "60": 0.58, "180": 0.33}[h])
        q = float({"5": 0.37, "15": 0.52, "30": 0.71, "60": 0.63, "180": 0.41}[h])
        base["forecast"][h] = {
            "lightning_probability": p,
            "thunderstorm_probability": q,
            "field": {"probability": np.array([[0.08, 0.13, 0.18, 0.21, 0.12], [0.14, 0.22, 0.38, 0.52, 0.20], [0.12, 0.29, 0.67, 0.73, 0.31], [0.08, 0.18, 0.39, 0.44, 0.16]], dtype=float)},
        }
    return base


def _build_india_geo_plot(data: Dict[str, Any], horizon: str, globe_mode: bool = False) -> go.Figure:
    field = np.asarray(data["forecast"][horizon]["field"]["probability"], dtype=float)
    lat_vals = np.linspace(INDIA_BOUNDS["lat_min"], INDIA_BOUNDS["lat_max"], field.shape[0])
    lon_vals = np.linspace(INDIA_BOUNDS["lon_min"], INDIA_BOUNDS["lon_max"], field.shape[1])
    lon_grid, lat_grid = np.meshgrid(lon_vals, lat_vals)
    lat_flat = lat_grid.ravel()
    lon_flat = lon_grid.ravel()
    val_flat = field.ravel()

    fig = go.Figure()
    fig.add_trace(
        go.Scattergeo(
            lat=lat_flat,
            lon=lon_flat,
            mode="markers",
            marker={
                "size": 12,
                "color": val_flat,
                "colorscale": [[0.0, "#0b2235"], [0.26, "#144f70"], [0.62, "#ffc857"], [1.0, "#ff6b6b"]],
                "cmin": 0,
                "cmax": 1,
                "opacity": 0.82,
                "colorbar": {"title": "risk"},
            },
            hovertemplate="%{lat:.2f}°N<br>%{lon:.2f}°E<br>risk %{marker.color:.0%}<extra></extra>",
            name="hazard field",
        )
    )

    cells = data.get("storm_cells", [])
    if cells:
        cell_lats = []
        cell_lons = []
        cell_labels = []
        for c in cells:
            lat = INDIA_BOUNDS["lat_min"] + (c["centroid_y"] / 4.0) * (INDIA_BOUNDS["lat_max"] - INDIA_BOUNDS["lat_min"])
            lon = INDIA_BOUNDS["lon_min"] + (c["centroid_x"] / 5.0) * (INDIA_BOUNDS["lon_max"] - INDIA_BOUNDS["lon_min"])
            cell_lats.append(lat)
            cell_lons.append(lon)
            cell_labels.append(f"C{c['cell_id']}")
        fig.add_trace(
            go.Scattergeo(
                lat=cell_lats,
                lon=cell_lons,
                mode="markers+text",
                text=cell_labels,
                textposition="top center",
                marker={"size": 18, "color": "#fff3b0", "line": {"color": "#ff6b6b", "width": 2}},
                hovertemplate="%{text}<br>%{lat:.2f}°N<br>%{lon:.2f}°E<extra></extra>",
                name="storm cells",
            )
        )

    fig.update_geos(
        projection_type="orthographic" if globe_mode else "equirectangular",
        showland=True,
        landcolor="#102b3a",
        showocean=True,
        oceancolor="#071b2d",
        showcountries=True,
        countrycolor="#4a6a80",
        coastlinecolor="#7ca3ba",
        showframe=False,
        center={"lat": 22.5, "lon": 82.0},
        lataxis_showgrid=True,
        lataxis_gridcolor="#21435d",
        lonaxis_showgrid=True,
        lonaxis_gridcolor="#21435d",
    )
    fig.update_layout(
        height=620,
        margin={"l": 0, "r": 0, "t": 20, "b": 0},
        paper_bgcolor="#0b1b2b",
        plot_bgcolor="#0b1b2b",
        font={"color": "#edf7ff"},
        legend={"orientation": "h", "y": 1.08},
        title=f"India risk field · +{horizon} minutes",
    )
    return fig


def _health_table(data: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    for item in data.get("sensor_health", []):
        rows.append(
            {
                "source": item.get("source", "unknown"),
                "state": item.get("status", "UNKNOWN"),
                "provenance": item.get("provenance", "UNKNOWN"),
                "freshness_min": item.get("latency_minutes", "n/a"),
            }
        )
    return pd.DataFrame(rows)


# Sidebar controls
with st.sidebar:
    st.markdown('<div class="panel"><div class="panel-title">Mission controls</div>', unsafe_allow_html=True)
    mode = st.selectbox("Operating mode", ["SYNTHETIC", "REPLAY", "LIVE"], index=0)
    district = st.text_input("District", "Patna")
    state = st.text_input("State", "Bihar")
    case_id = st.text_input("Case / session id", "synthetic-demo")
    run_now = st.button("Launch nowcast", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="panel">
          <div class="panel-title">Source fabric</div>
          <div class="status-row"><span><span class="dot dot-ok"></span>Radar</span><strong>LIVE</strong></div>
          <div class="status-row"><span><span class="dot dot-warn"></span>Satellite</span><strong>DELAYED</strong></div>
          <div class="status-row"><span><span class="dot dot-ok"></span>NWP</span><strong>OPEN</strong></div>
          <div class="status-row"><span><span class="dot dot-bad"></span>Lightning</span><strong>FALLBACK</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Synthetic mode is clearly labelled; no real live source is implied.")

if "data" not in st.session_state:
    st.session_state.data = _make_demo_payload("synthetic-demo", district, state, "SYNTHETIC")

if run_now:
    if mode != "SYNTHETIC":
        st.warning(f"{mode} mode is gated in this demo. This shell refuses to fabricate real {mode.lower()} evidence.")
        st.session_state.data = _make_demo_payload(case_id, district, state, "SYNTHETIC")
    else:
        payload = _backend_forecast(mode, case_id, district, state)
        st.session_state.data = payload if payload is not None else _make_demo_payload(case_id, district, state, "SYNTHETIC")


data = st.session_state.data
if data is None:
    st.info("No forecast available yet. Launch the shell to start the demo run.")
    st.stop()

now = datetime.now(timezone.utc)
st.markdown(
    f'''
    <div class="topbar">
      <div class="brand">
        <div class="brand-badge">⛈️</div>
        <div>
          <div class="brand-title">INDRA / Earth Operations</div>
          <div class="brand-sub">India convective intelligence · nowcasting for thunderstorm + lightning</div>
        </div>
      </div>
      <div class="clock">{now.strftime('%d %b %Y · %H:%M:%S UTC')}<br>API latency logged · target &lt; 60s</div>
    </div>
    ''',
    unsafe_allow_html=True,
)

horizon = st.select_slider("Forecast lead time", options=HORIZONS, value="15")

st.markdown(
    f'''
    <div class="panel" style="padding:0.7rem 0.9rem;">
      <span class="pill pill-{data.get('provenance','synthetic').lower()}">{data.get('provenance','SYNTHETIC')}</span>
      <span style="margin-left:0.7rem; color:var(--muted); font-size:0.76rem;">case {data.get('case_id','demo')} · {data.get('district','Patna')}, {data.get('state','Bihar')} · inference {data.get('latency_ms', 0)} ms</span>
    </div>
    ''',
    unsafe_allow_html=True,
)

summary_cols = st.columns(5)
for idx, h in enumerate(HORIZONS):
    info = data["forecast"][h]
    with summary_cols[idx]:
        st.markdown(
            f'''
            <div class="metric-card">
              <div class="metric-label">+{h} min</div>
              <div class="metric-value">{info['lightning_probability']:.0%}</div>
              <div class="metric-sub">lightning · {info['thunderstorm_probability']:.0%} thunderstorm</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

left_col, right_col = st.columns([1.7, 1.0], gap="medium")

with left_col:
    st.markdown('<div class="panel"><div class="panel-title">Earth workspace</div>', unsafe_allow_html=True)
    globe_mode = st.toggle("Globe projection", value=False)
    st.plotly_chart(_build_india_geo_plot(data, horizon, globe_mode), use_container_width=True, config={"displaylogo": False})
    st.caption("Illustrative India-centered view for the current synthetic demo. It is not a real georeferenced radar map unless the backend returns georeferenced observations.")
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="panel"><div class="panel-title">Selected storm object</div>', unsafe_allow_html=True)
    cells = data.get("storm_cells", [])
    if cells:
        c = cells[0]
        st.markdown(f"<h3 style='margin:0 0 0.4rem;'>C{c['cell_id']:02d}</h3>", unsafe_allow_html=True)
        r = _risk_tag(data["forecast"][horizon]["thunderstorm_probability"])
        risk_class = r.lower().replace("sev", "sev").replace("mod", "mod").replace("low", "low").replace("high", "high")
        st.markdown(f'<div class="risk-tag risk-{risk_class}">{r}</div>', unsafe_allow_html=True)
        a, b = st.columns(2)
        a.metric("Max dBZ", f"{c['max_reflectivity']:.0f}")
        b.metric("Growth", f"{c['area_growth']:+.0%}")
        a, b = st.columns(2)
        a.metric("Motion X", f"{c['motion_x']:+.1f}")
        b.metric("Motion Y", f"{c['motion_y']:+.1f}")
        st.caption(f"Area {c['area']} px · provenance {c.get('provenance', 'UNKNOWN')}")
    else:
        st.warning("No thresholded storm cell in current synthetic field.")

    st.markdown("<div style='height:0.7rem;'></div>", unsafe_allow_html=True)
    lad = data.get("lad_state", {})
    st.markdown('<div class="kicker">LAD state</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    a.metric("Pₜ", f"{lad.get('pressure', 0):.2f}")
    b.metric("Proxy", f"{lad.get('proxy', 0):.0%}")
    st.caption("Inspectable pressure state, not a separately supervised target.")
    st.markdown("</div>", unsafe_allow_html=True)

risk_tab, evidence_tab, review_tab = st.tabs(["Risk / impact", "Evidence & health", "Forecaster desk"])

with risk_tab:
    prob = data["forecast"][horizon]["thunderstorm_probability"]
    tag = _risk_tag(prob)
    st.markdown(
        f'''
        <div class="panel">
          <div class="panel-title">Decision support</div>
          <div style="display:flex; align-items:center; gap:0.7rem; margin-bottom:0.55rem;">
            <span class="risk-tag risk-{tag.lower() if tag != 'SEVERE' else 'sev'}">{tag}</span>
            <span style="font-size:0.8rem; color:var(--muted);">{data.get('district', 'Patna')}, {data.get('state', 'Bihar')} · +{horizon} min</span>
          </div>
          <div style="font-size:1.8rem; font-weight:800; margin-bottom:0.35rem;">{prob:.0%} thunderstorm probability</div>
          <div style="color:var(--muted);">This is a prototype decision support signal. No public warning is being issued here.</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    st.info(data.get("alert_context", {}).get("ndma_actions", "Follow local emergency instructions and official guidance."))

with evidence_tab:
    health_df = _health_table(data)
    st.markdown('<div class="panel"><div class="panel-title">Source health</div>', unsafe_allow_html=True)
    st.dataframe(health_df, hide_index=True, use_container_width=True)
    st.caption("Source availability is not sensor agreement. Synthetic mode does not imply actual real-world measurement freshness.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="panel-title">Forecast evidence</div>', unsafe_allow_html=True)
    st.json(
        {
            "lead_min": int(horizon),
            "lightning_probability": data["forecast"][horizon]["lightning_probability"],
            "thunderstorm_probability": data["forecast"][horizon]["thunderstorm_probability"],
            "source_provenance": data.get("provenance", "SYNTHETIC"),
            "uncertainty": "Calibration not claimed in this demo shell",
        }
    )
    st.markdown("</div>", unsafe_allow_html=True)

with review_tab:
    st.markdown('<div class="panel"><div class="panel-title">Forecaster desk</div>', unsafe_allow_html=True)
    action = st.selectbox("Operator action", ["Approve", "Edit / hold", "Dismiss"], index=0)
    note = st.text_area("Review note", value="Storm-cell signal shows a coherent convective object; continue monitoring for lightning escalation.")
    st.write(f"Suggested status: {action} · {data.get('district','Patna')} / {data.get('state','Bihar')}")
    if st.button("Record review", use_container_width=True):
        st.success("Review recorded locally; no public warning was issued by this prototype.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="panel"><div class="panel-title">Multi-horizon timeline</div>', unsafe_allow_html=True)
curve_df = pd.DataFrame(
    {
        "lead_min": [int(h) for h in HORIZONS],
        "lightning": [data["forecast"][h]["lightning_probability"] for h in HORIZONS],
        "thunderstorm": [data["forecast"][h]["thunderstorm_probability"] for h in HORIZONS],
    }
)
fig = go.Figure()
fig.add_trace(go.Scatter(x=curve_df["lead_min"], y=curve_df["lightning"], mode="lines+markers", name="Lightning", line={"color": "#63e4f6", "width": 3}, marker={"size": 8}))
fig.add_trace(go.Scatter(x=curve_df["lead_min"], y=curve_df["thunderstorm"], mode="lines+markers", name="Thunderstorm", line={"color": "#ffc857", "width": 3}, marker={"size": 8}))
fig.update_layout(
    height=260,
    margin={"l": 0, "r": 0, "t": 10, "b": 26},
    paper_bgcolor="#0b1b2b",
    plot_bgcolor="#0b1b2b",
    font={"color": "#edf7ff"},
    xaxis_title="Minutes from observation",
    yaxis={"range": [0, 1], "tickformat": ".0%"},
    legend={"orientation": "h", "y": 1.08},
)
st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
st.markdown("</div>", unsafe_allow_html=True)

st.caption("INDRA Earth Operations prototype · synthetic demo shell only · no real warning issuance or uncalibrated live claims are implied.")




# The UI is intentionally designed for the existing API contract and explicit provenance labeling.
# It never claims that synthetic demo raster data is a real geographic product.
