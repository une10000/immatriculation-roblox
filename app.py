import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# ======================================================================================
# 1. CONFIGURATION SYSTÈME & DESIGN (CSS ÉTENDU)
# ======================================================================================
st.set_page_config(
    page_title="RCRP - Système de Gestion Intégral Professionnel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Correction globale pour le mode nuit */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Boutons personnalisés pour éviter le blanc en mode nuit */
    .stButton>button {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #4b4b4b !important;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
        box-shadow: 0px 0px 10px rgba(255, 75, 75, 0.3);
    }

    /* Badges Assurance */
    .badge-assu { 
        background-color: #ff4b4b; 
        color: white !important; 
        padding: 6px 18px; 
        border-radius: 50px; 
        font-weight: bold; 
        font-size: 0.9rem;
    }

    /* Ticket de Caisse Terminal */
    .ticket-fix { 
        background-color: #000000 !important; 
        color: #00FF00 !important; 
        padding: 35px; 
        border: 2px dashed #ff4b4b; 
        border-radius: 15px; 
        font-family: 'Courier New', monospace; 
        margin: 20px 0;
        box-shadow: inset 0px 0px 15px rgba(0, 255, 0, 0.1);
    }

    /* Sidebar et Conteneurs */
    [data-testid="stSidebar"] img { border-radius: 20px; width: 100% !important; border: 2px solid #333; }
    .main .block-container { padding-top: 5rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1c23; border-radius: 5px 5px 0 0; padding: 10px 20px; }
    </style>
    """, unsafe_allow_html=True)

# ======================================================================================
# 2. PARAMÈTRES ET CONSTANTES (SÉCURITÉ)
# ======================================================================================
if "role" not in st.session_state:
    st.session_state.role = None

TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010" 
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

# ======================================================================================
# 3. GESTION DES DONNÉES (GOOGLE SHEETS)
# ======================================================================================
def fetch_bank_data(connection):
    return connection.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")

def fetch_immat_data(connection):
    return connection.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")

# Ligne 100 : Initialisation et lecture des feuilles
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_banque = fetch_bank_data(conn)
    df_im = fetch_immat_data(conn)
    # Ajout de la lecture pour les permis
    df_permis = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
except Exception as e:
    st.error(f"⚠️ Erreur de liaison système : {e}")
    st.info("Vérifiez la configuration de votre fichier secrets.toml")
    st.stop()

# ======================================================================================
# 4. PORTAIL D'AUTHENTIFICATION
# ======================================================================================
if st.session_state.role is None:
    st.title("🏛️ Système de Gestion Centralisé - Rensselaer County Roleplay FR")
    st.write("---")
    
    st.markdown("""
    ### 📢 Avis Officiel du Gouvernement
    Bienvenue sur le terminal de gestion de la République. Cet outil permet la régulation 
    des flux monétaires, l'immatriculation des biens mobiliers et la gestion des citoyens.
    """)
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.header("👤 Portail Civil")
        if st.button("Connexion Citoyen", use_container_width=True):
            st.session_state.role = "Civil"
            st.rerun()
            
    with col_b:
        st.header("🛠️ Service RCT")
        pwd_rct = st.text_input("Code Agent RCT", type="password", key="login_rct")
        if st.button("Authentification RCT", use_container_width=True):
            if pwd_rct == CODE_PRO:
                st.session_state.role = "RCT"
                st.rerun()
            else:
                st.error("Accès refusé.")
            
    with col_c:
        st.header("👮 Administration")
        pwd_staff = st.text_input("Code Administrateur", type="password", key="login_staff")
        if st.button("Authentification Admin", use_container_width=True):
            if pwd_staff == CODE_ADMIN:
                st.session_state.role = "Staff"
                st.rerun()
            else:
                st.error("Accès refusé.")

    st.divider()
    st.caption("© 2026 RCRP FR - Système de traçage IP activé.")
    st.stop()

# ======================================================================================
# 5. BARRE LATÉRALE
# ======================================================================================
with st.sidebar:
    st.image(LOGO_URL)
    st.divider()
    st.markdown(f"### 📍 Session : **{st.session_state.role}**")
    st.write(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.divider()
    if st.button("🔄 Synchroniser", use_container_width=True):
        st.rerun()
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None
        st.rerun()

# ======================================================================================
# 6. NAVIGATION PRINCIPALE (ONGLETS)
# ======================================================================================
tab_immat, tab_dossier, tab_banque = st.tabs([
    "🚗 REGISTRE VÉHICULES", 
    "🪪 DOSSIERS CITOYENS", 
    "💰 BANQUE CENTRALE"
])

# --- ONGLET 1 : GESTION DES VÉHICULES ---
with tab_immat:
    st.header("🚗 Registre National des Immatriculations")
    with st.expander("➕ Enregistrer un nouveau véhicule", expanded=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            in_proprio = st.selectbox("Titulaire", ["---"] + df_banque["Nom Roblox"].tolist())
            in_marque = st.text_input("Marque et Modèle", placeholder="Ex: Audi RS6")
            in_plaque = st.text_input("Plaque", placeholder="RC-123-RP")
        with f_col2:
            in_assu = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            in_code_sec = st.text_input("Code Secret", type="password")

        taxe_base = 175
        taxe_assu = 130 if "AVERIS" in in_assu else (150 if "RCT" in in_assu else 0)
        total_ttc = taxe_base + taxe_assu

        st.markdown(f'<div class="ticket-fix">TOTAL À RÉGLER : {total_ttc}$</div>', unsafe_allow_html=True)

        if st.button("💳 Valider l'Enregistrement", use_container_width=True):
            if in_proprio != "---" and in_plaque != "" and in_code_sec != "":
                idx_citoyen = df_banque[df_banque["Nom Roblox"] == in_proprio].index[0]
                solde_actuel = float(str(df_banque.at[idx_citoyen, "Solde"]).replace('$', '').replace(' ', ''))
                
                if solde_actuel >= total_ttc:
                    df_banque.at[idx_citoyen, "Solde"] = solde_actuel - total_ttc
                    if taxe_assu > 0:
                        desti = TARGET_AVERIS if "AVERIS" in in_assu else TARGET_RCT
                        idx_dest = df_banque[df_banque["Nom Roblox"] == desti].index[0]
                        s_dest = float(str(df_banque.at[idx_dest, "Solde"]).replace('$', '').replace(' ', ''))
                        df_banque.at[idx_dest, "Solde"] = s_dest + taxe_assu
                    
                    new_vehicule = pd.DataFrame([{
                        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                        "Nom d'utilisateur ROBLOX": in_proprio,
                        "Marque du véhicule": in_marque,
                        "Numéro de la plaque": in_plaque,
                        "Assurance": in_assu,
                        "CODE": str(in_code_sec)
                    }])
                    conn.update(worksheet="Banque", data=df_banque)
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_vehicule], ignore_index=True))
                    st.success("✅ Enregistré !")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Solde insuffisant.")

# --- ONGLET 2 : DOSSIERS (AJOUTÉ : 15K + 25 PTS + DATE AUTO) ---
with tab_dossier:
    st.header("🪪 Dossiers Administratifs")
    if st.session_state.role == "Staff":
        with st.container(border=True):
            st.subheader("🧧 Création Nouveau Profil")
            with st.form("new_cit_form"):
                n_rob = st.text_input("Nom Roblox")
                n_dis = st.text_input("Nom Discord")
                n_job = st.selectbox("Poste", ["Civil", "Agent RCT", "Gouvernement"])
                if st.form_submit_button("Valider la création complète"):
                    d_crea = datetime.now().strftime("%d/%m/%Y")
                    # Double écriture demandée
                    new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": n_dis, "Nom Roblox": n_rob, "Date d'arrivée": d_crea, "Emploiement": n_job}])
                    new_p = pd.DataFrame([{"Nom Discord": n_dis, "Nom Roblox": n_rob, "PTS": 25, "Validité": "OUI"}])
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, new_b], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_permis, new_p], ignore_index=True))
                    st.success(f"✅ Dossier créé le {d_crea} ! 15k et 25pts ajoutés."); time.sleep(1); st.rerun()

    # Liste des dossiers
    search_cit = st.text_input("Rechercher un citoyen", key="search_cit").lower()
    for idx, r in df_banque.iterrows():
        if not search_cit or search_cit in str(r["Nom Roblox"]).lower():
            with st.container(border=True):
                st.write(f"👤 **{r['Nom Roblox']}** | 💼 {r['Emploiement']} | 📅 Arrivée : {r['Date d\'arrivée']}")

# --- ONGLET 3 : BANQUE ---
with tab_banque:
    st.header("💰 Banque Centrale")
    search_bank = st.text_input("Rechercher un compte", key="search_bank").lower()
    for idx, r in df_banque.iterrows():
        if search_bank in str(r["Nom Roblox"]).lower():
            with st.container(border=True):
                val_solde = float(str(r["Solde"]).replace('$', '').replace(' ', ''))
                st.metric(r['Nom Roblox'], f"{val_solde:,.0f} $")
                if st.session_state.role in ["RCT", "Staff"]:
                    m_amende = st.number_input("Montant ($)", min_value=0, key=f"am_{idx}")
                    if st.button("Prélever", key=f"btn_{idx}"):
                        df_banque.at[idx, "Solde"] = val_solde - m_amende
                        conn.update(worksheet="Banque", data=df_banque)
                        st.success("Fait !"); time.sleep(1); st.rerun()

st.markdown("<center>RCRP SYSTEM v16.8</center>", unsafe_allow_html=True)
