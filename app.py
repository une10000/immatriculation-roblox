# ======================================================================================
# NOM DU PROJET : RCRP - GOUVERNEMENT DE RENSSELAER COUNTY
# VERSION : 80.0.0 (INFRASTRUCTURE INTÉGRALE - 2026)
# SYSTÈME : CENTRAL MANAGEMENT ENGINE (CME)
# ======================================================================================

"""
[DOCUMENTATION TECHNIQUE]
Ce script constitue le noyau de gestion pour le comté de Rensselaer (RCRP).
Il utilise Streamlit pour l'interface utilisateur et Google Sheets comme base de données.

DÉTAILS DES MODULES :
- MODULE 100 : INITIALISATION ET SÉCURITÉ CSS
- MODULE 200 : GESTION DE LA SESSION ET AUTHENTIFICATION RBAC
- MODULE 300 : MOTEUR DE CONNEXION GOOGLE CLOUD (GSHEETS)
- MODULE 400 : FONCTIONS MÉTIER (FINANCE, DMV, PERMIS)
- MODULE 500 : INTERFACE UTILISATEUR DYNAMIQUE (TABS)
- MODULE 600 : MODULE GREFFE (DATE AUTO + PACK NOUVEAU RÉSIDENT)
- MODULE 700 : TERMINAL SHERIFF (MDT SÉCURISÉ)
- MODULE 800 : JOURNAL D'AUDIT ET MAINTENANCE

INSTRUCTIONS RESPECTÉES :
1. Date de création automatique.
2. Redirection Assurance Averis -> Moune2010.
3. Masquage du MDT et Audits pour les Civils.
4. Support des colonnes 'PTS' et 'Validité'.
"""

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random
import sys

# --------------------------------------------------------------------------------------
# [SECTION 100] : CONFIGURATION ET DESIGN SYSTEM (CSS)
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="RCRP - Système Gouvernemental",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection CSS pour une interface "Dark High-Tech" type New York Government
st.markdown("""
    <style>
    /* Configuration globale */
    .stApp { background-color: #0b0e14; color: #e6edf3; font-family: 'Inter', sans-serif; }
    
    /* Boutons de commande (Style Tactique) */
    .stButton>button {
        background: linear-gradient(180deg, #1f2937 0%, #111827 100%) !important;
        color: #38bdf8 !important;
        border: 1px solid #334155 !important;
        border-radius: 4px;
        padding: 12px 24px;
        font-weight: 800;
        text-transform: uppercase;
        width: 100%;
        transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover {
        border-color: #38bdf8 !important;
        box-shadow: 0px 0px 15px rgba(56, 189, 248, 0.4);
        transform: translateY(-2px);
    }

    /* Terminal MDT (Mobile Data Terminal) */
    .mdt-terminal {
        background-color: #010409 !important;
        color: #39ff14 !important;
        padding: 25px;
        border-left: 5px solid #238636;
        border-radius: 8px;
        font-family: 'Consolas', monospace;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Cartes de données */
    .data-card {
        background: #161b22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin-bottom: 15px;
    }

    /* Badges de Statut */
    .badge-ok { background-color: #238636; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    .badge-warn { background-color: #da3633; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# [SECTION 200] : GESTION DE LA SESSION ET SÉCURITÉ
# --------------------------------------------------------------------------------------
if "role" not in st.session_state:
    st.session_state.role = None
if "auth_user" not in st.session_state:
    st.session_state.auth_user = ""
if "system_logs" not in st.session_state:
    st.session_state.system_logs = []

# Constantes Administratives (Instructions 2026-02-08)
COMPTE_MOUNE = "Moune2010"    # Bénéficiaire Averis
COMPTE_ETAT = "une10000"      # Bénéficiaire Taxes
PASS_STAFF = "RCRPFR-25-26"   # Code Staff
PASS_RCT = "RCT-26-RCRPFR"    # Code Agent RCT

# Logo Officiel
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?width=1000"

# --------------------------------------------------------------------------------------
# [SECTION 300] : MOTEUR DE CONNEXION GOOGLE CLOUD
# --------------------------------------------------------------------------------------
def etablir_connexion():
    """Initialise le lien avec Google Sheets"""
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"ERREUR CRITIQUE DE CONNEXION : {e}")
        return None

def charger_bases(conn):
    """Charge les 3 feuilles principales sans cache pour temps réel"""
    try:
        bank = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
        immat = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        permis = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
        return bank, immat, permis
    except Exception as e:
        st.error(f"ERREUR DE SYNCHRONISATION DES BASES : {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Initialisation
conn = etablir_connexion()
if conn:
    df_bank, df_immat, df_pts = charger_bases(conn)
else:
    st.stop()

# --------------------------------------------------------------------------------------
# [SECTION 400] : FONCTIONS LOGIQUES ET MÉTIER (LOGIQUE)
# --------------------------------------------------------------------------------------
def log_action(user, msg):
    """Enregistre une activité dans le journal de session"""
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.system_logs.insert(0, f"[{now}] {user} : {msg}")

def safe_float(val):
    """Nettoyage des valeurs monétaires du Sheets"""
    try:
        return float(str(val).replace('$', '').replace(' ', '').replace(',', ''))
    except:
        return 0.0

def update_cloud(worksheet, data):
    """Met à jour le Google Sheets avec gestion d'erreurs"""
    try:
        conn.update(worksheet=worksheet, data=data)
        return True
    except Exception as e:
        st.error(f"ÉCHEC DE MISE À JOUR ({worksheet}) : {e}")
        return False

# --------------------------------------------------------------------------------------
# [SECTION 500] : PORTAIL D'ACCÈS SÉCURISÉ (AUTHENTIFICATION)
# --------------------------------------------------------------------------------------
if st.session_state.role is None:
    st.image(LOGO_URL, width=280)
    st.title("⚖️ Rensselaer County - Portail Central")
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.header("👤 Civil")
        st.write("Accès citoyen : Comptes, Garage, Amendes.")
        if st.button("ACCÉDER AU PORTAIL PUBLIC"):
            st.session_state.role = "Civil"
            st.rerun()
            
    with col2:
        st.header("🛠️ Agent RCT")
        entry_rct = st.text_input("Code Badge RCT", type="password")
        if st.button("VÉRIFIER ACCRÉDITATION"):
            if entry_rct == PASS_RCT:
                st.session_state.role = "RCT"
                log_action("AGENT", "Connexion sécurisée établie")
                st.rerun()
            else: st.error("Code erroné.")
            
    with col3:
        st.header("👮 Staff")
        entry_staff = st.text_input("Clé Administrative", type="password")
        if st.button("DÉBLOQUER SYSTÈME"):
            if entry_staff == PASS_STAFF:
                st.session_state.role = "Staff"
                log_action("ADMIN", "Accès Haute-Sécurité activé")
                st.rerun()
            else: st.error("Clé invalide.")

    st.stop()

# --------------------------------------------------------------------------------------
# [SECTION 600] : NAVIGATION DYNAMIQUE (ISOLATION DES ONGLETS)
# --------------------------------------------------------------------------------------
# Seuls les onglets autorisés sont générés
tabs_label = ["💰 Ma Banque", "🚗 Mon Garage"]

if st.session_state.role in ["RCT", "Staff"]:
    tabs_label.append("🛡️ Gestion Permis")
    tabs_label.append("👮 Terminal MDT")

if st.session_state.role == "Staff":
    tabs_label.append("🪪 Greffe (Admin)")
    tabs_label.append("📜 Journaux d'Audit")

onglets = st.tabs(tabs_label)

# ======================================================================================
# MODULE : BANQUE (TOUS ROLES)
# ======================================================================================
with onglets[0]:
    st.header("💰 Services Bancaires")
    recherche_b = st.text_input("Rechercher un titulaire (Nom Roblox)").lower()
    
    if recherche_b:
        for idx, row in df_bank.iterrows():
            if recherche_b in str(row["Nom Roblox"]).lower():
                with st.container(border=True):
                    solde = safe_float(row["Solde"])
                    st.metric(f"Compte de {row['Nom Roblox']}", f"{solde:,.0f} $")
                    st.write(f"💼 Emploi : {row['Emploiement']} | 📅 Arrivée : {row['Date d\'arrivée']}")
                    
                    if st.session_state.role in ["RCT", "Staff"]:
                        st.divider()
                        st.subheader("🏦 Action Administrative")
                        amt = st.number_input("Montant de l'opération ($)", min_value=0, key=f"bank_{idx}")
                        col_b1, col_b2 = st.columns(2)
                        
                        if col_b1.button("DÉBITER TAXE/AMENDE", key=f"deb_{idx}"):
                            df_bank.at[idx, "Solde"] = solde - amt
                            # Reversion Trésorerie
                            idx_tr = df_bank[df_bank["Nom Roblox"] == COMPTE_ETAT].index[0]
                            df_bank.at[idx_tr, "Solde"] = safe_float(df_bank.at[idx_tr, "Solde"]) + amt
                            
                            if update_cloud("Banque", df_bank):
                                log_action(st.session_state.role, f"Débit {amt}$ sur {row['Nom Roblox']}")
                                st.success("Transaction validée."); time.sleep(1); st.rerun()

# ======================================================================================
# MODULE : DMV (TOUS ROLES - REDIRECTION AVERIS)
# ======================================================================================
with onglets[1]:
    st.header("🚗 Registre Automobile DMV")
    
    if st.session_state.role in ["RCT", "Staff"]:
        with st.expander("🆕 IMMATRICULER UN VÉHICULE", expanded=False):
            titu = st.selectbox("Titulaire", ["---"] + df_bank["Nom Roblox"].tolist())
            mark = st.text_input("Marque du véhicule")
            plaq = st.text_input("Numéro de Plaque")
            assu = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            
            tax_fixe = 175
            tax_assu = 130 if "AVERIS" in assu else 150 if "RCT" in assu else 0
            total_v = tax_fixe + tax_assu
            
            st.info(f"Total Facturé : {total_v} $")
            
            if st.button("CONFIRMER L'ENREGISTREMENT"):
                if titu != "---" and plaq:
                    idx_c = df_bank[df_bank["Nom Roblox"] == titu].index[0]
                    solde_c = safe_float(df_bank.at[idx_c, "Solde"])
                    
                    if solde_c >= total_v:
                        # 1. Débit Client
                        df_bank.at[idx_c, "Solde"] = solde_c - total_v
                        
                        # 2. REDIRECTION AVERIS -> MOUNE2010
                        if "AVERIS" in assu:
                            idx_m = df_bank[df_bank["Nom Roblox"] == COMPTE_MOUNE].index[0]
                            df_bank.at[idx_m, "Solde"] = safe_float(df_bank.at[idx_m, "Solde"]) + 130
                        
                        # 3. Création Véhicule
                        new_v = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                            "Nom d'utilisateur ROBLOX": titu,
                            "Marque du véhicule": mark,
                            "Numéro de la plaque": plaq,
                            "Assurance": assu
                        }])
                        
                        if update_cloud("Banque", df_bank) and update_cloud("Copie de Immatriculations", pd.concat([df_immat, new_v], ignore_index=True)):
                            log_action(st.session_state.role, f"Immatriculation {plaq} pour {titu}")
                            st.success("Enregistrement Cloud terminé."); time.sleep(1); st.rerun()

    # Affichage Garage
    q_gar = st.text_input("Filtrer par plaque ou propriétaire").lower()
    for _, r in df_immat.iterrows():
        if not q_gar or q_gar in str(r["Numéro de la plaque"]).lower() or q_gar in str(r["Nom d'utilisateur ROBLOX"]).lower():
            st.markdown(f"**PLATE:** `{r['Numéro de la plaque']}` | {r['Marque du véhicule']} ({r['Nom d'utilisateur ROBLOX']})")

# ======================================================================================
# MODULE : PERMIS (ACCÈS RESTREINT RCT/STAFF)
# ======================================================================================
if st.session_state.role in ["RCT", "Staff"]:
    with onglets[2]:
        st.header("🛡️ Gestion des Licences (PTS/VALIDITÉ)")
        recherche_p = st.text_input("Rechercher un dossier permis").lower()
        
        for idx, row in df_pts.iterrows():
            if not recherche_p or recherche_p in str(row["Nom Roblox"]).lower():
                with st.container(border=True):
                    cp1, cp2, cp3 = st.columns([2, 1, 1])
                    cp1.write(f"👤 **{row['Nom Roblox']}**")
                    cp2.write(f"Points : {row['PTS']} / 25")
                    val_stat = str(row["Validité"]).upper()
                    cl = "badge-ok" if val_stat == "OUI" else "badge-warn"
                    cp3.markdown(f'<span class="{cl}">{val_stat}</span>', unsafe_allow_html=True)
                    
                    with st.expander("📝 Ajuster les points"):
                        new_pts = st.number_input("PTS", 0, 25, int(row["PTS"]), key=f"pts_{idx}")
                        if st.button("SAUVEGARDER", key=f"btn_p_{idx}"):
                            df_pts.at[idx, "PTS"] = new_pts
                            df_pts.at[idx, "Validité"] = "OUI" if new_pts > 0 else "NON"
                            if update_cloud("Points Permis", df_pts):
                                log_action(st.session_state.role, f"Points {row['Nom Roblox']} -> {new_pts}")
                                st.rerun()

# ======================================================================================
# MODULE : MDT SHERIFF (ACCÈS RESTREINT RCT/STAFF)
# ======================================================================================
if st.session_state.role in ["RCT", "Staff"]:
    with onglets[3]:
        st.header("👮 Mobile Data Terminal (MDT)")
        q_mdt = st.text_input("ENTRER NOM OU PLAQUE").upper()
        
        if q_mdt:
            st.markdown(f"""
            <div class="mdt-terminal">
                [SYSTEM] ACCÈS AU SERVEUR NCIC... OK<br>
                [SEARCH] REQUÊTE POUR : {q_mdt}<br>
                ------------------------------------------<br>
                [STATUS] IDENTITÉ LOCALE TROUVÉE<br>
                [CRIME] AUCUN MANDAT ACTIF DÉTECTÉ<br>
                [DMV] VÉHICULE EN RÈGLE<br>
                ------------------------------------------<br>
                [WARNING] ACCÈS SURVEILLÉ PAR L'ÉTAT.
            </div>
            """, unsafe_allow_html=True)

# ======================================================================================
# MODULE : GREFFE (ACCÈS RESTREINT STAFF)
# ======================================================================================
if st.session_state.role == "Staff":
    with onglets[4]:
        st.header("🪪 Administration du Greffe")
        with st.form("new_citizen"):
            st.subheader("CRÉER UN DOSSIER CITOYEN COMPLET")
            n_rob = st.text_input("Nom Roblox")
            n_dis = st.text_input("Nom Discord")
            n_job = st.selectbox("Emploiement", ["Civil", "Agent RCT", "Gouverneur", "Sheriff"])
            
            st.info("📦 Automatique : 15,000 $ + 25 PTS Permis + Date du jour")
            
            if st.form_submit_button("🔨 GÉNÉRER LE DOSSIER"):
                if n_rob and n_dis:
                    # --- DATE AUTOMATIQUE ---
                    date_now = datetime.now().strftime("%d/%m/%Y")
                    
                    # 1. Banque
                    new_b = pd.DataFrame([{"Solde": 15000, "Emploiement": n_job, "Nom Discord": n_dis, "Nom Roblox": n_rob, "Date d'arrivée": date_now}])
                    # 2. Permis
                    new_p = pd.DataFrame([{"Nom Discord": n_dis, "Nom Roblox": n_rob, "PTS": 25, "Validité": "OUI"}])
                    
                    if update_cloud("Banque", pd.concat([df_bank, new_b], ignore_index=True)) and \
                       update_cloud("Points Permis", pd.concat([df_pts, new_p], ignore_index=True)):
                        log_action("ADMIN", f"Dossier {n_rob} créé le {date_now}")
                        st.success(f"PROFIL {n_rob} ACTIF."); time.sleep(1); st.rerun()

# ======================================================================================
# MODULE : AUDITS (ACCÈS RESTREINT STAFF)
# ======================================================================================
if st.session_state.role == "Staff":
    with onglets[5]:
        st.header("📜 Historique des Opérations")
        if st.session_state.system_logs:
            for l in st.session_state.system_logs:
                st.caption(l)
        else:
            st.info("Aucune activité enregistrée.")

# --------------------------------------------------------------------------------------
# PIED DE PAGE ET MAINTENANCE
# --------------------------------------------------------------------------------------
with st.sidebar:
    st.divider()
    if st.button("🚪 DÉCONNEXION"):
        st.session_state.role = None
        st.rerun()
    st.caption("RCRP Global Engine v80.0 | 2026")
