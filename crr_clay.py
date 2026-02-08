# crr_clay.py
import streamlit as st
import numpy as np

def run():
    st.set_page_config(
        page_title="CRR — clay & plastic silt",
        layout="wide"
    )
    st.header("CRR — clay & plastic silt")
    st.markdown("""
    Compute CRR for clay / plastic silt using one of:
    - CPT-based (Qtn)
    - DMT-based (K_D)
    - Empirical OCR-based
    Final CRR = CRR_base * MSF * K_sigma (CRR_base capped at 1.0).
    """)

    col1, = st.columns(1)
    with col1:
        method = st.selectbox("Method", ["CPT", "DMT", "OCR"])
        Pa = st.number_input("Atmospheric pressure Pa (kPa)", value=101.325, format="%.6f")
        MSF = st.number_input("MSF (magnitude scaling factor)", value=1.0, format="%.6f")
        K_sigma = st.number_input("K_sigma (overburden correction)", value=1.0, format="%.6f")
        st.write("Method-specific inputs below")


    st.markdown("---")

    CRR_base = None

    if method == "CPT":
        st.subheader("CPT inputs")
        qt = st.number_input("Cone tip resistance qt (kPa)", value=150.0, format="%.3f")
        sigma_vc = st.number_input("Effective consolidation stress σ'vc (kPa)", value=100.0, format="%.3f")
        n_star = st.selectbox("n* (choose exponent)", [1.0, 0.5], index=0, format_func=lambda x: f"{x:.1f}")
        # compute Qtn safely
        if sigma_vc <= 0:
            st.error("σ'vc must be > 0")
            return
        Qtn = ((qt - sigma_vc) / Pa) * (Pa / sigma_vc) ** n_star
        st.write(f"Normalized tip resistance Qtn = {Qtn:.4f}")
        CRR_base = 0.053 * Qtn

    elif method == "DMT":
        st.subheader("DMT inputs")
        p0 = st.number_input("p0 (lift-off pressure) (kPa)", value=200.0, format="%.3f")
        p1 = st.number_input("p1 (expansion pressure) (kPa)", value=400.0, format="%.3f")
        sigma_v0 = st.number_input("Effective vertical stress σ'v0 (kPa)", value=100.0, format="%.3f")
        if sigma_v0 <= 0:
            st.error("σ'v0 must be > 0")
            return
        K_D = (p1 - p0) / sigma_v0
        st.write(f"Horizontal stress index K_D = {K_D:.4f}")
        CRR_base = 0.074 * (K_D ** 1.25)

    else:  # OCR empirical
        st.subheader("OCR inputs")
        OCR = st.number_input("Overconsolidation ratio (OCR)", value=2.0, format="%.3f")
        if OCR <= 0:
            st.error("OCR must be > 0")
            return
        CRR_base = 0.18 * (OCR ** 0.8)
        st.write(f"OCR = {OCR:.3f}")

    # Clamp CRR_base to <= 1.0
    CRR_base = float(CRR_base)
    st.write(f"CRR_base (Mw=7.5, σ'v0=1 atm) = {CRR_base:.6f}")

    # final
    CRR = CRR_base * MSF * K_sigma
    st.markdown("---")
    st.subheader("Final CRR (clay/plastic silt)")
    st.metric("Cyclic Resistance Ratio (CRR)", f"{CRR:.6e}")

    st.caption("Notes: - Qtn uses n* as chosen (1.0 typical for clay). "
               "- Ensure units are consistent (kPa).")
