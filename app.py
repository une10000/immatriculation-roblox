import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="RCRP - Portail Officiel de Gestion",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS AVANCÉ (LOGO, BOUTONS, ET ALIGNEMENT) ---
st.markdown("""
    <style>
    /* Ajustement de l'espacement supérieur */
    .block-container { 
        padding-top: 1.5rem; 
        padding-bottom: 0rem; 
    }
    
    /* Force l'alignement vertical des boîtes de connexion */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        display: flex;
        flex-direction: column;
        height: 550px !important;
        justify-content: space-between;
    }
    
    /* Design des métriques bancaires */
    .stMetric { 
        background-color: #f8f9fb; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }

    /* Style du logo dans la sidebar */
    [data-testid="stSidebar"] img {
        border-radius: 15px;
        margin-bottom: 20px;
        border: 2px solid #333;
    }

    /* Personnalisation des onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
        gap: 1px;
        padding-top: 10px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #0e1117 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION DE LA SESSION ---
if "role" not in st.session_state:
    st.session_state.role = None

# --- CONNEXION AUX DONNÉES ET PARAMÈTRES ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Codes d'accès sécurisés
CODE_ADMIN_GENERAL = "RCRPFR-25-26" 
CODE_ENTREPRISE = "RCT-26-RCRPFR" 

# URL du Logo Officiel
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless"

def get_data(sheet_name):
    """Fonction de lecture des données avec vidage de cache pour temps réel"""
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except Exception as e:
        st.error(f"Erreur lors de la lecture de la feuille '{sheet_name}' : {e}")
        return pd.DataFrame()

# ==============================================================================
# 🚪 SYSTÈME DE CONNEXION INITIAL
# ==============================================================================
if st.session_state.role is None:
    st.title("🏛️ Portail des Services de la République de Californie")
    st.markdown("<h4 style='color: #666;'>Système Centralisé de Gestion - Session 2025-2026</h4>", unsafe_allow_html=True)
    
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 👤 Espace Citoyen")
            st.write("Consultez librement votre solde bancaire, vos points de permis de conduire ainsi que vos véhicules enregistrés.")
            st.write("---")
            st.info("Aucun code requis pour la consultation publique.")
            if st.button("Accéder au Portail Public", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### 🛠️ Espace Entreprise (RCT)")
            st.write("Interface réservée aux agents de la RCT pour la facturation, la gestion des assurances et des dossiers clients.")
            st.write("---")
            pass_rct = st.text_input("Code d'Accès Entreprise", type="password", key="p_rct")
            if st.button("Connexion Professionnelle", use_container_width=True):
                if pass_rct == CODE_ENTREPRISE:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("❌ Code d'accès entreprise invalide.")

    with col3:
        with st.container(border=True):
            st.markdown("### 👮 Espace Staff / État")
            st.write("Accès haute sécurité pour l'administration globale : Fichier Central, Points de Permis, Banque et Logs.")
            st.write("---")
            pass_staff = st.text_input("Code d'Autorisation Staff", type="password", key="p_staff")
            if st.button("Connexion Sécurisée", use_container_width=True):
                if pass_staff == CODE_ADMIN_GENERAL:
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    st.error("❌ Code d'autorisation incorrect.")
    st.stop()

# ==============================================================================
# 🖥️ INTERFACE PRINCIPALE APRÈS CONNEXION
# ==============================================================================

with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown(f"### 🛡️ Session : **{st.session_state.role}**")
    if st.button("🚪 Se Déconnecter", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    st.divider()
    st.write(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"⏰ **Heure :** {datetime.now().strftime('%H:%M')}")
    st.write("---")
    st.caption("RCRP Management System v9.43")

st.title(f"🏛️ Espace de Gestion : {st.session_state.role}")

# --- BASES DE DONNÉES ET LISTES ---
liste_assurances = ["Non assuré", "RCT", "Averis"]
liste_etats = sorted(["California", "Washington", "Texas", "New York", "Florida", "Quebec", "Ontario", "Nevada", "Colorado"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])

# Définition des onglets selon le rôle
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers Permis", "💰 Banque Centrale", "➕ Gestion Profils", "📜 Logs Système"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation RCT"])
else:
    tabs = st.tabs(["🚗 Registre Véhicules", "💰 Mon Compte"])

# ==============================================================================
# 🚗 ONGLET 1 : IMMATRICULATIONS (AVEC DROPDOWN PSEUDO)
# ==============================================================================
with tabs[0]:
    df_immatriculations = get_data("Copie de Immatriculations")
    df_banque_data = get_data("Banque")
    
    # Création de la liste des pseudos pour le menu déroulant
    pseudos_presents = sorted(df_banque_data["Nom Roblox"].unique().tolist()) if not df_banque_data.empty else []

    with st.expander("➕ Enregistrer un nouveau véhicule dans le Fichier Central"):
        with st.form("form_add_vehicule"):
            st.markdown("### 📝 Formulaire d'Enregistrement")
            c1, c2 = st.columns(2)
            
            # Utilisation de la liste déroulante pour éviter les erreurs de frappe
            user_select = c1.selectbox("👤 Sélectionner le Nom Roblox du propriétaire", ["--- Choisir un Citoyen ---"] + pseudos_presents)
            
            marque_select = c1.selectbox("🚘 Marque du véhicule", liste_marques)
            plaque_input = c2.text_input("🔢 Numéro de la plaque")
            etat_select = c2.selectbox("📍 État de la plaque", liste_etats)
            assurance_select = c1.selectbox("🛡️ Contrat d'Assurance", liste_assurances)
            code_secret_vehicule = c2.text_input("🔑 Code secret du véhicule (pour vos modifs)", type="password")
            
            st.write("---")
            if st.form_submit_button("✅ Enregistrer et Payer l'Immatriculation"):
                if user_select != "--- Choisir un Citoyen ---" and plaque_input and code_secret_vehicule:
                    # Logique de calcul du prix
                    prix_final = 175 
                    user_info = df_banque_data[df_banque_data["Nom Roblox"] == user_select]
                    
                    if not user_info.empty:
                        solde_bancaire = float(user_info.iloc[0]["Solde"])
                        
                        # Cas Assurance Averis
                        if assurance_select == "Averis":
                            prix_final += 130
                            try:
                                date_entree = datetime.strptime(str(user_info.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                                if datetime.now() - date_entree < timedelta(days=30):
                                    prix_final += 50
                                    st.info("💡 Frais additionnels : Taxe Jeune Conducteur appliquée.")
                            except: pass
                        
                        # Cas Assurance RCT
                        elif assurance_select == "RCT":
                            count_rct = df_immatriculations[(df_immatriculations["Nom d'utilisateur ROBLOX"] == user_select) & (df_immatriculations["Assurance"] == "RCT")].shape[0]
                            if count_rct >= 2:
                                prix_final += 0
                                st.success("🎉 Bonus : 3ème assurance RCT offerte !")
                            else:
                                prix_final += 150
                        
                        # Vérification du solde
                        if solde_bancaire >= prix_final:
                            # 1. Débit bancaire
                            df_banque_data.at[user_info.index[0], "Solde"] = solde_bancaire - prix_final
                            
                            # 2. Création de la ligne véhicule
                            nouvelle_immat = pd.DataFrame([{
                                "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "Nom d'utilisateur ROBLOX": user_select,
                                "Marque du véhicule": marque_select,
                                "L'état de la plaque": etat_select,
                                "Numéro de la plaque": plaque_input,
                                "Assurance": assurance_select,
                                "CODE": str(code_secret_vehicule)
                            }])
                            
                            conn.update(worksheet="Banque", data=df_banque_data)
                            conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_immatriculations, nouvelle_immat], ignore_index=True))
                            
                            st.success(f"🎉 Véhicule immatriculé ! {prix_final}$ ont été débités.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ Solde insuffisant : Il vous manque {prix_final - solde_bancaire}$.")
                    else:
                        st.error("❌ Profil bancaire introuvable.")
                else:
                    st.warning("⚠️ Remplissez tous les champs avant de valider.")

    st.divider()
    recherche = st.text_input("🔍 Rechercher un véhicule (Plaque, Nom, Marque...)").strip().lower()
    
    if not df_immatriculations.empty:
        filtre = df_immatriculations.apply(lambda r: recherche in str(r).lower(), axis=1)
        resultats = df_immatriculations[filtre]
        
        for idx_im, row_im in resultats.iterrows():
            with st.container(border=True):
                col_info_v, col_btn_v = st.columns([4, 1])
                with col_info_v:
                    st.markdown(f"### 🚗 Plaque : **{row_im['Numéro de la plaque']}**")
                    st.write(f"👤 **Propriétaire :** {row_im['Nom d\'utilisateur ROBLOX']} | 🛡️ **Assurance :** {row_im['Assurance']}")
                    st.write(f"🚘 **Modèle :** {row_im['Marque du véhicule']} ({row_im['L\'état de la plaque']})")
                
                with col_btn_v:
                    if st.button("⚙️ Options", key=f"btn_opt_{idx_im}"):
                        st.session_state[f"show_v_{idx_im}"] = not st.session_state.get(f"show_v_{idx_im}", False)
                
                if st.session_state.get(f"show_v_{idx_im}"):
                    st.write("---")
                    with st.form(f"form_auth_v_{idx_im}"):
                        code_test = st.text_input("Saisir le code secret du véhicule", type="password")
                        if st.form_submit_button("🔓 Déverrouiller"):
                            if st.session_state.role == "Staff" or str(code_test) == str(row_im['CODE']):
                                st.session_state[f"auth_v_ok_{idx_im}"] = True
                            else:
                                st.error("❌ Code secret incorrect.")
                    
                    if st.session_state.get(f"auth_v_ok_{idx_im}"):
                        with st.form(f"form_edit_v_{idx_im}"):
                            new_assu = st.selectbox("Changer l'Assurance", liste_assurances, index=liste_assurances.index(row_im['Assurance']) if row_im['Assurance'] in liste_assurances else 0)
                            b_save, b_del = st.columns(2)
                            if b_save.form_submit_button("💾 Sauvegarder"):
                                df_immatriculations.at[idx_im, 'Assurance'] = new_assu
                                conn.update(worksheet="Copie de Immatriculations", data=df_immatriculations)
                                st.success("Modifications enregistrées !")
                                st.rerun()
                            if b_del.form_submit_button("🗑️ Supprimer le véhicule"):
                                df_immatriculations = df_immatriculations.drop(idx_im)
                                conn.update(worksheet="Copie de Immatriculations", data=df_immatriculations)
                                st.error("Véhicule supprimé.")
                                st.rerun()

# ==============================================================================
# 💰 ONGLET 2 : BANQUE (GESTION DES COMPTES)
# ==============================================================================
with tabs[1 if st.session_state.role != "Staff" else 2]:
    df_banque_complet = get_data("Banque")
    
    if st.session_state.role == "Civil":
        nom_search = st.text_input("🔍 Entrez votre Nom Roblox pour consulter votre compte").strip().lower()
        if nom_search:
            user_b = df_banque_complet[df_banque_complet.apply(lambda r: nom_search in str(r).lower(), axis=1)]
            if not user_user_b.empty:
                c_b1, c_b2 = st.columns(2)
                c_b1.metric("💵 Solde Bancaire", f"{float(user_b.iloc[0]['Solde']):,.0f} $")
                
                df_pts_view = get_data("Points Permis")
                user_p = df_pts_view[df_pts_view.apply(lambda r: nom_search in str(r).lower(), axis=1)]
                if not user_p.empty:
                    c_b2.metric("🪪 Points de Permis", f"{user_p.iloc[0]['PTS']} / 25")
            else:
                st.info("Aucun compte trouvé à ce nom.")
    
    else:
        st.write("### 🏦 Administration Bancaire Centrale")
        search_b = st.text_input("🔍 Rechercher un compte citoyen (Nom, Discord, Admin...)").strip().lower()
        if search_b:
            res_b = df_banque_complet[df_banque_complet.apply(lambda r: search_b in str(r).lower(), axis=1)]
            for idx_bank, row_bank in res_b.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **Propriétaire : {row_bank['Nom Roblox']}**")
                    # Correction de la syntaxe pour l'apostrophe dans le texte
                    st.write(f"💬 Discord : {row_bank['Nom Discord']} | 🛡️ Admin : {row_bank['Pseudo Admin']}")
                    st.write(f"📅 Date d'arrivée : {row_bank['Date d\'arrivée']}")
                    
                    solde_actuel = float(row_bank['Solde'])
                    st.metric("Solde Bancaire", f"{solde_actuel:,.0f} $")
                    
                    with st.form(f"form_op_bank_{idx_bank}"):
                        montant_op = st.number_input("Montant de la transaction", min_value=0.0, step=100.0)
                        btn_col1, btn_col2 = st.columns(2)
                        
                        if btn_col1.form_submit_button("📉 Facturer / Retirer"):
                            df_banque_complet.at[idx_bank, 'Solde'] = solde_actuel - montant_op
                            conn.update(worksheet="Banque", data=df_banque_complet)
                            st.success(f"Débit de {montant_op}$ effectué.")
                            st.rerun()
                            
                        if btn_col2.form_submit_button("📈 Ajouter / Créditer") and st.session_state.role == "Staff":
                            df_banque_complet.at[idx_bank, 'Solde'] = solde_actuel + montant_op
                            conn.update(worksheet="Banque", data=df_banque_complet)
                            st.success(f"Crédit de {montant_op}$ effectué.")
                            st.rerun()

# ==============================================================================
# 🪪 ONGLET 3 : PERMIS (STAFF UNIQUEMENT)
# ==============================================================================
if st.session_state.role == "Staff":
    with tabs[1]:
        st.write("### 🪪 Dossiers des Permis de Conduire")
        df_permis_staff = get_data("Points Permis")
        recherche_p = st.text_input("🔍 Rechercher un dossier (Nom Roblox)").strip().lower()
        
        if recherche_p:
            res_p_staff = df_permis_staff[df_permis_staff.apply(lambda r: recherche_p in str(r).lower(), axis=1)]
            for idx_ps, row_ps in res_p_staff.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **Citoyen : {row_ps['Nom Roblox']}**")
                    st.write(f"📍 Points actuels : **{row_ps['PTS']} / 25**")
                    with st.form(f"form_pts_edit_{idx_ps}"):
                        nv_points = st.number_input("Ajuster le solde de points", 0, 25, value=int(row_ps['PTS']))
                        if st.form_submit_button("💾 Mettre à jour le dossier"):
                            df_permis_staff.at[idx_ps, 'PTS'] = nv_points
                            conn.update(worksheet="Points Permis", data=df_permis_staff)
                            st.success("Points mis à jour !")
                            st.rerun()

    # ==============================================================================
    # ➕ ONGLET 4 : GESTION PROFILS (CRÉATION COMPLÈTE)
    # ==============================================================================
    with tabs[3]:
        st.write("### ➕ Création d'un Nouveau Citoyen")
        st.info("Cet outil crée simultanément le compte bancaire et le dossier de permis.")
        
        with st.form("form_creation_totale"):
            col_c1, col_c2 = st.columns(2)
            new_u = col_c1.text_input("Nom d'utilisateur ROBLOX")
            new_d = col_c2.text_input("Nom Discord (ex: @pseudo)")
            new_a = col_c1.text_input("Votre Pseudo Admin (Celui qui crée)")
            new_s = col_c2.number_input("Solde Bancaire Initial", value=15000.0)
            new_p = col_c1.number_input("Points de Permis Initiaux", 0, 25, value=25)
            
            st.write("---")
            if st.form_submit_button("🚀 Créer le profil intégral"):
                df_b_new = get_data("Banque")
                df_p_new = get_data("Points Permis")
                
                if not df_b_new[df_b_new["Nom Roblox"].str.lower() == new_u.lower()].empty:
                    st.error("❌ Un citoyen avec ce nom existe déjà !")
                elif new_u == "" or new_a == "":
                    st.warning("⚠️ Merci de remplir le nom et votre pseudo admin.")
                else:
                    # 1. Préparation Banque (Colonnes : Solde, Nom Discord, Nom Roblox, Pseudo Admin, Date d'arrivée)
                    ligne_b = pd.DataFrame([{
                        "Solde": new_s,
                        "Nom Discord": new_d,
                        "Nom Roblox": new_u,
                        "Pseudo Admin": new_a,
                        "Date d'arrivée": datetime.now().strftime("%d/%m/%Y")
                    }])
                    # 2. Préparation Permis
                    ligne_p = pd.DataFrame([{
                        "Nom Roblox": new_u,
                        "PTS": new_p
                    }])
                    
                    conn.update(worksheet="Banque", data=pd.concat([df_b_new, ligne_b], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_p_new, ligne_p], ignore_index=True))
                    
                    st.success(f"🎉 Citoyen {new_u} créé avec succès !")
                    time.sleep(1)
                    st.rerun()

    # ==============================================================================
    # 📜 ONGLET 5 : LOGS
    # ==============================================================================
    with tabs[4]:
        st.write("### 📜 Archives des Logs Système")
        df_logs_sys = get_data("Logs")
        if not df_logs_sys.empty:
            st.dataframe(df_logs_sys.iloc[::-1], use_container_width=True)

st.markdown("---")
st.markdown("<center><small>RCRP - Système de Gestion République de Californie | v9.43</small></center>", unsafe_allow_html=True)
