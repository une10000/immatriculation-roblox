import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Système Intégral", layout="wide")

# --- 2. STYLE CSS (FIX LOGO, TABS ET REÇU LISIBLE MODE NUIT) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    [data-testid="stSidebar"] img { border-radius: 10px; margin-bottom: 15px; }
    
    /* FIX REÇU MODE NUIT : Fond sombre, texte blanc, bordure rouge */
    .ticket-nuit { 
        background-color: #1a1a1a !important; 
        color: #ffffff !important; 
        padding: 20px; 
        border-radius: 10px; 
        border: 2px solid #ff4b4b; 
        margin: 10px 0; 
        font-family: 'Courier New', Courier, monospace;
        line-height: 1.5;
    }
    .ticket-nuit b { color: #ff4b4b !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INITIALISATION & CONNEXION ---
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
            st.subheader("🛠️ Entreprise")
            kp = st.text_input("Code Pro", type="password", key="log_pro")
            if st.button("Connexion Pro", use_container_width=True):
                if kp == CODE_PRO: st.session_state.role = "RCT"; st.rerun()
                else: st.error("Code incorrect")
    with col3:
        with st.container(border=True):
            st.subheader("👮 Staff")
            ks = st.text_input("Code Staff", type="password", key="log_staff")
            if st.button("Connexion Staff", use_container_width=True):
                if ks == CODE_ADMIN: st.session_state.role = "Staff"; st.rerun()
                else: st.error("Code incorrect")
    st.stop()

# ==========================================
# 🖥️ INTERFACE CONNECTÉE
# ==========================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown(f"🎭 **Session :** `{st.session_state.role}`")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()
    st.divider()
    st.markdown(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown(f"⏰ **Heure :** {datetime.now().strftime('%H:%M')}")

df_banque = get_data("Banque")
df_im = get_data("Copie de Immatriculations")
df_pts = get_data("Points Permis")

tabs = st.tabs(["🚗 Immatriculations", "🪪 Points & Profils", "💰 Banque", "📜 Logs"]) if st.session_state.role == "Staff" else \
       st.tabs(["🚗 Immatriculations", "💰 Facturation"]) if st.session_state.role == "RCT" else \
       st.tabs(["🚗 Mes Véhicules", "💰 Mon Compte"])

# --- ONGLET 1 : IMMATRICULATIONS (LOGIQUE TRIO DÉTECTÉE) ---
with tabs[0]:
    st.header("📋 Registre des Véhicules")
    
    if st.session_state.role != "Civil":
        with st.expander("➕ Enregistrer un nouveau véhicule"):
            with st.form("form_immat"):
                u = st.selectbox("Propriétaire", ["---"] + df_banque["Nom Roblox"].tolist())
                m = st.selectbox("Marque", sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"]))
                p = st.text_input("Plaque (ABC-123)")
                assu = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
                v_pwd = st.text_input("🔑 Code Secret du véhicule", type="password")
                
                # --- CALCULS ---
                cost_ville = 175
                cost_assu = 0
                promo_trio = False
                
                if u != "---":
                    # Détection TRIO RCT : Compte combien de véhicules le client a déjà chez RCT
                    vehicules_rct = len(df_im[(df_im["Nom d'utilisateur ROBLOX"] == u) & (df_im["Assurance"].str.contains("RCT"))])
                    
                    if "RCT" in assu:
                        if vehicules_rct >= 2: # C'est son 3ème véhicule (ou plus)
                            cost_assu = 0 # Le 3ème est gratis (Prime Trio)
                            promo_trio = True
                        else:
                            cost_assu = 150
                    elif "AVERIS" in assu:
                        cost_assu = 130
                
                # Taxe Jeune Conducteur
                taxe_jeune = 0
                if u != "---":
                    u_info = df_banque[df_banque["Nom Roblox"] == u]
                    if not u_info.empty:
                        try:
                            d_arr = datetime.strptime(u_info.iloc[0]["Date d'arrivée"], "%d/%m/%Y")
                            if datetime.now() - d_arr < timedelta(days=30): taxe_jeune = 50
                        except: pass
                
                total = cost_ville + cost_assu + taxe_jeune
                
                # REÇU MODE NUIT
                st.markdown(f"""
                <div class="ticket-nuit">
                    <b>📄 REÇU OFFICIEL</b><br>
                    ----------------------------<br>
                    Frais Immatriculation : 175$<br>
                    Assurance : {cost_assu}$ {"(🎁 PRIME TRIO !)" if promo_trio else ""}<br>
                    Taxe Jeune Conducteur : {taxe_jeune}$<br>
                    ----------------------------<br>
                    <b>TOTAL : {total}$</b>
                </div>
                """, unsafe_allow_html=True)

                if st.form_submit_button("✅ Valider"):
                    if u != "---" and p and v_pwd:
                        idx_u = df_banque[df_banque["Nom Roblox"] == u].index[0]
                        if float(df_banque.at[idx_u, "Solde"]) >= total:
                            df_banque.at[idx_u, "Solde"] = float(df_banque.at[idx_u, "Solde"]) - total
                            
                            # Virement
                            target = TARGET_AVERIS if "AVERIS" in assu else TARGET_RCT if "RCT" in assu else None
                            if target and cost_assu > 0:
                                idx_t = df_banque[df_banque["Nom Roblox"] == target].index
                                if not idx_t.empty:
                                    df_banque.at[idx_t[0], "Solde"] = float(df_banque.at[idx_t[0], "Solde"]) + cost_assu
                            
                            new_v = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "Numéro de la plaque": p, "Assurance": assu, "CODE": str(v_pwd)}])
                            conn.update(worksheet="Banque", data=df_banque)
                            conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_v], ignore_index=True))
                            st.success("Enregistré !"); time.sleep(1); st.rerun()
                        else: st.error("Fonds insuffisants.")

    # --- LISTE DES VÉHICULES ---
    st.divider()
    search = st.text_input("🔍 Recherche Plaque/Nom").lower()
    if not df_im.empty:
        res = df_im[df_im.apply(lambda x: search in str(x).lower(), axis=1)]
        for i, r in res.iterrows():
            with st.container(border=True):
                st.write(f"🚗 **{r['Numéro de la plaque']}** | {r['Nom d\'utilisateur ROBLOX']}")
                with st.expander("⚙️ Options"):
                    if st.text_input("Code secret", type="password", key=f"c_{i}") == str(r['CODE']) or st.session_state.role == "Staff":
                        if st.button("🗑️ Supprimer", key=f"d_{i}"):
                            conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                            st.rerun()

# --- ONGLET 2 : POINTS & PROFILS ---
if st.session_state.role == "Staff":
    with tabs[1]:
        with st.expander("👤 Nouveau Citoyen"):
            with st.form("n_c"):
                n_r = st.text_input("Pseudo Roblox")
                n_d = st.text_input("Pseudo Discord")
                if st.form_submit_button("🚀 Créer"):
                    d = datetime.now().strftime("%d/%m/%Y")
                    nb = pd.DataFrame([{"Solde": 15000, "Nom Discord": n_d, "Nom Roblox": n_r, "Date d'arrivée": d}])
                    np = pd.DataFrame([{"Nom Roblox": n_r, "PTS": 25}])
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, nb], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, np], ignore_index=True))
                    st.success("Profil créé !"); time.sleep(1); st.rerun()

st.markdown("---")
st.markdown("<center><small>RCRP Système v11.9 | 2026</small></center>", unsafe_allow_html=True)
