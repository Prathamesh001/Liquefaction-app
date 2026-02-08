import streamlit as st

from csr import run as run_csr
from crr_cpt import run as run_crr_cpt
from crr_spt import run as run_crr_spt
from crr_dmt import run as run_crr_dmt
from crr_vs import run as run_crr_vs
from crr_clay import run as run_crr_clay


# ---------- HOME PAGE ----------
def home():
    st.title("Liquefaction Potential Assessment")
    st.caption("IS 1893 (2025) aligned • Mobile friendly")

    st.markdown("### Select analysis")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("CSR"):
            st.session_state.page = "CSR"
            st.rerun()
        if st.button("CRR – CPT"):
            st.session_state.page = "CRR – CPT"
            st.rerun()
        if st.button("CRR – SPT"):
            st.session_state.page = "CRR – SPT"
            st.rerun()

    with col2:
        if st.button("CRR – DMT"):
            st.session_state.page = "CRR – DMT"
            st.rerun()
        if st.button("CRR – Vs"):
            st.session_state.page = "CRR – Vs"
            st.rerun()
        if st.button("CRR – Clay / Plastic silt"):
            st.session_state.page = "CRR – Clay / Plastic silt"
            st.rerun()


# ---------- PAGE STATE ----------
if "page" not in st.session_state:
    st.session_state.page = "Home"


st.set_page_config(
    page_title="Liquefaction Potential Analyser",
    layout="wide"
)


# ---------- SIDEBAR ----------
st.sidebar.title("Liquefaction Toolkit")

st.sidebar.radio(
    "Analysis type",
    [
        "Home",
        "CSR",
        "CRR – CPT",
        "CRR – SPT",
        "CRR – DMT",
        "CRR – Vs",
        "CRR – Clay / Plastic silt",
    ],
    key="page",   # 🔥 THIS IS THE FIX
)



# ---------- ROUTER ----------
if st.session_state.page == "Home":
    home()
elif st.session_state.page == "CSR":
    run_csr()
elif st.session_state.page == "CRR – CPT":
    run_crr_cpt()
elif st.session_state.page == "CRR – SPT":
    run_crr_spt()
elif st.session_state.page == "CRR – DMT":
    run_crr_dmt()
elif st.session_state.page == "CRR – Vs":
    run_crr_vs()
elif st.session_state.page == "CRR – Clay / Plastic silt":
    run_crr_clay()
