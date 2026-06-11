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

try:
    st.image("vetcool_logo.png", width=280)
except:
    pass

st.title("VetCool HVAC Load Calculator")
st.markdown("**Professional Multi-Room Heating & Cooling Load Estimator**")

# Initialize session state for multi-room
if 'rooms' not in st.session_state:
    st.session_state.rooms = []

tab1, tab2 = st.tabs(["🧮 Multi-Room Calculation", "📘 How to Use"])

with tab1:
    st.subheader("Add Rooms")

    with st.form("room_form"):
        room_name = st.text_input("Room Name (e.g. Living Room)", value=f"Room {len(st.session_state.rooms) + 1}")
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

        submitted = st.form_submit_button("Add Room", type="primary")

        if submitted:
            st.session_state.rooms.append({
                'name': room_name,
                'area_walls': area_walls,
                'u_walls': u_walls,
                'area_windows': area_windows,
                'u_windows': u_windows,
                'area_roof': area_roof,
                'u_roof': u_roof,
                'volume': volume,
                'ach': ach,
                'occupants': occupants
            })
            st.success(f"Room '{room_name}' added!")

    # Show added rooms
    if st.session_state.rooms:
        st.subheader("Added Rooms")
        total_btu = 0
        total_cfm = 0

        for i, room in enumerate(st.session_state.rooms):
            st.write(f"**{room['name']}**")
            data = {**room, 't_indoor': 75, 't_outdoor': 95, 'mode': 'Cooling Load'}
            result = calculate_cooling_load(data)  # Default to cooling for demo
            st.write(f"   Cooling Load: {result['total_btu_hr']} BTU/hr | {result['tons']} Tons")
            total_btu += result['total_btu_hr']
            total_cfm += result['cfm']

        st.success(f"**GRAND TOTAL:** {total_btu} BTU/hr ({round(total_btu/12000, 2)} Tons) | Airflow: {total_cfm} CFM")

        if st.button("Clear All Rooms"):
            st.session_state.rooms = []
            st.rerun()

# Calculation Functions
def calculate_heating_load(data):
    # ... (same as previous)
    q_walls = data['u_walls'] * data['area_walls'] * (data.get('t_indoor', 75) - data.get('t_outdoor', 20))
    # simplified for brevity
    return {'total_btu_hr': 0, 'cfm': 0}  # Replace with real logic later

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

def generate_pdf_report(...):  # keep your existing function
    pass  # I'll expand if needed

with tab2:
    st.header("Multi-Room Instructions")
    st.write("Add each room one by one. The app will sum the totals automatically.")

st.caption("© VetCool Refrigerant | vetcoolrefrigerant.com")