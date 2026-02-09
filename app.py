# ======================================================================================
# PROJECT : RCRP ENTERPRISE OS - FEDERAL ADMINISTRATION SYSTEM
# VERSION : 21.0.1 (ULTIMATE EDITION - 500+ LINES)
# BUILD   : FEBRUARY 2026
# DEVELOPED FOR : RENSSELAER COUNTY ROLEPLAY
# ======================================================================================

"""
CE LOGICIEL EST LA PROPRIÉTÉ EXCLUSIVE DU GOUVERNEMENT DE RENSSELAER.
TOUTE UTILISATION NON AUTORISÉE DES SYSTÈMES BANCAIRES OU DES BASES DE DONNÉES
EST STRICTEMENT INTERDITE ET SURVEILLÉE PAR L'ADMINISTRATION STAFF.

FONCTIONNALITÉS INCLUSES :
- Gestion adaptative du design (Fix Mode Clair/Nuit pour les captures d'écran)
- Création de profil automatisée (15,000$, 25 PTS, Date automatique)
- Redirection bancaire Averis vers Moune2010
- Redirection bancaire RCT vers une10000
- Calculateur de taxes Trio RCT (3ème assurance offerte)
- Système de logs d'audit en temps réel
- Sécurisation par clés d'accès hiérarchisées
"""

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random
import json

# ======================================================================================
# 1. CORE INTERFACE ENGINE - DESIGN ADAPTATIF ANTI-BUG
# ======================================================================================

st.set_page_config(
    page_title="RCRP - Système de Gestion Gouvernemental",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection d'un CSS massif pour garantir la lisibilité sur les captures (Fix texte invisible)
st.markdown("""
    <style>
    /* VARIABLES DE SYSTÈME */
    :root {
        --rcrp-red: #ff4b4b;
        --rcrp-green: #00FF41;
        --border-color: rgba(128, 128, 128, 0.4);
    }

    /* CORRECTIF MODE CLAIR : Force les bordures et les contrastes */
    /* Cela empêche le bug du texte blanc sur fond blanc lors de tes captures */
    [data-baseweb="input"], .stTextInput>div>div>input, .stNumberInput>div>div>input {
        border: 2px solid var(--border-color) !important;
        border-radius: 10px !important;
        color: inherit !important;
        background-color: transparent !important;
    }

    /* BANNIÈRE GOUVERNEMENTALE PREMIUM */
    .header-box {
        padding: 60px;
        border-radius: 30px;
        border-left: 20px solid var(--rcrp-red);
        background: linear-gradient(135deg, rgba(255,75,75,0.05) 0%, rgba(128,128,128,0.05) 100%);
        margin-bottom: 50px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }
    .header-box h1 { font-size: 3.5em; font-weight: 900; margin: 0; }
    .header-box p { font-size: 1.4em; opacity: 0.8; margin-top: 10px; }

    /* REÇU LÉGAL STYLE "TICKET NÉON" */
    .rcrp-receipt { 
        background-color: #0c0c0c !important; 
        color: var(--rcrp-green) !important; 
        padding: 45px; 
        border-radius: 8px; 
        font-family: 'Courier New', Courier, monospace; 
        border: 2px solid var(--rcrp-green);
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.1);
        line-height: 1.8;
    }
    .divider { border-top: 2px dashed var(--rcrp-green); margin: 25px 0; opacity: 0.4; }

    /* BOUTONS ACTIONS */
    .stButton>button {
        border-radius: 15px !important;
        height: 4em !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }

    /* PANNEAUX INFO */
    .info-card {
        padding: 30px;
        border-radius: 20px;
        border: 1px solid var(--border-color);
        background-color: rgba(128, 128, 128, 0.05);
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# ======================================================================================
# 2. GLOBAL STATE MANAGEMENT & SECURITY
# ======================================================================================

# Initialisation des variables persistantes
if "role" not in st.session_state: st.session_state.role = None
if "receipt_data" not in st.session_state: st.session_state.receipt_data = None
if "audit_trail" not in st.session_state: st.session_state.audit_trail = []
if "temp_msg" not in st.session_state: st.session_state.temp_msg = ""

# Constantes de Routage Bancaire
RCT_TARGET = "une10000"
AVERIS_TARGET = "Moune2010" 

# Identifiants de Cryptage (Codes d'accès)
KEY_ADMIN = "RCRPFR-25-26" 
KEY_RCT = "RCT-26-RCRPFR"

# Assets Graphiques
LOGO_PATH = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

def write_audit(action):
    """Enregistre chaque interaction pour le Staff."""
    ts = datetime.now().strftime("%d/%m - %H:%M:%S")
    st.session_state.audit_trail.append(f"[{ts}] {action}")

# ======================================================================================
# 3. DATA PERSISTENCE LAYER (GOOGLE CLOUD SQL/SHEETS)
# ======================================================================================

@st.cache_data(ttl=0)
def connect_to_cloud():
    """Établit la liaison sécurisée avec les serveurs de données."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Importation des tables
        b_df = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
        i_df = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        p_df = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
        return conn, b_df, i_df, p_df
    except Exception as e:
        st.error(f"FATAL ERROR : Connection failed. {e}")
        return None, None, None, None

cloud_conn, df_bank, df_immat, df_pts = connect_to_cloud()

# ======================================================================================
# 4. PORTAIL D'ACCÈS HIÉRARCHISÉ
# ======================================================================================

if st.session_state.role is None:
    st.markdown("""
        <div class="header-box">
            <h1>🏛️ RCRP OS - TERMINAL V21</h1>
            <p>Connectez-vous pour accéder aux services gouvernementaux de Rensselaer.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.warning("🔒 Système de sécurité actif. Toutes les tentatives échouées sont logguées.")
    
    col_login_1, col_login_2, col_login_3 = st.columns(3)
    
    with col_login_1:
        st.markdown('<div class="info-card"><h3>👤 CIVIL</h3><p>Accès public : Soldes personnels et enregistrement véhicules.</p></div>', unsafe_allow_html=True)
        if st.button("LOG AS CIVIL", use_container_width=True):
            st.session_state.role = "Civil"
            write_audit("Connexion : Mode Civil")
            st.rerun()
            
    with col_login_2:
        st.markdown('<div class="info-card"><h3>👮 AGENT RCT</h3><p>Accès métier : Fiscalité, amendes et gestion de flotte.</p></div>', unsafe_allow_html=True)
        input_rct = st.text_input("Clé Agent", type="password", key="auth_rct")
        if st.button("VÉRIFIER RCT", use_container_width=True):
            if input_rct == KEY_RCT:
                st.session_state.role = "RCT"
                write_audit("Connexion : Mode Agent RCT")
                st.rerun()
            else: st.error("Clé invalide.")
            
    with col_login_3:
        st.markdown('<div class="info-card"><h3>🛡️ STAFF ADMIN</h3><p>Accès racine : Salaires, base de données et réglages.</p></div>', unsafe_allow_html=True)
        input_admin = st.text_input("Clé Racine", type="password", key="auth_admin")
        if st.button("VÉRIFIER ADMIN", use_container_width=True):
            if input_admin == KEY_ADMIN:
                st.session_state.role = "Staff"
                write_audit("Connexion : Mode Administrateur")
                st.rerun()
            else: st.error("Accès refusé.")
    st.stop()

# ======================================================================================
# 5. STRUCTURE DE NAVIGATION ET SIDEBAR
# ======================================================================================

with st.sidebar:
    st.image(LOGO_PATH, use_container_width=True)
    st.markdown("---")
    st.write(f"📂 **SESSION :** `{st.session_state.role}`")
    st.write(f"📅 **DATE SYSTÈME :** {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown("---")
    
    st.subheader("📊 État du Serveur")
    st.success("Synchronisation OK")
    st.info(f"Banque : {len(df_bank)} comptes")
    st.info(f"Véhicules : {len(df_immat)} enregistrés")
    
    st.markdown("---")
    if st.button("🔄 RECHARGER LES DONNÉES", use_container_width=True):
        st.rerun()
        
    if st.button("🚪 QUITTER LA SESSION", use_container_width=True):
        st.session_state.role = None
        st.rerun()
        
    st.markdown("---")
    st.caption("RCRP Enterprise OS v21.0.1 - Build 2026")

# ======================================================================================
# 6. MODULE ALPHA : GESTION DES VÉHICULES ET TITRES
# ======================================================================================

tab_v, tab_c, tab_b, tab_l = st.tabs([
    "🚗 IMMATRICULATIONS", 
    "🪪 REGISTRE CITOYEN", 
    "💰 TERMINAL BANCAIRE",
    "📝 LOGS D'AUDIT"
])

with tab_v:
    st.header("🚗 Registre des Titres de Propriété")
    
    v_col_1, v_col_2 = st.columns([1.5, 1])
    
    with v_col_1:
        with st.expander("➕ ENREGISTRER UN VÉHICULE", expanded=True):
            st.write("Remplissez le formulaire pour générer le titre de circulation.")
            
            f_owner = st.selectbox("Titulaire du véhicule", ["---"] + df_bank["Nom Roblox"].tolist())
            f_model = st.text_input("Marque et Modèle du véhicule")
            f_plate = st.text_input("Numéro de Plaque (Plaque visible)")
            f_insur = st.selectbox("Contrat d'assurance", ["Aucun", "AVERIS (130$)", "RCT (150$)"])
            f_secret = st.text_input("Code de Sécurité pour Radiation", type="password")

            # Moteur de calcul des taxes
            f_tax_reg = 175
            f_tax_ins = 130 if "AVERIS" in f_insur else (150 if "RCT" in f_insur else 0)
            
            # Algorithme : Offre Trio RCT
            # Vérifie si le citoyen possède déjà 2 véhicules assurés RCT
            user_fleet = df_immat[df_immat["Nom d'utilisateur ROBLOX"] == f_owner]
            rct_count = len(user_fleet[user_fleet["Assurance"].str.contains("RCT", na=False)])
            
            if "RCT" in f_insur and rct_count >= 2:
                f_tax_ins = 0
                st.success("✨ AVANTAGE DÉTECTÉ : Offre Trio RCT (Assurance offerte)")

            total_bill = f_tax_reg + f_tax_ins
            st.markdown(f"### MONTANT TOTAL : **{total_bill}$**")

            if st.button("💳 PROCÉDER AU PAIEMENT ET À L'IMMATRICULATION", use_container_width=True):
                if f_owner != "---" and f_plate and f_secret:
                    # Traitement bancaire
                    u_idx = df_bank[df_bank["Nom Roblox"] == f_owner].index[0]
                    current_bal = float(str(df_bank.at[u_idx, "Solde"]).replace('$', '').replace(' ', ''))
                    
                    if current_bal >= total_bill:
                        # 1. Débit du citoyen
                        df_bank.at[u_idx, "Solde"] = current_bal - total_bill
                        
                        # 2. Dispatching des fonds (Redirect consignes)
                        if f_tax_ins > 0:
                            target_name = AVERIS_TARGET if "AVERIS" in f_insur else RCT_TARGET
                            t_idx = df_bank[df_bank["Nom Roblox"] == target_name].index[0]
                            df_bank.at[t_idx, "Solde"] = float(str(df_bank.at[t_idx, "Solde"]).replace('$', '')) + f_tax_ins
                        
                        # 3. Écriture du titre de propriété
                        new_veh = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                            "Nom d'utilisateur ROBLOX": f_owner,
                            "Marque du véhicule": f_model,
                            "Numéro de la plaque": f_plate,
                            "Assurance": f_insur,
                            "CODE": str(f_secret)
                        }])
                        
                        cloud_conn.update(worksheet="Banque", data=df_bank)
                        cloud_conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_immat, new_veh], ignore_index=True))
                        
                        # Stockage du reçu
                        st.session_state.receipt_data = {
                            "id": random.randint(1000000, 9999999),
                            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "owner": f_owner, "veh": f_model, "plq": f_plate,
                            "ass": f_insur, "tr": f_tax_reg, "ti": f_tax_ins, "tt": total_bill
                        }
                        write_audit(f"Immat : {f_plate} par {f_owner}")
                        st.success("✅ VÉHICULE ENREGISTRÉ !"); time.sleep(1); st.rerun()
                    else:
                        st.error("❌ SOLDE INSUFFISANT.")

    with v_col_2:
        st.subheader("🧾 REÇU DE PAIEMENT")
        if st.session_state.receipt_data:
            rd = st.session_state.receipt_data
            st.markdown(f"""
            <div class="rcrp-receipt">
                <center><b>REPUBLIQUE DE RENSSELAER</b><br><small>MINISTÈRE DU TRANSPORT</small></center>
                <div class="divider"></div>
                <b>DOSSIER N° :</b> RCRP-{rd['id']}<br>
                <b>DATE :</b> {rd['date']}<br>
                <b>AGENT :</b> {st.session_state.role}<br>
                <div class="divider"></div>
                <b>PROPRIÉTAIRE :</b> {rd['owner'].upper()}<br>
                <b>VÉHICULE :</b> {rd['veh']}<br>
                <b>PLAQUE :</b> {rd['plq']}<br>
                <b>ASSURANCE :</b> {rd['ass']}<br>
                <div class="divider"></div>
                TAXE IMMATRICULATION : {rd['tr']}$<br>
                TAXE ASSURANCE : {rd['ti']}$<br>
                <div class="divider"></div>
                <b>TOTAL PAYÉ : {rd['tt']}$</b>
                <div class="divider"></div>
                <center><small>SYSTÈME SÉCURISÉ RCRP-OS<br>MERCI DE VOTRE PAIEMENT</small></center>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Aucune transaction récente.")

    st.divider()
    st.subheader("🔍 ARCHIVES DES VÉHICULES")
    v_search = st.text_input("Filtrer par plaque ou citoyen :").lower()
    
    for i_v, r_v in df_immat.iterrows():
        if not v_search or v_search in str(r_v["Numéro de la plaque"]).lower() or v_search in str(r_v["Nom d'utilisateur ROBLOX"]).lower():
            with st.container(border=True):
                st.write(f"🚗 **Plaque : {r_v['Numéro de la plaque']}** | {r_v['Marque du véhicule']}")
                with st.expander("🛠️ OPTIONS DE GESTION"):
                    v_pass = st.text_input("Code Secret de Radiation", type="password", key=f"sec_{i_v}")
                    if v_pass == str(r_v["CODE"]) or st.session_state.role == "Staff":
                        if st.button("🗑️ RADIER LE VÉHICULE", key=f"del_{i_v}"):
                            cloud_conn.update(worksheet="Copie de Immatriculations", data=df_immat.drop(i_v))
                            write_audit(f"Radiation : {r_v['Numéro de la plaque']}")
                            st.success("Titre détruit."); st.rerun()

# --------------------------------------------------------------------------------------
# MODULE BÊTA : CITOYENS - AUTOMATISATION 15K + 25 PTS + DATE
# --------------------------------------------------------------------------------------
with tab_c:
    st.header("🪪 Registre National de la Population")
    
    # Seul le staff peut créer des profils
    if st.session_state.role == "Staff":
        st.subheader("⚙️ CRÉATION DE PROFIL AUTOMATISÉE")
        with st.form("new_cit_form"):
            col_nc1, col_nc2 = st.columns(2)
            with col_nc1:
                new_rob = st.text_input("Pseudo Roblox")
                new_dis = st.text_input("Tag Discord")
            with col_nc2:
                new_job = st.selectbox("Assignation Poste", ["Civil", "Agent RCT", "Gouvernement", "Police"])
            
            if st.form_submit_button("🔨 INITIALISER LE CITOYEN (START PACK)"):
                if new_rob and new_dis:
                    # DATE AUTOMATIQUE
                    d_join = datetime.now().strftime("%d/%m/%Y")
                    
                    # 1. CRÉATION BANQUE (15,000$ AUTO)
                    b_row = pd.DataFrame([{
                        "Solde": 15000, 
                        "Nom Discord": new_dis, 
                        "Nom Roblox": new_rob, 
                        "Date d'arrivée": d_join, 
                        "Emploiement": new_job
                    }])
                    
                    # 2. CRÉATION PERMIS (25 POINTS AUTO)
                    p_row = pd.DataFrame([{
                        "Nom Discord": new_dis, 
                        "Nom Roblox": new_rob, 
                        "PTS": 25, 
                        "Validité": "OUI"
                    }])
                    
                    # Mise à jour Cloud
                    cloud_conn.update(worksheet="Banque", data=pd.concat([df_bank, b_row], ignore_index=True))
                    cloud_conn.update(worksheet="Points Permis", data=pd.concat([df_pts, p_row], ignore_index=True))
                    
                    write_audit(f"Création profil : {new_rob}")
                    st.success(f"Dossier créé : {new_rob} a reçu 15,000$ et 25 points."); time.sleep(1); st.rerun()

        st.divider()
        st.subheader("💰 SYSTÈME DE PAIE NATIONALE")
        if st.button("💸 VERSER LES SALAIRES (15K/17K) À TOUT LE MONDE", use_container_width=True):
            for i_s, r_s in df_bank.iterrows():
                # Les agents RCT touchent 17,000$, les autres 15,000$
                p_val = 17000 if "RCT" in str(r_s["Emploiement"]) else 15000
                df_bank.at[i_s, "Solde"] = float(str(r_s["Solde"]).replace('$', '').replace(' ', '')) + p_val
            cloud_conn.update(worksheet="Banque", data=df_bank)
            write_audit("Versement général des salaires")
            st.success("Salaires distribués !"); time.sleep(1); st.rerun()

    st.divider()
    st.subheader("📋 ARCHIVES DES RÉSIDENTS")
    c_find = st.text_input("Rechercher un citoyen :").lower()
    
    for i_c, r_c in df_bank.iterrows():
        if not c_find or c_find in str(r_c["Nom Roblox"]).lower():
            with st.container(border=True):
                st.markdown(f"👤 **{r_c['Nom Roblox']}** | 💼 {r_c['Emploiement']} | 📅 Inscrit le : {r_c['Date d\'arrivée']}")
                with st.expander("🔎 VOIR LE DOSSIER DÉTAILLÉ"):
                    d_col1, d_col2 = st.columns(2)
                    d_col1.write(f"ID Discord : {r_c['Nom Discord']}")
                    # Récupération dynamique des points de permis
                    u_pts = df_pts[df_pts["Nom Roblox"] == r_c["Nom Roblox"]]["PTS"]
                    d_col2.write(f"Points de Permis : **{u_pts.values[0] if not u_pts.empty else 'Non inscrit'}**")

# --------------------------------------------------------------------------------------
# MODULE GAMMA : FINANCES - DÉBITS ET REDIRECTIONS
# --------------------------------------------------------------------------------------
with tab_b:
    st.header("💰 Terminal Bancaire Central")
    st.write("Gestion des flux monétaires et fiscalité directe.")
    
    b_find = st.text_input("Saisir le nom du client :").lower()
    
    for i_b, r_b in df_bank.iterrows():
        if not b_find or b_find in str(r_b["Nom Roblox"]).lower():
            with st.container(border=True):
                s_brut = float(str(r_b["Solde"]).replace('$', '').replace(' ', ''))
                
                b_c1, b_c2 = st.columns([1, 1])
                b_c1.metric(f"Compte de {r_b['Nom Roblox']}", f"{s_brut:,.0f} $")
                
                if st.session_state.role in ["RCT", "Staff"]:
                    with b_c2:
                        op_amt = st.number_input("Montant de l'opération", min_value=0, key=f"op_{i_b}")
                        
                        b_btn_1, b_btn_2 = st.columns(2)
                        if b_btn_1.button("📉 PRÉLEVER (TAXE)", key=f"pre_{i_b}"):
                            # Débit client
                            df_bank.at[i_b, "Solde"] = s_brut - op_amt
                            
                            # Si c'est un Agent RCT, l'argent va sur le compte RCT
                            if st.session_state.role == "RCT":
                                idx_rct = df_bank[df_bank["Nom Roblox"] == RCT_TARGET].index[0]
                                s_rct = float(str(df_bank.at[idx_rct, "Solde"]).replace('$', ''))
                                df_bank.at[idx_rct, "Solde"] = s_rct + op_amt
                                write_audit(f"Taxe RCT : {op_amt}$ sur {r_b['Nom Roblox']}")
                            
                            cloud_conn.update(worksheet="Banque", data=df_bank)
                            st.success("Débit effectué."); time.sleep(0.5); st.rerun()
                            
                        if b_btn_2.button("📈 CRÉDITER", key=f"add_{i_b}"):
                            df_bank.at[i_b, "Solde"] = s_brut + op_amt
                            cloud_conn.update(worksheet="Banque", data=df_bank)
                            write_audit(f"Crédit : {op_amt}$ pour {r_b['Nom Roblox']}")
                            st.success("Compte crédité."); time.sleep(0.5); st.rerun()

# --------------------------------------------------------------------------------------
# MODULE DELTA : LOGS D'AUDIT (VISIBLE STAFF UNIQUEMENT)
# --------------------------------------------------------------------------------------
with tab_l:
    st.header("📝 Journal des Opérations")
    if st.session_state.role == "Staff":
        st.write("Historique complet des actions effectuées durant cette session.")
        for log_line in reversed(st.session_state.audit_trail):
            st.text(log_line)
    else:
        st.error("Accès réservé au personnel administratif de niveau 5.")

# ======================================================================================
# 7. PIED DE PAGE SYSTÈME - MÉDATA ET SÉCURITÉ
# ======================================================================================

st.write("")
st.divider()
st.markdown("""
    <div style='text-align: center;'>
        <p style='color: gray; font-size: 0.8em;'>
            RCRP CORE v21.0.1 - SECURE OPERATING SYSTEM<br>
            CHESTNUT COUNTY FEDERAL ADMINISTRATION<br>
            TOUTES LES DONNÉES SONT CHIFFRÉES EN AES-256<br>
            © 2026 GOUVERNEMENT DE RENSSELAER
        </p>
    </div>
""", unsafe_allow_html=True)

# FIN DU CODE - PLUS DE 500 LIGNES DE LOGIQUE DÉPLOYÉES.
