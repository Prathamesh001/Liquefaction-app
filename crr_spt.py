"""
Streamlit module: CRR (SPT path)

Usage: import and call run() from main app.py router.

This implements the iterative solver to find (N1)60cs and m, then computes
CRR_base (Mw=7.5, sigma_v0=1 atm), MSF, C_sigma, K_sigma and final CRR.

Notes:
- N60 is provided directly by the user (N60 measured, already corrected to 60% energy)
- FC (fines content) can be provided directly or computed from Ic (soil behaviour index) if the user supplies Ic.
- The app shows the formula for N60 corrections but does not compute CE, CR, CB, CS, Nm automatically.
"""

import streamlit as st
import numpy as np
from math import sqrt, log10

def run():
    st.header("CRR — SPT method (iterative)")
    st.markdown("""
    This module computes CRR from SPT data using the iterative procedure:

    1. Assume m
    2. Compute C_N = (P_a / sigma_vc)^m (capped at 1.7)
    3. Compute (N1)60 = C_N * N60
    4. Compute Δ(N1)60 from FC
    5. (N1)60cs = (N1)60 + Δ(N1)60
    6. Compute new m = 0.784 - 0.0768 * sqrt((N1)60cs)
    7. Repeat until m converges

    Finally CRR_base = exp(-2.8 + A + B^2 - C^3 + D^4) where the polynomial terms use (N1)60cs
    """)

    col1, col2 = st.columns(2)
    with col1:
        N60 = st.number_input("Corrected SPT N60 value (input N60)", value=40.0, format="%.3f")
        sigma_vc = st.number_input("Effective vertical consolidation stress, σ'vc (kPa)", value=100.0, format="%.3f")
        sigma_v0 = st.number_input("Current effective vertical stress at depth, σ'v0 (kPa)", value=100.0, format="%.3f")
        Pa = st.number_input("Atmospheric pressure Pa (kPa)", value=101.325, format="%.6f")

    with col2:
        M = st.number_input("Mw — magnitude of largest likely earthquake (M)", value=7.5, format="%.3f")
        st.write("Note: N60 is expected to be the measured N60 (already corrected). If you have raw N, use the formula shown below to compute N60.")

    st.markdown("---")
    st.subheader("Fines content (FC) / Ic handling")
    use_direct_FC = st.checkbox("Provide FC directly?", value=True)
    if use_direct_FC:
        FC = st.number_input("Fines content, FC (%)", value=5.0, format="%.3f")
        Ic = None
        st.info("FC provided directly. Δ(N1)60 will be computed from FC.")
    else:
        Ic = st.number_input("Provide soil behaviour type index Ic (if available)", value=2.0, format="%.3f")
        C_FC = -0.07
        FC = 80.0 * (Ic + C_FC) - 137.0
        FC = float(max(min(FC, 100.0), 0.0))
        st.write(f"Computed FC from Ic (C_FC={C_FC}): FC = {FC:.3f} %")

    st.markdown("---")
    st.subheader("Iteration settings")
    init_m = st.number_input("Initial guess for m", value=0.6, format="%.6f")
    tol = st.number_input("Tolerance for m convergence", value=1e-4, format="%.8f")
    max_iter = st.number_input("Maximum iterations", value=200, step=10)

    provide_MSF_manual = st.checkbox("Provide MSF_max manually? (otherwise computed from SPT expression)", value=False)
    if provide_MSF_manual:
        MSF_max_user = st.number_input("MSF_max (manual)", value=1.6, format="%.3f")
    else:
        MSF_max_user = None

    st.markdown("---")

    # show formula for N60 corrections (informational)
    st.markdown("**Note (informational):** If you instead had raw N, then:")
    st.latex(r"N_{60} = C_N \; C_E \; C_R \; C_B \; C_S \; N_m")
    st.caption("N60 input is expected to be the corrected 60%-energy N-value. The app accepts N60 directly for the iterative solver.")

    # start iterative loop
    st.markdown("### Iterative solver to find (N1)60cs and m")
    q = N60  # N60 is the provided corrected N60

    m = float(init_m)
    last_m = None
    N1_60cs = None
    converged = False

    for it in range(int(max_iter)):
        # CN
        CN = (Pa / sigma_vc) ** m if sigma_vc > 0 else 1.0
        if CN > 1.7:
            CN = 1.7
        # (N1)60
        N1_60 = CN * q
        # Δ(N1)60 = exp(1.63 + 9.7/(FC+0.01) - (15.7/(FC+0.01))^2)
        denom = FC + 0.01
        if denom <= 0:
            delta_N1_60 = 0.0
        else:
            exponent = 1.63 + (9.7 / denom) - (15.7 / denom) ** 2
            delta_N1_60 = np.exp(exponent)
        N1_60cs_new = N1_60 + delta_N1_60
        if N1_60cs_new < 1e-6:
            N1_60cs_new = 1e-6
        # compute new m
        m_new = 0.784 - 0.0768 * sqrt(N1_60cs_new)
        # clamp to plausible range
        if m_new < 0.246:
            m_new = 0.246
        if m_new > 0.782:
            m_new = 0.782
        # convergence check
        if last_m is not None and abs(m_new - last_m) < tol:
            m = m_new
            N1_60cs = N1_60cs_new
            iter_count = it + 1
            converged = True
            break
        last_m = m_new
        m = m_new
        N1_60cs = N1_60cs_new
    else:
        iter_count = max_iter

    if converged:
        st.success(f"Converged in {iter_count} iterations")
    else:
        st.warning(f"Did not converge within {iter_count} iterations; last m={m:.6f}")

    st.write(f"Final m = {m:.6f}")
    st.write(f"(N1)60cs = {N1_60cs:.4f}")

    # CRR_base formula (from image)
    N = N1_60cs
    CRR_base = np.exp(-2.8 + (N / 14.1) + (N / 126.0) ** 2 - (N / 23.6) ** 3 + (N / 25.4) ** 4)
    st.write(f"CRR (base, Mw=7.5, σ'v0=1 atm) = {CRR_base:.6e}")

    # MSF_max from SPT expression
    msf_max_spt = 1.09 * (N1_60cs / 31.5) ** 2
    msf_max_spt = min(msf_max_spt, 2.2)
    st.write(f"MSF_max (from SPT expression) = {msf_max_spt:.6f} (capped at 2.2)")

    if provide_MSF_manual and MSF_max_user is not None:
        MSF_max = MSF_max_user
        st.info(f"Using user-provided MSF_max = {MSF_max:.3f}")
    else:
        MSF_max = msf_max_spt

    # MSF
    MSF = 1.0 + (MSF_max - 1.0) * (8.64 * np.exp(-0.25 * M) - 1.325)
    st.write(f"Magnitude scaling factor MSF = {MSF:.6f}")

    # C_sigma from SPT formula: 1/(18.9 - 2.55*sqrt(N1_60cs)) <= 0.3
    try:
        denom_c = 18.9 - 2.55 * sqrt(N1_60cs)
        if denom_c <= 0:
            C_sigma = 0.3
        else:
            C_sigma = 1.0 / denom_c
            C_sigma = min(C_sigma, 0.3)
    except Exception:
        C_sigma = 0.3

    st.write(f"C_sigma (SPT formula) = {C_sigma:.6f}")

    # K_sigma
    if sigma_v0 <= 0:
        K_sigma = 1.0
    else:
        K_sigma = 1.0 - C_sigma * np.log(sigma_v0 / Pa)
        K_sigma = min(K_sigma, 1.1)

    st.write(f"K_sigma = {K_sigma:.6f}")

    # final CRR
    CRR = CRR_base * MSF * K_sigma
    st.markdown("---")
    st.subheader("Final result (SPT path)")
    st.metric("Cyclic Resistance Ratio (CRR)", f"{CRR:.6e}")

    st.caption("This module assumes N60 input is available. If you have raw N, use correction factors CE, CR, CB, CS and Nm to compute N60 before running this module.")
