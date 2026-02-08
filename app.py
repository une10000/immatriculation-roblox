import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
if "time" not in globals():
    import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Système Intégral", layout="wide")

# --- STYLE CSS (LOGO & SIDEBAR CUTE) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    [data-testid="stSidebar"] img { border-radius: 15px; margin-bottom: 10px; border: 2px solid #2e3136; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .ticket { background: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin: 10px 0; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION & CONNEXION ---
if "role" not in st.session_state:
    st.session_state.role = None

conn = st.connection("gsheets", type=GSheetsConnection)
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

def get_data(sheet_name):
    st.cache_data.clear()
    try:
        return conn.read(worksheet=sheet_name, ttl=0).dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

# ==========================================
# 🚪 PAGE DE CONNEXION
# ==========================================
if st.session_state.role is None:
    st.title("🏛️ Portail des Services RCRP")
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("### 👤 Citoyen")
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"; st.rerun()
    with col2:
        with st.container(border=True):
            st.markdown("### 🛠️ Pro (RCT/AVE)")
            kp = st.text_input("Code Pro", type="password")
            if st.button("Connexion", key="pro_btn"):
                if kp == CODE_PRO: st.session_state.role = "RCT"; st.rerun()
    with col3:
        with st.container(border=True):
            st.markdown("### 👮 Staff")
            ks = st.text_input("Code Staff", type="password")
            if st.button("Connexion", key="staff_btn"):
                if ks == CODE_ADMIN: st.session_state.role = "Staff"; st.rerun()
    st.stop()

# ==========================================
# 🖥️ INTERFACE CONNECTÉE
# ==========================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown(f"🎭 **Session :** {st.session_state.role}")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()
    st.divider()
    st.markdown(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown(f"⏰ **Heure :** {datetime.now().strftime('%H:%M')}")

# Chargement des bases
df_im = get_data("Copie de Immatriculations")
df_banque = get_data("Banque")
df_points = get_data("Points Permis")
liste_citoyens = df_banque["Nom Roblox"].tolist()

# Définition des Onglets
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers & Points", "💰 Banque", "📜 Logs"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation"])
else:
    tabs = st.tabs(["🚗 Mes Véhicules", "💰 Mon Compte"])

# ==========================================
# 🚗 MODULE IMMATRICULATION (LOGIQUE PRIX)
# ==========================================
with tabs[0]:
    st.subheader("📋 Registre des Véhicules")
    
    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("add_v"):
            u = st.selectbox("Propriétaire", ["---"] + liste_citoyens)
            m = st.selectbox("Marque", sorted(["Bremen", "Altstadt", "Delton", "Envy", "Turismo", "Eva", "Shatoku", "Lyon", "Mita"]))
            p = st.text_input("Plaque (ABC-123)")
            assu = st.selectbox("Assurance", ["Aucune", "RCT (1 = 150$)", "RCT (Trio = 300$)", "Averis (130$)"])
            pwd_car = st.text_input("🔑 Code Secret du véhicule (pour modifier/supprimer)", type="password")
            
            # --- CALCUL DES FRAIS ---
            frais_immat = 175
            frais_assu = 0
            taxe_jeune = 0
            
            if u != "---":
                # Check Jeune Conducteur
                u_data = df_banque[df_banque["Nom Roblox"] == u]
                if not u_data.empty:
                    try:
                        date_arr = datetime.strptime(u_data.iloc[0]["Date d'arrivée"], "%d/%m/%Y")
                        if datetime.now() - date_arr < timedelta(days=30):
                            taxe_jeune = 50
                    except: pass
                
                # Check Assurance
                if "RCT (1" in assu: frais_assu = 150
                elif "Trio" in assu: frais_assu = 300
                elif "Averis" in assu: frais_assu = 130
                
            total = frais_immat + frais_assu + taxe_jeune
            
            st.markdown(f"""<div class="ticket">
                <b>FACTURE ESTIMÉE :</b><br>
                Immatriculation : 175$<br>
                Assurance : {frais_assu}$<br>
                Taxe Jeune (-1 mois) : {taxe_jeune}$<br>
                ---<br>
                <b>TOTAL : {total}$</b>
            </div>""", unsafe_allow_html=True)

            if st.form_submit_button("✅ Valider l'enregistrement"):
                if u != "---" and p and pwd_car:
                    idx_u = df_banque[df_banque["Nom Roblox"] == u].index[0]
                    if float(df_banque.at[idx_u, "Solde"]) >= total:
                        # 1. Débit Client
                        df_banque.at[idx_u, "Solde"] = float(df_banque.at[idx_u, "Solde"]) - total
                        
                        # 2. Virement vers Entreprises
                        if "RCT" in assu:
                            idx_target = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index
                            if not idx_target.empty:
                                df_banque.at[idx_target[0], "Solde"] = float(df_banque.at[idx_target[0], "Solde"]) + frais_assu
                        elif "Averis" in assu:
                            idx_target = df_banque[df_banque["Nom Roblox"] == TARGET_AVERIS].index
                            if not idx_target.empty:
                                df_banque.at[idx_target[0], "Solde"] = float(df_banque.at[idx_target[0], "Solde"]) + frais_assu
                        
                        # 3. Sauvegarde Véhicule
                        new_v = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "Numéro de la plaque": p, "Assurance": assu, "CODE": str(pwd_car)}])
                        conn.update(worksheet="Banque", data=df_banque)
                        conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_v], ignore_index=True))
                        st.success("🎉 Véhicule immatriculé !"); time.sleep(1); st.rerun()
                    else: st.error("Solde insuffisant.")

    # --- RECHERCHE ET GESTION (MODIFIER / EFFACER) ---
    search = st.text_input("🔍 Rechercher une Plaque ou un Nom").lower()
    if search:
        res = df_im[(df_im["Numéro de la plaque"].str.lower().contains(search)) | (df_im["Nom d'utilisateur ROBLOX"].str.lower().contains(search))]
        for i, r in res.iterrows():
            with st.container(border=True):
                st.write(f"🚗 **{r['Numéro de la plaque']}** - {r['Nom d\'utilisateur ROBLOX']} ({r['Marque du véhicule']})")
                with st.expander("⚙️ Modifier ou Supprimer"):
                    test_pwd = st.text_input("Code Secret du véhicule", type="password", key=f"pwd_{i}")
                    if test_pwd == str(r['CODE']) or st.session_state.role == "Staff":
                        new_p = st.text_input("Nouvelle Plaque", value=r['Numéro de la plaque'], key=f"np_{i}")
                        c1, c2 = st.columns(2)
                        if c1.button("💾 Sauvegarder", key=f"save_{i}"):
                            df_im.at[i, "Numéro de la plaque"] = new_p
                            conn.update(worksheet="Copie de Immatriculations", data=df_im)
                            st.success("Modifié !"); st.rerun()
                        if c2.button("🗑️ Supprimer", key=f"del_{i}"):
                            df_im = df_im.drop(i)
                            conn.update(worksheet="Copie de Immatriculations", data=df_im)
                            st.error("Supprimé !"); st.rerun()
                    elif test_pwd != "": st.warning("Code incorrect")

# ==========================================
# 🪪 MODULE DOSSIERS (CREATION PROFIL DANS POINTS)
# ==========================================
if st.session_state.role == "Staff":
    with tabs[1]:
        st.subheader("🪪 Gestion des Citoyens")
        
        with st.expander("👤 Créer un nouveau Profil Citoyen"):
            with st.form("new_profile"):
                new_rob = st.text_input("Nom Roblox")
                new_dis = st.text_input("Nom Discord")
                new_solde = st.number_input("Solde de base", value=15000)
                if st.form_submit_button("🚀 Créer le dossier"):
                    if new_rob and new_dis:
                        today = datetime.now().strftime("%d/%m/%Y")
                        # Ajout Banque
                        nb = pd.DataFrame([{"Solde": new_solde, "Nom Discord": new_dis, "Nom Roblox": new_rob, "Date d'arrivée": today}])
                        # Ajout Points (Dossier Permis)
                        np = pd.DataFrame([{"Nom Roblox": new_rob, "PTS": 25}])
                        conn.update(worksheet="Banque", data=pd.concat([df_banque, nb], ignore_index=True))
                        conn.update(worksheet="Points Permis", data=pd.concat([df_points, np], ignore_index=True))
                        st.success(f"Profil de {new_rob} créé le {today} !"); time.sleep(1); st.rerun()

        # Gestion des points existants
        search_p = st.text_input("🔍 Rechercher un dossier permis").lower()
        if search_p:
            res_p = df_points[df_points["Nom Roblox"].str.lower().contains(search_p)]
            for i, r in res_p.iterrows():
                with st.container(border=True):
                    st.write(f"**Citoyen :** {r['Nom Roblox']}")
                    new_pts = st.slider("Points", 0, 25, int(r['PTS']), key=f"sl_{i}")
                    if st.button("Mettre à jour", key=f"up_{i}"):
                        df_points.at[i, "PTS"] = new_pts
                        conn.update(worksheet="Points Permis", data=df_points)
                        st.success("Points mis à jour !"); st.rerun()

# ==========================================
# 💰 MODULE BANQUE
# ==========================================
with tabs[2 if st.session_state.role == "Staff" else 1]:
    st.subheader("🏦 Banque Centrale")
    q_b = st.text_input("🔍 Nom Roblox ou Discord").lower()
    if q_b:
        res_b = df_banque[(df_banque["Nom Roblox"].str.lower().contains(q_b)) | (df_banque["Nom Discord"].str.lower().contains(q_b))]
        for i, r in res_b.iterrows():
            with st.container(border=True):
                st.metric(f"Compte de {r['Nom Roblox']}", f"{float(r['Solde']):,.0f} $")
                if st.session_state.role == "Staff":
                    amt = st.number_input("Modifier montant", key=f"amt_{i}")
                    c1, c2 = st.columns(2)
                    if c1.button("📈 Créditer", key=f"plus_{i}"):
                        df_banque.at[i, "Solde"] = float(r["Solde"]) + amt
                        conn.update(worksheet="Banque", data=df_banque); st.rerun()
                    if c2.button("📉 Débiter", key=f"minus_{i}"):
                        df_banque.at[i, "Solde"] = float(r["Solde"]) - amt
                        conn.update(worksheet="Banque", data=df_banque); st.rerun()

st.markdown("---")
st.markdown("<center><small>RCRP Système v11.5 | 2026</small></center>", unsafe_allow_html=True)
