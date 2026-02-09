# ======================================================================================
# PROJECT       : RCRP FR OS - CLEAN EDITION
# VERSION       : 29.0.0 (INTERFACE ÉPURÉE)
# BUILD DATE    : 09/02/2026
# ======================================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# ======================================================================================
# 1. CONFIGURATION ET STYLE (BORDURES NOIRES & CLEAN UI)
# ======================================================================================

st.set_page_config(page_title="RCRP FR OS", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stTextInput>div>div>input, .stNumberInput>div>div>input, 
    .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
        border: 2px solid #000000 !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    .header-box {
        background-color: #1a1a1a;
        color: #ffffff;
        padding: 30px;
        border-radius: 10px;
        border-left: 10px solid #d32f2f;
        margin-bottom: 20px;
    }
    .receipt-container {
        background-color: #ffffff;
        padding: 20px;
        border: 2px solid #000000;
        font-family: 'Courier New', Courier, monospace;
    }
    .stButton>button {
        border: 2px solid #000 !important;
        font-weight: 900 !important;
        height: 3em;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ======================================================================================
# 2. ENGINE : CONNEXION CLOUD
# ======================================================================================

cloud_conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def load_data():
    df_bank = cloud_conn.read(worksheet="Banque").dropna(how='all').fillna("")
    df_immat = cloud_conn.read(worksheet="Copie de Immatriculations").dropna(how='all').fillna("")
    df_pts = cloud_conn.read(worksheet="Points Permis").dropna(how='all').fillna("")
    return df_bank, df_immat, df_pts

df_b, df_i, df_p = load_data()

# ======================================================================================
# 3. SESSIONS & CONSTANTES
# ======================================================================================

if "user_auth" not in st.session_state: st.session_state.user_auth = None
if "active_receipt" not in st.session_state: st.session_state.active_receipt = None

ACC_RCT = "une10000"
ACC_AVERIS = "Moune2010"
KEY_RCT = "RCT-26-RCRPFR"
KEY_STAFF = "RCRPFR-25-26"

# ======================================================================================
# 4. SIDEBAR (LOGO + DATE & HEURE + LOGOUT)
# ======================================================================================

with st.sidebar:
    st.image("https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=698a61b3&is=69891033&hm=8210184eaca7e5b311b5e00c11ba2e30e86bd67228f54e1f148577592ecfb090&=&format=webp&quality=lossless&width=2732&height=1508", use_container_width=True)
    
    st.divider()
    # Affichage Date et Heure à gauche
    now = datetime.now()
    st.subheader(f"📅 {now.strftime('%d/%m/%Y')}")
    st.subheader(f"⏰ {now.strftime('%H:%M:%S')}")
    st.divider()
    
    st.write(f"Accréditation : **{st.session_state.user_auth}**")
    if st.button("🔄 SYNCHRONISER"): st.cache_data.clear(); st.rerun()
    if st.button("🚪 DÉCONNEXION"): st.session_state.user_auth = None; st.rerun()

# ======================================================================================
# 5. ÉCRAN DE CONNEXION
# ======================================================================================

if st.session_state.user_auth is None:
    st.markdown('<div class="header-box"><h1>🏛️ RCRPFR OS - TERMINAL FÉDÉRAL</h1></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("ACCÈS CIVIL"): st.session_state.user_auth = "Civil"; st.rerun()
    with c2:
        k_r = st.text_input("Code RCT", type="password")
        if st.button("LOGIN RCT"):
            if k_r == KEY_RCT: st.session_state.user_auth = "RCT"; st.rerun()
    with c3:
        k_s = st.text_input("Code Staff", type="password")
        if st.button("LOGIN STAFF"):
            if k_s == KEY_STAFF: st.session_state.user_auth = "Staff"; st.rerun()
    st.stop()

# ======================================================================================
# 6. LE DOSSIER CITOYEN (VUE UNIQUE ET CENTRALE)
# ======================================================================================

st.markdown('<div class="header-box"><h2>📂 DOSSIER CITOYEN UNIFIÉ</h2></div>', unsafe_allow_html=True)

target = st.selectbox("Rechercher un citoyen :", ["---"] + df_b["Nom Roblox"].tolist())

if target != "---":
    col1, col2, col3 = st.columns(3)
    with col1:
        p_data = df_p[df_p["Nom Roblox"] == target]
        st.metric("POINTS PERMIS", f"{p_data.iloc[0]['PTS'] if not p_data.empty else '?'}/25")
        st.caption(f"Validité : {p_data.iloc[0]['Validité'] if not p_data.empty else 'Inconnue'}")
    with col2:
        b_data = df_b[df_b["Nom Roblox"] == target]
        st.metric("SOLDE BANCAIRE", f"{b_data.iloc[0]['Solde'] if not b_data.empty else '0'}$")
        st.caption(f"Métier : {b_data.iloc[0]['Emploiement'] if not b_data.empty else 'Civil'}")
    with col3:
        v_data = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
        st.write(f"🚘 **{len(v_data)} Véhicule(s)**")
        for _, v in v_data.iterrows(): st.caption(f"• {v['Marque du véhicule']} ({v['Numéro de la plaque']})")

st.divider()

# ======================================================================================
# 7. LES ONGLETS D'ACTION (ÉPURÉS)
# ======================================================================================

# On ne garde que les onglets "Action". La visibilité des listes est supprimée.
tabs = st.tabs(["🚗 IMMATRICULATION", "⚙️ SERVICES RCT", "🛡️ ADMINISTRATION"])

# --- ONGLET IMMATRICULATION ---
with tabs[0]:
    col_f, col_r = st.columns([1.5, 1])
    with col_f:
        with st.form("immat_form"):
            st.subheader("📝 Nouvelle Immatriculation")
            f_o = st.selectbox("Propriétaire", ["---"] + df_b["Nom Roblox"].tolist())
            f_m = st.text_input("Modèle")
            f_p = st.text_input("Plaque")
            f_a = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            f_s = st.text_input("Code Secret de Radiation", type="password")
            
            p_tot = 175 + (130 if "AVERIS" in f_a else (150 if "RCT" in f_a else 0))
            if "RCT" in f_a and len(df_i[df_i["Nom d'utilisateur ROBLOX"] == f_o]) >= 2: p_tot -= 150
            
            if st.form_submit_button(f"PAYER {p_tot}$"):
                u_idx = df_b[df_b["Nom Roblox"] == f_o].index[0]
                solde = float(str(df_b.at[u_idx, "Solde"]).replace('$', ''))
                if solde >= p_tot:
                    df_b.at[u_idx, "Solde"] = solde - p_tot
                    if p_tot > 175:
                        dest = ACC_AVERIS if "AVERIS" in f_a else ACC_RCT
                        d_idx = df_b[df_b["Nom Roblox"] == dest].index[0]
                        df_b.at[d_idx, "Solde"] = float(str(df_b.at[d_idx, "Solde"]).replace('$', '')) + (p_tot - 175)
                    
                    new_v = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y"), "Nom d'utilisateur ROBLOX": f_o, "Marque du véhicule": f_m, "Numéro de la plaque": f_p, "Assurance": f_a, "CODE": f_s}])
                    cloud_conn.update(worksheet="Banque", data=df_b)
                    cloud_conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_i, new_v]))
                    st.session_state.active_receipt = {"nom": f_o, "plq": f_p, "prix": p_tot}
                    st.cache_data.clear(); st.rerun()

    with col_r:
        if st.session_state.active_receipt:
            r = st.session_state.active_receipt
            st.markdown(f'<div class="receipt-container"><b>RECU FEDERAL</b><br>NOM: {r["nom"]}<br>PLAQUE: {r["plq"]}<br>TOTAL: {r["prix"]}$</div>', unsafe_allow_html=True)
        
        st.divider()
        st.subheader("🗑️ RADIATION")
        rad_p = st.text_input("Plaque à radier", key="radp").upper()
        rad_c = st.text_input("Code Secret", type="password", key="radc")
        if st.button("RADIER LE VÉHICULE"):
            match = df_i[df_i["Numéro de la plaque"].astype(str).str.upper() == rad_p]
            if not match.empty and (str(rad_c) == str(match.iloc[0]["CODE"]) or st.session_state.user_auth == "Staff"):
                cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i.drop(match.index[0]))
                st.cache_data.clear(); st.success("Radié !"); time.sleep(1); st.rerun()

# --- ONGLET RCT (POINTS & TAXES) ---
with tabs[1]:
    if st.session_state.user_auth in ["RCT", "Staff"]:
        st.subheader("👮 ACTIONS DE SERVICE")
        if target != "---":
            st.write(f"Actions sur le dossier de : **{target}**")
            c_p1, c_p2 = st.columns(2)
            # Retrait points
            p_loss = c_p1.number_input("Retirer Points Permis", min_value=0, max_value=25)
            if c_p1.button("APPLIQUER RETRAIT POINTS"):
                idx_p = df_p[df_p["Nom Roblox"] == target].index[0]
                df_p.at[idx_p, "PTS"] = max(0, int(df_p.at[idx_p, "PTS"]) - p_loss)
                cloud_conn.update(worksheet="Points Permis", data=df_p)
                st.cache_data.clear(); st.success("Points mis à jour"); st.rerun()
            # Taxe/Amende
            tax_v = c_p2.number_input("Montant Amende ($)", min_value=0)
            if c_p2.button("APPLIQUER AMENDE"):
                idx_b = df_b[df_b["Nom Roblox"] == target].index[0]
                df_b.at[idx_b, "Solde"] = float(str(df_b.at[idx_b, "Solde"]).replace('$', '')) - tax_v
                # Redir RCT
                r_idx = df_b[df_b["Nom Roblox"] == ACC_RCT].index[0]
                df_b.at[r_idx, "Solde"] = float(str(df_b.at[r_idx, "Solde"]).replace('$', '')) + tax_v
                cloud_conn.update(worksheet="Banque", data=df_b)
                st.cache_data.clear(); st.success("Amende perçue"); st.rerun()
    else: st.error("Accès réservé aux agents RCT.")

# --- ONGLET ADMIN (CREATION PROFIL) ---
with tabs[2]:
    if st.session_state.user_auth == "Staff":
        with st.form("new_citizen"):
            st.subheader("🔨 Création de Profil (Pack 15k + 25pts)")
            n_r = st.text_input("Nom Roblox")
            n_d = st.text_input("Discord")
            n_j = st.selectbox("Job", ["Civil", "RCT", "Gouv"])
            if st.form_submit_button("VALIDER L'ARRIVÉE"):
                d_now = datetime.now().strftime("%d/%m/%Y")
                rb = pd.DataFrame([{"Solde": 15000, "Nom Discord": n_d, "Nom Roblox": n_r, "Date d'arrivée": d_now, "Emploiement": n_j}])
                rp = pd.DataFrame([{"Nom Discord": n_d, "Nom Roblox": n_r, "PTS": 25, "Validité": "OUI"}])
                cloud_conn.update(worksheet="Banque", data=pd.concat([df_b, rb]))
                cloud_conn.update(worksheet="Points Permis", data=pd.concat([df_p, rp]))
                st.cache_data.clear(); st.success("Dossier créé !"); st.rerun()
    else: st.error("Accès Staff uniquement.")
