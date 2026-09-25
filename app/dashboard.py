"""Operational dashboard for the spatial, temporal and provenance-aware API."""
import streamlit as st, requests, pandas as pd, numpy as np
st.set_page_config(page_title="INDRA Nowcast",layout="wide")
st.title("INDRA | Reliability-aware India Nowcast")
st.caption("0–3 hour thunderstorm + lightning decision support · every view is provenance-labelled")
with st.sidebar:
    tier=st.selectbox("Data tier",["SYNTHETIC","REPLAY:demo-case","LIVE"]); case=st.text_input("Case ID","demo-case"); district=st.text_input("District","Patna"); state=st.text_input("State","Bihar"); run=st.button("Run nowcast",type="primary")
if run:
    if tier!="SYNTHETIC": st.error("This UI requires a real replay/live payload adapter. It will not relabel synthetic data as replay/live."); st.stop()
    payload={"provenance":"SYNTHETIC","case_id":case,"district":district,"state":state,"radar_field":[[20,36,40,44,20],[20,38,52,58,23],[18,37,55,62,26],[12,20,38,43,20]]}
    try: d=requests.post("http://127.0.0.1:8000/forecast",json=payload,timeout=5).json()
    except Exception as e: st.error(f"Start API first: {e}"); st.stop()
    st.warning(f"PROVENANCE: {d['provenance']} · case {d['case_id']} · {d['latency_ms']} ms")
    tabs=st.tabs(["Hazard map","Cell/LAD","Sensor health"])
    with tabs[0]:
        cols=st.columns(5)
        for col,(h,v) in zip(cols,d["forecast"].items()): col.metric(f"{h} min lightning",f"{v['lightning_probability']:.0%}"); col.caption(f"Thunderstorm {v['thunderstorm_probability']:.0%}")
        h=st.select_slider("Map horizon",options=list(d["forecast"].keys()),value="15"); field=np.asarray(d["forecast"][h]["field"]["probability"]); st.subheader(f"Spatial lightning probability field · +{h} min"); st.image(field,clamp=True,use_container_width=True)
    with tabs[1]: st.dataframe(pd.DataFrame(d["storm_cells"])); st.json(d["lad_state"])
    with tabs[2]: st.dataframe(pd.DataFrame(d["sensor_health"])); st.info(d["alert_context"]["ndma_actions"])
else: st.info("Run the explicitly labelled synthetic demo, or connect a real replay/live adapter. The UI refuses to disguise synthetic observations as real.")
