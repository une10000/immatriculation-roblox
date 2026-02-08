# =============================================================
# RCRP VOGUE OS - EDITION 2026
# DESIGN : MINIMALIST LUXURY / TACTICAL 
# =============================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# -------------------------------------------------------------
# [STYLE] : L'INTERFACE "WOW"
# -------------------------------------------------------------
st.set_page_config(page_title="RCRP VOGUE", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700;900&family=JetBrains+Mono&display=swap');

    /* BASE */
    .stApp {
        background-color: #080808;
        font-family: 'Montserrat', sans-serif;
        color: #FFFFFF;
    }

    /* TITRE PRINCIPAL */
    .main-title {
        font-weight: 900;
        font-size: 5rem;
        letter-spacing: -4px;
        background: linear-gradient(180deg, #FFFFFF 30%, #222 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }

    /* CARTES GLASSMORPHISM */
    .st-emotion-cache-12w0qpk {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
    }

    /* REÇU TICKET STYLISÉ */
    .receipt-box {
        background-color: #FFFFFF;
        color: #000000;
        padding: 30px;
        border-radius: 2px;
        font-family: 'JetBrains Mono', monospace;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        margin: 20px 0;
        position: relative;
    }
    .receipt-header {
        border-bottom: 2px dashed #000;
        padding-bottom: 10px;
        margin-bottom: 15px;
        text-align: center;
        font-weight: 900;
    }

    /* BOUTONS PRÉCISION */
    .stButton>button {
        background: transparent !important;
        border: 1px solid #444 !important;
        color: #888 !important;
        border-radius: 0px !important;
        padding: 10px 20px !important;
        font-size: 0.7rem !important;
        letter-spacing: 2px;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        border-color: #FFF !important;
        color: #FFF !important;
        background: rgba(255,255,255,0.05) !important;
    }

    /* INPUTS */
    .stTextInput>div>div>input {
        background: transparent !important;
        border: none !important;
        border-bottom: 1px solid #333 !important;
        border-radius: 0px !important;
        color: #FFF !important;
        font-size: 1.2rem !important;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] { gap: 40px; }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #444 !important;
        font-weight: 700 !important;
        font-size: 1.1rem;
    }
    .stTabs [aria-selected="true"] { color: #FFF !important; }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# [LOGIQUE] : PARAMÈTRES ET DATA
# -------------------------------------------------------------
RULES = {
    "RCT": "une10000",
    "AVE": "Moune2010",
    "TAXE": 175,
    "PRICE_RCT": 150,
    "PRICE_AVE": 130
}

if 'auth' not in st.session_state: st.session_state.auth = None
if 'receipt' not in st.session_state: st.session_state.receipt = None

def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    b = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
    i = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
    p = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
    return conn, b, i, p

def clean_val(v):
    try: return float(str(v).replace('$', '').replace(' ', '').replace(',', ''))
    except: return 0.0

# -------------------------------------------------------------
# [MODULE] : SYSTÈME D'IMMATRICULATION + TICKET REÇU
# -------------------------------------------------------------
def register_vehicle(conn, df_b, df_i, user, brand, plate, assurance):
    # Calcul Prix
    total = RULES["TAXE"]
    if "RCT" in assurance: total += RULES["PRICE_RCT"]
    if "AVERIS" in assurance: total += RULES["PRICE_AVE"]
    
    # Check Money
    idx_u = df_b[df_b["Nom Roblox"] == user].index[0]
    bal_u = clean_val(df_b.at[idx_u, "Solde"])
    
    if bal_u < total:
        return False, "Fonds insuffisants."
    
    # Transaction
    df_b.at[idx_u, "Solde"] = bal_u - total
    
    # Redirections
    if "RCT" in assurance:
        idx_r = df_b[df_b["Nom Roblox"] == RULES["RCT"]].index[0]
        df_b.at[idx_r, "Solde"] = clean_val(df_b.at[idx_r, "Solde"]) + 150
    if "AVERIS" in assurance:
        idx_m = df_b[df_b["Nom Roblox"] == RULES["AVE"]].index[0]
        df_b.at[idx_m, "Solde"] = clean_val(df_b.at[idx_m, "Solde"]) + 130
        
    # Enregistrement
    new_v = pd.DataFrame([{
        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
        "Nom d'utilisateur ROBLOX": user,
        "Marque du véhicule": brand,
        "Numéro de la plaque": plate,
        "Assurance": assurance
    }])
    
    conn.update(worksheet="Banque", data=df_b)
    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_i, new_v]))
    
    # Création du Reçu "Wow"
    st.session_state.receipt = {
        "user": user,
        "plate": plate,
        "brand": brand,
        "total": total,
        "tax": RULES["TAXE"],
        "ins": total - RULES["TAXE"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    return True, "Enregistré avec succès."

# -------------------------------------------------------------
# [INTERFACE] : PORTAIL
# -------------------------------------------------------------
if st.session_state.auth is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 class='main-title'>VOGUE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='letter-spacing:5px; color:#555;'>RENSSELAER COUNTY OS</p>", unsafe_allow_html=True)
        
        mode = st.selectbox("SECTION", ["Accès Public", "Agent RCT", "Staff"])
        if mode == "Accès Public":
            if st.button("ENTRER"): st.session_state.auth = "Civil"; st.rerun()
        elif mode == "Agent RCT":
            p = st.text_input("PASSWORD", type="password")
            if st.button("LOGIN"):
                if p == "RCT-26-RCRPFR": st.session_state.auth = "RCT"; st.rerun()
        else:
            p = st.text_input("PASSWORD", type="password")
            if st.button("LOGIN"):
                if p == "RCRPFR-25-26": st.session_state.auth = "Staff"; st.rerun()
    st.stop()

# -------------------------------------------------------------
# [MAIN] : DASHBOARD
# -------------------------------------------------------------
conn, df_b, df_i, df_p = load_data()

# Header Simple
st.markdown(f"<p style='color:#555; font-weight:700;'>AUTH // {st.session_state.auth.upper()}</p>", unsafe_allow_html=True)
if st.button("DÉCONNEXION", key="logout"): st.session_state.auth = None; st.rerun()

tabs = st.tabs(["💰 BANQUE", "🚔 DMV / IMMAT", "🛡️ PERMIS", "⚙️ ADMINISTRATION"])

# --- TAB BANQUE ---
with tabs[0]:
    search = st.text_input("RECHERCHER UN NOM...")
    for idx, r in df_b.iterrows():
        if search.lower() in str(r["Nom Roblox"]).lower():
            st.markdown(f"""
                <div style="border-bottom: 1px solid #222; padding: 20px 0; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight:800; font-size:1.5rem;">{r['Nom Roblox']}</div>
                        <div style="color:#555; font-size:0.8rem;">{r['Emploiement']}</div>
                    </div>
                    <div style="font-family:'JetBrains Mono'; font-size:1.5rem;">{clean_val(r['Solde']):,.0f} $</div>
                </div>
            """, unsafe_allow_html=True)

# --- TAB DMV (AVEC TICKET REÇU) ---
with tabs[1]:
    if st.session_state.auth in ["RCT", "Staff"]:
        st.markdown("### ENREGISTREMENT")
        with st.container():
            ca1, ca2 = st.columns(2)
            u_name = ca1.selectbox("PROPRIÉTAIRE", df_b["Nom Roblox"].tolist())
            u_brand = ca1.text_input("MARQUE ET MODÈLE")
            u_plate = ca2.text_input("PLAQUE")
            u_assu = ca2.selectbox("ASSURANCE", ["AUCUNE", "RCT (150$)", "AVERIS (130$)"])
            
            if st.button("GÉNÉRER L'IMMATRICULATION"):
                if u_brand and u_plate:
                    ok, msg = register_vehicle(conn, df_b, df_i, u_name, u_brand, u_plate, u_assu)
                    if ok: st.success(msg)
                    else: st.error(msg)
                else: st.warning("Champs manquants.")

    # AFFICHAGE DU REÇU (LE TRUC COOL)
    if st.session_state.receipt:
        st.markdown("<br>", unsafe_allow_html=True)
        rc = st.session_state.receipt
        st.markdown(f"""
            <div class="receipt-box">
                <div class="receipt-header">RCRP STATE OFFICIAL RECEIPT</div>
                <div style="display:flex; justify-content:space-between;">
                    <span>CITOYEN:</span> <span>{rc['user']}</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span>VÉHICULE:</span> <span>{rc['brand']}</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span>PLAQUE:</span> <span>{rc['plate']}</span>
                </div>
                <br>
                <div style="border-top:1px solid #EEE; padding-top:10px;">
                    <div style="display:flex; justify-content:space-between;">
                        <span>TAXE ÉTAT:</span> <span>{rc['tax']}$</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span>ASSURANCE:</span> <span>{rc['ins']}$</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-weight:900; font-size:1.2rem; margin-top:10px;">
                        <span>TOTAL PAYÉ:</span> <span>{rc['total']}$</span>
                    </div>
                </div>
                <br>
                <div style="text-align:center; font-size:0.7rem; color:#888;">{rc['date']}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("FERMER LE REÇU"): st.session_state.receipt = None; st.rerun()

    st.markdown("### REGISTRE")
    st.dataframe(df_i, use_container_width=True)

# --- TAB PERMIS ---
with tabs[2]:
    st.markdown("### GESTION DES POINTS")
    for i, r in df_p.iterrows():
        with st.container():
            st.markdown(f"**{r['Nom Roblox']}** — {r['PTS']} PTS")
            if st.session_state.auth in ["RCT", "Staff"]:
                if st.button(f"Saisir points ({r['Nom Roblox']})"):
                    # Logique de retrait simplifiée
                    pass

# --- TAB ADMIN (GREFFE) ---
with tabs[3]:
    if st.session_state.auth == "Staff":
        st.markdown("### GREFFE AUTOMATIQUE")
        with st.form("greffe_form"):
            g_rob = st.text_input("NOM ROBLOX")
            g_dis = st.text_input("NOM DISCORD")
            if st.form_submit_button("CRÉER DOSSIER"):
                # AJOUT AUTO DE LA DATE DE CRÉATION
                d_creation = datetime.now().strftime("%d/%m/%Y")
                nb = pd.DataFrame([{"Solde": 15000, "Emploiement": "Civil", "Nom Discord": g_dis, "Nom Roblox": g_rob, "Date d'arrivée": d_creation}])
                np = pd.DataFrame([{"Nom Discord": g_dis, "Nom Roblox": g_rob, "PTS": 25, "Validité": "OUI"}])
                conn.update(worksheet="Banque", data=pd.concat([df_b, nb]))
                conn.update(worksheet="Points Permis", data=pd.concat([df_p, np]))
                st.success(f"Dossier crée le {d_creation}")
