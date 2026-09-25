"""INDRA Earth Operations Console.

Original, map-first Streamlit interface for the existing /forecast API. The Earth
view is explicitly marked illustrative in SYNTHETIC mode because the current API
returns grid coordinates rather than georeferenced observations.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

API = "http://127.0.0.1:8000"
HORIZONS = ["5", "15", "30", "60", "180"]
DEMO_DOMAIN = {"lat_min": 18.0, "lat_max": 28.0, "lon_min": 72.0, "lon_max": 88.0}

st.set_page_config(page_title="INDRA Earth Operations", page_icon="🌩️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --bg:#06111c; --surface:#0b1b2a; --surface2:#102639; --line:#1e3a50; --text:#e8f1f7; --muted:#8ca8bb; --cyan:#52e0ed; --gold:#ffc857; --danger:#ff6b6b; --green:#59e391; }
html,body,[data-testid="stAppViewContainer"] { background:var(--bg); color:var(--text); font-family:'Manrope',sans-serif; }
[data-testid="stHeader"] { background:rgba(6,17,28,.92); }
[data-testid="stSidebar"] { background:#071624; border-right:1px solid var(--line); }
.block-container { max-width:1900px; padding:1rem 1.35rem 2rem; }
.topbar { display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid var(--line); padding:0 0 13px; margin-bottom:14px; }
.identity { display:flex; align-items:center; gap:12px; }
.logo { width:42px;height:42px;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle at 35% 30%,#65f0ef,#1673b8 58%,#071a37);box-shadow:0 0 25px #2bbbd055;font-size:21px;border:1px solid #73eff055; }
.title { font-weight:800; letter-spacing:.13em; font-size:1.2rem; }
.subtitle { color:var(--muted); font-size:.69rem; letter-spacing:.1em; text-transform:uppercase; margin-top:2px; }
.clock { text-align:right; font-family:'DM Mono',monospace; color:var(--muted); font-size:.72rem; }
.pill { padding:4px 9px; border-radius:100px; font-size:.66rem; font-weight:800; letter-spacing:.08em; display:inline-block; }
.synthetic { color:#ffd789;background:#4b3517;border:1px solid #806028; }.live { color:#93f3ba;background:#123a2a;border:1px solid #26794f; }.replay { color:#a9ceff;background:#17355b;border:1px solid #2c62a0; }
.panel { background:linear-gradient(145deg,#0c1c2b,#091725); border:1px solid var(--line); border-radius:14px; padding:14px; margin-bottom:12px; box-shadow:0 8px 30px #00000018; }
.panel-title { color:var(--muted); font-size:.66rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; margin-bottom:10px; }
.big-number { font-size:1.65rem; font-weight:800; line-height:1.1; }.small { color:var(--muted);font-size:.73rem; }.mono { font-family:'DM Mono',monospace; }
.status-row { display:flex; align-items:center; justify-content:space-between; padding:8px 0; border-bottom:1px solid #183145; font-size:.78rem; }.status-row:last-child { border-bottom:0; }.dot { width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:7px; }.ok { background:var(--green);box-shadow:0 0 9px var(--green); }.warn { background:var(--gold); }.off { background:var(--danger); }
[data-testid="stMetric"] { background:var(--surface2); border:1px solid var(--line); border-radius:11px; padding:8px; }.stButton button { border-radius:9px; border:1px solid #2b5873; }.stTabs [data-baseweb="tab"] { font-weight:700; }
</style>
""", unsafe_allow_html=True)

def api_forecast(mode: str, case_id: str, district: str, state: str):
    payload = {"provenance": "SYNTHETIC", "case_id": case_id, "district": district, "state": state,
               "radar_field": [[20,36,40,44,20],[20,38,52,58,23],[18,37,55,62,26],[12,20,38,43,20]]}
    try:
        r = requests.post(f"{API}/forecast", json=payload, timeout=8)
        if r.ok: return r.json()
        st.error(f"API {r.status_code}: {r.text[:250]}")
    except requests.RequestException as exc:
        st.error(f"FastAPI is unavailable at {API}: {exc}")
    return None

def geo_from_grid(y, x):
    # Only for the clearly labelled synthetic illustrative view.
    return (DEMO_DOMAIN["lat_max"] - y / 4.0 * (DEMO_DOMAIN["lat_max"]-DEMO_DOMAIN["lat_min"]),
            DEMO_DOMAIN["lon_min"] + x / 5.0 * (DEMO_DOMAIN["lon_max"]-DEMO_DOMAIN["lon_min"]))

def earth_map(data: Dict[str, Any], horizon: str, globe: bool = False):
    f = data["forecast"][horizon]; z = np.asarray(f["field"]["probability"], dtype=float)
    fig = go.Figure()
    # Heat cells are rendered as small geospatial polygons in the synthetic demo.
    ny,nx=z.shape; lat=[]; lon=[]; val=[]
    for y in range(ny):
        for x in range(nx):
            la,lo=geo_from_grid(y,x); lat.append(la); lon.append(lo); val.append(float(z[y,x]))
    fig.add_trace(go.Scattergeo(lat=lat,lon=lon,mode="markers",marker={"size":18,"color":val,"colorscale":[[0,"#102b43"],[.35,"#19718a"],[.7,"#ffc857"],[1,"#ff5d67"],],"cmin":0,"cmax":1,"opacity":.82,"colorbar":{"title":"Risk","thickness":10}},name="probability field",hovertemplate="%{lat:.2f}°N, %{lon:.2f}°E<br>risk %{marker.color:.0%}<extra></extra>"))
    cells=data.get("storm_cells",[])
    if cells:
        clat=[]; clon=[]; labels=[]
        for c in cells:
            la,lo=geo_from_grid(c["centroid_y"],c["centroid_x"]); clat.append(la);clon.append(lo);labels.append(f"C{c['cell_id']}")
        fig.add_trace(go.Scattergeo(lat=clat,lon=clon,mode="markers+text",text=labels,textposition="top center",marker={"size":17,"color":"#fff1a8","line":{"color":"#ff6b6b","width":2}},name="storm cells",hovertemplate="%{text}<br>%{lat:.2f}°N, %{lon:.2f}°E<extra></extra>"))
    projection="orthographic" if globe else "equirectangular"
    fig.update_geos(projection_type=projection,center={"lat":23,"lon":80},projection_scale=.95 if globe else 1.8,
                    showland=True,landcolor="#0d263b",showocean=True,oceancolor="#061b2d",showlakes=True,lakecolor="#08263d",
                    showcountries=True,countrycolor="#416177",showcoastlines=True,coastlinecolor="#6d91a3",showframe=False,
                    lataxis_showgrid=True,lataxis_gridcolor="#17394e",lonaxis_showgrid=True,lonaxis_gridcolor="#17394e")
    fig.update_layout(height=620,margin={"l":0,"r":0,"t":22,"b":0},paper_bgcolor="#0b1b2a",font={"color":"#e8f1f7"},legend={"orientation":"h","y":1.02},title=f"India operations view · +{horizon} min")
    return fig

def health(data):
    rows=[]
    for x in data.get("sensor_health",[]):
        s=x.get("status","MISSING"); rows.append({"source":x.get("source","—"),"state":s,"provenance":x.get("provenance","—"),"freshness":"not measured"})
    return pd.DataFrame(rows)

def level(prob): return "SEVERE" if prob>=.8 else "HIGH" if prob>=.6 else "MODERATE" if prob>=.35 else "LOW"

# Header
now=datetime.now(timezone.utc)
st.markdown(f'<div class="topbar"><div class="identity"><div class="logo">⛈</div><div><div class="title">INDRA EARTH OPERATIONS</div><div class="subtitle">India convective intelligence · 0–3 hour decision support</div></div></div><div class="clock">{now.strftime("%d %b %Y · %H:%M:%S UTC")}<br><span class="small">SYSTEM READY · API LATENCY LOGGED</span></div></div>',unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="panel"><div class="panel-title">Mission context</div>',unsafe_allow_html=True)
    mode=st.selectbox("Operating mode",["SYNTHETIC","REPLAY","LIVE"])
    district=st.text_input("District","Patna"); state=st.text_input("State","Bihar"); case=st.text_input("Session / case","synthetic-demo")
    run=st.button("LAUNCH NOWCAST",type="primary",use_container_width=True)
    st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-title">Data fabric</div><div class="status-row"><span><span class="dot warn"></span>Radar</span><b>SYNTHETIC</b></div><div class="status-row"><span><span class="dot off"></span>Satellite</span><b>MISSING</b></div><div class="status-row"><span><span class="dot off"></span>Lightning</span><b>MISSING</b></div><div class="status-row"><span><span class="dot off"></span>NWP</span><b>MISSING</b></div></div>',unsafe_allow_html=True)
    st.caption("The connected demo is synthetic. Replay/live controls remain gated until actual authorized payloads are connected.")

if "data" not in st.session_state: st.session_state.data=None
if "review" not in st.session_state: st.session_state.review="DRAFT"
if run:
    if mode != "SYNTHETIC": st.warning(f"{mode} is gated: the UI will not fabricate a {mode.lower()} observation stream.")
    else:
        with st.spinner("Updating Earth view · detecting cells · advancing LAD state..."): st.session_state.data=api_forecast(mode,case,district,state)
if st.session_state.data is None:
    st.info("Launch the explicitly labelled synthetic demonstrator. Start the API first: `uvicorn app.service:app --reload`")
    st.stop()
data=st.session_state.data

# Status ribbon and metrics
st.markdown(f'<div class="panel"><span class="pill synthetic">{data.get("provenance","UNKNOWN")}</span> <span class="small">CASE {data.get("case_id","—")} · synthetic illustrative geography · {data.get("latency_ms","—")} ms inference · no official warning issued</span></div>',unsafe_allow_html=True)
horizon=st.select_slider("Forecast horizon",options=HORIZONS,value="15")
current=data["forecast"][horizon]
cols=st.columns(5)
for col,h in zip(cols,HORIZONS):
    q=data["forecast"][h]; col.metric(f"+{h} MIN",f"{q['lightning_probability']:.0%}",f"TS {q['thunderstorm_probability']:.0%}")

# Main map workspace
mapcol, sidecol=st.columns([1.72,1],gap="medium")
with mapcol:
    st.markdown('<div class="panel"><div class="panel-title">Earth workspace · storm probability field</div>',unsafe_allow_html=True)
    globe=st.toggle("Globe projection",value=False)
    st.plotly_chart(earth_map(data,horizon,globe),use_container_width=True,config={"displaylogo":False,"scrollZoom":True})
    st.caption("Synthetic mode: positions are illustrative grid-to-India coordinates. They are not real radar geolocation.")
    st.markdown('</div>',unsafe_allow_html=True)
with sidecol:
    st.markdown('<div class="panel"><div class="panel-title">Selected storm object</div>',unsafe_allow_html=True)
    cells=data.get("storm_cells",[])
    if cells:
        c=cells[0]; la,lo=geo_from_grid(c["centroid_y"],c["centroid_x"])
        st.markdown(f"## C{c['cell_id']:02d} <span class='pill synthetic'>DEMO CELL</span>",unsafe_allow_html=True)
        a,b=st.columns(2); a.metric("Position",f"{la:.1f}°N"); b.metric("Position",f"{lo:.1f}°E")
        a,b=st.columns(2); a.metric("Core",f"{c['max_reflectivity']:.0f} dBZ"); b.metric("Growth",f"{c['area_growth']:+.0%}")
        st.write(f"Motion vector: `{c['motion_x']:+.1f}, {c['motion_y']:+.1f}` grid units/frame")
    else: st.warning("No tracked cell in current synthetic field")
    st.divider(); st.markdown("**Hazard at selected horizon**")
    st.metric("Lightning",f"{current['lightning_probability']:.0%}"); st.metric("Thunderstorm",f"{current['thunderstorm_probability']:.0%}")
    lad=data.get("lad_state",{}); st.caption(f"LAD Pₜ {lad.get('pressure',0):.2f} · proxy {lad.get('proxy',0):.0%}")
    st.markdown('</div>',unsafe_allow_html=True)

# Operational lower workspace
one,two,three,four=st.tabs(["EVIDENCE & HEALTH","RISK / EXPOSURE","FORECAST TIMELINE","FORECASTER DESK"])
with one:
    a,b=st.columns(2)
    with a:
        st.markdown('<div class="panel"><div class="panel-title">Source health</div>',unsafe_allow_html=True); st.dataframe(health(data),hide_index=True,use_container_width=True); st.caption("Availability is not agreement. Synthetic mode has no measured live freshness."); st.markdown('</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel"><div class="panel-title">Evidence chain</div>',unsafe_allow_html=True)
        st.write("**Observed:** thresholded synthetic reflectivity field")
        st.write("**State:** inspectable LAD pressure")
        st.write("**Forecast:** separate lightning and thunderstorm heads")
        st.write("**Uncertainty:** demo field bounds; statistical calibration not claimed")
        st.markdown('</div>',unsafe_allow_html=True)
with two:
    p=float(current["thunderstorm_probability"]); st.markdown(f'<div class="panel"><div class="panel-title">Decision support · not an issued warning</div><div class="big-number">{level(p)} · {district}</div><p class="small">+{horizon} minute thunderstorm probability {p:.0%}. District polygon and critical-infrastructure records are not connected in the current backend, so no fabricated exposure/ETA is shown.</p>',unsafe_allow_html=True); st.info(data.get("alert_context",{}).get("ndma_actions","Follow official local guidance.")); st.markdown('</div>',unsafe_allow_html=True)
with three:
    st.markdown('<div class="panel"><div class="panel-title">Lead-time curve</div>',unsafe_allow_html=True)
    frame=pd.DataFrame({"lead": [int(h) for h in HORIZONS],"lightning":[data["forecast"][h]["lightning_probability"] for h in HORIZONS],"thunderstorm":[data["forecast"][h]["thunderstorm_probability"] for h in HORIZONS]})
    fig=go.Figure(); fig.add_trace(go.Scatter(x=frame.lead,y=frame.lightning,mode="lines+markers",name="Lightning",line={"color":"#52e0ed","width":3})); fig.add_trace(go.Scatter(x=frame.lead,y=frame.thunderstorm,mode="lines+markers",name="Thunderstorm",line={"color":"#ffc857","width":3})); fig.update_layout(height=280,margin={"l":0,"r":0,"t":10,"b":20},paper_bgcolor="#0b1b2a",plot_bgcolor="#0b1b2a",font={"color":"#e8f1f7"},yaxis={"range":[0,1],"tickformat":".0%"},xaxis_title="minutes from observation"); st.plotly_chart(fig,use_container_width=True); st.markdown('</div>',unsafe_allow_html=True)
with four:
    st.markdown('<div class="panel"><div class="panel-title">Human-in-the-loop warning review</div>',unsafe_allow_html=True)
    st.warning(f"Status: {st.session_state.review} · no public alert has been issued")
    st.write(f"Suggested action: review {level(p)} risk for {district} at +{horizon} min.")
    note=st.text_area("Forecaster note",key="note")
    a,b,c=st.columns(3)
    if a.button("Approve",key="approve"): st.session_state.review="PENDING REVIEW"; st.success("Recorded locally for review.")
    if b.button("Edit / hold",key="hold"): st.session_state.review="EDIT REQUIRED"
    if c.button("Dismiss",key="dismiss"): st.session_state.review="DISMISSED"
    st.markdown('</div>',unsafe_allow_html=True)

st.caption("INDRA · original operator-console UI · synthetic demonstration only · connect authorized georeferenced replay/live data before operational claims.")
