"""INDRA operational console.

This is an original Streamlit decision-support UI. It uses the existing /forecast
contract and makes the data tier explicit. Synthetic mode is the only runnable mode
until an authorized replay/live adapter is connected; the UI never relabels it.
"""
from __future__ import annotations
import time
from datetime import datetime, timezone
from typing import Any, Dict, List
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"
HORIZONS = ["5", "15", "30", "60", "180"]

st.set_page_config(page_title="INDRA Operations Console", page_icon="⛈️", layout="wide", initial_sidebar_state="expanded")

# ---------- visual system ----------
st.markdown("""
<style>
:root { --ink:#dce8f5; --muted:#8fa5bc; --panel:#111d2c; --panel2:#17283b; --line:#263c52; --cyan:#50d5e8; --amber:#f6bd60; --red:#ff6b6b; }
html, body, [data-testid="stAppViewContainer"] { background:#08121f; color:var(--ink); }
[data-testid="stHeader"] { background:rgba(8,18,31,.94); }
[data-testid="stSidebar"] { background:#0b1726; border-right:1px solid var(--line); }
.block-container { max-width:1700px; padding:1.2rem 1.6rem 2rem; }
.brand { display:flex; align-items:center; gap:14px; padding:4px 0 14px; }
.brand-mark { width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#45d7e9,#1e6ee8);display:grid;place-items:center;font-size:23px;box-shadow:0 0 26px #1d8cb455; }
.brand h1 { margin:0; font-size:1.55rem; letter-spacing:.08em; font-weight:750; }
.brand p { margin:3px 0 0;color:var(--muted);font-size:.78rem; }
.panel { background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:15px; margin-bottom:12px; }
.kicker { color:var(--muted); text-transform:uppercase; letter-spacing:.11em; font-size:.68rem; font-weight:700; }
.metric { background:var(--panel2); border:1px solid var(--line); border-radius:12px; padding:12px 14px; min-height:86px; }
.metric .label { color:var(--muted); font-size:.72rem; text-transform:uppercase; letter-spacing:.06em; }
.metric .value { font-size:1.55rem; font-weight:750; margin-top:6px; }
.metric .sub { color:var(--muted); font-size:.72rem; margin-top:3px; }
.pill { display:inline-block; padding:4px 9px; border-radius:999px; font-size:.7rem; font-weight:700; letter-spacing:.04em; }
.pill-syn { color:#ffd18a;background:#4b3217;border:1px solid #8a5e25; }
.pill-live { color:#8df2bd;background:#123a2b;border:1px solid #267c56; }
.pill-missing { color:#ffaeae;background:#4a2028;border:1px solid #903d4c; }
.small { color:var(--muted);font-size:.78rem; }
hr { border-color:var(--line); }
[data-testid="stMetric"] { background:var(--panel2); border:1px solid var(--line); border-radius:12px; padding:8px; }
</style>
""", unsafe_allow_html=True)

# ---------- helpers ----------
def metric_card(label: str, value: str, sub: str = "") -> None:
    st.markdown(f'<div class="metric"><div class="label">{label}</div><div class="value">{value}</div><div class="sub">{sub}</div></div>', unsafe_allow_html=True)

def call_forecast(provenance: str, case_id: str, district: str, state: str) -> Dict[str, Any] | None:
    # The current API supports a deliberately labelled synthetic scenario.
    payload = {
        "provenance": provenance, "case_id": case_id, "district": district, "state": state,
        "radar_field": [[20,36,40,44,20],[20,38,52,58,23],[18,37,55,62,26],[12,20,38,43,20]],
    }
    try:
        response = requests.post(f"{API_URL}/forecast", json=payload, timeout=8)
        if response.ok: return response.json()
        st.error(f"API returned {response.status_code}: {response.text[:300]}")
    except requests.RequestException as exc:
        st.error(f"Cannot reach API at {API_URL}. Start FastAPI first. ({exc})")
    return None

def map_figure(data: Dict[str, Any], horizon: str) -> go.Figure:
    # The API's synthetic/raster fallback is an image grid, so geo coordinates are
    # only shown for real georeferenced cells when the backend provides them.
    field = np.asarray(data["forecast"][horizon]["field"]["probability"], dtype=float)
    cells = data.get("storm_cells", [])
    fig = go.Figure()
    if cells:
        # Synthetic grid indices are explicitly labelled as grid coordinates.
        xs=[c["centroid_x"] for c in cells]; ys=[c["centroid_y"] for c in cells]
        fig.add_trace(go.Scatter(x=xs,y=ys,mode="markers+text",text=[f'C{c["cell_id"]}' for c in cells],textposition="top center",marker={"size":18,"color":"#ffcf70","line":{"color":"#fff","width":1}},name="storm cells"))
    fig.add_trace(go.Heatmap(z=field, colorscale=[[0,"#10243a"],[.35,"#155f83"],[.7,"#f6bd60"],[1,"#ff5d66"]], opacity=.76, colorbar={"title":"risk"}, name="hazard field"))
    fig.update_layout(height=590, margin={"l":10,"r":10,"t":35,"b":10}, paper_bgcolor="#111d2c", plot_bgcolor="#0a1727", font={"color":"#dce8f5"}, title=f"Hazard field · +{horizon} min · grid coordinates (not a geographic map)", xaxis_title="grid x", yaxis_title="grid y", legend={"orientation":"h","y":1.02})
    return fig

def health_table(data: Dict[str, Any]) -> pd.DataFrame:
    rows=[]
    for item in data.get("sensor_health", []):
        status=item.get("status","MISSING")
        rows.append({"Source":item.get("source","unknown"),"State":status,"Provenance":item.get("provenance","unknown"),"Freshness":f'{item.get("latency_minutes", 0) or 0:.1f} min' if item.get("latency_minutes") is not None else "not measured"})
    return pd.DataFrame(rows)

# ---------- header/sidebar ----------
st.markdown('<div class="brand"><div class="brand-mark">⚡</div><div><h1>INDRA / OPERATIONS CONSOLE</h1><p>Reliability-aware thunderstorm & lightning decision support · SIH PS 26072</p></div></div>', unsafe_allow_html=True)
with st.sidebar:
    st.markdown('<div class="kicker">Mission controls</div>', unsafe_allow_html=True)
    mode=st.selectbox("Data mode",["SYNTHETIC","REPLAY","LIVE"],help="The current backend only executes SYNTHETIC mode from this UI.")
    case_id=st.text_input("Case / session ID","synthetic-demo")
    district=st.text_input("Target district","Patna"); state=st.text_input("State","Bihar")
    run=st.button("▶  Run nowcast",use_container_width=True,type="primary")
    st.divider()
    st.markdown('<div class="kicker">System contract</div>',unsafe_allow_html=True)
    st.caption("Synthetic values are never displayed as live or replay observations. Real replay mode becomes available after an authorized case is connected to the API.")
    st.link_button("Open API documentation",f"{API_URL}/docs",use_container_width=True)

if "forecast_data" not in st.session_state: st.session_state.forecast_data=None
if "alert_state" not in st.session_state: st.session_state.alert_state="DRAFT"
if run:
    if mode != "SYNTHETIC":
        st.warning(f"{mode} mode is intentionally gated: no real {mode.lower()} payload is connected to this UI, so the console refuses to fabricate one.")
    else:
        with st.spinner("Running cell detection, LAD update and forecast..."): st.session_state.forecast_data=call_forecast("SYNTHETIC",case_id,district,state)

data=st.session_state.forecast_data
if data is None:
    st.info("Choose SYNTHETIC and press Run nowcast to launch the demonstrator. The API must be running first.")
    st.stop()

# ---------- status ribbon ----------
mode_label=data.get("provenance","UNKNOWN")
now=datetime.now(timezone.utc).strftime("%d %b %Y · %H:%M:%S UTC")
st.markdown(f'<div class="panel"><span class="pill pill-syn">{mode_label}</span> <span class="small">CASE {data.get("case_id","-")} · updated {now} · inference {data.get("latency_ms","-")} ms · target &lt;60 s</span></div>',unsafe_allow_html=True)

# ---------- top metrics ----------
selected=st.select_slider("Forecast horizon",options=HORIZONS,value="15",key="horizon")
current=data["forecast"][selected]
cols=st.columns(5)
for col,h in zip(cols,HORIZONS):
    f=data["forecast"][h]; col.metric(f"+{h} min",f"{f['lightning_probability']:.0%}",f"TS {f['thunderstorm_probability']:.0%}")

# ---------- map workspace + storm panel ----------
left,right=st.columns([1.65,1],gap="medium")
with left:
    st.markdown('<div class="panel"><div class="kicker">Primary workspace</div>',unsafe_allow_html=True)
    st.plotly_chart(map_figure(data,selected),use_container_width=True,config={"displaylogo":False,"scrollZoom":True})
    st.caption("The current backend returns a raster fallback without latitude/longitude metadata. This view labels it as grid coordinates rather than pretending it is a geographic map.")
    st.markdown('</div>',unsafe_allow_html=True)
with right:
    st.markdown('<div class="panel"><div class="kicker">Selected cell</div>',unsafe_allow_html=True)
    cells=data.get("storm_cells",[])
    if cells:
        cell=cells[0]
        st.subheader(f"CELL C{cell['cell_id']:02d}")
        a,b=st.columns(2); a.metric("Reflectivity",f"{cell['max_reflectivity']:.0f} dBZ"); b.metric("Area",f"{cell['area']} px")
        a,b=st.columns(2); a.metric("Motion",f"Δ {cell['motion_x']:.1f}, {cell['motion_y']:.1f}"); b.metric("Growth",f"{cell['area_growth']:+.0%}")
        st.markdown(f"**Track note:** prototype cell association · provenance `{cell.get('provenance',mode_label)}`")
    else: st.warning("No thresholded storm cell in the current field.")
    st.markdown("#### LAD convective state")
    lad=data.get("lad_state",{}); a,b=st.columns(2); a.metric("Pressure Pₜ",f"{lad.get('pressure',0):.2f}"); b.metric("Proxy",f"{lad.get('proxy',0):.0%}")
    st.caption("Inspectable state; not a direct observation or independently supervised label.")
    st.markdown('</div>',unsafe_allow_html=True)

# ---------- evidence, impact, workflow ----------
t1,t2,t3=st.tabs(["Evidence & health","Risk / impact","Forecaster review"])
with t1:
    a,b=st.columns([1,1]);
    with a:
        st.markdown('<div class="panel"><div class="kicker">Source health</div>',unsafe_allow_html=True)
        st.dataframe(health_table(data),hide_index=True,use_container_width=True)
        st.caption("Availability is not sensor agreement. Current API health reflects payload presence; source latency is not measured in synthetic mode.")
        st.markdown('</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel"><div class="kicker">Forecast evidence</div>',unsafe_allow_html=True)
        st.write("Current model outputs")
        st.json({"horizon":selected,"lightning_probability":current["lightning_probability"],"thunderstorm_probability":current["thunderstorm_probability"],"sensor_agreement":current.get("sensor_agreement","not supplied"),"uncertainty":"Backend field bounds are demo spatial bounds; calibration not claimed."})
        st.markdown('</div>',unsafe_allow_html=True)
with t2:
    st.markdown('<div class="panel"><div class="kicker">Decision support · not an issued warning</div>',unsafe_allow_html=True)
    p=float(current["thunderstorm_probability"]); level="SEVERE" if p>=.8 else "HIGH" if p>=.6 else "MODERATE" if p>=.35 else "LOW"
    a,b,c=st.columns(3); a.metric("Risk level",level); b.metric("Affected area",district); c.metric("Lead",f"+{selected} min")
    st.info(data.get("alert_context",{}).get("ndma_actions","Follow local official guidance."))
    st.caption("The current backend does not yet provide geospatial district intersection or infrastructure records, so no fabricated ETA/exposure is shown.")
    st.markdown('</div>',unsafe_allow_html=True)
with t3:
    st.markdown('<div class="panel"><div class="kicker">Human review workflow</div>',unsafe_allow_html=True)
    st.warning(f"Suggested status: {st.session_state.alert_state} · this is not an officially issued alert.")
    st.write(f"**Suggested warning:** {level} thunderstorm risk for {district}, based on the +{selected} min prototype output.")
    st.write("**Evidence:** thresholded cell, LAD pressure state, and model hazard probabilities. Source provenance is shown above.")
    note=st.text_area("Reviewer note",placeholder="Record why this suggestion is approved, edited or dismissed.")
    a,b,c=st.columns(3)
    if a.button("Approve suggestion"): st.session_state.alert_state="PENDING_APPROVAL"; st.success("Recorded locally as pending review; no public alert was issued.")
    if b.button("Edit / hold"): st.session_state.alert_state="EDIT_REQUIRED"; st.info("Marked for operator editing.")
    if c.button("Dismiss"): st.session_state.alert_state="DISMISSED"; st.info("Suggestion dismissed locally.")
    st.markdown('</div>',unsafe_allow_html=True)

# ---------- lower timeline and honesty panel ----------
st.markdown('<div class="panel"><div class="kicker">Operational timeline</div>',unsafe_allow_html=True)
rows=[]
for h in HORIZONS:
    f=data["forecast"][h]; rows.append({"lead_min":int(h),"lightning":f["lightning_probability"],"thunderstorm":f["thunderstorm_probability"]})
timeline=pd.DataFrame(rows)
fig=go.Figure(); fig.add_trace(go.Scatter(x=timeline.lead_min,y=timeline.lightning,mode="lines+markers",name="Lightning",line={"color":"#50d5e8","width":3})); fig.add_trace(go.Scatter(x=timeline.lead_min,y=timeline.thunderstorm,mode="lines+markers",name="Thunderstorm",line={"color":"#f6bd60","width":3})); fig.update_yaxes(range=[0,1],tickformat=".0%",gridcolor="#263c52"); fig.update_xaxes(title="minutes from observation",gridcolor="#263c52"); fig.update_layout(height=250,margin={"l":10,"r":10,"t":10,"b":30},paper_bgcolor="#111d2c",plot_bgcolor="#111d2c",font={"color":"#dce8f5"}); st.plotly_chart(fig,use_container_width=True,config={"displaylogo":False})
st.markdown('</div>',unsafe_allow_html=True)

st.caption("INDRA prototype · Synthetic demo only in this connected UI · no calibrated uncertainty, real-data skill, geographic district intersection, infrastructure exposure, or official warning is claimed until the corresponding backend/data adapters are connected.")
