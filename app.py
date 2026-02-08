import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Portail Officiel", layout="wide")

# --- STYLE CSS ---
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

# --- SESSION ---
if "role" not in st.session_state:
    st.session_state.role = None

# --- CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26"
CODE_ENTREPRISE = "RCT-26-RCRPFR"
MON_PSEUDO_ROBLOX = "une10000"

LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

def get_data(sheet):
    try:
        data = conn.read(worksheet=sheet, ttl=0)
        return data.dropna(how="all").fillna("")
    except:
        return pd.DataFrame()

# ==========================================
# 🚪 CONNEXION
# ==========================================
if st.session_state.role is None:
    st.title("🏛️ Portail des Services RCRP")
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("### 👤 Citoyen")
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### 🛠️ Entreprise (RCT)")
            st.text_input("Code RCT", type="password", key="p_rct")
            if st.button("Connexion Pro", use_container_width=True):
                if st.session_state.p_rct == CODE_ENTREPRISE:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("Code incorrect")

    with col3:
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

# ==========================================
# 🖥️ INTERFACE
# ==========================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.write(f"🎭 **{st.session_state.role}**")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    st.divider()
    st.write(datetime.now().strftime("📅 %d/%m/%Y"))

st.title(f"🏛️ Espace {st.session_state.role}")

# --- ONGLETS ---
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers Permis", "💰 Banque", "📜 Logs"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Banque"])
else:
    tabs = st.tabs(["🚗 Véhicules", "💰 Compte"])

# ==========================================
# 🚗 ONGLET 1
# ==========================================
with tabs[0]:
    st.info("Section immatriculations inchangée")

# ==========================================
# 🪪 ONGLET STAFF – POINTS + CRÉATION PROFIL
# ==========================================
if st.session_state.role == "Staff":
    with tabs[1]:
        st.subheader("🪪 Gestion des Permis")

        with st.expander("➕ Créer un nouveau profil citoyen"):
            with st.form("create_citizen"):
                c1, c2 = st.columns(2)
                nom_discord = c1.text_input("Nom Discord")
                nom_roblox = c2.text_input("Nom Roblox")
                pts = c1.number_input("Points", 0, 25, 25)
                validite = c2.selectbox("Validité", ["OUI", "NON", "VALIDE"])

                if st.form_submit_button("Créer le profil"):
                    df_b = get_data("Banque")
                    df_p = get_data("Points Permis")

                    if nom_roblox.lower() in df_b["Nom Roblox"].astype(str).str.lower().values:
                        st.error("Profil déjà existant")
                    else:
                        conn.update(
                            worksheet="Banque",
                            data=pd.concat([df_b, pd.DataFrame([{
                                "Nom Discord": nom_discord,
                                "Nom Roblox": nom_roblox,
                                "Solde": 15000,
                                "Date d'arrivée": datetime.now().strftime("%d/%m/%Y")
                            }])], ignore_index=True)
                        )

                        conn.update(
                            worksheet="Points Permis",
                            data=pd.concat([df_p, pd.DataFrame([{
                                "Nom Discord": nom_discord,
                                "Nom Roblox": nom_roblox,
                                "PTS": pts,
                                "Validité": validite,
                                "UserID DISC": "",
                                "UserID RBLX": ""
                            }])], ignore_index=True)
                        )

                        st.success("Profil créé avec succès")
                        time.sleep(1)
                        st.rerun()

        st.divider()

        df_pts = get_data("Points Permis")
        search = st.text_input("🔍 Rechercher citoyen")
        if search:
            res = df_pts[df_pts.apply(lambda r: search.lower() in str(r).lower(), axis=1)]
            for idx, row in res.iterrows():
                with st.form(f"pts_{idx}"):
                    st.write(f"**{row['Nom Roblox']}** — {row['PTS']} / 25")
                    new_pts = st.number_input("Nouveaux points", 0, 25, int(row["PTS"]))
                    if st.form_submit_button("Mettre à jour"):
                        df_pts.at[idx, "PTS"] = new_pts
                        conn.update(worksheet="Points Permis", data=df_pts)
                        st.success("Mis à jour")
                        time.sleep(1)
                        st.rerun()

# ==========================================
# 💰 ONGLET BANQUE
# ==========================================
with tabs[2 if st.session_state.role == "Staff" else 1]:
    st.info("Section banque inchangée")

# ==========================================
# 📜 LOGS
# ==========================================
if st.session_state.role == "Staff":
    with tabs[3]:
        st.dataframe(get_data("Logs"), use_container_width=True)

st.markdown("---")
st.markdown("<center><small>RCRP FR | Système de Gestion Intégral v9.32</small></center>", unsafe_allow_html=True)
