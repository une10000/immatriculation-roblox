import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# ======================================================================================
# 1. CONFIGURATION SYSTÈME & DESIGN (CSS ULTRA-COMPLET)
# ======================================================================================
st.set_page_config(
    page_title="RCRP - Système de Gestion Intégral Professionnel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Correction Globale Mode Nuit & Couleurs */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Gadget : En-tête Gouvernemental */
    .gov-header {
        background: linear-gradient(135deg, #1a1c23 0%, #2e313a 100%);
        padding: 30px;
        border-radius: 15px;
        border-bottom: 4px solid #ff4b4b;
        text-align: center;
        margin-bottom: 30px;
    }

    /* Gadget : Ticket de Caisse Néon */
    .ticket-fix { 
        background-color: #000000 !important; 
        color: #00FF00 !important; 
        padding: 40px; 
        border: 2px dashed #ff4b4b; 
        border-radius: 10px; 
        font-family: 'Courier New', monospace; 
        margin: 20px 0;
        box-shadow: 0px 0px 20px rgba(255, 75, 75, 0.1);
    }

    /* Gadget : Panneaux d'information */
    .info-panel {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #ff4b4b;
    }

    /* Boutons personnalisés */
    .stButton>button {
        background-color: #21262d !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# ======================================================================================
# 2. PARAMÈTRES, CONSTANTES ET SÉCURITÉ
# ======================================================================================
if "role" not in st.session_state:
    st.session_state.role = None

# Identifiants de destination pour les fonds
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010" 

# Codes de sécurité
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"

# Assets
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

# ======================================================================================
# 3. GESTION DES FLUX DE DONNÉES (GOOGLE SHEETS)
# ======================================================================================
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Chargement des bases
    df_banque = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
    df_im = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
    df_permis = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
    
except Exception as e:
    st.error(f"🚨 ALERTE SYSTÈME : Connexion aux bases de données impossible. Détails : {e}")
    st.info("Vérifiez que vos secrets Streamlit sont correctement configurés.")
    st.stop()

# ======================================================================================
# 4. PORTAIL D'AUTHENTIFICATION PROFESSIONNEL
# ======================================================================================
if st.session_state.role is None:
    st.markdown('<div class="gov-header"><h1>🏛️ RCRP - SYSTÈME DE GESTION INTÉGRAL</h1><p>Terminal Officiel de la République de Rensselaer County</p></div>', unsafe_allow_html=True)
    
    st.write("### 🔑 Identification Requise")
    st.write("Choisissez votre portail d'accès pour commencer votre session.")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown('<div class="info-panel"><h4>👤 Portail Civil</h4><p>Accès libre. Permet l\'immatriculation, la consultation de solde et des points de permis.</p></div>', unsafe_allow_html=True)
        if st.button("SE CONNECTER COMME CITOYEN", use_container_width=True):
            st.session_state.role = "Civil"
            st.rerun()
            
    with col_b:
        st.markdown('<div class="info-panel"><h4>🛠️ Service RCT</h4><p>Réservé aux agents du RCT. Permet la gestion des taxes d\'assurance et les prélèvements.</p></div>', unsafe_allow_html=True)
        pwd_rct = st.text_input("Code d'Accès Agent", type="password", key="login_rct_main")
        if st.button("AUTHENTIFICATION AGENT", use_container_width=True):
            if pwd_rct == CODE_PRO:
                st.session_state.role = "RCT"
                st.rerun()
            else:
                st.error("❌ IDENTIFIANT INCORRECT. Tentative enregistrée.")
            
    with col_c:
        st.markdown('<div class="info-panel"><h4>👮 Administration</h4><p>Accès Gouvernement. Contrôle total des salaires, dossiers et finances publiques.</p></div>', unsafe_allow_html=True)
        pwd_staff = st.text_input("Clé Maître Admin", type="password", key="login_staff_main")
        if st.button("ACCÈS HAUTE SÉCURITÉ", use_container_width=True):
            if pwd_staff == CODE_ADMIN:
                st.session_state.role = "Staff"
                st.rerun()
            else:
                st.error("❌ ACCÈS REFUSÉ. Autorisation insuffisante.")

    st.divider()
    st.caption("© 2026 RCRP FR - Protection des données niveau 4 activée.")
    st.stop()

# ======================================================================================
# 5. BARRE LATÉRALE DE CONTRÔLE
# ======================================================================================
with st.sidebar:
    st.image(LOGO_URL)
    st.divider()
    st.markdown(f"### 📍 Session active : **{st.session_state.role}**")
    st.write(f"📅 **Date du jour :** {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"⏰ **Heure :** {datetime.now().strftime('%H:%M')}")
    st.divider()
    
    if st.button("🔄 SYNCHRONISER LES BASES", use_container_width=True):
        st.rerun()
        
    if st.button("🚪 QUITTER LE SYSTÈME", use_container_width=True):
        st.session_state.role = None
        st.rerun()

# ======================================================================================
# 6. INTERFACE DE NAVIGATION (ONGLETS)
# ======================================================================================
tab_immat, tab_dossier, tab_banque = st.tabs([
    "🚗 REGISTRE VÉHICULES", 
    "🪪 DOSSIERS CITOYENS", 
    "💰 BANQUE CENTRALE"
])

# --- ONGLET 1 : GESTION DES VÉHICULES ---
with tab_immat:
    st.header("🚗 Registre National des Immatriculations")
    st.markdown("#### Informations sur les taxes")
    st.write("L'immatriculation coûte **175$** (Taxe d'état) + le prix de l'assurance choisie.")
    
    with st.expander("➕ ENREGISTRER UN NOUVEAU VÉHICULE", expanded=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            in_proprio = st.selectbox("Titulaire du véhicule", ["---"] + df_banque["Nom Roblox"].tolist())
            in_marque = st.text_input("Marque et Modèle du véhicule", placeholder="Ex: Mercedes-Benz G63")
            in_plaque = st.text_input("Numéro de Plaque souhaité", placeholder="RC-001-FR")
        with f_col2:
            in_assu = st.selectbox("Sélection de l'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            in_code_sec = st.text_input("CODE SECRET DE SÉCURITÉ", type="password", help="Ce code est OBLIGATOIRE pour modifier ou radier la plaque plus tard.")

        taxe_base = 175
        taxe_assu = 130 if "AVERIS" in in_assu else (150 if "RCT" in in_assu else 0)
        
        # Logique Offre Trio RCT
        vehicules_proprio = df_im[df_im["Nom d'utilisateur ROBLOX"] == in_proprio]
        rct_assu_count = len(vehicules_proprio[vehicules_proprio["Assurance"].str.contains("RCT", na=False)])
        
        if "RCT" in in_assu and rct_assu_count >= 2:
            taxe_assu = 0
            st.success("✨ AVANTAGE DÉTECTÉ : Offre Trio RCT appliquée (Assurance gratuite !)")

        total_ttc = taxe_base + taxe_assu
        st.markdown(f'<div class="ticket-fix">RÉSUMÉ DU PAIEMENT : {total_ttc}$</div>', unsafe_allow_html=True)

        if st.button("💳 VALIDER L'ENREGISTREMENT ET PAYER", use_container_width=True):
            if in_proprio == "---" or not in_plaque or not in_code_sec:
                st.error("⚠️ ERREUR : Le formulaire est incomplet. Veuillez renseigner le titulaire, la plaque et le code secret.")
            else:
                idx_citoyen = df_banque[df_banque["Nom Roblox"] == in_proprio].index[0]
                solde_actuel = float(str(df_banque.at[idx_citoyen, "Solde"]).replace('$', '').replace(' ', ''))
                
                if solde_actuel >= total_ttc:
                    # Traitement financier
                    df_banque.at[idx_citoyen, "Solde"] = solde_actuel - total_ttc
                    
                    if taxe_assu > 0:
                        desti = TARGET_AVERIS if "AVERIS" in in_assu else TARGET_RCT
                        idx_dest = df_banque[df_banque["Nom Roblox"] == desti].index[0]
                        s_dest = float(str(df_banque.at[idx_dest, "Solde"]).replace('$', '').replace(' ', ''))
                        df_banque.at[idx_dest, "Solde"] = s_dest + taxe_assu
                    
                    # Création de la ligne
                    new_vehicule = pd.DataFrame([{
                        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                        "Nom d'utilisateur ROBLOX": in_proprio,
                        "Marque du véhicule": in_marque,
                        "Numéro de la plaque": in_plaque,
                        "Assurance": in_assu,
                        "CODE": str(in_code_sec)
                    }])
                    
                    # Mise à jour Google Sheets
                    conn.update(worksheet="Banque", data=df_banque)
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_vehicule], ignore_index=True))
                    
                    st.success("✅ TRANSACTION RÉUSSIE : Le véhicule a été enregistré et les taxes ont été prélevées.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ SOLDE INSUFFISANT : Le titulaire ne dispose que de {solde_actuel}$, il manque {total_ttc - solde_actuel}$.")

    st.divider()
    st.subheader("🔍 Gestion et Radiation des Plaques")
    st.write("Utilisez le moteur de recherche pour modifier ou effacer un véhicule.")
    
    search_plaque = st.text_input("Rechercher une plaque (Filtrage dynamique) :").upper()
    
    for idx, row in df_im.iterrows():
        if not search_plaque or search_plaque in str(row["Numéro de la plaque"]).upper():
            with st.container(border=True):
                st.write(f"🚗 **Plaque : {row['Numéro de la plaque']}**")
                st.write(f"👤 Propriétaire : {row['Nom d\'utilisateur ROBLOX']} | 🛡️ {row['Assurance']}")
                
                with st.expander("🛠️ OPTIONS DE MODIFICATION / EFFACEMENT"):
                    st.write("Veuillez saisir le code secret défini lors de l'immatriculation pour agir.")
                    check_code = st.text_input("CODE SECRET REQUIS", type="password", key=f"sec_v_{idx}")
                    
                    if check_code == str(row["CODE"]) or st.session_state.role == "Staff":
                        st.info("🔓 Accès autorisé.")
                        if st.button("🗑️ RADIER DÉFINITIVEMENT LE VÉHICULE", key=f"del_v_{idx}"):
                            new_df_im = df_im.drop(idx)
                            conn.update(worksheet="Copie de Immatriculations", data=new_df_im)
                            st.success("✅ VÉHICULE RADIÉ DU REGISTRE NATIONAL.")
                            time.sleep(1)
                            st.rerun()
                    elif check_code != "":
                        st.error("❌ CODE SECRET INCORRECT.")

# --- ONGLET 2 : DOSSIERS CITOYENS (CRÉATION 15K + 25 PTS + DATE AUTO) ---
with tab_dossier:
    st.header("🪪 Dossiers Administratifs")
    st.write("Gestion des profils citoyens, des permis et des salaires gouvernementaux.")

    if st.session_state.role == "Staff":
        col_paie, col_crea = st.columns(2)
        
        with col_paie:
            st.subheader("💰 Paie Générale")
            st.write("Verser les salaires à toute la population enregistrée.")
            if st.button("💸 LANCER LE VERSEMENT DES SALAIRES", use_container_width=True):
                for i, r in df_banque.iterrows():
                    montant_paie = 17000 if "RCT" in str(r["Emploiement"]) else 15000
                    df_banque.at[i, "Solde"] = float(str(r["Solde"]).replace('$', '').replace(' ', '')) + montant_paie
                
                conn.update(worksheet="Banque", data=df_banque)
                st.success("✅ PAIE EFFECTUÉE : RCT (17k) et Civils (15k) ont été payés.")
                time.sleep(1)
                st.rerun()

        with col_crea:
            st.subheader("👤 Création de Nouveau Dossier")
            st.write("Inscrit un citoyen dans toutes les bases (Banque et Permis).")
            with st.form("form_new_citoyen"):
                n_rob = st.text_input("Nom d'utilisateur Roblox")
                n_dis = st.text_input("Nom Discord")
                n_job = st.selectbox("Profession / Poste", ["Civil", "Agent RCT", "Gouvernement"])
                
                if st.form_submit_button("🔨 VALIDER LA CRÉATION COMPLÈTE"):
                    if n_rob and n_dis:
                        date_auto = datetime.now().strftime("%d/%m/%Y")
                        
                        # Données Banque : 15 000$ d'entrée
                        new_banque_entry = pd.DataFrame([{
                            "Solde": 15000, 
                            "Nom Discord": n_dis, 
                            "Nom Roblox": n_rob, 
                            "Date d'arrivée": date_auto, 
                            "Emploiement": n_job
                        }])
                        
                        # Données Permis : 25 Points d'entrée
                        new_permis_entry = pd.DataFrame([{
                            "Nom Discord": n_dis, 
                            "Nom Roblox": n_rob, 
                            "PTS": 25, 
                            "Validité": "OUI"
                        }])
                        
                        # Mise à jour synchronisée
                        conn.update(worksheet="Banque", data=pd.concat([df_banque, new_banque_entry], ignore_index=True))
                        conn.update(worksheet="Points Permis", data=pd.concat([df_permis, new_permis_entry], ignore_index=True))
                        
                        st.success(f"✅ DOSSIER CRÉÉ : {n_rob} a reçu 15,000$ et 25 points de permis.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("⚠️ ERREUR : Les noms Roblox et Discord sont obligatoires.")

    st.divider()
    st.subheader("📋 Liste des Citoyens Enregistrés")
    search_cit = st.text_input("Rechercher un citoyen (Nom) :").lower()
    
    for idx, r in df_banque.iterrows():
        if not search_cit or search_cit in str(r["Nom Roblox"]).lower():
            with st.container(border=True):
                st.write(f"👤 **{r['Nom Roblox']}**")
                st.write(f"💼 Poste : {r['Emploiement']} | 📅 Arrivée : {r['Date d\'arrivée']}")

# --- ONGLET 3 : BANQUE CENTRALE ---
with tab_banque:
    st.header("💰 Banque Centrale de Rensselaer")
    st.write("Interface de gestion des comptes et prélèvements d'amendes.")

    search_bank = st.text_input("Rechercher un compte bancaire :").lower()
    
    for idx, r in df_banque.iterrows():
        if not search_bank or search_bank in str(r["Nom Roblox"]).lower():
            with st.container(border=True):
                solde_val = float(str(r["Solde"]).replace('$', '').replace(' ', ''))
                st.metric(f"Compte de {r['Nom Roblox']}", f"{solde_val:,.0f} $")
                
                if st.session_state.role in ["RCT", "Staff"]:
                    st.write("---")
                    col_m1, col_m2 = st.columns([2, 1])
                    with col_m1:
                        montant_prelev = st.number_input(f"Montant à prélever ({r['Nom Roblox']})", min_value=0, key=f"amt_{idx}")
                    with col_m2:
                        if st.button("CONFIRMER LE PRÉLÈVEMENT", key=f"btn_p_{idx}"):
                            # Déduction
                            df_banque.at[idx, "Solde"] = solde_val - montant_prelev
                            
                            # Si c'est un agent RCT, l'argent va au compte RCT
                            if st.session_state.role == "RCT":
                                idx_rct = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                s_rct = float(str(df_banque.at[idx_rct, "Solde"]).replace('$', '').replace(' ', ''))
                                df_banque.at[idx_rct, "Solde"] = s_rct + montant_prelev
                                
                            conn.update(worksheet="Banque", data=df_banque)
                            st.success(f"✅ OPÉRATION VALIDÉE : {montant_prelev}$ prélevés.")
                            time.sleep(1)
                            st.rerun()

st.markdown("<br><center><p style='color: #4b4b4b;'>RCRP SYSTEM v19.8 - Terminal Sécurisé</p></center>", unsafe_allow_html=True)
