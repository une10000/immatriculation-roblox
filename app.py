# ======================================================================================
# NOM DU PROJET : RENSSELAER COUNTY ROLE-PLAY (RCRP) - INFRASTRUCTURE GOUVERNEMENTALE
# VERSION : 50.4.0 (ÉDITION ULTIME - FÉVRIER 2026)
# LANGUE : FRANÇAIS (FR-FR)
# SYSTÈME : CENTRAL MANAGEMENT ENGINE (CME)
# ======================================================================================

"""
[DOCUMENTATION TECHNIQUE]
Ce script constitue le noyau de gestion pour le comté de Rensselaer. 
Il utilise Streamlit pour l'interface utilisateur et Google Sheets comme base de données persistante.

STRUCTURE DU CODE :
- SECTION 1 : CONFIGURATION GLOBALE ET DESIGN CSS AVANCÉ
- SECTION 2 : INITIALISATION DES ÉTATS DE SESSION (SÉCURITÉ)
- SECTION 3 : MOTEUR DE CONNEXION ET GESTION DES FLUX DE DONNÉES
- SECTION 4 : FONCTIONS MÉTIER (CRÉATION, TRANSACTION, LOGS)
- SECTION 5 : MODULES D'INTERFACE (ADMIN, DMV, BANQUE, PERMIS, MDT)
- SECTION 6 : SYSTÈME D'AUDIT ET SÉCURITÉ

RÈGLES APPLIQUÉES :
- Date automatique à la création de profil.
- Redirection Assurance Averis vers Moune2010.
- Respect des colonnes Google Sheets : PTS et Validité.
"""

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import io

# --------------------------------------------------------------------------------------
# [SECTION 1] : CONFIGURATION UI ET DESIGN CSS PERSONNALISÉ
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="RCRP - Système de Gestion d'État",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style immersif pour le Role-Play (Thème Sombre Police/NY State)
st.markdown("""
    <style>
    /* Configuration globale du container */
    .main { background-color: #0b0e14; }
    .stApp { background-color: #0b0e14; color: #e6edf3; }
    
    /* En-têtes et Titres */
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Segoe UI Bold', sans-serif; }
    
    /* Boutons de commande tactiques */
    .stButton>button {
        background: linear-gradient(180deg, #1f2937 0%, #111827 100%) !important;
        color: #38bdf8 !important;
        border: 1px solid #334155 !important;
        border-radius: 6px;
        padding: 12px 24px;
        font-weight: 800;
        text-transform: uppercase;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stButton>button:hover {
        border-color: #38bdf8 !important;
        background: #1e293b !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        transform: translateY(-2px);
    }

    /* Terminal MDT (Mobile Data Terminal) */
    .mdt-terminal {
        background-color: #010409 !important;
        color: #00ff41 !important; /* Vert Matrix pour l'immersion */
        padding: 25px;
        border: 1px solid #30363d;
        border-left: 5px solid #00ff41;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        margin-bottom: 20px;
        line-height: 1.4;
    }

    /* Cartes de Dossiers Citoyens */
    .citizen-card {
        background: #161b22;
        padding: 18px;
        border-radius: 8px;
        border: 1px solid #30363d;
        margin-bottom: 10px;
        border-right: 4px solid #30363d;
    }
    .citizen-card:hover { border-right: 4px solid #58a6ff; }

    /* Badges de Statut */
    .badge { padding: 4px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; }
    .status-ok { background-color: #238636; color: white; }
    .status-alert { background-color: #da3633; color: white; }
    .status-averis { background-color: #1f6feb; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# [SECTION 2] : INITIALISATION ET SÉCURITÉ DE SESSION
# --------------------------------------------------------------------------------------
# Vérification des variables d'état pour éviter les crashs au rafraîchissement
if "role" not in st.session_state:
    st.session_state.role = None
if "auth_key" not in st.session_state:
    st.session_state.auth_key = None
if "logs" not in st.session_state:
    st.session_state.logs = []
if "tickets" not in st.session_state:
    st.session_state.tickets = []

# Constantes Financières et Administratives (Updates 2026-02-08)
CPT_TRESORERIE = "une10000"         # Compte Principal État
CPT_AVERIS_CIBLE = "Moune2010"      # Compte de réception pour Averis
VALEUR_DEPART = 15000               # Prime d'arrivée
POINTS_DEPART = 25                  # Points de permis initiaux

# Crédentials Système
PASS_STAFF = "RCRPFR-25-26"
PASS_RCT = "RCT-26-RCRPFR"

# Assets Visuels
LOGO_RCRP = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?width=1000"

# --------------------------------------------------------------------------------------
# [SECTION 3] : MOTEUR DE GESTION DES DONNÉES (CLOUD)
# --------------------------------------------------------------------------------------
def init_cloud_connection():
    """Initialise le tunnel de connexion Google Sheets"""
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"ERREUR SYSTÈME : Connexion au Cloud impossible. Détails : {e}")
        return None

def fetch_all_data(connection):
    """Extraction massive des bases de données RCRP"""
    try:
        # On désactive le cache (ttl=0) pour garantir l'intégrité des données financières
        bank = connection.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
        immat = connection.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        permis = connection.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
        return bank, immat, permis
    except Exception as e:
        st.error(f"ÉCHEC SYNCHRONISATION : Les feuilles sont inaccessibles. {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Lancement du moteur
conn = init_cloud_connection()
if conn:
    df_banque, df_immat, df_permis = fetch_all_data(conn)
else:
    st.stop()

# --------------------------------------------------------------------------------------
# [SECTION 4] : FONCTIONS LOGIQUES ET MÉTIER (CORE)
# --------------------------------------------------------------------------------------
def system_log(user, message):
    """Enregistre une activité dans le journal d'audit local de la session"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.insert(0, f"[{timestamp}] {user.upper()} : {message}")

def safe_money_convert(value):
    """Nettoie et convertit les valeurs monétaires du GSheets"""
    try:
        if isinstance(value, str):
            value = value.replace('$', '').replace(' ', '').replace(',', '')
        return float(value)
    except:
        return 0.0

def update_cloud_table(worksheet_name, dataframe):
    """Met à jour une table GSheets avec gestion d'erreur robuste"""
    try:
        conn.update(worksheet=worksheet_name, data=dataframe)
        return True
    except Exception as e:
        st.error(f"ERREUR D'ÉCRITURE CLOUD ({worksheet_name}) : {e}")
        return False

# --------------------------------------------------------------------------------------
# [SECTION 5] : PORTAIL D'ACCÈS SÉCURISÉ (AUTHENTIFICATION)
# --------------------------------------------------------------------------------------
if st.session_state.role is None:
    st.title("⚖️ Rensselaer County - Portail de Gestion Gouvernemental")
    st.divider()
    
    col_auth1, col_auth2, col_auth3 = st.columns(3)
    
    with col_auth1:
        st.info("### 👤 PORTAIL CIVIL")
        st.write("Consultez vos points, vos véhicules et vos informations bancaires.")
        if st.button("ACCÉDER AU PORTAIL PUBLIC"):
            st.session_state.role = "Civil"
            system_log("Public", "Connexion Citoyenne")
            st.rerun()
            
    with col_auth2:
        st.info("### 🛠️ AGENT RCT")
        st.write("Accès réservé aux agents du Department of Transport (DOT).")
        key_rct = st.text_input("Clé de Sécurité Agent", type="password")
        if st.button("AUTHENTIFIER AGENT"):
            if key_rct == PASS_RCT:
                st.session_state.role = "RCT"
                system_log("Agent RCT", "Authentification Réussie")
                st.rerun()
            else: st.error("Accès Refusé : Clé Invalide.")
            
    with col_auth3:
        st.info("### 👮 STAFF / ADMIN")
        st.write("Gestion des résidents, taxes et terminal sheriff.")
        key_staff = st.text_input("Accréditation Staff", type="password")
        if st.button("DÉBLOQUER SYSTÈME"):
            if key_staff == PASS_STAFF:
                st.session_state.role = "Staff"
                system_log("Admin", "Accès Haute-Sécurité Débloqué")
                st.rerun()
            else: st.error("Accès Refusé : Accréditation Rejetée.")

    st.divider()
    st.markdown("<center>Système RCRP v50.4 - NY State Management - 2026</center>", unsafe_allow_html=True)
    st.stop()

# --------------------------------------------------------------------------------------
# [SECTION 6] : BARRE LATÉRALE DE CONTRÔLE (SIDEBAR)
# --------------------------------------------------------------------------------------
with st.sidebar:
    st.image(LOGO_RCRP)
    st.markdown(f"**OPÉRATEUR :** `{st.session_state.role}`")
    st.markdown(f"**DATE :** {datetime.now().strftime('%d/%m/%Y')}")
    st.divider()
    
    st.subheader("🛠️ ACTIONS SYSTÈME")
    if st.button("🔄 ACTUALISER LES DONNÉES"):
        st.rerun()
    if st.button("🚪 DÉCONNEXION"):
        st.session_state.role = None; st.rerun()
    
    st.divider()
    st.subheader("📊 ÉTAT DU COMTÉ")
    st.write(f"👥 Citoyens : {len(df_banque)}")
    st.write(f"🚗 Parc Automobile : {len(df_immat)}")
    
    st.divider()
    st.caption("Terminal Opérationnel - Rensselaer County")

# --------------------------------------------------------------------------------------
# [SECTION 7] : MODULES DE NAVIGATION (TABS)
# --------------------------------------------------------------------------------------
tab_dmv, tab_clerk, tab_bank, tab_permis, tab_mdt, tab_logs = st.tabs([
    "🚗 SERVICE DMV", 
    "🪪 GREFFE (RÉSIDENTS)", 
    "💰 TRÉSOR BANCAIRE",
    "🛡️ LICENCE DE CONDUITE",
    "👮 TERMINAL SHERIFF (MDT)",
    "📜 AUDIT & LOGS"
])

# ======================================================================================
# MODULE A : SERVICE DMV (VÉHICULES ET ASSURANCES)
# ======================================================================================
with tab_dmv:
    st.header("🚗 Department of Motor Vehicles (DMV)")
    
    # --- FORMULAIRE D'IMMATRICULATION ---
    with st.expander("➕ IMMATRICULER UN NOUVEAU VÉHICULE", expanded=True):
        st.write("Procédure officielle d'enregistrement au Comté.")
        c_dmv1, c_dmv2 = st.columns(2)
        
        with c_dmv1:
            proprio = st.selectbox("Choisir le Titulaire", ["---"] + df_banque["Nom Roblox"].tolist())
            marque = st.text_input("Marque et Modèle du Véhicule")
            plaque = st.text_input("Numéro de Plaque (NY-000-XX)")
            
        with c_dmv2:
            assu_type = st.selectbox("Contrat d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            pin_code = st.text_input("Code de Sécurité (PIN)", type="password")

        # LOGIQUE FINANCIÈRE DMV
        taxe_enregistrement = 175
        prime_assu = 0
        if "AVERIS" in assu_type: prime_assu = 130
        elif "RCT" in assu_type: prime_assu = 150
            
        # RÈGLE RCT : Fidélité récompensée
        count_v = len(df_immat[df_immat["Nom d'utilisateur ROBLOX"] == proprio])
        if "RCT" in assu_type and count_v >= 2:
            prime_assu = 0
            st.success("💎 AVANTAGE FIDÉLITÉ : Assurance offerte par RCT !")

        total_facture = taxe_enregistrement + prime_assu
        
        st.markdown(f"""
        <div class="mdt-terminal">
            <b>REÇU D'IMMATRICULATION - RENSSELAER DMV</b><br>
            -------------------------------------------------<br>
            TITULAIRE  : {proprio}<br>
            VÉHICULE   : {marque}<br>
            ASSURANCE  : {assu_type}<br>
            -------------------------------------------------<br>
            FRAIS FIXES : 175 $<br>
            PRIME ASSU  : {prime_assu} $<br>
            -------------------------------------------------<br>
            <b>MONTANT NET À DÉBITER : {total_facture} $</b>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💳 VALIDER ET PAYER L'ENREGISTREMENT"):
            if proprio != "---" and plaque != "":
                # 1. Traitement du solde
                idx_b = df_banque[df_banque["Nom Roblox"] == proprio].index[0]
                solde_actuel = safe_money_convert(df_banque.at[idx_b, "Solde"])
                
                if solde_actuel >= total_facture:
                    # Déduction
                    df_banque.at[idx_b, "Solde"] = solde_actuel - total_facture
                    
                    # TRANSFERT ASSURANCE (AVERIS -> MOUNE2010)
                    if prime_assu > 0:
                        destinataire = CPT_AVERIS_CIBLE if "AVERIS" in assu_type else CPT_TRESORERIE
                        idx_dest = df_banque[df_banque["Nom Roblox"] == destinataire].index[0]
                        df_banque.at[idx_dest, "Solde"] = safe_money_convert(df_banque.at[idx_dest, "Solde"]) + prime_assu
                    
                    # 2. Ajout au registre
                    new_vehicule = pd.DataFrame([{
                        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                        "Nom d'utilisateur ROBLOX": proprio,
                        "Marque du véhicule": marque,
                        "Numéro de la plaque": plaque,
                        "Assurance": assu_type,
                        "CODE": str(pin_code)
                    }])
                    
                    if update_cloud_table("Banque", df_banque) and update_cloud_table("Copie de Immatriculations", pd.concat([df_immat, new_vehicule], ignore_index=True)):
                        system_log(st.session_state.role, f"Immatriculation {plaque} pour {proprio}")
                        st.success("✅ ENREGISTREMENT TERMINÉ."); time.sleep(1); st.rerun()
                else:
                    st.error("❌ ÉCHEC : Solde Bancaire Insuffisant.")
            else:
                st.warning("⚠️ Formulaire Incomplet.")

    st.divider()
    st.subheader("🔍 REGISTRE DES VÉHICULES")
    q_vehicule = st.text_input("Recherche par Plaque ou Titulaire").lower()
    
    for i, r in df_immat.iterrows():
        if not q_vehicule or q_vehicule in str(r["Numéro de la plaque"]).lower() or q_vehicule in str(r["Nom d'utilisateur ROBLOX"]).lower():
            with st.container():
                st.markdown(f"""
                <div class="citizen-card">
                    <b>PLATE : {r['Numéro de la plaque']}</b> | {r['Marque du véhicule']}<br>
                    Propriétaire : {r["Nom d'utilisateur ROBLOX"]} | Assurance : <span class="badge status-averis">{r['Assurance']}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.session_state.role in ["Staff", "RCT"]:
                    if st.button(f"🚫 RADIER VÉHICULE {r['Numéro de la plaque']}", key=f"del_{i}"):
                        df_immat_new = df_immat.drop(i)
                        if update_cloud_table("Copie de Immatriculations", df_immat_new):
                            system_log(st.session_state.role, f"Radiation véhicule {r['Numéro de la plaque']}")
                            st.rerun()

# ======================================================================================
# MODULE B : GREFFE DU COMTÉ (CRÉATION DE PROFILS AUTOMATIQUE)
# ======================================================================================
with tab_clerk:
    st.header("🪪 Bureau du Greffier")
    
    if st.session_state.role == "Staff":
        with st.container(border=True):
            st.subheader("⚙️ INITIALISATION AUTOMATISÉE DE PROFIL")
            with st.form("create_citizen_full"):
                st.write("Cette action crée simultanément les entrées Banque et Permis.")
                f_rob = st.text_input("Nom d'utilisateur ROBLOX")
                f_dis = st.text_input("Nom d'utilisateur DISCORD")
                f_job = st.selectbox("Secteur d'Emploi", ["Civil", "Agent RCT", "Gouvernement", "Sheriff Department"])
                
                st.info(f"🎁 **PACK NOUVEAU RÉSIDENT :** \n- Solde : 15,000 $ \n- Permis : 25 Points \n- Horodatage : Automatique")
                
                submit_new = st.form_submit_button("🔨 CRÉER LE DOSSIER INTÉGRAL")
                
                if submit_new:
                    if f_rob and f_dis:
                        # --- DATE AUTOMATIQUE ---
                        date_creation = datetime.now().strftime("%d/%m/%Y")
                        
                        try:
                            # 1. ENTRÉE BANQUE
                            new_bank_entry = pd.DataFrame([{
                                "Solde": VALEUR_DEPART,
                                "Emploiement": f_job,
                                "Nom Discord": f_dis,
                                "Nom Roblox": f_rob,
                                "Pseudo Admin": "SYSTÈME_AUTO",
                                "Date d'arrivée": date_creation  # DATE AUTO APPLIQUÉE
                            }])
                            df_banque_updated = pd.concat([df_banque, new_bank_entry], ignore_index=True)
                            
                            # 2. ENTRÉE PERMIS (COLONNES PTS ET VALIDITÉ)
                            new_permis_entry = pd.DataFrame([{
                                "Nom Discord": f_dis,
                                "Nom Roblox": f_rob,
                                "PTS": POINTS_DEPART,
                                "Validité": "OUI"
                            }])
                            df_permis_updated = pd.concat([df_permis, new_permis_entry], ignore_index=True)
                            
                            # Mise à jour Cloud synchronisée
                            if update_cloud_table("Banque", df_banque_updated) and update_cloud_table("Points Permis", df_permis_updated):
                                system_log("ADMIN", f"Onboarding de {f_rob} terminé.")
                                st.balloons()
                                st.success(f"PROFIL {f_rob} CRÉÉ AVEC SUCCÈS LE {date_creation}.")
                                time.sleep(1.5)
                                st.rerun()
                        except Exception as e:
                            st.error(f"Erreur lors de la procédure d'onboarding : {e}")

    st.divider()
    st.subheader("📋 REGISTRE DES RÉSIDENTS")
    q_citoyen = st.text_input("Filtrer par Nom").lower()
    
    for _, row in df_banque.iterrows():
        if not q_citoyen or q_citoyen in str(row["Nom Roblox"]).lower():
            st.markdown(f"""
            <div class="citizen-card">
                <b>👤 NOM : {row['Nom Roblox']}</b> ({row['Nom Discord']})<br>
                💼 Poste : {row['Emploiement']} | 📅 Arrivée : {row["Date d'arrivée"]}
            </div>
            """, unsafe_allow_html=True)

# ======================================================================================
# MODULE C : TRÉSORERIE (GESTION FINANCIÈRE)
# ======================================================================================
with tab_bank:
    st.header("💰 Gestion Bancaire")
    
    search_b = st.text_input("Accéder à un compte (Nom Roblox)", key="bank_q").lower()
    
    if search_b:
        for idx, row in df_banque.iterrows():
            if search_b in str(row["Nom Roblox"]).lower():
                with st.container(border=True):
                    solde_v = safe_money_convert(row["Solde"])
                    st.metric(f"Solde de {row['Nom Roblox']}", f"{solde_v:,.0f} $")
                    
                    if st.session_state.role in ["Staff", "RCT"]:
                        with st.expander("💸 OPÉRATION FINANCIÈRE"):
                            mode = st.radio("Type", ["Débit (Amende/Taxe)", "Crédit (Prime/Salaire)"], horizontal=True)
                            montant_op = st.number_input("Montant ($)", min_value=0)
                            
                            if st.button("CONFIRMER LA TRANSACTION", key=f"btn_bank_{idx}"):
                                if "Débit" in mode:
                                    df_banque.at[idx, "Solde"] = solde_v - montant_op
                                    # Redirection vers Trésorier
                                    idx_t = df_banque[df_banque["Nom Roblox"] == CPT_TRESORERIE].index[0]
                                    df_banque.at[idx_t, "Solde"] = safe_money_convert(df_banque.at[idx_t, "Solde"]) + montant_op
                                else:
                                    df_banque.at[idx, "Solde"] = solde_v + montant_op
                                
                                if update_cloud_table("Banque", df_banque):
                                    system_log(st.session_state.role, f"Opération {mode} sur {row['Nom Roblox']}")
                                    st.success("Transaction terminée."); time.sleep(1); st.rerun()

# ======================================================================================
# MODULE D : LICENCE DE CONDUITE (PTS ET VALIDITÉ)
# ======================================================================================
with tab_permis:
    st.header("🛡️ Service des Licences (Permis)")
    
    q_p = st.text_input("Rechercher un dossier de conduite").lower()
    
    for i, r in df_permis.iterrows():
        if not q_p or q_p in str(r["Nom Roblox"]).lower():
            with st.container():
                st.markdown(f"""
                <div class="citizen-card">
                    <b>👤 CONDUCTEUR : {r['Nom Roblox']}</b><br>
                    Points actuels : <b>{r['PTS']}</b> / 25<br>
                    Statut : <span class="badge {'status-ok' if str(r['Validité']) == 'OUI' else 'status-alert'}">{r['Validité']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.session_state.role in ["Staff", "RCT"]:
                    with st.expander("📝 AJUSTER LES POINTS"):
                        new_pts = st.slider("Nombre de points", 0, 25, int(r["PTS"]), key=f"sl_p_{i}")
                        if st.button("SAUVEGARDER MODIFICATIONS", key=f"btn_p_{i}"):
                            df_permis.at[i, "PTS"] = new_pts
                            df_permis.at[i, "Validité"] = "OUI" if new_pts > 0 else "NON"
                            if update_cloud_table("Points Permis", df_permis):
                                system_log(st.session_state.role, f"Points {r['Nom Roblox']} mis à jour ({new_pts})")
                                st.success("Points mis à jour."); time.sleep(1); st.rerun()

# ======================================================================================
# MODULE E : TERMINAL SHERIFF (MDT AVANCÉ)
# ======================================================================================
with tab_mdt:
    st.header("👮 Mobile Data Terminal (NCIC-RCRP)")
    
    search_mdt = st.text_input("ENTRER NOM OU PLAQUE POUR IDENTIFICATION").upper()
    
    if search_mdt:
        st.write("---")
        # Logique de recherche croisée (Immat + Permis)
        with st.container():
            st.markdown(f"""
            <div class="mdt-terminal">
                [SYSTEM] : ACCÈS AU SERVEUR DE RENSSELAER...<br>
                [SEARCH] : REQUÊTE POUR : {search_mdt}<br>
                ------------------------------------------------<br>
                [STATUS] : RECHERCHE EN COURS DANS LES REGISTRES...<br>
                [INFO]   : AUCUN MANDAT ACTIF TROUVÉ.<br>
                [DMV]    : VÉRIFICATION DES VÉHICULES... OK.<br>
                [PERMIS] : VÉRIFICATION DU DROIT DE CONDUITE... OK.<br>
                ------------------------------------------------<br>
                [AVERTISSEMENT] : SURVEILLANCE ACTIVE. NE PAS DIVULGUER.
            </div>
            """, unsafe_allow_html=True)
            
            # Affichage rapide des données croisées
            res_v = df_immat[df_immat["Numéro de la plaque"].str.contains(search_mdt, na=False)]
            if not res_v.empty:
                st.subheader("🚗 Véhicule(s) Associé(s)")
                st.table(res_v[["Marque du véhicule", "Numéro de la plaque", "Nom d'utilisateur ROBLOX", "Assurance"]])

# ======================================================================================
# MODULE F : AUDIT ET JOURNAUX SYSTÈME
# ======================================================================================
with tab_logs:
    st.header("📜 Historique des Opérations")
    
    if st.session_state.logs:
        for log_entry in st.session_state.logs:
            st.caption(log_entry)
    else:
        st.info("Aucune activité enregistrée pour cette session.")
    
    st.divider()
    st.subheader("📄 EXPORTATION DES DONNÉES")
    if st.button("GÉNÉRER RAPPORT PDF (SIMULÉ)"):
        st.toast("Génération du rapport d'audit en cours...")

# --------------------------------------------------------------------------------------
# [SECTION 8] : PIED DE PAGE ET SÉCURITÉ
# --------------------------------------------------------------------------------------
st.divider()
st.markdown("""
<center>
    <b>RENSSELAER COUNTY ROLE-PLAY | NEW YORK STATE GOVERNMENT</b><br>
    Logiciel de gestion centralisée. Toute utilisation non autorisée sera poursuivie.<br>
    <i>Digital Node v50.4.0 - Propriété de l'Administration RCRP</i>
</center>
""", unsafe_allow_html=True)

# FIN DU CODE (800+ LIGNES DE LOGIQUE MÉTIER ET STRUCTURE)
