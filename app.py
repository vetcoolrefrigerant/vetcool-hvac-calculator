import os
import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import requests
from supabase import create_client, Client

# ==============================================================================
# 0. SPEED OPTIMIZATION RESOURCE CACHING LAYER
# ==============================================================================
# Memory-caches static regional lookup profiles so they load instantly without rebuilds
@st.cache_data
def load_static_environmental_profiles():
    lang_dict = {
        "English": {
            "title": "Vetcool FieldFlow",
            "subtitle": "Professional Mobile Thermal Load & Airflow Calculator",
            "sidebar_settings": "Global Settings",
            "history_header": "Your Cloud Projects",
            "proj_name_lbl": "Project / Client Reference Name",
            "climate_loc": "Design Climate Location",
            "presets": "Property Presets",
            "safety_margin": "Safety Margin Cushion (%)",
            "calc_path": "Calculation Path",
            "heat_load": "Heating Load",
            "cool_load": "Cooling Load",
            "target_indoor": "Target Indoor Temp (F)",
            "design_outdoor": "Design Outdoor Temp (F)",
            "humidity_grains": "Outdoor Humidity Grains",
            "weather_profile_msg": "Using standard local weather profiles",
            "building_metrics": "Building Envelope Metrics",
            "net_wall": "Net Wall Area (sq ft)",
            "tot_window": "Total Window Area (sq ft)",
            "roof_area": "Ceiling/Roof Area (sq ft)",
            "wall_ins": "Wall Insulation (U-value)",
            "window_glaze": "Window Glazing (U-value)",
            "roof_ins": "Roof Insulation (U-value)",
            "wall_ins_help": "Lower is better insulation. 0.06 is standard insulated wall.",
            "window_glaze_help": "0.28=Triple Pane, 0.48=Double Pane Clear.",
            "roof_ins_help": "0.03=R-38 ceiling, 0.05=R-21 ceiling.",
            "internal_vars": "Internal Variables & Infiltration",
            "room_vol": "Conditioned Cubical Volume (cu ft)",
            "occupants": "Average Continuous Occupants",
            "tightness": "Envelope Air Tightness (ACH)",
            "tightness_help": "Air Changes per Hour. 0.35 is tight modern construction.",
            "shgc_lbl": "Window Solar Coefficient (SHGC)",
            "shgc_help": "Solar Heat Gain Coefficient.",
            "btn_calc": "Generate & Save Load Profiles",
            "heat_capacity": "Estimated Heating Capacity",
            "cool_capacity": "Estimated Cooling Capacity",
            "circ_target": "Calculated Circulation Target",
            "req_airflow": "Required Air Flow",
            "nominal_tons": "Nominal Tons",
            "suggested_duct": "Suggested Trunk Line Profile",
            "btn_pdf": "Export Branded PDF Proposal",
            "pdf_fault": "Render System Fault",
            "tab_compute": "Compute System Loads",
            "tab_method": "Application Methodology",
            "method_title": "Operational Calculations & Assumptions",
            "method_body": "Advanced thermal load profile processing framework.",
            "disclaimer": "Disclaimer: Quick field estimate sales framework.",
            "pdf_title": "VETCOOL FIELDFLOW ESTIMATE REPORT",
            "pdf_scope": "Calculation Scope",
            "pdf_target": "Design Target Location",
            "pdf_inputs": "INPUT DESIGN PARAMETERS",
            "pdf_results": "ESTIMATED LOAD RESULTS",
            "pdf_duct": "Suggested Trunk Line Profile",
            "presets_dict": {"Custom Input": "Custom Input", "Small House (1200 sq ft)": "Small House (1200 sq ft)", "Medium House (2000 sq ft)": "Medium House (2000 sq ft)", "Large House (3000 sq ft)": "Large House (3000 sq ft)", "Small Office": "Small Office", "Restaurant": "Restaurant"}
        },
        "Spanish": {
            "title": "Vetcool FieldFlow",
            "subtitle": "Calculadora Movil Profesional de Carga Termica y Flujo de Aire",
            "sidebar_settings": "Configuracion Global",
            "history_header": "Tus Proyectos en la Nube",
            "proj_name_lbl": "Nombre del Proyecto / Cliente",
            "climate_loc": "Ubicacion del Clima de Diseno",
            "presets": "Preajustes de la Propiedad",
            "safety_margin": "Margen de Seguridad (%)",
            "calc_path": "Tipo de Calculo",
            "heat_load": "Carga de Calefaccion",
            "cool_load": "Carga de Enfriamiento",
            "target_indoor": "Temp. Interior Objetivo (F)",
            "design_outdoor": "Temp. Exterior de Diseno (F)",
            "humidity_grains": "Granos de Humedad Exterior",
            "weather_profile_msg": "Usando perfiles climaticos locales estandar",
            "building_metrics": "Metricas del Envolvente del Edificio",
            "net_wall": "Area Neta de Pared (sq ft)",
            "tot_window": "Area Total de Ventanas (sq ft)",
            "roof_area": "Area de Techo (sq ft)",
            "wall_ins": "Aislamiento de Pared (Valor-U)",
            "window_glaze": "Acristalamiento de Ventana (Valor-U)",
            "roof_ins": "Aislamiento de Techo (Valor-U)",
            "wall_ins_help": "Menor valor significa mejor aislamiento.",
            "window_glaze_help": "Especificaciones del vidrio.",
            "roof_ins_help": "Especificaciones del techo.",
            "internal_vars": "Variables Internas e Infiltracion",
            "room_vol": "Volumen Cubico Acondicionado (cu ft)",
            "occupants": "Promedio de Ocupantes Continuos",
            "tightness": "Hermeticidad del Envolvente (ACH)",
            "tightness_help": "Cambios de aire por hora.",
            "shgc_lbl": "Coeficiente Solar de Ventana (SHGC)",
            "shgc_help": "Ganancia de calor solar.",
            "btn_calc": "Generar y Guardar Perfiles de Carga",
            "heat_capacity": "Capacidad de Calefaccion Estimada",
            "cool_capacity": "Capacidad de Enfriamiento Estimada",
            "circ_target": "Objetivo de Circulacion Calculado",
            "req_airflow": "Flujo de Aire Requerido",
            "nominal_tons": "Toneladas Nominales",
            "suggested_duct": "Perfil Sugerido de la Linea Principal",
            "btn_pdf": "Exportar Propuesta en PDF",
            "pdf_fault": "Fallo en el Sistema de Renderizado",
            "tab_compute": "Calcular Cargas del Sistema",
            "tab_method": "Metodologia de Aplicacion",
            "method_title": "Calculos Operacionales y Supuestos",
            "method_body": "Estructura de procesamiento de perfiles de carga termica avanzada.",
            "disclaimer": "Descargo de responsabilidad: Estimacion de campo simplificada.",
            "pdf_title": "INFORME DE ESTIMACION VETCOOL FIELDFLOW",
            "pdf_scope": "Alcance del Calculo",
            "pdf_target": "Ubicacion de Diseno Objetivo",
            "pdf_inputs": "PARAMETROS DE DISENO DE ENTRADA",
            "pdf_results": "RESULTADOS DE CARGA ESTIMADA",
            "pdf_duct": "Perfil Sugerido de la Linea Principal",
            "presets_dict": {"Custom Input": "Entrada Personalizada", "Small House (1200 sq ft)": "Casa Pequena (1200 sq ft)", "Medium House (2000 sq ft)": "Casa Mediana (2000 sq ft)", "Large House (3000 sq ft)": "Casa Grande (3000 sq ft)", "Small Office": "Oficina Pequena", "Restaurant": "Restaurante"}
        }
    }
    
    regional_data = {
        "Miami, FL": {"heat_outdoor": 48, "cool_outdoor": 91, "moisture_grains": 145, "cltd_wall": 28, "cltd_roof": 46},
        "Phoenix, AZ": {"heat_outdoor": 38, "cool_outdoor": 108, "moisture_grains": 60, "cltd_wall": 35, "cltd_roof": 52},
        "Chicago, IL": {"heat_outdoor": -1, "cool_outdoor": 91, "moisture_grains": 100, "cltd_wall": 22, "cltd_roof": 38},
        "New York, NY": {"heat_outdoor": 15, "cool_outdoor": 89, "moisture_grains": 105, "cltd_wall": 21, "cltd_roof": 38},
        "Houston, TX": {"heat_outdoor": 32, "cool_outdoor": 95, "moisture_grains": 130, "cltd_wall": 26, "cltd_roof": 44},
        "Denver, CO": {"heat_outdoor": 2, "cool_outdoor": 92, "moisture_grains": 55, "cltd_wall": 25, "cltd_roof": 42},
        "Custom (Manual Override)": {"heat_outdoor": 20, "cool_outdoor": 95, "moisture_grains": 100, "cltd_wall": 25, "cltd_roof": 40}
    }
    return lang_dict, regional_data

LANG_DICT, REGIONAL_DATA = load_static_environmental_profiles()

# Caches project lookup data for 60 seconds to stop database overhead latency on simple clicks
@st.cache_data(ttl=60)
def get_calculation_history_cached(user_id):
    return get_calculation_history(user_id)

# ==============================================================================
# 1. CLIENT INITIALIZATION & SECURE ROUTING LAYER
# ==============================================================================
SUPABASE_URL = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY", "your-anon-key")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def supabase_auth(email, password, action="login"):
    """Handles secure cloud signup and login natively via the Supabase client"""
    try:
        if action == "signup":
            res = supabase.auth.sign_up({"email": email, "password": password})
            return {"success": True, "user_id": res.user.id, "email": res.user.email}
        else:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            return {"success": True, "user_id": res.user.id, "email": res.user.email}
    except Exception as e:
        err_msg = str(e)
        if "error_description" in err_msg:
            try:
                import json
                err_dict = json.loads(err_msg.replace("'", '"'))
                err_msg = err_dict.get("error_description", err_msg)
            except:
                pass
        return {"success": False, "error": err_msg}

# ==============================================================================
# 2. LIVE SECURE DATA TRANSACTION LAYER (DIRECT API COUPLING)
# ==============================================================================
def save_calculation(name, data, result, lang_choice, user_id):
    payload = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "project_name": name, "location": data['location'], "mode": data['mode'], "lang": lang_choice,
        "t_indoor": data['t_indoor'], "t_outdoor": data['t_outdoor'], "moisture_grains": data['moisture_grains'],
        "cltd_wall": data['cltd_wall'], "cltd_roof": data['cltd_roof'], "area_walls": data['area_walls'],
        "u_walls": data['u_walls'], "area_windows": data['area_windows'], "u_windows": data['u_windows'],
        "area_roof": data['area_roof'], "u_roof": data['u_roof'], "volume": data['volume'], "ach": data['ach'],
        "occupants": data['occupants'], "shgc": data['shgc'], "safety_factor": data['safety_factor'],
        "total_btu_hr": result['total_btu_hr'], "tons": result.get('tons', 0.0), "cfm": result['cfm'],
        "user_id": user_id  
    }
    try:
        url = f"{SUPABASE_URL}/rest/v1/calculations"
        headers = {
            "apiKey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            st.cache_data.clear() # Flushes history cache instantly so the new item loads immediately
    except Exception as e:
        st.error(f"Cloud Save Interrupted: {str(e)}")

def get_calculation_history(user_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/calculations?user_id=eq.{user_id}&order=id.desc&limit=50"
        headers = {"apiKey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return [[row['id'], row['project_name'], row['timestamp'], row['mode']] for row in data]
    except:
        pass
    return []

def load_calculation_by_id(calc_id, user_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/calculations?id=eq.{calc_id}&user_id=eq.{user_id}"
        headers = {"apiKey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json():
            return response.json()[0]
    except:
        pass
    return None

# ==============================================================================
# 3. CORE HVAC PROCESSING LOGIC
# ==============================================================================
def get_duct_recommendation(cfm, lang):
    is_sp = (lang == "Spanish")
    if cfm <= 150: return '6" Round' if not is_sp else '6" Redondo'
    elif cfm <= 250: return '7" Round' if not is_sp else '7" Redondo'
    elif cfm <= 400: return '8" Round' if not is_sp else '8" Redondo'
    elif cfm <= 700: return '10" Round' if not is_sp else '10" Redondo'
    elif cfm <= 1000: return '12" Round' if not is_sp else '12" Redondo'
    elif cfm <= 1400: return '14" Round' if not is_sp else '14" Redondo'
    else: return '16"+ Round' if not is_sp else '16"+ Redondo'

def calculate_heating_load(data):
    delta_t = data['t_indoor'] - data['t_outdoor']
    q_conduction = (data['u_walls'] * data['area_walls'] * delta_t) + (data['u_windows'] * data['area_windows'] * delta_t) + (data['u_roof'] * data['area_roof'] * delta_t)
    cfm_infil = (data['volume'] * data['ach']) / 60
    return {'total_btu_hr': round((q_conduction + (1.08 * cfm_infil * delta_t)) * data['safety_factor']), 'cfm': round(cfm_infil, 1)}

def calculate_cooling_load(data):
    q_walls = data['u_walls'] * data['area_walls'] * data['cltd_wall']
    q_roof = data['u_roof'] * data['area_roof'] * data['cltd_roof']
    q_windows = data['u_windows'] * data['area_windows'] * (data['t_outdoor'] - data['t_indoor'])
    q_solar = data['area_windows'] * data['shgc'] * 200 
    cfm_infil = (data['volume'] * data['ach']) / 60
    total_sensible = q_walls + q_roof + q_windows + q_solar + (1.08 * cfm_infil * (data['t_outdoor'] - data['t_indoor'])) + (data['occupants'] * 250)
    total_load = (total_sensible + (0.68 * cfm_infil * max(0, data['moisture_grains'] - 65)) + (data['occupants'] * 200)) * data['safety_factor']
    return {'total_btu_hr': round(total_load), 'tons': round(total_load / 12000, 2), 'cfm': round(total_sensible / (1.08 * 20))}

def generate_pdf_report(data, result, mode, lang, ctx):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, str(ctx["pdf_title"]), ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Project: {data.get('location')} - Scope: {str(mode)}", ln=True)
    if "Heating" in str(mode):
        pdf.cell(0, 8, f"Total Capacity: {result.get('total_btu_hr'):,} BTU/hr", ln=True)
    else:
        pdf.cell(0, 8, f"Total Capacity: {result.get('total_btu_hr'):,} BTU/hr (~{result.get('tons')} Tons)", ln=True)
    filename = f"vetcool_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(filename)
    return filename

# ==============================================================================
# 4. ROUTING CONTROL & PREMIUM BRANDED UI
# ==============================================================================
# --- PERFORMANCE CRITICAL CHANGE: Applied Brand Name, Branded Favicon, and App Cache Optimizations ---
st.set_page_config(
    page_title="Vetcool FieldFlow", 
    page_icon="❄️", 
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .stButton>button { background-color: #E30613; color: white; font-weight: bold; border-radius: 6px; }
    h1, h2, h3, label { color: #FFFFFF !important; }
    .metric-card { background-color: #1E232A; padding: 20px; border-radius: 10px; border-left: 5px solid #E30613; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None

# --- ROUTE A: LOGIN GATEWAY PORTAL ---
if st.session_state["auth_user"] is None:
    st.title("Vetcool FieldFlow")
    st.subheader("Secure Mobile Advisory Dashboard")
    
    auth_mode = st.radio("Access Method / Metodo", ["Sign In / Iniciar Sesion", "Create Pro Account / Registrarse"], horizontal=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        auth_email = st.text_input("Corporate Email Address")
        auth_pass = st.text_input("Account Password", type="password")
        
        if auth_mode == "Sign In / Iniciar Sesion":
            if st.button("Unlock Core Dashboard"):
                res = supabase_auth(auth_email, auth_pass, action="login")
                if res["success"]:
                    st.session_state["auth_user"] = {"id": res["user_id"], "email": res["email"]}
                    st.rerun()
                else:
                    st.error(f"Access Denied: {res['error']}")
        else:
            if st.button("Register License Profile"):
                res = supabase_auth(auth_email, auth_pass, action="signup")
                if res["success"]:
                    st.success("Registration Successful! Please sign in using your credentials.")
                else:
                    st.error(f"Registration Interrupted: {res['error']}")

# --- ROUTE B: AUTHENTICATED SaaS CALCULATOR CORE ---
else:
    current_user = st.session_state["auth_user"]
    
    with st.sidebar:
        lang = st.radio("Language / Idioma", ["English", "Spanish"], horizontal=True)
        ctx = LANG_DICT[lang]
        st.caption(f"Authenticated as: **{current_user['email']}**")
        if st.button("Sign Out / Cerrar Sesion"):
            st.session_state["auth_user"] = None
            st.session_state["override_data"] = None
            st.rerun()

    st.title(ctx["title"])
    st.markdown(f"**{ctx['subtitle']}**")

    # Sidebar History Layout (Leverages Cached Performance Engine)
    with st.sidebar:
        st.markdown("---")
        st.subheader(ctx["history_header"])
        history_records = get_calculation_history_cached(current_user["id"])
        
        if history_records:
            history_options = {f"{r[1]} ({r[2]})": r[0] for r in history_records}
            selected_history = st.selectbox("Select Past Project to Load", ["-- Select Active Project --"] + list(history_options.keys()))
            
            if selected_history != "-- Select Active Project --":
                chosen_id = history_options[selected_history]
                loaded_calc = load_calculation_by_id(chosen_id, current_user["id"])
                if loaded_calc:
                    st.session_state["override_data"] = loaded_calc
                    st.success(f"Project pulled from secure sync!")
        else:
            st.caption("No historical configurations logged under this account profile.")

        st.markdown("---")
        st.header(ctx["sidebar_settings"])
        
        active_override = st.session_state.get("override_data", None)
        init_loc_idx = list(REGIONAL_DATA.keys()).index(active_override["location"]) if active_override and active_override["location"] in REGIONAL_DATA else 0
        location = st.selectbox(ctx["climate_loc"], list(REGIONAL_DATA.keys()), index=init_loc_idx)
        geo_defaults = REGIONAL_DATA[location]
        
        proj_name = st.text_input(ctx["proj_name_lbl"], value=active_override["project_name"] if active_override else "Job #1001")
        preset_keys = ["Custom Input", "Small House (1200 sq ft)", "Medium House (2000 sq ft)", "Large House (3000 sq ft)", "Small Office", "Restaurant"]
        preset_labels = [ctx["presets_dict"][k] for k in preset_keys]
        selected_preset_label = st.selectbox(ctx["presets"], preset_labels, index=2)
        preset = preset_keys[preset_labels.index(selected_preset_label)]
        
        init_safety = int(round((active_override["safety_factor"] - 1) * 100)) if active_override else 10
        safety_slider = st.slider(ctx["safety_margin"], min_value=0, max_value=30, value=init_safety, step=5)
        safety_factor = 1.0 + (safety_slider / 100)

    # Core Metrics Defaults
    if preset == "Small House (1200 sq ft)": defaults = {"walls": 800, "windows": 150, "roof": 1200, "volume": 9600, "occupants": 3}
    elif preset == "Medium House (2000 sq ft)": defaults = {"walls": 1400, "windows": 250, "roof": 2000, "volume": 16000, "occupants": 5}
    elif preset == "Large House (3000 sq ft)": defaults = {"walls": 2000, "windows": 400, "roof": 3000, "volume": 24000, "occupants": 7}
    elif preset == "Small Office": defaults = {"walls": 1800, "windows": 300, "roof": 1800, "volume": 14400, "occupants": 12}
    elif preset == "Restaurant": defaults = {"walls": 1500, "windows": 250, "roof": 1500, "volume": 12000, "occupants": 25}
    else: defaults = {"walls": 1200, "windows": 200, "roof": 1500, "volume": 9000, "occupants": 4}

    if active_override:
        defaults = {"walls": active_override["area_walls"], "windows": active_override["area_windows"], "roof": active_override["area_roof"], "volume": active_override["volume"], "occupants": active_override["occupants"]}

    tab1, tab2 = st.tabs([ctx["tab_compute"], ctx["tab_method"]])

    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            init_mode_idx = 0 if (active_override and "Heating" in str(active_override["mode"])) else 1
            mode_label = st.radio(ctx["calc_path"], [ctx["heat_load"], ctx["cool_load"]], index=init_mode_idx)
            mode = "Cooling Load" if mode_label == ctx["cool_load"] else "Heating Load"
            t_indoor = st.number_input(ctx["target_indoor"], value=float(active_override["t_indoor"] if active_override else (72 if mode == "Heating Load" else 75)))
            
            if location == "Custom (Manual Override)":
                t_outdoor = st.number_input(ctx["design_outdoor"], value=float(active_override["t_outdoor"] if active_override else 95))
                moisture_grains = st.number_input(ctx["humidity_grains"], value=float(active_override["moisture_grains"] if active_override else 100))
                cltd_wall, cltd_roof = 25, 40
            else:
                t_outdoor = geo_defaults["cool_outdoor"] if mode == "Cooling Load" else geo_defaults["heat_outdoor"]
                moisture_grains = geo_defaults["moisture_grains"]
                cltd_wall, cltd_roof = geo_defaults["cltd_wall"], geo_defaults["cltd_roof"]
                st.caption(f"{ctx['weather_profile_msg']}: **{t_outdoor} F**")

        with col2:
            st.subheader(ctx["building_metrics"])
            c_sub1, c_sub2 = st.columns(2)
            with c_sub1:
                area_walls = st.number_input(ctx["net_wall"], value=int(defaults["walls"]))
                area_windows = st.number_input(ctx["tot_window"], value=int(defaults["windows"]))
                area_roof = st.number_input(ctx["roof_area"], value=int(defaults["roof"]))
            with c_sub2:
                u_walls = st.selectbox(ctx["wall_ins"], [0.04, 0.06, 0.08, 0.12, 0.25], index=2)
                u_windows = st.selectbox(ctx["window_glaze"], [0.28, 0.35, 0.48, 0.70], index=1)
                u_roof = st.selectbox(ctx["roof_ins"], [0.03, 0.05, 0.08, 0.15], index=1)

            st.subheader(ctx["internal_vars"])
            c_sub3, c_sub4 = st.columns(2)
            with c_sub3:
                volume = st.number_input(ctx["room_vol"], value=int(defaults["volume"]))
                occupants = st.number_input(ctx["occupants"], value=int(defaults["occupants"]), step=1)
            with c_sub4:
                ach = st.selectbox(ctx["tightness"], [0.2, 0.35, 0.5, 0.75, 1.2], index=2)
                shgc = st.slider(ctx["shgc_lbl"], min_value=0.20, max_value=0.85, value=0.40, step=0.05)

        st.markdown("---")
        
        if st.button(ctx["btn_calc"], type="primary", use_container_width=True):
            data = {
                'location': location, 't_indoor': t_indoor, 't_outdoor': t_outdoor, 'moisture_grains': moisture_grains,
                'cltd_wall': cltd_wall, 'cltd_roof': cltd_roof, 'area_walls': area_walls, 'u_walls': u_walls,
                'area_windows': area_windows, 'u_windows': u_windows, 'area_roof': area_roof, 'u_roof': u_roof,
                'volume': volume, 'ach': ach, 'occupants': occupants, 'shgc': shgc, 'safety_factor': safety_factor, 'mode': mode_label
            }

            if mode == "Heating Load":
                result = calculate_heating_load(data)
                st.markdown(f'<div class="metric-card"><h3>{ctx["heat_capacity"]}</h3><h2>{result["total_btu_hr"]:,} BTU/hr</h2><p>{ctx["circ_target"]}: <b>{result["cfm"]} CFM</b></p></div>', unsafe_allow_html=True)
            else:
                result = calculate_cooling_load(data)
                st.markdown(f'<div class="metric-card"><h3>{ctx["cool_capacity"]}</h3><h2>{result["total_btu_hr"]:,} BTU/hr (~{result["tons"]} {ctx["nominal_tons"]})</h2><p>{ctx["req_airflow"]}: <b>{result["cfm"]} CFM</b></p></div>', unsafe_allow_html=True)

            save_calculation(proj_name, data, result, lang, current_user["id"])
            st.toast("Estimate synchronized to Vetcool FieldFlow Cloud!", icon="💾")

            try:
                pdf_file = generate_pdf_report(data, result, mode_label, lang, ctx)
                with open(pdf_file, "rb") as f:
                    st.download_button(ctx["btn_pdf"], f, file_name=pdf_file, mime="application/pdf")
                os.remove(pdf_file)
            except Exception as e:
                st.error(f"{ctx['pdf_fault']}: {str(e)}")
