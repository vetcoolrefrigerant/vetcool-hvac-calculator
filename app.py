import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os

st.set_page_config(page_title="VetCool HVAC Calculator", page_icon="🔧", layout="centered")

# Dark Theme
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .stButton>button { background-color: #E30613; color: white; font-weight: bold; }
    .stButton>button:hover { background-color: #FF1A1A; }
    h1, h2, h3 { color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)

# Logo
try:
    st.image("vetcool_logo.png", width=280)
except:
    pass

st.title("VetCool HVAC Load Calculator")
st.markdown("**Professional Heating & Cooling Load Estimator**")
st.caption("Manual J Style • Duct Sizing")

# Quick Presets
st.subheader("Quick Presets")
preset = st.selectbox("Choose a common scenario", [
    "Custom Input", "Small House (1200 sq ft)", "Medium House (2000 sq ft)", 
    "Large House (3000 sq ft)", "Small Office", "Restaurant", "Warehouse"
])

if preset == "Small House (1200 sq ft)":
    defaults = {"walls": 800, "windows": 150, "roof": 1200, "volume": 9600, "occupants": 3}
elif preset == "Medium House (2000 sq ft)":
    defaults = {"walls": 1400, "windows": 250, "roof": 2000, "volume": 16000, "occupants": 5}
elif preset == "Large House (3000 sq ft)":
    defaults = {"walls": 2000, "windows": 400, "roof": 3000, "volume": 24000, "occupants": 7}
elif preset == "Small Office":
    defaults = {"walls": 1800, "windows": 300, "roof": 1800, "volume": 14400, "occupants": 12}
elif preset == "Restaurant":
    defaults = {"walls": 1500, "windows": 250, "roof": 1500, "volume": 12000, "occupants": 25}
elif preset == "Warehouse":
    defaults = {"walls": 4000, "windows": 100, "roof": 5000, "volume": 80000, "occupants": 8}
else:
    defaults = {"walls": 1200, "windows": 200, "roof": 1500, "volume": 9000, "occupants": 4}

tab1, tab2 = st.tabs(["🧮 New Calculation", "📘 How to Use"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        mode = st.radio("Calculation Type", ["Heating Load", "Cooling Load"], horizontal=True)

    with col2:
        t_indoor = st.number_input("Indoor Temperature (°F)", value=75)
        t_outdoor = st.number_input("Outdoor Temperature (°F)", value=95 if mode == "Cooling Load" else 20)

    st.subheader("Building Details")
    col3, col4 = st.columns(2)
    with col3:
        area_walls = st.number_input("Wall Area (sq ft)", value=defaults["walls"])
        area_windows = st.number_input("Window Area (sq ft)", value=defaults["windows"])
        area_roof = st.number_input("Roof Area (sq ft)", value=defaults["roof"])
    with col4:
        u_walls = st.selectbox("Wall U-value", [0.04, 0.06, 0.08, 0.12, 0.25], index=1)
        u_windows = st.selectbox("Window U-value", [0.25, 0.35, 0.50], index=1)
        u_roof = st.selectbox("Roof U-value", [0.04, 0.06, 0.08], index=0)

    volume = st.number_input("Room Volume (cubic ft)", value=defaults["volume"])
    ach = st.selectbox("Air Changes per Hour (ACH)", [0.3, 0.5, 0.8, 1.0, 1.5], index=1)
    occupants = st.number_input("Number of Occupants", value=defaults["occupants"])

    if st.button("Calculate Load", type="primary", use_container_width=True):
        data = {
            't_indoor': t_indoor,
            't_outdoor': t_outdoor,
            'area_walls': area_walls,
            'u_walls': u_walls,
            'area_windows': area_windows,
            'u_windows': u_windows,
            'area_roof': area_roof,
            'u_roof': u_roof,
            'volume': volume,
            'ach': ach,
            'occupants': occupants,
            'mode': mode
        }

        if mode == "Heating Load":
            result = calculate_heating_load(data)
            st.success(f"**Total Heating Load: {result['total_btu_hr']} BTU/hr**")
            st.info(f"**Recommended Airflow: {result['cfm']} CFM**")
        else:
            result = calculate_cooling_load(data)
            st.success(f"**Total Cooling Load: {result['total_btu_hr']} BTU/hr** ({result['tons']} Tons)")
            st.info(f"**Supply Airflow: {result['cfm']} CFM**")

        # Duct Sizing
        cfm = result.get('cfm', 0)
        duct_text = "8-10 inch round" if cfm < 400 else "12-14 inch round" if cfm < 800 else "16+ inch or rectangular"
        st.info(f"**Suggested Main Duct Size:** {duct_text}")

        # PDF
        try:
            pdf_file = generate_pdf_report(data, result, mode)