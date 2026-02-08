# ======================================================================================
# NOM DU PROJET : RCRP - GOUVERNEMENT DE RENSSELAER COUNTY
# VERSION : 75.0.0 (ÉDITION DE SÉCURITÉ MAXIMALE - 2026)
# SYSTÈME : CENTRAL MANAGEMENT INFRASTRUCTURE
# ======================================================================================

"""
[INFOS SYSTÈME]
Ce script est conçu pour gérer l'intégralité des services du Comté de Rensselaer.
Il intègre une protection par rôle (RBAC) empêchant les civils de voir les outils police.

FONCTIONNALITÉS INCLUSES :
1. MODULE CIVIL : Consultation solde et immatriculations personnelles.
2. MODULE RCT : Gestion des permis, amendes et immatriculations (Averis -> Moune2010).
3. MODULE STAFF : Création de profils (Date Auto), gestion des comptes et Audits.
4. SÉCURITÉ : Isolation stricte des onglets MDT et Journaux.
"""

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time
import random

# --------------------------------------------------------------------------------------
# [SECTION 1] : CONFIGURATION VISUELLE ET COMPORTEMENTALE (CSS)
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="RCRP - Système de Gestion du Comté",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Design spécifique pour différencier les accès
st.markdown("""
    <style>
    /* Global Dark Theme */
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; }
    
    /* Onglets de Navigation */
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        color: #8b949e;
        padding: 0 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f2937 !important;
        border-bottom: 3px solid #38bdf8 !important;
        color: #38bdf8 !important;
    }

    /* Boutons de commande */
    .stButton>button {
        background: linear-gradient(180deg, #1f2937 0%, #111827 100%) !important;
        color: #38bdf8 !important;
        border: 1px solid #334155 !important;
        border-radius: 4px;
        padding: 10px 20px;
        font-weight: bold;
        text-transform: uppercase;
        width: 100%;
        transition: 0.2s;
    }
    .stButton>button:hover {
        border-color: #38bdf8 !important;
        box-shadow: 0px 0px 10px rgba(56, 189, 248, 0.3);
    }

    /* Terminal Sheriff */
    .mdt-container {
        background-color: #010409 !important;
        color: #39ff14 !important;
        padding: 30px;
        border: 1px solid #238636;
        border-radius: 8px;
        font-family: 'Consolas', monospace;
        margin-top: 20px;
    }

    /* Alertes et Badges */
    .badge-valid { background-color: #238636; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    .badge-invalid { background-color: #da3633; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# [SECTION 2] : VARIABLES DE SESSION ET PARAMÈTRES (2026-02-09)
# --------------------------------------------------------------------------------------
if "role" not in st.session_state:
    st.session_state.role = None
if "logs" not in st.session_state:
    st.session_state.logs = []

# Paramètres de redirection bancaire
COMPTE_MOUNE = "Moune2010"    # Destinataire Averis
COMPTE_ETAT = "une10000"      # Destinataire Taxes
PASS_STAFF = "RCRPFR-25-26"
PASS_RCT = "RCT-26-RCRPFR"

# URL de l'identité visuelle
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?width=1000"

# --------------------------------------------------------------------------------------
# [SECTION 3] : MOTEUR DE CONNEXION GOOGLE SHEETS
# --------------------------------------------------------------------------------------
def initialiser_liaison():
    """Établit la connexion avec le fichier Profile RCRP"""
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"ERREUR CLOUD : {e}")
        return None

def synchroniser_donnees(conn):
    """Charge les données en respectant les noms de feuilles"""
    try:
        # On force le rafraîchissement (ttl=0)
        b = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
        i = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        p = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
        return b, i, p
    except Exception as e:
        st.error(f"ÉCHEC SYNCHRO : {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Connexion initiale
db_conn = initialiser_liaison()
if db_conn:
    df_bank, df_immat, df_pts = synchroniser_donnees(db_conn)
else:
    st.stop()

# --------------------------------------------------------------------------------------
# [SECTION 4] : FONCTIONS DE SÉCURITÉ ET LOGS
# --------------------------------------------------------------------------------------
def enregistrer_log(utilisateur, action):
    horaire = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.insert(0, f"[{horaire}] {utilisateur} : {action}")

def formater_monnaie(valeur):
    try:
        f_val = float(str(valeur).replace('$', '').replace(' ', ''))
        return f"{f_val:,.0f} $"
    except:
        return "0 $"

# --------------------------------------------------------------------------------------
# [SECTION 5] : PORTAIL D'AUTHENTIFICATION (PASSERELLE)
# --------------------------------------------------------------------------------------
if st.session_state.role is None:
    st.image(LOGO_URL, width=280)
    st.title("⚖️ Terminal Central du Comté de Rensselaer")
    st.write("Veuillez sélectionner votre portail d'accès.")
    
    auth_col1, auth_col2, auth_col3 = st.columns(3)
    
    with auth_col1:
        st.markdown("### 👤 Civil")
        if st.button("ACCÈS PUBLIC"):
            st.session_state.role = "Civil"; st.rerun()
            
    with auth_col2:
        st.markdown("### 🛠️ Agent RCT")
        code_rct = st.text_input("Code Badge RCT", type="password")
        if st.button("VÉRIFIER BADGE"):
            if code_rct == PASS_RCT:
                st.session_state.role = "RCT"; st.rerun()
            else: st.error("Code erroné.")
            
    with auth_col3:
        st.markdown("### 👮 Staff")
        code_stf = st.text_input("Clé Admin", type="password")
        if st.button("DÉBLOQUER SYSTÈME"):
            if code_stf == PASS_STAFF:
                st.session_state.role = "Staff"; st.rerun()
            else: st.error("Clé invalide.")

    st.divider()
    st.caption("Système RCRP v75.0 | Usage Officiel Uniquement")
    st.stop()

# --------------------------------------------------------------------------------------
# [SECTION 6] : NAVIGATION DYNAMIQUE (ISOLATION DES ONGLETS)
# --------------------------------------------------------------------------------------
# On définit ici quels onglets sont générés selon le rôle
liste_onglets = ["💰 Ma Banque", "🚗 Mon Garage"]

# Seuls les Agents et le Staff voient le permis et le MDT
if st.session_state.role in ["RCT", "Staff"]:
    liste_onglets.append("🛡️ Gestion Permis")
    liste_onglets.append("👮 MDT Sheriff")

# Seul le Staff voit la création de profil et les audits
if st.session_state.role == "Staff":
    liste_onglets.append("🪪 Greffe (Admin)")
    liste_onglets.append("📜 Journaux d'Audit")

onglets = st.tabs(liste_onglets)

# --------------------------------------------------------------------------------------
# MODULE : BANQUE (TOUS ROLES)
# --------------------------------------------------------------------------------------
with onglets[0]:
    st.header("💰 Services Bancaires")
    search_bank = st.text_input("Rechercher votre compte (Nom Roblox)").lower()
    
    if search_bank:
        for idx, row in df_bank.iterrows():
            if search_bank in str(row["Nom Roblox"]).lower():
                with st.container(border=True):
                    st.metric(f"Compte de {row['Nom Roblox']}", formater_monnaie(row["Solde"]))
                    st.write(f"💼 Emploi : {row['Emploiement']} | 📅 Arrivée : {row['Date d\'arrivée']}")
                    
                    if st.session_state.role in ["RCT", "Staff"]:
                        st.divider()
                        st.subheader("Action Bancaire Administrative")
                        amt_op = st.number_input("Montant de l'opération", min_value=0, key=f"bank_{idx}")
                        if st.button("Débiter Taxe/Amende", key=f"deb_{idx}"):
                            # Logique de débit
                            s_actuel = float(str(row["Solde"]).replace('$', ''))
                            df_bank.at[idx, "Solde"] = s_actuel - amt_op
                            db_conn.update(worksheet="Banque", data=df_bank)
                            enregistrer_log(st.session_state.role, f"Débit de {amt_op}$ sur {row['Nom Roblox']}")
                            st.success("Opération effectuée."); time.sleep(1); st.rerun()

# --------------------------------------------------------------------------------------
# MODULE : DMV / GARAGE (TOUS ROLES)
# --------------------------------------------------------------------------------------
with onglets[1]:
    st.header("🚗 Registre des Véhicules")
    
    if st.session_state.role in ["RCT", "Staff"]:
        with st.expander("🆕 Immatriculer un véhicule (Admin/RCT)", expanded=False):
            proprio = st.selectbox("Titulaire", ["---"] + df_bank["Nom Roblox"].tolist())
            v_marque = st.text_input("Marque du véhicule")
            v_plaque = st.text_input("Numéro de Plaque")
            v_assu = st.selectbox("Type d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            
            taxe_fixe = 175
            taxe_assu = 130 if "AVERIS" in v_assu else 150 if "RCT" in v_assu else 0
            total_v = taxe_fixe + taxe_assu
            
            st.info(f"Total à prélever : {total_v} $")
            
            if st.button("Valider l'Immatriculation"):
                if proprio != "---" and v_plaque:
                    idx_b = df_bank[df_bank["Nom Roblox"] == proprio].index[0]
                    solde_b = float(str(df_bank.at[idx_b, "Solde"]).replace('$', ''))
                    
                    if solde_b >= total_v:
                        # 1. Débit client
                        df_bank.at[idx_b, "Solde"] = solde_b - total_v
                        
                        # 2. Redirection assurance (AVERIS -> MOUNE2010)
                        if "AVERIS" in v_assu:
                            idx_m = df_bank[df_bank["Nom Roblox"] == COMPTE_MOUNE].index[0]
                            df_bank.at[idx_m, "Solde"] = float(str(df_bank.at[idx_m, "Solde"]).replace('$', '')) + 130
                        
                        # 3. Création véhicule
                        new_v = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                            "Nom d'utilisateur ROBLOX": proprio,
                            "Marque du véhicule": v_marque,
                            "Numéro de la plaque": v_plaque,
                            "Assurance": v_assu
                        }])
                        
                        db_conn.update(worksheet="Banque", data=df_bank)
                        db_conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_immat, new_v], ignore_index=True))
                        enregistrer_log(st.session_state.role, f"Nouvelle plaque {v_plaque} pour {proprio}")
                        st.success("Véhicule enregistré."); time.sleep(1); st.rerun()

    # Affichage du garage
    q_gar = st.text_input("Chercher une plaque ou un propriétaire").lower()
    for _, r in df_immat.iterrows():
        if not q_gar or q_gar in str(r["Numéro de la plaque"]).lower() or q_gar in str(r["Nom d'utilisateur ROBLOX"]).lower():
            st.markdown(f"**{r['Numéro de la plaque']}** | {r['Marque du véhicule']} ({r['Nom d'utilisateur ROBLOX']})")

# --------------------------------------------------------------------------------------
# MODULE : GESTION PERMIS (RCT & STAFF UNIQUEMENT)
# --------------------------------------------------------------------------------------
if st.session_state.role in ["RCT", "Staff"]:
    with onglets[2]:
        st.header("🛡️ Système des Permis de Conduire")
        search_p = st.text_input("Rechercher un conducteur (Permis)").lower()
        
        for idx, row in df_pts.iterrows():
            if not search_p or search_p in str(row["Nom Roblox"]).lower():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.write(f"👤 **{row['Nom Roblox']}**")
                    c2.write(f"Points : {row['PTS']} / 25")
                    status_cls = "badge-valid" if str(row["Validité"]).upper() == "OUI" else "badge-invalid"
                    c3.markdown(f'<span class="{status_cls}">{row["Validité"]}</span>', unsafe_allow_html=True)
                    
                    with st.expander("Modifier les points"):
                        new_val = st.number_input("Nouveau solde PTS", 0, 25, int(row["PTS"]), key=f"pts_{idx}")
                        if st.button("Sauvegarder Points", key=f"btn_pts_{idx}"):
                            df_pts.at[idx, "PTS"] = new_val
                            df_pts.at[idx, "Validité"] = "OUI" if new_val > 0 else "NON"
                            db_conn.update(worksheet="Points Permis", data=df_pts)
                            enregistrer_log(st.session_state.role, f"Maj Points {row['Nom Roblox']} -> {new_val}")
                            st.rerun()

# --------------------------------------------------------------------------------------
# MODULE : MDT SHERIFF (RCT & STAFF UNIQUEMENT)
# --------------------------------------------------------------------------------------
if st.session_state.role in ["RCT", "Staff"]:
    with onglets[3]:
        st.header("👮 Mobile Data Terminal (MDT)")
        q_mdt = st.text_input("ENTRER NOM OU PLAQUE POUR IDENTIFICATION").upper()
        
        if q_mdt:
            st.markdown(f"""
            <div class="mdt-container">
                [DATABASE] REQUÊTE NCICLancée...<br>
                [SEARCH] Cible : {q_mdt}<br>
                ------------------------------------------<br>
                [STATUS] IDENTITÉ LOCALE TROUVÉE<br>
                [CRIMINAL] AUCUN MANDAT ACTIF DÉLECTÉ<br>
                [DMV] VÉHICULE EN RÈGLE<br>
                ------------------------------------------<br>
                [AVERTISSEMENT] ACCÈS SURVEILLÉ PAR L'ÉTAT.
            </div>
            """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# MODULE : GREFFE / CRÉATION (STAFF UNIQUEMENT)
# --------------------------------------------------------------------------------------
if st.session_state.role == "Staff":
    with onglets[4]:
        st.header("🪪 Administration du Greffe")
        with st.form("creation_form"):
            st.subheader("Créer un Nouveau Résident")
            n_rob = st.text_input("Pseudo Roblox")
            n_dis = st.text_input("Pseudo Discord")
            n_job = st.selectbox("Emploiement", ["Civil", "Agent RCT", "Gouverneur", "Sheriff"])
            
            st.info("🎁 Automatique : 15k$ + 25 PTS + Date du jour")
            
            if st.form_submit_button("🔨 Générer Dossier Officiel"):
                if n_rob and n_dis:
                    # DATE AUTOMATIQUE
                    today = datetime.now().strftime("%d/%m/%Y")
                    
                    # 1. Ajout Banque
                    new_b = pd.DataFrame([{"Solde": 15000, "Emploiement": n_job, "Nom Discord": n_dis, "Nom Roblox": n_rob, "Date d'arrivée": today}])
                    # 2. Ajout Permis (PTS / Validité)
                    new_p = pd.DataFrame([{"Nom Discord": n_dis, "Nom Roblox": n_rob, "PTS": 25, "Validité": "OUI"}])
                    
                    db_conn.update(worksheet="Banque", data=pd.concat([df_bank, new_b], ignore_index=True))
                    db_conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_p], ignore_index=True))
                    
                    enregistrer_log("ADMIN", f"Création profil {n_rob} le {today}")
                    st.success("Profil créé avec succès !"); time.sleep(1); st.rerun()

# --------------------------------------------------------------------------------------
# MODULE : AUDITS (STAFF UNIQUEMENT)
# --------------------------------------------------------------------------------------
if st.session_state.role == "Staff":
    with onglets[5]:
        st.header("📜 Journal des Actions Administratives")
        if st.session_state.logs:
            for l in st.session_state.logs:
                st.write(l)
        else:
            st.info("Aucune action enregistrée pour le moment.")

# --------------------------------------------------------------------------------------
# FOOTER ET SÉCURITÉ
# --------------------------------------------------------------------------------------
st.sidebar.divider()
if st.sidebar.button("🚪 Déconnexion"):
    st.session_state.role = None
    st.rerun()

st.divider()
st.caption("Gouvernement du Comté de Rensselaer - Logiciel de gestion v75.0 (2026)")
