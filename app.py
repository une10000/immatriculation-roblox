# ==============================================================================
# 🏛️ REPUBLIQUE DE CALIFORNIE RP - SYSTEME DE GESTION INTEGRAL (v9.49)
# ==============================================================================
# Développé pour la gestion centralisée des services de l'État et des entreprises.
# Ce script gère : Banque, Permis, Immatriculations, et Transferts RCT.

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION INITIALE DE L'INTERFACE ---
st.set_page_config(
    page_title="RCRP - Portail Officiel de Gestion",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INJECTION DU STYLE CSS PERSONNALISÉ (MODE NUIT & COMPOSANTS) ---
st.markdown("""
    <style>
    /* Ajustement global du conteneur principal */
    .block-container { 
        padding-top: 1.5rem; 
        padding-bottom: 1rem; 
    }
    
    /* Design des boîtes de connexion et des conteneurs d'information */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 25px !important;
        display: flex;
        flex-direction: column;
        height: 580px !important;
        justify-content: space-between;
        box-shadow: 0px 8px 16px rgba(0,0,0,0.2);
    }

    /* Style spécifique pour le Ticket de Caisse RCT / Ville */
    .frais-container-premium {
        background-color: rgba(0, 0, 0, 0.4);
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2ecc71;
        margin-top: 15px;
        margin-bottom: 25px;
        font-family: 'Courier New', Courier, monospace;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }

    /* Personnalisation des métriques (Banque et Permis) */
    .stMetric {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        transition: transform 0.2s;
    }
    .stMetric:hover {
        transform: scale(1.02);
    }

    /* Style du Logo dans la Sidebar */
    [data-testid="stSidebar"] img {
        border-radius: 20px;
        margin-bottom: 25px;
        border: 2px solid rgba(255, 255, 255, 0.1);
        transition: 0.3s;
    }
    [data-testid="stSidebar"] img:hover {
        border: 2px solid #ff4b4b;
    }

    /* Personnalisation des onglets (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
        color: #ccc;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b !important;
        color: white !important;
        font-weight: bold;
    }

    /* Boutons de soumission */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION DE LA PERSISTENCE DE SESSION ---
if "role" not in st.session_state:
    st.session_state.role = None

# --- CONNEXION AUX GOOGLE SHEETS ---
try:
    connection_gsheets = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Impossible d'établir la connexion aux bases de données : {e}")

# --- PARAMÈTRES DE SÉCURITÉ ET IDENTIFIANTS ---
CODE_ACCES_ADMIN_GENERAL = "RCRPFR-25-26" 
CODE_ACCES_ENTREPRISE_RCT = "RCT-26-RCRPFR" 
COMPTE_BANQUE_RCT_CIBLE = "une10000" 

# URL DU LOGO OFFICIEL
URL_LOGO_OFFICIEL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless"

# --- FONCTION DE RÉCUPÉRATION DES DONNÉES ---
def charger_donnees_feuille(nom_de_la_feuille):
    """Récupère les données d'une feuille spécifique avec nettoyage complet."""
    st.cache_data.clear()
    try:
        dataframe_brut = connection_gsheets.read(worksheet=nom_de_la_feuille, ttl=0)
        dataframe_propre = dataframe_brut.dropna(how='all').fillna("")
        return dataframe_propre
    except Exception as erreur_lecture:
        st.error(f"Erreur lors de l'accès à la feuille '{nom_de_la_feuille}' : {erreur_lecture}")
        return pd.DataFrame()

# ==============================================================================
# 🚪 ÉCRAN D'ACCÈS ET D'AUTHENTIFICATION
# ==============================================================================
if st.session_state.role is None:
    st.title("🏛️ Portail des Services de la République de Californie")
    st.markdown("<h4 style='color: #aaaaaa;'>Système de Gestion Gouvernementale & Professionnelle</h4>", unsafe_allow_html=True)
    st.divider()
    
    colonne_civil, colonne_rct, colonne_staff = st.columns(3)
    
    with colonne_civil:
        with st.container(border=True):
            st.markdown("### 👤 Espace Citoyen")
            st.write("Accès public permettant de consulter librement votre solde bancaire, vos points de permis et vos véhicules enregistrés.")
            st.write("---")
            st.info("ℹ️ Aucun code requis pour la consultation publique.")
            if st.button("🔓 Accéder au Portail Public", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()

    with colonne_rct:
        with st.container(border=True):
            st.markdown("### 🛠️ Espace Entreprise (RCT)")
            st.write("Interface réservée aux agents de la RCT pour la gestion des assurances, de la facturation et des clients.")
            st.write("---")
            code_rct_input = st.text_input("Code d'Accès Entreprise", type="password", key="auth_rct_key")
            if st.button("💼 Connexion Professionnelle", use_container_width=True):
                if code_rct_input == CODE_ACCES_ENTREPRISE_RCT:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("❌ Code d'accès invalide.")

    with colonne_staff:
        with st.container(border=True):
            st.markdown("### 👮 Espace Staff / État")
            st.write("Accès de haute sécurité pour l'administration globale : Fichier Central, Banque Centrale et Dossiers Citoyens.")
            st.write("---")
            code_staff_input = st.text_input("Code d'Autorisation Staff", type="password", key="auth_staff_key")
            if st.button("🛡️ Connexion Sécurisée", use_container_width=True):
                if code_staff_input == CODE_ACCES_ADMIN_GENERAL:
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    st.error("❌ Autorisation refusée.")
    
    st.stop()

# ==============================================================================
# 🖥️ DASHBOARD PRINCIPAL (SESSION ACTIVE)
# ==============================================================================
with st.sidebar:
    st.image(URL_LOGO_OFFICIEL, use_container_width=True)
    st.markdown(f"### 🔐 Session : **{st.session_state.role}**")
    if st.button("🚪 Se déconnecter du portail", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    st.divider()
    st.write(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"⏰ **Heure :** {datetime.now().strftime('%H:%M')}")
    st.write("---")
    st.caption("Gouvernement RCRP - 2026")
    st.caption("Version du logiciel : 9.49")

st.title(f"🏛️ Espace de Gestion : {st.session_state.role}")

# --- BASES DE DONNÉES ET LISTES DE RÉFÉRENCE ---
LISTE_ASSURANCES_VALIDEES = ["Non assuré", "RCT", "Averis"]
LISTE_ETATS_PLAQUES = sorted(["California", "Washington", "Texas", "New York", "Florida", "Quebec", "Ontario", "Nevada", "Colorado"])
LISTE_MARQUES_VEHICULES = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])

# DÉFINITION DYNAMIQUE DES ONGLETS SELON LES PRIVILÈGES
if st.session_state.role == "Staff":
    onglets_principaux = st.tabs(["🚗 Immatriculations", "🪪 Dossiers Permis", "💰 Banque Centrale", "➕ Gestion Profils", "📜 Logs Système"])
elif st.session_state.role == "RCT":
    onglets_principaux = st.tabs(["🚗 Immatriculations", "💰 Facturation RCT"])
else:
    onglets_principaux = st.tabs(["🚗 Registre Véhicules", "💰 Mon Compte"])

# ==============================================================================
# 🚗 ONGLET 1 : GESTION DES IMMATRICULATIONS (AVEC CALCULS DE FRAIS)
# ==============================================================================
with onglets_principaux[0]:
    base_immatriculations = charger_donnees_feuille("Copie de Immatriculations")
    base_bancaire = charger_donnees_feuille("Banque")
    
    liste_pseudos_roblox = sorted(base_bancaire["Nom Roblox"].unique().tolist()) if not base_bancaire.empty else []

    with st.expander("➕ Enregistrer un nouveau véhicule dans le Fichier Central"):
        with st.form("formulaire_ajout_vehicule_complet"):
            st.markdown("### 📝 Formulaire Officiel d'Enregistrement")
            col_form_1, col_form_2 = st.columns(2)
            
            selection_proprietaire = col_form_1.selectbox("👤 Propriétaire (Nom Roblox)", ["--- Choisir un citoyen ---"] + liste_pseudos_roblox)
            selection_marque = col_form_1.selectbox("🚘 Marque du véhicule", LISTE_MARQUES_VEHICULES)
            input_plaque = col_form_2.text_input("🔢 Numéro de la plaque d'immatriculation")
            selection_etat = col_form_2.selectbox("📍 État de la plaque", LISTE_ETATS_PLAQUES)
            selection_assurance = col_form_1.selectbox("🛡️ Contrat d'Assurance", LISTE_ASSURANCES_VALIDEES)
            input_code_vehicule = col_form_2.text_input("🔑 Code secret du véhicule (pour modifications futures)", type="password")
            
            # --- LOGIQUE DE CALCUL DU TICKET DE CAISSE ---
            montant_base_ville = 175
            montant_assurance_rct = 0
            montant_assurance_averis = 0
            montant_taxe_jeune = 0
            
            if selection_proprietaire != "--- Choisir un citoyen ---":
                donnees_proprietaire = base_bancaire[base_bancaire["Nom Roblox"] == selection_proprietaire]
                if not donnees_proprietaire.empty:
                    if selection_assurance == "Averis":
                        montant_assurance_averis = 130
                        try:
                            date_entree_citoyen = datetime.strptime(str(donnees_proprietaire.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                            if datetime.now() - date_entree_citoyen < timedelta(days=30):
                                montant_taxe_jeune = 50
                        except: pass
                    elif selection_assurance == "RCT":
                        nombre_vehicules_rct = base_immatriculations[(base_immatriculations["Nom d'utilisateur ROBLOX"] == selection_proprietaire) & (base_immatriculations["Assurance"] == "RCT")].shape[0]
                        if nombre_vehicules_rct < 2:
                            montant_assurance_rct = 150

            total_facturation_finale = montant_base_ville + montant_assurance_rct + montant_assurance_averis + montant_taxe_jeune
            
            # --- AFFICHAGE DU TICKET DE CAISSE ---
            st.markdown("### 💸 Détail de la Facturation")
            texte_ticket = f"""
            <div class='frais-container-premium'>
                • Frais d'Immatriculation (Trésor Public) : {montant_base_ville}$<br>
                {f'• Contrat Averis (Trésor Public) : {montant_assurance_averis}$<br>' if montant_assurance_averis > 0 else ''}
                {f'• Taxe Jeune Conducteur (Trésor Public) : {montant_taxe_jeune}$<br>' if montant_taxe_jeune > 0 else ''}
                {f'• Assurance RCT (Compte RCT Entreprise) : {montant_assurance_rct}$<br>' if montant_assurance_rct > 0 else ''}
                {f'• Promotion Fidélité RCT (3ème véhicule) : 0$<br>' if selection_assurance == 'RCT' and montant_assurance_rct == 0 else ''}
                <hr style='border: 0.5px solid rgba(255,255,255,0.1)'>
                <b style='font-size: 18px; color: #2ecc71;'>TOTAL À DÉBITER : {total_facturation_finale}$</b>
            </div>
            """
            st.markdown(texte_ticket, unsafe_allow_html=True)
            
            if st.form_submit_button("💳 Confirmer l'achat et immatriculer"):
                if selection_proprietaire != "--- Choisir un citoyen ---" and input_plaque and input_code_vehicule:
                    ligne_banque_client = base_bancaire[base_bancaire["Nom Roblox"] == selection_proprietaire]
                    solde_actuel_client = float(ligne_banque_client.iloc[0]["Solde"])
                    
                    if solde_actuel_client >= total_facturation_finale:
                        # 1. Débit bancaire du client
                        base_bancaire.at[ligne_banque_client.index[0], "Solde"] = solde_actuel_client - total_facturation_finale
                        
                        # 2. Redirection des fonds RCT vers une10000
                        if montant_assurance_rct > 0:
                            ligne_rct_dest = base_bancaire[base_bancaire["Nom Roblox"] == COMPTE_BANQUE_RCT_CIBLE]
                            if not ligne_rct_dest.empty:
                                base_bancaire.at[ligne_rct_dest.index[0], "Solde"] = float(ligne_rct_dest.iloc[0]["Solde"]) + montant_assurance_rct
                                st.toast(f"💰 {montant_assurance_rct}$ transférés à {COMPTE_BANQUE_RCT_CIBLE}")
                        
                        # 3. Création de la ligne véhicule
                        nouvelle_ligne_immat = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Nom d'utilisateur ROBLOX": selection_proprietaire,
                            "Marque du véhicule": selection_marque,
                            "L'état de la plaque": selection_etat,
                            "Numéro de la plaque": input_plaque,
                            "Assurance": selection_assurance,
                            "CODE": str(input_code_vehicule)
                        }])
                        
                        connection_gsheets.update(worksheet="Banque", data=base_bancaire)
                        connection_gsheets.update(worksheet="Copie de Immatriculations", data=pd.concat([base_immatriculations, nouvelle_ligne_immat], ignore_index=True))
                        
                        st.success(f"🎉 Véhicule enregistré avec succès pour {selection_proprietaire} !")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Solde insuffisant (Manque {total_facturation_finale - solde_actuel_client}$).")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs du formulaire.")

    st.divider()
    recherche_vehicule = st.text_input("🔍 Rechercher un véhicule (Plaque, Nom du propriétaire, Marque...)").strip().lower()
    
    if not base_immatriculations.empty:
        filtre_vehicules = base_immatriculations.apply(lambda row: recherche_vehicule in str(row).lower(), axis=1)
        resultats_vehicules = base_immatriculations[filtre_vehicules]
        
        for index_v, ligne_v in resultats_vehicules.iterrows():
            with st.container(border=True):
                col_info_v, col_actions_v = st.columns([4, 1])
                with col_info_v:
                    st.markdown(f"### 🚗 Plaque : **{ligne_v['Numéro de la plaque']}**")
                    st.write(f"👤 **Propriétaire :** {ligne_v['Nom d\'utilisateur ROBLOX']} | 🛡️ **Assurance :** {ligne_v['Assurance']}")
                    st.write(f"🚘 **Détails :** {ligne_v['Marque du véhicule']} ({ligne_v['L\'état de la plaque']})")
                
                with col_actions_v:
                    if st.button("⚙️ Options", key=f"btn_options_veh_{index_v}"):
                        st.session_state[f"afficher_options_{index_v}"] = not st.session_state.get(f"afficher_options_{index_v}", False)
                
                if st.session_state.get(f"afficher_options_{index_v}"):
                    st.write("---")
                    with st.form(f"formulaire_verif_veh_{index_v}"):
                        verif_code = st.text_input("Veuillez saisir le code secret du véhicule", type="password")
                        if st.form_submit_button("🔓 Déverrouiller l'accès"):
                            if st.session_state.role == "Staff" or str(verif_code) == str(ligne_v['CODE']):
                                st.session_state[f"acces_autorise_veh_{index_v}"] = True
                            else:
                                st.error("❌ Code secret invalide.")
                    
                    if st.session_state.get(f"acces_autorise_veh_{index_v}"):
                        with st.form(f"formulaire_edition_veh_{index_v}"):
                            nouveau_contrat = st.selectbox("Changer le contrat d'assurance", LISTE_ASSURANCES_VALIDEES, index=LISTE_ASSURANCES_VALIDEES.index(ligne_v['Assurance']) if ligne_v['Assurance'] in LISTE_ASSURANCES_VALIDEES else 0)
                            col_b_save, col_b_delete = st.columns(2)
                            if col_b_save.form_submit_button("💾 Sauvegarder les modifications"):
                                base_immatriculations.at[index_v, 'Assurance'] = nouveau_contrat
                                connection_gsheets.update(worksheet="Copie de Immatriculations", data=base_immatriculations)
                                st.success("Données mises à jour !")
                                st.rerun()
                            if col_b_delete.form_submit_button("🗑️ Supprimer définitivement"):
                                base_immatriculations = base_immatriculations.drop(index_v)
                                connection_gsheets.update(worksheet="Copie de Immatriculations", data=base_immatriculations)
                                st.error("Véhicule supprimé du registre.")
                                st.rerun()

# ==============================================================================
# 💰 ONGLET 2 : BANQUE (GESTION ET CONSULTATION DES COMPTES)
# ==============================================================================
with onglets_principaux[1 if st.session_state.role != "Staff" else 2]:
    base_bancaire_admin = charger_donnees_feuille("Banque")
    
    if st.session_state.role == "Civil":
        recherche_compte_civil = st.text_input("🔍 Entrez votre Nom Roblox pour consulter votre situation").strip().lower()
        if recherche_compte_civil:
            resultat_compte_civil = base_bancaire_admin[base_bancaire_admin.apply(lambda r: recherche_compte_civil in str(r).lower(), axis=1)]
            if not resultat_compte_civil.empty:
                col_metric_1, col_metric_2 = st.columns(2)
                col_metric_1.metric("💵 Solde Bancaire Actuel", f"{float(resultat_compte_civil.iloc[0]['Solde']):,.0f} $")
                
                base_permis_public = charger_donnees_feuille("Points Permis")
                ligne_permis_public = base_permis_public[base_permis_public.apply(lambda r: recherche_compte_civil in str(r).lower(), axis=1)]
                if not ligne_permis_public.empty:
                    col_metric_2.metric("🪪 Points de Permis de Conduire", f"{ligne_permis_public.iloc[0]['PTS']} / 25")
            else:
                st.info("Aucun profil correspondant à ce nom n'a été trouvé.")
    
    else:
        st.write("### 🏦 Interface d'Administration de la Banque Centrale")
        recherche_admin_banque = st.text_input("🔍 Rechercher un compte (Nom, Discord, Administrateur...)").strip().lower()
        
        if recherche_admin_banque:
            resultats_recherche_banque = base_bancaire_admin[base_bancaire_admin.apply(lambda r: recherche_admin_banque in str(r).lower(), axis=1)]
            for index_b, ligne_b in resultats_recherche_banque.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **Citoyen : {ligne_b['Nom Roblox']}**")
                    st.write(f"💬 Discord : {ligne_b['Nom Discord']} | 🛡️ Créé par : {ligne_b['Pseudo Admin']}")
                    st.write(f"📅 Date d'enregistrement : {ligne_b['Date d\'arrivée']}")
                    
                    solde_actuel_compte = float(ligne_b['Solde'])
                    st.metric("Solde Disponible", f"{solde_actuel_compte:,.0f} $")
                    
                    with st.form(f"formulaire_operation_banque_{index_b}"):
                        montant_operation = st.number_input("Saisir le montant de la transaction", min_value=0.0, step=100.0)
                        col_btn_deb, col_btn_cred = st.columns(2)
                        
                        if col_btn_deb.form_submit_button("📉 Retirer / Facturer"):
                            base_bancaire_admin.at[index_b, 'Solde'] = solde_actuel_compte - montant_operation
                            connection_gsheets.update(worksheet="Banque", data=base_bancaire_admin)
                            st.success(f"Transaction effectuée : -{montant_operation}$")
                            st.rerun()
                            
                        if col_btn_cred.form_submit_button("📈 Ajouter / Créditer") and st.session_state.role == "Staff":
                            base_bancaire_admin.at[index_b, 'Solde'] = solde_actuel_compte + montant_operation
                            connection_gsheets.update(worksheet="Banque", data=base_bancaire_admin)
                            st.success(f"Transaction effectuée : +{montant_operation}$")
                            st.rerun()

# ==============================================================================
# 🪪 ONGLET 3 : PERMIS DE CONDUIRE (STAFF UNIQUEMENT)
# ==============================================================================
if st.session_state.role == "Staff":
    with onglets_principaux[1]:
        st.write("### 🪪 Registre National des Permis de Conduire")
        base_permis_staff = charger_donnees_feuille("Points Permis")
        recherche_permis_staff = st.text_input("🔍 Rechercher un dossier par Nom Roblox").strip().lower()
        
        if recherche_permis_staff:
            resultats_permis_staff = base_permis_staff[base_permis_staff.apply(lambda r: recherche_permis_staff in str(r).lower(), axis=1)]
            for index_p, ligne_p in resultats_permis_staff.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **Titulaire : {ligne_p['Nom Roblox']}**")
                    st.write(f"📍 État actuel : **{ligne_p['PTS']} / 25 points**")
                    with st.form(f"formulaire_maj_points_{index_p}"):
                        nouveau_solde_points = st.number_input("Ajuster le nombre de points", 0, 25, value=int(ligne_p['PTS']))
                        if st.form_submit_button("💾 Mettre à jour le dossier"):
                            base_permis_staff.at[index_p, 'PTS'] = nouveau_solde_points
                            connection_gsheets.update(worksheet="Points Permis", data=base_permis_staff)
                            st.success("Les points ont été mis à jour dans le fichier central.")
                            st.rerun()

    # ==============================================================================
    # ➕ ONGLET 4 : CRÉATION DE PROFILS (AUTOMATIQUE)
    # ==============================================================================
    with onglets_principaux[3]:
        st.write("### ➕ Enregistrement d'un Nouveau Citoyen")
        st.info("💡 Cette procédure crée simultanément le compte bancaire, le dossier permis et enregistre la date de création.")
        
        with st.form("formulaire_creation_profil_integral"):
            col_c1, col_c2 = st.columns(2)
            nouveau_nom_roblox = col_c1.text_input("Nom d'utilisateur ROBLOX")
            nouveau_discord = col_c2.text_input("Nom Discord (ex: @pseudo)")
            pseudo_administrateur = col_c1.text_input("Votre Pseudo Administrateur")
            montant_initial_banque = col_c2.number_input("Dotation Bancaire Initiale", value=15000.0)
            points_initiaux_permis = col_c1.number_input("Points de Permis Initiaux", 0, 25, value=25)
            
            st.write("---")
            if st.form_submit_button("🚀 Finaliser la création du citoyen"):
                base_banque_creation = charger_donnees_feuille("Banque")
                base_permis_creation = charger_donnees_feuille("Points Permis")
                
                if not base_banque_creation[base_banque_creation["Nom Roblox"].str.lower() == nouveau_nom_roblox.lower()].empty:
                    st.error("❌ Un profil existe déjà avec ce nom Roblox.")
                elif nouveau_nom_roblox == "" or pseudo_administrateur == "":
                    st.warning("⚠️ Le nom du citoyen et le pseudo admin sont obligatoires.")
                else:
                    # Préparation de la ligne bancaire complète
                    nouvelle_ligne_banque = pd.DataFrame([{
                        "Solde": montant_initial_banque,
                        "Nom Discord": nouveau_discord,
                        "Nom Roblox": nouveau_nom_roblox,
                        "Pseudo Admin": pseudo_administrateur,
                        "Date d'arrivée": datetime.now().strftime("%d/%m/%Y")
                    }])
                    
                    # Préparation de la ligne permis
                    nouvelle_ligne_permis = pd.DataFrame([{
                        "Nom Roblox": nouveau_nom_roblox,
                        "PTS": points_initiaux_permis
                    }])
                    
                    connection_gsheets.update(worksheet="Banque", data=pd.concat([base_banque_creation, nouvelle_ligne_banque], ignore_index=True))
                    connection_gsheets.update(worksheet="Points Permis", data=pd.concat([base_permis_creation, nouvelle_ligne_permis], ignore_index=True))
                    
                    st.success(f"🎉 Bienvenue à {nouveau_nom_roblox} ! Le profil a été généré avec succès.")
                    time.sleep(1)
                    st.rerun()

    # ==============================================================================
    # 📜 ONGLET 5 : LOGS SYSTÈME
    # ==============================================================================
    with onglets_principaux[4]:
        st.write("### 📜 Archives des Logs de Navigation")
        donnees_logs = charger_donnees_feuille("Logs")
        if not donnees_logs.empty:
            st.dataframe(donnees_logs.iloc[::-1], use_container_width=True)

# --- PIED DE PAGE ---
st.markdown("---")
st.markdown("<center><small>République de Californie RP | v9.49 | Système de Gestion Intégral</small></center>", unsafe_allow_html=True)
