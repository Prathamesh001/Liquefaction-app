def run():
    """
    Streamlit app: CRR calculator (CPT path, iterative solution for m and qc1Ncs)
    Improved: accepts FC directly or computes it from inputs; computes MSF_max from qc1Ncs by default.

    How to run:
        pip install streamlit numpy
        streamlit run crr_cpt_streamlit.py

    Notes:
     - This app currently implements the CPT-based iterative solver to find qc1Ncs and m,
       calculates the magnitude scaling factor (MSF), overburden correction C_sigma, K_sigma and
       final CRR using the formulas you provided.
     - Units: pressures in kPa. Pa (atmospheric pressure) default set to 101.325 kPa.
    """

    import streamlit as st
    import numpy as np
    from math import log10, sqrt

    st.set_page_config(page_title="CRR (CPT) calculator", layout="centered")
    st.title("CRR calculator — CPT (iterative solver)")

    # --- Inputs ---
    col1, col2 = st.columns(2)
    with col1:
        qt = st.number_input("Cone tip resistance, qt (kPa)", value=150.0, format="%.3f")
        sigma_vc = st.number_input("Effective vertical consolidation stress, σ'vc (kPa)", value=100.0, format="%.3f")
        sigma_v0 = st.number_input("Current effective vertical stress at depth, σ'v0 (kPa)", value=100.0, format="%.3f")
        Pa = st.number_input("Atmospheric pressure Pa (kPa)", value=101.325, format="%.6f")

    with col2:
        M = st.number_input("Mw — magnitude of largest likely earthquake (M)", value=7.5, format="%.3f")
        n_for_Qtn = st.selectbox("n for Qtn (use 0.5 for sand, 1.0 for clay)", options=[0.5, 1.0], index=0)

    st.markdown("---")

    # FC / Ic handling
    use_direct_FC = st.checkbox("Provide fines content (FC) directly?", value=False)
    if use_direct_FC:
        FC = st.number_input("Fines content, FC (percent)", value=5.0, format="%.3f")
        st.info("Since you provided FC directly, sleeve friction fs is optional and not required for FC calculation.")
        fs = st.number_input("Sleeve friction, fs (kPa) — optional", value=0.0, format="%.3f")
        Ic = None
    else:
        st.write("We'll compute FC from Ic (soil behaviour type index). You may enter Ic manually or let the app compute it using Qtn and F.")
        provide_Ic_manual = st.checkbox("Provide Ic (soil behaviour index) manually?", value=False)
        if provide_Ic_manual:
            Ic = st.number_input("Soil behaviour type index, Ic", value=0.0, format="%.3f")
            fs = st.number_input("Sleeve friction, fs (kPa) — required to compute friction ratio F", value=5.0, format="%.3f")
        else:
            # compute Ic from Qtn and F: need fs
            fs = st.number_input("Sleeve friction, fs (kPa) — required to compute Qtn and F", value=5.0, format="%.3f")
            Ic = None

    st.markdown("---")

    # Iteration options
    st.markdown("**Iteration / solver settings**")
    init_m = st.number_input("Initial guess for m", value=0.6, format="%.6f")
    tol = st.number_input("Tolerance for m convergence", value=1e-4, format="%.8f")
    max_iter = st.number_input("Maximum iterations", value=200, step=10)

    # MSF_max override option
    provide_MSF_manual = st.checkbox("Provide MSF_max manually? (If unchecked, MSF_max is computed from qc1Ncs)", value=False)
    if provide_MSF_manual:
        MSF_max_user = st.number_input("MSF_max (manual)", value=1.6, format="%.3f")
    else:
        MSF_max_user = None

    # --- helper functions ---

    def compute_Qtn(qt, sigma_vc, Pa, n=float(n_for_Qtn)):
        # Qtn = ((qt - sigma_vc)/Pa) * (Pa/sigma_vc)^n
        if qt - sigma_vc <= 0 or sigma_vc <= 0:
            return 1e-9
        return ((qt - sigma_vc) / Pa) * (Pa / sigma_vc) ** n


    def compute_F_from_fs(qt, fs, sigma_vc):
        if qt - sigma_vc <= 0:
            return 1e-9
        return 100.0 * (fs / (qt - sigma_vc))


    def compute_Ic_from_Q_F(Qtn, F):
        # Ic = sqrt((3.47 - logQ)^2 + (1.22 + logF)^2)
        logQ = log10(Qtn) if Qtn > 0 else -10.0
        logF = log10(F) if F > 0 else -10.0
        return sqrt((3.47 - logQ) ** 2 + (1.22 + logF) ** 2)


    def estimate_FC_from_Ic(Ic, C_FC=-0.07):
        return 80.0 * (Ic + C_FC) - 137.0


    def delta_qc1N_formula(qc1N, FC):
        denom = (FC + 2.0)
        exponent = 1.63 - (9.7 / denom) - (15.7 / denom) ** 2
        return (11.9 + qc1N / 14.6) * np.exp(exponent)


    def compute_m_from_qc1Ncs(qc1Ncs):
        return 1.338 - 0.249 * (qc1Ncs ** 0.264)

    # --- compute FC, Ic, F depending on inputs ---
    C_FC = -0.07

    if use_direct_FC:
        # FC provided directly
        computed_F = compute_F_from_fs(qt, fs, sigma_vc) if fs > 0 else None
        Ic_display = None
        st.write(f"C_FC (constant) = {C_FC}")
    else:
        # FC must be computed
        computed_F = compute_F_from_fs(qt, fs, sigma_vc)
        st.write(f"Computed sleeve friction ratio F = {computed_F:.4f} % (using fs={fs} kPa)")
        st.write(f"C_FC (constant) = {C_FC}")
        if provide_Ic_manual and Ic is not None and Ic != 0.0:
            Ic_display = Ic
            st.write(f"Using manual Ic = {Ic_display:.4f}")
        else:
            Qtn = compute_Qtn(qt, sigma_vc, Pa, n_for_Qtn)
            Ic_display = compute_Ic_from_Q_F(Qtn, computed_F)
            st.write(f"Computed Ic from Qtn & F = {Ic_display:.4f}")
        FC = estimate_FC_from_Ic(Ic_display, C_FC=C_FC)
        # clamp
        FC = float(max(min(FC, 100.0), 0.0))

    if use_direct_FC:
        st.write(f"Fines content (FC) (user provided) = {FC:.3f} %")
    else:
        st.write(f"Estimated fines content (FC) from Ic = {FC:.3f} %")

    st.markdown("---")

    # --- Iterative solver for CPT path ---
    st.markdown("### Iterative solution (CPT) to find qc1Ncs and m")

    # normalized tip resistance qCN
    qCN = qt / Pa

    m = float(init_m)
    qc1Ncs = None
    last_m = None
    converged = False
    for it in range(int(max_iter)):
        CN = (Pa / sigma_vc) ** m
        if CN > 1.7:
            CN = 1.7
        qc1N = CN * qCN
        dq = delta_qc1N_formula(qc1N, FC)
        qc1Ncs_new = qc1N + dq
        if qc1Ncs_new < 1e-6:
            qc1Ncs_new = 1e-6
        m_new = compute_m_from_qc1Ncs(qc1Ncs_new)
        # clamp m to valid range for formula
        if m_new < 0.246:
            m_new = 0.246
        if m_new > 0.782:
            m_new = 0.782
        if last_m is not None and abs(m_new - last_m) < tol:
            m = m_new
            qc1Ncs = qc1Ncs_new
            converged = True
            iter_count = it + 1
            break
        last_m = m_new
        m = m_new
        qc1Ncs = qc1Ncs_new
    else:
        iter_count = max_iter

    # show iteration results
    if converged:
        st.success(f"Converged in {iter_count} iterations")
    else:
        st.warning(f"Did not converge within {iter_count} iterations; last m={m:.6f}")

    st.write(f"m = {m:.6f}")
    st.write(f"qc1Ncs = {qc1Ncs:.4f} (dimensionless normalized value)")

    # --- compute CRR_base from qc1Ncs ---
    qc = qc1Ncs
    CRR_base = np.exp(qc / 113.0 + (qc / 1000.0) ** 2 - (qc / 140.0) ** 3 + (qc / 137.0) ** 4 - 2.8)
    st.write(f"CRR (base, Mw=7.5, σ'v0=1 atm) = {CRR_base:.6e}")

    # --- compute MSF_max from qc1Ncs (CPT) unless user provided ---
    # expression: 1.09*(qc1Ncs/180)^3 <= 2.2
    msf_max_cpt = 1.09 * (qc1Ncs / 180.0) ** 3
    msf_max_cpt = min(msf_max_cpt, 2.2)
    st.write(f"MSF_max (from CPT expression) = {msf_max_cpt:.6f} (capped at 2.2)")

    if provide_MSF_manual and MSF_max_user is not None:
        MSF_max = MSF_max_user
        st.info(f"Using user-provided MSF_max = {MSF_max:.3f}")
    else:
        MSF_max = msf_max_cpt

    # --- MSF ---
    MSF = 1.0 + (MSF_max - 1.0) * (8.64 * np.exp(-0.25 * M) - 1.325)
    st.write(f"Magnitude scaling factor MSF = {MSF:.6f}")

    # --- C_sigma (use CPT expression) ---
    try:
        denom = (37.3 - 8.27 * (qc1Ncs)**0.264)
        if denom <= 0:
            C_sigma = 0.3
        else:
            C_sigma = 1.0 / (37.3 - 8.27 * (qc1Ncs)** 0.264)
            C_sigma = min(C_sigma, 0.3)
    except Exception:
        C_sigma = 0.3

    st.write(f"C_sigma (CPT formula) = {C_sigma:.6f}")

    # --- K_sigma ---
    if sigma_v0 <= 0:
        K_sigma = 1.0
    else:
        K_sigma = 1.0 - C_sigma * np.log(sigma_vc / Pa)
        K_sigma = min(K_sigma, 1.1)

    st.write(f"K_sigma = {K_sigma:.6f}")

    # --- final CRR ---
    CRR = CRR_base * MSF * K_sigma
    st.markdown("---")
    st.subheader("Final result")
    st.metric("Cyclic Resistance Ratio (CRR)", f"{CRR:.6e}")

    st.markdown("---")
