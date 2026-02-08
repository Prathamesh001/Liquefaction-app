import streamlit as st

from csr import run as run_csr
from crr_cpt import run as run_crr_cpt
from crr_spt import run as run_crr_spt
from crr_dmt import run as run_crr_dmt
from crr_vs  import run as run_crr_vs

st.set_page_config(page_title="Liquefaction Analysis Toolkit", layout="wide")

st.sidebar.title("Analysis type")

choice = st.sidebar.radio(
    "Select module",
    [
        "CSR",
        "CRR – CPT",
        "CRR – SPT",
        "CRR – DMT",
        "CRR – Vs"
    ]
)

if choice == "CSR":
    run_csr()
elif choice == "CRR – CPT":
    run_crr_cpt()
elif choice == "CRR – SPT":
    run_crr_spt()
elif choice == "CRR – DMT":
    run_crr_dmt()
elif choice == "CRR – Vs":
    run_crr_vs()
