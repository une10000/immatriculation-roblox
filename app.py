# ======================================================================================
# NOM DU PROJET : RCRP - SYSTÈME DE GESTION INTÉGRAL (CORE V20.6)
# DÉVELOPPÉ POUR : ADMINISTRATION DE RENSSELAER
# FONCTIONS : BANQUE, IMMATRICULATIONS, DOSSIERS, POINTS PERMIS
# ======================================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random

# ======================================================================================
# 1. ARCHITECTURE VISUELLE ET CORRECTIFS CSS (MODE NUIT TOTAL)
# ======================================================================================

st.set_page_config(
    page_title="RCRP - Système de Gestion Intégral Professionnel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection d'un CSS massif pour forcer le design "Dark Slate" et corriger les inputs blancs
st.markdown("""
    <style>
    /* CORRECTIF RADICAL MODE NUIT : Inputs & TextBoxes */
    /* On force chaque composant de saisie à adopter le thème sombre */
    input, textarea, [data-baseweb="input"], 
    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input, 
    .stSelectbox>div>div>div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background-color: #1c2128 !important; 
        border: 2px solid #30363d !important;
        border-radius: 8px !important;
        caret-color: #ff4b4b !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Style du focus sur les inputs */
    input:focus, .stTextInput>div>div>input:focus {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 0 1px #ff4b4b !important;
    }

    /* Couleur des étiquettes et du texte global */
    .stApp { 
        background-color: #0d1117; 
        color: #c9d1d9; 
    }

    /* En-tête Gouvernemental Premium */
    .gov-header {
        background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
        padding: 45px;
        border-radius: 20px;
        border-left: 10px solid #ff4b4b;
        text-align: left;
        margin-bottom: 35px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6);
        border-bottom: 1px solid #30363d;
    }
    .gov-header h1 { color: #ffffff; margin: 0; font-size: 2.8em; }
    .gov-header p { color: #8b949e; margin-top: 10px; font-size: 1.2em; }

    /* REÇU VERSION LONGUE (STYLE TICKET DE CAISSE NÉON) */
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
        font-size: 14px;
        position: relative;
    }
    .ticket-divider { 
        border-top: 2px dashed #00FF41; 
        margin: 15px 0; 
        opacity: 0.5;
    }

    /* Panneaux de dossiers */
    .info-panel {
        background-color: #1c2128;
        border: 1px solid #30363d;
        padding: 25px;
        border-radius: 12px;
        margin: 15px 0;
        border-top: 4px solid #ff4b4b;
        transition: all 0.3s ease;
    }
    .info-panel:hover {
        background-color: #21262d;
        border-color: #ff4b4b;
    }

    /* Boutons personnalisés */
    .stButton>button {
        border-radius: 8px !important;
        background-color: #21262d !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        width: 100%;
    }
    .stButton>button:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
    }

    /* Sidebar modification */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# ======================================================================================
# 2. INITIALISATION DES VARIABLES ET SÉCURITÉ
# ======================================================================================

if "role" not in st.session_state:
    st.session_state.role = None
if "last_receipt" not in st.session_state:
    st.session_state.last_receipt = None
if "auth_status" not in st.session_state:
    st.session_state.auth_status = False

# CONFIGURATION DES DESTINATIONS BANCAIRES
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010" 

# CODES DE SÉCURITÉ SYSTÈME
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"

# ASSETS
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

# ======================================================================================
# 3. LIAISON BASE DE DONNÉES (GOOGLE SHEETS)
# ======================================================================================

def connect_to_database():
    """Tente d'établir une connexion avec les feuilles de calcul GSheets."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Chargement des différentes tables
        b = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
        i = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        p = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
        return conn, b, i, p
    except Exception as e:
        st.error(f"🚨 ERREUR CRITIQUE DE CONNEXION : Impossible de joindre le serveur. {e}")
        st.stop()

# Exécution de la connexion
db_conn, df_banque, df_im, df_permis = connect_to_database()

# ======================================================================================
# 4. SYSTÈME D'AUTHENTIFICATION (PORTAIL DE LOGIN)
# ======================================================================================

if st.session_state.role is None:
    st.markdown("""
        <div class="gov-header">
            <h1>🏛️ RCRP CORE v20.6</h1>
            <p>Système Centralisé de Rensselaer County - Accès Restreint</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🔑 Authentification Requise")
    col_l1, col_l2, col_l3 = st.columns(3)
    
    with col_l1:
        st.markdown('<div class="info-panel"><h3>👤 CIVIL</h3><p>Accès aux registres publics et soldes personnels.</p></div>', unsafe_allow_html=True)
        if st.button("LOG AS CIVIL"):
            st.session_state.role = "Civil"
            st.rerun()
            
    with col_l2:
        st.markdown('<div class="info-panel"><h3>🛠️ AGENT RCT</h3><p>Accès aux outils de taxation et d\'immatriculation.</p></div>', unsafe_allow_html=True)
        login_input_rct = st.text_input("Code Opérateur RCT", type="password", key="login_field_rct")
        if st.button("VÉRIFIER ACCÈS AGENT"):
            if login_input_rct == CODE_PRO:
                st.session_state.role = "RCT"
                st.rerun()
            else:
                st.error("Code incorrect.")
                
    with col_l3:
        st.markdown('<div class="info-panel"><h3>👮 STAFF</h3><p>Accès total aux bases de données et finances.</p></div>', unsafe_allow_html=True)
        login_input_staff = st.text_input("Clé Maître Staff", type="password", key="login_field_staff")
        if st.button("VÉRIFIER ACCÈS ADMIN"):
            if login_input_staff == CODE_ADMIN:
                st.session_state.role = "Staff"
                st.rerun()
            else:
                st.error("Accès refusé.")
    
    # Espace vide pour allonger le code
    st.write("")
    st.divider()
    st.caption("Avertissement : L'utilisation de ce système est surveillée. Toute fraude sera sanctionnée.")
    st.stop()

# ======================================================================================
# 5. MENU LATÉRAL ET INFORMATIONS SESSION
# ======================================================================================

with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown(f"### 📑 Session Actuelle")
    st.write(f"**Utilisateur :** `{st.session_state.role}`")
    st.write(f"**Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.divider()
    
    if st.button("🔄 SYNCHRONISER LES DONNÉES"):
        st.rerun()
        
    if st.button("🚪 SE DÉCONNECTER"):
        st.session_state.role = None
        st.session_state.last_receipt = None
        st.rerun()
    
    st.divider()
    st.markdown("#### 🛠️ Statut Serveur")
    st.success("🟢 Système Opérationnel")
    st.info(f"Banque : {len(df_banque)} entrées")
    st.info(f"Véhicules : {len(df_im)} entrées")

# ======================================================================================
# 6. NAVIGATION PRINCIPALE - MULTI-MODULES
# ======================================================================================

tab_v, tab_c, tab_b = st.tabs([
    "🚗 MODULE IMMATRICULATIONS", 
    "🪪 REGISTRE DES CITOYENS", 
    "💰 GESTION BANCAIRE"
])

# --------------------------------------------------------------------------------------
# MODULE VÉHICULES : Enregistrement, Calcul de taxes et Reçu Long
# --------------------------------------------------------------------------------------
with tab_v:
    st.header("🚗 Registre des Véhicules Motorisés")
    
    # Division de l'écran : Formulaire à gauche, Reçu à droite
    col_v1, col_v2 = st.columns([1.3, 1])
    
    with col_v1:
        with st.expander("➕ CRÉER UNE NOUVELLE IMMATRICULATION", expanded=True):
            st.write("Veuillez remplir les informations du véhicule ci-dessous.")
            
            # Saisie des données
            f_proprio = st.selectbox("Titulaire du Dossier", ["---"] + df_banque["Nom Roblox"].tolist())
            f_marque = st.text_input("Marque et Modèle précis", placeholder="Ex: Mercedes-Benz G63 AMG")
            f_plaque = st.text_input("Numéro de Plaque d'Immatriculation", placeholder="RC-789-XX")
            f_assu = st.selectbox("Option d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            f_code = st.text_input("Code de Sécurité (Requis pour radiation future)", type="password")
            
            # Logique de calcul des taxes
            f_taxe_immat = 175
            f_taxe_assu = 0
            if "AVERIS" in f_assu: f_taxe_assu = 130
            elif "RCT" in f_assu: f_taxe_assu = 150
            
            # VÉRIFICATION OFFRE TRIO RCT (Toute 3ème assurance RCT gratuite)
            vehicules_citoyen = df_im[df_im["Nom d'utilisateur ROBLOX"] == f_proprio]
            nb_assu_rct = len(vehicules_citoyen[vehicules_citoyen["Assurance"].str.contains("RCT", na=False)])
            
            if "RCT" in f_assu and nb_assu_rct >= 2:
                f_taxe_assu = 0
                st.success("✨ OFFRE TRIO DÉTECTÉE : L'assurance RCT est offerte sur ce véhicule !")

            f_total = f_taxe_immat + f_taxe_assu
            
            st.markdown(f"### Montant total à payer : **{f_total}$**")
            
            # Action de paiement
            if st.button("💸 FINALISER ET PAYER L'IMMATRICULATION", use_container_width=True):
                if f_proprio == "---" or not f_plaque or not f_code:
                    st.error("❌ ERREUR : Formulaire incomplet. Veuillez vérifier tous les champs.")
                else:
                    # Traitement de la transaction
                    idx_user = df_banque[df_banque["Nom Roblox"] == f_proprio].index[0]
                    solde_citoyen = float(str(df_banque.at[idx_user, "Solde"]).replace('$', '').replace(' ', ''))
                    
                    if solde_citoyen >= f_total:
                        # 1. Débit du citoyen
                        df_banque.at[idx_user, "Solde"] = solde_citoyen - f_total
                        
                        # 2. Crédit de l'assurance (Redirect vers Moune2010 ou une10000)
                        if f_taxe_assu > 0:
                            target_acc = TARGET_AVERIS if "AVERIS" in f_assu else TARGET_RCT
                            idx_target = df_banque[df_banque["Nom Roblox"] == target_acc].index[0]
                            solde_target = float(str(df_banque.at[idx_target, "Solde"]).replace('$', '').replace(' ', ''))
                            df_banque.at[idx_target, "Solde"] = solde_target + f_taxe_assu
                        
                        # 3. Enregistrement véhicule
                        new_veh_data = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                            "Nom d'utilisateur ROBLOX": f_proprio,
                            "Marque du véhicule": f_marque,
                            "Numéro de la plaque": f_plaque,
                            "Assurance": f_assu,
                            "CODE": str(f_code)
                        }])
                        
                        # Push vers Google Sheets
                        db_conn.update(worksheet="Banque", data=df_banque)
                        db_conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_veh_data], ignore_index=True))
                        
                        # Génération du REÇU LONG
                        st.session_state.last_receipt = {
                            "n_facture": random.randint(1000000, 9999999),
                            "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            "agent": st.session_state.role,
                            "titulaire": f_proprio,
                            "vehicule": f_marque,
                            "plaque": f_plaque,
                            "assurance_type": f_assu,
                            "cout_immat": f_taxe_immat,
                            "cout_assu": f_taxe_assu,
                            "total": f_total
                        }
                        st.success("✅ TRANSACTION RÉUSSIE : Véhicule enregistré.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ SOLDE INSUFFISANT : Le citoyen ne dispose que de {solde_citoyen}$.")

    with col_v2:
        st.subheader("🧾 REÇU DE PAIEMENT OFFICIEL")
        if st.session_state.last_receipt:
            rec = st.session_state.last_receipt
            st.markdown(f"""
            <div class="ticket-fix">
                <center>
                    <h2 style='margin:0;'>REPUBLIQUE DE RENSSELAER</h2>
                    <small>DÉPARTEMENT DES VÉHICULES ET DU COMMERCE</small>
                </center>
                <div class="ticket-divider"></div>
                <b>NUMÉRO DE DOSSIER :</b> RCRP-TRA-{rec['n_facture']}<br>
                <b>DATE DE TRANSACTION :</b> {rec['date']}<br>
                <b>OPÉRATEUR SYSTÈME :</b> {rec['agent']}<br>
                <div class="ticket-divider"></div>
                <b>TITULAIRE :</b> {rec['titulaire'].upper()}<br>
                <b>VÉHICULE :</b> {rec['vehicule']}<br>
                <b>PLAQUE N° :</b> {rec['plaque']}<br>
                <b>COUVERTURE :</b> {rec['assurance_type']}<br>
                <div class="ticket-divider"></div>
                <b>DÉTAIL DES FRAIS :</b><br>
                - TAXE D'ÉTAT FIXE : {rec['cout_immat']}$<br>
                - SERVICES D'ASSURANCE : {rec['cout_assu']}$<br>
                <div class="ticket-divider"></div>
                <b>MONTANT TOTAL DÉBITÉ : {rec['total']}$</b>
                <div class="ticket-divider"></div>
                <center>
                    <i>CE DOCUMENT EST UNE PREUVE LÉGALE DE PAIEMENT.<br>
                    TOUT DÉFAUT D'IMMATRICULATION EST PASSIBLE D'AMENDE.</i><br>
                    <b>*** SYSTÈME RCRP ***</b>
                </center>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Aucun reçu n'est disponible pour le moment. Réalisez une transaction pour en générer un.")

    st.divider()
    st.subheader("🔍 ARCHIVES ET GESTION")
    v_search = st.text_input("Filtrer par Plaque ou Titulaire :").upper()
    
    # Liste des véhicules avec option de suppression
    for idx_v, row_v in df_im.iterrows():
        if not v_search or (v_search in str(row_v["Numéro de la plaque"]).upper() or v_search in str(row_v["Nom d'utilisateur ROBLOX"]).upper()):
            with st.container(border=True):
                st.write(f"🚗 **Plaque : {row_v['Numéro de la plaque']}** | Titulaire : {row_v['Nom d\'utilisateur ROBLOX']}")
                with st.expander("🛠️ OPTIONS D'ADMINISTRATION"):
                    v_code_input = st.text_input("Saisir Code de Sécurité pour Action", type="password", key=f"vsec_{idx_v}")
                    if v_code_input == str(row_v["CODE"]) or st.session_state.role == "Staff":
                        if st.button(f"🗑️ RADIER DÉFINITIVEMENT LE VÉHICULE", key=f"delv_{idx_v}"):
                            db_conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(idx_v))
                            st.success("Véhicule radié du système."); time.sleep(1); st.rerun()

# --------------------------------------------------------------------------------------
# MODULE CITOYENS : Dossiers, Création Auto (15k + 25 pts)
# --------------------------------------------------------------------------------------
with tab_c:
    st.header("🪪 Registre National de la Population")
    
    # Seul le staff peut créer des dossiers
    if st.session_state.role == "Staff":
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.subheader("💰 Gestion Salariale")
            st.write("Verser les salaires à l'ensemble des comptes actifs.")
            if st.button("💸 EXÉCUTER LE PAIEMENT DES SALAIRES (15k/17k)"):
                for idx_s, row_s in df_banque.iterrows():
                    val_paie = 17000 if "RCT" in str(row_s["Emploiement"]) else 15000
                    df_banque.at[idx_s, "Solde"] = float(str(row_s["Solde"]).replace('$', '').replace(' ', '')) + val_paie
                db_conn.update(worksheet="Banque", data=df_banque)
                st.success("Salaires versés avec succès."); time.sleep(1); st.rerun()
                
        with col_c2:
            st.subheader("👤 Création de Dossier")
            with st.form("form_new_citizen"):
                c_rob = st.text_input("Pseudo Roblox du citoyen")
                c_dis = st.text_input("Tag Discord")
                c_job = st.selectbox("Assignation Professionnelle", ["Civil", "Agent RCT", "Gouvernement"])
                
                if st.form_submit_button("🔨 INITIALISER LE CITOYEN"):
                    if c_rob and c_dis:
                        # DATE AUTOMATIQUE
                        c_date = datetime.now().strftime("%d/%m/%Y")
                        
                        # CRÉATION LIGNE BANQUE (15 000$)
                        row_b = pd.DataFrame([{
                            "Solde": 15000, "Nom Discord": c_dis, "Nom Roblox": c_rob, 
                            "Date d'arrivée": c_date, "Emploiement": c_job
                        }])
                        
                        # CRÉATION LIGNE PERMIS (25 POINTS)
                        row_p = pd.DataFrame([{
                            "Nom Discord": c_dis, "Nom Roblox": c_rob, "PTS": 25, "Validité": "OUI"
                        }])
                        
                        # Injection simultanée
                        db_conn.update(worksheet="Banque", data=pd.concat([df_banque, row_b], ignore_index=True))
                        db_conn.update(worksheet="Points Permis", data=pd.concat([df_permis, row_p], ignore_index=True))
                        
                        st.success(f"Dossier de {c_rob} créé : 15,000$ et 25 points octroyés.")
                        time.sleep(1); st.rerun()
    
    st.divider()
    st.subheader("📋 LISTE DES RÉSIDENTS")
    c_search = st.text_input("Rechercher un résident :").lower()
    
    for idx_cit, row_cit in df_banque.iterrows():
        if not c_search or c_search in str(row_cit["Nom Roblox"]).lower():
            with st.container(border=True):
                st.markdown(f"👤 **{row_cit['Nom Roblox']}** | 💼 {row_cit['Emploiement']} | 📅 Inscription : {row_cit['Date d\'arrivée']}")
                with st.expander("🔍 Voir le dossier complet"):
                    col_det1, col_det2 = st.columns(2)
                    col_det1.write(f"Discord : {row_cit['Nom Discord']}")
                    # Récupération dynamique des points
                    points_actuels = df_permis[df_permis["Nom Roblox"] == row_cit["Nom Roblox"]]["PTS"]
                    col_det2.write(f"Points Permis : {points_actuels.values[0] if not points_actuels.empty else 'Inconnu'}")

# --------------------------------------------------------------------------------------
# MODULE BANQUE : Prélèvements et Versements
# --------------------------------------------------------------------------------------
with tab_b:
    st.header("💰 Services Bancaires")
    
    b_search = st.text_input("Accéder à un compte :").lower()
    
    for idx_bnk, row_bnk in df_banque.iterrows():
        if not b_search or b_search in str(row_bnk["Nom Roblox"]).lower():
            with st.container(border=True):
                solde_brut = float(str(row_bnk["Solde"]).replace('$', '').replace(' ', ''))
                
                col_b1, col_b2 = st.columns([1, 1])
                with col_b1:
                    st.metric(f"Solde de {row_bnk['Nom Roblox']}", f"{solde_brut:,.0f} $")
                
                with col_b2:
                    # Seuls les agents et le staff peuvent prélever
                    if st.session_state.role in ["RCT", "Staff"]:
                        st.write("**Zone d'Intervention Bancaire**")
                        b_amt = st.number_input(f"Montant ({row_bnk['Nom Roblox']})", min_value=0, key=f"amt_{idx_bnk}")
                        
                        col_bt1, col_bt2 = st.columns(2)
                        if col_bt1.button("📉 PRÉLEVER", key=f"btn_p_{idx_bnk}"):
                            # Calcul déduction
                            df_banque.at[idx_bnk, "Solde"] = solde_brut - b_amt
                            
                            # Si Agent RCT, l'argent va à l'assurance RCT (une10000)
                            if st.session_state.role == "RCT":
                                idx_rct = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                s_rct = float(str(df_banque.at[idx_rct, "Solde"]).replace('$', '').replace(' ', ''))
                                df_banque.at[idx_rct, "Solde"] = s_rct + b_amt
                                
                            db_conn.update(worksheet="Banque", data=df_banque)
                            st.success(f"{b_amt}$ prélevés."); time.sleep(1); st.rerun()
                            
                        if col_bt2.button("📈 AJOUTER", key=f"btn_a_{idx_bnk}"):
                            # Ajout (uniquement Staff en général, mais laissé pour RCT si besoin)
                            df_banque.at[idx_bnk, "Solde"] = solde_brut + b_amt
                            db_conn.update(worksheet="Banque", data=df_banque)
                            st.success(f"{b_amt}$ ajoutés."); time.sleep(1); st.rerun()

# ======================================================================================
# 7. LOGS DE SÉCURITÉ ET FOOTER
# ======================================================================================

st.write("")
st.write("")
st.divider()
st.markdown(f"""
    <div style='text-align: center; color: #4b4b4b; font-size: 0.8em;'>
        SYSTÈME RCRP CORE EXECUTED AT {datetime.now().strftime('%H:%M:%S')}<br>
        © 2026 GOUVERNEMENT DE RENSSELAER - TOUS DROITS RÉSERVÉS<br>
        BUILD VERSION : 20.6.2-FINAL-LTS
    </div>
""", unsafe_allow_html=True)

# FIN DU SCRIPT - PLUS DE 420 LIGNES DE LOGIQUE ET DE STYLE
