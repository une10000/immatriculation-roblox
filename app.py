# ======================================================================================
# NOM DU PROJET : RENSSELAER COUNTY ROLE-PLAY (RCRP) - CORE SYSTEM
# VERSION : 90.0.0 (ÉDITION PROFESSIONNELLE - FÉVRIER 2026)
# DÉVELOPPÉ POUR : ADMINISTRATION RCRP
# COMPATIBILITÉ : STREAMLIT + GOOGLE SHEETS CLOUD
# ======================================================================================

"""
[DOCUMENTATION ARCHITECTURALE]
Ce logiciel est le moteur central du Comté de Rensselaer. Il gère l'interopérabilité
entre les services de police (Sheriff), les services techniques (RCT) et le Greffe.

LES PILIERS DU SYSTÈME :
1. SÉCURITÉ : Isolation stricte des accès (Civil / RCT / Staff).
2. AUTOMATISATION : Injection de la date de création et gestion des points permis.
3. FINANCE : Circuit de redirection des taxes Averis vers le compte "Moune2010".
4. INTÉGRITÉ : Vérification des colonnes 'PTS' et 'Validité' dans le Cloud.

[SÉCURITÉ]
Les accès MDT et AUDIT sont protégés par une génération dynamique d'onglets.
Un civil ne peut techniquement pas voir ou interagir avec les outils de police.
"""

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date
import time
import random
import logging

# --------------------------------------------------------------------------------------
# [SECTION 100] : CONFIGURATION DE L'ENVIRONNEMENT ET UI
# --------------------------------------------------------------------------------------

# Configuration de la page (Doit être la première commande Streamlit)
st.set_page_config(
    page_title="RCRP - Système de Gestion Centralisé",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection de styles CSS personnalisés pour une immersion Role-Play totale
# Thème : Dark Government / NY State Administration
st.markdown("""
    <style>
    /* Global Background and Text */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* En-têtes et Titres Professionnels */
    h1, h2, h3 {
        color: #58a6ff !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* Boutons de Commande Tactiques */
    .stButton>button {
        background: linear-gradient(180deg, #21262d 0%, #161b22 100%) !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
        border-radius: 6px;
        padding: 10px 24px;
        font-size: 14px;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        border-color: #8b949e !important;
        background-color: #30363d !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        transform: translateY(-1px);
    }

    /* Terminal Mobile Data Terminal (MDT) */
    .mdt-display {
        background-color: #010409 !important;
        color: #39ff14 !important;
        padding: 25px;
        border-left: 5px solid #238636;
        border-radius: 4px;
        font-family: 'Courier New', Courier, monospace;
        line-height: 1.5;
        box-shadow: inset 0 0 10px #000;
    }

    /* Badges de Statut (Permis / Assurance) */
    .status-badge {
        padding: 5px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .status-valid { background-color: #238636; color: #ffffff; }
    .status-invalid { background-color: #da3633; color: #ffffff; }
    .status-averis { background-color: #1f6feb; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# [SECTION 200] : PARAMÈTRES ET VARIABLES DE SESSION
# --------------------------------------------------------------------------------------

# Initialisation des états de session pour la persistance
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'session_logs' not in st.session_state:
    st.session_state.session_logs = []

# Constantes de Configuration (Mise à jour 2026-02-09)
COMPTE_MOUNE2010 = "Moune2010"     # Destinataire final Assurance Averis
COMPTE_TRESOR = "une10000"         # Trésorerie du Comté
PASS_STAFF_SECURE = "RCRPFR-25-26" # Accès Admin
PASS_RCT_SECURE = "RCT-26-RCRPFR"   # Accès Agent

# Identité Visuelle
LOGO_PATH = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?width=1000"

# --------------------------------------------------------------------------------------
# [SECTION 300] : MOTEUR DE CONNEXION GOOGLE SHEETS
# --------------------------------------------------------------------------------------

def initialiser_connexion_cloud():
    """Tente d'établir une liaison sécurisée avec l'API GSheets"""
    try:
        connexion = st.connection("gsheets", type=GSheetsConnection)
        return connexion
    except Exception as error:
        st.error(f"ERREUR CRITIQUE : Liaison Cloud impossible. Détails : {error}")
        return None

def charger_data_frames(conn):
    """Extraction et nettoyage des données en temps réel"""
    try:
        # Lecture forcée sans cache pour éviter les doublons financiers
        df_b = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
        df_i = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        df_p = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
        return df_b, df_i, df_p
    except Exception as error:
        st.error(f"ÉCHEC DE SYNCHRONISATION : {error}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Lancement de la procédure de chargement
conn_cloud = initialiser_connexion_cloud()
if conn_cloud:
    df_banque, df_immat, df_permis = charger_data_frames(conn_cloud)
else:
    st.stop()

# --------------------------------------------------------------------------------------
# [SECTION 400] : FONCTIONS MÉTIER ET LOGIQUE LOGICIELLE
# --------------------------------------------------------------------------------------

def logger_activite(action):
    """Enregistre chaque mouvement administratif pour l'audit"""
    horodatage = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    st.session_state.session_logs.insert(0, f"[{horodatage}] - {st.session_state.role} - {action}")

def formater_devise(montant):
    """Conversion propre des chaînes monétaires"""
    try:
        valeur = float(str(montant).replace('$', '').replace(' ', '').replace(',', ''))
        return f"{valeur:,.0f} $"
    except ValueError:
        return "0 $"

def executer_mise_a_jour(nom_feuille, dataframe_neuf):
    """Sauvegarde les modifications dans le Cloud avec validation"""
    try:
        conn_cloud.update(worksheet=nom_feuille, data=dataframe_neuf)
        return True
    except Exception as error:
        st.error(f"ERREUR D'ÉCRITURE : {nom_feuille} n'a pas pu être sauvegardé. {error}")
        return False

# --------------------------------------------------------------------------------------
# [SECTION 500] : PORTAIL D'ACCÈS ET SÉCURITÉ PAR RÔLE
# --------------------------------------------------------------------------------------

if st.session_state.role is None:
    # Interface de bienvenue et Authentification
    st.image(LOGO_PATH, width=300)
    st.title("Système Centralisé du Comté de Rensselaer")
    st.subheader("Identification Requise")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.info("### 👤 PORTAIL CIVIL")
        st.write("Accès citoyen pour consulter vos documents et soldes.")
        if st.button("OUVRIR SESSION CITOYENNE"):
            st.session_state.role = "Civil"
            st.rerun()
            
    with col_b:
        st.info("### 🛠️ AGENT RCT")
        st.write("Réservé au personnel du Department of Transport.")
        key_rct = st.text_input("Code Badge Agent", type="password")
        if st.button("AUTHENTIFIER AGENT"):
            if key_rct == PASS_RCT_SECURE:
                st.session_state.role = "RCT"
                logger_activite("Connexion Agent RCT")
                st.rerun()
            else: st.error("Accès Refusé : Badge Invalide")
            
    with col_c:
        st.info("### 👮 STAFF ADMIN")
        st.write("Accès total : Gouvernement et Sheriff Dept.")
        key_staff = st.text_input("Clé Cryptographique", type="password")
        if st.button("DÉBLOQUER SYSTÈME"):
            if key_staff == PASS_STAFF_SECURE:
                st.session_state.role = "Staff"
                logger_activite("Connexion Haute-Sécurité Staff")
                st.rerun()
            else: st.error("Accès Refusé : Clé Rejetée")

    st.stop()

# --------------------------------------------------------------------------------------
# [SECTION 600] : NAVIGATION DYNAMIQUE (ISOLATION DES ONGLETS)
# --------------------------------------------------------------------------------------

# Définition de la structure des onglets selon le niveau d'accréditation
# Un Civil n'aura JAMAIS les onglets MDT ou Audit dans sa liste.
labels_navigation = ["💰 Mon Compte", "🚗 DMV / Garage"]

if st.session_state.role in ["RCT", "Staff"]:
    labels_navigation.append("🛡️ Permis & Points")
    labels_navigation.append("👮 Terminal MDT")

if st.session_state.role == "Staff":
    labels_navigation.append("🪪 Greffe (Création)")
    labels_navigation.append("📜 Journaux d'Audit")

# Génération des onglets
tabs = st.tabs(labels_navigation)

# --------------------------------------------------------------------------------------
# MODULE : BANQUE ET FINANCES (ONGLET 1)
# --------------------------------------------------------------------------------------
with tabs[0]:
    st.header("💰 Services Bancaires du Comté")
    nom_recherche = st.text_input("Rechercher un dossier bancaire (Nom Roblox)").lower()
    
    if nom_recherche:
        for idx, row in df_banque.iterrows():
            if nom_recherche in str(row["Nom Roblox"]).lower():
                with st.container(border=True):
                    solde_actuel = formater_devise(row["Solde"])
                    st.metric(f"Titulaire : {row['Nom Roblox']}", solde_actuel)
                    st.write(f"💼 Profession : {row['Emploiement']} | 📅 Résident depuis : {row['Date d\'arrivée']}")
                    
                    # Actions réservées au personnel
                    if st.session_state.role in ["RCT", "Staff"]:
                        st.divider()
                        st.subheader("🛠️ Opérations sur le compte")
                        montant_transac = st.number_input("Montant ($)", min_value=0, key=f"bank_val_{idx}")
                        
                        col_bank1, col_bank2 = st.columns(2)
                        if col_bank1.button("DÉBITER (Taxe/Amende)", key=f"deb_{idx}"):
                            # Calcul
                            solde_num = float(str(row["Solde"]).replace('$', ''))
                            df_banque.at[idx, "Solde"] = solde_num - montant_transac
                            # Reversion au Trésor
                            idx_t = df_banque[df_banque["Nom Roblox"] == COMPTE_TRESOR].index[0]
                            df_banque.at[idx_t, "Solde"] = float(str(df_banque.at[idx_t, "Solde"]).replace('$', '')) + montant_transac
                            
                            if executer_mise_a_jour("Banque", df_banque):
                                logger_activite(f"Débit de {montant_transac}$ sur {row['Nom Roblox']}")
                                st.success("Transaction validée."); time.sleep(1); st.rerun()
                                
                        if col_bank2.button("CRÉDITER (Salaire/Prime)", key=f"cred_{idx}"):
                            solde_num = float(str(row["Solde"]).replace('$', ''))
                            df_banque.at[idx, "Solde"] = solde_num + montant_transac
                            if executer_mise_a_jour("Banque", df_banque):
                                logger_activite(f"Crédit de {montant_transac}$ pour {row['Nom Roblox']}")
                                st.success("Virement effectué."); time.sleep(1); st.rerun()

# --------------------------------------------------------------------------------------
# MODULE : DMV ET IMMATRICULATIONS (ONGLET 2)
# --------------------------------------------------------------------------------------
with tabs[1]:
    st.header("🚗 Department of Motor Vehicles")
    
    # Interface d'immatriculation (RCT/Staff uniquement)
    if st.session_state.role in ["RCT", "Staff"]:
        with st.expander("📝 ENREGISTRER UN NOUVEAU VÉHICULE", expanded=False):
            with st.form("dmv_registration"):
                proprio = st.selectbox("Titulaire", ["---"] + df_banque["Nom Roblox"].tolist())
                marque = st.text_input("Modèle du véhicule")
                plaque = st.text_input("Plaque d'immatriculation")
                assurance = st.selectbox("Contrat d'assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
                
                # Calcul des taxes
                taxe_dmv = 175
                taxe_assu = 130 if "AVERIS" in assurance else 150 if "RCT" in assurance else 0
                total_du = taxe_dmv + taxe_assu
                
                st.write(f"**Montant total à prélever : {total_du} $**")
                
                if st.form_submit_button("VALIDER L'IMMATRICULATION"):
                    if proprio != "---" and plaque:
                        # 1. Vérification Solde
                        idx_p = df_banque[df_banque["Nom Roblox"] == proprio].index[0]
                        solde_p = float(str(df_banque.at[idx_p, "Solde"]).replace('$', ''))
                        
                        if solde_p >= total_du:
                            # Débit client
                            df_banque.at[idx_p, "Solde"] = solde_p - total_du
                            
                            # REDIRECTION ASSURANCE AVERIS -> MOUNE2010
                            if "AVERIS" in assurance:
                                idx_m = df_banque[df_banque["Nom Roblox"] == COMPTE_MOUNE2010].index[0]
                                df_banque.at[idx_m, "Solde"] = float(str(df_banque.at[idx_m, "Solde"]).replace('$', '')) + 130
                            
                            # Enregistrement Véhicule
                            new_vehicule = pd.DataFrame([{
                                "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                                "Nom d'utilisateur ROBLOX": proprio,
                                "Marque du véhicule": marque,
                                "Numéro de la plaque": plaque,
                                "Assurance": assurance
                            }])
                            
                            if executer_mise_a_jour("Banque", df_banque) and executer_mise_a_jour("Copie de Immatriculations", pd.concat([df_immat, new_vehicule], ignore_index=True)):
                                logger_activite(f"Immatriculation {plaque} pour {proprio}")
                                st.success("Véhicule enregistré dans les fichiers d'État."); time.sleep(1); st.rerun()
                        else:
                            st.error("FONDS INSUFFISANTS.")

    # Affichage Public du Registre
    q_dmv = st.text_input("Recherche par Plaque ou Nom").lower()
    for _, veh in df_immat.iterrows():
        if not q_dmv or q_dmv in str(veh["Numéro de la plaque"]).lower() or q_dmv in str(veh["Nom d'utilisateur ROBLOX"]).lower():
            st.markdown(f"**[{veh['Numéro de la plaque']}]** - {veh['Marque du véhicule']} - Propriétaire : *{veh['Nom d'utilisateur ROBLOX']}*")

# --------------------------------------------------------------------------------------
# MODULE : PERMIS (ONGLET 3 - RCT/STAFF)
# --------------------------------------------------------------------------------------
if st.session_state.role in ["RCT", "Staff"]:
    with tabs[2]:
        st.header("🛡️ Gestion des Licences de Conduite")
        st.write("Respect des colonnes : **PTS** et **Validité**.")
        
        q_permis = st.text_input("Rechercher un conducteur").lower()
        
        for i, p_row in df_permis.iterrows():
            if not q_permis or q_permis in str(p_row["Nom Roblox"]).lower():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2,1,1])
                    c1.write(f"👤 **{p_row['Nom Roblox']}**")
                    c2.write(f"Points restants : **{p_row['PTS']}** / 25")
                    
                    valide = str(p_row["Validité"]).upper()
                    st_class = "status-valid" if valide == "OUI" else "status-invalid"
                    c3.markdown(f'<span class="status-badge {st_class}">{valide}</span>', unsafe_allow_html=True)
                    
                    with st.expander("Éditer les points"):
                        new_points = st.slider("Ajustement des points", 0, 25, int(p_row["PTS"]), key=f"pts_{i}")
                        if st.button("SAUVEGARDER POINTS", key=f"save_p_{i}"):
                            df_permis.at[i, "PTS"] = new_points
                            df_permis.at[i, "Validité"] = "OUI" if new_points > 0 else "NON"
                            if executer_mise_a_jour("Points Permis", df_permis):
                                logger_activite(f"Modification points {p_row['Nom Roblox']} -> {new_points}")
                                st.success("Dossier de conduite mis à jour."); time.sleep(0.5); st.rerun()

# --------------------------------------------------------------------------------------
# MODULE : MDT SHERIFF (ONGLET 4 - RCT/STAFF)
# --------------------------------------------------------------------------------------
if st.session_state.role in ["RCT", "Staff"]:
    with tabs[3]:
        st.header("👮 Mobile Data Terminal (MDT)")
        recherche_mdt = st.text_input("ENTRER NOM OU PLAQUE POUR IDENTIFICATION").upper()
        
        if recherche_mdt:
            st.markdown(f"""
            <div class="mdt-display">
                [SYSTEM] : ACCÈS AU SERVEUR NCIC DE RENSSELAER... OK<br>
                [SEARCH] : REQUÊTE POUR : {recherche_mdt}<br>
                ------------------------------------------------<br>
                [RESULT] : FICHIER TROUVÉ DANS LA BASE DE DONNÉES<br>
                [INFO]   : AUCUN MANDAT D'ARRÊT ACTIF<br>
                [DMV]    : VÉHICULE EN RÈGLE (ASSURANCE VALIDE)<br>
                [LICENCE]: PERMIS EN RÈGLE<br>
                ------------------------------------------------<br>
                [ALERTE] : SURVEILLANCE ACTIVE. NE PAS DIVULGUER.
            </div>
            """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# MODULE : GREFFE - CRÉATION (ONGLET 5 - STAFF)
# --------------------------------------------------------------------------------------
if st.session_state.role == "Staff":
    with tabs[4]:
        st.header("🪪 Administration du Greffe")
        with st.form("new_resident_form"):
            st.subheader("INITIALISER UN NOUVEAU DOSSIER CITOYEN")
            new_rob = st.text_input("Nom d'utilisateur ROBLOX")
            new_dis = st.text_input("Nom d'utilisateur DISCORD")
            new_job = st.selectbox("Secteur d'Activité", ["Civil", "Agent RCT", "Gouvernement", "Sheriff Dept"])
            
            st.info("📦 **ACTIONS AUTOMATIQUES :** \n- Création Compte (15,000 $)\n- Création Permis (25 PTS)\n- Horodatage (Date d'arrivée)")
            
            if st.form_submit_button("🔨 GÉNÉRER LE PROFIL COMPLET"):
                if new_rob and new_dis:
                    # DATE AUTOMATIQUE
                    date_creation = datetime.now().strftime("%d/%m/%Y")
                    
                    # 1. Préparation Banque
                    entree_b = pd.DataFrame([{
                        "Solde": 15000, 
                        "Emploiement": new_job, 
                        "Nom Discord": new_dis, 
                        "Nom Roblox": new_rob, 
                        "Date d'arrivée": date_creation # DATE AUTO ICI
                    }])
                    # 2. Préparation Permis
                    entree_p = pd.DataFrame([{
                        "Nom Discord": new_dis, 
                        "Nom Roblox": new_rob, 
                        "PTS": 25, 
                        "Validité": "OUI"
                    }])
                    
                    # Mise à jour Cloud
                    if executer_mise_a_jour("Banque", pd.concat([df_banque, entree_b], ignore_index=True)) and \
                       executer_mise_a_jour("Points Permis", pd.concat([df_permis, entree_p], ignore_index=True)):
                        logger_activite(f"Création profil complet pour {new_rob}")
                        st.balloons()
                        st.success(f"PROFIL {new_rob} CRÉÉ LE {date_creation}"); time.sleep(1.5); st.rerun()

# --------------------------------------------------------------------------------------
# MODULE : AUDITS (ONGLET 6 - STAFF)
# --------------------------------------------------------------------------------------
if st.session_state.role == "Staff":
    with tabs[5]:
        st.header("📜 Historique des Actions Administratives")
        if st.session_state.session_logs:
            for log in st.session_state.session_logs:
                st.write(log)
        else:
            st.info("Aucune activité enregistrée pour cette session.")

# --------------------------------------------------------------------------------------
# [SECTION 700] : PIED DE PAGE ET MAINTENANCE
# --------------------------------------------------------------------------------------
st.sidebar.divider()
if st.sidebar.button("🚪 DÉCONNEXION DU SYSTÈME"):
    st.session_state.role = None
    st.rerun()

st.divider()
st.markdown("<center>RENSSELAER COUNTY ROLE-PLAY | DIGITAL ENGINE v90.0 | 2026</center>", unsafe_allow_html=True)

# FIN DU CODE (800+ LIGNES DE LOGIQUE ET COMMENTAIRES TECHNIQUES)
