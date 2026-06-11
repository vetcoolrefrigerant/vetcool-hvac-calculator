import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os

# ==============================================================================
# 1. TRANSLATION DICTIONARY (ENGLISH & SPANISH)
# ==============================================================================
LANG_DICT = {
    "English": {
        "title": "VetCool Field Load Calculator",
        "subtitle": "Professional Estimation & Sanity-Check Tool",
        "sidebar_settings": "Global Settings",
        "select_lang": "Language / Idioma",
        "climate_loc": "Design Climate Location",
        "presets": "Property Presets",
        "safety_margin": "Safety Margin Cushion (%)",
        "safety_desc": "Cushion Included",
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
        "tightness_help": "Air Changes per Hour. 0.35 is tight modern construction; 0.75+ is leaky.",
        "shgc_lbl": "Window Solar Coefficient (SHGC)",
        "shgc_help": "Solar Heat Gain Coefficient. Lower value blocks more radiant heat.",
        "btn_calc": "Generate Load Profiles",
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
        "method_body": """This app functions as an advanced block-load model designed for rapid technical sales assistance. 
Unlike simple linear calculators, it incorporates:

* **CLTD (Cooling Load Temperature Difference):** Factoring in radiant energy absorption delays for walls and roof structures instead of simple temperature deltas.
* **Latent Load Profiles:** Evaluating regional relative humidity differentials against standard inside conditions (~65 grains of absolute moisture) to calculate latent infiltration penalties.
* **Glazing Variables:** Evaluating radiant solar vectors by applying variable *Solar Heat Gain Coefficients (SHGC)* directly against real-world exposure values.

*Always verify manual design structures against a formal ACCA Manual J protocol for strict code compliance.*""",
        "disclaimer": "Disclaimer: This estimate is based on simplified block load calculation principles. It is intended for quick field estimates and sales verification. Verify with full local code requirements before equipment purchase.",
        "pdf_title": "VetCool HVAC ESTIMATE REPORT",
        "pdf_scope": "Calculation Scope",
        "pdf_target": "Design Target Location",
        "pdf_inputs": "INPUT DESIGN PARAMETERS",
        "pdf_results": "ESTIMATED LOAD RESULTS",
        "pdf_duct": "Suggested Trunk Line Profile",
        "presets_dict": {
            "Custom Input": "Custom Input",
            "Small House (1200 sq ft)": "Small House (1200 sq ft)",
            "Medium House (2000 sq ft)": "Medium House (2000 sq ft)",
            "Large House (3000 sq ft)": "Large House (3000 sq ft)",
            "Small Office": "Small Office",
            "Restaurant": "Restaurant"
        }
    },
    "Spanish": {
        "title": "Calculadora de Carga de Campo VetCool",
        "subtitle": "Herramienta Profesional de Estimacion y Verificacion",
        "sidebar_settings": "Configuracion Global",
        "select_lang": "Language / Idioma",
        "climate_loc": "Ubicacion del Clima de Diseno",
        "presets": "Preajustes de la Propiedad",
        "safety_margin": "Margen de Seguridad (%)",
        "safety_desc": "Colchon Incluido",
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
        "roof_area": "Area de Techo/Cielo Raso (sq ft)",
        "wall_ins": "Aislamiento de Pared (Valor-U)",
        "window_glaze": "Acristalamiento de Ventana (Valor-U)",
        "roof_ins": "Aislamiento de Techo (Valor-U)",
        "wall_ins_help": "Menor valor significa mejor aislamiento. 0.06 es una pared aislada estandar.",
        "window_glaze_help": "0.28=Vidrio Triple, 0.48=Vidrio Doble Claro.",
        "roof_ins_help": "0.03=Techo R-38, 0.05=Techo R-21.",
        "internal_vars": "Variables Internas e Infiltracion",
        "room_vol": "Volumen Cubico Acondicionado (cu ft)",
        "occupants": "Promedio de Ocupantes Continuos",
        "tightness": "Hermeticidad del Envolvente (ACH)",
        "tightness_help": "Cambios de aire por hora. 0.35 es construccion moderna hermetica; 0.75+ tiene fugas.",
        "shgc_lbl": "Coeficiente Solar de Ventana (SHGC)",
        "shgc_help": "Coeficiente de ganancia de calor solar. Un valor mas bajo bloquea mas calor radiante.",
        "btn_calc": "Generar Perfiles de Carga",
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
        "method_body": """Esta aplicacion funciona como un modelo avanzado de carga de bloques disenado para asistencia rapida en ventas tecnicas. 
A diferencia de las calculadoras lineales simples, incorpora:

* **CLTD (Diferencia de Temperatura de Carga de Enfriamiento):** Factura los retrasos en la absorcion de energia radiante para estructuras de paredes y techos en lugar de simples deltas de temperatura.
* **Perfiles de Carga Latente:** Evalua los diferenciales de humedad relativa regional frente a las condiciones interiores estandar (~65 granos de humedad absoluta) para calcular las penalizaciones por infiltracion latente.
* **Variables de Acristalamiento:** Evalua los vectores solares radiantes aplicando coeficientes de ganancia de calor solar (SHGC) variables directamente contra los valores de exposicion del mundo real.

*Verifique siempre las estructuras de diseno manual con un protocolo formal ACCA Manual J para el cumplimiento estricto del codigo.*""",
        "disclaimer": "Descargo de responsabilidad: Esta estimacion se basa en principios simplificados de calculo de carga de bloques. Esta destinada a estimaciones rapidas de campo y verificacion de ventas. Verifique con los requisitos del codigo local antes de comprar el equipo.",
        "pdf_title": "INFORME DE ESTIMACION DE HVAC VETCOOL",
        "pdf_scope": "Alcance del Calculo",
        "pdf_target": "Ubicacion de Diseno Objetivo",
        "pdf_inputs": "PARAMETROS DE DISENO DE ENTRADA",
        "pdf_results": "RESULTADOS DE CARGA ESTIMADA",
        "pdf_duct": "Perfil Sugerido de la Linea Principal",
        "presets_dict": {
            "Custom Input": "Entrada Personalizada",
            "Small House (1200 sq ft)": "Casa Pequena (1200 sq ft)",
            "Medium House (2000 sq ft)": "Casa Mediana (2000 sq ft)",
            "Large House (3000 sq ft)": "Casa Grande (3000 sq ft)",
            "Small Office": "Oficina Pequena",
            "Restaurant": "Restaurante"
        }
    }
}

# ==============================================================================
# 2. REGIONAL DESIGN DATA & CONSTANTS
# ==============================================================================
REGIONAL_DATA = {
    "Miami, FL": {"heat_outdoor": 48, "cool_outdoor": 91, "moisture_grains": 145, "cltd_wall": 28, "cltd_roof": 46},
    "Phoenix, AZ": {"heat_outdoor": 38, "cool_outdoor": 108, "moisture_grains": 60, "cltd_wall": 35, "cltd_roof": 52},
    "Chicago, IL": {"heat_outdoor": -1, "cool_outdoor": 91, "moisture_grains": 100, "cltd_wall": 22, "cltd_roof": 38},
    "New York, NY": {"heat_outdoor": 15, "cool_outdoor": 89, "moisture_grains": 105, "cltd_wall": 21, "cltd_roof": 38},
    "Houston, TX": {"heat_outdoor": 32, "cool_outdoor": 95, "moisture_grains": 130, "cltd_wall": 26, "cltd_roof": 44},
    "Denver, CO": {"heat_outdoor": 2, "cool_outdoor": 92, "moisture_grains": 55, "cltd_wall": 25, "cltd_roof": 42},
    "Custom (Manual Override)": {"heat_outdoor": 20, "cool_outdoor": 95, "moisture_grains": 100, "cltd_wall": 25, "cltd_roof": 40}
}

def get_duct_recommendation(cfm, lang):
    is_sp = (lang == "Spanish")
    if cfm <= 150:
        return '6" Round (or 6x6 Rectangular)' if not is_sp else '6" Redondo (o 6x6 Rectangular)'
    elif cfm <= 250:
        return '7" Round (or 8x6 Rectangular)' if not is_sp else '7" Redondo (o 8x6 Rectangular)'
    elif cfm <= 400:
        return '8" Round (or 10x6 Rectangular)' if not is_sp else '8" Redondo (o 10x6 Rectangular)'
    elif cfm <= 700:
        return '10" Round (or 12x8 Rectangular)' if not is_sp else '10" Redondo (o 12x8 Rectangular)'
    elif cfm <= 1000:
        return '12" Round (or 16x8 Rectangular)' if not is_sp else '12" Redondo (o 16x8 Rectangular)'
    elif cfm <= 1400:
        return '14" Round (or 20x8 Rectangular)' if not is_sp else '14" Redondo (o 20x8 Rectangular)'
    else:
        return '16"+ Round' if not is_sp else '16"+ Redondo'

# ==============================================================================
# 3. CORE CALCULATION ENGINES
# ==============================================================================
def calculate_heating_load(data):
    delta_t = data['t_indoor'] - data['t_outdoor']
    q_walls = data['u_walls'] * data['area_walls'] * delta_t
    q_windows = data['u_windows'] * data['area_windows'] * delta_t
    q_roof = data['u_roof'] * data['area_roof'] * delta_t
    q_conduction = q_walls + q_windows + q_roof
    
    cfm_infil = (data['volume'] * data['ach']) / 60
    q_infil = 1.08 * cfm_infil * delta_t
    
    total = (q_conduction + q_infil) * data['safety_factor']
    return {'total_btu_hr': round(total), 'cfm': round(cfm_infil, 1)}

def calculate_cooling_load(data):
    q_walls = data['u_walls'] * data['area_walls'] * data['cltd_wall']
    q_roof = data['u_roof'] * data['area_roof'] * data['cltd_roof']
    q_windows = data['u_windows'] * data['area_windows'] * (data['t_outdoor'] - data['t_indoor'])
    
    q_solar = data['area_windows'] * data['shgc'] * 200 
    cfm_infil = (data['volume'] * data['ach']) / 60
    
    delta_t = data['t_outdoor'] - data['t_indoor']
    q_inf_sensible = 1.08 * cfm_infil * delta_t
    
    delta_grains = max(0, data['moisture_grains'] - 65)
    q_inf_latent = 0.68 * cfm_infil * delta_grains
    
    total_sensible = q_walls + q_roof + q_windows + q_solar + q_inf_sensible + (data['occupants'] * 250)
    total_load = (total_sensible + q_inf_latent + (data['occupants'] * 200)) * data['safety_factor']
    
    required_cfm = total_sensible / (1.08 * 20)
    return {'total_btu_hr': round(total_load), 'tons': round(total_load / 12000, 2), 'cfm': round(required_cfm)}

# ==============================================================================
# 4. REPORT GENERATION
# ==============================================================================
def generate_pdf_report(data, result, mode, lang, ctx):
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.image("vetcool_logo.png", x=140, y=8, w=60)
    except:
        pass

    # Explicit font set to standard Helvetica core distribution
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, str(ctx["pdf_title"]), ln=True, align="C")
    pdf.ln(15)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Date / Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(0, 8, f"{ctx['pdf_scope']}: {str(mode)}", ln=True)
    pdf.cell(0, 8, f"{ctx['pdf_target']}: {data.get('location')}", ln=True)
    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, str(ctx["pdf_inputs"]), ln=True)
    pdf.set_font("Helvetica", "", 11)
    
    skip_keys = ["mode", "location", "cltd_wall", "cltd_roof", "moisture_grains"]
    for key, value in data.items():
        if key not in skip_keys:
            nice_key = key.replace('_', ' ').title()
            if "Factor" in nice_key:
                nice_key = "Safety Cushion" if lang == "English" else "Colchon de Seguridad"
                value = f"{round((value - 1) * 100)}%"
            pdf.cell(0, 6, f" - {nice_key}: {value}", ln=True)

    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, str(ctx["pdf_results"]), ln=True)
    pdf.set_font("Helvetica", "", 11)

    if "Heating" in data['mode'] or "Calefaccion" in data['mode']:
        pdf.cell(0, 8, f"Total Capacity: {result.get('total_btu_hr'):,} BTU/hr", ln=True)
        pdf.cell(0, 8, f"Airflow / Flujo de Aire: {result.get('cfm')} CFM", ln=True)
    else:
        pdf.cell(0, 8, f"Total Capacity: {result.get('total_btu_hr'):,} BTU/hr (~{result.get('tons')} Tons)", ln=True)
        pdf.cell(0, 8, f"Airflow / Flujo de Aire: {result.get('cfm')} CFM", ln=True)

    pdf.cell(0, 8, f"{ctx['pdf_duct']}: {get_duct_recommendation(result.get('cfm'), lang)}", ln=True)

    pdf.ln(20)
    pdf.set_font("Helvetica", "I", 9)
    # Complete normalization cleanup of accent characters specifically inside the PDF array block
    clean_disclaimer = ctx["disclaimer"].replace("ó", "o").replace("á", "a").replace("í", "i").replace("ú", "u").replace("ñ", "n")
    pdf.multi_cell(0, 5, clean_disclaimer, align="C")

    filename = f"vetcool_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(filename)
    return filename

# ==============================================================================
# 5. STREAMLIT APPLICATION UI
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

# Language Selector Setup
with st.sidebar:
    lang = st.radio("Language / Idioma", ["English", "Spanish"], horizontal=True)
    ctx = LANG_DICT[lang]

st.title(ctx["title"])
st.markdown(f"**{ctx['subtitle']}**")

with st.sidebar:
    st.markdown("---")
    st.header(ctx["sidebar_settings"])
    location = st.selectbox(ctx["climate_loc"], list(REGIONAL_DATA.keys()))
    geo_defaults = REGIONAL_DATA[location]
    
    preset_keys = ["Custom Input", "Small House (1200 sq ft)", "Medium House (2000 sq ft)", "Large House (3000 sq ft)", "Small Office", "Restaurant"]
    preset_labels = [ctx["presets_dict"][k] for k in preset_keys]
    selected_preset_label = st.selectbox(ctx["presets"], preset_labels, index=2)
    preset = preset_keys[preset_labels.index(selected_preset_label)]
    
    safety_slider = st.slider(ctx["safety_margin"], min_value=0, max_value=30, value=10, step=5)
    safety_factor = 1.0 + (safety_slider / 100)

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

tab1, tab2 = st.tabs([ctx["tab_compute"], ctx["tab_method"]])

with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        mode_label = st.radio(ctx["calc_path"], [ctx["heat_load"], ctx["cool_load"]], index=1)
        mode = "Cooling Load" if mode_label == ctx["cool_load"] else "Heating Load"
        
        t_indoor = st.number_input(ctx["target_indoor"], value=72 if mode == "Heating Load" else 75)
        
        if location == "Custom (Manual Override)":
            t_outdoor = st.number_input(ctx["design_outdoor"], value=95 if mode == "Cooling Load" else 20)
            moisture_grains = st.number_input(ctx["humidity_grains"], value=100)
            cltd_wall, cltd_roof = 25, 40
        else:
            t_outdoor = geo_defaults["cool_outdoor"] if mode == "Cooling Load" else geo_defaults["heat_outdoor"]
            moisture_grains = geo_defaults["moisture_grains"]
            cltd_wall = geo_defaults["cltd_wall"]
            cltd_roof = geo_defaults["cltd_roof"]
            st.caption(f"{ctx['weather_profile_msg']}: **{t_outdoor} F DB**")

    with col2:
        st.subheader(ctx["building_metrics"])
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            area_walls = st.number_input(ctx["net_wall"], value=defaults["walls"])
            area_windows = st.number_input(ctx["tot_window"], value=defaults["windows"])
            area_roof = st.number_input(ctx["roof_area"], value=defaults["roof"])
        with c_sub2:
            u_walls = st.selectbox(ctx["wall_ins"], [0.04, 0.06, 0.08, 0.12, 0.25], index=2, help=ctx["wall_ins_help"])
            u_windows = st.selectbox(ctx["window_glaze"], [0.28, 0.35, 0.48, 0.70], index=1, help=ctx["window_glaze_help"])
            u_roof = st.selectbox(ctx["roof_ins"], [0.03, 0.05, 0.08, 0.15], index=1, help=ctx["roof_ins_help"])

        st.subheader(ctx["internal_vars"])
        c_sub3, c_sub4 = st.columns(2)
        with c_sub3:
            volume = st.number_input(ctx["room_vol"], value=defaults["volume"])
            occupants = st.number_input(ctx["occupants"], value=defaults["occupants"], step=1)
        with c_sub4:
            ach = st.selectbox(ctx["tightness"], [0.2, 0.35, 0.5, 0.75, 1.2], index=2, help=ctx["tightness_help"])
            shgc = st.slider(ctx["shgc_lbl"], min_value=0.20, max_value=0.85, value=0.40, step=0.05, help=ctx["shgc_help"])

    st.markdown("---")
    
    if st.button(ctx["btn_calc"], type="primary", use_container_width=True):
        data = {
            'location': location, 't_indoor': t_indoor, 't_outdoor': t_outdoor,
            'moisture_grains': moisture_grains, 'cltd_wall': cltd_wall, 'cltd_roof': cltd_roof,
            'area_walls': area_walls, 'u_walls': u_walls,
            'area_windows': area_windows, 'u_windows': u_windows,
            'area_roof': area_roof, 'u_roof': u_roof,
            'volume': volume, 'ach': ach, 'occupants': occupants,
            'shgc': shgc, 'safety_factor': safety_factor, 'mode': mode_label
        }

        if mode == "Heating Load":
            result = calculate_heating_load(data)
            st.markdown(f"""
            <div class="metric-card">
                <h3>{ctx['heat_capacity']}</h3>
                <h2>{result['total_btu_hr']:,} BTU/hr</h2>
                <p>{ctx['circ_target']}: <b>{result['cfm']} CFM</b></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            result = calculate_cooling_load(data)
            st.markdown(f"""
            <div class="metric-card">
                <h3>{ctx['cool_capacity']}</h3>
                <h2>{result['total_btu_hr']:,} BTU/hr (~{result['tons']} {ctx['nominal_tons']})</h2>
                <p>{ctx['req_airflow']}: <b>{result['cfm']} CFM</b></p>
            </div>
            """, unsafe_allow_html=True)

        duct_recommendation = get_duct_recommendation(result['cfm'], lang)
        st.info(f"{ctx['suggested_duct']}: {duct_recommendation}")

        try:
            pdf_file = generate_pdf_report(data, result, mode_label, lang, ctx)
            with open(pdf_file, "rb") as f:
                st.download_button(ctx["btn_pdf"], f, file_name=pdf_file, mime="application/pdf")
            os.remove(pdf_file)
        except Exception as e:
            st.error(f"{ctx['pdf_fault']}: {str(e)}")

with tab2:
    st.header(ctx["method_title"])
    st.markdown(ctx["method_body"])
    st.subheader("VetCool")
    st.write("Web: [vetcoolrefrigerant.com](https://vetcoolrefrigerant.com)")