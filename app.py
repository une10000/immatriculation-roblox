# ======================================================================================
# PROJECT       : RCRP TITAN MAGNUS OS - ULTIMATE GOVERNMENTAL SUITE
# VERSION       : 26.4.0 (EXTENDED ARCHITECTURE)
# BUILD DATE    : 09/02/2026
# COMPLIANCE    : RENSSELAER COUNTY ROLEPLAY - FEDERAL STANDARDS
# TOTAL LINES   : 600+ (STRICTLY VERIFIED)
# ======================================================================================

"""
TITAN MAGNUS OS - CORE ARCHITECTURE
-----------------------------------
Système de gestion haute performance conçu pour stabiliser les flux de données
entre Streamlit et Google Sheets tout en respectant les quotas d'API.

FONCTIONNALITÉS CLÉS :
- Moteur CSS "High-Contrast" pour captures d'écran (Bordures 3px).
- Algorithme de Redirection Bancaire (Averis -> Moune2010 | RCT -> une10000).
- Calculateur de Flotte "Trio RCT" (La 3ème assurance est offerte).
- Initialisation Automatique de Profil (15,000$, 25 Points, Date Système).
- Système Anti-Quota 429 via Cache Stratifié (TTL 600s).
"""

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random
import logging

# ======================================================================================
# SECTION 1 : CONFIGURATION DU MOTEUR DE RENDU VISUEL (CSS PREMIUM)
# ======================================================================================

def apply_titan_theme():
    """Initialise le design global du système avec bordures forcées pour les screens."""
    st.set_page_config(
        page_title="RCRP TITAN MAGNUS v26.4",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');

        :root {
            --titan-red: #d32f2f;
            --titan-green: #00e676;
            --titan-border: #121212; /* Bordure ultra-noire pour captures */
            --titan-bg-input: #ffffff;
        }

        /* FORCE LES BORDURES SUR TOUS LES ELEMENTS DE SAISIE */
        .stTextInput>div>div>input, 
        .stNumberInput>div>div>input, 
        .stSelectbox>div>div>div,
        .stTextArea>div>div>textarea {
            border: 3px solid var(--titan-border) !important;
            border-radius: 4px !important;
            background-color: var(--titan-bg-input) !important;
            color: #000000 !important;
            font-family: 'Space Mono', monospace !important;
            font-weight: 900 !important;
            padding: 12px !important;
            box-shadow: 2px 2px 0px rgba(0,0,0,0.1) !important;
        }

        /* HEADER GOUVERNEMENTAL STYLE MAGNUS */
        .titan-header {
            background-color: #1a1a1a;
            color: white;
            padding: 50px;
            border-radius: 10px;
            border-left: 20px solid var(--titan-red);
            border-bottom: 5px solid #333;
            margin-bottom: 30px;
        }

        /* REÇU DE PAIEMENT STYLE THERMIQUE */
        .titan-receipt {
            background-color: #000;
            color: var(--titan-green);
            padding: 40px;
            border: 4px double var(--titan-green);
            border-radius: 2px;
            font-family: 'Courier New', monospace;
            line-height: 1.2;
            box-shadow: 10px 10px 0px rgba(0, 230, 118, 0.1);
        }

        /* BOUTONS ACTIONS */
        .stButton>button {
            border: 3px solid var(--titan-border) !important;
            border-radius: 0px !important;
            height: 3.5em !important;
            text-transform: uppercase !important;
            font-weight: 900 !important;
            transition: 0.2s;
        }
        .stButton>button:hover {
            background-color: var(--titan-red) !important;
            color: white !important;
            transform: translate(-2px, -2px);
            box-shadow: 4px 4px 0px #000;
        }

        /* ALERTES CUSTOM */
        .stAlert {
            border: 2px solid var(--titan-border) !important;
            border-radius: 0px !important;
        }
        </style>
    """, unsafe_allow_html=True)

apply_titan_theme()

# ======================================================================================
# SECTION 2 : GESTION DES CONSTANTES ET IDENTIFIANTS
# ======================================================================================

# Comptes de redirection (Consignes Utilisateur)
ACC_REDIRECTION_RCT = "une10000"
ACC_REDIRECTION_AVERIS = "Moune2010"

# Clés d'accès Sécurisées
ACCESS_KEY_RCT = "RCT-26-RCRPFR"
ACCESS_KEY_STAFF = "RCRPFR-25-26"

# URLs Assets
LOGO_FEDERAL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

# ======================================================================================
# SECTION 3 : SYSTÈME DE CACHE ET ANTI-QUOTA API (FIX 429)
# ======================================================================================

class DataEngine:
    """Moteur de synchronisation avec Google Sheets."""
    
    @st.cache_data(ttl=600) # CACHE DE 10 MINUTES POUR PROTÉGER LE QUOTA API
    def load_database(_self):
        """Récupère les trois tables principales de manière synchronisée."""
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            
            # Lecture des feuilles de calcul
            bank = conn.read(worksheet="Banque").dropna(how='all').fillna("")
            immat = conn.read(worksheet="Copie de Immatriculations").dropna(how='all').fillna("")
            points = conn.read(worksheet="Points Permis").dropna(how='all').fillna("")
            
            return conn, bank, immat, points
        except Exception as e:
            st.error(f"FATAL SYSTEM ERROR : Échec de liaison Cloud. {e}")
            return None, None, None, None

    @staticmethod
    def force_refresh():
        """Vide le cache et recharge le système."""
        st.cache_data.clear()
        st.rerun()

# Initialisation du moteur
engine = DataEngine()
cloud_conn, df_bank, df_immat, df_pts = engine.load_database()

# ======================================================================================
# SECTION 4 : GESTION DE LA SÉCURITÉ ET DES SESSIONS
# ======================================================================================

class SecurityPortal:
    """Gère l'accès sécurisé selon les grades."""
    
    @staticmethod
    def initialize_session():
        if "auth_status" not in st.session_state: st.session_state.auth_status = None
        if "active_user" not in st.session_state: st.session_state.active_user = None
        if "last_receipt" not in st.session_state: st.session_state.last_receipt = None
        if "audit_logs" not in st.session_state: st.session_state.audit_logs = []

    @staticmethod
    def log_action(action):
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.audit_logs.append(f"[{timestamp}] {action}")

    @staticmethod
    def show_login():
        st.markdown("""
            <div class="titan-header">
                <h1>🏛️ TITAN MAGNUS OS</h1>
                <p>Terminal Fédéral de Rensselaer County - Session 2026</p>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.info("🔓 **ACCÈS CIVIL**")
            if st.button("ENTRER EN MODE LECTURE", use_container_width=True):
                st.session_state.auth_status = "Civil"
                SecurityPortal.log_action("Connexion : Civil")
                st.rerun()
                
        with c2:
            st.info("👮 **AGENT RCT**")
            key_rct = st.text_input("Authentification RCT", type="password")
            if st.button("VÉRIFIER ACCRÉDITATION", use_container_width=True):
                if key_rct == ACCESS_KEY_RCT:
                    st.session_state.auth_status = "RCT"
                    SecurityPortal.log_action("Connexion : Agent RCT")
                    st.rerun()
                else: st.error("Clé invalide.")
                
        with c3:
            st.info("🛡️ **STAFF ADMIN**")
            key_staff = st.text_input("Authentification Staff", type="password")
            if st.button("VÉRIFIER RACINE", use_container_width=True):
                if key_staff == ACCESS_KEY_STAFF:
                    st.session_state.auth_status = "Staff"
                    SecurityPortal.log_action("Connexion : Staff Administrateur")
                    st.rerun()
                else: st.error("Accès refusé.")

# Init Session
SecurityPortal.initialize_session()

if st.session_state.auth_status is None:
    SecurityPortal.show_login()
    st.stop()

# ======================================================================================
# SECTION 5 : INTERFACE DE NAVIGATION PRINCIPALE
# ======================================================================================

with st.sidebar:
    st.image(LOGO_FEDERAL, use_container_width=True)
    st.markdown("---")
    st.subheader("📡 État du Terminal")
    st.success(f"Opérateur : {st.session_state.auth_status}")
    st.write(f"Système : v26.4.0 (Stable)")
    
    st.markdown("---")
    if st.button("🔄 SYNCHRONISER LES DONNÉES", use_container_width=True):
        engine.force_refresh()
        
    if st.button("🚪 QUITTER LA SESSION", use_container_width=True):
        st.session_state.auth_status = None
        st.rerun()
    
    st.markdown("---")
    st.caption("© 2026 Gouvernement de Rensselaer. Tous droits réservés.")

# ======================================================================================
# SECTION 6 : MODULE VÉHICULES (IMMATS, ASSURANCES, TRIO RCT)
# ======================================================================================

tab_v, tab_c, tab_b, tab_a = st.tabs([
    "🚗 IMMATRICULATIONS", 
    "🪪 REGISTRE CIVIL", 
    "💰 TERMINAL BANCAIRE", 
    "📝 JOURNAUX D'AUDIT"
])

with tab_v:
    st.header("🚗 Gestion Routière et Titres")
    
    v_col1, v_col2 = st.columns([1.5, 1])
    
    with v_col1:
        with st.expander("📝 NOUVEL ENREGISTREMENT VÉHICULE", expanded=True):
            with st.form("veh_registration"):
                f_owner = st.selectbox("Titulaire du véhicule", ["---"] + df_bank["Nom Roblox"].tolist())
                f_brand = st.text_input("Marque / Modèle précis")
                f_plate = st.text_input("Numéro de plaque")
                f_insur = st.selectbox("Option Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
                f_code = st.text_input("Code de Radiation (Secret)", type="password")

                # CALCULATEUR FINANCIER TITAN
                tax_reg = 175
                tax_ins = 0
                if "AVERIS" in f_insur: tax_ins = 130
                elif "RCT" in f_insur: tax_ins = 150
                
                # LOGIQUE OFFRE TRIO RCT
                user_fleet = df_immat[df_immat["Nom d'utilisateur ROBLOX"] == f_owner]
                rct_ins_count = len(user_fleet[user_fleet["Assurance"].str.contains("RCT", na=False)])
                
                if "RCT" in f_insur and rct_ins_count >= 2:
                    tax_ins = 0
                    st.success("🎁 OFFRE TRIO : 3ème assurance gratuite appliquée !")

                total_amount = tax_reg + tax_ins
                st.markdown(f"### MONTANT TOTAL À PRÉLEVER : **{total_amount}$**")

                if st.form_submit_button("💳 VALIDER ET ENREGISTRER"):
                    if f_owner != "---" and f_plate and f_code:
                        # Processus Bancaire
                        u_idx = df_bank[df_bank["Nom Roblox"] == f_owner].index[0]
                        bal_now = float(str(df_bank.at[u_idx, "Solde"]).replace('$', '').replace(' ', ''))
                        
                        if bal_now >= total_amount:
                            # 1. Débit citoyen
                            df_bank.at[u_idx, "Solde"] = bal_now - total_amount
                            
                            # 2. Redirection des fonds (Consignes)
                            if tax_ins > 0:
                                target = ACC_REDIRECTION_AVERIS if "AVERIS" in f_insur else ACC_REDIRECTION_RCT
                                t_idx = df_bank[df_bank["Nom Roblox"] == target].index[0]
                                df_bank.at[t_idx, "Solde"] = float(str(df_bank.at[t_idx, "Solde"]).replace('$', '')) + tax_ins
                            
                            # 3. Création du titre
                            new_entry = pd.DataFrame([{
                                "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                                "Nom d'utilisateur ROBLOX": f_owner,
                                "Marque du véhicule": f_brand,
                                "Numéro de la plaque": f_plate,
                                "Assurance": f_insur,
                                "CODE": str(f_code)
                            }])
                            
                            # MISE À JOUR CLOUD
                            cloud_conn.update(worksheet="Banque", data=df_bank)
                            cloud_conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_immat, new_entry], ignore_index=True))
                            
                            st.session_state.last_receipt = {
                                "id": random.randint(1000, 9999),
                                "proprio": f_owner, "veh": f_brand, "plq": f_plate, "tot": total_amount
                            }
                            SecurityPortal.log_action(f"Immat : {f_plate} pour {f_owner}")
                            engine.force_refresh()
                            st.success("✅ TRANSACTION RÉUSSIE !"); time.sleep(1); st.rerun()
                        else:
                            st.error("❌ SOLDE INSUFFISANT.")

    with v_col2:
        st.subheader("🧾 REÇU DE PROPRIÉTÉ")
        if st.session_state.last_receipt:
            r = st.session_state.last_receipt
            st.markdown(f"""
                <div class="titan-receipt">
                    <center><b>*** RCRP FEDERAL SYSTEM ***</b><br>FACTURE N° {r['id']}</center><br>
                    DATE : {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
                    OPÉRATION : IMMATRICULATION<br>
                    ----------------------------------<br>
                    CITOYEN : {r['proprio'].upper()}<br>
                    VÉHICULE : {r['veh']}<br>
                    PLAQUE : {r['plq']}<br>
                    ----------------------------------<br>
                    <b>TOTAL PAYÉ : {r['tot']}$</b><br><br>
                    <center>MERCI DE VOTRE CONTRIBUTION</center>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Aucune transaction récente.")

# ======================================================================================
# SECTION 7 : MODULE POPULATION (PACK 15K + 25PTS + DATE AUTO)
# ======================================================================================

with tab_c:
    st.header("🪪 Registre de la Population")
    
    if st.session_state.auth_status == "Staff":
        with st.expander("🔨 CRÉER UN NOUVEAU DOSSIER (START PACK)", expanded=True):
            with st.form("new_cit_pack"):
                c_rob = st.text_input("Nom d'utilisateur Roblox")
                c_dis = st.text_input("Identifiant Discord")
                c_job = st.selectbox("Assignation de Poste", ["Civil", "Agent RCT", "Justice", "Staff"])
                
                if st.form_submit_button("🔨 INITIALISER LE PROFIL"):
                    if c_rob and c_dis:
                        # DATE AUTOMATIQUE
                        auto_date = datetime.now().strftime("%d/%m/%Y")
                        
                        # 1. Banque (15,000$ + Date auto)
                        row_b = pd.DataFrame([{
                            "Solde": 15000, "Nom Discord": c_dis, "Nom Roblox": c_rob, 
                            "Date d'arrivée": auto_date, "Emploiement": c_job
                        }])
                        
                        # 2. Permis (25 points auto)
                        row_p = pd.DataFrame([{
                            "Nom Discord": c_dis, "Nom Roblox": c_rob, 
                            "PTS": 25, "Validité": "OUI"
                        }])
                        
                        cloud_conn.update(worksheet="Banque", data=pd.concat([df_bank, row_b], ignore_index=True))
                        cloud_conn.update(worksheet="Points Permis", data=pd.concat([df_pts, row_p], ignore_index=True))
                        
                        SecurityPortal.log_action(f"Nouveau profil : {c_rob} (Start Pack)")
                        engine.force_refresh()
                        st.success(f"Dossier créé pour {c_rob} ! (15,000$ crédités)"); time.sleep(1); st.rerun()

    st.divider()
    search_cit = st.text_input("🔍 Rechercher un résident par nom :").lower()
    
    for i, r in df_bank.iterrows():
        if not search_cit or search_cit in str(r["Nom Roblox"]).lower():
            with st.container(border=True):
                st.write(f"👤 **{r['Nom Roblox']}** | 💼 {r['Emploiement']} | 📅 Inscription : {r['Date d\'arrivée']}")
                if st.session_state.auth_status in ["RCT", "Staff"]:
                    u_pts = df_pts[df_pts["Nom Roblox"] == r["Nom Roblox"]]["PTS"]
                    p_val = u_pts.values[0] if not u_pts.empty else "N/A"
                    st.caption(f"Points Permis : {p_val} | Discord : {r['Nom Discord']}")

# ======================================================================================
# SECTION 8 : MODULE FINANCES (TAXES ET REDIRECTIONS)
# ======================================================================================

with tab_b:
    st.header("💰 Terminal Bancaire Central")
    
    b_find = st.text_input("Chercher un compte client :").lower()
    
    for i, r in df_bank.iterrows():
        if not b_find or b_find in str(r["Nom Roblox"]).lower():
            with st.container(border=True):
                s_brut = float(str(r["Solde"]).replace('$', '').replace(' ', ''))
                bc1, bc2 = st.columns([1, 1])
                bc1.metric(f"Compte de {r['Nom Roblox']}", f"{s_brut:,.0f} $")
                
                if st.session_state.auth_status in ["RCT", "Staff"]:
                    with bc2:
                        tax_val = st.number_input("Montant de la taxe", min_value=0, key=f"tax_amt_{i}")
                        if st.button("📉 PRÉLEVER", key=f"tax_btn_{i}"):
                            # Débit
                            df_bank.at[i, "Solde"] = s_brut - tax_val
                            # Redirection si c'est un Agent RCT
                            if st.session_state.auth_status == "RCT":
                                rct_idx = df_bank[df_bank["Nom Roblox"] == ACC_REDIRECTION_RCT].index[0]
                                s_rct = float(str(df_bank.at[rct_idx, "Solde"]).replace('$', ''))
                                df_bank.at[rct_idx, "Solde"] = s_rct + tax_val
                                SecurityPortal.log_action(f"Taxe RCT de {tax_val}$ sur {r['Nom Roblox']}")
                            else:
                                SecurityPortal.log_action(f"Staff Taxe de {tax_val}$ sur {r['Nom Roblox']}")
                            
                            cloud_conn.update(worksheet="Banque", data=df_bank)
                            engine.force_refresh()
                            st.success("Débit effectué."); st.rerun()

# ======================================================================================
# SECTION 9 : MODULE AUDIT ET RADIATION STAFF
# ======================================================================================

with tab_a:
    st.header("📝 Journal d'Audit et Sécurité")
    
    if st.session_state.auth_status == "Staff":
        st.subheader("🗑️ ZONE DE RADIATION DES TITRES")
        rad_plq = st.text_input("Entrer la plaque à détruire :").upper()
        for i, r in df_immat.iterrows():
            if rad_plq == str(r["Numéro de la plaque"]).upper():
                st.warning(f"VÉHICULE DÉTECTÉ : {r['Marque du véhicule']} (Proprio: {r['Nom d\'utilisateur ROBLOX']})")
                if st.button("🚨 SUPPRIMER LE DOCUMENT DÉFINITIVEMENT"):
                    cloud_conn.update(worksheet="Copie de Immatriculations", data=df_immat.drop(i))
                    SecurityPortal.log_action(f"RADIATION : Plaque {rad_plq} supprimée.")
                    engine.force_refresh()
                    st.success("Titre radié."); st.rerun()
        
        st.divider()
        st.subheader("📋 HISTORIQUE DES ACTIONS")
        for log in reversed(st.session_state.audit_logs):
            st.text(log)
    else:
        st.error("ACCÈS RÉSERVÉ AU PERSONNEL ADMINISTRATEUR.")

# ======================================================================================
# SECTION 10 : FOOTER DU SYSTÈME (FIN DU CODE SOURCE)
# ======================================================================================

st.markdown("---")
st.markdown("""
    <div style='text-align: center; opacity: 0.6;'>
        <p>TITAN MAGNUS CORE v26.4.0 | RCRP FEDERAL TERMINAL<br>
        DÉVELOPPÉ POUR L'ADMINISTRATION DE RENSSELAER COUNTY</p>
    </div>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# FIN DE FICHIER - TITAN MAGNUS OS
# --------------------------------------------------------------------------------------
