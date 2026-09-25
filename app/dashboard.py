"""Judge-facing operational console. Every displayed dataset carries provenance."""
import streamlit as st, requests, pandas as pd
st.set_page_config(page_title="INDRA Nowcast",layout="wide")
st.title("INDRA | India Thunderstorm & Lightning Nowcast")
st.caption("SIH 2026 PS 26072 · 0–3 hour decision support · prototype, not an operational warning")
with st.sidebar:
    st.header("Scenario")
    provenance=st.selectbox("Data tier",["SYNTHETIC","REPLAY:demo-case","LIVE"])
    district=st.text_input("District","Patna"); state=st.text_input("State","Bihar")
    run=st.button("Run nowcast",type="primary")
if run:
    payload={"provenance":provenance,"district":district,"state":state,"radar_field":[[20,36,40,44,20],[20,38,52,58,23],[18,37,55,62,26],[12,20,38,43,20]],"flash":False}
    try: data=requests.post("http://127.0.0.1:8000/forecast",json=payload,timeout=5).json()
    except Exception as e: st.error(f"Start the API first: {e}"); st.stop()
    st.warning(f"PROVENANCE: {data['provenance']} · latency {data['latency_ms']} ms · model {data['model']['model_version']}")
    cols=st.columns(5)
    for col,(h,v) in zip(cols,data["forecast"].items()): col.metric(f"{h} min lightning",f"{v['lightning_probability']:.0%}",f"± {((v['confidence_interval'][1]-v['confidence_interval'][0])/2):.0%}")
    left,right=st.columns([1,1])
    with left:
        st.subheader("Storm-cell output")
        st.dataframe(pd.DataFrame(data["storm_cells"]))
        st.subheader("LAD explainability")
        st.line_chart(pd.DataFrame({"P_t":[data["lad_state"]["pressure"]],"proxy":[data["lad_state"]["proxy"]]}))
    with right:
        st.subheader("Sensor health / provenance")
        st.dataframe(pd.DataFrame(data["sensor_health"]),use_container_width=True)
        st.subheader("NDMA action text")
        st.info(data["alert_context"]["ndma_actions"])
else:
    st.info("Select a data tier and run a scenario. LIVE mode requires real normalized sensor payload through the API; it never silently falls back to random data.")
