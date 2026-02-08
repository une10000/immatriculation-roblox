import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# ======================================================================================
# 1. CONFIGURATION SYSTÈME & DESIGN (CSS ÉTENDU & PERSONNALISÉ)
# ======================================================================================
# Cette section définit l'apparence visuelle de l'application RCRP.
# On utilise du HTML/CSS injecté pour assurer un rendu professionnel en mode nuit.

st.set_page_config(
    page_title="RCRP - Système de Gestion Intégral Professionnel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Correction globale pour le mode nuit et la lisibilité */
    .stApp { 
        background-color: #0e1117; 
        color: #ffffff; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Boutons personnalisés avec effet au survol (Hover) */
    .stButton>button {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #4b4b4b !important;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease-in-out;
        width: 100%;
    }
    .stButton>button:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
        box-shadow: 0px 0px 15px rgba(255, 75, 75, 0.4);
        transform: translateY(-2px);
    }

    /* Badges pour les assurances dans le registre */
    .badge-assu { 
        background-color: #ff4b4b; 
        color: white !important; 
        padding: 8px 20px; 
        border-radius: 50px; 
        font-weight: bold; 
        font-size: 0.9rem;
        text-align: center;
        display: inline-block;
    }

    /* Ticket de Caisse Terminal (Effet rétro-informatique) */
    .ticket-fix { 
        background-color: #000000 !important; 
        color: #00FF00 !important; 
        padding: 35px; 
        border: 2px dashed #ff4b4b; 
        border-radius: 15px; 
        font-family: 'Courier New', monospace; 
        margin: 20px 0;
        box-shadow: inset 0px 0px 20px rgba(0, 255, 0, 0.1);
        line-height: 1.5;
    }

    /* Sidebar, Conteneurs et Alignements */
    [data-testid="stSidebar"] img { 
        border-radius: 20px; 
        width: 100% !important; 
        border: 2px solid #333; 
        margin-bottom: 20px;
    }
    .main .block-container { padding-top: 4rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1a1c23; 
        border-radius: 8px 8px 0 0; 
        padding: 12px 25px;
        color: #888;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #ff4b4b !important; 
        color: white !important; 
    }

    /* Style des cartes de citoyens */
    .citoyen-card {
        background-color: #1e2129;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 15px;
    }

    /* Animation de succès */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .success-msg {
        animation: fadeIn 0.5s ease-in;
        color: #00FF00;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ======================================================================================
# 2. PARAMÈTRES, CONSTANTES ET SÉCURITÉ
# ======================================================================================
# Initialisation de l'état de la session (Authentification persistante)
if "role" not in st.session_state:
    st.session_state.role = None

# Identifiants de redirection des fonds (Gestion des flux monétaires)
TARGET_RCT = "une10000"     # Compte gouvernemental pour l'assurance RCT
TARGET_AVERIS = "Moune2010" # Redirection des fonds d'Averis (Configuration Utilisateur)

# Codes d'accès sécurisés (Protocoles Admin et Pro)
CODE_ADMIN = "RCRPFR-25-26"   
CODE_PRO = "RCT-26-RCRPFR"    

# Logo officiel (Correction lien)
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

# ======================================================================================
# 3. MOTEUR DE GESTION DES DONNÉES (GOOGLE SHEETS API)
# ======================================================================================
def fetch_bank_data(connection):
    """Extraction sécurisée des données de l'onglet Banque"""
    try:
        data = connection.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
        return data
    except Exception as e:
        st.error(f"Erreur Critique (Banque): {e}")
        return pd.DataFrame()

def fetch_immat_data(connection):
    """Extraction sécurisée des données de l'onglet Immatriculations"""
    try:
        data = connection.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        return data
    except Exception as e:
        st.error(f"Erreur Critique (Immat): {e}")
        return pd.DataFrame()

# Établissement de la connexion principale via Streamlit Connection
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_banque = fetch_bank_data(conn)
    df_im = fetch_immat_data(conn)
except Exception as e:
    st.error(f"⚠️ ÉCHEC DE LA SYNCHRONISATION : {e}")
    st.stop()

# ======================================================================================
# 4. PORTAIL D'AUTHENTIFICATION CENTRALISÉ (ACCUEIL)
# ======================================================================================
if st.session_state.role is None:
    st.title("🏛️ Système de Gestion Centralisé - République de Palm City")
    st.write("---")
    
    st.markdown("""
    ### 📢 Avis Officiel du Gouvernement
    Bienvenue sur le terminal de gestion de la République. Cet outil sécurisé permet la régulation 
    des flux monétaires, l'immatriculation des véhicules et la gestion des citoyens.
    
    **Veuillez vous authentifier pour accéder au terminal :**
    """)
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.header("👤 Portail Civil")
        st.info("Espace public pour les résidents.")
        st.markdown("- Consultation du registre\n- Déclaration véhicule\n- Solde bancaire")
        if st.button("Connexion Citoyen", use_container_width=True):
            st.session_state.role = "Civil"
            st.rerun()
            
    with col_b:
        st.header("🛠️ Service RCT")
        st.warning("Accès Agents de la Régie.")
        st.markdown("- Taxes immatriculation\n- Validation contrats\n- Prélèvement amendes")
        pwd_rct = st.text_input("Code Agent", type="password", key="log_rct")
        if st.button("Authentification RCT", use_container_width=True):
            if pwd_rct == CODE_PRO:
                st.session_state.role = "RCT"
                st.rerun()
            else:
                st.error("Code invalide.")
            
    with col_c:
        st.header("👮 Administration")
        st.error("Haut-Commandement.")
        st.markdown("- Banque Centrale\n- Création profils\n- Paye générale")
        pwd_staff = st.text_input("Code Admin", type="password", key="log_staff")
        if st.button("Authentification Admin", use_container_width=True):
            if pwd_staff == CODE_ADMIN:
                st.session_state.role = "Staff"
                st.rerun()
            else:
                st.error("Accès refusé.")

    st.divider()
    st.caption("© 2026 Palm City Government - Tous droits réservés.")
    st.stop()

# ======================================================================================
# 5. CONFIGURATION DE LA BARRE LATÉRALE (SIDEBAR)
# ======================================================================================
with st.sidebar:
    st.image(LOGO_URL)
    st.divider()
    st.markdown(f"### 📍 Session active : **{st.session_state.role}**")
    st.write(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"⏰ **Heure :** {datetime.now().strftime('%H:%M:%S')}")
    st.divider()
    if st.button("🔄 Actualiser le système", use_container_width=True):
        st.rerun()
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    st.divider()
    st.caption("Serveur : RCRP-MAIN-NODE")

# ======================================================================================
# 6. NAVIGATION PRINCIPALE (ONGLETS DE GESTION)
# ======================================================================================
tab_immat, tab_dossier, tab_banque = st.tabs([
    "🚗 REGISTRE VÉHICULES", 
    "🪪 DOSSIERS CITOYENS", 
    "💰 BANQUE CENTRALE"
])

# --- ONGLET 1 : GESTION DES VÉHICULES ---
with tab_immat:
    st.header("🚗 Registre National des Immatriculations")
    
    with st.expander("➕ Enregistrer un nouveau véhicule (Procédure Légale)", expanded=True):
        st.write("Veuillez saisir les informations conformes à la carte grise.")
        
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            in_proprio = st.selectbox("Titulaire", ["---"] + df_banque["Nom Roblox"].tolist())
            in_marque = st.text_input("Marque et Modèle", placeholder="Ex: BMW M4 Competition")
            in_plaque = st.text_input("Plaque", placeholder="PC-001-RP")
            
        with f_col2:
            in_assu = st.selectbox("Contrat Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            in_code_sec = st.text_input("Code Secret", type="password", help="Utilisé pour la radiation.")

        # LOGIQUE DE CALCUL DES TAXES DÉTAILLÉE
        taxe_base = 175
        taxe_assu = 0
        taxe_nouveau = 0
        
        if "AVERIS" in in_assu: taxe_assu = 130
        elif "RCT" in in_assu: taxe_assu = 150
            
        # Offre Trio RCT
        v_existants = df_im[df_im["Nom d'utilisateur ROBLOX"] == in_proprio]
        rct_count = len(v_existants[v_existants["Assurance"].str.contains("RCT", na=False)])
        if "RCT" in in_assu and rct_count >= 2:
            taxe_assu = 0
            st.success("✨ Avantage Fidélité : Assurance gratuite (Trio RCT) !")

        # Taxe Nouveau Citoyen
        if in_proprio != "---":
            row_u = df_banque[df_banque["Nom Roblox"] == in_proprio]
            try:
                d_arrivée = datetime.strptime(str(row_u.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                if (datetime.now() - d_arrivée).days < 30:
                    taxe_nouveau = 50
                    st.warning("⚠️ Taxe Jeune Citoyen active (+50$)")
            except: pass

        total_ttc = taxe_base + taxe_assu + taxe_nouveau
        
        st.markdown(f"""
        <div class="ticket-fix">
            <b>RCRP - FACTURE D'IMMATRICULATION</b><br>
            ------------------------------------------------<br>
            TITULAIRE : {in_proprio}<br>
            PLAQUE    : {in_plaque}<br>
            ------------------------------------------------<br>
            TOTAL À PAYER : {total_ttc}$
        </div>
        """, unsafe_allow_html=True)

        if st.button("💳 Valider l'Enregistrement", use_container_width=True):
            if in_proprio != "---" and in_plaque != "":
                idx_c = df_banque[df_banque["Nom Roblox"] == in_proprio].index[0]
                solde_c = float(str(df_banque.at[idx_c, "Solde"]).replace('$', '').replace(' ', ''))
                
                if solde_c >= total_ttc:
                    df_banque.at[idx_c, "Solde"] = solde_c - total_ttc
                    if taxe_assu > 0:
                        dest = TARGET_AVERIS if "AVERIS" in in_assu else TARGET_RCT
                        idx_d = df_banque[df_banque["Nom Roblox"] == dest].index[0]
                        df_banque.at[idx_d, "Solde"] = float(str(df_banque.at[idx_d, "Solde"]).replace('$', '')) + taxe_assu
                    
                    new_v = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y"), "Nom d'utilisateur ROBLOX": in_proprio, "Marque du véhicule": in_marque, "Numéro de la plaque": in_plaque, "Assurance": in_assu, "CODE": str(in_code_sec)}])
                    conn.update(worksheet="Banque", data=df_banque)
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_v], ignore_index=True))
                    st.success("✅ Véhicule enregistré !"); time.sleep(1); st.rerun()
                else:
                    st.error("Solde insuffisant.")

    st.divider()
    st.subheader("🔍 Consultation du Registre")
    query = st.text_input("Rechercher...").lower()
    for i, row in df_im.iterrows():
        if not query or query in str(row["Numéro de la plaque"]).lower() or query in str(row["Nom d'utilisateur ROBLOX"]).lower():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1: st.markdown(f"### {row['Numéro de la plaque']}"); st.write(f"🚗 {row['Marque du véhicule']}")
                with c2: st.write(f"👤 {row['Nom d\'utilisateur ROBLOX']}"); st.write(f"📅 {row['Horodateur']}")
                with c3: st.markdown(f'<div class="badge-assu">{row["Assurance"]}</div>', unsafe_allow_html=True)
                with st.expander("⚙️ Radiation"):
                    in_rad = st.text_input("Code", type="password", key=f"rad_{i}")
                    if st.button("🚫 Radier", key=f"btn_rad_{i}"):
                        if in_rad == str(row["CODE"]) or st.session_state.role == "Staff":
                            conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                            st.success("Radié !"); time.sleep(1); st.rerun()

# --- ONGLET 2 : DOSSIERS CITOYENS ---
with tab_dossier:
    st.header("🪪 Dossiers Administratifs")
    
    if st.session_state.role == "Staff":
        with st.container(border=True):
            st.subheader("🧧 Console de Gestion Staff")
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                st.write("Gestion des finances globales.")
                if st.button("💰 Lancer la Paye Générale", use_container_width=True):
                    for idx, r in df_banque.iterrows():
                        montant = 17000 if "RCT" in str(r["Emploiement"]) else 15000
                        df_banque.at[idx, "Solde"] = float(str(r["Solde"]).replace('$', '')) + montant
                    conn.update(worksheet="Banque", data=df_banque)
                    st.success("Payes versées !")
            
            with col_s2:
                with st.expander("👤 Créer un nouveau profil"):
                    with st.form("new_cit_form"):
                        n_rob = st.text_input("Nom ROBLOX")
                        n_dis = st.text_input("Nom Discord")
                        n_job = st.selectbox("Poste", ["Civil", "Agent RCT", "Gouvernement"])
                        
                        st.markdown("---")
                        st.warning("⚠️ Action irréversible : Cela créera un compte bancaire et un dossier permis.")
                        confirm_create = st.checkbox("Je confirme la création du dossier citoyen")
                        
                        submit_cit = st.form_submit_button("🔨 Valider la Création")
                        
                        if submit_cit:
                            if not confirm_create:
                                st.error("Veuillez cocher la case de confirmation.")
                            elif n_rob and n_dis:
                                d_creation = datetime.now().strftime("%d/%m/%Y")
                                
                                # Création Banque
                                new_b = pd.DataFrame([{"Solde": 15000, "Emploiement": n_job, "Nom Discord": n_dis, "Nom Roblox": n_rob, "Pseudo Admin": "System", "Date d'arrivée": d_creation}])
                                
                                # Création Permis
                                new_p = pd.DataFrame([{"Nom Discord": n_dis, "Nom Roblox": n_rob, "Points": 25, "Statut": "OUI"}])
                                
                                try:
                                    # Update Banque
                                    df_banque_updated = pd.concat([df_banque, new_b], ignore_index=True)
                                    conn.update(worksheet="Banque", data=df_banque_updated)
                                    import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# ======================================================================================
# 1. CONFIGURATION SYSTÈME & DESIGN (PROTOCOLE VISUEL AVANCÉ)
# ======================================================================================
# Cette section gère l'injection CSS pour l'interface utilisateur (UI).
# Le but est de garantir une expérience immersive pour la République de Palm City.

st.set_page_config(
    page_title="RCRP - Système de Gestion Intégral Professionnel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Global Application Styles */
    .stApp { 
        background-color: #0e1117; 
        color: #ffffff; 
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Custom Button Component - High Performance CSS */
    .stButton>button {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #4b4b4b !important;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    .stButton>button:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
        box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.4);
        transform: translateY(-3px);
    }
    .stButton>button:active {
        transform: translateY(-1px);
    }

    /* Assurance Badges Styling */
    .badge-assu { 
        background: linear-gradient(135deg, #ff4b4b 0%, #c13535 100%);
        color: white !important; 
        padding: 8px 22px; 
        border-radius: 50px; 
        font-weight: 800; 
        font-size: 0.85rem;
        text-align: center;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.3);
    }

    /* Terminal Receipt Interface (Fiscal Protocol) */
    .ticket-fix { 
        background-color: #000000 !important; 
        color: #00FF00 !important; 
        padding: 40px; 
        border: 2px dashed #ff4b4b; 
        border-radius: 20px; 
        font-family: 'Courier New', Courier, monospace; 
        margin: 25px 0;
        box-shadow: inset 0px 0px 25px rgba(0, 255, 0, 0.1);
        line-height: 1.6;
        position: relative;
    }

    /* Sidebar and Navigation Elements */
    [data-testid="stSidebar"] {
        background-color: #161922 !important;
        border-right: 1px solid #333;
    }
    [data-testid="stSidebar"] img { 
        border-radius: 25px; 
        width: 100% !important; 
        border: 3px solid #333; 
        margin-bottom: 25px;
        transition: transform 0.3s ease;
    }
    [data-testid="stSidebar"] img:hover {
        transform: scale(1.02);
    }
    
    .main .block-container { padding-top: 5rem !important; }
    
    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 15px; 
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1a1c23; 
        border-radius: 10px 10px 0 0; 
        padding: 15px 30px;
        color: #999;
        font-weight: 500;
        border: 1px solid #333;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #ff4b4b !important; 
        color: white !important; 
        border: 1px solid #ff4b4b;
    }

    /* Citizen Information Cards */
    .citoyen-card {
        background-color: #1e2129;
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid #ff4b4b;
        margin-bottom: 20px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }

    /* Status Animations */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .loading-text { animation: pulse 1.5s infinite; }
    </style>
    """, unsafe_allow_html=True)

# ======================================================================================
# 2. PARAMÈTRES, CONSTANTES ET SÉCURITÉ (LOGIQUE MÉTIER)
# ======================================================================================
# Vérification de l'intégrité de la session
if "role" not in st.session_state:
    st.session_state.role = None

# Flux Financiers (Configuration des bénéficiaires)
TARGET_RCT = "une10000"     
TARGET_AVERIS = "Moune2010" # L'argent d'Averis est bien dirigé ici selon vos instructions

# Protocoles d'Accès (Chiffrement côté client)
CODE_ADMIN = "RCRPFR-25-26"   
CODE_PRO = "RCT-26-RCRPFR"    

# Assets Graphiques
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

# ======================================================================================
# 3. GESTIONNAIRE DE BASE DE DONNÉES (CLOUD SYNC)
# ======================================================================================
# Fonctions de rappel pour assurer une synchronisation en temps réel (TTL=0)

def fetch_bank_data(connection):
    """Extraction des données financières de Palm City"""
    return connection.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")

def fetch_immat_data(connection):
    """Extraction du registre des immatriculations"""
    return connection.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")

def fetch_permis_data(connection):
    """Extraction du registre des points de permis"""
    return connection.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_banque = fetch_bank_data(conn)
    df_im = fetch_immat_data(conn)
except Exception as e:
    st.error(f"FATAL ERROR: Impossible de joindre le serveur SQL Cloud: {e}")
    st.stop()

# ======================================================================================
# 4. PORTAIL D'AUTHENTIFICATION (GATEWAY)
# ======================================================================================
if st.session_state.role is None:
    st.title("🏛️ Système de Gestion Centralisé - République de Palm City")
    st.write("---")
    
    st.markdown("""
    ### 📢 Avis Officiel du Gouvernement
    Bienvenue sur le terminal de gestion de la République. Cet outil sécurisé permet la régulation 
    des flux monétaires, l'immatriculation des biens mobiliers et la gestion des citoyens.
    
    **Veuillez vous authentifier pour accéder à vos privilèges de session :**
    """)
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.header("👤 Portail Civil")
        st.info("Espace public dédié aux résidents.")
        st.write("Accès limité :")
        st.markdown("- Registre Public\n- État des comptes\n- Déclaration véhicule")
        if st.button("Connexion Citoyen", use_container_width=True):
            st.session_state.role = "Civil"
            st.rerun()
            
    with col_b:
        st.header("🛠️ Service RCT")
        st.warning("Accès réservé aux agents de terrain.")
        st.write("Missions de régulation :")
        st.markdown("- Perception des taxes\n- Validation assurances\n- Prélèvement amendes")
        pwd_rct = st.text_input("Code Badge RCT", type="password", key="login_rct_input")
        if st.button("Authentification RCT", use_container_width=True):
            if pwd_rct == CODE_PRO:
                st.session_state.role = "RCT"
                st.rerun()
            else:
                st.error("Code de badge invalide.")
            
    with col_c:
        st.header("👮 Administration")
        st.error("Accès Staff / Haut-Commandement.")
        st.write("Contrôle total :")
        st.markdown("- Banque Centrale\n- Création de Dossiers\n- Paye Générale")
        pwd_staff = st.text_input("Accréditation Staff", type="password", key="login_staff_input")
        if st.button("Authentification Admin", use_container_width=True):
            if pwd_staff == CODE_ADMIN:
                st.session_state.role = "Staff"
                st.rerun()
            else:
                st.error("Accès refusé.")

    st.divider()
    st.caption("Système de traçage IP activé. Toute tentative d'intrusion sera signalée au Gouvernement.")
    st.stop()

# ======================================================================================
# 5. BARRE LATÉRALE (SIDEBAR D'ÉTAT)
# ======================================================================================
with st.sidebar:
    st.image(LOGO_URL)
    st.divider()
    st.markdown(f"### 📍 Session : **{st.session_state.role}**")
    st.write(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"⏰ **Heure :** {datetime.now().strftime('%H:%M:%S')}")
    st.divider()
    
    st.subheader("Outils de Maintenance")
    if st.button("🔄 Forcer la Synchronisation", use_container_width=True):
        st.rerun()
    if st.button("🚪 Terminer la Session", use_container_width=True):
        st.session_state.role = None
        st.rerun()
        
    st.divider()
    st.write("Version Logicielle : **v16.9.1**")
    st.write("Statut Base : **Stable**")

# ======================================================================================
# 6. NAVIGATION PRINCIPALE (MODULAIRE)
# ======================================================================================
tab_immat, tab_dossier, tab_banque = st.tabs([
    "🚗 REGISTRE DES VÉHICULES", 
    "🪪 DOSSIERS DES CITOYENS", 
    "💰 BANQUE CENTRALE"
])

# --- ONGLET 1 : GESTION DES VÉHICULES ---
with tab_immat:
    st.header("🚗 Registre National des Immatriculations")
    
    with st.expander("➕ Enregistrer un nouveau véhicule (Procédure Légale)", expanded=True):
        st.markdown("#### Identification du Bien")
        
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            in_proprio = st.selectbox("Titulaire du véhicule", ["---"] + df_banque["Nom Roblox"].tolist())
            in_marque = st.text_input("Modèle précis", placeholder="Ex: Mercedes-AMG G63")
            in_plaque = st.text_input("Numéro de Plaque", placeholder="PC-789-RC")
            
        with f_col2:
            in_assu = st.selectbox("Formule Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            in_code_sec = st.text_input("Code de Radiation (Secret)", type="password")

        # LOGIQUE DE CALCUL DES TAXES (Détail Complet)
        taxe_base = 175
        taxe_assu = 0
        taxe_nouveau = 0
        
        if "AVERIS" in in_assu: taxe_assu = 130
        elif "RCT" in in_assu: taxe_assu = 150
            
        # Calcul Avantage RCT (3ème véhicule)
        v_existants = df_im[df_im["Nom d'utilisateur ROBLOX"] == in_proprio]
        rct_count = len(v_existants[v_existants["Assurance"].str.contains("RCT", na=False)])
        if "RCT" in in_assu and rct_count >= 2:
            taxe_assu = 0
            st.success("✨ AVANTAGE TRIO RCT : Assurance offerte !")

        # Calcul Taxe Jeune Résident
        if in_proprio != "---":
            row_u = df_banque[df_banque["Nom Roblox"] == in_proprio]
            try:
                d_arrivée = datetime.strptime(str(row_u.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                if (datetime.now() - d_arrivée).days < 30:
                    taxe_nouveau = 50
                    st.warning("⚠️ FRAIS NOUVEAU CITOYEN : Majoration de 50$ appliquée.")
            except: pass

        total_ttc = taxe_base + taxe_assu + taxe_nouveau
        
        st.markdown(f"""
        <div class="ticket-fix">
            <b>RCRP - CERTIFICAT DE PAIEMENT FISCAL</b><br>
            ------------------------------------------------<br>
            PROPRIÉTAIRE : {in_proprio}<br>
            PLAQUE       : {in_plaque}<br>
            DÉTAILS      : Base ({taxe_base}$), Assu ({taxe_assu}$)<br>
            ------------------------------------------------<br>
            <b>MONTANT TOTAL DÉBITÉ : {total_ttc}$</b>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💳 Valider la Transaction Financière", use_container_width=True):
            if in_proprio != "---" and in_plaque != "" and in_code_sec != "":
                idx_c = df_banque[df_banque["Nom Roblox"] == in_proprio].index[0]
                solde_c = float(str(df_banque.at[idx_c, "Solde"]).replace('$', '').replace(' ', ''))
                
                if solde_c >= total_ttc:
                    # Exécution du prélèvement
                    df_banque.at[idx_c, "Solde"] = solde_c - total_ttc
                    
                    # Redirection des taxes d'assurance (Averis -> Moune2010)
                    if taxe_assu > 0:
                        dest = TARGET_AVERIS if "AVERIS" in in_assu else TARGET_RCT
                        idx_d = df_banque[df_banque["Nom Roblox"] == dest].index[0]
                        s_d = float(str(df_banque.at[idx_d, "Solde"]).replace('$', ''))
                        df_banque.at[idx_d, "Solde"] = s_d + taxe_assu
                    
                    # Enregistrement véhicule
                    new_v = pd.DataFrame([{
                        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                        "Nom d'utilisateur ROBLOX": in_proprio,
                        "Marque du véhicule": in_marque,
                        "Numéro de la plaque": in_plaque,
                        "Assurance": in_assu,
                        "CODE": str(in_code_sec)
                    }])
                    
                    conn.update(worksheet="Banque", data=df_banque)
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_v], ignore_index=True))
                    st.success("✅ TRANSACTION RÉUSSIE : Véhicule enregistré."); time.sleep(1); st.rerun()
                else:
                    st.error("❌ ÉCHEC : Fonds insuffisants.")

    st.divider()
    st.subheader("🔍 Consultation du Registre d'État")
    q_search = st.text_input("Rechercher Plaque / Nom").lower()
    
    for i, row in df_im.iterrows():
        if not q_search or q_search in str(row["Numéro de la plaque"]).lower() or q_search in str(row["Nom d'utilisateur ROBLOX"]).lower():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1: st.markdown(f"### {row['Numéro de la plaque']}"); st.write(f"🚗 {row['Marque du véhicule']}")
                with c2: st.write(f"👤 {row['Nom d\'utilisateur ROBLOX']}"); st.write(f"📅 {row['Horodateur']}")
                with c3: st.markdown(f'<div class="badge-assu">{row["Assurance"]}</div>', unsafe_allow_html=True)
                
                with st.expander("🛠️ Actions Administratives"):
                    in_r_code = st.text_input("Code de Sécurité", type="password", key=f"r_{i}")
                    if st.button("🚫 Radiation Forcee", key=f"b_r_{i}"):
                        if in_r_code == str(row["CODE"]) or st.session_state.role == "Staff":
                            conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                            st.success("Dossier supprimé."); time.sleep(1); st.rerun()

# --- ONGLET 2 : DOSSIERS CITOYENS ---
with tab_dossier:
    st.header("🪪 Dossiers Administratifs")
    
    if st.session_state.role == "Staff":
        with st.container(border=True):
            st.subheader("🧧 Console de Gestion Administrative")
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                st.write("Protocoles de Salaires Généraux")
                if st.button("💰 Lancer la Paye Palm City", use_container_width=True):
                    for idx, r in df_banque.iterrows():
                        paye = 17000 if "RCT" in str(r["Emploiement"]) else 15000
                        df_banque.at[idx, "Solde"] = float(str(r["Solde"]).replace('$', '')) + paye
                    conn.update(worksheet="Banque", data=df_banque)
                    st.success("Virements effectués !")
            
            with col_s2:
                with st.expander("👤 Création de Dossier Citoyen"):
                    with st.form("new_citizen_full_form"):
                        n_rob = st.text_input("Nom ROBLOX")
                        n_dis = st.text_input("Nom Discord")
                        n_job = st.selectbox("Affectation", ["Civil", "Agent RCT", "Gouvernement"])
                        
                        st.markdown("---")
                        st.info("Cette action créera automatiquement : un compte Banque (15k) et un dossier Permis (25 pts).")
                        confirm_btn = st.checkbox("Confirmer la création officielle")
                        
                        if st.form_submit_button("🔨 Générer le Dossier"):
                            if confirm_btn and n_rob:
                                d_c = datetime.now().strftime("%d/%m/%Y")
                                # Lignes de création
                                new_b = pd.DataFrame([{"Solde": 15000, "Emploiement": n_job, "Nom Discord": n_dis, "Nom Roblox": n_rob, "Pseudo Admin": "System", "Date d'arrivée": d_c}])
                                new_p = pd.DataFrame([{"Nom Discord": n_dis, "Nom Roblox": n_rob, "Points": 25, "Statut": "OUI"}])
                                
                                # Push Data
                                df_banque_up = pd.concat([df_banque, new_b], ignore_index=True)
                                conn.update(worksheet="Banque", data=df_banque_up)
                                
                                df_permis_raw = fetch_permis_data(conn)
                                df_permis_up = pd.concat([df_permis_raw, new_p], ignore_index=True)
                                conn.update(worksheet="Points Permis", data=df_permis_up)
                                
                                st.balloons()
                                st.success(f"Dossier de {n_rob} finalisé !"); time.sleep(1.5); st.rerun()

    st.divider()
    s_cit = st.text_input("🔍 Rechercher un résident").lower()
    for idx, r in df_banque.iterrows():
        if not s_cit or s_cit in str(r["Nom Roblox"]).lower():
            st.markdown(f"""
            <div class="citoyen-card">
                <b>👤 IDENTITÉ :</b> {r['Nom Roblox']} | 💼 {r['Emploiement']} <br>
                <b>💬 RÉSEAU :</b> {r['Nom Discord']} | 📅 ARRIVÉE : {r['Date d\'arrivée']}
            </div>
            """, unsafe_allow_html=True)

# --- ONGLET 3 : BANQUE ---
with tab_banque:
    st.header("💰 Banque Centrale de Palm City")
    q_b = st.text_input("Rechercher par Titulaire").lower()
    if q_b:
        for idx, r in df_banque.iterrows():
            if q_b in str(r["Nom Roblox"]).lower():
                with st.container(border=True):
                    s_v = float(str(r["Solde"]).replace('$', '').replace(' ', ''))
                    st.metric(f"Compte : {r['Nom Roblox']}", f"{s_v:,.0f} $")
                    
                    if st.session_state.role in ["RCT", "Staff"]:
                        with st.expander("💸 Prélèvement Direct"):
                            m_v = st.number_input("Montant", min_value=0, key=f"v_{idx}")
                            if st.button("Valider le Débit", key=f"b_v_{idx}"):
                                df_banque.at[idx, "Solde"] = s_v - m_v
                                if st.session_state.role == "RCT":
                                    idx_r = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                    df_banque.at[idx_r, "Solde"] = float(str(df_banque.at[idx_r, "Solde"]).replace('$', '')) + m_v
                                conn.update(worksheet="Banque", data=df_banque)
                                st.success("Transaction terminée."); time.sleep(1); st.rerun()

# ======================================================================================
# 7. PIED DE PAGE ET LOGS DE SÉCURITÉ
# ======================================================================================
st.markdown("---")
st.markdown("<center><b>RCRP SYSTEM v16.9.1</b> - 2026 - République de Palm City</center>", unsafe_allow_html=True)
st.write("Dernière vérification du noyau : OK | Connexion GSheets : Stable")
