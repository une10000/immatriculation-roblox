# ==============================================================================
# 🏛️ REPUBLIQUE DE CALIFORNIE RP - SYSTEME DE GESTION INTEGRAL (v11.1)
# ==============================================================================
# Version : 11.1 | Date : 08/02/2026 | Développeur : RCRP Tech Division
# 
# [LOGIQUE MÉTIER]
# - Assurances Averis : Crédits -> 'Moune2010'
# - Assurances RCT : Crédits -> 'une10000'
# - Profils : Date d'arrivée AUTO à la création.
# - Civil : Recherche par Roblox/Discord + Affichage visuel du permis.
# ==============================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURATION DE L'INTERFACE ---
st.set_page_config(
    page_title="RCRP - Système Intégré de l'État",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ENGINE CSS (Design Complet 600px Height) ---
st.markdown("""
    <style>
    .main { background-color: #0b0d10; color: #ecf0f1; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(30, 34, 40, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 40px !important;
        height: 600px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
    }

    .transaction-ticket {
        background: linear-gradient(135deg, #1e272e 0%, #050505 100%);
        border: 1px solid #27ae60;
        border-left: 12px solid #27ae60;
        padding: 25px;
        border-radius: 12px;
        margin: 20px 0;
        color: #ffffff;
        font-family: 'Consolas', 'Courier New', monospace;
    }

    .id-card {
        background: rgba(52, 152, 219, 0.1);
        border: 1px solid #3498db;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .license-box {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-top: 10px;
        background: rgba(0,0,0,0.3);
    }

    .stMetric {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }

    [data-testid="stSidebar"] img {
        border-radius: 25px;
        border: 3px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 25px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #c0392b !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONSTANTES ---
AUTH_ADMIN_KEY = "RCRPFR-25-26" 
AUTH_PRO_KEY = "RCT-26-RCRPFR" 
TARGET_RCT = "une10000" 
TARGET_AVERIS = "Moune2010"
ASSET_LOGO = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless"

# --- 4. GESTION DE SESSION ET DONNEES ---
if "role" not in st.session_state:
    st.session_state.role = None

conn = st.connection("gsheets", type=GSheetsConnection)

def load_table(name):
    st.cache_data.clear()
    try:
        return conn.read(worksheet=name, ttl=0).dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

def commit_log(agent, category, info):
    try:
        logs = load_table("Logs")
        entry = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "Opérateur": agent, "Catégorie": category, "Description": info}])
        conn.update(worksheet="Logs", data=pd.concat([logs, entry], ignore_index=True))
    except: pass

# ==============================================================================
# 🚪 SECTION 5 : PORTAIL D'ACCÈS
# ==============================================================================
if st.session_state.role is None:
    st.title("🏛️ État de Californie - Portail Central")
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("### 👤 Citoyen")
            if st.button("Session Civile", use_container_width=True):
                st.session_state.role = "Civil"; st.rerun()
    with c2:
        with st.container(border=True):
            st.markdown("### 🛠️ Pro (RCT/Averis)")
            kp = st.text_input("Code Entreprise", type="password")
            if st.button("Accès Pro", use_container_width=True):
                if kp == AUTH_PRO_KEY: st.session_state.role = "RCT"; st.rerun()
                else: st.error("Code erroné.")
    with c3:
        with st.container(border=True):
            st.markdown("### 👮 Administration")
            ks = st.text_input("Code Staff", type="password")
            if st.button("Accès Staff", use_container_width=True):
                if ks == AUTH_ADMIN_KEY: st.session_state.role = "Staff"; st.rerun()
                else: st.error("Code erroné.")
    st.stop()

with st.sidebar:
    st.image(ASSET_LOGO, use_container_width=True)
    st.write(f"🛂 **Role :** {st.session_state.role}")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()
    st.divider()
    st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

# --- ONGLETS ---
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immat", "💰 Banque", "🪪 Permis", "➕ Profils", "⚖️ Justice", "📊 Stats", "📜 Logs"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation Pro", "📜 Historique"])
else:
    tabs = st.tabs(["💰 Mon Compte", "🪪 Mon Permis", "🚗 Mes Véhicules"])

# ==============================================================================
# 💰 MODULE : BANQUE & IDENTITE (Recherche Hybride + Date)
# ==============================================================================
current_tab_bk = tabs[1] if st.session_state.role == "Staff" else tabs[0]
if st.session_state.role == "RCT": current_tab_bk = tabs[1]

with current_tab_bk:
    df_bk = load_table("Banque")
    search_q = st.text_input("🔍 Votre Nom Roblox ou Discord").lower()
    
    if search_q:
        res_bk = df_bk[(df_bk["Nom Roblox"].str.lower().str.contains(search_q)) | 
                       (df_bk["Nom Discord"].str.lower().str.contains(search_q))]
        if not res_bk.empty:
            for i, row in res_bk.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="id-card">
                        <h3>👤 {row['Nom Roblox']}</h3>
                        <p><b>🎮 Discord :</b> {row['Nom Discord']}<br>
                        <b>📅 Date d'arrivée :</b> {row["Date d'arrivée"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.metric("Solde", f"{float(row['Solde']):,.0f} $")
                    if st.session_state.role == "Staff":
                        with st.form(f"f_bk_{i}"):
                            amt = st.number_input("Montant", step=100.0)
                            if st.form_submit_button("Modifier Solde"):
                                df_bk.at[i, 'Solde'] = float(row['Solde']) + amt
                                conn.update(worksheet="Banque", data=df_bk); st.rerun()
        else: st.warning("Introuvable.")

# ==============================================================================
# 🪪 MODULE : PERMIS (Visuel Couleurs)
# ==============================================================================
target_tab_p = tabs[2] if st.session_state.role == "Staff" else tabs[1]
if st.session_state.role != "RCT":
    with target_tab_p:
        df_p = load_table("Points Permis")
        search_p = st.text_input("🔍 Vérif Permis (Roblox/Discord)", key="p_s").lower()
        if search_p:
            df_ref = load_table("Banque")
            found = df_ref[(df_ref["Nom Roblox"].str.lower().str.contains(search_p)) | (df_ref["Nom Discord"].str.lower().str.contains(search_p))]
            if not found.empty:
                names = found["Nom Roblox"].tolist()
                res_p = df_p[df_p["Nom Roblox"].isin(names)]
                for ip, lp in res_p.iterrows():
                    pts = int(lp['PTS'])
                    color = "#2ecc71" if pts >= 15 else "#f1c40f" if pts >= 6 else "#e74c3c"
                    st.markdown(f"""
                    <div class="license-box" style="border: 2px solid {color};">
                        <h1 style="color:{color};">{pts} / 25 PTS</h1>
                        <h4>{lp['Nom Roblox']}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.session_state.role == "Staff":
                        new_pts = st.slider("Ajuster", 0, 25, pts, key=f"s_{ip}")
                        if st.button("Sauver", key=f"b_{ip}"):
                            df_p.at[ip, 'PTS'] = new_pts
                            conn.update(worksheet="Points Permis", data=df_p); st.rerun()

# ==============================================================================
# 🚗 MODULE : IMMATRICULATIONS (Correction Apostrophe)
# ==============================================================================
target_tab_v = tabs[0] if st.session_state.role != "Civil" else tabs[2]
with target_tab_v:
    df_v = load_table("Copie de Immatriculations")
    df_u = load_table("Banque")
    
    if st.session_state.role != "Civil":
        with st.expander("➕ Nouveau Véhicule"):
            with st.form("nv_v"):
                c1, c2 = st.columns(2)
                u = c1.selectbox("Citoyen", ["---"] + sorted(df_u["Nom Roblox"].unique().tolist()))
                m = c1.selectbox("Marque", sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"]))
                p = c2.text_input("Plaque")
                a = c1.selectbox("Assurance", ["Non assuré", "RCT", "Averis"])
                pw = c2.text_input("Code Secret", type="password")
                
                f_v, f_r, f_a, f_j = 175, 0, 0, 0
                if u != "---":
                    u_row = df_u[df_u["Nom Roblox"] == u]
                    if a == "Averis": f_a = 130
                    elif a == "RCT": f_r = 150 if df_v[(df_v["Nom d'utilisateur ROBLOX"] == u) & (df_v["Assurance"] == "RCT")].shape[0] < 2 else 0
                    try:
                        if datetime.now() - datetime.strptime(str(u_row.iloc[0]["Date d'arrivée"]), "%d/%m/%Y") < timedelta(days=30): f_j = 50
                    except: pass

                total = f_v + f_r + f_a + f_j
                st.write(f"### Total : {total} $")
                if st.form_submit_button("💳 Payer"):
                    curr = float(u_row.iloc[0]["Solde"])
                    if curr >= total:
                        df_u.at[u_row.index[0], "Solde"] = curr - total
                        if f_r > 0: 
                            tr = df_u[df_u["Nom Roblox"] == TARGET_RCT]
                            df_u.at[tr.index[0], "Solde"] = float(tr.iloc[0]["Solde"]) + f_r
                        if f_a > 0:
                            ta = df_u[df_u["Nom Roblox"] == TARGET_AVERIS]
                            df_u.at[ta.index[0], "Solde"] = float(ta.iloc[0]["Solde"]) + f_a
                        
                        nv = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "L'état de la plaque": "California", "Numéro de la plaque": p, "Assurance": a, "CODE": str(pw)}])
                        conn.update(worksheet="Banque", data=df_u)
                        conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_v, nv]))
                        st.success("Payé !"); st.rerun()

    q_v = st.text_input("🔍 Recherche Véhicule").lower()
    if q_v:
        res_v = df_v[df_v.apply(lambda r: q_v in str(r).lower(), axis=1)]
        for iv, rv in res_v.iterrows():
            with st.container(border=True):
                # FIX APOSTROPHE ICI
                nom_col = "Nom d'utilisateur ROBLOX"
                proprio = rv[nom_col]
                st.write(f"🚗 **{rv['Marque du véhicule']}** | `{rv['Numéro de la plaque']}`")
                st.caption(f"Propriétaire : {proprio} | {rv['Assurance']}")

# ==============================================================================
# ➕ MODULE STAFF : CREATION & JUSTICE
# ==============================================================================
if st.session_state.role == "Staff":
    with tabs[3]: # Profils
        with st.form("cp"):
            nr, nd, pa = st.text_input("Roblox"), st.text_input("Discord"), st.text_input("Ton Pseudo")
            if st.form_submit_button("🚀 Créer Profil (Date Auto)"):
                db_b, db_p = load_table("Banque"), load_table("Points Permis")
                today = datetime.now().strftime("%d/%m/%Y")
                lb = pd.DataFrame([{"Solde": 15000, "Nom Discord": nd, "Nom Roblox": nr, "Pseudo Admin": pa, "Date d'arrivée": today}])
                lp = pd.DataFrame([{"Nom Roblox": nr, "PTS": 25}])
                conn.update(worksheet="Banque", data=pd.concat([db_b, lb]))
                conn.update(worksheet="Points Permis", data=pd.concat([db_p, lp]))
                st.success("Dossier créé !"); st.rerun()
    with tabs[4]: # Justice
        with st.form("jus"):
            target = st.selectbox("Coupable", sorted(df_u["Nom Roblox"].tolist()))
            fine = st.number_input("Amende", min_value=0)
            if st.form_submit_button("⚖️ Sanctionner"):
                db_j = load_table("Banque")
                idx = db_j[db_j["Nom Roblox"] == target].index[0]
                db_j.at[idx, "Solde"] = float(db_j.at[idx, "Solde"]) - fine
                conn.update(worksheet="Banque", data=db_j); st.rerun()
    with tabs[6]: # Logs
        st.dataframe(load_table("Logs").iloc[::-1])

st.markdown("---")
st.markdown("<center><small>RCRP v11.1 | © 2026</small></center>", unsafe_allow_html=True)
