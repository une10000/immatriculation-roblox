import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# ======================================================================================
# 1. CONFIGURATION SYSTÈME & DESIGN (CSS ÉTENDU & PERSONNALISÉ)
# ======================================================================================
# Cette section définit l'apparence visuelle de l'application RCRP.
# On utilise du HTML/CSS injecté pour contourner les limitations de Streamlit.

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
    </style>
    """, unsafe_allow_html=True)

# ======================================================================================
# 2. PARAMÈTRES, CONSTANTES ET SÉCURITÉ
# ======================================================================================
# Initialisation de l'état de la session (Auth)
if "role" not in st.session_state:
    st.session_state.role = None

# Identifiants de redirection des fonds pour les taxes d'assurance
TARGET_RCT = "une10000"     # Compte gouvernemental pour l'assurance RCT
TARGET_AVERIS = "Moune2010" # Compte de redirection pour l'assurance AVERIS

# Codes d'accès sécurisés (À changer régulièrement)
CODE_ADMIN = "RCRPFR-25-26"   # Code pour le rôle Staff
CODE_PRO = "RCT-26-RCRPFR"    # Code pour le rôle Agent RCT

# Logo officiel du projet
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
        st.error(f"Erreur de lecture Banque: {e}")
        return pd.DataFrame()

def fetch_immat_data(connection):
    """Extraction sécurisée des données de l'onglet Immatriculations"""
    try:
        data = connection.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
        return data
    except Exception as e:
        st.error(f"Erreur de lecture Immat: {e}")
        return pd.DataFrame()

# Établissement de la connexion principale
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_banque = fetch_bank_data(conn)
    df_im = fetch_immat_data(conn)
except Exception as e:
    st.error(f"⚠️ ÉCHEC DE LA CONNEXION AU SERVEUR DE DONNÉES : {e}")
    st.info("Action requise : Vérifiez vos secrets Streamlit et les permissions Google Sheets.")
    st.stop()

# ======================================================================================
# 4. PORTAIL D'AUTHENTIFICATION CENTRALISÉ (ACCUEIL)
# ======================================================================================
if st.session_state.role is None:
    st.title("🏛️ Système de Gestion Centralisé - République de Palm City")
    st.write("---")
    
    st.markdown("""
    ### 📢 Avis Officiel du Gouvernement
    Bienvenue sur le terminal de gestion de la République. Cet outil permet la régulation 
    des flux monétaires, l'immatriculation des biens mobiliers et la gestion des citoyens.
    
    **Veuillez vous identifier pour accéder à vos privilèges de session :**
    """)
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.header("👤 Portail Civil")
        st.info("Accès standard pour les résidents.")
        st.markdown("""
        * Consulter le registre des véhicules
        * Déclarer une nouvelle immatriculation
        * Vérifier l'état de ses comptes bancaires
        * Accès aux informations publiques
        """)
        if st.button("Connexion Citoyen", key="btn_civil"):
            st.session_state.role = "Civil"
            st.rerun()
            
    with col_b:
        st.header("🛠️ Service RCT")
        st.warning("Accès réservé aux Agents de la Régie.")
        st.markdown("""
        * Perception des taxes d'immatriculation
        * Validation des contrats d'assurance
        * Gestion et prélèvement des amendes
        * Suivi des activités de transport
        """)
        pwd_rct = st.text_input("Code Agent RCT", type="password", key="login_rct_input")
        if st.button("Authentification RCT", key="btn_rct"):
            if pwd_rct == CODE_PRO:
                st.session_state.role = "RCT"
                st.rerun()
            else:
                st.error("Accès refusé : Code agent invalide.")
            
    with col_c:
        st.header("👮 Administration")
        st.error("Accès restreint au Haut-Commandement.")
        st.markdown("""
        * Gestion de la Banque Centrale de Palm City
        * Création et modification des profils citoyens
        * Radiation administrative forcée des véhicules
        * Exécution des protocoles de salaires (Paye)
        """)
        pwd_staff = st.text_input("Code Administrateur", type="password", key="login_staff_input")
        if st.button("Authentification Admin", key="btn_staff"):
            if pwd_staff == CODE_ADMIN:
                st.session_state.role = "Staff"
                st.rerun()
            else:
                st.error("Accès refusé : Accréditation insuffisante.")

    st.divider()
    st.caption("© 2026 Palm City Government - Système sécurisé par cryptage RSA-2048.")
    st.stop()

# ======================================================================================
# 5. CONFIGURATION DE LA BARRE LATÉRALE (SIDEBAR)
# ======================================================================================
with st.sidebar:
    st.image(LOGO_URL)
    st.divider()
    st.markdown(f"### 💠 État du Système")
    st.info(f"Session active : **{st.session_state.role}**")
    
    st.markdown("---")
    st.write(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"⏰ **Heure :** {datetime.now().strftime('%H:%M:%S')}")
    st.write(f"🌍 **Zone :** Palm City Central")
    
    st.markdown("---")
    st.subheader("Paramètres de session")
    if st.button("🔄 Actualiser les données", use_container_width=True):
        st.rerun()
    if st.button("🚪 Fermer la session", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    
    st.divider()
    st.write("Serveur Principal : **RCRP-FR-NODE-01**")
    st.write("Statut : **Connecté**")

# ======================================================================================
# 6. NAVIGATION PRINCIPALE (ONGLETS DE GESTION)
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
        st.markdown("#### Formulaire d'Immatriculation")
        st.write("Le titulaire doit posséder les fonds nécessaires sur son compte bancaire.")
        
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            in_proprio = st.selectbox("Titulaire du véhicule", ["---"] + df_banque["Nom Roblox"].tolist())
            in_marque = st.text_input("Marque et Modèle du véhicule", placeholder="Ex: Mercedes-Benz Classe G")
            in_plaque = st.text_input("Plaque d'immatriculation", placeholder="PC-456-RC")
            
        with f_col2:
            in_assu = st.selectbox("Contrat d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            in_code_sec = st.text_input("Code Secret de Sécurité", type="password", help="Obligatoire pour radier le véhicule plus tard.")

        # LOGIQUE DE CALCUL DES TAXES (DÉTAILLÉE)
        taxe_base = 175 # Frais fixes administratifs
        taxe_assu = 0
        taxe_nouveau = 0
        
        # Calcul de la prime d'assurance
        if "AVERIS" in in_assu: taxe_assu = 130
        elif "RCT" in in_assu: taxe_assu = 150
            
        # Algorithme Avantage RCT : Le 3ème véhicule avec assurance RCT est gratuit
        v_existants = df_im[df_im["Nom d'utilisateur ROBLOX"] == in_proprio]
        rct_count = len(v_existants[v_existants["Assurance"].str.contains("RCT", na=False)])
        if "RCT" in in_assu and rct_count >= 2:
            taxe_assu = 0
            st.success("✨ AVANTAGE FIDÉLITÉ : Ce véhicule bénéficie de la gratuité RCT !")

        # Calcul de la taxe de résidence pour les nouveaux arrivants
        if in_proprio != "---":
            row_u = df_banque[df_banque["Nom Roblox"] == in_proprio]
            try:
                date_str = str(row_u.iloc[0]["Date d'arrivée"])
                d_arrivée = datetime.strptime(date_str, "%d/%m/%Y")
                if (datetime.now() - d_arrivée).days < 30:
                    taxe_nouveau = 50
                    st.warning("⚠️ TAXE NOUVEAU CITOYEN : Majoration de 50$ appliquée.")
            except: pass

        total_ttc = taxe_base + taxe_assu + taxe_nouveau
        
        # Affichage de la Facture Format Ticket
        st.markdown(f"""
        <div class="ticket-fix">
            <b>RCRP - FACTURE OFFICIELLE D'IMMATRICULATION</b><br>
            ------------------------------------------------<br>
            CITOYEN      : {in_proprio}<br>
            VÉHICULE     : {in_marque}<br>
            PLAQUE       : {in_plaque}<br>
            ------------------------------------------------<br>
            DÉTAIL DES FRAIS :<br>
            - Frais de Dossier Standard : {taxe_base}$<br>
            - Prime d'Assurance Sélectionnée : {taxe_assu}$<br>
            - Taxe de Résidence (<30j) : {taxe_nouveau}$<br>
            ------------------------------------------------<br>
            <b>MONTANT TOTAL TTC : {total_ttc}$</b><br>
            ------------------------------------------------<br>
            <i>Paiement sécurisé par prélèvement bancaire direct.</i>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💳 Valider la Transaction et l'Enregistrement", key="btn_submit_immat"):
            if in_proprio != "---" and in_plaque != "" and in_code_sec != "":
                idx_c = df_banque[df_banque["Nom Roblox"] == in_proprio].index[0]
                solde_c = float(str(df_banque.at[idx_c, "Solde"]).replace('$', '').replace(' ', ''))
                
                if solde_c >= total_ttc:
                    # Débit du citoyen
                    df_banque.at[idx_c, "Solde"] = solde_c - total_ttc
                    
                    # Crédit vers les comptes de destination (Moune2010 pour Averis)
                    if taxe_assu > 0:
                        dest = TARGET_AVERIS if "AVERIS" in in_assu else TARGET_RCT
                        idx_d = df_banque[df_banque["Nom Roblox"] == dest].index[0]
                        s_d = float(str(df_banque.at[idx_d, "Solde"]).replace('$', '').replace(' ', ''))
                        df_banque.at[idx_d, "Solde"] = s_d + taxe_assu
                    
                    # Création de la nouvelle entrée véhicule
                    new_v = pd.DataFrame([{
                        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                        "Nom d'utilisateur ROBLOX": in_proprio,
                        "Marque du véhicule": in_marque,
                        "Numéro de la plaque": in_plaque,
                        "Assurance": in_assu,
                        "CODE": str(in_code_sec)
                    }])
                    
                    # Mise à jour des bases de données distantes
                    conn.update(worksheet="Banque", data=df_banque)
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_v], ignore_index=True))
                    
                    st.success("✅ TRANSACTION RÉUSSIE : Véhicule enregistré et taxes perçues.")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("❌ ÉCHEC : Fonds insuffisants sur le compte du citoyen.")
            else:
                st.error("❌ ERREUR : Formulaire incomplet.")

    st.divider()
    st.subheader("🔍 Consultation de la Base de Données")
    q_reg = st.text_input("Rechercher par Plaque ou Propriétaire", key="q_reg").lower()
    
    for i, row in df_im.iterrows():
        if not q_reg or q_reg in str(row["Numéro de la plaque"]).lower() or q_reg in str(row["Nom d'utilisateur ROBLOX"]).lower():
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown(f"### {row['Numéro de la plaque']}")
                    st.write(f"🚗 **Véhicule :** {row['Marque du véhicule']}")
                with col2:
                    st.write(f"👤 **Propriétaire :** {row['Nom d\'utilisateur ROBLOX']}")
                    st.write(f"📅 **Enregistré le :** {row['Horodateur']}")
                with col3:
                    st.markdown(f'<div class="badge-assu">{row["Assurance"]}</div>', unsafe_allow_html=True)
                
                with st.expander("⚙️ Gérer l'enregistrement"):
                    c_rad = st.text_input("Entrer le code de sécurité pour radiation", type="password", key=f"rad_c_{i}")
                    if st.button("🚫 Confirmer la Radiation Administrative", key=f"btn_rad_{i}"):
                        if c_rad == str(row["CODE"]) or st.session_state.role == "Staff":
                            df_im_new = df_im.drop(i)
                            conn.update(worksheet="Copie de Immatriculations", data=df_im_new)
                            st.success("✅ RADIATION EFFECTUÉE.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Code secret invalide.")

# --- ONGLET 2 : DOSSIERS CITOYENS ---
with tab_dossier:
    st.header("🪪 Gestion des Dossiers Citoyens")
    
    if st.session_state.role == "Staff":
        with st.container(border=True):
            st.subheader("🧧 Console de Commandement (Staff Only)")
            s_col1, s_col2 = st.columns(2)
            
            with s_col1:
                st.write("Exécution des protocoles financiers globaux.")
                if st.button("💰 Lancer la Paye Générale", use_container_width=True):
                    with st.spinner("Calcul des salaires en cours..."):
                        for idx, r in df_banque.iterrows():
                            # Logique de salaire : RCT = 17k, Civil/Gouv = 15k
                            base_paye = 17000 if "RCT" in str(r["Emploiement"]) else 15000
                            s_vieux = float(str(r["Solde"]).replace('$', '').replace(' ', ''))
                            df_banque.at[idx, "Solde"] = s_vieux + base_paye
                        conn.update(worksheet="Banque", data=df_banque)
                        st.success("💳 SALAIRES VERSÉS : Tous les citoyens ont reçu leur virement.")
            
            with s_col2:
                with st.expander("👤 Création de Profil Citoyen"):
                    with st.form("new_cit_form"):
                        st.write("Remplissez les informations d'identité.")
                        n_rob = st.text_input("Nom d'utilisateur ROBLOX")
                        n_dis = st.text_input("Nom Discord")
                        n_job = st.selectbox("Affectation / Poste", ["Civil", "Agent RCT", "Gouvernement"])
                        
                        # VALIDATION DU FORMULAIRE
                        submit_cit = st.form_submit_button("🔨 Créer le dossier")
                        
                        if submit_cit:
                            # Date automatique de création (Sauvegarde utilisateur)
                            d_creation = datetime.now().strftime("%d/%m/%Y")
                            
                            # Préparation Banque (15 000 $)
                            new_b = pd.DataFrame([{
                                "Solde": 15000, 
                                "Emploiement": n_job,
                                "Nom Discord": n_dis, 
                                "Nom Roblox": n_rob, 
                                "Pseudo Admin": "System",
                                "Date d'arrivée": d_creation
                            }])
                            
                            # Préparation Permis (25 Points)
                            new_p = pd.DataFrame([{
                                "Nom Discord": n_dis,
                                "Nom Roblox": n_rob,
                                "Points": 25,
                                "Statut": "OUI"
                            }])
                            
                            try:
                                # Update Banque
                                df_b_up = pd.concat([df_banque, new_b], ignore_index=True)
                                conn.update(worksheet="Banque", data=df_b_up)
                                
                                # Update Points Permis
                                df_p = conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
                                df_p_up = pd.concat([df_p, new_p], ignore_index=True)
                                conn.update(worksheet="Points Permis", data=df_p_up)
                                
                                st.success(f"✅ DOSSIER CRÉÉ : {n_rob} a reçu ses 15k $ et ses 25 points.")
                                time.sleep(1.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ ERREUR API : {e}")

    st.divider()
    st.subheader("📋 Liste des Résidents Enregistrés")
    q_cit = st.text_input("Rechercher un citoyen", key="q_cit").lower()
    
    for idx, r in df_banque.iterrows():
        if not q_cit or q_cit in str(r["Nom Roblox"]).lower():
            # Affichage via une classe CSS personnalisée (citoyen-card)
            st.markdown(f"""
            <div class="citoyen-card">
                <b>👤 NOM ROBLOX :</b> {r['Nom Roblox']} <br>
                <b>💬 DISCORD :</b> {r['Nom Discord']} <br>
                <b>💼 POSTE :</b> {r['Emploiement']} <br>
                <b>📅 ARRIVÉE :</b> {r['Date d\'arrivée']}
            </div>
            """, unsafe_allow_html=True)

# --- ONGLET 3 : BANQUE ---
with tab_banque:
    st.header("💰 Gestion de la Banque Centrale")
    st.write("Interface de contrôle des flux monétaires et prélèvements.")
    
    q_bank = st.text_input("🔍 Rechercher un compte par nom", key="q_bank").lower()
    
    if q_bank:
        for idx, r in df_banque.iterrows():
            if q_bank in str(r["Nom Roblox"]).lower():
                with st.container(border=True):
                    s_actuel = float(str(r["Solde"]).replace('$', '').replace(' ', ''))
                    col_m1, col_m2 = st.columns([1, 1])
                    with col_m1:
                        st.metric(f"Compte de {r['Nom Roblox']}", f"{s_actuel:,.0f} $")
                    
                    # Droits de prélèvement (Staff et RCT uniquement)
                    if st.session_state.role in ["RCT", "Staff"]:
                        with col_m2:
                            with st.expander("💸 Effectuer un prélèvement"):
                                m_prel = st.number_input("Montant à prélever", min_value=0, key=f"val_p_{idx}")
                                if st.button("Confirmer le débit", key=f"btn_p_{idx}"):
                                    # Débit
                                    df_banque.at[idx, "Solde"] = s_actuel - m_prel
                                    # Si RCT, l'argent est redirigé vers le compte Gouvernement
                                    if st.session_state.role == "RCT":
                                        idx_rct = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                        s_rct = float(str(df_banque.at[idx_rct, "Solde"]).replace('$', ''))
                                        df_banque.at[idx_rct, "Solde"] = s_rct + m_prel
                                    
                                    conn.update(worksheet="Banque", data=df_banque)
                                    st.success("✅ TRANSACTION EFFECTUÉE.")
                                    time.sleep(1)
                                    st.rerun()

# ======================================================================================
# 7. PIED DE PAGE ET CRÉDITS
# ======================================================================================
st.markdown("---")
st.markdown("""
    <center>
        <b>RCRP SYSTEM v16.8</b> - Terminal Gouvernemental de la République de Palm City<br>
        Développé pour la gestion automatisée des dossiers et flux bancaires.<br>
        <i>"Sécurité - Progrès - Prospérité"</i>
    </center>
""", unsafe_allow_html=True)
