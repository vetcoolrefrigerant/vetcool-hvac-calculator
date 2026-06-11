import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os

st.set_page_config(page_title="VetCool HVAC Calculator", page_icon="vetcool_logo.png", layout="centered")

# PWA Support
st.markdown("""
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#E30613">
""", unsafe_allow_html=True)

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
st.markdown("**Professional Multi-Room Heating & Cooling Estimator**")
st.caption("Installable App • Manual J Style")

# Session State for Multi-Room
if 'rooms' not in st.session_state:
    st.session_state.rooms = []

tab1, tab2 = st.tabs(["🧮 Multi-Room Calculation", "📘 How to Use"])

with tab1:
    st.subheader("Add a Room")
    with st.form("add_room"):
        room_name = st.text_input("Room Name", value=f"Room {len(st.session_state.rooms)+1}")
        col1, col2 = st.columns(2)
        with col1:
            area_walls = st.number_input("Wall Area (sq ft)", value=800)
            area_windows = st.number_input("Window Area (sq ft)", value=150)
            area_roof = st.number_input("Roof Area (sq ft)", value=600)
        with col2:
            u_walls = st.selectbox("Wall U-value", [0.04, 0.06, 0.08, 0.12, 0.25], index=1)
            u_windows = st.selectbox("Window U-value", [0.25, 0.35, 0.50], index=1)
            u_roof = st.selectbox("Roof U-value", [0.04, 0.06, 0.08], index=0)

        volume = st.number_input("Room Volume (cubic ft)", value=4800)
        ach = st.selectbox("Air Changes per Hour (ACH)", [0.3, 0.5, 0.8, 1.0, 1.5], index=1)
        occupants = st.number_input("Occupants in this room", value=2)

        if st.form_submit_button("Add Room", type="primary"):
            st.session_state.rooms.append({
                'name': room_name,
                'area_walls': area_walls, 'u_walls': u_walls,
                'area_windows': area_windows, 'u_windows': u_windows,
                'area_roof': area_roof, 'u_roof': u_roof,
                'volume': volume, 'ach': ach, 'occupants': occupants
            })
            st.success(f"✅ Added: {room_name}")

    # Display Rooms & Grand Total
    if st.session_state.rooms:
        st.subheader("Added Rooms")
        total_btu = 0
        total_cfm = 0

        for i, room in enumerate(st.session_state.rooms):
            st.write(f"**{room['name']}**")
            data = {**room, 't_indoor': 75, 't_outdoor': 95, 'mode': 'Cooling Load'}
            result = calculate_cooling_load(data)
            st.write(f"   → {result['total_btu_hr']} BTU/hr ({result['tons']} Tons) | {result['cfm']} CFM")
            total_btu += result['total_btu_hr']
            total_cfm += result['cfm']

        st.success(f"**GRAND TOTAL:** {total_btu} BTU/hr ({round(total_btu/12000, 2)} Tons) | Airflow: {total_cfm} CFM")

        if st.button("Clear All Rooms"):
            st.session_state.rooms = []
            st.rerun()

# ========================= FUNCTIONS =========================
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
    delta_t = data.get('t_outdoor', 95) - data.get('t_indoor', 75)
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
    try:
        pdf.image("vetcool_logo.png", x=140, y=8, w=60)
    except:
        pass
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "VetCool HVAC LOAD REPORT", ln=True, align="C")
    pdf.ln(15)

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
            pdf.cell(0, 6, f"{nice_key}: {value}", ln=True)

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

with tab2:
    st.header("📘 How to Use")
    st.write("Add each room one by one. Grand total is calculated automatically.")
    st.subheader("Contact VetCool")
    st.markdown("🌐 **[vetcoolrefrigerant.com](https://vetcoolrefrigerant.com)**")

st.caption("© VetCool Refrigerant")