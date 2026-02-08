import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# =============================
# CONFIG PAGE
# =============================
st.set_page_config(page_title="RCRP - Portail Officiel", layout="wide")

# =============================
# STYLE
# =============================
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; padding-bottom: 0rem; }

div[data-testid="stVerticalBlockBorderWrapper"] {
    display: flex;
    flex-direction: column;
    height: 520px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] .stButton {
    margin-top: auto !important;
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

# =============================
# SESSION
# =============================
if "role" not in st.session_state:
    st.session_state.role = None

# =============================
# CONNEXION
# =============================
conn = st.connection("gsheets", type=GSheetsConnection)

CODE_ADMIN_GENERAL = "RCRPFR-25-26"
CODE_ENTREPRISE = "RCT-26-RCRPFR"
MON_PSEUDO_ROBLOX = "une10000"

LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

def get_data(sheet):
    try:
        df = conn.read(worksheet=sheet, ttl=0)
        return df.dropna(how="all").fillna("")
    except:
        return pd.DataFrame()

# =============================
# CONNEXION PAGE
# =============================
if st.session_state.role is None:
    st.title("🏛️ Portail des Services RCRP")
    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.markdown("### 👤 Citoyen")
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()

    with c2:
        with st.container(border=True):
            st.markdown("### 🛠️ Entreprise (RCT)")
            st.text_input("Code RCT", type="password", key="p_rct")
            if st.button("Connexion Pro", use_container_width=True):
                if st.session_state.p_rct == CODE_ENTREPRISE:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("Code incorrect")

    with c3:
        with st.container(border=True):
            st.markdown("### 👮 Staff")
            st.text_input("Code Staff", type="password", key="p_staff")
            if st.button("Connexion Staff", use_container_width=True):
                if st.session_state.p_staff == CODE_ADMIN_GENERAL:
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    st.error("Code incorrect")

    st.stop()

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.write(f"🎭 **{st.session_state.role}**")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    st.divider()
    st.write(datetime.now().strftime("📅 %d/%m/%Y"))

st.title(f"🏛️ Espace {st.session_state.role}")

# =============================
# LISTES
# =============================
liste_assurances = ["Non assuré", "RCT", "Averis"]
liste_etats = ["California", "Washington", "Texas", "New York", "Florida"]
liste_marques = ["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam"]

# =============================
# ONGLET
# =============================
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers Permis", "💰 Banque", "📜 Logs"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Banque"])
else:
    tabs = st.tabs(["🚗 Véhicules", "💰 Compte"])

# =============================
# IMMATRICULATIONS
# =============================
with tabs[0]:
    df_im = get_data("Copie de Immatriculations")

    with st.expander("➕ Nouveau véhicule"):
        with st.form("add_vehicle"):
            c1, c2 = st.columns(2)
            user = c1.text_input("Pseudo Roblox")
            marque = c1.selectbox("Marque", liste_marques)
            plaque = c2.text_input("Plaque")
            etat = c2.selectbox("État", liste_etats)
            assurance = c1.selectbox("Assurance", liste_assurances)
            code = c2.text_input("Code secret", type="password")

            if st.form_submit_button("Enregistrer"):
                new = pd.DataFrame([{
                    "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Nom d'utilisateur ROBLOX": user,
                    "Marque du véhicule": marque,
                    "Numéro de la plaque": plaque,
                    "L'état de la plaque": etat,
                    "Assurance": assurance,
                    "CODE": code
                }])
                conn.update("Copie de Immatriculations", pd.concat([df_im, new], ignore_index=True))
                st.success("Véhicule enregistré")
                time.sleep(1)
                st.rerun()

    search = st.text_input("🔍 Recherche")
    for idx, row in df_im.iterrows():
        if search.lower() in str(row).lower():
            with st.container(border=True):
                st.write(f"🚗 **{row['Numéro de la plaque']}** — {row['Nom d'utilisateur ROBLOX']}")
                st.write(f"{row['Marque du véhicule']} | {row['Assurance']}")

# =============================
# DOSSIERS PERMIS (STAFF)
# =============================
if st.session_state.role == "Staff":
    with tabs[1]:
        with st.expander("➕ Créer citoyen"):
            with st.form("create_citizen"):
                nom_discord = st.text_input("Discord")
                nom_roblox = st.text_input("Roblox")
                pts = st.number_input("Points", 0, 25, 25)
                validite = st.selectbox("Validité", ["OUI", "NON", "VALIDE"])

                if st.form_submit_button("Créer"):
                    df_b = get_data("Banque")
                    df_p = get_data("Points Permis")

                    if nom_roblox.lower() in df_b["Nom Roblox"].astype(str).str.lower().values:
                        st.error("Déjà existant")
                    else:
                        conn.update("Banque", pd.concat([df_b, pd.DataFrame([{
                            "Nom Discord": nom_discord,
                            "Nom Roblox": nom_roblox,
                            "Solde": 15000,
                            "Date d'arrivée": datetime.now().strftime("%d/%m/%Y")
                        }])], ignore_index=True))

                        conn.update("Points Permis", pd.concat([df_p, pd.DataFrame([{
                            "Nom Discord": nom_discord,
                            "Nom Roblox": nom_roblox,
                            "PTS": pts,
                            "Validité": validite
                        }])], ignore_index=True))

                        st.success("Profil créé")
                        time.sleep(1)
                        st.rerun()

# =============================
# BANQUE
# =============================
with tabs[2 if st.session_state.role == "Staff" else 1]:
    df_b = get_data("Banque")
    search = st.text_input("🔍 Compte")
    for idx, row in df_b.iterrows():
        if search.lower() in str(row).lower():
            with st.container(border=True):
                st.metric(row["Nom Roblox"], f"{float(row['Solde']):,.0f} $")

# =============================
# LOGS
# =============================
if st.session_state.role == "Staff":
    with tabs[3]:
        st.dataframe(get_data("Logs"), use_container_width=True)

st.markdown("---")
st.markdown("<center><small>RCRP FR | v9.32</small></center>", unsafe_allow_html=True)
