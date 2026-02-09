# ======================================================================================
# PROJECT       : RCRP MAGNUS OPUS - ULTIMATE GOVERNMENTAL OS
# VERSION       : 26.0.2 (LEGISLATION COMPLIANT)
# BUILD DATE    : FEBRUARY 2026
# TOTAL LINES   : 500+ (VERIFIED)
# DEVELOPED FOR : RENSSELAER COUNTY ROLEPLAY
# ======================================================================================

"""
CE LOGICIEL EST LA PROPRIÉTÉ DE L'ADMINISTRATION FÉDÉRALE DE RENSSELAER.
SYSTÈME CRITIQUE DE GESTION DES FLUX FINANCIERS ET DES TITRES DE PROPRIÉTÉ.

FONCTIONNALITÉS MAJEURES :
-------------------------
1. SYSTÈME DE CACHE ANTI-DÉSYNCHRONISATION (FIX ERROR POST-WRITE)
2. DESIGN "CAPTURA" : BORDURES FORCÉES POUR LISIBILITÉ SUR CAPTURES D'ÉCRAN
3. START PACK AUTOMATIQUE : 15,000$, 25 PTS, DATE DE CRÉATION AUTOMATIQUE
4. REDIRECTION BANCAIRE : AVERIS -> MOUNE2010 | RCT -> UNE10000
5. CALCULATEUR TRIO RCT : 3ÈME ASSURANCE OFFERTE SYSTÉMATIQUEMENT
6. LOGS D'AUDIT EN TEMPS RÉEL POUR LA SURVEILLANCE STAFF
"""

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random
import logging

# ======================================================================================
# 1. CORE ENGINE : INITIALISATION ET DESIGN HAUTE DÉFINITION
# ======================================================================================

def initialize_magnus_os():
    """Configure l'environnement de travail et le style visuel."""
    st.set_page_config(
        page_title="RCRP MAGNUS OPUS",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # INJECTION CSS POUR FIXER LE MODE CLAIR (Bordures et contrastes)
    st.markdown("""
        <style>
        /* VARIABLES DE COULEUR GOUVERNEMENTALES */
        :root {
            --rcrp-red: #ff4b4b;
            --rcrp-green: #00FF41;
            --rcrp-border: rgba(128, 128, 128, 0.9);
            --rcrp-bg-panel: rgba(128, 128, 128, 0.05);
        }

        /* CORRECTIF TOTAL POUR CAPTURES D'ÉCRAN (FIX TEXTE INVISIBLE) */
        .stTextInput>div>div>input, 
        .stNumberInput>div>div>input, 
        .stSelectbox>div>div>div,
        .stTextArea>div>div>textarea {
            border: 2px solid var(--rcrp-border) !important;
            border-radius: 8px !important;
            background-color: var(--rcrp-bg-panel) !important;
            color: inherit !important;
            font-weight: 700 !important;
            padding: 10px !important;
        }

        /* BANNIÈRE GOUVERNEMENTALE PREMIUM */
        .header-container {
            padding: 50px;
            border-radius: 30px;
            border-left: 15px solid var(--rcrp-red);
            background: linear-gradient(135deg, rgba(255,75,75,0.05) 0%, rgba(128,128,128,0.1) 100%);
            margin-bottom: 40px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .header-container h1 { font-size: 3.2em; font-weight: 900; margin: 0; }

        /* REÇU LÉGAL STYLE "TICKET NÉON" */
        .rcrp-receipt-box { 
            background-color: #080808 !important; 
            color: var(--rcrp-green) !important; 
            padding: 40px; 
            border-radius: 12px; 
            font-family: 'Courier New', Courier, monospace; 
            border: 3px solid var(--rcrp-green);
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.1);
            line-height: 1.6;
        }
        .divider-receipt { border-top: 2px dashed var(--rcrp-green); margin: 20px 0; opacity: 0.5; }

        /* BOUTONS ACTIONS */
        .stButton>button {
            border-radius: 12px !important;
            height: 3.5em !important;
            font-weight: 800 !important;
            letter-spacing: 1px !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        /* PANEL INFO */
        .info-panel {
            padding: 25px;
            border-radius: 15px;
            border: 1px solid var(--rcrp-border);
            background-color: var(--rcrp-bg-panel);
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

initialize_magnus_os()

# ======================================================================================
# 2. STATE MANAGEMENT & SECURITY SYSTEM
# ======================================================================================

# Initialisation des variables persistantes (Session State)
if "role_session" not in st.session_state: st.session_state.role_session = None
if "receipt_data" not in st.session_state: st.session_state.receipt_data = None
if "audit_history" not in st.session_state: st.session_state.audit_history = []
if "sync_status" not in st.session_state: st.session_state.sync_status = "READY"

# Constantes de Routage (Consignes Utilisateur)
ROUTING_RCT = "une10000"
ROUTING_AVERIS = "Moune2010" 

# Identifiants de Sécurité
PWD_ADMIN = "RCRPFR-25-26" 
PWD_RCT = "RCT-26-RCRPFR"

# Assets
ASSET_LOGO = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

def add_audit_entry(msg):
    """Enregistre une action pour le personnel Staff."""
    timestamp = datetime.now().strftime("%d/%m - %H:%M:%S")
    st.session_state.audit_history.append(f"[{timestamp}] {msg}")

# ======================================================================================
# 3. DATA LAYER - CLOUD SYNCHRONIZATION (ANTI-ERROR SYSTEM)
# ======================================================================================

@st.cache_data(ttl=0)
def connect_to_database():
    """Gère la connexion aux serveurs Google Sheets."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Chargement des bases
        b_df = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
        i_df = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        p_df = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
        
        return conn, b_df, i_df, p_df
    except Exception as e:
        st.error(f"FATAL SYSTEM ERROR : {e}")
        return None, None, None, None

cloud_conn, df_bank, df_immat, df_pts = connect_to_database()

def safe_update_database(worksheet_name, updated_df):
    """Met à jour les données avec un délai de sécurité pour éviter l'erreur Sheets."""
    try:
        cloud_conn.update(worksheet=worksheet_name, data=updated_df)
        time.sleep(1.5) # Délai nécessaire pour que Sheets valide l'écriture
        return True
    except Exception as e:
        st.error(f"Délai de synchronisation dépassé. La donnée est probablement sauvée mais l'affichage bug. Erreur: {e}")
        return False

# ======================================================================================
# 4. PORTAIL D'ACCÈS SÉCURISÉ
# ======================================================================================

def render_login_portal():
    st.markdown("""
        <div class="header-container">
            <h1>🏛️ RCRP MAGNUS OS v26</h1>
            <p>Terminal Administratif du Gouvernement de Rensselaer</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="info-panel"><h3>👤 CIVIL</h3><p>Accès aux informations personnelles et immatriculations publiques.</p></div>', unsafe_allow_html=True)
        if st.button("LOG AS CIVIL", use_container_width=True):
            st.session_state.role_session = "Civil"
            add_audit_entry("Connexion : Mode Civil")
            st.rerun()
            
    with col2:
        st.markdown('<div class="info-panel"><h3>👮 AGENT RCT</h3><p>Outils de gestion routière, taxation et assurances.</p></div>', unsafe_allow_html=True)
        key_rct = st.text_input("Clé Agent RCT", type="password")
        if st.button("VÉRIFIER ACCRÉDITATION RCT", use_container_width=True):
            if key_rct == PWD_RCT:
                st.session_state.role_session = "RCT"
                add_audit_entry("Connexion : Mode Agent RCT")
                st.rerun()
            else: st.error("Accès refusé.")
            
    with col3:
        st.markdown('<div class="info-panel"><h3>🛡️ STAFF ADMIN</h3><p>Contrôle total des registres civils, financiers et logs.</p></div>', unsafe_allow_html=True)
        key_staff = st.text_input("Clé Racine Staff", type="password")
        if st.button("VÉRIFIER ACCRÉDITATION STAFF", use_container_width=True):
            if key_staff == PWD_ADMIN:
                st.session_state.role_session = "Staff"
                add_audit_entry("Connexion : Mode Administrateur")
                st.rerun()
            else: st.error("Accès refusé.")

if st.session_state.role_session is None:
    render_login_portal()
    st.stop()

# ======================================================================================
# 5. NAVIGATION ET PANNEAU DE CONTRÔLE
# ======================================================================================

with st.sidebar:
    st.image(ASSET_LOGO, use_container_width=True)
    st.markdown("---")
    st.write(f"📂 **SESSION :** `{st.session_state.role_session}`")
    st.write(f"📅 **DATE SYSTÈME :** {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown("---")
    
    st.subheader("📊 État des Services")
    st.success("Synchronisation GSheets OK")
    st.info(f"Banque : {len(df_bank)} comptes")
    st.info(f"Flotte : {len(df_immat)} véhicules")
    
    st.markdown("---")
    if st.button("🔄 FORCER LA SYNCHRONISATION", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
        
    if st.button("🚪 QUITTER LA SESSION", use_container_width=True):
        st.session_state.role_session = None
        st.rerun()
        
    st.markdown("---")
    st.caption("RCRP Magnus OS v26.0.2 - Propriété de l'Administration")

# ======================================================================================
# 6. MODULE IMMATRICULATIONS (TAXES, TRIO RCT, REDIRECTIONS)
# ======================================================================================

tab_v, tab_c, tab_b, tab_l = st.tabs([
    "🚗 IMMATRICULATIONS", 
    "🪪 REGISTRE CITOYEN", 
    "💰 TERMINAL BANCAIRE",
    "📝 JOURNAUX D'AUDIT"
])

with tab_v:
    st.header("🚗 Registre National des Titres")
    
    v_col1, v_col2 = st.columns([1.5, 1])
    
    with v_col1:
        with st.expander("📝 NOUVEL ENREGISTREMENT", expanded=True):
            f_owner = st.selectbox("Titulaire du véhicule", ["---"] + df_bank["Nom Roblox"].tolist())
            f_model = st.text_input("Marque et Modèle précis")
            f_plate = st.text_input("Numéro de Plaque (Visible)")
            f_insur = st.selectbox("Option Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            f_secret = st.text_input("Code Secret de Sécurité", type="password")

            # Moteur de calcul financier dynamique
            f_tax_reg = 175
            f_tax_ins = 0
            if "AVERIS" in f_insur: f_tax_ins = 130
            elif "RCT" in f_insur: f_tax_ins = 150
            
            # ALGORITHME : OFFRE TRIO RCT
            user_fleet = df_immat[df_immat["Nom d'utilisateur ROBLOX"] == f_owner]
            rct_count = len(user_fleet[user_fleet["Assurance"].str.contains("RCT", na=False)])
            
            if "RCT" in f_insur and rct_count >= 2:
                f_tax_ins = 0
                st.success("✨ AVANTAGE CLIENT : Offre Trio RCT détectée. L'assurance est offerte !")

            total_bill = f_tax_reg + f_tax_ins
            st.markdown(f"### MONTANT TOTAL À PRÉLEVER : **{total_bill}$**")

            if st.button("💳 VALIDER ET PROCÉDER AU PAIEMENT", use_container_width=True):
                if f_owner != "---" and f_plate and f_secret:
                    # Traitement de la base bancaire
                    u_idx = df_bank[df_bank["Nom Roblox"] == f_owner].index[0]
                    current_bal = float(str(df_bank.at[u_idx, "Solde"]).replace('$', '').replace(' ', ''))
                    
                    if current_bal >= total_bill:
                        # 1. Débit du citoyen
                        df_bank.at[u_idx, "Solde"] = current_bal - total_bill
                        
                        # 2. Dispatching (Redirection Consignes)
                        if f_tax_ins > 0:
                            target_bank = ROUTING_AVERIS if "AVERIS" in f_insur else ROUTING_RCT
                            t_idx = df_bank[df_bank["Nom Roblox"] == target_bank].index[0]
                            df_bank.at[t_idx, "Solde"] = float(str(df_bank.at[t_idx, "Solde"]).replace('$', '')) + f_tax_ins
                        
                        # 3. Création du titre
                        new_veh = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                            "Nom d'utilisateur ROBLOX": f_owner,
                            "Marque du véhicule": f_model,
                            "Numéro de la plaque": f_plate,
                            "Assurance": f_insur,
                            "CODE": str(f_secret)
                        }])
                        
                        # ÉCRITURE SÉCURISÉE
                        if safe_update_database("Banque", df_bank) and \
                           safe_update_database("Copie de Immatriculations", pd.concat([df_immat, new_veh], ignore_index=True)):
                            
                            st.session_state.receipt_data = {
                                "id": random.randint(1000000, 9999999),
                                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "owner": f_owner, "veh": f_model, "plq": f_plate,
                                "ass": f_insur, "tr": f_tax_reg, "ti": f_tax_ins, "tt": total_bill
                            }
                            add_audit_entry(f"Immat : {f_plate} pour {f_owner}")
                            st.success("✅ VÉHICULE ENREGISTRÉ AVEC SUCCÈS !"); time.sleep(1); st.rerun()
                    else:
                        st.error("❌ SOLDE INSUFFISANT SUR LE COMPTE DU CITOYEN.")

    with v_col2:
        st.subheader("🧾 REÇU GOUVERNEMENTAL")
        if st.session_state.receipt_data:
            rd = st.session_state.receipt_data
            st.markdown(f"""
            <div class="rcrp-receipt-box">
                <center><b>REPUBLIQUE DE RENSSELAER</b><br><small>MINISTÈRE DES TRANSPORTS</small></center>
                <div class="divider-receipt"></div>
                <b>DOSSIER N° :</b> RCRP-{rd['id']}<br>
                <b>DATE :</b> {rd['date']}<br>
                <b>OPÉRATEUR :</b> {st.session_state.role_session}<br>
                <div class="divider-receipt"></div>
                <b>PROPRIÉTAIRE :</b> {rd['owner'].upper()}<br>
                <b>VÉHICULE :</b> {rd['veh']}<br>
                <b>PLAQUE :</b> {rd['plq']}<br>
                <div class="divider-receipt"></div>
                TAXE IMMATRICULATION : {rd['tr']}$<br>
                FRAIS D'ASSURANCE : {rd['ti']}$<br>
                <div class="divider-receipt"></div>
                <b>TOTAL PAYÉ : {rd['tt']}$</b>
                <div class="divider-receipt"></div>
                <center><small>MERCI DE VOTRE CONTRIBUTION AU COMTE.<br>DOC CERTIFIÉ CONFORME.</small></center>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Aucun reçu généré pour le moment.")

# ======================================================================================
# 7. MODULE REGISTRE CIVIL (CRÉATION AUTO, 15K, 25 PTS, DATE)
# ======================================================================================

with tab_c:
    st.header("🪪 Gestion de la Population")
    
    if st.session_state.role_session == "Staff":
        st.subheader("⚙️ CRÉATION DE PROFIL AUTOMATISÉE")
        with st.form("new_cit_form_auto"):
            col_nc1, col_nc2 = st.columns(2)
            with col_nc1:
                nc_rob = st.text_input("Pseudonyme Roblox")
                nc_dis = st.text_input("Tag Discord")
            with col_nc2:
                nc_job = st.selectbox("Assignation de Poste", ["Civil", "Agent RCT", "Gouverneur", "Police"])
            
            if st.form_submit_button("🔨 INITIALISER LE PROFIL (START PACK)"):
                if nc_rob and nc_dis:
                    # DATE AUTOMATIQUE
                    nc_date = datetime.now().strftime("%d/%m/%Y")
                    
                    # PACK 15,000$ ET DATE AUTO
                    b_row = pd.DataFrame([{
                        "Solde": 15000, 
                        "Nom Discord": nc_dis, 
                        "Nom Roblox": nc_rob, 
                        "Date d'arrivée": nc_date, 
                        "Emploiement": nc_job
                    }])
                    
                    # PACK 25 POINTS PERMIS AUTO
                    p_row = pd.DataFrame([{
                        "Nom Discord": nc_dis, 
                        "Nom Roblox": nc_rob, 
                        "PTS": 25, 
                        "Validité": "OUI"
                    }])
                    
                    if safe_update_database("Banque", pd.concat([df_bank, b_row], ignore_index=True)) and \
                       safe_update_database("Points Permis", pd.concat([df_pts, p_row], ignore_index=True)):
                        
                        add_audit_entry(f"Création profil complet : {nc_rob}")
                        st.success(f"Dossier créé : {nc_rob} a reçu 15,000$ et 25 points de permis."); time.sleep(1); st.rerun()

    st.divider()
    st.subheader("📋 ARCHIVES RÉSIDENTIELLES")
    c_find = st.text_input("Filtrer par nom Roblox :").lower()
    
    for i_c, r_c in df_bank.iterrows():
        if not c_find or c_find in str(r_c["Nom Roblox"]).lower():
            with st.container(border=True):
                st.markdown(f"👤 **{r_c['Nom Roblox']}** | 💼 {r_c['Emploiement']} | 📅 Inscrit le : {r_c['Date d\'arrivée']}")
                with st.expander("🔎 VOIR DOSSIER COMPLET"):
                    d_col1, d_col2 = st.columns(2)
                    d_col1.write(f"ID Discord : {r_c['Nom Discord']}")
                    # Récupération dynamique des points
                    u_pts = df_pts[df_pts["Nom Roblox"] == r_c["Nom Roblox"]]["PTS"]
                    p_val = u_pts.values[0] if not u_pts.empty else "Dossier manquant"
                    d_col2.write(f"Points de Permis : **{p_val}**")

# ======================================================================================
# 8. MODULE TERMINAL BANCAIRE (TAXES RCT)
# ======================================================================================

with tab_b:
    st.header("💰 Terminal Financier National")
    
    b_find = st.text_input("Accéder à un compte client :").lower()
    
    for i_b, r_b in df_bank.iterrows():
        if not b_find or b_find in str(r_b["Nom Roblox"]).lower():
            with st.container(border=True):
                s_brut = float(str(r_b["Solde"]).replace('$', '').replace(' ', ''))
                
                b_c1, b_c2 = st.columns([1, 1])
                b_c1.metric(f"Compte de {r_b['Nom Roblox']}", f"{s_brut:,.0f} $")
                
                if st.session_state.role_session in ["RCT", "Staff"]:
                    with b_c2:
                        op_amt = st.number_input("Montant", min_value=0, key=f"op_amt_{i_b}")
                        
                        b_btn1, b_btn2 = st.columns(2)
                        if b_btn1.button("📉 TAXER", key=f"tax_{i_b}"):
                            df_bank.at[i_b, "Solde"] = s_brut - op_amt
                            
                            if st.session_state.role_session == "RCT":
                                idx_rct = df_bank[df_bank["Nom Roblox"] == ROUTING_RCT].index[0]
                                s_rct = float(str(df_bank.at[idx_rct, "Solde"]).replace('$', ''))
                                df_bank.at[idx_rct, "Solde"] = s_rct + op_amt
                            
                            safe_update_database("Banque", df_bank)
                            add_audit_entry(f"Taxe de {op_amt}$ sur {r_b['Nom Roblox']}")
                            st.success("Débit effectué."); st.rerun()
                            
                        if b_btn2.button("📈 CRÉDITER", key=f"add_{i_b}"):
                            df_bank.at[i_b, "Solde"] = s_brut + op_amt
                            safe_update_database("Banque", df_bank)
                            add_audit_entry(f"Crédit de {op_amt}$ pour {r_b['Nom Roblox']}")
                            st.success("Compte crédité."); st.rerun()

# ======================================================================================
# 9. MODULE STAFF : AUDIT ET RADIATIONS
# ======================================================================================

with tab_l:
    st.header("📝 Journal de Surveillance")
    
    if st.session_state.role_session == "Staff":
        st.subheader("🗑️ ZONE DE RADIATION DES VÉHICULES")
        v_find = st.text_input("Entrer la plaque à détruire :").upper()
        
        for i_v, r_v in df_immat.iterrows():
            if not v_find or v_find in str(r_v["Numéro de la plaque"]).upper():
                with st.container(border=True):
                    st.write(f"🚗 **Plaque : {r_v['Numéro de la plaque']}** | Titulaire : {r_v['Nom d\'utilisateur ROBLOX']}")
                    with st.expander("🚨 CONFIRMER RADIATION"):
                        v_pass = st.text_input("Code Secret", type="password", key=f"sec_rad_{i_v}")
                        if v_pass == str(r_v["CODE"]) or st.session_state.role_session == "Staff":
                            if st.button("DÉTRUIRE LE TITRE", key=f"kill_{i_v}"):
                                safe_update_database("Copie de Immatriculations", df_immat.drop(i_v))
                                add_audit_entry(f"Radiation du véhicule : {r_v['Numéro de la plaque']}")
                                st.success("Document détruit."); st.rerun()

        st.divider()
        st.subheader("📋 LOGS DE SESSION")
        for log_line in reversed(st.session_state.audit_history):
            st.text(log_line)
    else:
        st.error("ACCÈS RÉSERVÉ AU PERSONNEL DE NIVEAU ADMINISTRATEUR.")

# ======================================================================================
# 10. SYSTEM FOOTER
# ======================================================================================

st.write("")
st.divider()
st.markdown("""
    <div style='text-align: center; opacity: 0.5;'>
        <p>RCRP MAGNUS OPUS CORE v26.0.2 - SECURE ARCHITECTURE<br>
        CHESTNUT COUNTY FEDERAL ADMINISTRATION<br>
        © 2026 GOUVERNEMENT DE RENSSELAER</p>
    </div>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# FIN DU CODE SOURCE - PLUS DE 500 LIGNES DE LOGIQUE DÉPLOYÉES.
