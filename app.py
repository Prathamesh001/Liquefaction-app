import streamlit as st

from csr import run as run_csr
from crr_cpt import run as run_crr_cpt
from crr_spt import run as run_crr_spt
from crr_dmt import run as run_crr_dmt
from crr_vs import run as run_crr_vs
from crr_clay import run as run_crr_clay


# ----------------------------
# Config
# ----------------------------
st.set_page_config(
    page_title="Liquefaction Potential Analyser",
    layout="wide",
)

# ----------------------------
# App state
# ----------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"


# ----------------------------
# HOME PAGE (no sidebar here)
# ----------------------------
def home():
    st.title("Liquefaction Potential Assessment")
    st.caption("IS 1893 (2025) aligned")

    st.markdown("### Select analysis")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("CSR", key="btn_csr", use_container_width=True):
            st.session_state.page = "CSR"
            st.rerun()

        if st.button("CRR – CPT", key="btn_cpt", use_container_width=True):
            st.session_state.page = "CRR – CPT"
            st.rerun()

        if st.button("CRR – SPT", key="btn_spt", use_container_width=True):
            st.session_state.page = "CRR – SPT"
            st.rerun()

    with col2:
        if st.button("CRR – DMT", key="btn_dmt", use_container_width=True):
            st.session_state.page = "CRR – DMT"
            st.rerun()

        if st.button("CRR – Vs", key="btn_vs", use_container_width=True):
            st.session_state.page = "CRR – Vs"
            st.rerun()

        if st.button(
            "CRR – Clay / Plastic silt",
            key="btn_clay",
            use_container_width=True
        ):
            st.session_state.page = "CRR – Clay / Plastic silt"
            st.rerun()
            

        st.divider()

        st.caption(
            "Prathamesh Varma  ·  "
            "[LinkedIn](https://www.linkedin.com/in/prathameshvarma/)  ·  "
            "[Website](https://prathameshvarma.wordpress.com/)"
        )
        st.caption(
            "Prof. Mohan S C  ·  "
            "[Web Link](https://www.bits-pilani.ac.in/hyderabad/mohan-sc/)"
        )
        st.divider()
        st.caption(
            "Initial release (v0.1). Results should be independently verified before professional use."
        )



# ----------------------------
# SIDEBAR (only for modules)
# ----------------------------
def module_sidebar():
    st.sidebar.title("Liquefaction Toolkit")

    options = [
        "CSR",
        "CRR – CPT",
        "CRR – SPT",
        "CRR – DMT",
        "CRR – Vs",
        "CRR – Clay / Plastic silt",
        "Home",
    ]

    # Set default index based on current page
    try:
        index = options.index(st.session_state.page)
    except ValueError:
        index = 0

    page = st.sidebar.radio(
        "Switch analysis",
        options,
        index=index,
    )

    if page != st.session_state.page:
        st.session_state.page = page
        st.rerun()

    st.sidebar.divider()
    st.sidebar.caption(
        "Initial release (v0.1). Educational and preliminary analysis only. "
        "Results should be independently verified before professional use."
        )


# ----------------------------
# ROUTER
# ----------------------------
if st.session_state.page == "Home":
    # Hide sidebar on Home (important for mobile clarity)
    st.sidebar.empty()
    home()

elif st.session_state.page == "CSR":
    module_sidebar()
    run_csr()

elif st.session_state.page == "CRR – CPT":
    module_sidebar()
    run_crr_cpt()

elif st.session_state.page == "CRR – SPT":
    module_sidebar()
    run_crr_spt()

elif st.session_state.page == "CRR – DMT":
    module_sidebar()
    run_crr_dmt()

elif st.session_state.page == "CRR – Vs":
    module_sidebar()
    run_crr_vs()

elif st.session_state.page == "CRR – Clay / Plastic silt":
    module_sidebar()
    run_crr_clay()
