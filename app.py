import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Portail Officiel", layout="wide")

# --- STYLE CSS AVANCÉ (ALIGNEMENT & LOGO) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    
    /* Force les colonnes de connexion à avoir la même structure */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        display: flex;
        flex-direction: column;
        height: 450px !important; /* Hauteur fixe pour aligner les boutons en bas */
        justify-content: space-between;
    }

    .stMetric { 
        background-color: #f8f9fb; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid #e0e0e0; 
    }
    
    [data-testid="stSidebar"] img {
        border-radius: 10px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "role" not in st.session_state:
    st.session_state.role = None

conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26" 
CODE_ENTREPRISE = "RCT-26-RCRPFR" 
MON_PSEUDO_ROBLOX = "une10000"
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

def get_data(sheet_name):
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except: return pd.DataFrame()

# ==========================================
# 🚪 PAGE DE CONNEXION (FIX ALIGNEMENT)
# ==========================================
if st.session_state.role is None:
    st.title("🏛️ Portail des Services RCRP")
    st.markdown("<p style='font-size: 20px; color: #555;'>Système Centralisé de la République de Californie</p>", unsafe_allow_html=True)
    
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 👤 Citoyen")
            st.write("Accès public : consultez les registres, votre solde bancaire et vos points de permis.")
            # Espaceur pour compenser l'absence d'input et aligner le bouton
            st.write("") 
            st.write("")
            st.write("")
            st.write("")
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"; st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### 🛠️ Entreprise (RCT)")
            st.write("Interface RCT : Facturation professionnelle et gestion des assurances.")
            c_rct = st.text_input("Code RCT", type="password", key="log_rct")
            if st.button("Connexion Pro", use_container_width=True):
                if c_rct == CODE_ENTREPRISE:
                    st.session_state.role = "RCT"; st.rerun()
                else: st.error("❌ Code incorrect.")

    with col3:
        with st.container(border=True):
            st.markdown("### 👮 Autorités / Staff")
            st.write("Administration totale : Fichier Central, gestion des permis et logs.")
            c_pol = st.text_input("Code Autorisation", type="password", key="log_pol")
            if st.button("Connexion Sécurisée", use_container_width=True):
                if c_pol == CODE_ADMIN_GENERAL:
                    st.session_state.role = "Staff"; st.rerun()
                else: st.error("❌ Code incorrect.")
    st.stop()

# ==========================================
# 🖥️ INTERFACE CONNECTÉE (RETOUR DU COMPLET)
# ==========================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.write(f"🎭 Session : **{st.session_state.role}**")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()
    st.divider()
    st.info(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

st.title(f"🏛️ Espace {st.session_state.role}")

# --- LISTES & DONNÉES ---
liste_assurances = ["Non assuré", "RCT", "Averis"]
liste_etats = sorted(["California", "Washington", "Texas", "New York", "Florida", "Quebec", "Ontario"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Revolt", "Turismo", "Roamer", "Envy", "Mizuhara"])

# --- ONGLETS ---
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers Permis", "💰 Banque Centrale", "📜 Logs"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation RCT"])
else:
    tabs = st.tabs(["🚗 Registre Véhicules", "💰 Mon Compte (Solde & Points)"])

# 🚗 ONGLET 1 : IMMATRICULATIONS (FONCTIONS RCT/STAFF)
with tabs[0]:
    df_im = get_data("Copie de Immatriculations")
    st.metric("🚗 Véhicules enregistrés", len(df_im))
    
    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("add_v"):
            c1, c2 = st.columns(2)
            u = c1.text_input("👤 Pseudo Roblox")
            m = c1.selectbox("🚘 Marque", liste_marques)
            p = c2.text_input("🔢 Plaque")
            e = c2.selectbox("📍 État", liste_etats)
            a = c1.selectbox("🛡️ Assurance", liste_assurances)
            c = c2.text_input("🔑 Code secret", type="password")
            if st.form_submit_button("✅ Valider"):
                if u and p:
                    new_r = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "L'état de la plaque": e, "Numéro de la plaque": p, "Assurance": a, "CODE": str(c)}])
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_r], ignore_index=True))
                    st.success("🎉 Enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    sq = st.text_input("🔍 Rechercher une plaque ou un nom").strip().upper()
    if not df_im.empty:
        mask = df_im.apply(lambda r: sq in str(r).upper(), axis=1) if sq else [True]*len(df_im)
        for idx, row in df_im[mask].iterrows():
            with st.container(border=True):
                co1, co2 = st.columns([3, 1])
                co1.markdown(f"**🚗 {row['Numéro de la plaque']}** — {row['Marque du véhicule']}")
                co1.write(f"👤 {row['Nom d\'utilisateur ROBLOX']} | 🛡️ {row['Assurance']}")
                
                if st.session_state.role in ["Staff", "RCT"]:
                    if co2.button(f"⚙️ Gérer", key=f"g_{idx}"):
                        st.session_state[f"op_{idx}"] = not st.session_state.get(f"op_{idx}", False)
                    if st.session_state.get(f"op_{idx}"):
                        with st.form(f"fo_{idx}"):
                            na = st.selectbox("Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']) if row['Assurance'] in liste_assurances else 0)
                            if st.form_submit_button("💾 Sauver"):
                                df_im.at[idx, 'Assurance'] = na
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.success("Mis à jour !"); time.sleep(1); st.rerun()

# 💰 ONGLET 2 : BANQUE & POINTS (FIX ERROR)
with tabs[1]:
    if st.session_state.role == "Civil":
        nom_c = st.text_input("Pseudo Roblox exact", value="une10000").strip().lower()
        if nom_c:
            m1, m2 = st.columns(2)
            df_b = get_data("Banque")
            res_b = df_b[df_b['Nom Roblox'].str.lower() == nom_c] if not df_b.empty else pd.DataFrame()
            if not res_b.empty: m1.metric("💵 Solde", f"{float(res_b.iloc[0]['Solde']):,.0f} $")
            
            df_p = get_data("Points Permis")
            if not df_p.empty:
                res_p = df_p[df_p['Nom Roblox'].str.lower() == nom_c]
                if not res_p.empty and 'Points' in res_p.columns:
                    m2.metric("🪪 Points", f"{res_p.iloc[0]['Points']} / 12")
                else: m2.info("Pas de points trouvés.")
    else:
        # Administration financière complète
        df_b = get_data("Banque")
        sb = st.text_input("🔍 Rechercher un compte").strip().lower()
        if not df_b.empty and sb:
            res_b = df_b[df_b['Nom Roblox'].str.lower().str.contains(sb)]
            for idx, row in res_b.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **{row['Nom Roblox']}** | 💰 {float(row['Solde']):,.0f} $")
                    with st.form(f"fb_{idx}"):
                        mt = st.number_input("Montant", min_value=0.0, step=100.0)
                        if st.form_submit_button("📉 Facturer"):
                            # Logique de facturation RCT/Staff...
                            st.info("Action effectuée.")

# 🪪 & 📜 STAFF ONLY
if st.session_state.role == "Staff":
    with tabs[2]: st.write("### Dossiers Permis"); st.dataframe(get_data("Points Permis"), use_container_width=True)
    with tabs[3]: st.write("### Archives Logs"); st.dataframe(get_data("Logs").iloc[::-1], use_container_width=True)

st.markdown("---")
st.markdown("<center><small>République de Californie RP | Système v9.22</small></center>", unsafe_allow_html=True)
