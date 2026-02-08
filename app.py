# ======================================================================================
# RCRP PRISMA OS | VERSION 4000.0.0
# DESIGN : MINIMALIST PREMIUM / GLASSMORPHISM
# ======================================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --------------------------------------------------------------------------------------
# [SECTION 1] : LE DESIGN "WOW" (STYLES CSS AVANCÉS)
# --------------------------------------------------------------------------------------
st.set_page_config(page_title="RCRP PRISMA", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400&display=swap');

    /* FOND D'ÉCRAN PROFOND */
    .stApp {
        background: #000000;
        font-family: 'Inter', sans-serif;
        color: #FFFFFF;
    }

    /* EFFET DE VERRE (GLASSMORPHISM) */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 25px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }

    /* TITRES ÉPURÉS */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -2px !important;
        background: linear-gradient(90deg, #FFFFFF, #666666);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        margin-bottom: 0px !important;
    }

    /* BOUTONS PREMIUM */
    .stButton>button {
        background: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        transition: 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        text-transform: uppercase;
        font-size: 0.8rem !important;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(255, 255, 255, 0.2) !important;
    }

    /* INPUTS MINIMALISTES */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 10px 15px !important;
    }

    /* TABS STYLISÉS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent !important;
        border: none !important;
        color: #666 !important;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom: 2px solid #FFFFFF !important;
    }

    /* METRICS */
    div[data-testid="stMetricValue"] {
        font-weight: 700 !important;
        font-family: 'JetBrains Mono', monospace !important;
        color: #FFFFFF !important;
    }

    /* SCROLLBAR */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #000; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# [SECTION 2] : CONFIGURATION & FLUX (TES RÈGLES)
# --------------------------------------------------------------------------------------
if 'auth' not in st.session_state: st.session_state.auth = None
if 'logs' not in st.session_state: st.session_state.logs = []

RULES = {
    "RCT_CPT": "une10000",
    "AVE_CPT": "Moune2010",
    "TAXE": 175,
    "PRICE_RCT": 150,
    "PRICE_AVE": 130,
    "PWD_RCT": "RCT-26-RCRPFR",
    "PWD_STAFF": "RCRPFR-25-26",
    "MARQUES": sorted(["Acura", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", "BMW", "Bugatti", "Cadillac", "Chevrolet", "Dodge", "Ferrari", "Ford", "GMC", "Honda", "Hyundai", "Jaguar", "Jeep", "Lamborghini", "Land Rover", "Lexus", "Maserati", "Mazda", "McLaren", "Mercedes-Benz", "Nissan", "Porsche", "Rolls-Royce", "Tesla", "Toyota", "Volkswagen", "Volvo"])
}

# --------------------------------------------------------------------------------------
# [SECTION 3] : MOTEUR DATA
# --------------------------------------------------------------------------------------
def load_prisma_db():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        b = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
        i = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        p = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
        return conn, b, i, p
    except:
        st.error("DATABASE OFFLINE"); return None, None, None, None

def push_log(msg):
    st.session_state.logs.insert(0, f"{datetime.now().strftime('%H:%M')} — {msg}")

def clean_cash(val):
    try: return float(str(val).replace('$', '').replace(' ', '').replace(',', ''))
    except: return 0.0

# --------------------------------------------------------------------------------------
# [SECTION 4] : PORTAIL D'ENTRÉE (LOOK WOW)
# --------------------------------------------------------------------------------------
if st.session_state.auth is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1>PRISMA OS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#666; font-size:1.2rem; margin-top:-10px;'>RENSSELAER COUNTY ADMINISTRATION</p>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            mode = st.selectbox("IDENTIFICATION", ["Citoyen", "Agent RCT", "Administrateur Staff"])
            
            if mode == "Citoyen":
                if st.button("ACCÉDER AU TERMINAL"):
                    st.session_state.auth = "Civil"; st.rerun()
            
            elif mode == "Agent RCT":
                key = st.text_input("BADGE ID", type="password")
                if st.button("DÉVERROUILLER"):
                    if key == RULES["PWD_RCT"]: st.session_state.auth = "RCT"; st.rerun()
                    else: st.error("IDENTIFIANT INCORRECT")
            
            elif mode == "Administrateur Staff":
                key = st.text_input("ROOT KEY", type="password")
                if st.button("DÉVERROUILLER SYSTEM"):
                    if key == RULES["PWD_STAFF"]: st.session_state.auth = "Staff"; st.rerun()
                    else: st.error("ACCÈS RÉVOQUÉ")
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --------------------------------------------------------------------------------------
# [SECTION 5] : CORE INTERFACE
# --------------------------------------------------------------------------------------
conn, df_b, df_i, df_p = load_prisma_db()

# HEADER
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"<h1>{st.session_state.auth.upper()} PORTAL</h1>", unsafe_allow_html=True)
with col_h2:
    if st.button("DÉCONNEXION"): st.session_state.auth = None; st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# STATS RAPIDES (LOOK FINTECH)
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.metric("TOTAL CIRCULATION", f"{len(df_i)} UNITÉS")
    st.markdown("</div>", unsafe_allow_html=True)
with m2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    total_val = sum([clean_cash(x) for x in df_b["Solde"]])
    st.metric("LIQUIDITÉS COMTÉ", f"{total_val:,.0f} $")
    st.markdown("</div>", unsafe_allow_html=True)
with m3:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.metric("STATUS", "OPÉRATIONNEL", "LIVE")
    st.markdown("</div>", unsafe_allow_html=True)

# NAVIGATION
tabs = st.tabs(["FINANCES", " DMV REGISTRY", " CONDUCTEURS", "ADMINISTRATION"])

# --- ONGLETS BANQUE ---
with tabs[0]:
    st.markdown("### RECHERCHE DE COMPTE")
    search = st.text_input("Nom de l'utilisateur...", label_visibility="collapsed")
    
    for idx, r in df_b.iterrows():
        if search.lower() in str(r["Nom Roblox"]).lower():
            st.markdown(f"""
                <div class="glass-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="color:#666; font-size:0.8rem;">PROFIL CITOYEN</span><br>
                            <span style="font-size:1.5rem; font-weight:700;">{r['Nom Roblox']}</span><br>
                            <span style="color:#666;">{r['Emploiement']}</span>
                        </div>
                        <div style="text-align:right;">
                            <span style="color:#666; font-size:0.8rem;">SOLDE ACTUEL</span><br>
                            <span style="font-size:2rem; font-weight:800;">{clean_cash(r['Solde']):,.0f} $</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.auth in ["RCT", "Staff"]:
                c1, c2, c3 = st.columns([2, 1, 1])
                amt = c1.number_input("Somme à débiter ($)", min_value=0.0, key=f"deb_{idx}")
                if c2.button("CONFIRMER LE DÉBIT", key=f"btn_d_{idx}"):
                    curr = clean_cash(df_b.at[idx, "Solde"])
                    if curr >= amt:
                        df_b.at[idx, "Solde"] = curr - amt
                        conn.update(worksheet="Banque", data=df_b)
                        push_log(f"Prélèvement de {amt}$ sur {r['Nom Roblox']}")
                        st.rerun()

# --- ONGLET DMV (LA LOGIQUE DE PRIX WOW) ---
with tabs[1]:
    if st.session_state.auth in ["RCT", "Staff"]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### NOUVEL ENREGISTREMENT")
        with st.form("dmv_prisma"):
            ca1, ca2 = st.columns(2)
            u_name = ca1.selectbox("PROPRIÉTAIRE", df_b["Nom Roblox"].tolist())
            u_brand = ca1.selectbox("MARQUE", RULES["MARQUES"])
            u_plate = ca2.text_input("PLAQUE")
            u_assu = ca2.selectbox("ASSURANCE", ["AUCUNE", "AVERIS (130$)", "RCT (150$)"])
            
            # CALCULS
            total = RULES["TAXE"]
            if "RCT" in u_assu: total += RULES["PRICE_RCT"]
            if "AVERIS" in u_assu: total += RULES["PRICE_AVE"]
            
            st.markdown(f"#### TOTAL : {total}$")
            
            if st.form_submit_button("ÉMETTRE L'IMMATRICULATION"):
                idx_u = df_b[df_b["Nom Roblox"] == u_name].index[0]
                solde_u = clean_cash(df_b.at[idx_u, "Solde"])
                
                if solde_u >= total:
                    # 1. Débit
                    df_bank_new = df_b.copy()
                    df_bank_new.at[idx_u, "Solde"] = solde_u - total
                    
                    # 2. Redirection RCT -> une10000
                    if "RCT" in u_assu:
                        idx_r = df_bank_new[df_bank_new["Nom Roblox"] == RULES["RCT_CPT"]].index[0]
                        df_bank_new.at[idx_r, "Solde"] = clean_cash(df_bank_new.at[idx_r, "Solde"]) + 150
                    
                    # 3. Redirection Averis -> Moune2010
                    if "AVERIS" in u_assu:
                        idx_m = df_bank_new[df_bank_new["Nom Roblox"] == RULES["AVE_CPT"]].index[0]
                        df_bank_new.at[idx_m, "Solde"] = clean_cash(df_bank_new.at[idx_m, "Solde"]) + 130
                        
                    new_v = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y"), "Nom d'utilisateur ROBLOX": u_name, "Marque du véhicule": u_brand, "Numéro de la plaque": u_plate, "Assurance": u_assu}])
                    conn.update(worksheet="Banque", data=df_bank_new)
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_i, new_v]))
                    push_log(f"Nouvelle plaque {u_plate} pour {u_name}")
                    st.success("ENREGISTRÉ"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("### VÉHICULES ENREGISTRÉS")
    st.dataframe(df_i, use_container_width=True)

# --- ONGLET CONDUCTEURS ---
with tabs[2]:
    st.markdown("### DOSSIERS PERMIS")
    for i, r in df_p.iterrows():
        with st.container():
            st.markdown(f"""
                <div class="glass-card" style="padding:15px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between;">
                        <span>{r['Nom Roblox']}</span>
                        <span style="font-weight:700;">{r['PTS']} POINTS</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- ONGLET ADMIN (GREFFE + LOGS) ---
with tabs[3]:
    if st.session_state.auth == "Staff":
        with st.expander("🔨 GREFFE - CRÉER UN CITOYEN"):
            with st.form("new_cit"):
                nc1, nc2 = st.columns(2)
                rob = nc1.text_input("PSEUDO ROBLOX")
                dis = nc2.text_input("PSEUDO DISCORD")
                if st.form_submit_button("CRÉER LE DOSSIER"):
                    d_sys = datetime.now().strftime("%d/%m/%Y")
                    nb = pd.DataFrame([{"Solde": 15000, "Emploiement": "Civil", "Nom Discord": dis, "Nom Roblox": rob, "Date d'arrivée": d_sys}])
                    np = pd.DataFrame([{"Nom Discord": dis, "Nom Roblox": rob, "PTS": 25, "Validité": "OUI"}])
                    conn.update(worksheet="Banque", data=pd.concat([df_b, nb]))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_p, np]))
                    push_log(f"Nouveau citoyen : {rob}")
                    st.success("CITOYEN CRÉÉ"); st.rerun()
    
    st.markdown("### JOURNAL SYSTÈME")
    for log in st.session_state.logs:
        st.markdown(f"<p style='color:#666; font-family:monospace;'>{log}</p>", unsafe_allow_html=True)
