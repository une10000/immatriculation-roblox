# ==============================================================================
# 🏛️ REPUBLIQUE DE CALIFORNIE RP - SYSTEME DE GESTION INTEGRAL (v9.99)
# ==============================================================================
# Plateforme de gestion centralisée : Économie, Transports, Justice et Logistique.
# Version : 9.99 | Date : 08/02/2026 | Développeur : RCRP Tech Division
# 
# PROTOCOLES DE TRANSFERT ET RÈGLES MÉTIER :
# 1. Flux Financiers :
#    - Paiements Assurance RCT : Transfert direct vers l'IBAN 'une10000'.
#    - Paiements Assurance Averis : Transfert direct vers l'IBAN 'Moune2010'.
# 2. Gestion des Profils :
#    - L'horodatage de création est injecté automatiquement.
#    - Le pseudo du Staff créateur est sauvegardé dans le registre.
# 3. Sécurité :
#    - Accès restreints par codes alphanumériques.
# ==============================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION DE L'INTERFACE GOUVERNEMENTALE ---
st.set_page_config(
    page_title="RCRP - Système Intégré de l'État",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ENGINE CSS : DESIGN HAUTE DÉFINITION ---
st.markdown("""
    <style>
    .main { background-color: #0b0d10; color: #ecf0f1; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(30, 34, 40, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 40px !important;
        height: 600px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0px 20px 50px rgba(0,0,0,0.7);
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

    .stMetric {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 22px !important;
    }

    [data-testid="stSidebar"] img {
        border-radius: 25px;
        border: 3px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 25px;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px 10px 0 0;
        padding: 15px 30px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #c0392b !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONSTANTES ---
AUTH_ADMIN_KEY = "RCRPFR-25-26" 
AUTH_PRO_KEY = "RCT-26-RCRPFR" 
TARGET_RCT = "une10000" 
TARGET_AVERIS = "Moune2010"
ASSET_LOGO = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless"

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
# 🚪 SECTION 1 : PORTAIL D'ACCÈS
# ==============================================================================
if st.session_state.role is None:
    st.title("🏛️ État de Californie - Portail Central")
    col_c, col_p, col_s = st.columns(3)
    with col_c:
        with st.container(border=True):
            st.markdown("### 👤 Citoyen")
            if st.button("Session Civile", use_container_width=True):
                st.session_state.role = "Civil"; st.rerun()
    with col_p:
        with st.container(border=True):
            st.markdown("### 🛠️ Professionnel")
            key_p = st.text_input("Code Entreprise", type="password")
            if st.button("Accès Pro", use_container_width=True):
                if key_p == AUTH_PRO_KEY: st.session_state.role = "RCT"; st.rerun()
    with col_s:
        with st.container(border=True):
            st.markdown("### 👮 Administration")
            key_s = st.text_input("Code Staff", type="password")
            if st.button("Accès Staff", use_container_width=True):
                if key_s == AUTH_ADMIN_KEY: st.session_state.role = "Staff"; st.rerun()
    st.stop()

with st.sidebar:
    st.image(ASSET_LOGO, use_container_width=True)
    st.write(f"🛂 **Session :** {st.session_state.role}")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()

# --- ONGLETS ---
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immat", "💰 Banque", "🪪 Permis", "➕ Profils", "⚖️ Justice", "📊 Stats", "📜 Logs"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immat", "💰 Facturation", "📜 Logs"])
else:
    tabs = st.tabs(["🚗 Mes Véhicules", "💰 Mon Solde", "🪪 Mon Permis"])

# ==============================================================================
# 🚗 MODULE : IMMATRICULATIONS
# ==============================================================================
with tabs[0]:
    df_immat = load_table("Copie de Immatriculations")
    df_bank = load_table("Banque")
    owners = sorted(df_bank["Nom Roblox"].unique().tolist()) if not df_bank.empty else []

    if st.session_state.role != "Civil":
        with st.expander("➕ Enregistrer un Véhicule"):
            with st.form("add_v"):
                c1, c2 = st.columns(2)
                u = c1.selectbox("Citoyen", ["---"] + owners)
                m = c1.selectbox("Marque", sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"]))
                p = c2.text_input("Plaque")
                a = c1.selectbox("Assurance", ["Non assuré", "RCT", "Averis"])
                pw = c2.text_input("Code Secret", type="password")
                
                # --- CALCUL TAXES ---
                f_v, f_r, f_a, f_j = 175, 0, 0, 0
                if u != "---":
                    udat = df_bank[df_bank["Nom Roblox"] == u]
                    if a == "Averis":
                        f_a = 130
                        try:
                            da = datetime.strptime(str(udat.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                            if datetime.now() - da < timedelta(days=30): f_j = 50
                        except: pass
                    elif a == "RCT":
                        if df_immat[(df_immat["Nom d'utilisateur ROBLOX"] == u) & (df_immat["Assurance"] == "RCT")].shape[0] < 2: f_r = 150
                
                total = f_v + f_r + f_a + f_j
                st.write(f"**Total à payer : {total}$**")
                
                if st.form_submit_button("💳 Valider"):
                    ur = df_bank[df_bank["Nom Roblox"] == u]
                    if float(ur.iloc[0]["Solde"]) >= total:
                        df_bank.at[ur.index[0], "Solde"] = float(ur.iloc[0]["Solde"]) - total
                        if f_r > 0:
                            tr = df_bank[df_bank["Nom Roblox"] == TARGET_RCT]
                            if not tr.empty: df_bank.at[tr.index[0], "Solde"] = float(tr.iloc[0]["Solde"]) + f_r
                        if f_a > 0:
                            ta = df_bank[df_bank["Nom Roblox"] == TARGET_AVERIS]
                            if not ta.empty: df_bank.at[ta.index[0], "Solde"] = float(ta.iloc[0]["Solde"]) + f_a
                        
                        nv = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "L'état de la plaque": "California", "Numéro de la plaque": p, "Assurance": a, "CODE": str(pw)}])
                        conn.update(worksheet="Banque", data=df_bank)
                        conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_immat, nv], ignore_index=True))
                        st.success("Véhicule enregistré !"); st.rerun()

    # RECHERCHE CIVILE (ROBLOX OU DISCORD)
    q = st.text_input("🔍 Rechercher un véhicule (Plaque, Nom Roblox ou Discord)").lower()
    if q:
        res = df_immat[df_immat.apply(lambda r: q in str(r).lower(), axis=1)]
        # Jointure avec banque pour trouver par discord
        res_discord = df_bank[df_bank["Nom Discord"].str.lower().str.contains(q)]
        if not res_discord.empty:
            users = res_discord["Nom Roblox"].tolist()
            res = pd.concat([res, df_immat[df_immat["Nom d'utilisateur ROBLOX"].isin(users)]]).drop_duplicates()
        
        for i, r in res.iterrows():
            with st.container(border=True):
                st.write(f"🚗 **Plaque : {r['Numéro de la plaque']}** | 👤 {r['Nom d\'utilisateur ROBLOX']}")

# ==============================================================================
# 💰 MODULE : BANQUE (RECHERCHE DOUBLE)
# ==============================================================================
with tabs[1]:
    df_bk = load_table("Banque")
    search_bank = st.text_input("🔍 Entrez votre Nom Roblox OU votre Discord pour voir votre solde").lower()
    if search_bank:
        # Recherche flexible Roblox ou Discord
        res_b = df_bk[(df_bk["Nom Roblox"].str.lower().str.contains(search_bank)) | 
                      (df_bk["Nom Discord"].str.lower().str.contains(search_bank))]
        if not res_b.empty:
            for ib, lb in res_b.iterrows():
                with st.container(border=True):
                    st.metric(f"💵 Solde de {lb['Nom Roblox']}", f"{float(lb['Solde']):,.0f} $")
                    if st.session_state.role == "Staff":
                        with st.form(f"f_{ib}"):
                            amt = st.number_input("Montant", min_value=0.0)
                            if st.form_submit_button("Créditer"):
                                df_bk.at[ib, 'Solde'] = float(lb['Solde']) + amt
                                conn.update(worksheet="Banque", data=df_bk); st.rerun()

# ==============================================================================
# 🪪 MODULE : PERMIS (ENFIN COMPLET POUR LES CIVILS)
# ==============================================================================
with tabs[2]:
    st.write("### 🪪 Registre National des Permis de Conduire")
    df_p = load_table("Points Permis")
    search_p = st.text_input("🔍 Entrez votre Nom Roblox ou Discord pour vérifier vos points").lower()
    
    if search_p:
        # Logique de recherche croisée (Roblox/Discord via table banque)
        db_ref = load_table("Banque")
        users_found = db_ref[(db_ref["Nom Roblox"].str.lower().str.contains(search_p)) | 
                             (db_ref["Nom Discord"].str.lower().str.contains(search_p))]["Nom Roblox"].tolist()
        
        res_p = df_p[df_p["Nom Roblox"].isin(users_found)]
        
        if not res_p.empty:
            for ip, lp in res_p.iterrows():
                pts = int(lp['PTS'])
                color = "green" if pts > 15 else "orange" if pts > 5 else "red"
                st.markdown(f"""
                <div style='padding:30px; border-radius:15px; border: 2px solid {color}; background:rgba(0,0,0,0.2)'>
                    <h2 style='color:{color}'>{pts} / 25 Points</h2>
                    <p><b>Titulaire :</b> {lp['Nom Roblox']}</p>
                    <p><b>Statut :</b> {"✅ Valide" if pts > 0 else "❌ Suspendu"}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.session_state.role == "Staff":
                    new_pts = st.slider("Ajuster les points", 0, 25, pts)
                    if st.button("Sauvegarder les points", key=f"s_{ip}"):
                        df_p.at[ip, 'PTS'] = new_pts
                        conn.update(worksheet="Points Permis", data=df_p); st.rerun()
        else:
            st.warning("Aucun dossier de permis trouvé pour cette recherche.")
    else:
        st.info("Veuillez saisir votre nom pour accéder à vos informations de conduite.")

# ==============================================================================
# ➕ MODULE : STAFF (PROFILS)
# ==============================================================================
if st.session_state.role == "Staff":
    with tabs[3]: # Création Profils
        with st.form("new_cit"):
            nr = st.text_input("Nom Roblox")
            nd = st.text_input("Discord")
            pa = st.text_input("Admin créateur")
            if st.form_submit_button("🚀 Créer Profil (Date Auto)"):
                db_b = load_table("Banque")
                db_p = load_table("Points Permis")
                # AJOUT DATE AUTO
                new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": nd, "Nom Roblox": nr, "Pseudo Admin": pa, "Date d'arrivée": datetime.now().strftime("%d/%m/%Y")}])
                new_p = pd.DataFrame([{"Nom Roblox": nr, "PTS": 25}])
                conn.update(worksheet="Banque", data=pd.concat([db_b, new_b], ignore_index=True))
                conn.update(worksheet="Points Permis", data=pd.concat([db_p, new_p], ignore_index=True))
                st.success("Profil créé !"); st.rerun()

    with tabs[4]: # Justice
        st.write("### ⚖️ Sanctions")
        with st.form("jus"):
            target = st.selectbox("Coupable", owners)
            fine = st.number_input("Amende", min_value=0)
            if st.form_submit_button("Appliquer"):
                db_j = load_table("Banque")
                idx = db_j[db_j["Nom Roblox"] == target].index[0]
                db_j.at[idx, "Solde"] = float(db_j.at[idx, "Solde"]) - fine
                conn.update(worksheet="Banque", data=db_j); st.success("Sanctionné !"); st.rerun()

    with tabs[5]: # Stats
        st.metric("Masse Monétaire", f"{df_bank['Solde'].astype(float).sum():,.0f} $")
    
    with tabs[6]: # Logs
        st.dataframe(load_table("Logs").iloc[::-1], use_container_width=True)

st.markdown("---")
st.markdown("<center><small>RCRP Enterprise v9.99 | © 2026</small></center>", unsafe_allow_html=True)
