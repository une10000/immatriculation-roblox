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

# Identifiants de redirection de fonds
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010" # Argent d'Averis redirigé ici

# Codes d'accès
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"

# Ressources visuelles
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

# ======================================================================================
# 3. GESTION DES DONNÉES (GOOGLE SHEETS)
# ======================================================================================
def fetch_bank_data(connection):
    """Récupère les données de la feuille Banque"""
    return connection.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")

def fetch_immat_data(connection):
    """Récupère les données de la feuille Immatriculations"""
    return connection.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_banque = fetch_bank_data(conn)
    df_im = fetch_immat_data(conn)
except Exception as e:
    st.error(f"⚠️ Erreur de liaison système : {e}")
    st.info("Vérifiez la configuration de votre fichier secrets.toml")
    st.stop()

# ======================================================================================
# 4. PORTAIL D'AUTHENTIFICATION (ACCUEIL COMPLET)
# ======================================================================================
if st.session_state.role is None:
    st.title("🏛️ Système de Gestion Centralisé - Rensselaer County Roleplay FR")
    st.write("---")
    
    # Message d'accueil informatif
    st.markdown("""
    ### 📢 Avis Officiel du Gouvernement
    Bienvenue sur le terminal de gestion de la République. Cet outil permet la régulation 
    des flux monétaires, l'immatriculation des biens mobiliers et la gestion des citoyens.
    
    **Veuillez vous identifier pour accéder à vos privilèges :**
    """)
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.header("👤 Portail Civil")
        st.info("Ouvert à tous les résidents.")
        st.write("""
        - Consulter le registre des véhicules
        - Déclarer une nouvelle immatriculation
        - Vérifier l'état de ses comptes
        """)
        if st.button("Connexion Citoyen", use_container_width=True):
            st.session_state.role = "Civil"
            st.rerun()
            
    with col_b:
        st.header("🛠️ Service RCT")
        st.warning("Accès Agents de la Régie.")
        st.write("""
        - Perception des taxes d'immatriculation
        - Validation des contrats d'assurance
        - Gestion des amendes routières
        """)
        pwd_rct = st.text_input("Code Agent RCT", type="password", key="login_rct")
        if st.button("Authentification RCT", use_container_width=True):
            if pwd_rct == CODE_PRO:
                st.session_state.role = "RCT"
                st.rerun()
            else:
                st.error("Accès refusé : Code incorrect.")
            
    with col_c:
        st.header("👮 Administration")
        st.error("Accès Staff / Gouvernement.")
        st.write("""
        - Gestion de la Banque Centrale
        - Création de nouveaux dossiers
        - Radiation administrative forcée
        - Exécution des salaires généraux
        """)
        pwd_staff = st.text_input("Code Administrateur", type="password", key="login_staff")
        if st.button("Authentification Admin", use_container_width=True):
            if pwd_staff == CODE_ADMIN:
                st.session_state.role = "Staff"
                st.rerun()
            else:
                st.error("Accès refusé : Accréditation insuffisante.")

    st.divider()
    st.caption("© 2026 RCRP FR - Système de traçage IP activé.")
    st.stop()

# ======================================================================================
# 5. BARRE LATÉRALE (SIDEBAR DÉTAILLÉE)
# ======================================================================================
with st.sidebar:
    st.image(LOGO_URL)
    st.divider()
    st.markdown(f"### 📍 Session : **{st.session_state.role}**")
    st.write(f"📅 **Date du jour :** {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"⏰ **Heure locale :** {datetime.now().strftime('%H:%M:%S')}")
    st.divider()
    st.subheader("Options de session")
    if st.button("🔄 Synchroniser les données", use_container_width=True):
        st.rerun()
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    st.divider()
    st.write("Serveur : **RCRP-FR-01**")

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
    
    # SECTION A : FORMULAIRE D'ENREGISTREMENT
    with st.expander("➕ Enregistrer un nouveau véhicule (Procédure Légale)", expanded=True):
        st.write("Veuillez remplir tous les champs pour générer la facture.")
        
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            in_proprio = st.selectbox("Titulaire du véhicule", ["---"] + df_banque["Nom Roblox"].tolist())
            in_marque = st.text_input("Marque et Modèle précis", placeholder="Ex: Audi RS6 Avant")
            in_plaque = st.text_input("Plaque d'immatriculation", placeholder="RC-123-RP")
            
        with f_col2:
            in_assu = st.selectbox("Contrat d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            in_code_sec = st.text_input("Code Secret de Sécurité", type="password", help="Ce code sera demandé pour toute radiation future.")

        # LOGIQUE DE CALCUL DES TAXES (Détail complet)
        taxe_base = 175
        taxe_assu = 0
        taxe_nouveau = 0
        
        # Calcul assurance
        if "AVERIS" in in_assu:
            taxe_assu = 130
        elif "RCT" in in_assu:
            taxe_assu = 150
            
        # Offre Trio RCT (3ème véhicule assurance gratuite)
        v_existants = df_im[df_im["Nom d'utilisateur ROBLOX"] == in_proprio]
        rct_count = len(v_existants[v_existants["Assurance"].str.contains("RCT", na=False)])
        if "RCT" in in_assu and rct_count >= 2:
            taxe_assu = 0
            st.success("✨ Avantage RCT : 3ème véhicule assuré gratuitement !")

        # Taxe Jeune Citoyen (-30 jours)
        if in_proprio != "---":
            row_u = df_banque[df_banque["Nom Roblox"] == in_proprio]
            try:
                d_arrivée = datetime.strptime(str(row_u.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                if (datetime.now() - d_arrivée).days < 30:
                    taxe_nouveau = 50
                    st.warning("⚠️ Taxe Nouveau Citoyen : +50$ (Inscrit depuis moins de 30 jours)")
            except:
                pass

        total_ttc = taxe_base + taxe_assu + taxe_nouveau
        
        # Affichage Facture
        st.markdown(f"""
        <div class="ticket-fix">
            <b>RCRP - FACTURE OFFICIELLE D'IMMATRICULATION</b><br>
            ------------------------------------------<br>
            PROPRIÉTAIRE : {in_proprio}<br>
            VÉHICULE     : {in_marque}<br>
            PLAQUE       : {in_plaque}<br>
            ------------------------------------------<br>
            FRAIS DE DOSSIER : {taxe_base}$<br>
            ASSURANCE        : {taxe_assu}$<br>
            TAXE JEUNE PERMIS   : {taxe_nouveau}$<br>
            ------------------------------------------<br>
            <b>TOTAL À RÉGLER : {total_ttc}$</b>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💳 Valider la Transaction et l'Enregistrement", use_container_width=True):
            if in_proprio != "---" and in_plaque != "" and in_code_sec != "":
                # Recherche du compte bancaire
                idx_citoyen = df_banque[df_banque["Nom Roblox"] == in_proprio].index[0]
                solde_actuel = float(str(df_banque.at[idx_citoyen, "Solde"]).replace('$', '').replace(' ', ''))
                
                if solde_actuel >= total_ttc:
                    # 1. Débiter le citoyen
                    df_banque.at[idx_citoyen, "Solde"] = solde_actuel - total_ttc
                    
                    # 2. Créditer l'assurance (Moune2010 pour Averis)
                    if taxe_assu > 0:
                        desti = TARGET_AVERIS if "AVERIS" in in_assu else TARGET_RCT
                        idx_dest = df_banque[df_banque["Nom Roblox"] == desti].index[0]
                        s_dest = float(str(df_banque.at[idx_dest, "Solde"]).replace('$', '').replace(' ', ''))
                        df_banque.at[idx_dest, "Solde"] = s_dest + taxe_assu
                    
                    # 3. Créer la ligne véhicule
                    new_vehicule = pd.DataFrame([{
                        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                        "Nom d'utilisateur ROBLOX": in_proprio,
                        "Marque du véhicule": in_marque,
                        "Numéro de la plaque": in_plaque,
                        "Assurance": in_assu,
                        "CODE": str(in_code_sec)
                    }])
                    
                    # 4. Mise à jour des bases
                    conn.update(worksheet="Banque", data=df_banque)
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_vehicule], ignore_index=True))
                    
                    st.success("✅ Enregistrement terminé avec succès !")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("❌ Erreur : Solde bancaire insuffisant.")
            else:
                st.error("❌ Erreur : Veuillez remplir tous les champs obligatoires.")

    st.divider()
    
    # SECTION B : CONSULTATION ET RECHERCHE
    st.subheader("🔍 Consultation du Registre Public")
    query = st.text_input("Rechercher par Plaque ou par Nom de Propriétaire", key="search_reg").lower()
    
    for i, row in df_im.iterrows():
        if not query or query in str(row["Numéro de la plaque"]).lower() or query in str(row["Nom d'utilisateur ROBLOX"]).lower():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    st.markdown(f"### {row['Numéro de la plaque']}")
                    st.write(f"🚗 **Modèle :** {row['Marque du véhicule']}")
                with c2:
                    st.write(f"👤 **Propriétaire :** {row['Nom d\'utilisateur ROBLOX']}")
                    st.write(f"📅 **Date :** {row['Horodateur']}")
                with c3:
                    st.markdown(f'<div class="badge-assu">{row["Assurance"]}</div>', unsafe_allow_html=True)
                
                # Option de radiation
                with st.expander("⚙️ Options d'administration du véhicule"):
                    in_rad_code = st.text_input("Code de Sécurité", type="password", key=f"rad_in_{i}")
                    if st.button("🚫 Demander la Radiation Administrative", key=f"rad_btn_{i}"):
                        if in_rad_code == str(row["CODE"]) or st.session_state.role == "Staff":
                            # Suppression de la ligne
                            df_im_new = df_im.drop(i)
                            conn.update(worksheet="Copie de Immatriculations", data=df_im_new)
                            st.success("✅ Véhicule radié du registre.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Code de sécurité incorrect.")

# --- ONGLET 2 : DOSSIERS CITOYENS ---
with tab_dossier:
    st.header("🪪 Dossiers Administratifs")
    
    if st.session_state.role == "Staff":
        # Bloc Staff de gestion
        with st.container(border=True):
            st.subheader("🧧 Console de Gestion Staff")
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                if st.button("Lancer la Paye Générale (Salaire de Base)", use_container_width=True):
                    for idx, r in df_banque.iterrows():
                        montant_paye = 17000 if "RCT" in str(r["Emploiement"]) else 15000
                        solde_vieux = float(str(r["Solde"]).replace('$', '').replace(' ', ''))
                        df_banque.at[idx, "Solde"] = solde_vieux + montant_paye
                    conn.update(worksheet="Banque", data=df_banque)
                    st.success("💰 Tous les salaires ont été versés.")
            
            with col_s2:
                with st.expander("👤 Créer un nouveau profil citoyen"):
                    with st.form("new_cit_form"):
                        n_rob = st.text_input("Nom Roblox")
                        n_dis = st.text_input("Nom Discord")
                        n_job = st.selectbox("Poste Occupé", ["Civil", "Agent RCT", "Gouvernement"])
                        if st.form_submit_button("Valider la création"):
                            # DATE AUTOMATIQUE DEMANDÉE
                            d_creation = datetime.now().strftime("%d/%m/%Y")
                            new_citizen = pd.DataFrame([{
                                "Solde": 15000, 
                                "Nom Discord": n_dis, 
                                "Nom Roblox": n_rob, 
                                "Date d'arrivée": d_creation, 
                                "Emploiement": n_job
                            }])
                            conn.update(worksheet="Banque", data=pd.concat([df_banque, new_citizen], ignore_index=True))
                            st.success(f"✅ Citoyen enregistré le {d_creation}")
                            st.rerun()

    st.divider()
    
    # Liste des citoyens
    search_cit = st.text_input("Chercher un dossier par Nom Roblox", key="search_cit").lower()
    for idx, r in df_banque.iterrows():
        if not search_cit or search_cit in str(r["Nom Roblox"]).lower():
            with st.container(border=True):
                cd1, cd2 = st.columns(2)
                cd1.write(f"👤 **Nom Roblox :** {r['Nom Roblox']}")
                cd1.write(f"💬 **Discord :** {r['Nom Discord']}")
                cd2.write(f"💼 **Métier :** {r['Emploiement']}")
                cd2.write(f"📅 **Arrivée :** {r['Date d\'arrivée']}")

# --- ONGLET 3 : BANQUE ---
with tab_banque:
    st.header("💰 Gestion de la Banque Centrale")
    
    search_bank = st.text_input("🔍 Rechercher un compte bancaire par Nom", key="search_bank").lower()
    
    if search_bank:
        for idx, r in df_banque.iterrows():
            if search_bank in str(r["Nom Roblox"]).lower():
                with st.container(border=True):
                    val_solde = float(str(r["Solde"]).replace('$', '').replace(' ', ''))
                    st.metric(f"Compte de {r['Nom Roblox']}", f"{val_solde:,.0f} $")
                    
                    # Actions pour Staff et RCT
                    if st.session_state.role in ["RCT", "Staff"]:
                        with st.expander("💸 Effectuer une transaction (Amende / Prélèvement)"):
                            m_prelevement = st.number_input("Montant à retirer ($)", min_value=0, key=f"prel_{idx}")
                            if st.button("Confirmer le prélèvement", key=f"btn_prel_{idx}"):
                                # Débit citoyen
                                df_banque.at[idx, "Solde"] = val_solde - m_prelevement
                                
                                # Si c'est un agent RCT, l'argent va au compte gouvernemental RCT
                                if st.session_state.role == "RCT":
                                    idx_rct = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                    s_rct = float(str(df_banque.at[idx_rct, "Solde"]).replace('$', '').replace(' ', ''))
                                    df_banque.at[idx_rct, "Solde"] = s_rct + m_prelevement
                                
                                conn.update(worksheet="Banque", data=df_banque)
                                st.success("✅ Opération bancaire réussie.")
                                time.sleep(1)
                                st.rerun()

st.markdown("---")
st.markdown("<center><b>RCRP SYSTEM v16.7</b> - Interface Rensselaer County Roleplay FR</center>", unsafe_allow_html=True)
