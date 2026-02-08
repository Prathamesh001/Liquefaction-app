"""
Streamlit module: CRR — DMT method

Implements CRR from Marchetti DMT using IS 1893 / published correlations.

Assumptions (as per your instruction):
- CRR_base is computed directly from KD (horizontal stress index)
- MSF and K_sigma are applied in the same way as CPT/SPT modules
- MSF and K_sigma are taken directly as inputs (no iteration required)

Usage:
    from crr_dmt import run
    run()
"""

import streamlit as st
import numpy as np

def run():
    st.set_page_config(
        page_title="CRR — DMT Calculator",
        layout="wide"
    )

    st.header("CRR — DMT method")

    st.markdown("""
    This module computes the **Cyclic Resistance Ratio (CRR)** using **Dilatometer Test (DMT)** data.

    The formulation is **non-iterative** and is valid for:
    - **2 < K_D < 6**
    - **I_D > 1.2**
    """)

    col1, col2 = st.columns(2)
    with col1:
        p0 = st.number_input("Lift-off pressure p₀ (kPa)", value=200.0, format="%.3f")
        p1 = st.number_input("Expansion pressure p₁ (kPa)", value=400.0, format="%.3f")
        u0 = st.number_input("Pore pressure u₀ (kPa)", value=50.0, format="%.3f")
        sigma_v0 = st.number_input("Current effective vertical stress σ'v0 (kPa)", value=100.0, format="%.3f")

    with col2:
        Pa = st.number_input("Atmospheric pressure Pa (kPa)", value=101.325, format="%.6f")
        MSF = st.number_input("Magnitude Scaling Factor MSF", value=1.0, format="%.6f")
        K_sigma = st.number_input("Overburden correction factor Kσ", value=1.0, format="%.6f")

    st.markdown("---")
    st.subheader("Computed DMT indexes")

    # KD = (p1 - p0) / sigma_v0
    if sigma_v0 > 0:
        K_D = (p1 - p0) / sigma_v0
    else:
        K_D = 0.0

    # ID = (p1 - p0) / (p0 - u0)
    if (p0 - u0) > 0:
        I_D = (p1 - p0) / (p0 - u0)
    else:
        I_D = 0.0

    st.write(f"Horizontal stress index K_D = {K_D:.4f}")
    st.write(f"Material index I_D = {I_D:.4f}")

    if not (2.0 < K_D < 6.0):
        st.warning("K_D is outside the recommended validity range (2 < K_D < 6). Results should be used with caution.")
    if not (I_D > 1.2):
        st.warning("I_D ≤ 1.2. CRR correlation may not be applicable for this soil.")

    st.markdown("---")
    st.subheader("CRR computation")

    # CRR_base = [93 (0.025 KD)^2 + 0.08] <= 1.0
    CRR_base = 93.0 * (0.025 * K_D) ** 2 + 0.08
    CRR_base = min(CRR_base, 1.0)

    st.write(f"CRR_base (Mw=7.5, σ'v0=1 atm) = {CRR_base:.6f}")
    st.write(f"Applied MSF = {MSF:.6f}")
    st.write(f"Applied Kσ = {K_sigma:.6f}")

    CRR = CRR_base * MSF * K_sigma

    st.markdown("---")
    st.subheader("Final result (DMT path)")
    st.metric("Cyclic Resistance Ratio (CRR)", f"{CRR:.6e}")

    st.caption("CRR computed using DMT-based correlation. User must ensure validity limits of KD and ID are satisfied.")
