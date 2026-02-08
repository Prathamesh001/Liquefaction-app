import streamlit as st

from csr import run as run_csr
from crr_cpt import run as run_crr_cpt
from crr_spt import run as run_crr_spt
from crr_dmt import run as run_crr_dmt
from crr_vs import run as run_crr_vs
from crr_clay import run as run_crr_clay

# -----------------------
# Page config (first)
# -----------------------
st.set_page_config(
    page_title="Liquefaction Potential Analyser",
    layout="wide"
)

# -----------------------
# App-owned state
# -----------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

# -----------------------
# Home page function
# (buttons only update 'page', not 'nav')
# -----------------------
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

# -----------------------
# Sidebar radio (widget-owned key = "nav")
# We initialize the radio's selected index using st.session_state.page,
# so the radio will not overwrite the app-owned page on reruns.
# -----------------------
st.sidebar.title("Liquefaction Toolkit")

options = [
    "Home",
    "CSR",
    "CRR – CPT",
    "CRR – SPT",
    "CRR – DMT",
    "CRR – Vs",
    "CRR – Clay / Plastic silt",
]

# Compute index safely based on current page
try:
    index_for_radio = options.index(st.session_state.page)
except ValueError:
    index_for_radio = 0

# radio owns key "nav"; do NOT write to st.session_state["nav"] anywhere
st.sidebar.radio(
    "Analysis type",
    options,
    index=index_for_radio,
    key="nav",
)

# -----------------------
# Sync radio -> page (allowed: writing to page is fine)
# If the user changed the radio, reflect that in the app-owned page.
# -----------------------
if "nav" in st.session_state and st.session_state.nav != st.session_state.page:
    st.session_state.page = st.session_state.nav

# -----------------------
# Router: render the chosen module
# -----------------------
if st.session_state.page == "Home":
    home()

elif st.session_state.page == "CSR":
    # optional: add a back-to-home button inside modules if you like
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

else:
    # fallback
    st.warning("Unknown page - returning to Home")
    st.session_state.page = "Home"
    st.experimental_rerun()
