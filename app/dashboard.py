"""Dashboard stub for the nowcasting prototype."""
import streamlit as st

st.set_page_config(page_title="Thunderstorm & Lightning Nowcast", layout="wide")
st.title("SIH 2026 PS 26072 — Thunderstorm & Lightning Nowcasting")

st.subheader("Prototype status")
st.info("Verification, LAD state, and API serving are implemented before the dashboard layer.")
st.write("- Provenance tagging: LIVE / REPLAY:<case-study> / SYNTHETIC")
st.write("- Separate storm-cell module present")
st.write("- LAD pressure state and probability outputs available")
st.write("- Rare-event metrics and leakage checks implemented")
st.write("- FastAPI serving layer connected to the same logic")

with st.expander("AI/ML design summary"):
    st.markdown(
        """
        - LAD cell: `P_t = gamma * P_(t-1) + f_theta(x_t)` with discharge on flash `P_t <- P_t * (1-rho)`
        - Storm cells: connected-component detection + tracking
        - Multi-horizon output: 5, 15, 30, 60, 180 minutes
        - Observed outputs: thunderstorm probability and lightning probability
        - Provenance labeling: every record carries source and provenance metadata
        """
    )
