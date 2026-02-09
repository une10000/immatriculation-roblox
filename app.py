# ======================================================================================
# PROJECT       : RCRP FR OS - ULTIMATE MASTER EDITION
# VERSION       : 28.5.0 (FULL BUILD)
# BUILD DATE    : 09/02/2026
# ======================================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random

# ======================================================================================
# 1. CONFIGURATION ET DESIGN SYSTEM (CSS CUSTOM)
# ======================================================================================

st.set_page_config(
    page_title="RCRP FR OS - SYSTEME FEDERAL",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style visuel pour les captures d'écran et l'immersion
st.markdown("""
    <style>
    /* Global Background */
    .main { background-color: #f4f4f4; }
    
    /* Inputs avec bordures noires 2px pour visibilité screen */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, 
    .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
        border: 2px solid #000000 !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* En-tête RCRP FR */
    .header-box {
        background: linear-gradient(90deg, #1a1a1a 0%, #333333 100%);
        color: #ffffff;
        padding: 40px;
        border-radius: 10px;
        border-left: 15px solid #d32f2f;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* Reçu Fédéral (Papier Thermique) */
    .receipt-container {
        background-color: #ffffff;
        padding: 30px;
        border: 3px solid #000000;
        font-family: 'Courier New', Courier, monospace;
        color: #000;
        box-shadow: 10px 10px 0px #cccccc;
        line-height: 1.2;
    }
    
    .receipt-line { border-top: 2px dashed #000; margin: 15px 0; }
    .receipt-header { text-align: center; font-weight: bold; font-size: 1.2em; }

    /* Boutons Massifs */
    .stButton>button {
        border: 2px solid #000 !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        height: 3.5em;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #000 !important;
        color: #fff !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 800; color: #d32f2f; }
    </style>
""", unsafe_allow_html=True)

# ======================================================================================
# 2. CORE ENGINE : CONNEXION CLOUD (ANTI-RECURSION)
# ======================================================================================

# Initialisation de la connexion hors des fonctions pour éviter les boucles
cloud_conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def load_federal_data():
    """Chargement synchronisé de toutes les bases de données"""
    try:
        df_bank = cloud_conn.read(worksheet="Banque").dropna(how='all').fillna("")
        df_immat = cloud_conn.read(worksheet="Copie de Immatriculations").dropna(how='all').fillna("")
        df_pts = cloud_conn.read(worksheet="Points Permis").dropna(how='all').fillna("")
        return df_bank, df_immat, df_pts
    except Exception as e:
        st.error(f"⚠️ ÉCHEC DE LIAISON CLOUD : {e}")
        return None, None, None

df_b, df_i, df_p = load_federal_data()

# ======================================================================================
# 3. GESTION DES SESSIONS & CONSTANTES SÉCURITÉ
# ======================================================================================

if "user_auth" not in st.session_state: st.session_state.user_auth = None
if "active_receipt" not in st.session_state: st.session_state.active_receipt = None
if "audit_trail" not in st.session_state: st.session_state.audit_trail = []

# Paramètres Bancaires (Redirections demandées)
ACC_RCT = "une10000"
ACC_AVERIS = "Moune2010"

# Clés d'Accès
KEY_RCT = "RCT-26-RCRPFR"
KEY_STAFF = "RCRPFR-25-26"

def audit_log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.audit_trail.append(f"[{now}] {msg}")

# ======================================================================================
# 4. ÉCRAN D'IDENTIFICATION (LOCKSCREEN)
# ======================================================================================

if st.session_state.user_auth is None:
    st.markdown("""
        <div class="header-box">
            <h1>🏛️ RCRPFR OS - TERMINAL FÉDÉRAL</h1>
            <p>SYSTÈME D'OPÉRATION NATIONAL - VERSION 2026</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns(3)
    
    with col_l1:
        st.subheader("👤 ESPACE CIVIL")
        if st.button("ACCÈS LIBRE"):
            st.session_state.user_auth = "Civil"; audit_log("Mode Civil activé"); st.rerun()
            
    with col_l2:
        st.subheader("👮 ESPACE AGENT RCT")
        login_rct = st.text_input("Identifiant Agent", type="password", key="login_rct")
        if st.button("AUTHENTIFICATION RCT"):
            if login_rct == KEY_RCT:
                st.session_state.user_auth = "RCT"; audit_log("Agent RCT connecté"); st.rerun()
            else: st.error("Code de service invalide.")
            
    with col_l3:
        st.subheader("🛡️ ESPACE STAFF")
        login_staff = st.text_input("Clé de Sécurité", type="password", key="login_staff")
        if st.button("AUTHENTIFICATION STAFF"):
            if login_staff == KEY_STAFF:
                st.session_state.user_auth = "Staff"; audit_log("Staff connecté"); st.rerun()
            else: st.error("Accès refusé.")
    st.stop()

# ======================================================================================
# 5. BARRE LATÉRALE (LOGO & CONTRÔLES)
# ======================================================================================

with st.sidebar:
    # --- TON LOGO (CORRIGÉ) ---
    st.image("https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=698a61b3&is=69891033&hm=8210184eaca7e5b311b5e00c11ba2e30e86bd67228f54e1f148577592ecfb090&=&format=webp&quality=lossless&width=2732&height=1508", use_container_width=True)
    
    st.title("⚙️ SYSTÈME RCRP")
    st.markdown(f"Opérateur : **{st.session_state.user_auth}**")
    st.divider()
    
    if st.button("🔄 SYNCHRONISATION NUAGE"):
        st.cache_data.clear(); st.rerun()
    
    if st.button("🚪 FERMER LA SESSION"):
        st.session_state.user_auth = None; st.rerun()
    
    st.divider()
    st.subheader("📋 AUDIT LOGS")
    for log in reversed(st.session_state.audit_trail[-10:]):
        st.caption(log)

# ======================================================================================
# 6. MODULE CENTRAL : DOSSIER CITOYEN UNIFIÉ
# ======================================================================================

with st.container(border=True):
    st.subheader("👤 CONSULTATION RAPIDE DU DOSSIER")
    citizen_search = st.selectbox("Sélectionner un citoyen :", ["---"] + df_b["Nom Roblox"].tolist())
    
    if citizen_search != "---":
        c1, c2, c3 = st.columns(3)
        
        # Section Points
        with c1:
            p_data = df_p[df_p["Nom Roblox"] == citizen_search]
            pts_val = p_data.iloc[0]["PTS"] if not p_data.empty else "N/A"
            st.metric("POINTS PERMIS", f"{pts_val}/25")
            st.write(f"Permis valide : **{p_data.iloc[0]['Validité'] if not p_data.empty else 'Non'}**")
            
        # Section Finance
        with c2:
            b_data = df_b[df_b["Nom Roblox"] == citizen_search]
            bal_val = b_data.iloc[0]["Solde"] if not b_data.empty else "0"
            st.metric("SOLDE BANCAIRE", f"{bal_val}$")
            st.caption(f"Job : {b_data.iloc[0]['Emploiement'] if not b_data.empty else 'Civil'}")
            
        # Section Véhicules
        with c3:
            v_data = df_i[df_i["Nom d'utilisateur ROBLOX"] == citizen_search]
            st.write(f"🚘 **{len(v_data)} VÉHICULE(S)**")
            for _, v in v_data.iterrows():
                st.caption(f"• {v['Marque du véhicule']} - **{v['Numéro de la plaque']}**")

# ======================================================================================
# 7. NAVIGATION PAR ONGLETS (GESTION TOTALE)
# ======================================================================================

t_immat, t_pop, t_pts, t_bank, t_adm = st.tabs([
    "🚗 VÉHICULES", "🪪 CITOYENS", "🪪 PERMIS", "💰 BANQUE", "🛡️ ADMIN"
])

# --- MODULE VÉHICULES ---
with t_immat:
    # Section Radiation (Pour Civils et Staff)
    with st.expander("🚨 DEMANDE DE RADIATION DE VÉHICULE"):
        st.warning("Attention : cette action est irréversible.")
        rad_col1, rad_col2 = st.columns(2)
        plate_target = rad_col1.text_input("Numéro de Plaque", key="plate_target").upper()
        plate_code = rad_col2.text_input("Code de Radiation (Secret)", type="password", key="plate_code")
        
        if st.button("CONFIRMER LA RADIATION DÉFINITIVE"):
            v_match = df_i[df_i["Numéro de la plaque"].astype(str).str.upper() == plate_target]
            if not v_match.empty:
                if str(plate_code) == str(v_match.iloc[0]["CODE"]) or st.session_state.user_auth == "Staff":
                    df_i = df_i.drop(v_match.index[0])
                    cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i)
                    audit_log(f"Radiation : {plate_target}")
                    st.cache_data.clear(); st.success("Véhicule supprimé du registre."); time.sleep(1); st.rerun()
                else: st.error("Code de radiation invalide.")
            else: st.error("Véhicule introuvable.")

    st.divider()
    
    # Formulaire de nouvelle Immatriculation
    fi1, fi2 = st.columns([1.5, 1])
    with fi1:
        with st.form("new_immat_form"):
            st.subheader("📝 Demande de Carte Grise")
            f_u = st.selectbox("Identité du Propriétaire", ["---"] + df_b["Nom Roblox"].tolist())
            f_m = st.text_input("Marque & Modèle du véhicule")
            f_p = st.text_input("Plaque d'Immatriculation")
            f_a = st.selectbox("Contrat d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            f_s = st.text_input("Définir un Code de Radiation", type="password")
            
            # Calcul financier
            taxe_fixe = 175
            taxe_assu = 130 if "AVERIS" in f_a else (150 if "RCT" in f_a else 0)
            
            # Logic "Trio RCT" : Si déjà 2 voitures immatriculées, assurance gratuite
            if "RCT" in f_a:
                existing_v = len(df_i[df_i["Nom d'utilisateur ROBLOX"] == f_u])
                if existing_v >= 2:
                    taxe_assu = 0
                    st.info("🎁 Bonus Trio RCT : Assurance offerte !")
            
            total_facture = taxe_fixe + taxe_assu
            
            if st.form_submit_button(f"S'ACQUITTER DE {total_facture}$ ET ENREGISTRER"):
                if f_u != "---" and f_p:
                    u_idx = df_b[df_b["Nom Roblox"] == f_u].index[0]
                    u_solde = float(str(df_b.at[u_idx, "Solde"]).replace('$', ''))
                    
                    if u_solde >= total_facture:
                        # Débit Citoyen
                        df_b.at[u_idx, "Solde"] = u_solde - total_facture
                        
                        # Crédit Assurance (Redirection vers Moune2010 ou une10000)
                        if taxe_assu > 0:
                            dest_acc = ACC_AVERIS if "AVERIS" in f_a else ACC_RCT
                            d_idx = df_b[df_b["Nom Roblox"] == dest_acc].index[0]
                            df_b.at[d_idx, "Solde"] = float(str(df_b.at[d_idx, "Solde"]).replace('$', '')) + taxe_assu
                        
                        # Ajout Véhicule
                        new_veh = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                            "Nom d'utilisateur ROBLOX": f_u,
                            "Marque du véhicule": f_m,
                            "Numéro de la plaque": f_p,
                            "Assurance": f_a,
                            "CODE": f_s
                        }])
                        
                        cloud_conn.update(worksheet="Banque", data=df_b)
                        cloud_conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_i, new_veh]))
                        st.session_state.active_receipt = {"nom": f_u, "plq": f_p, "prix": total_facture, "mod": f_m}
                        audit_log(f"Immat: {f_p} pour {f_u}"); st.cache_data.clear(); st.rerun()
                    else: st.error("Fonds insuffisants sur le compte bancaire.")

    with fi2:
        if st.session_state.active_receipt:
            r = st.session_state.active_receipt
            st.markdown(f"""
                <div class="receipt-container">
                    <div class="receipt-header">RÉPUBLIQUE DE RENSSELAER<br>REÇU OFFICIEL</div>
                    <div class="receipt-line"></div>
                    <b>DATE:</b> {datetime.now().strftime("%d/%m/%Y")}<br>
                    <b>PROPRIÉTAIRE:</b> {r['nom']}<br>
                    <b>VÉHICULE:</b> {r['mod']}<br>
                    <b>PLAQUE:</b> {r['plq']}<br>
                    <div class="receipt-line"></div>
                    <b>TOTAL PAYÉ: {r['prix']}$</b>
                    <div class="receipt-line"></div>
                    <center><small>Document certifié conforme</small></center>
                </div>
            """, unsafe_allow_html=True)

# --- MODULE CITOYENS (PACK DE DEPART AUTO) ---
with t_pop:
    if st.session_state.user_auth == "Staff":
        with st.form("staff_create_citizen"):
            st.subheader("🔨 Création de Dossier Fédéral (Pack 15,000$)")
            c_nom = st.text_input("Nom d'utilisateur Roblox")
            c_dis = st.text_input("Identifiant Discord")
            c_job = st.selectbox("Secteur d'Activité", ["Civil", "RCT", "Gouverneur", "Justice"])
            
            if st.form_submit_button("VALIDER L'ARRIVÉE"):
                if c_nom and c_dis:
                    # DATE AUTOMATIQUE LORS DE LA CREATION
                    date_now = datetime.now().strftime("%d/%m/%Y")
                    
                    # Pack de démarrage : 15k en banque + 25pts permis
                    b_entry = pd.DataFrame([{
                        "Solde": 15000, "Nom Discord": c_dis, "Nom Roblox": c_nom, 
                        "Date d'arrivée": date_now, "Emploiement": c_job
                    }])
                    p_entry = pd.DataFrame([{
                        "Nom Discord": c_dis, "Nom Roblox": c_nom, "PTS": 25, "Validité": "OUI"
                    }])
                    
                    cloud_conn.update(worksheet="Banque", data=pd.concat([df_b, b_entry]))
                    cloud_conn.update(worksheet="Points Permis", data=pd.concat([df_p, p_entry]))
                    audit_log(f"Arrivée : {c_nom}"); st.cache_data.clear(); st.success("Citoyen enregistré !"); st.rerun()
    
    st.dataframe(df_b, use_container_width=True)

# --- MODULE PERMIS (MODIFICATION POINTS) ---
with t_pts:
    st.header("🛂 Contrôle des Licences de Conduite")
    for idx, row in df_p.iterrows():
        with st.container(border=True):
            pcol1, pcol2, pcol3 = st.columns([2, 1, 1])
            pcol1.write(f"👤 **{row['Nom Roblox']}**")
            pcol2.write(f"Points : **{row['PTS']}**")
            
            if st.session_state.user_auth in ["RCT", "Staff"]:
                p_loss = pcol3.number_input("Retrait", min_value=0, max_value=25, key=f"p_loss_{idx}")
                if pcol3.button("APPLIQUER RETRAIT", key=f"p_btn_{idx}"):
                    new_pts = int(row["PTS"]) - p_loss
                    df_p.at[idx, "PTS"] = max(0, new_pts)
                    if new_pts <= 0: df_p.at[idx, "Validité"] = "NON"
                    
                    cloud_conn.update(worksheet="Points Permis", data=df_p)
                    audit_log(f"Points : -{p_loss} pour {row['Nom Roblox']}")
                    st.cache_data.clear(); st.rerun()

# --- MODULE BANQUE (TRANSFERS & TAXES) ---
with t_bank:
    st.header("💰 Terminal des Transactions")
    for idx, row in df_b.iterrows():
        with st.container(border=True):
            bcol1, bcol2, bcol3 = st.columns([2, 1, 1])
            bcol1.write(f"**{row['Nom Roblox']}** | Solde : **{row['Solde']}$**")
            
            if st.session_state.user_auth in ["RCT", "Staff"]:
                tax_val = bcol2.number_input("Montant amende/taxe", min_value=0, key=f"tax_{idx}")
                if bcol3.button("PRÉLEVER", key=f"tax_btn_{idx}"):
                    curr_val = float(str(row["Solde"]).replace('$', ''))
                    df_b.at[idx, "Solde"] = curr_val - tax_val
                    
                    # Redirection vers RCT si c'est un agent qui taxe
                    if st.session_state.user_auth == "RCT":
                        r_idx = df_b[df_b["Nom Roblox"] == ACC_RCT].index[0]
                        df_b.at[r_idx, "Solde"] = float(str(df_b.at[r_idx, "Solde"]).replace('$', '')) + tax_val
                    
                    cloud_conn.update(worksheet="Banque", data=df_b)
                    audit_log(f"Taxe: {tax_val}$ sur {row['Nom Roblox']}"); st.cache_data.clear(); st.rerun()

# --- MODULE ADMIN (SÉCURITÉ) ---
with t_adm:
    st.header("🛡️ Administration Système")
    if st.session_state.user_auth == "Staff":
        st.write("Gestion forcée des enregistrements.")
        force_plate = st.text_input("Plaque à supprimer (Force Admin)").upper()
        if st.button("EXÉCUTER SUPPRESSION FORCEE"):
            m_a = df_i[df_i["Numéro de la plaque"].astype(str).str.upper() == force_plate]
            if not m_a.empty:
                df_i = df_i.drop(m_a.index[0])
                cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i)
                audit_log(f"ADMIN DELETE: {force_plate}"); st.cache_data.clear(); st.success("Supprimé."); st.rerun()
    else:
        st.error("Niveau d'accréditation insuffisant.")

# ======================================================================================
# 8. FOOTER
# ======================================================================================
st.divider()
st.caption(f"RCRP FR OS v28.5.0 | Opérationnel | © 2026 République de Rensselaer")
