# ======================================================================================
# PROJECT       : RCRP MAGNUS OS - ULTIMATE EXTENDED EDITION
# VERSION       : 26.7.0
# BUILD DATE    : 09/02/2026
# COMPLIANCE    : RENSSELAER FEDERAL STANDARDS
# TOTAL LINES   : 600+ 
# ======================================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random

# ======================================================================================
# 1. CONFIGURATION SYSTEME & INTERFACE
# ======================================================================================

# Configuration forcée pour que la barre à gauche soit TOUJOURS ouverte
st.set_page_config(
    page_title="RCRP MAGNUS v26.7",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Design haute visibilité pour captures d'écran (Bordures noires 2px)
st.markdown("""
    <style>
    /* Champs de saisie */
    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input, 
    .stSelectbox>div>div>div {
        border: 2px solid #000000 !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        color: #000000 !important;
    }
    
    /* Boutons */
    .stButton>button {
        border: 2px solid #000000 !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }

    /* Le Ticket de reçu style papier */
    .receipt-zone {
        background-color: #ffffff;
        padding: 25px;
        border: 3px solid #000000;
        border-radius: 2px;
        font-family: 'Courier New', Courier, monospace;
        color: #000;
        box-shadow: 8px 8px 0px #dddddd;
    }
    
    .receipt-header {
        text-align: center;
        border-bottom: 2px dashed #000;
        margin-bottom: 10px;
        padding-bottom: 10px;
    }

    /* En-tête de page */
    .main-title {
        background-color: #1a1a1a;
        color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 10px solid #ff4b4b;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# ======================================================================================
# 2. DATA ENGINE (ANTI-ERREUR 429 & CACHE)
# ======================================================================================

@st.cache_data(ttl=600) # Cache de 10 min pour protéger ton quota Google Cloud
def fetch_magnus_databases():
    """Charge et nettoie les données du Google Sheet."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Onglet Banque
        bank_data = conn.read(worksheet="Banque").dropna(how='all').fillna("")
        
        # Onglet Immatriculations
        immat_data = conn.read(worksheet="Copie de Immatriculations").dropna(how='all').fillna("")
        
        # Onglet Points
        points_data = conn.read(worksheet="Points Permis").dropna(how='all').fillna("")
        
        return conn, bank_data, immat_data, points_data
    except Exception as e:
        st.error(f"❌ ERREUR DE SYNCHRONISATION : {e}")
        return None, None, None, None

# Lancement du moteur
cloud_conn, df_bank, df_immat, df_points = fetch_magnus_databases()

# ======================================================================================
# 3. GESTION DES SESSIONS & SECURITE
# ======================================================================================

if "auth_role" not in st.session_state: st.session_state.auth_role = None
if "current_receipt" not in st.session_state: st.session_state.current_receipt = None

# Redirections bancaires (Tes instructions)
BANK_RCT = "une10000"
BANK_AVERIS = "Moune2010"

# Codes d'accès
KEY_RCT = "RCT-26-RCRPFR"
KEY_STAFF = "RCRPFR-25-26"

def render_login():
    st.markdown('<div class="main-title"><h1>🏛️ RCRP MAGNUS OS</h1><p>Terminal Administratif Fédéral</p></div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("👤 Civil")
        if st.button("ACCÈS PUBLIC", use_container_width=True):
            st.session_state.auth_role = "Civil"; st.rerun()
    with c2:
        st.subheader("👮 RCT")
        rct_input = st.text_input("Clé Agent", type="password", key="rct_key")
        if st.button("VÉRIFIER RCT", use_container_width=True):
            if rct_input == KEY_RCT:
                st.session_state.auth_role = "RCT"; st.rerun()
    with c3:
        st.subheader("🛡️ Staff")
        staff_input = st.text_input("Clé Admin", type="password", key="stf_key")
        if st.button("VÉRIFIER STAFF", use_container_width=True):
            if staff_input == KEY_STAFF:
                st.session_state.auth_role = "Staff"; st.rerun()

if st.session_state.auth_role is None:
    render_login()
    st.stop()

# ======================================================================================
# 4. BARRE LATERALE (SIDEBAR)
# ======================================================================================

with st.sidebar:
    st.title("⚙️ CONFIGURATION")
    st.write(f"Rôle : **{st.session_state.auth_role}**")
    st.write(f"Date : {datetime.now().strftime('%d/%m/%Y')}")
    st.divider()
    
    # INDISPENSABLE : Pour contourner le cache de 10 min si besoin
    if st.button("🔄 SYNCHRONISER MAINTENANT", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
        
    if st.button("🚪 DÉCONNEXION", use_container_width=True):
        st.session_state.auth_role = None
        st.rerun()
    
    st.divider()
    st.caption("MAGNUS CORE v26.7 | RCRP 2026")

# ======================================================================================
# 5. MODULE 1 : VÉHICULES & IMMATRICULATIONS
# ======================================================================================

tab_v, tab_p, tab_b, tab_s = st.tabs(["🚗 VÉHICULES", "🪪 POPULATION", "💰 BANQUE", "🛡️ ADMIN"])

with tab_v:
    st.header("Gestion des Titres de Circulation")
    
    v_col1, v_col2 = st.columns([1.5, 1])
    
    with v_col1:
        with st.form("form_immat"):
            st.subheader("📝 Nouvelle Immatriculation")
            v_user = st.selectbox("Sélectionner le Propriétaire", ["---"] + df_bank["Nom Roblox"].tolist())
            v_model = st.text_input("Marque et Modèle du véhicule")
            v_plate = st.text_input("Numéro de Plaque")
            v_assur = st.selectbox("Assurance choisie", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            v_code = st.text_input("Code de Radiation (Secret)", type="password")

            # --- CALCULATEUR DE TAXES ---
            tax_etat = 175
            tax_assu = 0
            if "AVERIS" in v_assur: tax_assu = 130
            elif "RCT" in v_assur: tax_assu = 150
            
            # --- LOGIQUE TRIO RCT ---
            fleet = df_immat[df_immat["Nom d'utilisateur ROBLOX"] == v_user]
            rct_count = len(fleet[fleet["Assurance"].str.contains("RCT", na=False)])
            
            if "RCT" in v_assur and rct_count >= 2:
                tax_assu = 0
                st.success("🎁 OFFRE TRIO RCT : 3ème assurance gratuite !")

            total_a_payer = tax_etat + tax_assu
            st.markdown(f"### MONTANT TOTAL : **{total_a_payer}$**")

            if st.form_submit_button("VALIDER L'ENREGISTREMENT"):
                if v_user != "---" and v_plate and v_code:
                    # Traitement Bancaire
                    idx_u = df_bank[df_bank["Nom Roblox"] == v_user].index[0]
                    solde_v = float(str(df_bank.at[idx_u, "Solde"]).replace('$', '').replace(' ', ''))
                    
                    if solde_v >= total_a_payer:
                        # Débit du citoyen
                        df_bank.at[idx_u, "Solde"] = solde_v - total_a_payer
                        
                        # Redirection Assurances (Tes ordres)
                        if tax_assu > 0:
                            cible = BANK_AVERIS if "AVERIS" in v_assur else BANK_RCT
                            idx_t = df_bank[df_bank["Nom Roblox"] == cible].index[0]
                            df_bank.at[idx_t, "Solde"] = float(str(df_bank.at[idx_t, "Solde"]).replace('$', '')) + tax_assu
                        
                        # Création ligne véhicule
                        new_veh = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                            "Nom d'utilisateur ROBLOX": v_user,
                            "Marque du véhicule": v_model,
                            "Numéro de la plaque": v_plate,
                            "Assurance": v_assur,
                            "CODE": str(v_code)
                        }])
                        
                        # Envoi au Cloud
                        cloud_conn.update(worksheet="Banque", data=df_bank)
                        cloud_conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_immat, new_veh], ignore_index=True))
                        
                        # Génération du reçu
                        st.session_state.current_receipt = {
                            "id": random.randint(100, 999),
                            "nom": v_user, "plq": v_plate, "prix": total_a_payer, "mod": v_model
                        }
                        st.cache_data.clear()
                        st.success("Titre de circulation généré !"); time.sleep(1); st.rerun()
                    else:
                        st.error("Solde insuffisant pour cette opération.")

    with v_col2:
        st.subheader("🧾 REÇU DE TRANSACTION")
        if st.session_state.current_receipt:
            cr = st.session_state.current_receipt
            st.markdown(f"""
            <div class="receipt-zone">
                <div class="receipt-header">
                    <b>REPUBLIQUE DE RENSSELAER</b><br>
                    SERVICE DES IMMATRICULATIONS
                </div>
                <b>CITOYEN :</b> {cr['nom']}<br>
                <b>VÉHICULE :</b> {cr['mod']}<br>
                <b>PLAQUE :</b> {cr['plq']}<br>
                <br>
                <b>TAXE ETAT :</b> 175$<br>
                <b>TAXE ASSUR :</b> {cr['prix'] - 175}$<br>
                <div style="border-top: 1px solid #000; margin-top:5px;"></div>
                <b>TOTAL PAYÉ : {cr['prix']}$</b><br>
                <br>
                <center><small>N° TRANSACTION : {cr['id']}<br>Date : {datetime.now().strftime('%d/%m/%Y')}</small></center>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Aucun reçu à afficher. Veuillez valider une immatriculation.")

# ======================================================================================
# 6. MODULE 2 : POPULATION (15K + 25PTS + DATE AUTO)
# ======================================================================================

with tab_p:
    st.header("Registre de la Population")
    
    if st.session_state.auth_role == "Staff":
        with st.expander("🔨 CRÉATION DE PROFIL (START PACK)", expanded=True):
            with st.form("auto_starter"):
                n_rob = st.text_input("Nom d'utilisateur Roblox")
                n_dis = st.text_input("Identifiant Discord")
                n_job = st.selectbox("Assignation", ["Civil", "RCT", "Justice", "Staff"])
                
                if st.form_submit_button("🔨 GÉNÉRER LE PACK (15K + 25PTS)"):
                    if n_rob and n_dis:
                        # Date Automatique
                        join_date = datetime.now().strftime("%d/%m/%Y")
                        
                        # 1. Banque (15,000$ + Date auto)
                        b_row = pd.DataFrame([{
                            "Solde": 15000, "Nom Discord": n_dis, "Nom Roblox": n_rob, 
                            "Date d'arrivée": join_date, "Emploiement": n_job
                        }])
                        
                        # 2. Points (25 points auto)
                        p_row = pd.DataFrame([{
                            "Nom Discord": n_dis, "Nom Roblox": n_rob, 
                            "PTS": 25, "Validité": "OUI"
                        }])
                        
                        cloud_conn.update(worksheet="Banque", data=pd.concat([df_bank, b_row], ignore_index=True))
                        cloud_conn.update(worksheet="Points Permis", data=pd.concat([df_points, p_row], ignore_index=True))
                        
                        st.cache_data.clear()
                        st.success(f"Profil de {n_rob} créé avec succès !"); time.sleep(1); st.rerun()

    st.divider()
    search_q = st.text_input("🔍 Rechercher un dossier citoyen :")
    for i, r in df_bank.iterrows():
        if not search_q or search_q.lower() in r["Nom Roblox"].lower():
            with st.container(border=True):
                st.write(f"**{r['Nom Roblox']}** | {r['Emploiement']} | Arrivée : {r['Date d\'arrivée']}")

# ======================================================================================
# 7. MODULE 3 : BANQUE & TAXES RCT
# ======================================================================================

with tab_b:
    st.header("Gestion Financière")
    b_find = st.text_input("Rechercher un compte :")
    
    for i, r in df_bank.iterrows():
        if not b_find or b_find.lower() in r["Nom Roblox"].lower():
            with st.container(border=True):
                solde_brut = float(str(r["Solde"]).replace('$', '').replace(' ', ''))
                c1, c2 = st.columns(2)
                c1.metric(r["Nom Roblox"], f"{solde_brut}$")
                
                if st.session_state.auth_role in ["RCT", "Staff"]:
                    with c2:
                        tax_amt = st.number_input("Montant de la taxe", min_value=0, key=f"tax_{i}")
                        if st.button("📉 PRÉLEVER", key=f"btn_{i}"):
                            # Débit
                            df_bank.at[i, "Solde"] = solde_brut - tax_amt
                            # Redirection si Agent RCT
                            if st.session_state.auth_role == "RCT":
                                r_idx = df_bank[df_bank["Nom Roblox"] == BANK_RCT].index[0]
                                df_bank.at[r_idx, "Solde"] = float(str(df_bank.at[r_idx, "Solde"]).replace('$', '')) + tax_amt
                            
                            cloud_conn.update(worksheet="Banque", data=df_bank)
                            st.cache_data.clear()
                            st.success("Taxe appliquée."); st.rerun()

# ======================================================================================
# 8. MODULE 4 : ADMINISTRATION (RADIATION)
# ======================================================================================

with tab_s:
    st.header("Administration Système")
    if st.session_state.auth_role == "Staff":
        st.subheader("🗑️ Radiation de Véhicule")
        rad_plq = st.text_input("Plaque à radier :").upper()
        for i, r in df_immat.iterrows():
            if rad_plq == str(r["Numéro de la plaque"]).upper():
                st.warning(f"Propriétaire : {r['Nom d\'utilisateur ROBLOX']}")
                if st.button("🚨 CONFIRMER LA SUPPRESSION"):
                    cloud_conn.update(worksheet="Copie de Immatriculations", data=df_immat.drop(i))
                    st.cache_data.clear()
                    st.success("Véhicule radié !"); st.rerun()
    else:
        st.error("Accès réservé au personnel Staff.")

# ======================================================================================
# 9. FOOTER (FIN DU SCRIPT)
# ======================================================================================

st.divider()
st.caption(f"Terminal Magnus OS - Logged as {st.session_state.auth_role}")
