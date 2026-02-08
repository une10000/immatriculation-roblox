# ======================================================================================
# RCRP APEX ENGINE | VERSION 5000.0.0
# ARCHITECTURE : ENTERPRISE ROLEPLAY MANAGEMENT SYSTEM
# DÉVELOPPÉ POUR : RENSSELAER COUNTY RP
# ======================================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import plotly.graph_objects as go
import random

# --------------------------------------------------------------------------------------
# [SECTION 1] : DESIGN SYSTEM - "APEX DARK" (CSS ULTRA-LOURD)
# --------------------------------------------------------------------------------------
st.set_page_config(page_title="RCRP APEX", page_icon="🏎️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600;800&display=swap');

    /* FOND ET TEXTE */
    .stApp {
        background: #050505;
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }

    /* TITRE APEX */
    .apex-title {
        font-family: 'Orbitron', sans-serif;
        font-weight: 800;
        background: linear-gradient(180deg, #FFFFFF 0%, #333333 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem;
        letter-spacing: 5px;
        margin-bottom: 0px;
    }

    /* CARTE GLASSMORPHISM V2 */
    .st-emotion-cache-12w0qpk { /* Container Streamlit */
        background: rgba(20, 20, 20, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
    }

    .card {
        background: rgba(255, 255, 255, 0.02);
        border-left: 4px solid #FFFFFF;
        padding: 20px;
        margin: 10px 0px;
        border-radius: 0px 10px 10px 0px;
        transition: 0.3s;
    }
    .card:hover {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #58a6ff;
    }

    /* BOUTONS TACTIQUES */
    .stButton>button {
        width: 100%;
        background: transparent !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
        border-radius: 0px !important;
        padding: 15px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.7rem !important;
        transition: 0.3s !important;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background: #FFFFFF !important;
        color: #000000 !important;
        box-shadow: 0px 0px 20px rgba(255, 255, 255, 0.3) !important;
    }

    /* BADGES */
    .badge {
        padding: 5px 12px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .badge-rct { background: #0052FF; color: white; }
    .badge-staff { background: #FF004D; color: white; }
    .badge-civ { background: #333; color: #AAA; }

    /* INPUTS */
    input, select, textarea {
        background: #111 !important;
        border: 1px solid #333 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# [SECTION 2] : LOGIQUE CORE & CONSTANTES
# --------------------------------------------------------------------------------------
CONFIG = {
    "CPT_MOUNE": "Moune2010",
    "CPT_UNE": "une10000",
    "TAXE_DMV": 175,
    "INS_RCT": 150,
    "INS_AVE": 130,
    "PWD_RCT": "RCT-26-RCRPFR",
    "PWD_STAFF": "RCRPFR-25-26",
    "MARQUES": sorted(["Acura", "Audi", "BMW", "Bentley", "Bugatti", "Cadillac", "Chevrolet", "Dodge", "Ferrari", "Ford", "GMC", "Honda", "Hyundai", "Jaguar", "Jeep", "Lamborghini", "Land Rover", "Lexus", "Maserati", "Mazda", "McLaren", "Mercedes-Benz", "Nissan", "Porsche", "Rolls-Royce", "Tesla", "Toyota", "Volkswagen", "Volvo"])
}

# Initialisation Session State
if 'page' not in st.session_state: st.session_state.page = "Login"
if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'logs' not in st.session_state: st.session_state.logs = []

# --------------------------------------------------------------------------------------
# [SECTION 3] : MOTEUR DE DONNÉES (GOOGLE SHEETS)
# --------------------------------------------------------------------------------------
def connect_db():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        b = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
        i = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        p = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
        return conn, b, i, p
    except Exception as e:
        st.error(f"DATABASE CONNECTION ERROR: {e}")
        return None, None, None, None

def save_log(msg):
    st.session_state.logs.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def to_cash(val):
    try: return float(str(val).replace('$', '').replace(' ', '').replace(',', ''))
    except: return 0.0

# --------------------------------------------------------------------------------------
# [SECTION 4] : SYSTÈME DE FACTURATION & REDIRECTION (TON LOGO + TES COMPTES)
# --------------------------------------------------------------------------------------
def process_transaction(conn, df_bank, df_immat, civil, marque, plaque, assurance):
    """Gère le débit, les taxes et les virements vers toi ou Moune"""
    
    # 1. Calcul du prix
    total = CONFIG["TAXE_DMV"]
    if "RCT" in assurance: total += CONFIG["INS_RCT"]
    if "AVERIS" in assurance: total += CONFIG["INS_AVE"]
    
    # 2. Vérification solde
    idx_civ = df_bank[df_bank["Nom Roblox"] == civil].index[0]
    solde_civ = to_cash(df_bank.at[idx_civ, "Solde"])
    
    if solde_civ < total:
        return False, "Solde insuffisant pour cette opération."
    
    # 3. Exécution débit
    df_bank.at[idx_civ, "Solde"] = solde_civ - total
    
    # 4. REDIRECTIONS
    if "RCT" in assurance:
        idx_u = df_bank[df_bank["Nom Roblox"] == CONFIG["CPT_UNE"]].index[0]
        df_bank.at[idx_u, "Solde"] = to_cash(df_bank.at[idx_u, "Solde"]) + 150
        save_log(f"Virement Assurance RCT (150$) -> {CONFIG['CPT_UNE']}")
        
    if "AVERIS" in assurance:
        idx_m = df_bank[df_bank["Nom Roblox"] == CONFIG["CPT_MOUNE"]].index[0]
        df_bank.at[idx_m, "Solde"] = to_cash(df_bank.at[idx_m, "Solde"]) + 130
        save_log(f"Virement Assurance Averis (130$) -> {CONFIG['CPT_MOUNE']}")
        
    # 5. Enregistrement Immatriculation
    new_veh = pd.DataFrame([{
        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
        "Nom d'utilisateur ROBLOX": civil,
        "Marque du véhicule": marque,
        "Numéro de la plaque": plaque,
        "Assurance": assurance
    }])
    
    # 6. Push Google Sheets
    conn.update(worksheet="Banque", data=df_bank)
    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_immat, new_veh]))
    
    return True, "Succès : Immatriculation et flux financiers validés."

# --------------------------------------------------------------------------------------
# [SECTION 5] : INTERFACE DE CONNEXION APEX
# --------------------------------------------------------------------------------------
if st.session_state.role is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.markdown("<h1 class='apex-title'>APEX ENGINE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='letter-spacing:10px; color:#555;'>RENSSELAER COUNTY</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            mode = st.radio("SÉLECTIONNER LE PORTAIL", ["CIVIL", "RCT AGENT", "STAFF ADMIN"], horizontal=True)
            
            if mode == "CIVIL":
                if st.button("ACCÈS LIBRE"):
                    st.session_state.role = "Civil"; st.rerun()
            
            elif mode == "RCT AGENT":
                pwd = st.text_input("BADGE AUTH", type="password")
                if st.button("VÉRIFIER"):
                    if pwd == CONFIG["PWD_RCT"]:
                        st.session_state.role = "RCT"; st.rerun()
                    else: st.error("ACCÈS REFUSÉ")
            
            elif mode == "STAFF ADMIN":
                pwd = st.text_input("ROOT ACCESS", type="password")
                if st.button("DÉVERROUILLER"):
                    if pwd == CONFIG["PWD_STAFF"]:
                        st.session_state.role = "Staff"; st.rerun()
                    else: st.error("CRITICAL ERROR")
    st.stop()

# --------------------------------------------------------------------------------------
# [SECTION 6] : CHARGEMENT ET DASHBOARD
# --------------------------------------------------------------------------------------
conn, df_b, df_i, df_p = connect_db()

# Barre latérale tactique
with st.sidebar:
    st.markdown(f"### 🎖️ {st.session_state.role}")
    st.markdown("---")
    st.markdown("### 📊 ÉCONOMIE")
    total_val = sum([to_cash(x) for x in df_b["Solde"]])
    st.metric("Masse Monétaire", f"{total_val:,.0f} $")
    
    st.markdown("---")
    if st.button("🚪 QUITTER LE SYSTÈME"):
        st.session_state.role = None; st.rerun()

# CONTENU PRINCIPAL
t1, t2, t3, t4, t5 = st.tabs(["💎 DASHBOARD", "🏦 BANQUE", "🚔 DMV", "🛡️ PERMIS", "⚙️ SYSTEM"])

# --- TAB DASHBOARD (NOUVEAU: Graphiques Wow) ---
with t1:
    st.markdown("## VUE D'ENSEMBLE DU COMTÉ")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.metric("CITOYENS", len(df_b))
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.metric("FLOTTE TOTALE", len(df_i))
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        avg_bal = total_val / len(df_b) if len(df_b) > 0 else 0
        st.metric("SOLDE MOYEN", f"{avg_bal:,.0f} $")
        st.markdown("</div>", unsafe_allow_html=True)

    # Graphique de répartition des richesses
    st.markdown("### RÉPARTITION DES CAPITAUX")
    fig = go.Figure(data=[go.Pie(labels=df_b["Nom Roblox"][:10], values=[to_cash(x) for x in df_b["Solde"]][:10], hole=.4)])
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# --- TAB BANQUE (NOUVEAU: Système de facturation) ---
with t2:
    st.markdown("## GESTION DES FLUX FINANCIERS")
    search_b = st.text_input("🔍 Rechercher un compte...", placeholder="Entrez un pseudo...")
    
    for idx, r in df_b.iterrows():
        if search_b.lower() in str(r["Nom Roblox"]).lower():
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-size:1.2rem; font-weight:800;">{r['Nom Roblox']}</span>
                        <span style="font-family:'Orbitron'; font-size:1.5rem;">{to_cash(r['Solde']):,.0f} $</span>
                    </div>
                    <span style="color:#555;">ID Discord: {r['Nom Discord']} | Arrivée: {r.get("Date d'arrivée", "Inconnue")}</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.session_state.role in ["RCT", "Staff"]:
                    with st.expander("🛠️ OPÉRATIONS"):
                        c_a, c_b = st.columns(2)
                        amt = c_a.number_input("Montant", min_value=0.0, key=f"amt_{idx}")
                        reason = c_b.text_input("Raison", key=f"rs_{idx}")
                        if st.button("APPLIQUER TAXE / AMENDE", key=f"tax_{idx}"):
                            df_b.at[idx, "Solde"] = to_cash(df_b.at[idx, "Solde"]) - amt
                            conn.update(worksheet="Banque", data=df_b)
                            save_log(f"Amende de {amt}$ appliquée à {r['Nom Roblox']} pour {reason}")
                            st.success("Transaction effectuée."); st.rerun()

# --- TAB DMV (NOUVEAU: Garage personnel) ---
with t3:
    st.markdown("## DÉPARTEMENT DES VÉHICULES")
    
    if st.session_state.role in ["RCT", "Staff"]:
        with st.container(border=True):
            st.markdown("### 📝 NOUVELLE IMMATRICULATION")
            with st.form("dmv_apex"):
                f1, f2 = st.columns(2)
                f_civ = f1.selectbox("PROPRIÉTAIRE", df_b["Nom Roblox"].tolist())
                f_mar = f1.selectbox("MARQUE", CONFIG["MARQUES"])
                f_pla = f2.text_input("PLAQUE")
                f_ass = f2.selectbox("FORMULE", ["AUCUNE", "AVERIS (130$)", "RCT (150$)"])
                
                if st.form_submit_button("VALIDER LE DOSSIER"):
                    ok, msg = process_transaction(conn, df_b, df_i, f_civ, f_mar, f_pla, f_ass)
                    if ok:
                        save_log(f"Immat {f_pla} ({f_mar}) pour {f_civ}")
                        st.success(msg); time.sleep(1); st.rerun()
                    else: st.error(msg)
    
    st.markdown("### 📂 REGISTRE NATIONAL")
    search_i = st.text_input("Rechercher Plaque/Proprio", key="si")
    res_i = df_i[df_i.astype(str).apply(lambda x: x.str.contains(search_i, case=False)).any(axis=1)]
    st.dataframe(res_i, use_container_width=True)

# --- TAB PERMIS (Barre de progression visuelle) ---
with t4:
    st.markdown("## ÉTAT DES LICENCES")
    for i, r in df_p.iterrows():
        with st.container():
            pts = int(r["PTS"]) if str(r["PTS"]).isdigit() else 0
            color = "#00FF00" if pts > 15 else "#FFA500" if pts > 5 else "#FF0000"
            
            st.markdown(f"**{r['Nom Roblox']}**")
            st.markdown(f"""
            <div style="background:#222; width:100%; height:10px; border-radius:5px;">
                <div style="background:{color}; width:{pts*4}%; height:10px; border-radius:5px;"></div>
            </div>
            <span style="font-size:10px; color:#555;">{pts} / 25 POINTS</span>
            """, unsafe_allow_html=True)
            
            if st.session_state.role in ["RCT", "Staff"]:
                if st.button(f"RETIRER 1 POINT ({r['Nom Roblox']})"):
                    df_p.at[i, "PTS"] = max(0, pts - 1)
                    conn.update(worksheet="Points Permis", data=df_p)
                    st.rerun()

# --- TAB SYSTEM (GREFFE AUTO-DATE + LOGS) ---
with t5:
    if st.session_state.role == "Staff":
        st.markdown("## 🔨 ADMINISTRATION DU GREFFE")
        with st.form("greffe_form"):
            st.markdown("### CRÉATION DE PROFIL CITOYEN")
            g1, g2 = st.columns(2)
            g_rob = g1.text_input("NOM ROBLOX")
            g_dis = g2.text_input("NOM DISCORD")
            if st.form_submit_button("VALIDER L'IDENTITÉ"):
                d_sys = datetime.now().strftime("%d/%m/%Y")
                new_b = pd.DataFrame([{"Solde": 15000, "Emploiement": "Civil", "Nom Discord": g_dis, "Nom Roblox": g_rob, "Date d'arrivée": d_sys}])
                new_p = pd.DataFrame([{"Nom Discord": g_dis, "Nom Roblox": g_rob, "PTS": 25, "Validité": "OUI"}])
                conn.update(worksheet="Banque", data=pd.concat([df_b, new_b]))
                conn.update(worksheet="Points Permis", data=pd.concat([df_p, new_p]))
                save_log(f"NOUVEAU CITOYEN : {g_rob} ({d_sys})")
                st.success(f"Dossier créé le {d_sys}"); st.rerun()

    st.markdown("## 📜 LOGS SÉCURISÉS")
    for log in st.session_state.logs:
        st.markdown(f"<div style='font-family:monospace; color:#444;'>{log}</div>", unsafe_allow_html=True)family:monospace;'>{log}</p>", unsafe_allow_html=True)
