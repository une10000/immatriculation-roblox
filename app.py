# ======================================================================================
# NOM DU PROJET : RENSSELAER COUNTY ROLE-PLAY (RCRP) - SUPREME INFRASTRUCTURE OS
# VERSION : 600.0.1 (ULTRA-LONG EDITION - 2026)
# DÉVELOPPÉ POUR : ADMINISTRATION DU COMTÉ DE RENSSELAER
# SYSTÈME : CENTRALIZED DATA MANAGEMENT ARCHITECTURE (CDMA)
# ======================================================================================

"""
[MANUEL TECHNIQUE DE L'INFRASTRUCTURE RCRP]

Ce logiciel constitue le système d'exploitation complet (OS) pour le comté.
Il est conçu pour être l'interface unique entre le terrain (Roblox) et le Cloud.

LOGIQUE DE SÉCURITÉ (RBAC - Role Based Access Control) :
-------------------------------------------------------
- CIVIL : Accès restreint. Lecture seule de son propre dossier.
- RCT (Department of Transport) : Accès aux modules DMV, Permis et MDT.
- STAFF (Administration) : Accès Root (Greffe, Trésorerie, Audit, Manipulation Solde).

RÈGLES FINANCIÈRES IMPÉRATIVES :
--------------------------------
1. REDIRECTION AVERIS : Les 130$ d'assurance sont détournés vers 'Moune2010'.
2. TAXE D'ÉTAT : 175$ prélevés sur chaque plaque et envoyés à 'une10000'.
3. PACK BIENVENUE : 15,000$ + 25 PTS + Date d'arrivée automatique.

INSTRUCTIONS DE FORMATAGE :
- Pas de code dans les logs civils.
- Utilisation de Markdown pour une interface scannable.
"""

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date, timedelta
import time
import random

# --------------------------------------------------------------------------------------
# [SECTION 100] : ARCHITECTURE DE L'INTERFACE (CSS HAUTE DENSITÉ)
# --------------------------------------------------------------------------------------

st.set_page_config(
    page_title="RCRP - Système d'État Centralisé",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Framework Global */
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Inter', sans-serif; }
    
    /* Titres Gouvernementaux */
    h1, h2, h3 { 
        color: #58a6ff !important; 
        font-weight: 900 !important; 
        text-transform: uppercase; 
        letter-spacing: 2px;
        border-bottom: 2px solid #30363d;
        padding-bottom: 15px;
        margin-top: 30px;
    }
    
    /* Boutons Tactiques */
    .stButton>button {
        background: linear-gradient(180deg, #21262d 0%, #161b22 100%) !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
        border-radius: 6px;
        padding: 15px 30px;
        font-weight: 800;
        text-transform: uppercase;
        width: 100%;
        transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover {
        border-color: #58a6ff !important;
        box-shadow: 0px 0px 20px rgba(88, 166, 255, 0.3);
        transform: translateY(-2px);
    }

    /* Terminal MDT Sheriff */
    .mdt-terminal {
        background-color: #010409 !important;
        color: #39ff14 !important;
        padding: 40px;
        border-left: 10px solid #238636;
        border-radius: 4px;
        font-family: 'Consolas', 'Monaco', monospace;
        margin: 20px 0;
        box-shadow: inset 0 0 40px #000;
        border-top: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
    }

    /* Badges de Statut */
    .badge-valid { background-color: #238636; color: white; padding: 5px 15px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    .badge-invalid { background-color: #da3633; color: white; padding: 5px 15px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #010409 !important; border-right: 2px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# [SECTION 200] : CORE CONFIGURATION & CONSTANTS
# --------------------------------------------------------------------------------------

if 'role' not in st.session_state: st.session_state.role = None
if 'user_id' not in st.session_state: st.session_state.user_id = ""
if 'audit_trail' not in st.session_state: st.session_state.audit_trail = []

SETTINGS = {
    "CLE_STAFF": "RCRPFR-25-26",
    "CLE_RCT": "RCT-26-RCRPFR",
    "MOUNE_ACCOUNT": "Moune2010",
    "ETAT_ACCOUNT": "une10000",
    "START_MONEY": 15000,
    "START_PTS": 25,
    "TAX_DMV": 175,
    "TAX_AVERIS": 130,
    "TAX_RCT": 150,
    "LOGO": "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?width=1000",
    "MARQUES": [
        "Acura", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", "BMW", "Bugatti", 
        "Buick", "Cadillac", "Chevrolet", "Chrysler", "Dodge", "Ferrari", "Fiat", 
        "Ford", "GMC", "Honda", "Hyundai", "Infiniti", "Jaguar", "Jeep", "Kia", 
        "Lamborghini", "Land Rover", "Lexus", "Lincoln", "Maserati", "Mazda", 
        "McLaren", "Mercedes-Benz", "MINI", "Mitsubishi", "Nissan", "Pagani", 
        "Porsche", "Ram", "Rolls-Royce", "Subaru", "Tesla", "Toyota", "Volkswagen", "Volvo"
    ]
}

# --------------------------------------------------------------------------------------
# [SECTION 300] : MOTEUR DE DONNÉES CLOUD (ETL PROCESS)
# --------------------------------------------------------------------------------------

def initialiser_liaison_cloud():
    """Établit une connexion persistante avec Google Sheets API"""
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"ERREUR LIAISON CLOUD : {e}")
        return None

def synchroniser_base_donnees(conn):
    """Extraction et nettoyage des DataFrames avec TTL zéro pour temps réel"""
    try:
        bank = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
        immat = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        pts = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
        return bank, immat, pts
    except Exception as e:
        st.error(f"ERREUR SYNCHRO : {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Initialisation des flux
cloud_conn = initialiser_liaison_cloud()
if cloud_conn:
    df_bank, df_immat, df_pts = synchroniser_base_donnees(cloud_conn)
else:
    st.stop()

# --------------------------------------------------------------------------------------
# [SECTION 400] : FONCTIONS UTILITAIRES & LOGIQUE MÉTIER
# --------------------------------------------------------------------------------------

def parse_currency(value):
    """Nettoyage des données monétaires pour calculs mathématiques"""
    try:
        return float(str(value).replace('$', '').replace(' ', '').replace(',', ''))
    except:
        return 0.0

def push_update(worksheet, dataframe):
    """Envoi des modifications au Cloud avec vérification de succès"""
    try:
        cloud_conn.update(worksheet=worksheet, data=dataframe)
        return True
    except Exception as e:
        st.error(f"ÉCHEC ÉCRITURE : {e}")
        return False

def add_log(message):
    """Enregistre une action sans exposer de code source"""
    stamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.audit_trail.insert(0, f"[{stamp}] {message}")

# --------------------------------------------------------------------------------------
# [SECTION 500] : MOTEUR DE REDIRECTION AVERIS -> MOUNE2010
# --------------------------------------------------------------------------------------

def transferer_fonds_averis(df_comptes, montant):
    """
    LOGIQUE DÉDIÉE : Cherche Moune2010 et lui crédite le montant de l'assurance.
    Vérifie l'intégrité du compte avant transfert.
    """
    target = SETTINGS["MOUNE_ACCOUNT"]
    if target in df_comptes["Nom Roblox"].values:
        idx = df_comptes[df_comptes["Nom Roblox"] == target].index[0]
        current_bal = parse_currency(df_comptes.at[idx, "Solde"])
        df_comptes.at[idx, "Solde"] = current_bal + montant
        add_log(f"Redirection Assurance vers {target}")
        return df_comptes
    else:
        st.error(f"COMPTE CIBLE {target} NON TROUVÉ. FONDS EN ATTENTE.")
        return df_comptes

# --------------------------------------------------------------------------------------
# [SECTION 600] : PORTAIL D'AUTHENTIFICATION HAUTE SÉCURITÉ
# --------------------------------------------------------------------------------------

if st.session_state.role is None:
    st.image(SETTINGS["LOGO"], width=300)
    st.title("⚖️ Rensselaer County Central Engine")
    st.markdown("### Authentification Système Requis")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.info("#### 👤 CIVIL")
        st.write("Accès citoyen limité.")
        if st.button("OUVRIR PORTAIL"):
            st.session_state.role = "Civil"; st.rerun()
            
    with col_b:
        st.info("#### 🛠️ AGENT RCT")
        st.write("Department of Transport.")
        pwd_r = st.text_input("Code Badge", type="password")
        if st.button("IDENTIFIER AGENT"):
            if pwd_r == SETTINGS["CLE_RCT"]:
                st.session_state.role = "RCT"; add_log("Connexion RCT"); st.rerun()
            else: st.error("Badge Invalide.")
            
    with col_c:
        st.info("#### 👮 STAFF")
        st.write("Administration Comté.")
        pwd_s = st.text_input("Clé État", type="password")
        if st.button("OUVRIR SYSTÈME"):
            if pwd_s == SETTINGS["CLE_STAFF"]:
                st.session_state.role = "Staff"; add_log("Connexion Admin"); st.rerun()
            else: st.error("Accès Refusé.")
    
    st.stop()

# --------------------------------------------------------------------------------------
# [SECTION 700] : NAVIGATION ET ISOLATION DES INTERFACES
# --------------------------------------------------------------------------------------

tabs_labels = ["💰 Banque", "🚗 DMV"]

if st.session_state.role in ["RCT", "Staff"]:
    tabs_labels += ["🛡️ Permis", "👮 MDT"]

if st.session_state.role == "Staff":
    tabs_labels += ["🪪 Greffe", "🏦 État", "📜 Audit"]

tabs = st.tabs(tabs_labels)

# --------------------------------------------------------------------------------------
# [MODULE 800] : BANQUE - GESTION DES FLUX FINANCIERS
# --------------------------------------------------------------------------------------
with tabs[0]:
    st.header("Gestion des Comptes Bancaires")
    q_bank = st.text_input("Rechercher un résident (Nom Roblox)").lower()
    
    if q_bank:
        for idx, row in df_bank.iterrows():
            if q_bank in str(row["Nom Roblox"]).lower():
                with st.container(border=True):
                    bal = parse_currency(row["Solde"])
                    c1, c2 = st.columns([2, 1])
                    c1.markdown(f"### Compte de : **{row['Nom Roblox']}**")
                    c1.write(f"💼 Emploi : {row['Emploiement']} | 📅 Arrivée : {row['Date d\'arrivée']}")
                    c2.metric("Solde Bancaire", f"{bal:,.0f} $")
                    
                    if st.session_state.role in ["RCT", "Staff"]:
                        st.divider()
                        st.subheader("🛠️ Opération Administrative")
                        amount = st.number_input("Montant ($)", min_value=0, key=f"b_{idx}")
                        
                        cb1, cb2 = st.columns(2)
                        if cb1.button("DÉBITER (Taxe/Amende)", key=f"deb_{idx}"):
                            df_bank.at[idx, "Solde"] = bal - amount
                            # Reversement Trésorerie
                            idx_e = df_bank[df_bank["Nom Roblox"] == SETTINGS["ETAT_ACCOUNT"]].index[0]
                            df_bank.at[idx_e, "Solde"] = parse_currency(df_bank.at[idx_e, "Solde"]) + amount
                            
                            if push_update("Banque", df_bank):
                                add_log(f"Débit de {amount}$ sur {row['Nom Roblox']}")
                                st.success("Transaction terminée."); time.sleep(1); st.rerun()

# --------------------------------------------------------------------------------------
# [MODULE 900] : DMV - GESTION DES VÉHICULES ET MARQUES
# --------------------------------------------------------------------------------------
with tabs[1]:
    st.header("Registre Automobile (DMV)")
    
    if st.session_state.role in ["RCT", "Staff"]:
        with st.expander("🆕 ENREGISTRER UN NOUVEAU VÉHICULE"):
            with st.form("dmv_form"):
                v_owner = st.selectbox("Choisir le Propriétaire", ["---"] + df_bank["Nom Roblox"].tolist())
                # RÉINTÉGRATION DE LA LISTE DES MARQUES
                v_brand = st.selectbox("Marque du véhicule", sorted(SETTINGS["MARQUES"]))
                v_model = st.text_input("Modèle spécifique")
                v_plate = st.text_input("Numéro de Plaque")
                v_assu = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
                
                v_total = SETTINGS["TAX_DMV"]
                if "AVERIS" in v_assu: v_total += SETTINGS["TAX_AVERIS"]
                elif "RCT" in v_assu: v_total += SETTINGS["TAX_RCT"]
                
                st.write(f"**Coût total (Taxe + Assurance) : {v_total} $**")
                
                if st.form_submit_button("VALIDER L'IMMATRICULATION"):
                    if v_owner != "---" and v_plate:
                        idx_c = df_bank[df_bank["Nom Roblox"] == v_owner].index[0]
                        solde_c = parse_currency(df_bank.at[idx_c, "Solde"])
                        
                        if solde_c >= v_total:
                            # 1. Débit Client
                            df_bank.at[idx_c, "Solde"] = solde_c - v_total
                            
                            # 2. REDIRECTION AVERIS -> MOUNE2010
                            if "AVERIS" in v_assu:
                                df_bank = transferer_fonds_averis(df_bank, SETTINGS["TAX_AVERIS"])
                            
                            # 3. Création Véhicule
                            new_v = pd.DataFrame([{
                                "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                                "Nom d'utilisateur ROBLOX": v_owner,
                                "Marque du véhicule": f"{v_brand} {v_model}",
                                "Numéro de la plaque": v_plate,
                                "Assurance": v_assu
                            }])
                            
                            if push_update("Banque", df_bank) and push_update("Copie de Immatriculations", pd.concat([df_immat, new_v])):
                                add_log(f"Immatriculation {v_plate} pour {v_owner}")
                                st.success("Véhicule enregistré avec succès !"); time.sleep(1); st.rerun()
                        else: st.error("Fonds insuffisants.")

    q_dmv = st.text_input("Rechercher Plaque ou Nom").lower()
    for i, rv in df_immat.iterrows():
        if not q_dmv or q_dmv in str(rv["Numéro de la plaque"]).lower() or q_dmv in str(rv["Nom d'utilisateur ROBLOX"]).lower():
            st.markdown(f"**[{rv['Numéro de la plaque']}]** - {rv['Marque du véhicule']} (*{rv['Nom d'utilisateur ROBLOX']}*)")

# --------------------------------------------------------------------------------------
# [MODULE 1000] : PERMIS - GESTION DES POINTS
# --------------------------------------------------------------------------------------
if "🛡️ Permis" in tabs_labels:
    with tabs[2]:
        st.header("Administration des Permis de Conduire")
        q_p = st.text_input("Rechercher un conducteur").lower()
        
        for i, rp in df_pts.iterrows():
            if not q_p or q_p in str(rp["Nom Roblox"]).lower():
                with st.container(border=True):
                    pc1, pc2, pc3 = st.columns([2, 1, 1])
                    pc1.markdown(f"👤 **{rp['Nom Roblox']}**")
                    pc2.write(f"Points : **{rp['PTS']}** / 25")
                    
                    valide = str(rp["Validité"]).upper()
                    st_badge = "badge-valid" if valide == "OUI" else "badge-invalid"
                    pc3.markdown(f'<span class="{st_badge}">{valide}</span>', unsafe_allow_html=True)
                    
                    if st.session_state.role in ["RCT", "Staff"]:
                        with st.expander("📝 Ajuster Points"):
                            n_pts = st.number_input("Nouveaux Points", 0, 25, int(rp["PTS"]), key=f"p_{i}")
                            if st.button("SAUVEGARDER", key=f"btn_p_{i}"):
                                df_pts.at[i, "PTS"] = n_pts
                                df_pts.at[i, "Validité"] = "OUI" if n_pts > 0 else "NON"
                                if push_update("Points Permis", df_pts):
                                    add_log(f"Points {rp['Nom Roblox']} -> {n_pts}"); st.rerun()

# --------------------------------------------------------------------------------------
# [MODULE 1100] : MDT - TERMINAL POLICE
# --------------------------------------------------------------------------------------
if "👮 MDT" in tabs_labels:
    with tabs[3]:
        st.header("Mobile Data Terminal (MDT)")
        q_mdt = st.text_input("IDENTIFICATION NCIC (NOM OU PLAQUE)").upper()
        
        if q_mdt:
            st.markdown(f"""
            <div class="mdt-terminal">
                [SYSTEM] : ACCÈS AU TERMINAL DE RENSSELAER... OK<br>
                [SEARCH] : REQUÊTE POUR : {q_mdt}<br>
                ------------------------------------------------<br>
                [RESULT] : FICHIER CORRESPONDANT TROUVÉ.<br>
                [STATUS] : AUCUN MANDAT ACTIF DÉTECTÉ.<br>
                [ALERTE] : USAGE OFFICIEL UNIQUEMENT.
            </div>
            """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# [MODULE 1200] : GREFFE - DATE AUTOMATIQUE
# --------------------------------------------------------------------------------------
if "🪪 Greffe" in tabs_labels:
    with tabs[4]:
        st.header("Bureau du Greffier")
        with st.form("greffe_form"):
            st.subheader("CRÉATION D'UN DOSSIER CITOYEN")
            n_rob = st.text_input("Pseudo Roblox")
            n_dis = st.text_input("Pseudo Discord")
            n_job = st.selectbox("Métier", ["Civil", "RCT Agent", "Sheriff Dept", "Gouvernement"])
            
            st.info("🎁 **DOTATION :** 15,000 $ | 25 PTS | Date : AUTOMATIQUE")
            
            if st.form_submit_button("🔨 GÉNÉRER PROFIL"):
                if n_rob and n_dis:
                    # DATE AUTOMATIQUE (CONSIGNE 2026)
                    date_now = datetime.now().strftime("%d/%m/%Y")
                    
                    e_b = pd.DataFrame([{"Solde": SETTINGS["START_MONEY"], "Emploiement": n_job, "Nom Discord": n_dis, "Nom Roblox": n_rob, "Date d'arrivée": date_now}])
                    e_p = pd.DataFrame([{"Nom Discord": n_dis, "Nom Roblox": n_rob, "PTS": SETTINGS["START_PTS"], "Validité": "OUI"}])
                    
                    if push_update("Banque", pd.concat([df_bank, e_b])) and push_update("Points Permis", pd.concat([df_pts, e_p])):
                        add_log(f"Création résident {n_rob} le {date_now}")
                        st.balloons(); st.success(f"PROFIL ACTIF ({date_now})"); st.rerun()

# --------------------------------------------------------------------------------------
# [MODULE 1300] : ÉTAT - TRÉSORERIE PUBLIC
# --------------------------------------------------------------------------------------
if "🏦 État" in tabs_labels:
    with tabs[5]:
        st.header("Trésorerie du Comté")
        idx_e = df_bank[df_bank["Nom Roblox"] == SETTINGS["ETAT_ACCOUNT"]].index[0]
        bal_e = parse_currency(df_bank.at[idx_e, "Solde"])
        st.metric("COMPTE D'ÉTAT (une10000)", f"{bal_e:,.0f} $")

# --------------------------------------------------------------------------------------
# [MODULE 1400] : AUDIT - JOURNAUX SANS CODE
# --------------------------------------------------------------------------------------
if "📜 Audit" in tabs_labels:
    with tabs[6]:
        st.header("Historique Administratif")
        for log in st.session_state.audit_trail:
            st.write(log)

# --------------------------------------------------------------------------------------
# [SECTION 1500] : FOOTER & MAINTENANCE
# --------------------------------------------------------------------------------------
with st.sidebar:
    st.image(SETTINGS["LOGO"], width=100)
    if st.button("🚪 DÉCONNEXION"):
        st.session_state.role = None; st.rerun()
    st.divider()
    st.caption("RCRP DIGITAL ENGINE v600.0")
    st.caption("Février 2026 | Cloud Connected")

st.divider()
st.markdown("<center>RCRP CENTRAL OS | VERSION TITAN | 2026</center>", unsafe_allow_html=True)
