import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os

# --- Dark Mode + VetCool Branding ---
st.set_page_config(page_title="VetCool HVAC Calculator", page_icon="🔧", layout="centered")

st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #E30613;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FF1A1A;
    }
    h1, h2, h3, h4 {
        color: #FFFFFF;
    }
    .stSelectbox, .stNumberInput, .stRadio {
        color: white;
    }
    .css-1d391kg {  /* Header area */
        background-color: #1A1C23;
    }
</style>
""", unsafe_allow_html=True)

# --- Logo ---
try:
    st.image("vetcool_logo.png", width=280)
except:
    st.warning("⚠️ Logo file not found. Place 'vetcool_logo.png' in this folder.")

st.title("VetCool HVAC Load Calculator")
st.markdown("**Professional Heating & Cooling Load Estimator**")

# Quick Presets
st.subheader("Quick Presets")
preset = st.selectbox("Choose a common scenario", 
    ["Custom Input", "Small House (1200 sq ft)", "Medium House (2000 sq ft)", "Large House (3000 sq ft)"])

if preset != "Custom Input":
    if preset == "Small House (1200 sq ft)":
        defaults = {"walls": 800, "windows": 150, "roof": 1200, "volume": 9600, "occupants": 3}
    elif preset == "Medium House (2000 sq ft)":
        defaults = {"walls": 1400, "windows": 250, "roof": 2000, "volume": 16000, "occupants": 5}
    else:
        defaults = {"walls": 2000, "windows": 400, "roof": 3000, "volume": 24000, "occupants": 7}
else:
    defaults = {"walls": 1200, "windows": 200, "roof": 1500, "volume": 9000, "occupants": 4}

tab1, tab2 = st.tabs(["🧮 New Calculation", "📘 How to Use"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        mode = st.radio("Calculation Type", ["Heating Load", "Cooling Load"], horizontal=True)

    with col2:
        t_indoor = st.number_input("Indoor Temperature (°F)", value=75)
        t_outdoor = st.number_input("Outdoor Temperature (°F)", 
                                  value=95 if mode == "Cooling Load" else 20)

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
            't_indoor': t_indoor, 't_outdoor': t_outdoor,
            'area_walls': area_walls, 'u_walls': u_walls,
            'area_windows': area_windows, 'u_windows': u_windows,
            'area_roof': area_roof, 'u_roof': u_roof,
            'volume': volume, 'ach': ach, 'occupants': occupants,
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

        try:
            pdf_file = generate_pdf_report(data, result, mode)
            with open(pdf_file, "rb") as f:
                st.download_button("📥 Download PDF Report", f, file_name=pdf_file, mime="application/pdf")
            os.remove(pdf_file)
        except:
            st.warning("Could not generate PDF")

# Calculation Functions
def calculate_heating_load(data):
    q_walls = data['u_walls'] * data['area_walls'] * (data['t_indoor'] - data['t_outdoor'])
    q_windows = data['u_windows'] * data['area_windows'] * (data['t_indoor'] - data['t_outdoor'])
    q_roof = data['u_roof'] * data['area_roof'] * (data['t_indoor'] - data['t_outdoor'])
    q_conduction = q_walls + q_windows + q_roof
    cfm = (data['volume'] * data['ach']) / 60
    q_infil = 1.08 * cfm * (data['t_indoor'] - data['t_outdoor'])
    total = q_conduction + q_infil
    return {'total_btu_hr': round(total), 'cfm': round(cfm, 1)}

def calculate_cooling_load(data):
    q_walls = data['u_walls'] * data['area_walls'] * 25
    q_roof = data['u_roof'] * data['area_roof'] * 40
    q_windows = data['u_windows'] * data['area_windows'] * 12
    q_solar = data['area_windows'] * 140
    cfm = (data['volume'] * data['ach']) / 60
    delta_t = data['t_outdoor'] - data['t_indoor']
    q_inf_s = 1.08 * cfm * delta_t
    q_inf_l = 0.68 * cfm * 30
    q_people = data['occupants'] * 380
    sensible = q_walls + q_roof + q_windows + q_solar + q_inf_s + q_people
    total = sensible + q_inf_l
    return {
        'total_btu_hr': round(total),
        'tons': round(total / 12000, 2),
        'cfm': round(sensible / (1.08 * 20))
    }

def generate_pdf_report(data, result, mode):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "VetCool HVAC LOAD REPORT", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(0, 8, f"Type: {mode}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "INPUT PARAMETERS", ln=True)
    pdf.set_font("Arial", "", 11)
    for key, value in data.items():
        if key not in ["mode"]:
            nice_key = key.replace('_', ' ').title()
            pdf.cell(0, 6, f"• {nice_key}: {value}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "RESULTS", ln=True)
    pdf.set_font("Arial", "", 11)

    if "Heating" in mode:
        pdf.cell(0, 8, f"Total Heating Load: {result.get('total_btu_hr')} BTU/hr", ln=True)
        pdf.cell(0, 8, f"Airflow: {result.get('cfm')} CFM", ln=True)
    else:
        pdf.cell(0, 8, f"Total Cooling Load: {result.get('total_btu_hr')} BTU/hr", ln=True)
        pdf.cell(0, 8, f"Tons: {result.get('tons')} Tons", ln=True)
        pdf.cell(0, 8, f"Airflow: {result.get('cfm')} CFM", ln=True)

    pdf.ln(20)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 8, "Generated by VetCool HVAC Calculator", ln=True, align="C")

    filename = f"vetcool_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(filename)
    return filename

# How to Use
with tab2:
    st.header("📘 How to Use This Calculator")
    st.subheader("1. Basic Instructions")
    st.write("Choose Heating or Cooling → Enter temperatures → Fill building details → Click Calculate.")
    st.subheader("2. Tips")
    st.write("Use realistic outdoor temps for your area. Measure rooms separately for best accuracy.")
    st.subheader("3. About VetCool")
    st.write("Provided by VetCool Refrigerant to support the HVAC community.")

st.markdown("---")
st.caption("© VetCool Refrigerant - Professional HVAC Tools")