"""
Streamlit module: CRR — Vs (Shear Wave Velocity) method

Implements CRR using shear wave velocity (Vs) based correlation
(as per IS 1893 / Andrus–Stokoe type formulation).

CRR_total = CRR_Mw=7.5 * MSF * K_sigma

Non-iterative method.
"""

import streamlit as st
import numpy as np

def run():
    st.header("CRR — Vs method (shear wave velocity)")

    st.markdown("""
    This module computes **Cyclic Resistance Ratio (CRR)** using
    **shear wave velocity (Vs)** measurements.

    The formulation is non-iterative and suitable for clean sands
    and sands with limited fines.
    """)

    col1, col2 = st.columns(2)

    with col1:
        Vs = st.number_input("Measured shear wave velocity Vs (m/s)", value=180.0, format="%.3f")
        sigma_v0 = st.number_input("Effective vertical stress σ'v0 (kPa)", value=100.0, format="%.3f")
        Pa = st.number_input("Atmospheric pressure Pa (kPa)", value=101.325, format="%.6f")
        FC = st.number_input("Fines content FC (%)", value=5.0, format="%.3f")

    with col2:
        M = st.number_input("Earthquake magnitude Mw", value=7.5, format="%.3f")
        MSF = st.number_input("Magnitude Scaling Factor (MSF)", value=1.0, format="%.6f")
        K_sigma = st.number_input("Overburden correction factor Kσ", value=1.0, format="%.6f")

    st.markdown("---")
    st.subheader("Overburden-corrected shear wave velocity")

    # Vs1 = (Pa / sigma_v0)^0.25 * Vs
    if sigma_v0 > 0:
        Vs1 = (Pa / sigma_v0) ** 0.25 * Vs
    else:
        Vs1 = Vs

    st.write(f"Vs₁ (overburden-corrected shear wave velocity) = {Vs1:.3f} m/s")

    st.markdown("---")
    st.subheader("Limiting upper shear wave velocity Vs₁* for liquefaction")

    # Vs1* definition based on FC
    if FC < 5.0:
        Vs1_star = 200.0 + 15.0 * ((35.0 - FC) / 30.0)
        st.write("FC < 5% → interpolated Vs₁*")
    else:
        Vs1_star = 215.0
        st.write("FC ≥ 5% → Vs₁* = 215 m/s")

    st.write(f"Vs₁* (limiting value) = {Vs1_star:.3f} m/s")

    if Vs1 >= Vs1_star:
        st.warning("Vs₁ ≥ Vs₁* → soil not expected to liquefy (CRR may be very high).")

    st.markdown("---")
    st.subheader("CRR computation")

    # constants
    a = 0.022
    b = 2.8

    # CRR_Mw=7.5
    if Vs1 > 0 and Vs1 < Vs1_star:
        CRR_base = a * (Vs1 / 100.0) ** 2 + b * ((1.0 / (Vs1_star - Vs1)) - (1.0 / Vs1_star))
    else:
        CRR_base = a * (Vs1 / 100.0) ** 2

    st.write(f"CRR_base (Mw = 7.5, σ'v0 = 1 atm) = {CRR_base:.6f}")
    st.write(f"Applied MSF = {MSF:.6f}")
    st.write(f"Applied Kσ = {K_sigma:.6f}")

    CRR = CRR_base * MSF * K_sigma

    st.markdown("---")
    st.subheader("Final result (Vs path)")
    st.metric("Cyclic Resistance Ratio (CRR)", f"{CRR:.6e}")

    st.caption("CRR computed using shear wave velocity correlation. Ensure applicability limits for soil type and fines content.")
