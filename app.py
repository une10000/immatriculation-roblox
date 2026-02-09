import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# ======================================================================================
# 1. CONFIGURATION SYSTÈME & DESIGN (EXTRÊMEMENT DÉTAILLÉ)
# ======================================================================================
st.set_page_config(
    page_title="RCRP - Système de Gestion Intégral Professionnel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Design immersif pour simuler un terminal gouvernemental
st.markdown("""
    <style>
    /* Fond et texte global */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Boutons stylés */
    .stButton>button {
        background-color: #1e2129 !important;
        color: #ffffff !important;
        border: 1px solid #4b4b4b !important;
        border-radius: 4px;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        border-color: #ff4b4b !important;
        background-color: #262730 !important;
    }

    /* Boîtes de texte informatives */
    .info-box {
        background-color: #161b22;
        border-left: 5px solid #007bff;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }

    /* REÇU D'IMMATRICULATION (EFFET TERMINAL) */
    .receipt-container {
        background-color: #000000 !important;
        color: #00FF00 !important;
        padding: 40px;
        border: 2px dashed #333;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        line-height: 1.2;
        box-shadow: 0px 0px 20px rgba(0, 255, 0, 0.05);
    }
    .receipt-header { text-align: center; border-bottom: 1px solid #00FF00; margin-bottom: 10px; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# ======================================================================================
# 2. LOGIQUE DE CONNEXION ET DONNÉES
# ======================================================================================
if "role" not in st.session_state:
    st.session_state.role = None

TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010" 
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_banque = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
    df_im = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
    df_permis = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
except Exception as e:
    st.error(f"ERREUR SYSTÈME : Liaison Google Sheets interrompue. ({e})")
    st.stop()

# ======================================================================================
# 3. PORTAIL D'ACCÈS (UI PLUS RICHE)
# ======================================================================================
if st.session_state.role is None:
    st.title("🏛️ RENSSELAER COUNTY - SERVICE CENTRAL")
    st.write("Veuillez sélectionner votre terminal d'accès pour continuer.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("👤 Citoyen")
        st.info("Consultez vos soldes, vos points et immatriculez vos véhicules personnels.")
        if st.button("ACCÉDER AU TERMINAL CIVIL"):
            st.session_state.role = "Civil"; st.rerun()

    with col2:
        st.subheader("🛠️ Agent RCT")
        st.warning("Espace réservé aux agents certifiés. Prélèvements et amendes autorisés.")
        pwd_rct = st.text_input("Authentification Agent", type="password")
        if st.button("CONNEXION SERVICE"):
            if pwd_rct == CODE_PRO: st.session_state.role = "RCT"; st.rerun()
            else: st.error("IDENTIFIANT INVALIDE")

    with col3:
        st.subheader("👮 Administration")
        st.error("Accès Gouvernemental. Gestion budgétaire et base de données complète.")
        pwd_staff = st.text_input("Code de Sécurité", type="password")
        if st.button("ACCÈS GOUVERNEMENT"):
            if pwd_staff == CODE_ADMIN: st.session_state.role = "Staff"; st.rerun()
            else: st.error("ACCÈS REFUSÉ")
    st.stop()

# ======================================================================================
# 4. INTERFACE PRINCIPALE (ONGLETS)
# ======================================================================================
with st.sidebar:
    st.image(LOGO_URL)
    st.divider()
    st.success(f"Connecté en tant que : {st.session_state.role}")
    st.write(f"📅 Session du : {datetime.now().strftime('%d/%m/%Y')}")
    if st.button("🚪 QUITTER LA SESSION"):
        st.session_state.role = None; st.rerun()

tab_immat, tab_dossier, tab_banque = st.tabs(["🚗 IMMATRICULATIONS", "🪪 REGISTRE CIVIL", "💰 BANQUE & FINANCES"])

# --- ONGLET 1 : IMMATRICULATIONS ---
with tab_immat:
    st.header("🚗 Service National des Immatriculations")
    st.markdown("""
    <div class="info-box">
    <b>Note informative :</b> L'immatriculation d'un véhicule est obligatoire. 
    Une taxe fixe de <b>175$</b> est appliquée, à laquelle s'ajoute le montant de l'assurance choisie.
    </div>
    """, unsafe_allow_html=True)

    col_v1, col_v2 = st.columns([1, 1.2])
    
    with col_v1:
        with st.form("form_immat"):
            st.subheader("📝 Nouveau Dossier")
            in_proprio = st.selectbox("Titulaire du véhicule", ["---"] + df_banque["Nom Roblox"].tolist())
            in_marque = st.text_input("Marque et Modèle")
            in_plaque = st.text_input("Numéro de Plaque (Ex: RC-888-FR)")
            in_assu = st.selectbox("Option Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            in_code_sec = st.text_input("Code Secret de Radiation", type="password", help="Ce code sera demandé pour supprimer le véhicule plus tard.")
            
            taxe_base = 175
            taxe_assu = 130 if "AVERIS" in in_assu else (150 if "RCT" in in_assu else 0)
            
            # Offre Trio
            v_existants = df_im[df_im["Nom d'utilisateur ROBLOX"] == in_proprio]
            if "RCT" in in_assu and len(v_existants[v_existants["Assurance"].str.contains("RCT", na=False)]) >= 2:
                taxe_assu = 0; st.success("✨ OFFRE TRIO : Assurance 0$ !")

            total = taxe_base + taxe_assu
            
            if st.form_submit_button("VALIDER L'ACHAT"):
                if in_proprio == "---" or not in_plaque or not in_code_sec:
                    st.error("❌ DOSSIER INCOMPLET : Veuillez remplir tous les champs.")
                else:
                    idx = df_banque[df_banque["Nom Roblox"] == in_proprio].index[0]
                    solde = float(str(df_banque.at[idx, "Solde"]).replace('$', ''))
                    if solde >= total:
                        # Transaction
                        df_banque.at[idx, "Solde"] = solde - total
                        if taxe_assu > 0:
                            dest = TARGET_AVERIS if "AVERIS" in in_assu else TARGET_RCT
                            idx_d = df_banque[df_banque["Nom Roblox"] == dest].index[0]
                            df_banque.at[idx_d, "Solde"] = float(str(df_banque.at[idx_d, "Solde"]).replace('$', '')) + taxe_assu
                        
                        new_v = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y"), "Nom d'utilisateur ROBLOX": in_proprio, "Marque du véhicule": in_marque, "Numéro de la plaque": in_plaque, "Assurance": in_assu, "CODE": str(in_code_sec)}])
                        conn.update(worksheet="Banque", data=df_banque)
                        conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_v], ignore_index=True))
                        st.session_state.last_receipt = {"proprio": in_proprio, "marque": in_marque, "plaque": in_plaque, "total": total, "date": datetime.now().strftime("%d/%m/%Y %H:%M")}
                        st.success("✅ TRANSACTION RÉUSSIE"); st.rerun()
                    else:
                        st.error(f"❌ FONDS INSUFFISANTS : Il manque {total - solde}$ sur le compte.")

    with col_v2:
        st.subheader("🧾 Reçu de Transaction")
        if "last_receipt" in st.session_state:
            res = st.session_state.last_receipt
            st.markdown(f"""
            <div class="receipt-container">
                <div class="receipt-header">RENSSELAER COUNTY - DÉPARTEMENT VÉHICULES</div>
                <br>DATE : {res['date']}
                <br>TITULAIRE : {res['proprio']}
                <br>VÉHICULE  : {res['marque']}
                <br>PLAQUE    : {res['plaque']}
                <br>----------------------------------
                <br>TAXE ADMINISTRATIVE : 175$
                <br>TAXE ASSURANCE      : {res['total'] - 175}$
                <br>TOTAL PAYÉ          : {res['total']}$
                <br>----------------------------------
                <br>MERCI DE VOTRE CONTRIBUTION.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.write("Aucune transaction récente à afficher.")

    st.divider()
    st.subheader("🔎 Gestion des plaques actives")
    search = st.text_input("Filtrer par plaque :").upper()
    for i, row in df_im.iterrows():
        if not search or search in str(row["Numéro de la plaque"]).upper():
            with st.expander(f"⚙️ {row['Numéro de la plaque']} - {row['Nom d\'utilisateur ROBLOX']}"):
                st.write(f"Modèle : {row['Marque du véhicule']} | Assurance : {row['Assurance']}")
                pwd_check = st.text_input("Entrez le code secret pour supprimer :", type="password", key=f"p_{i}")
                if pwd_check == str(row["CODE"]) or st.session_state.role == "Staff":
                    if st.button("🗑️ RADIER LE VÉHICULE", key=f"del_{i}"):
                        conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                        st.success("VÉHICULE EFFACÉ"); time.sleep(1); st.rerun()

# --- ONGLET 2 : DOSSIERS (CREATION + PAIE) ---
with tab_dossier:
    st.header("🪪 Registre des Citoyens")
    
    if st.session_state.role == "Staff":
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            st.subheader("💰 Administration Budgétaire")
            st.info("Cette action versera automatiquement 17k aux agents RCT et 15k aux civils.")
            if st.button("🏦 DÉCLENCHER LA PAIE GÉNÉRALE", use_container_width=True):
                for i, r in df_banque.iterrows():
                    p = 17000 if "RCT" in str(r["Emploiement"]) else 15000
                    df_banque.at[i, "Solde"] = float(str(r["Solde"]).replace('$', '')) + p
                conn.update(worksheet="Banque", data=df_banque)
                st.success("✅ OPÉRATION TERMINÉE : Les citoyens ont reçu leur salaire."); time.sleep(1); st.rerun()
        
        with col_s2:
            st.subheader("👤 Enrôlement Nouveau Citoyen")
            st.write("Crée un dossier complet (Banque, Permis, Registre).")
            with st.form("new_cit_form"):
                n_rob = st.text_input("Nom d'utilisateur Roblox")
                n_dis = st.text_input("Identifiant Discord")
                n_job = st.selectbox("Secteur d'activité", ["Civil", "Agent RCT", "Gouvernement"])
                if st.form_submit_button("VÉRIFIER ET CRÉER LE DOSSIER"):
                    if n_rob and n_dis:
                        d_actu = datetime.now().strftime("%d/%m/%Y")
                        # 15 000 $ + 25 PTS + DATE AUTO
                        new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": n_dis, "Nom Roblox": n_rob, "Date d'arrivée": d_actu, "Emploiement": n_job}])
                        new_p = pd.DataFrame([{"Nom Discord": n_dis, "Nom Roblox": n_rob, "PTS": 25, "Validité": "OUI"}])
                        conn.update(worksheet="Banque", data=pd.concat([df_banque, new_b], ignore_index=True))
                        conn.update(worksheet="Points Permis", data=pd.concat([df_permis, new_p], ignore_index=True))
                        st.success(f"✅ DOSSIER CRÉÉ : 15,000$ et 25 points ont été alloués à {n_rob}."); time.sleep(1); st.rerun()
                    else: st.error("ERREUR : Informations manquantes.")

    st.divider()
    st.subheader("📋 Liste des citoyens")
    c_search = st.text_input("Rechercher un dossier :").lower()
    for i, r in df_banque.iterrows():
        if not c_search or c_search in str(r["Nom Roblox"]).lower():
            st.write(f"🆔 {r['Nom Roblox']} | 💼 {r['Emploiement']} | 📅 Entrée : {r['Date d\'arrivée']}")

# --- ONGLET 3 : BANQUE ---
with tab_banque:
    st.header("💰 Système Bancaire Central")
    st.markdown('<p class="info-text">Gestion des flux monétaires et prélèvements officiels.</p>', unsafe_allow_html=True)
    
    b_search = st.text_input("Chercher un compte bancaire :").lower()
    for i, r in df_banque.iterrows():
        if not b_search or b_search in str(r["Nom Roblox"]).lower():
            with st.container(border=True):
                solde = float(str(r["Solde"]).replace('$', ''))
                st.metric(f"Compte de {r['Nom Roblox']}", f"{solde:,.0f} $")
                
                if st.session_state.role in ["RCT", "Staff"]:
                    col_b1, col_b2 = st.columns([2, 1])
                    with col_b1:
                        montant = st.number_input(f"Prélèvement pour {r['Nom Roblox']}", min_value=0, key=f"m_{i}")
                    with col_b2:
                        if st.button("PRÉLEVER", key=f"btn_{i}"):
                            df_banque.at[i, "Solde"] = solde - montant
                            if st.session_state.role == "RCT":
                                idx_r = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                df_banque.at[idx_r, "Solde"] = float(str(df_banque.at[idx_r, "Solde"]).replace('$', '')) + montant
                            conn.update(worksheet="Banque", data=df_banque)
                            st.success("TRANSACTION VALIDÉE"); time.sleep(1); st.rerun()

st.markdown("<center>RCRP OPERATING SYSTEM v18.0 - Système Sécurisé</center>", unsafe_allow_html=True)
