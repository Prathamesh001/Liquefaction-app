import streamlit as st
import numpy as np
from math import sqrt, log10

def run():
    st.set_page_config(
        page_title="CRR-SPT Calculator",
        layout="wide"
    )
    st.header("CRR — SPT method (iterative)")

    col1, col2 = st.columns(2)
    with col1:
        N60 = st.number_input("Corrected SPT N60 value (input N60)", value=40.0, format="%.3f")
        sigma_vc = st.number_input("Effective vertical consolidation stress, σ'vc (kPa)", value=100.0, format="%.3f")
        sigma_v0 = st.number_input("Current effective vertical stress at depth, σ'v0 (kPa)", value=100.0, format="%.3f")
        Pa = st.number_input("Atmospheric pressure Pa (kPa)", value=101.325, format="%.6f")

    with col2:
        M = st.number_input("Mw — magnitude of largest likely earthquake (M)", value=7.5, format="%.3f")

    st.markdown("---")
    st.subheader("Fines content (FC)")
    # REQUIRED FC input (no auto-compute)
    FC = st.number_input("Fines content, FC (%) — provide directly", value=5.0, format="%.3f")

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
    st.markdown("**Note (informational):** If you instead had raw N, use correction factors CE, CR, CB, CS and Nm to compute N60 before running this module.")
    st.latex(r"N_{60} = C_N \; C_E \; C_R \; C_B \; C_S \; N_m")

    # Iteration
    q = N60
    m = float(init_m)
    last_m = None
    N1_60cs = None
    converged = False

    for it in range(int(max_iter)):
        CN = (Pa / sigma_vc) ** m if sigma_vc > 0 else 1.0
        if CN > 1.7:
            CN = 1.7

        N1_60 = CN * q

        denom = FC + 0.01
        if denom <= 0:
            delta_N1_60 = 0.0
        else:
            exponent = 1.63 + (9.7 / denom) - (15.7 / denom) ** 2
            delta_N1_60 = np.exp(exponent)

        N1_60cs_new = N1_60 + delta_N1_60
        if N1_60cs_new < 1e-6:
            N1_60cs_new = 1e-6

        m_new = 0.784 - 0.0768 * sqrt(N1_60cs_new)

##        # clamp m if desired
##        if m_new < 0.246:
##            m_new = 0.246
##        if m_new > 0.782:
##            m_new = 0.782

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
    st.write(f"CN = {CN:.4f}")
    st.write(f"(N1)60 = {N1_60:.4f}")
    st.write(f"(N1)60cs = {N1_60cs:.4f}")

    # CRR base
    N = N1_60cs
    CRR_base = np.exp(-2.8 + (N / 14.1) + (N / 126.0) ** 2 - (N / 23.6) ** 3 + (N / 25.4) ** 4)
    st.write(f"CRR (base, Mw=7.5, σ'v0=1 atm) = {CRR_base:.6e}")

    msf_max_spt = 1.09 * (N1_60cs / 31.5) ** 2
    msf_max_spt = min(msf_max_spt, 2.2)
    st.write(f"MSF_max (from SPT expression) = {msf_max_spt:.6f} (capped at 2.2)")

    if provide_MSF_manual and MSF_max_user is not None:
        MSF_max = MSF_max_user
        st.info(f"Using user-provided MSF_max = {MSF_max:.3f}")
    else:
        MSF_max = msf_max_spt

    MSF = 1.0 + (MSF_max - 1.0) * (8.64 * np.exp(-0.25 * M) - 1.325)
    st.write(f"Magnitude scaling factor MSF = {MSF:.6f}")

    # C_sigma from SPT
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

    CRR = CRR_base * MSF * K_sigma
    st.markdown("---")
    st.subheader("Final result (SPT path)")
    st.metric("Cyclic Resistance Ratio (CRR)", f"{CRR:.6e}")

    st.caption("This module expects N60 input. If you have raw N, compute N60 first using correction factors.")
