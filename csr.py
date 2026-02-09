def run():
    import streamlit as st
    import numpy as np
    import math
    import base64

    def show_pdf(path):
        with open(path, "rb") as f:
            pdf_bytes = f.read()
        b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        pdf_display = f"""
            <iframe src="data:application/pdf;base64,{b64_pdf}"
                    width="100%" height="600"
                    type="application/pdf">
            </iframe>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)




    print("""
    ========================================================
    CYCLIC STRESS RATIO (CSR) CALCULATION PROGRAM
    ========================================================

    This program computes the Cyclic Stress Ratio (CSR) at a
    specified depth using the simplified earthquake-induced
    liquefaction analysis method.

    -------------------------------
    WORKING OF THE PROGRAM
    -------------------------------
    1. The user defines an earthquake by providing:
       - Peak horizontal acceleration ratio (a_max / g)
       - Earthquake magnitude (M)

    2. The soil profile is defined using multiple layers:
       - Unit weight (γ) of each layer
       - Thickness (h) of each layer

       Total vertical overburden stress is computed as:
           σ_v0 = Σ (γ_i × h_i)

    3. Groundwater conditions are defined by:
       - Depth of water table from ground level
       - Liquefaction check depth (z)
       - Unit weight of water (γ_w)

       Pore water pressure at depth z is computed as:
           u_0 = γ_w × (z − water table depth)   (if z > WT)

    4. Effective vertical stress is computed as:
           σ'_v0 = σ_v0 − u_0

    5. Stress reduction coefficient (r_d) accounts for
       flexibility of the soil column and is computed as:
           r_d = exp(α_z + β_z × M)

       where:
           α_z = −1.012 − 1.126 sin(z/11.73 + 5.133)
           β_z =  0.106 + 0.118 sin(z/11.28 + 5.142)

    6. Finally, Cyclic Stress Ratio is calculated as:
           CSR = 0.65 × (a_max/g) × (σ_v0 / σ'_v0) × r_d

    -------------------------------
    IMPORTANT NOTES
    -------------------------------
    • All stresses are computed in kPa (kN/m²).
    • Depths are measured from ground level.
    • The liquefaction check point is assumed to be
      below the water table unless otherwise specified.
    • This program computes CSR at ONE depth point.

    ========================================================
    """)

    # -------------------------------
    # Stress reduction factor
    # -------------------------------
    def compute_rd(z, M):
        alpha_z = -1.012 - 1.126 * math.sin(z / 11.73 + 5.133)
        beta_z  =  0.106 + 0.118 * math.sin(z / 11.28 + 5.142)
        rd = math.exp(alpha_z + beta_z * M)
        return rd


    # -------------------------------
    # UI CONFIG
    # -------------------------------
    st.set_page_config(
        page_title="CSR Calculator",
        layout="wide"
    )

    st.title("Cyclic Stress Ratio (CSR) Calculator")
    st.markdown("**Simplified liquefaction analysis using IS 1893 Part 1**")

    # -------------------------------
    # SIDEBAR INPUTS
    # -------------------------------
    st.sidebar.header("Earthquake Input")

    amax_g = st.sidebar.number_input(
        "Peak acceleration ratio (a_max / g)",
        min_value=0.01, value=0.333, step=0.01
    )

    M = st.sidebar.number_input(
        "Earthquake Magnitude (M)",
        min_value=5.0, max_value=9.5, value=7.5, step=0.1
    )

    st.sidebar.header("Soil Profile")

    n_layers = st.sidebar.number_input(
        "Number of soil layers",
        min_value=1, max_value=10, value=2, step=1
    )

    st.sidebar.header("📚 Help & References")

    with st.sidebar.expander("CSR & Code Logic"):
        show_pdf("EQ_Code_Refs/CSR.pdf")
        
    with st.sidebar.expander("Peak Acceleration Ratio Values"):
        st.image("EQ_Code_Refs/SA_g.png")
    st.sidebar.markdown(
        "[Prathamesh Varma](https://prathameshvarma.wordpress.com/)"
    )


    # -------------------------------
    # Soil table
    # -------------------------------
    st.subheader("Soil Layer Properties")

    soil_data = np.ones((n_layers, 2))
    soil_df = st.data_editor(
        soil_data,
        column_config={
            1: "Unit weight γ (kN/m³)",
            2: "Thickness h (m)"
        },
        num_rows="fixed"
    )

    gamma = soil_df[:, 0]
    thickness = soil_df[:, 1]

    # -------------------------------
    # Groundwater input
    # -------------------------------
    st.subheader("Groundwater & Depth Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        z = st.number_input(
            "Liquefaction check depth z (m)",
            min_value=0.1, value=float(np.sum(thickness))
        )

    with col2:
        wt_depth = st.number_input(
            "Water table depth (m)",
            min_value=0.0, value=3.0
        )

    with col3:
        gamma_w = st.number_input(
            "Unit weight of water γ_w (kN/m³)",
            min_value=9.5, value=9.81
        )

    # -------------------------------
    # COMPUTE BUTTON
    # -------------------------------
    if st.button("▶ Compute CSR"):

        # 1. Total vertical stress
        sigma_vo = np.sum(gamma * thickness)

        # 2. Pore pressure
        if z <= wt_depth:
            u0 = 0.0
        else:
            u0 = gamma_w * (z - wt_depth)

        # 3. Effective stress
        sigma_vo_eff = sigma_vo - u0

        if sigma_vo_eff <= 0:
            st.error("Effective vertical stress ≤ 0. Check inputs.")
            st.stop()

        # 4. Stress reduction factor
        rd = compute_rd(z, M)

        # 5. CSR
        CSR = 0.65 * amax_g * (sigma_vo / sigma_vo_eff) * rd

        # -------------------------------
        # OUTPUT
        # -------------------------------
        st.subheader("📊 Results")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("σᵥ₀ (Total Stress)", f"{sigma_vo:.3f} kPa")
            st.metric("u₀ (Pore Pressure)", f"{u0:.3f} kPa")
            st.metric("σ′ᵥ₀ (Effective Stress)", f"{sigma_vo_eff:.3f} kPa")

        with col2:
            st.metric("Stress Reduction Factor rᵈ", f"{rd:.4f}")
            st.metric("Cyclic Stress Ratio (CSR)", f"{CSR:.4f}")

        st.success("CSR calculation completed successfully.")
