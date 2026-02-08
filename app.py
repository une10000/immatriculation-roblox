import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# ==============================================================================
# 🏛️ CONFIGURATION & DESIGN AVANCÉ
# ==============================================================================
st.set_page_config(
    page_title="RCRP - Système Intégré de l'État",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection CSS pour l'esthétique "Gouvernementale"
st.markdown("""
    <style>
    .main { background-color: #0b0d10; color: #ecf0f1; }
    [data-testid="stSidebar"] { background-color: #161b22; }
    
    /* Design des conteneurs de connexion */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(30, 34, 40, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 30px !important;
    }

    /* Ticket de transaction style papier */
    .transaction-ticket {
        background: #f8f9fa;
        color: #1e272e;
        border-left: 10px solid #27ae60;
        padding: 20px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        margin: 15px 0;
    }

    /* Badge de permis */
    .permis-badge {
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2em;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# ⚙️ MOTEUR DE DONNÉES & VARIABLES FIXES
# ==============================================================================
AUTH_ADMIN_KEY = "RCRPFR-25-26" 
AUTH_PRO_KEY = "RCT-26-RCRPFR" 
TARGET_RCT = "une10000" 
TARGET_AVERIS = "Moune2010"
ASSET_LOGO = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

if "role" not in st.session_state:
    st.session_state.role = None

conn = st.connection("gsheets", type=GSheetsConnection)

def load_table(name):
    st.cache_data.clear()
    try:
        return conn.read(worksheet=name, ttl=0).dropna(how='all').fillna("")
    except:
        st.error(f"Erreur de lecture : {name}")
        return pd.DataFrame()

def save_table(name, df):
    conn.update(worksheet=name, data=df)

def commit_log(agent, category, info):
    try:
        logs = load_table("Logs")
        new_log = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"), "Opérateur": agent, "Catégorie": category, "Description": info}])
        save_table("Logs", pd.concat([logs, new_log], ignore_index=True))
    except: pass

# ==============================================================================
# 🚪 PORTAIL D'AUTHENTIFICATION
# ==============================================================================
if st.session_state.role is None:
    st.title("🏛️ République de Californie - Système Central")
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.subheader("👤 Civil")
        if st.button("Accéder à mes dossiers", use_container_width=True):
            st.session_state.role = "Civil"; st.rerun()
            
    with c2:
        st.subheader("🛠️ Professionnel")
        kp = st.text_input("Clé Entreprise", type="password")
        if st.button("Connexion Pro", use_container_width=True):
            if kp == AUTH_PRO_KEY: st.session_state.role = "RCT"; st.rerun()
            else: st.error("Clé invalide.")

    with c3:
        st.subheader("👮 Gouvernement")
        ks = st.text_input("Code Agent", type="password")
        if st.button("Connexion État", use_container_width=True):
            if ks == AUTH_ADMIN_KEY: st.session_state.role = "Staff"; st.rerun()
            else: st.error("Accès refusé.")
    st.stop()

# ==============================================================================
# 🖥️ NAVIGATION & CHARGEMENT
# ==============================================================================
with st.sidebar:
    st.image(ASSET_LOGO, caption="RCRP Tech Division", use_container_width=True)
    st.success(f"Connecté : {st.session_state.role}")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()

# Chargement auto des DataFrames
df_banque = load_table("Banque")
df_immat = load_table("Copie de Immatriculations")
df_points = load_table("Points Permis")
list_citoyens = df_banque["Nom Roblox"].tolist()

if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immat", "💰 Banque", "🪪 Permis", "⚖️ Justice", "➕ Profils", "📊 Stats", "📜 Logs"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immat", "💰 Facturation Pro", "📜 Historique"])
else:
    tabs = st.tabs(["💰 Mon Compte", "🪪 Mon Permis", "🚗 Mes Véhicules"])

# ==============================================================================
# 💰 MODULE BANQUE (Héritage v11.0 + Recherche Hybride)
# ==============================================================================
t_bk = tabs[1] if st.session_state.role == "Staff" else tabs[0]
with t_bk:
    st.header("🏦 Gestion Bancaire")
    search = st.text_input("🔍 Rechercher par Nom Roblox ou Discord").lower()
    
    if search:
        # Recherche sur deux colonnes
        res = df_banque[(df_banque["Nom Roblox"].str.lower().str.contains(search)) | 
                        (df_banque["Nom Discord"].str.lower().str.contains(search))]
        
        for i, r in res.iterrows():
            with st.container(border=True):
                colA, colB = st.columns([2,1])
                colA.markdown(f"### 👤 {r['Nom Roblox']}")
                colA.write(f"**Discord :** {r['Nom Discord']} | **Entrée :** {r.get('Date d\'arrivée', 'Inconnue')}")
                colB.metric("Solde", f"{float(r['Solde']):,.0f} $")
                
                if st.session_state.role == "Staff":
                    with st.expander("💳 Actions Financières"):
                        montant = st.number_input("Somme", key=f"m_{i}", min_value=0.0)
                        ca, cb = st.columns(2)
                        if ca.button("📈 Créditer", key=f"cr_{i}"):
                            df_banque.at[i, "Solde"] = float(r["Solde"]) + montant
                            save_table("Banque", df_banque); st.rerun()
                        if cb.button("📉 Débiter", key=f"db_{i}"):
                            df_banque.at[i, "Solde"] = float(r["Solde"]) - montant
                            save_table("Banque", df_banque); st.rerun()

# ==============================================================================
# 🚗 MODULE IMMATRICULATIONS (L'INTEGRAL)
# ==============================================================================
t_im = tabs[0] if st.session_state.role != "Civil" else tabs[2]
with t_im:
    st.header("🚗 Registre Automobile")
    
    # --- FORMULAIRE D'ENREGISTREMENT ---
    with st.expander("➕ Enregistrer un nouveau véhicule"):
        with st.form("new_car"):
            c1, c2 = st.columns(2)
            u_name = c1.selectbox("Propriétaire", ["---"] + list_citoyens)
            marque = c1.selectbox("Marque", ["Bremen", "Altstadt", "Delton", "Envy", "Turismo", "Eva", "Shatoku", "Koritsu", "Lyon", "Mita"])
            plaque = c2.text_input("Plaque (ex: ABC-123)")
            assurance = c1.selectbox("Assurance", ["Non assuré", "RCT", "Averis"])
            code_sec = c2.text_input("Code Secret Véhicule", type="password")
            
            # Calcul Logique des Frais
            f_adm, f_rct, f_ave, f_jeune = 175, 0, 0, 0
            if assurance == "RCT": f_rct = 150
            if assurance == "Averis": f_ave = 130
            
            # Calcul Taxe Jeune Conducteur
            if u_name != "---":
                u_info = df_banque[df_banque["Nom Roblox"] == u_name]
                if not u_info.empty:
                    try:
                        d_arr = datetime.strptime(u_info.iloc[0]["Date d'arrivée"], "%d/%m/%Y")
                        if datetime.now() - d_arr < timedelta(days=30): f_jeune = 50
                    except: pass

            total_final = f_adm + f_rct + f_ave + f_jeune
            
            st.markdown(f"""
            <div class="transaction-ticket">
                <b>FACTURE RCRP v11.2</b><br>
                -------------------------<br>
                Frais Admin : {f_adm}$<br>
                Assurance ({assurance}) : {f_rct + f_ave}$<br>
                Taxe Jeune Permis : {f_jeune}$<br>
                -------------------------<br>
                <b>TOTAL : {total_final}$</b>
            </div>
            """, unsafe_allow_html=True)
            
            if st.form_submit_button("💳 Payer et Immatriculer"):
                if u_name != "---" and plaque and code_sec:
                    idx_u = df_banque[df_banque["Nom Roblox"] == u_name].index[0]
                    if float(df_banque.at[idx_u, "Solde"]) >= total_final:
                        # 1. Débit
                        df_banque.at[idx_u, "Solde"] = float(df_banque.at[idx_u, "Solde"]) - total_final
                        # 2. Virement Pro (Averis -> Moune2010 / RCT -> une10000)
                        if f_rct > 0:
                            idx_r = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index
                            if not idx_r.empty: df_banque.at[idx_r[0], "Solde"] = float(df_banque.at[idx_r[0], "Solde"]) + f_rct
                        if f_ave > 0:
                            idx_a = df_banque[df_banque["Nom Roblox"] == TARGET_AVERIS].index
                            if not idx_a.empty: df_banque.at[idx_a[0], "Solde"] = float(df_banque.at[idx_a[0], "Solde"]) + f_ave
                        
                        # 3. Enregistrement
                        new_v = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y"), "Nom d'utilisateur ROBLOX": u_name, "Marque du véhicule": marque, "Numéro de la plaque": plaque, "Assurance": assurance, "CODE": code_sec}])
                        save_table("Banque", df_banque)
                        save_table("Copie de Immatriculations", pd.concat([df_immat, new_v], ignore_index=True))
                        st.success("Immatriculation validée !"); time.sleep(1); st.rerun()
                    else: st.error("Fonds insuffisants.")

    # Liste des véhicules
    v_search = st.text_input("🔍 Rechercher une plaque ou un propriétaire").lower()
    if v_search:
        res_v = df_immat[(df_immat["Numéro de la plaque"].str.lower().str.contains(v_search)) | 
                         (df_immat["Nom d'utilisateur ROBLOX"].str.lower().str.contains(v_search))]
        st.table(res_v[["Nom d'utilisateur ROBLOX", "Marque du véhicule", "Numéro de la plaque", "Assurance"]])

# ==============================================================================
# 🪪 MODULE PERMIS (Visuel Couleurs)
# ==============================================================================
t_p = tabs[2] if st.session_state.role == "Staff" else tabs[1]
with t_p:
    st.header("🪪 État des Permis de Conduire")
    p_search = st.text_input("🔍 Entrez un nom Roblox").lower()
    if p_search:
        res_p = df_points[df_points["Nom Roblox"].str.lower().str.contains(p_search)]
        for i, r in res_p.iterrows():
            pts = int(r["PTS"])
            bg = "#27ae60" if pts > 15 else "#e67e22" if pts > 5 else "#c0392b"
            st.markdown(f"<div class='permis-badge' style='background:{bg};'>{r['Nom Roblox']} : {pts} / 25 POINTS</div>", unsafe_allow_html=True)
            if st.session_state.role == "Staff":
                new_pts = st.slider("Ajuster les points", 0, 25, pts, key=f"pts_{i}")
                if st.button("Mettre à jour", key=f"up_pts_{i}"):
                    df_points.at[i, "PTS"] = new_pts
                    save_table("Points Permis", df_points); st.rerun()

# ==============================================================================
# ⚖️ MODULE JUSTICE (Tribunal)
# ==============================================================================
if st.session_state.role == "Staff":
    with tabs[3]:
        st.header("⚖️ Système de Justice")
        with st.form("tribunal"):
            guilty = st.selectbox("Citoyen jugé", list_citoyens)
            amende = st.number_input("Montant de l'amende", min_value=0)
            motif = st.text_area("Raison du jugement")
            if st.form_submit_button("🔨 Appliquer la sentence"):
                idx = df_banque[df_banque["Nom Roblox"] == guilty].index[0]
                df_banque.at[idx, "Solde"] = float(df_banque.at[idx, "Solde"]) - amende
                save_table("Banque", df_banque)
                commit_log("Justice", "AMENDE", f"{guilty} paye {amende}$ : {motif}")
                st.success("La loi a été appliquée."); st.rerun()

# ==============================================================================
# ➕ MODULE STAFF : CRÉATION PROFILS (Date Automatique)
# ==============================================================================
    with tabs[4]:
        st.header("➕ Nouveau Citoyen")
        with st.form("add_citoyen"):
            c1, c2 = st.columns(2)
            n_rob = c1.text_input("Nom Roblox")
            n_dis = c2.text_input("Nom Discord")
            staff_resp = c1.text_input("Agent Responsable")
            solde_dep = c2.number_input("Solde de départ", value=15000)
            
            if st.form_submit_button("🚀 Valider la création"):
                if n_rob and n_dis:
                    # DATE AUTO ICI
                    date_now = datetime.now().strftime("%d/%m/%Y")
                    # Ajout Banque
                    n_b = pd.DataFrame([{"Solde": solde_dep, "Nom Discord": n_dis, "Nom Roblox": n_rob, "Pseudo Admin": staff_resp, "Date d'arrivée": date_now}])
                    # Ajout Permis
                    n_p = pd.DataFrame([{"Nom Roblox": n_rob, "PTS": 25}])
                    
                    save_table("Banque", pd.concat([df_banque, n_b], ignore_index=True))
                    save_table("Points Permis", pd.concat([df_points, n_p], ignore_index=True))
                    
                    st.success(f"Dossier créé pour {n_rob} le {date_now} !")
                    commit_log("Staff", "CREATION", f"Nouveau citoyen : {n_rob}")
                    time.sleep(1); st.rerun()

    # --- STATS & LOGS ---
    with tabs[5]:
        st.header("📊 Données Nationales")
        col1, col2, col3 = st.columns(3)
        col1.metric("Économie Totale", f"{df_banque['Solde'].astype(float).sum():,.0f} $")
        col2.metric("Véhicules", len(df_immat))
        col3.metric("Population", len(df_banque))

    with tabs[6]:
        st.header("📜 Registre des Logs")
        st.dataframe(load_table("Logs").iloc[::-1], use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<center><small>RCRP Integrated System v11.2 | République de Californie | © 2026</small></center>", unsafe_allow_html=True)
