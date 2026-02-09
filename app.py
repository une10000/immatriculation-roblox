import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random

# ======================================================================================
# 1. CONFIGURATION SYSTÈME & DESIGN GRAPHIQUE (FORCE MODE NUIT & CSS ÉTENDU)
# ======================================================================================
st.set_page_config(
    page_title="RCRP - Système de Gestion Intégral Professionnel Haute Sécurité",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection CSS Massive pour le look "Terminal Gouvernemental" et fix du texte blanc
st.markdown("""
    <style>
    /* FIX TOTAL MODE NUIT : Force le texte en blanc partout dans les inputs */
    input, textarea, [data-baseweb="input"], .stTextInput>div>div>input {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background-color: #1a1c23 !important;
        border: 1px solid #30363d !important;
        caret-color: white !important;
    }
    
    /* Global App Style */
    .stApp { 
        background-color: #0e1117; 
        color: #ffffff; 
    }
    
    /* Gadget : En-tête Gouvernemental Premium */
    .gov-header {
        background: linear-gradient(135deg, #1a1c23 0%, #3d4452 100%);
        padding: 45px;
        border-radius: 20px;
        border-left: 10px solid #ff4b4b;
        text-align: left;
        margin-bottom: 35px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6);
    }
    .gov-header h1 { margin: 0; font-size: 2.5em; color: white; }
    .gov-header p { margin: 5px 0 0; opacity: 0.8; font-size: 1.1em; }

    /* Gadget : REÇU VERSION LONGUE (NÉON GREEN) */
    .ticket-fix { 
        background-color: #050505 !important; 
        color: #00FF41 !important; 
        padding: 40px; 
        border: 1px solid #00FF41; 
        border-top: 15px solid #00FF41;
        border-radius: 4px; 
        font-family: 'Consolas', 'Courier New', monospace; 
        margin: 25px 0;
        box-shadow: 0px 0px 30px rgba(0, 255, 65, 0.15);
        line-height: 1.6;
        font-size: 13px;
    }
    .ticket-divider { 
        border-top: 2px dashed #00FF41; 
        margin: 15px 0; 
        opacity: 0.5;
    }

    /* Gadget : Panneaux d'information Civil/Agent/Admin */
    .info-panel {
        background-color: #1c2128;
        border: 1px solid #30363d;
        padding: 25px;
        border-radius: 12px;
        margin: 15px 0;
        border-top: 4px solid #ff4b4b;
        transition: transform 0.3s ease;
    }
    .info-panel:hover {
        transform: scale(1.02);
        border-color: #ff4b4b;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0e1117; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# ======================================================================================
# 2. PARAMÈTRES, CONSTANTES ET SÉCURITÉ
# ======================================================================================
if "role" not in st.session_state:
    st.session_state.role = None
if "last_receipt" not in st.session_state:
    st.session_state.last_receipt = None
if "auth_time" not in st.session_state:
    st.session_state.auth_time = None

# Identifiants de destination pour les fonds (Strict Respect des consignes)
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010" 

# Codes de sécurité chiffrés (Simulation)
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"

# Ressources visuelles
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

# ======================================================================================
# 3. GESTION DES FLUX DE DONNÉES (GOOGLE SHEETS INTEGRATION)
# ======================================================================================
@st.cache_data(ttl=0) # On désactive le cache pour avoir du temps réel
def load_rcrp_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        b = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
        i = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        p = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
        return conn, b, i, p
    except Exception as e:
        st.error(f"🚨 ALERTE CRITIQUE : Échec de liaison avec le Cloud. Détails : {e}")
        return None, None, None, None

connection, df_banque, df_im, df_permis = load_rcrp_data()

if connection is None:
    st.warning("Système en maintenance ou erreur de configuration des secrets.")
    st.stop()

# ======================================================================================
# 4. PORTAIL D'ENTRÉE SÉCURISÉ (LOGIN MULTI-NIVEAUX)
# ======================================================================================
if st.session_state.role is None:
    st.markdown("""
        <div class="gov-header">
            <h1>🏛️ RENSSELAER COUNTY</h1>
            <p>Système de Gestion Centralisé des Données (v20.6.2)</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("### 🔑 SÉLECTION DU TERMINAL D'ACCÈS")
    
    col_portail1, col_portail2, col_portail3 = st.columns(3)
    
    with col_portail1:
        st.markdown('<div class="info-panel"><h4>👤 Terminal Citoyen</h4><p>Consultation des plaques, du solde et enregistrement de nouveaux véhicules.</p></div>', unsafe_allow_html=True)
        if st.button("ACCÉDER AU TERMINAL CIVIL", use_container_width=True):
            st.session_state.role = "Civil"
            st.session_state.auth_time = datetime.now()
            st.rerun()
            
    with col_portail2:
        st.markdown('<div class="info-panel"><h4>🛠️ Terminal Agent RCT</h4><p>Accès restreint. Gestion des taxes, immatriculations et prélèvements bancaires.</p></div>', unsafe_allow_html=True)
        login_rct = st.text_input("Clé d'accès Agent", type="password", key="pwd_rct")
        if st.button("AUTHENTIFICATION RCT", use_container_width=True):
            if login_rct == CODE_PRO:
                st.session_state.role = "RCT"
                st.session_state.auth_time = datetime.now()
                st.rerun()
            else:
                st.error("❌ CLÉ INCORRECTE")
            
    with col_portail3:
        st.markdown('<div class="info-panel"><h4>👮 Terminal Staff</h4><p>Niveau 4. Gestion salariale, création de profils et accès total aux archives.</p></div>', unsafe_allow_html=True)
        login_staff = st.text_input("Clé Maître Admin", type="password", key="pwd_staff")
        if st.button("CONNEXION HAUTE SÉCURITÉ", use_container_width=True):
            if login_staff == CODE_ADMIN:
                st.session_state.role = "Staff"
                st.session_state.auth_time = datetime.now()
                st.rerun()
            else:
                st.error("❌ AUTORISATION REFUSÉE")

    st.divider()
    st.caption("Avertissement : Toute tentative de connexion non autorisée est enregistrée par le département de justice.")
    st.stop()

# ======================================================================================
# 5. NAVIGATION PAR ONGLETS (LOGIQUE MÉTIER ÉTENDUE)
# ======================================================================================
with st.sidebar:
    st.image(LOGO_URL, width=200)
    st.markdown(f"**👤 Utilisateur :** `{st.session_state.role}`")
    st.markdown(f"**⏰ Session depuis :** {st.session_state.auth_time.strftime('%H:%M:%S')}")
    st.divider()
    if st.button("🔄 SYNCHRONISATION", use_container_width=True):
        st.rerun()
    if st.button("🚪 DÉCONNEXION", use_container_width=True):
        st.session_state.role = None
        st.rerun()

tab_immat, tab_dossier, tab_banque = st.tabs([
    "🚗 GESTION DES VÉHICULES", 
    "🪪 REGISTRE DES CITOYENS", 
    "💰 BANQUE CENTRALE"
])

# --------------------------------------------------------------------------------------
# ONGLET 1 : IMMATRICULATIONS & REÇU ULTRA-DÉTAILLÉ
# --------------------------------------------------------------------------------------
with tab_immat:
    st.header("🚗 Registre National des Véhicules")
    st.info("Le coût standard est de 175$ de taxe d'immatriculation d'État.")
    
    col_v_form, col_v_receipt = st.columns([1.3, 1])
    
    with col_v_form:
        with st.expander("📝 FORMULAIRE OFFICIEL D'IMMATRICULATION", expanded=True):
            # Formulaire détaillé
            proprio = st.selectbox("Titulaire du véhicule", ["---"] + df_banque["Nom Roblox"].tolist())
            marque = st.text_input("Marque et Modèle du véhicule", placeholder="Ex: Audi RS6")
            plaque = st.text_input("Numéro de la Plaque", placeholder="RC-123-AA")
            assurance = st.selectbox("Type d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            code_sec = st.text_input("Code Secret (Nécessaire pour radiation)", type="password")

            # Logique de calcul complexe
            taxe_etat = 175
            taxe_assu = 0
            if "AVERIS" in assurance: taxe_assu = 130
            elif "RCT" in assurance: taxe_assu = 150
            
            # Application de l'offre Trio RCT (3ème assurance offerte)
            vehicules_existants = df_im[df_im["Nom d'utilisateur ROBLOX"] == proprio]
            nb_assu_rct = len(vehicules_existants[vehicules_existants["Assurance"].str.contains("RCT", na=False)])
            
            if "RCT" in assurance and nb_assu_rct >= 2:
                taxe_assu = 0
                st.success("🎁 OFFRE TRIO : 2 assurances RCT détectées, la 3ème est GRATUITE !")

            total_ttc = taxe_etat + taxe_assu
            
            st.markdown(f"**Montant total à débiter : {total_ttc}$**")

            if st.button("💳 VALIDER LA TRANSACTION BANCAIRE", use_container_width=True):
                if proprio == "---" or not plaque or not code_sec:
                    st.error("⚠️ Champs obligatoires manquants.")
                else:
                    # Recherche citoyen
                    idx_citoyen = df_banque[df_banque["Nom Roblox"] == proprio].index[0]
                    solde_actuel = float(str(df_banque.at[idx_citoyen, "Solde"]).replace('$', '').replace(' ', ''))
                    
                    if solde_actuel >= total_ttc:
                        with st.status("Traitement sécurisé en cours...", expanded=False) as status:
                            st.write("Vérification des fonds...")
                            time.sleep(1)
                            # Débit
                            df_banque.at[idx_citoyen, "Solde"] = solde_actuel - total_ttc
                            
                            # Crédit des comptes assurances (Respect Consignes)
                            if taxe_assu > 0:
                                st.write("Redirection des taxes d'assurance...")
                                dest = TARGET_AVERIS if "AVERIS" in assurance else TARGET_RCT
                                idx_dest = df_banque[df_banque["Nom Roblox"] == dest].index[0]
                                s_dest = float(str(df_banque.at[idx_dest, "Solde"]).replace('$', '').replace(' ', ''))
                                df_banque.at[idx_dest, "Solde"] = s_dest + taxe_assu
                            
                            st.write("Enregistrement dans la base nationale...")
                            new_v_row = pd.DataFrame([{
                                "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                                "Nom d'utilisateur ROBLOX": proprio,
                                "Marque du véhicule": marque,
                                "Numéro de la plaque": plaque,
                                "Assurance": assurance,
                                "CODE": str(code_sec)
                            }])
                            
                            # Update Sheets
                            connection.update(worksheet="Banque", data=df_banque)
                            connection.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_v_row], ignore_index=True))
                            
                            # Préparation du Reçu
                            st.session_state.last_receipt = {
                                "ticket_id": random.randint(1000000, 9999999),
                                "time": datetime.now().strftime("%d/%m/%Y à %H:%M"),
                                "user": proprio,
                                "car": marque,
                                "plate": plaque,
                                "insurance": assurance,
                                "t_etat": taxe_etat,
                                "t_ass": taxe_assu,
                                "total": total_ttc,
                                "agent": st.session_state.role
                            }
                            status.update(label="Transaction Terminée !", state="complete")
                        st.rerun()
                    else:
                        st.error(f"❌ FONDS INSUFFISANTS. Solde : {solde_actuel}$")

    with col_v_receipt:
        st.subheader("🧾 REÇU DE TRANSACTION")
        if st.session_state.last_receipt:
            res = st.session_state.last_receipt
            st.markdown(f"""
            <div class="ticket-fix">
                <center>
                    <h3 style='margin:0;'>REPUBLIQUE DE RENSSELAER</h3>
                    <small>DÉPARTEMENT DU TRANSPORT ET DU COMMERCE</small>
                </center>
                <div class="ticket-divider"></div>
                <b>DOSSIER N° :</b> RCRP-2026-{res['ticket_id']}<br>
                <b>DATE :</b> {res['time']}<br>
                <b>OPÉRATEUR :</b> {res['agent']}<br>
                <div class="ticket-divider"></div>
                <b>PROPRIÉTAIRE :</b> {res['user'].upper()}<br>
                <b>VÉHICULE :</b> {res['car']}<br>
                <b>PLAQUE :</b> {res['plate']}<br>
                <b>ASSURANCE :</b> {res['insurance']}<br>
                <div class="ticket-divider"></div>
                DÉTAIL FINANCIER :<br>
                - TAXE IMMATRICULATION : {res['t_etat']}$<br>
                - SERVICE ASSURANCE : {res['t_ass']}$<br>
                <div class="ticket-divider"></div>
                <b>TOTAL DÉBITÉ : {res['total']}$</b>
                <div class="ticket-divider"></div>
                <center>
                    <i>CE REÇU SERT DE PREUVE DE PROPRIÉTÉ PROVISOIRE.<br>
                    TOUTE ALTÉRATION EST UN CRIME FÉDÉRAL.</i><br>
                    <b>--- MERCI ---</b>
                </center>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Aucun reçu n'a été généré durant cette session.")

    st.divider()
    st.subheader("🔍 ARCHIVES DES IMMATRICULATIONS")
    recherche = st.text_input("Rechercher par plaque ou propriétaire :").upper()
    
    for idx_i, row_i in df_im.iterrows():
        if not recherche or (recherche in str(row_i["Numéro de la plaque"]).upper() or recherche in str(row_i["Nom d'utilisateur ROBLOX"]).upper()):
            with st.container(border=True):
                st.write(f"🚗 **Plaque : {row_i['Numéro de la plaque']}** | Titulaire : {row_i['Nom d\'utilisateur ROBLOX']}")
                with st.expander("⚙️ Gérer l'enregistrement"):
                    code_verif = st.text_input("Saisir Code Secret", type="password", key=f"v_sec_{idx_i}")
                    if code_verif == str(row_i["CODE"]) or st.session_state.role == "Staff":
                        if st.button(f"🗑️ RADIER LA PLAQUE {row_i['Numéro de la plaque']}", key=f"del_{idx_i}"):
                            new_df_im = df_im.drop(idx_i)
                            connection.update(worksheet="Copie de Immatriculations", data=new_df_im)
                            st.success("Radiation effectuée."); time.sleep(1); st.rerun()

# --------------------------------------------------------------------------------------
# ONGLET 2 : DOSSIERS (15K + 25 PTS + DATE AUTO)
# --------------------------------------------------------------------------------------
with tab_dossier:
    st.header("🪪 Dossiers Administratifs et Civils")
    
    if st.session_state.role == "Staff":
        col_adm1, col_adm2 = st.columns(2)
        
        with col_adm1:
            st.subheader("💰 Versement des Salaires")
            st.write("Calcul automatique : RCT (17k) | Civils (15k)")
            if st.button("💸 DÉCLENCHER LE VIREMENT GÉNÉRAL", use_container_width=True):
                for i_b, r_b in df_banque.iterrows():
                    m_paie = 17000 if "RCT" in str(r_b["Emploiement"]) else 15000
                    df_banque.at[i_b, "Solde"] = float(str(r_b["Solde"]).replace('$', '').replace(' ', '')) + m_paie
                connection.update(worksheet="Banque", data=df_banque)
                st.success("Virement effectué pour l'ensemble de la population."); time.sleep(1); st.rerun()
                
        with col_adm2:
            st.subheader("👤 Inscription au Registre")
            with st.form("inscription_new"):
                new_rob = st.text_input("Nom d'utilisateur Roblox")
                new_dis = st.text_input("Identifiant Discord")
                new_job = st.selectbox("Poste Occupé", ["Civil", "Agent RCT", "Gouvernement"])
                
                if st.form_submit_button("🔨 CRÉER LE DOSSIER COMPLET"):
                    if new_rob and new_dis:
                        date_j = datetime.now().strftime("%d/%m/%Y")
                        # 1. Banque (15,000$) + Date Auto
                        row_banque = pd.DataFrame([{
                            "Solde": 15000, "Nom Discord": new_dis, "Nom Roblox": new_rob, 
                            "Date d'arrivée": date_j, "Emploiement": new_job
                        }])
                        # 2. Permis (25 Points)
                        row_permis = pd.DataFrame([{
                            "Nom Discord": new_dis, "Nom Roblox": new_rob, "PTS": 25, "Validité": "OUI"
                        }])
                        
                        connection.update(worksheet="Banque", data=pd.concat([df_banque, row_banque], ignore_index=True))
                        connection.update(worksheet="Points Permis", data=pd.concat([df_permis, row_permis], ignore_index=True))
                        st.success(f"Dossier de {new_rob} finalisé (15k + 25pts)."); time.sleep(1); st.rerun()
    
    st.divider()
    st.subheader("📋 LISTE DES CITOYENS")
    recherche_cit = st.text_input("Filtrer par nom :").lower()
    
    for idx_b, r_b in df_banque.iterrows():
        if not recherche_cit or recherche_cit in str(r_b["Nom Roblox"]).lower():
            with st.container(border=True):
                st.markdown(f"👤 **{r_b['Nom Roblox']}** | 💼 {r_b['Emploiement']} | 📅 Inscrit le : {r_b['Date d\'arrivée']}")
                with st.expander("🔎 Détails du dossier"):
                    col_det1, col_det2 = st.columns(2)
                    col_det1.write(f"Discord : {r_b['Nom Discord']}")
                    # Récupération points permis
                    pts = df_permis[df_permis["Nom Roblox"] == r_b["Nom Roblox"]]["PTS"]
                    col_det2.write(f"Points Permis : {pts.values[0] if not pts.empty else 'N/A'}")

# --------------------------------------------------------------------------------------
# ONGLET 3 : BANQUE CENTRALE (TAXES & AMENDES)
# --------------------------------------------------------------------------------------
with tab_banque:
    st.header("💰 Gestion Bancaire et Fiscalité")
    
    search_bank = st.text_input("Rechercher un compte client :").lower()
    
    for idx_b, r_b in df_banque.iterrows():
        if not search_bank or search_bank in str(r_b["Nom Roblox"]).lower():
            with st.container(border=True):
                solde_num = float(str(r_b["Solde"]).replace('$', '').replace(' ', ''))
                
                col_b1, col_b2 = st.columns([1, 1])
                with col_b1:
                    st.metric(f"Solde de {r_b['Nom Roblox']}", f"{solde_num:,.0f} $")
                
                with col_b2:
                    if st.session_state.role in ["RCT", "Staff"]:
                        st.write("**Zone de Prélèvement (Amendes/Taxes)**")
                        m_prelev = st.number_input(f"Montant ({r_b['Nom Roblox']})", min_value=0, key=f"prel_{idx_b}")
                        if st.button("CONFIRMER LE DÉBIT", key=f"btn_prel_{idx_b}"):
                            # Débit
                            df_banque.at[idx_b, "Solde"] = solde_num - m_prelev
                            
                            # Si Agent RCT, l'argent va au compte RCT (une10000)
                            if st.session_state.role == "RCT":
                                idx_rct = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                s_rct = float(str(df_banque.at[idx_rct, "Solde"]).replace('$', '').replace(' ', ''))
                                df_banque.at[idx_rct, "Solde"] = s_rct + m_prelev
                                
                            connection.update(worksheet="Banque", data=df_banque)
                            st.success(f"Débit de {m_prelev}$ effectué."); time.sleep(1); st.rerun()

# Fin du script - Footer
st.divider()
st.markdown("<center><p style='color: #4b4b4b;'>RCRP SYSTEM - Version 20.6.2 - Logiciel sous licence gouvernementale</p></center>", unsafe_allow_html=True)
