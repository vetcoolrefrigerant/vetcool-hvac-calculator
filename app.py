import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os

# ==============================================================================
# 1. REGIONAL DESIGN DATA & CONSTANTS (ASHRAE / ACCA MANUAL J ALIGNED)
# ==============================================================================
# Design temperatures: Heating (99% dry bulb), Cooling (1% dry bulb), and Summer grains of moisture
REGIONAL_DATA = {
    "Miami, FL": {"heat_outdoor": 48, "cool_outdoor": 91, "moisture_grains": 145, "cltd_wall": 28, "cltd_roof": 46},
    "Phoenix, AZ": {"heat_outdoor": 38, "cool_outdoor": 108, "moisture_grains": 60, "cltd_wall": 35, "cltd_roof": 52},
    "Chicago, IL": {"heat_outdoor": -1, "cool_outdoor": 91, "moisture_grains": 100, "cltd_wall": 22, "cltd_roof": 38},
    "New York, NY": {"heat_outdoor": 15, "cool_outdoor": 89, "moisture_grains": 105, "cltd_wall": 21, "cltd_roof": 38},
    "Houston, TX": {"heat_outdoor": 32, "cool_outdoor": 95, "moisture_grains": 130, "cltd_wall": 26, "cltd_roof": 44},
    "Denver, CO": {"heat_outdoor": 2, "cool_outdoor": 92, "moisture_grains": 55, "cltd_wall": 25, "cltd_roof": 42},
    "Custom (Manual Override)": {"heat_outdoor": 20, "cool_outdoor": 95, "moisture_grains": 100, "cltd_wall": 25, "cltd_roof": 40}
}

# Equivalent duct sizes mapping based on CFM ranges (at ~0.1 friction rate)
def get_duct_recommendation(cfm):
    if cfm <= 150:
        return "6\" Round (or 6x6 Rectangular)"
    elif cfm <= 250:
        return "7\" Round (or 8x6 Rectangular)"
    elif cfm <= 400:
        return "8\" Round (or 10x6 Rectangular)"
    elif cfm <= 700:
        return "10\" Round (or 12x8 Rectangular)"
    elif cfm <= 1000:
        return "12\" Round (or 16x8 Rectangular)"
    elif cfm <= 1400:
        return "14\" Round (or 20x8 Rectangular)"
    else:
        return "16\"+ Round (or 24x10+ Trunk Line - Multiple Runs Required)"

# ==============================================================================
# 2. CORE CALCULATION ENGINES
# ==============================================================================
def calculate_heating_load(data):
    # Conduction: Q = U * A * Delta T
    delta_t = data['t_indoor'] - data['t_outdoor']
    q_walls = data['u_walls'] * data['area_walls'] * delta_t
    q_windows = data['u_windows'] * data['area_windows'] * delta_t
    q_roof = data['u_roof'] * data['area_roof'] * delta_t
    q_conduction = q_walls + q_windows + q_roof
    
    # Infiltration (Sensible Only for Heating)
    cfm_infil = (data['volume'] * data['ach']) / 60
    q_infil = 1.08 * cfm_infil * delta_t
    
    total = (q_conduction + q_infil) * data['safety_factor']
    return {'total_btu_hr': round(total), 'cfm': round(cfm_infil, 1)}

def calculate_cooling_load(data):
    # Conduction using CLTD (Cooling Load Temperature Difference) to account for solar delay
    q_walls = data['u_walls'] * data['area_walls'] * data['cltd_wall']
    q_roof = data['u_roof'] * data['area_roof'] * data['cltd_roof']
    q_windows = data['u_windows'] * data['area_windows'] * (data['t_outdoor'] - data['t_indoor'])
    
    # Solar Radiation through glass (Area * Solar Heat Gain Coefficient * Max Solar Heat Gain Factor)
    # 200 BTU/hr/sqft is a standard peak summer design average for mixed orientations
    q_solar = data['area_windows'] * data['shgc'] * 200 
    
    # Infiltration / Ventilation Airflow
    cfm_infil = (data['volume'] * data['ach']) / 60
    
    # Sensible Infiltration
    delta_t = data['t_outdoor'] - data['t_indoor']
    q_inf_sensible = 1.08 * cfm_infil * delta_t
    
    # Latent Infiltration (Moisture Load)
    # 0.68 * CFM * Delta Grains (Assuming indoor target is roughly 65 grains / 50% RH at 75°F)
    delta_grains = max(0, data['moisture_grains'] - 65)
    q_inf_latent = 0.68 * cfm_infil * delta_grains
    
    # Internal Loads (People: 250 Sensible + 200 Latent = 450 BTU/hr standard)
    q_people = data['occupants'] * 450
    
    total_sensible = q_walls + q_roof + q_windows + q_solar + q_inf_sensible + (data['occupants'] * 250)
    total_load = (total_sensible + q_inf_latent + (data['occupants'] * 200)) * data['safety_factor']
    
    # Required CFM based on standard 20°F evaporator temperature split
    required_cfm = total_sensible / (1.08 * 20)
    
    return {
        'total_btu_hr': round(total_load),
        'tons': round(total_load / 12000, 2),
        'cfm': round(required_cfm)
    }

# ==============================================================================
# 3. REPORT GENERATION
# ==============================================================================
def generate_pdf_report(data, result, mode):
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.image("vetcool_logo.png", x=140, y=8, w=60)
    except:
        pass

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "VetCool HVAC ESTIMATE REPORT", ln=True, align="C")
    pdf.ln(15)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(0, 8, f"Calculation Scope: {mode}", ln=True)
    pdf.cell(0, 8, f"Design Target Location: {data.get('location')}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "INPUT DESIGN PARAMETERS", ln=True)
    pdf.set_font("Arial", "", 11)
    
    skip_keys = ["mode", "location", "cltd_wall", "cltd_roof", "moisture_grains"]
    for key, value in data.items():
        if key not in skip_keys:
            nice_key = key.replace('_', ' ').title()
            if "Factor" in nice_key:
                value = f"{round((value - 1) * 100)}% Cushion Included"
            pdf.cell(0, 6, f" - {nice_key}: {value}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "ESTIMATED LOAD RESULTS", ln=True)
    pdf.set_font("Arial", "", 11)

    if "Heating" in mode:
        pdf.cell(0, 8, f"Total Heating Load: {result.get('total_btu_hr'):,} BTU/hr", ln=True)
        pdf.cell(0, 8, f"Required Airflow: {result.get('cfm')} CFM", ln=True)
    else:
        pdf.cell(0, 8, f"Total Cooling Load: {result.get('total_btu_hr'):,} BTU/hr", ln=True)
        pdf.cell(0, 8, f"Nominal Tonnage Needed: {result.get('tons')} Tons", ln=True)
        pdf.cell(0, 8, f"Required Supply Airflow: {result.get('cfm')} CFM", ln=True)

    pdf.cell(0, 8, f"Recommended Main Duct Size: {get_duct_recommendation(result.get('cfm'))}", ln=True)

    pdf.ln(20)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 5, "Disclaimer: This estimate is based on simplified block load calculation principles. "
                         "It is intended for quick field estimates and sales verification. Verify with full local code "
                         "requirements before equipment purchase.", align="C")

    filename = f"vetcool_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(filename)
    return filename

# ==============================================================================
# 4. STREAMLIT APPLICATION UI
# ==============================================================================
st.set_page_config(page_title="VetCool HVAC Loader", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .stButton>button { background-color: #E30613; color: white; font-weight: bold; border-radius: 6px; }
    .stButton>button:hover { background-color: #FF1A1A; border-color: #FF1A1A; }
    h1, h2, h3, label { color: #FFFFFF !important; }
    .metric-card { background-color: #1E232A; padding: 20px; border-radius: 10px; border-left: 5px solid #E30613; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

try:
    st.image("vetcool_logo.png", width=250)
except:
    pass

st.title("VetCool Field Load Calculator")
st.markdown("快速估算 / **Professional Estimation Sanity-Check Tool**")

# Global Settings & Presets Layout
with st.sidebar:
    st.header("⚙️ Global Settings")
    location = st.selectbox("Design Climate Location", list(REGIONAL_DATA.keys()))
    geo_defaults = REGIONAL_DATA[location]
    
    preset = st.selectbox("Property Presets", [
        "Custom Input", "Small House (1200 sq ft)", "Medium House (2000 sq ft)", 
        "Large House (3000 sq ft)", "Small Office", "Restaurant"
    ], index=2)
    
    safety_slider = st.slider("Safety Margin Cushion (%)", min_value=0, max_value=30, value=10, step=5)
    safety_factor = 1.0 + (safety_slider / 100)

# Preset Logic Overrides
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
else:
    defaults = {"walls": 1200, "windows": 200, "roof": 1500, "volume": 9000, "occupants": 4}

tab1, tab2 = st.tabs(["🧮 Compute System Loads", "📘 Application Methodology"])

with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        mode = st.radio("Calculation Path", ["Heating Load", "Cooling Load"], index=1)
        t_indoor = st.number_input("Target Indoor Temp (°F)", value=72 if mode == "Heating Load" else 75)
        
        # Override dynamic temperatures if manual location is chosen
        if location == "Custom (Manual Override)":
            t_outdoor = st.number_input("Design Outdoor Temp (°F)", value=95 if mode == "Cooling Load" else 20)
            moisture_grains = st.number_input("Outdoor Humidity Grains", value=100)
            cltd_wall, cltd_roof = 25, 40
        else:
            t_outdoor = geo_defaults["cool_outdoor"] if mode == "Cooling Load" else geo_defaults["heat_outdoor"]
            moisture_grains = geo_defaults["moisture_grains"]
            cltd_wall = geo_defaults["cltd_wall"]
            cltd_roof = geo_defaults["cltd_roof"]
            st.caption(f"Using standard local weather profiles: **{t_outdoor}°F DB**")

    with col2:
        st.subheader("Building Envelope Metrics")
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            area_walls = st.number_input("Net Wall Area (sq ft)", value=defaults["walls"])
            area_windows = st.number_input("Total Window Area (sq ft)", value=defaults["windows"])
            area_roof = st.number_input("Ceiling/Roof Area (sq ft)", value=defaults["roof"])
        with c_sub2:
            u_walls = st.selectbox("Wall Insulation (U-value)", [0.04, 0.06, 0.08, 0.12, 0.25], index=2, help="Lower is better insulation. 0.06 is standard insulated wall.")
            u_windows = st.selectbox("Window Glazing (U-value)", [0.28, 0.35, 0.48, 0.70], index=1, help="0.28=Triple Pane, 0.48=Double Pane Clear.")
            u_roof = st.selectbox("Roof Insulation (U-value)", [0.03, 0.05, 0.08, 0.15], index=1, help="0.03=R-38 ceiling, 0.05=R-21 ceiling.")

        st.subheader("Internal Variables & Infiltration")
        c_sub3, c_sub4 = st.columns(2)
        with c_sub3:
            volume = st.number_input("Conditioned Cubical Volume (cu ft)", value=defaults["volume"])
            occupants = st.number_input("Average Continuous Occupants", value=defaults["occupants"], step=1)
        with c_sub4:
            ach = st.selectbox("Envelope Air Tightness (ACH)", [0.2, 0.35, 0.5, 0.75, 1.2], index=2, help="Air Changes per Hour. 0.35 is tight modern construction; 0.75+ is leaky.")
            shgc = st.slider("Window Solar Coefficient (SHGC)", min_value=0.20, max_value=0.85, value=0.40, step=0.05, help="Solar Heat Gain Coefficient. Lower value blocks more radiant heat.")

    st.markdown("---")
    
    if st.button("Generate Load Profiles", type="primary", use_container_width=True):
        data = {
            'location': location, 't_indoor': t_indoor, 't_outdoor': t_outdoor,
            'moisture_grains': moisture_grains, 'cltd_wall': cltd_wall, 'cltd_roof': cltd_roof,
            'area_walls': area_walls, 'u_walls': u_walls,
            'area_windows': area_windows, 'u_windows': u_windows,
            'area_roof': area_roof, 'u_roof': u_roof,
            'volume': volume, 'ach': ach, 'occupants': occupants,
            'shgc': shgc, 'safety_factor': safety_factor, 'mode': mode
        }

        # Calculation routing
        if mode == "Heating Load":
            result = calculate_heating_load(data)
            st.markdown(f"""
            <div class="metric-card">
                <h3>🔥 Estimated Heating Capacity</h3>
                <h2>{result['total_btu_hr']:,} BTU/hr</h2>
                <p>Calculated Circulation Target: <b>{result['cfm']} CFM</b></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            result = calculate_cooling_load(data)
            st.markdown(f"""
            <div class="metric-card">
                <h3>❄️ Estimated Cooling Capacity</h3>
                <h2>{result['total_btu_hr']:,} BTU/hr (~{result['tons']} Nominal Tons)</h2>
                <p>Required Air Flow: <b>{result['cfm']} CFM</b></p>
            </div>
            """, unsafe_allow_html=True)

        duct_recommendation = get_duct_recommendation(result['cfm'])
        st.info(f"📐 **Suggested Trunk Line Profile:** {duct_recommendation}")

        # PDF Delivery Actions
        try:
            pdf_file = generate_pdf_report(data, result, mode)
            with open(pdf_file, "rb") as f:
                st.download_button("📥 Export Branded PDF Proposal", f, file_name=pdf_file, mime="application/pdf")
            os.remove(pdf_file)
        except Exception as e:
            st.error(f"Render System Fault: {str(e)}")

with tab2:
    st.header("📘 Operational Calculations & Assumptions")
    st.markdown("""
    This app functions as an advanced block-load model designed for rapid technical sales assistance. 
    Unlike simple linear calculators, it incorporates:
    
    * **CLTD (Cooling Load Temperature Difference):** Factoring in radiant energy absorption delays for walls and roof structures instead of simple temperature deltas.
    * **Latent Load Profiles:** Evaluating regional relative humidity differentials against standard inside conditions (~65 grains of absolute moisture) to calculate latent infiltration penalties.
    * **Glazing Variables:** Evaluating radiant solar vectors by applying variable *Solar Heat Gain Coefficients (SHGC)* directly against real-world exposure values.
    
    *Always verify manual design structures against a formal ACCA Manual J protocol for strict code compliance.*
    """)
    st.subheader("Maintained by VetCool")
    st.write("🌐 Website Link: [vetcoolrefrigerant.com](https://vetcoolrefrigerant.com)")