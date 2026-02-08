# ==================================================================================================
# FICHIER : RCRP_OVERLORD_OS.PY
# PROJET  : RENSSELAER COUNTY - SYSTEME CENTRAL (UI OVERHAUL)
# VERSION : 3000.0.0 (GRAPHICAL EDITION)
# CLIENT  : GOUVERNEMENT DE RENSSELAER
# ==================================================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random

# ==================================================================================================
# [1] CONFIGURATION ET DESIGN SYSTEM (CSS LOURD)
# ==================================================================================================

st.set_page_config(
    page_title="RCRP OVERLORD OS",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# THÈME GRAPHIQUE "TACTICAL BLUE"
st.markdown("""
    <style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Roboto+Mono:wght@400;700&display=swap');

    /* BASE */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(#111 1px, transparent 1px);
        background-size: 20px 20px;
        color: #e0f2fe;
        font-family: 'Rajdhani', sans-serif;
    }

    /* HEADERS AVEC GLOW */
    h1, h2, h3 {
        color: #0ea5e9 !important;
        text-transform: uppercase;
        text-shadow: 0 0 10px rgba(14, 165, 233, 0.5);
        border-bottom: 2px solid #0ea5e9;
        padding-bottom: 10px;
        letter-spacing: 2px;
    }

    /* CUSTOM METRICS CARDS */
    div[data-testid="stMetric"] {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        text-align: center;
    }
    div[data-testid="stMetricLabel"] { color: #94a3b8; font-size: 0.8rem; }
    div[data-testid="stMetricValue"] { color: #38bdf8; font-family: 'Roboto Mono', monospace; font-size: 1.8rem; }

    /* BOUTONS FUTURISTES */
    .stButton>button {
        background: linear-gradient(45deg, #0ea5e9, #0284c7);
        color: white;
        border: none;
        border-radius: 2px;
        padding: 12px 24px;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s ease;
        clip-path: polygon(10% 0, 100% 0, 100% 70%, 90% 100%, 0 100%, 0 30%);
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(14, 165, 233, 0.6);
    }

    /* INPUTS STYLISÉS */
    .stTextInput>div>div>input {
        background-color: #0f172a !important;
        color: #38bdf8 !important;
        border: 1px solid #1e293b !important;
        font-family: 'Roboto Mono', monospace;
    }
    .stSelectbox>div>div>div {
        background-color: #0f172a !important;
        color: #38bdf8 !important;
    }

    /* TERMINAL WINDOW */
    .terminal-window {
        background-color: #000;
        border: 1px solid #333;
        color: #0f0;
        font-family: 'Courier New', monospace;
        padding: 20px;
        border-radius: 5px;
        box-shadow: inset 0 0 20px rgba(0, 255, 0, 0.1);
        margin-top: 20px;
    }

    /* LOGS CONTAINER */
    .log-entry {
        font-family: 'Roboto Mono', monospace;
        font-size: 12px;
        border-left: 3px solid #0ea5e9;
        padding-left: 10px;
        margin-bottom: 5px;
        color: #94a3b8;
    }

    /* SIDEBAR SYSTEM MONITOR */
    .sys-monitor {
        font-size: 10px;
        color: #64748b;
        margin-top: 5px;
        font-family: 'Roboto Mono', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================================================================================================
# [2] CONSTANTES ET LOGIQUE MÉTIER (TES RÈGLES)
# ==================================================================================================

CONSTANTS = {
    "CLE_STAFF": "RCRPFR-25-26",
    "CLE_RCT": "RCT-26-RCRPFR",
    "IBAN_RCT": "une10000",       # TON COMPTE
    "IBAN_AVERIS": "Moune2010",   # COMPTE MOUNE
    "TAXE_ETAT": 175,             # ARCENT BRÛLÉ
    "ASSU_RCT": 150,
    "ASSU_AVERIS": 130,
    "MARQUES": [
        "Acura", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", "BMW", "Bugatti", 
        "Buick", "Cadillac", "Chevrolet", "Chrysler", "Dodge", "Ferrari", "Fiat", 
        "Ford", "GMC", "Honda", "Hyundai", "Infiniti", "Jaguar", "Jeep", "Kia", 
        "Lamborghini", "Land Rover", "Lexus", "Lincoln", "Lotus", "Maserati", "Mazda", 
        "McLaren", "Mercedes-Benz", "MINI", "Mitsubishi", "Nissan", "Pagani", 
        "Porsche", "Ram", "Rolls-Royce", "Subaru", "Tesla", "Toyota", "Volkswagen", "Volvo"
    ]
}

# Initialisation Session State
if 'user_role' not in st.session_state: st.session_state.user_role = None
if 'booted' not in st.session_state: st.session_state.booted = False
if 'system_logs' not in st.session_state: st.session_state.system_logs = []

# ==================================================================================================
# [3] FONCTIONS BACKEND (ROBUSTES)
# ==================================================================================================

def get_db():
    """Connecteur sécurisé GSheets"""
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except:
        return None

def fetch_data(conn):
    """Récupère les données avec nettoyage"""
    try:
        b = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
        i = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        p = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
        return b, i, p
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def parse_money(val):
    try: return float(str(val).replace('$', '').replace(' ', '').replace(',', ''))
    except: return 0.0

def add_log(action):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.system_logs.insert(0, f"[{ts}] {action}")

def simulate_processing(text="TRAITEMENT EN COURS"):
    """Fausse barre de chargement pour l'immersion"""
    my_bar = st.progress(0, text=text)
    for percent_complete in range(100):
        time.sleep(0.005) # Rapide mais visible
        my_bar.progress(percent_complete + 1, text=text)
    time.sleep(0.1)
    my_bar.empty()

# ==================================================================================================
# [4] LOGIQUE DE TRANSFERT (INTOUCHABLE)
# ==================================================================================================

def executer_paiement_dmv(conn, df_bank, df_immat, user, marque, plaque, assurance):
    """
    Logique complexe :
    1. Check Solde
    2. Debit User (Total)
    3. Credit RCT (Si applicable) -> une10000
    4. Credit Averis (Si applicable) -> Moune2010
    5. Save
    """
    # Calculs
    cout_total = CONSTANTS["TAXE_ETAT"]
    if "RCT" in assurance: cout_total += CONSTANTS["ASSU_RCT"]
    if "AVERIS" in assurance: cout_total += CONSTANTS["ASSU_AVERIS"]
    
    # Check User
    try:
        idx_user = df_bank[df_bank["Nom Roblox"] == user].index[0]
        solde_user = parse_money(df_bank.at[idx_user, "Solde"])
    except:
        return False, "Utilisateur introuvable."

    if solde_user < cout_total:
        return False, "Fonds Insuffisants."

    simulate_processing("SÉCURISATION DES FONDS...")

    # 1. Débit
    df_bank.at[idx_user, "Solde"] = solde_user - cout_total

    # 2. Crédit RCT (vers une10000)
    if "RCT" in assurance:
        try:
            idx_rct = df_bank[df_bank["Nom Roblox"] == CONSTANTS["IBAN_RCT"]].index[0]
            df_bank.at[idx_rct, "Solde"] = parse_money(df_bank.at[idx_rct, "Solde"]) + CONSTANTS["ASSU_RCT"]
        except: st.error("ERREUR CRITIQUE: COMPTE 'une10000' INTROUVABLE")

    # 3. Crédit Averis (vers Moune2010)
    if "AVERIS" in assurance:
        try:
            idx_avg = df_bank[df_bank["Nom Roblox"] == CONSTANTS["IBAN_AVERIS"]].index[0]
            df_bank.at[idx_avg, "Solde"] = parse_money(df_bank.at[idx_avg, "Solde"]) + CONSTANTS["ASSU_AVERIS"]
        except: st.error("ERREUR CRITIQUE: COMPTE 'Moune2010' INTROUVABLE")

    # 4. Enregistrement Véhicule
    new_row = pd.DataFrame([{
        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
        "Nom d'utilisateur ROBLOX": user,
        "Marque du véhicule": marque,
        "Numéro de la plaque": plaque,
        "Assurance": assurance
    }])
    
    conn.update(worksheet="Banque", data=df_bank)
    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_immat, new_row]))
    
    return True, "Transaction Validée."

# ==================================================================================================
# [5] INTERFACE : SÉQUENCE DE BOOT
# ==================================================================================================

if not st.session_state.booted:
    st.empty()
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.info("INITIALISATION DU SYSTÈME RCRP...")
        time.sleep(1)
        st.markdown("`> CHARGEMENT DU NOYAU... OK`")
        time.sleep(0.5)
        st.markdown("`> CONNEXION CLOUD... OK`")
        time.sleep(0.5)
        st.markdown("`> VÉRIFICATION PROTOCOLES FINANCIERS... OK`")
        st.progress(100)
        time.sleep(0.5)
        st.session_state.booted = True
        st.rerun()

# ==================================================================================================
# [6] INTERFACE : LOGIN SCREEN (CYBER STYLE)
# ==================================================================================================

if st.session_state.user_role is None:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("# RCRP OVERLORD")
        st.markdown("### SYSTÈME D'EXPLOITATION CENTRAL")
        st.markdown("Veuillez vous identifier pour accéder au mainframe.")
        st.markdown("---")
        
        tab_civ, tab_rct, tab_adm = st.tabs(["CITOYEN", "AGENT RCT", "ADMINISTRATION"])
        
        with tab_civ:
            st.caption("Accès restreint (Lecture seule)")
            if st.button("ACCÉDER AU PORTAIL PUBLIC"):
                st.session_state.user_role = "Civil"
                st.rerun()
                
        with tab_rct:
            p_rct = st.text_input("IDENTIFIANT BADGE", type="password")
            if st.button("CONNEXION SÉCURISÉE (RCT)"):
                if p_rct == CONSTANTS["CLE_RCT"]:
                    simulate_processing("DÉCHIFFREMENT...")
                    st.session_state.user_role = "RCT"
                    st.rerun()
                else: st.error("ACCÈS REFUSÉ")
                
        with tab_adm:
            p_adm = st.text_input("CLÉ DE CHIFFREMENT", type="password")
            if st.button("ACCÈS ROOT (ADMIN)"):
                if p_adm == CONSTANTS["CLE_STAFF"]:
                    simulate_processing("AUTHENTIFICATION BIOMÉTRIQUE...")
                    st.session_state.user_role = "Staff"
                    st.rerun()
                else: st.error("VIOLATION DE SÉCURITÉ")
    with c2:
        # Un peu de visuel "Hacker"
        st.markdown("""
        ```bash
        [SYSTEM STATUS]
        > UPTIME: 412h 32m
        > SECURITY: HIGH
        > ENCRYPTION: AES-256
        > DATABASE: CONNECTED
        > NODES: ACTIVE
        
        [WARNING]
        Toute tentative d'intrusion sera
        signalée aux autorités fédérales.
        ```
        """)
    st.stop()

# ==================================================================================================
# [7] INTERFACE : DASHBOARD PRINCIPAL (MAIN LOOP)
# ==================================================================================================

# CHARGEMENT DONNÉES
conn = get_db()
df_b, df_i, df_p = fetch_data(conn)

# SIDEBAR (TÉLÉMÉTRIE)
with st.sidebar:
    st.markdown("### 📡 STATUS SERVEUR")
    st.markdown(f"**USER:** {st.session_state.user_role.upper()}")
    
    # Fake metrics for immersion
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("CPU", f"{random.randint(10, 40)}%")
    col_s2.metric("RAM", f"{random.randint(30, 60)}%")
    st.progress(random.randint(80, 100), text="INTÉGRITÉ CLOUD")
    
    st.markdown("---")
    if st.button("DECONNEXION"):
        st.session_state.user_role = None
        st.rerun()
    
    st.markdown("<div class='sys-monitor'>RCRP_CORE_V3.0.0<br>BUILD: 20260209<br>LOC: NY_STATE</div>", unsafe_allow_html=True)

# DASHBOARD HEADER
st.title("CENTRE DE COMMANDEMENT")

# STATS GLOBALES (POUR LE LOOK)
total_money = df_b["Solde"].apply(parse_money).sum()
total_cars = len(df_i)
total_citizens = len(df_b)

m1, m2, m3, m4 = st.columns(4)
m1.metric("ÉCONOMIE TOTALE", f"{total_money:,.0f} $", "+1.2%")
m2.metric("VÉHICULES ENREGISTRÉS", f"{total_cars}", "+5")
m3.metric("POPULATION", f"{total_citizens}", "+2")
m4.metric("TAXE IMMAT.", "175 $", "FIXE")

st.markdown("---")

# NAVIGATION TABS
tabs = st.tabs(["🏦 BANQUE & FISCALITÉ", "🚗 DMV & IMMAT", "🛡️ PERMIS", "📋 LOGS SYSTÈME"])

# --- TAB BANQUE ---
with tabs[0]:
    c_search, c_res = st.columns([1, 3])
    with c_search:
        st.markdown("#### RECHERCHE")
        q_bank = st.text_input("Nom du citoyen", placeholder="Ex: John Doe...")
    
    with c_res:
        if q_bank:
            found = df_b[df_b["Nom Roblox"].str.contains(q_bank, case=False, na=False)]
            if not found.empty:
                for idx, row in found.iterrows():
                    with st.container(border=True):
                        col_inf, col_act = st.columns([2, 2])
                        with col_inf:
                            st.markdown(f"### 👤 {row['Nom Roblox']}")
                            st.caption(f"Discord: {row['Nom Discord']} | Job: {row['Emploiement']}")
                            st.metric("Solde Bancaire", f"{parse_money(row['Solde']):,.0f} $")
                        
                        with col_act:
                            if st.session_state.user_role in ["RCT", "Staff"]:
                                st.markdown("#### ⚡ ACTIONS RAPIDES")
                                amt = st.number_input("Montant ($)", min_value=0, key=f"b_{idx}")
                                if st.button("DÉBITER LE COMPTE", key=f"btn_{idx}"):
                                    simulate_processing("TRANSACTION...")
                                    curr = parse_money(df_b.at[idx, "Solde"])
                                    if curr >= amt:
                                        df_b.at[idx, "Solde"] = curr - amt
                                        conn.update(worksheet="Banque", data=df_b)
                                        add_log(f"DEBIT {amt}$ sur {row['Nom Roblox']}")
                                        st.success("TRANSACTION EFFECTUÉE")
                                        time.sleep(1); st.rerun()
                                    else: st.error("FONDS INSUFFISANTS")
            else:
                st.warning("Aucun dossier trouvé dans la base de données.")

# --- TAB DMV ---
with tabs[1]:
    col_form, col_list = st.columns([1, 1])
    
    # FORMULAIRE (GAUCHE)
    with col_form:
        if st.session_state.user_role in ["RCT", "Staff"]:
            st.markdown("### 📝 NOUVELLE IMMATRICULATION")
            with st.container(border=True):
                with st.form("dmv_form"):
                    f_user = st.selectbox("PROPRIÉTAIRE", ["---"] + df_b["Nom Roblox"].tolist())
                    f_brand = st.selectbox("MARQUE", sorted(CONSTANTS["MARQUES"]))
                    f_model = st.text_input("MODÈLE (Ex: RS6, M4...)")
                    f_plate = st.text_input("PLAQUE (Ex: NY-1234)")
                    f_assu = st.selectbox("TYPE ASSURANCE", ["AUCUNE", "AVERIS (130$)", "RCT (150$)"])
                    
                    # PREVISUALISATION COUT
                    cout = CONSTANTS["TAXE_ETAT"]
                    if "AVERIS" in f_assu: cout += CONSTANTS["ASSU_AVERIS"]
                    if "RCT" in f_assu: cout += CONSTANTS["ASSU_RCT"]
                    
                    st.markdown(f"**TOTAL À PAYER :** :red[{cout} $]")
                    
                    if st.form_submit_button("VALIDER ET FACTURER"):
                        if f_user != "---" and f_plate:
                            full_brand = f"{f_brand} {f_model}"
                            ok, msg = executer_paiement_dmv(conn, df_b, df_i, f_user, full_brand, f_plate, f_assu)
                            if ok:
                                add_log(f"IMMAT {f_plate} crée pour {f_user}")
                                st.success(msg)
                                time.sleep(1); st.rerun()
                            else: st.error(msg)
    
    # LISTE (DROITE)
    with col_list:
        st.markdown("### 📂 REGISTRE VÉHICULES")
        q_dmv = st.text_input("Rechercher Plaque...", key="search_plate").lower()
        
        # Affichage style tableau de bord
        matches = df_i[df_i["Numéro de la plaque"].astype(str).str.lower().str.contains(q_dmv, na=False)]
        st.dataframe(matches, use_container_width=True, hide_index=True)

# --- TAB PERMIS ---
with tabs[2]:
    if "Greffe" not in tabs: # GREFFE INTEGRE ICI SI ADMIN
        if st.session_state.user_role == "Staff":
            with st.expander("🔨 CRÉATION DE DOSSIER (GREFFE)", expanded=False):
                with st.form("greffe_maker"):
                    g_rob = st.text_input("NOM ROBLOX")
                    g_dis = st.text_input("NOM DISCORD")
                    if st.form_submit_button("INITIALISER NOUVEAU CITOYEN"):
                        simulate_processing("GÉNÉRATION ID ET COMPTES...")
                        d_now = datetime.now().strftime("%d/%m/%Y")
                        # 15k bank
                        new_b = pd.DataFrame([{"Solde": 15000, "Emploiement": "Civil", "Nom Discord": g_dis, "Nom Roblox": g_rob, "Date d'arrivée": d_now}])
                        # 25 pts
                        new_p = pd.DataFrame([{"Nom Discord": g_dis, "Nom Roblox": g_rob, "PTS": 25, "Validité": "OUI"}])
                        
                        conn.update(worksheet="Banque", data=pd.concat([df_b, new_b]))
                        conn.update(worksheet="Points Permis", data=pd.concat([df_p, new_p]))
                        add_log(f"NEW USER {g_rob} created.")
                        st.success("DOSSIER CRÉÉ AVEC SUCCÈS")
                        time.sleep(1); st.rerun()

    st.markdown("### 🚦 POINTS PERMIS")
    q_pts = st.text_input("Recherche Permis...").lower()
    for i, r in df_p.iterrows():
        if q_pts in str(r["Nom Roblox"]).lower():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2,1,1])
                c1.write(f"**{r['Nom Roblox']}**")
                c2.metric("Points", f"{r['PTS']}")
                if st.session_state.user_role in ["RCT", "Staff"]:
                    adj = c3.number_input("Modif.", value=int(r["PTS"]), key=f"pts_{i}", label_visibility="collapsed")
                    if c3.button("SAVE", key=f"s_{i}"):
                        df_p.at[i, "PTS"] = adj
                        conn.update(worksheet="Points Permis", data=df_p)
                        st.rerun()

# --- TAB LOGS ---
with tabs[3]:
    st.markdown("### 📜 JOURNAL D'ACTIVITÉ SÉCURISÉ")
    st.markdown("```")
    for l in st.session_state.system_logs:
        st.markdown(f"<div class='log-entry'>{l}</div>", unsafe_allow_html=True)
    st.markdown("```")

# Footer caché
st.markdown("<br><br><center><small>RCRP SECURE SYSTEM // UNAUTHORIZED ACCESS IS A FELONY</small></center>", unsafe_allow_html=True)
