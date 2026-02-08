import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Portail Officiel", layout="wide")

# --- STYLE CSS (OPTIMISATION ESPACE) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    div[data-testid="stExpander"] { border: 1px solid #f0f2f6; border-radius: 10px; }
    .stMetric { background-color: #f8f9fb; padding: 10px; border-radius: 10px; }
    /* Aligner verticalement le logo et le texte */
    [data-testid="stHorizontalBlock"] { align-items: center; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION SESSION ---
if "role" not in st.session_state:
    st.session_state.role = None

# --- PARAMÈTRES ET CODES ---
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26" 
CODE_ENTREPRISE = "RCT-26-RCRPFR" 
MON_PSEUDO_ROBLOX = "une10000"

LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=1100&height=608"

def get_data(sheet_name):
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except: return pd.DataFrame()

# ==========================================
# 🚪 PAGE DE CONNEXION
# ==========================================
if st.session_state.role is None:
    # Header Connexion : Logo à gauche, Texte à droite
    head_col1, head_col2 = st.columns([1, 3])
    with head_col1:
        st.image(LOGO_URL, use_container_width=True)
    with head_col2:
        st.markdown("<h1>🏛️ Portail des Services RCRP</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 20px;'>Système Centralisé de la République</p>", unsafe_allow_html=True)
    
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.write("### 👤 Citoyen")
            st.write("Consulter les registres publics.")
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"; st.rerun()
    with col2:
        with st.container(border=True):
            st.write("### 🛠️ Entreprise (RCT)")
            st.write("Interface Facturation.")
            c_rct = st.text_input("Code RCT", type="password", key="log_rct")
            if st.button("Connexion Pro", use_container_width=True):
                if c_rct == CODE_ENTREPRISE:
                    st.session_state.role = "RCT"; st.rerun()
                else: st.error("❌ Code incorrect.")
    with col3:
        with st.container(border=True):
            st.write("### 👮 Autorités / Staff")
            st.write("Gestion totale.")
            c_pol = st.text_input("Code Autorisation", type="password", key="log_pol")
            if st.button("Connexion Sécurisée", use_container_width=True):
                if c_pol == CODE_ADMIN_GENERAL:
                    st.session_state.role = "Staff"; st.rerun()
                else: st.error("❌ Code incorrect.")
    st.stop()

# ==========================================
# 🖥️ INTERFACE CONNECTÉE
# ==========================================

# Header Interface : Logo à gauche, Rôle à droite
main_head1, main_head2 = st.columns([1, 5])
with main_head1:
    st.image(LOGO_URL, use_container_width=True)
with main_head2:
    st.title(f"🏛️ Espace {st.session_state.role}")

# Barre latérale pour les actions secondaires
with st.sidebar:
    st.write(f"👤 Session : **{st.session_state.role}**")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()
    st.divider()
    st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

# --- DÉFINITION DES ONGLETS SELON LE RÔLE ---
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Permis", "💰 Banque", "📜 Logs"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation RCT Business"])
else:
    tabs = st.tabs(["🚗 Registre Véhicules", "💰 Mon Compte"])

# ... (Le reste du code des onglets reste identique aux versions précédentes pour ne rien perdre)

# ==========================================
# 🚗 ONGLET 1 : IMMATRICULATIONS (Exemple de contenu)
# ==========================================
with tabs[0]:
    df_im = get_data("Copie de Immatriculations")
    st.metric("🚗 Véhicules enregistrés", len(df_im))
    # Suite du code identique...
