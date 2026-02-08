import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURATION PAGE (FIX TABS COUPÉS) ---
st.set_page_config(page_title="RCRP - Système Intégral", layout="wide")

# --- 2. STYLE CSS COMPLET ---
st.markdown("""
    <style>
    /* Décale tout le contenu vers le bas pour ne pas couper les tabs */
    .stApp { margin-top: 5rem !important; }
    
    /* Style pour le logo */
    [data-testid="stSidebarNav"] { padding-top: 20px !important; }
    .sidebar-logo { border-radius: 15px; margin-bottom: 20px; width: 100%; border: 1px solid #444; }

    /* Cartes de véhicules avec assurance visible */
    .car-card {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #ff4b4b;
        margin-bottom: 15px;
    }
    .assu-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }

    /* Reçu Mode Nuit */
    .ticket-nuit { 
        background-color: #121212 !important; 
        color: #ffffff !important; 
        padding: 20px; 
        border: 2px solid #ff4b4b; 
        border-radius: 10px;
        font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INITIALISATION ---
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
        df = conn.read(worksheet=sheet_name, ttl=0)
        return df.dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

# ==========================================
# 🚪 PORTAIL DE CONNEXION
# ==========================================
if st.session_state.role is None:
    st.title("🏛️ Portail des Services RCRP")
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("👤 Citoyen")
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"; st.rerun()
    with col2:
        with st.container(border=True):
            st.subheader("🛠️ Pro")
            kp = st.text_input("Code", type="password", key="p_in")
            if st.button("Connexion Pro", use_container_width=True):
                if kp == CODE_PRO: st.session_state.role = "RCT"; st.rerun()
                else: st.error("Code erroné")
    with col3:
        with st.container(border=True):
            st.subheader("👮 Staff")
            ks = st.text_input("Code", type="password", key="s_in")
            if st.button("Connexion Staff", use_container_width=True):
                if ks == CODE_ADMIN: st.session_state.role = "Staff"; st.rerun()
                else: st.error("Code erroné")
    st.stop()

# ==========================================
# 🖥️ INTERFACE CONNECTÉE
# ==========================================
with st.sidebar:
    try:
        st.image(LOGO_URL)
    except:
        st.markdown("### [ LOGO RCRP ]")
    
    st.markdown(f"🎭 **Session :** `{st.session_state.role}`")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()
    st.divider()
    st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')} | ⏰ {datetime.now().strftime('%H:%M')}")

# Chargement bases
df_banque = get_data("Banque")
df_im = get_data("Copie de Immatriculations")
df_pts = get_data("Points Permis")

# Navigation
tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers", "💰 Banque", "📜 Logs"]) if st.session_state.role == "Staff" else \
       st.tabs(["🚗 Immatriculations", "💰 Facturation"]) if st.session_state.role == "RCT" else \
       st.tabs(["🚗 Mes Véhicules", "💰 Mon Compte"])

# --- ONGLET 1 : IMMATRICULATIONS ---
with tabs[0]:
    st.header("🚗 Registre des Véhicules")
    
    if st.session_state.role != "Civil":
        with st.expander("➕ Nouvelle Immatriculation"):
            with st.form("immat_form_v12"):
                u = st.selectbox("Propriétaire", ["---"] + df_banque["Nom Roblox"].tolist())
                m = st.text_input("Marque du véhicule")
                p = st.text_input("Plaque")
                as_choice = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
                pwd_car = st.text_input("🔑 Code Secret", type="password")
                
                # Calculs
                prix_ville = 175
                prix_assu = 130 if "AVERIS" in as_choice else 150 if "RCT" in as_choice else 0
                
                # Promo Trio RCT (le 3ème est gratuit)
                nb_rct = len(df_im[(df_im["Nom d'utilisateur ROBLOX"] == u) & (df_im["Assurance"].str.contains("RCT"))])
                if "RCT" in as_choice and nb_rct >= 2:
                    prix_assu = 0
                    st.info("🎁 Prime Trio détectée : Assurance gratuite !")
                
                # Taxe Jeune
                taxe_j = 0
                if u != "---":
                    u_row = df_banque[df_banque["Nom Roblox"] == u]
                    if not u_row.empty and u_row.iloc[0]["Date d'arrivée"]:
                        try:
                            date_a = datetime.strptime(str(u_row.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                            if datetime.now() - date_a < timedelta(days=30): taxe_j = 50
                        except: pass
                
                total = prix_ville + prix_assu + taxe_j
                
                st.markdown(f"""<div class="ticket-nuit">
                    <b>📄 FACTURE D'IMMATRICULATION</b><br>
                    ----------------------------<br>
                    Immat Ville : 175$<br>
                    Assurance : {prix_assu}$<br>
                    Taxe Jeune : {taxe_j}$<br>
                    ----------------------------<br>
                    <b>TOTAL : {total}$</b>
                </div>""", unsafe_allow_html=True)

                if st.form_submit_button("✅ Enregistrer"):
                    if u != "---" and p and pwd_car:
                        idx_u = df_banque[df_banque["Nom Roblox"] == u].index[0]
                        solde_actuel = float(df_banque.at[idx_u, "Solde"])
                        
                        if solde_actuel >= total:
                            # Prélèvement
                            df_banque.at[idx_u, "Solde"] = solde_actuel - total
                            # Virement
                            if "AVERIS" in as_choice:
                                idx_m = df_banque[df_banque["Nom Roblox"] == TARGET_AVERIS].index
                                if not idx_m.empty: df_banque.at[idx_m[0], "Solde"] = float(df_banque.at[idx_m[0], "Solde"]) + prix_assu
                            elif "RCT" in as_choice and prix_assu > 0:
                                idx_u1 = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index
                                if not idx_u1.empty: df_banque.at[idx_u1[0], "Solde"] = float(df_banque.at[idx_u1[0], "Solde"]) + prix_assu
                            
                            # Update Immat
                            new_v = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "Numéro de la plaque": p, "Assurance": as_choice, "CODE": str(pwd_car)}])
                            conn.update(worksheet="Banque", data=df_banque)
                            conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_v], ignore_index=True))
                            st.success("Terminé !"); time.sleep(1); st.rerun()
                        else: st.error("Solde insuffisant.")

    # --- LISTE DES VÉHICULES (ASSURANCE VISIBLE) ---
    st.divider()
    search = st.text_input("🔍 Rechercher Nom ou Plaque").lower()
    if not df_im.empty:
        res = df_im[df_im.apply(lambda x: search in str(x).lower(), axis=1)]
        for i, r in res.iterrows():
            st.markdown(f"""
            <div class="car-card">
                <span class="assu-badge">{r['Assurance']}</span><br>
                <b>🚗 {r['Numéro de la plaque']}</b><br>
                👤 Propriétaire : {r["Nom d'utilisateur ROBLOX"]} ({r['Marque du véhicule']})
            </div>
            """, unsafe_allow_html=True)
            with st.expander("Modifier/Supprimer"):
                pwd_test = st.text_input("Code secret", type="password", key=f"p_{i}")
                if pwd_test == str(r['CODE']) or st.session_state.role == "Staff":
                    if st.button("🗑️ Supprimer", key=f"d_{i}"):
                        conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                        st.rerun()

# --- ONGLET 2 : DOSSIERS (CREATION PROFIL) ---
if st.session_state.role == "Staff":
    with tabs[1]:
        st.subheader("👤 Gestion des Dossiers")
        with st.form("create_p"):
            n_r = st.text_input("Pseudo Roblox")
            n_d = st.text_input("Pseudo Discord")
            if st.form_submit_button("🚀 Créer Profil"):
                d = datetime.now().strftime("%d/%m/%Y")
                nb = pd.DataFrame([{"Solde": 15000, "Nom Discord": n_d, "Nom Roblox": n_r, "Date d'arrivée": d}])
                np = pd.DataFrame([{"Nom Roblox": n_r, "PTS": 25}])
                conn.update(worksheet="Banque", data=pd.concat([df_banque, nb], ignore_index=True))
                conn.update(worksheet="Points Permis", data=pd.concat([df_pts, np], ignore_index=True))
                st.success("Profil créé !"); st.rerun()

st.markdown("---")
st.markdown("<center><small>RCRP Système v12.1 | 2026</small></center>", unsafe_allow_html=True)
