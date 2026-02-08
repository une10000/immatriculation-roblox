import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE
# ==============================================================================
st.set_page_config(
    page_title="RCRP - Système Intégral Professionnel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. STYLE CSS COMPLET (PRÉSERVÉ À 100%)
# ==============================================================================
st.markdown("""
    <style>
    /* Ajustement de l'espace haut du container principal */
    .block-container { 
        padding-top: 6rem !important; 
    }
    
    /* Style du Logo dans la Sidebar avec bordures arrondies */
    [data-testid="stSidebar"] img { 
        border-radius: 15px; 
        width: 250px !important; 
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 25px;
        display: block;
        border: 1px solid #333;
    }

    /* Style des badges pour les types d'Assurance */
    .badge-assu {
        background-color: #ff4b4b;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }

    /* Style du Reçu Noir "Ticket de caisse" pour les transactions */
    .ticket-fix { 
        background-color: #0d0d0d !important; 
        color: #00ff00 !important; 
        padding: 25px; 
        border: 2px dashed #ff4b4b; 
        border-radius: 12px; 
        font-family: 'Courier New', monospace;
        line-height: 1.5;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. INITIALISATION DES VARIABLES DE SESSION ET CONNEXION
# ==============================================================================
# Vérification de l'état de connexion de l'utilisateur
if "role" not in st.session_state:
    st.session_state.role = None

# Connexion sécurisée au Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# Constantes de redirection pour les virements automatiques
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"

# Codes d'accès pour les différents niveaux d'autorisation
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"

# URL du Logo officiel (Averis / RCT)
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

# ==============================================================================
# 4. FONCTION DE CHARGEMENT DES DONNÉES (MODE RÉEL)
# ==============================================================================
def load_rcrp_data():
    """Charge toutes les bases de données depuis le GSheet"""
    st.cache_data.clear()
    try:
        # Importation de la feuille Banque
        bank_data = conn.read(worksheet="Banque", ttl=0)
        bank_df = bank_data.dropna(how='all').fillna("")
        
        # Importation de la feuille Immatriculations
        immat_data = conn.read(worksheet="Copie de Immatriculations", ttl=0)
        immat_df = immat_data.dropna(how='all').fillna("")
        
        # Importation de la feuille Points Permis
        points_data = conn.read(worksheet="Points Permis", ttl=0)
        points_df = points_data.dropna(how='all').fillna("")
        
        return bank_df, immat_df, points_df
    except Exception as e:
        st.error(f"Erreur fatale de connexion : {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Exécution du chargement initial
df_banque, df_im, df_pts = load_rcrp_data()

# ==============================================================================
# 5. PORTAIL DE SÉCURITÉ (LOGIN)
# ==============================================================================
if st.session_state.role is None:
    st.title("🏛️ Système de Gestion RCRP - Portail d'Authentification")
    st.write("Bienvenue dans l'interface de gestion. Sélectionnez votre accès.")
    
    col_civ, col_pro, col_staff = st.columns(3)
    
    with col_civ:
        with st.container(border=True):
            st.subheader("👤 Civil")
            st.info("Accès libre au registre public.")
            if st.button("Se connecter au Portail Public", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()
                
    with col_pro:
        with st.container(border=True):
            st.subheader("🛠️ Professionnel (RCT)")
            st.info("Accès réservé aux employés.")
            input_rct = st.text_input("Code Agent RCT", type="password", key="login_rct")
            if st.button("Authentification RCT", use_container_width=True):
                if input_rct == CODE_PRO:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("Code de sécurité invalide.")
                    
    with col_staff:
        with st.container(border=True):
            st.subheader("👮 Gouvernement (Staff)")
            st.info("Haute Administration Staff.")
            input_staff = st.text_input("Code Gouvernemental", type="password", key="login_staff")
            if st.button("Authentification Staff", use_container_width=True):
                if input_staff == CODE_ADMIN:
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    st.error("Code de sécurité invalide.")
    st.stop()

# ==============================================================================
# 6. SIDEBAR (LOGO, HEURE ET DATE EN DIRECT)
# ==============================================================================
with st.sidebar:
    # Affichage du Logo
    st.image(LOGO_URL, use_container_width=True)
    
    st.markdown("---")
    
    # Affichage Date et Heure
    maintenant = datetime.now()
    st.markdown(f"📅 **Date du jour :** {maintenant.strftime('%d/%m/%Y')}")
    st.markdown(f"⏰ **Heure système :** {maintenant.strftime('%H:%M:%S')}")
    
    if st.button("🔄 Actualiser l'heure", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    
    # Information Session
    st.info(f"Session active : **{st.session_state.role}**")
    
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    
    st.divider()
    st.caption("RCRP Management System v16.0")
    st.caption("Optimisé pour l'Administration RCRP")

# ==============================================================================
# 7. INTERFACE PRINCIPALE (GESTION DES ONGLETS)
# ==============================================================================
tab_immat, tab_dossier, tab_banque = st.tabs([
    "🚗 Registre National", 
    "🪪 Dossiers Citoyens", 
    "💰 Gestion Financière"
])

# ------------------------------------------------------------------------------
# ONGLET 1 : REGISTRE DES VÉHICULES (IMMATRICULATIONS)
# ------------------------------------------------------------------------------
with tab_immat:
    st.header("🚗 Registre National des Véhicules")
    
    # SECTION ACHAT (Uniquement pour les Civils pour éviter les abus)
    if st.session_state.role not in ["RCT", "Staff"]:
        with st.expander("➕ Formulaire d'Immatriculation de véhicule", expanded=True):
            col_form_left, col_form_right = st.columns(2)
            
            with col_form_left:
                choix_proprio = st.selectbox("Sélectionner le Titulaire", ["---"] + df_banque["Nom Roblox"].tolist())
                input_marque = st.text_input("Marque et Modèle du véhicule")
                input_plaque = st.text_input("Numéro de Plaque souhaité")
            
            with col_form_right:
                choix_assurance = st.selectbox("Formule d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
                input_code_secret = st.text_input("Code Secret de Radiation", type="password")
            
            # --- CALCUL DÉTAILLÉ DES FRAIS ---
            frais_fixe_dossier = 175
            frais_assurance_montant = 0
            taxe_nouveau_citoyen = 0
            
            # 1. Calcul du montant de l'assurance choisie
            if "AVERIS" in choix_assurance:
                frais_assurance_montant = 130
            elif "RCT" in choix_assurance:
                frais_assurance_montant = 150
            
            # 2. Application de l'Offre Trio RCT (2 achetées, la 3ème offerte)
            nombre_vehicules_rct = len(df_im[(df_im["Nom d'utilisateur ROBLOX"] == choix_proprio) & (df_im["Assurance"].str.contains("RCT"))])
            if "RCT" in choix_assurance and nombre_vehicules_rct >= 2:
                frais_assurance_montant = 0
                st.success("🎁 Offre Trio RCT détectée : L'assurance de ce 3ème véhicule est offerte !")
                
            # 3. Calcul de la Taxe Jeune Conducteur (-30 jours de présence)
            if choix_proprio != "---":
                row_citoyen = df_banque[df_banque["Nom Roblox"] == choix_proprio]
                try:
                    date_inscription = datetime.strptime(str(row_citoyen.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                    jours_presence = (datetime.now() - date_inscription).days
                    if jours_presence < 30:
                        taxe_nouveau_citoyen = 50
                        st.warning("⚠️ Taxe Jeune Conducteur appliquée (Moins de 30 jours de ville).")
                except:
                    pass
            
            total_facture_finale = frais_fixe_dossier + frais_assurance_montant + taxe_nouveau_citoyen
            
            # Affichage du Ticket de Caisse noir
            st.markdown(f"""
            <div class="ticket-fix">
                🧾 <b>PRÉ-VISUALISATION DE LA FACTURE</b><br>
                --------------------------------------<br>
                Titulaire : {choix_proprio}<br>
                Frais d'immatriculation : 175$<br>
                Frais d'Assurance : {frais_assurance_montant}$<br>
                Taxe Nouveau Citoyen : {taxe_nouveau_citoyen}$<br>
                --------------------------------------<br>
                <b>MONTANT TOTAL À RÉGLER : {total_facture_finale}$</b>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💳 Valider et Procéder au Paiement", use_container_width=True):
                if choix_proprio != "---" and input_plaque and input_code_secret:
                    # Vérification du solde bancaire
                    index_citoyen = df_banque[df_banque["Nom Roblox"] == choix_proprio].index[0]
                    solde_dispo = float(df_banque.at[index_citoyen, "Solde"])
                    
                    if solde_dispo >= total_facture_finale:
                        # Débit du compte du citoyen
                        df_banque.at[index_citoyen, "Solde"] = solde_dispo - total_facture_finale
                        
                        # Virement automatique vers les comptes d'assurance
                        if frais_assurance_montant > 0:
                            compte_cible = TARGET_AVERIS if "AVERIS" in choix_assurance else TARGET_RCT
                            idx_cible = df_banque[df_banque["Nom Roblox"] == compte_cible].index[0]
                            df_banque.at[idx_cible, "Solde"] = float(df_banque.at[idx_cible, "Solde"]) + frais_assurance_montant
                        
                        # Création de l'entrée véhicule
                        creation_vehicule = pd.DataFrame([{
                            "Horodateur": maintenant.strftime("%d/%m/%Y"), 
                            "Nom d'utilisateur ROBLOX": choix_proprio, 
                            "Marque du véhicule": input_marque, 
                            "Numéro de la plaque": input_plaque, 
                            "Assurance": choix_assurance, 
                            "CODE": str(input_code_secret)
                        }])
                        
                        # Mise à jour GSheet
                        conn.update(worksheet="Banque", data=df_banque)
                        conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, creation_vehicule], ignore_index=True))
                        st.success("Paiement validé ! Le véhicule a été enregistré dans le registre national."); time.sleep(1); st.rerun()
                    else:
                        st.error("Transaction refusée : Solde bancaire insuffisant.")
    else:
        st.info("💡 En tant qu'autorité (RCT/Staff), vous êtes en mode consultation du registre.")

    # RECHERCHE ET AFFICHAGE DES PLAQUES
    st.divider()
    recherche_text = st.text_input("🔍 Recherche rapide (Tapez une Plaque ou un Nom de Citoyen)").lower()
    
    for i, ligne in df_im.iterrows():
        nom_db = str(ligne['Nom d\'utilisateur ROBLOX']).lower()
        plaque_db = str(ligne['Numéro de la plaque']).lower()
        
        if recherche_text in nom_db or recherche_text in plaque_db:
            with st.container(border=True):
                col_disp_1, col_disp_2, col_disp_3 = st.columns([2,2,1])
                # AFFICHAGE DU NUMÉRO DE PLAQUE (IMPORTANT)
                col_disp_1.write(f"🆔 **PLAQUE : {ligne['Numéro de la plaque']}**")
                col_disp_2.write(f"👤 Propriétaire : {ligne['Nom d\'utilisateur ROBLOX']}")
                col_disp_3.markdown(f"<span class='badge-assu'>{ligne['Assurance']}</span>", unsafe_allow_html=True)
                
                # Détails et Radiation
                st.write(f"🚗 Modèle : {ligne['Marque du véhicule']}")
                with st.expander("⚙️ Options de gestion du véhicule"):
                    col_rad_1, col_rad_2 = st.columns(2)
                    with col_rad_1:
                        verif_code = st.text_input("Saisir le Code Secret pour radier", type="password", key=f"rad_code_{i}")
                    with col_rad_2:
                        if st.button("🚫 Confirmer la Radiation", key=f"rad_btn_{i}"):
                            if verif_code == str(ligne['CODE']) or st.session_state.role == "Staff":
                                conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                                st.success("Véhicule supprimé du registre."); time.sleep(1); st.rerun()
                            else:
                                st.error("Code secret incorrect.")

# ------------------------------------------------------------------------------
# ONGLET 2 : DOSSIERS CITOYENS ET PAYE GOUVERNEMENTALE
# ------------------------------------------------------------------------------
with tab_dossier:
    st.header("🪪 Gestion des Dossiers Citoyens")
    
    # SYSTEME DE PAYE (Staff uniquement)
    if st.session_state.role == "Staff":
        with st.container(border=True):
            st.subheader("🏦 Console de Paye Automatisée")
            st.write("Distribution des salaires (Civil: 15,000$ | RCT: 17,000$) et prélèvements d'assurances.")
            
            if st.button("🧧 EXECUTER LA PAYE GLOBALE", use_container_width=True):
                with st.status("Traitement des transactions bancaires..."):
                    
                    # 1. Traitement des Salaires (Colonne Emploiement)
                    for idx, citoyen in df_banque.iterrows():
                        poste_travail = str(citoyen["Emploiement"]).upper()
                        if "RCT" in poste_travail:
                            salaire_virement = 17000
                            st.write(f"💸 Virement RCT : {citoyen['Nom Roblox']} (+17k$)")
                        else:
                            salaire_virement = 15000
                            st.write(f"💸 Virement Civil : {citoyen['Nom Roblox']} (+15k$)")
                        
                        df_banque.at[idx, "Solde"] = float(citoyen["Solde"]) + salaire_virement
                    
                    # 2. Traitement des Prélèvements Assurances
                    dict_trio_rct = {}
                    for _, v in df_im.iterrows():
                        nom_prop = v["Nom d'utilisateur ROBLOX"]
                        
                        if nom_prop in df_banque["Nom Roblox"].values:
                            idx_bank = df_banque[df_banque["Nom Roblox"] == nom_prop].index[0]
                            label_assurance = v["Assurance"]
                            
                            # Logique RCT
                            if "RCT" in label_assurance:
                                dict_trio_rct[nom_prop] = dict_trio_rct.get(nom_prop, 0) + 1
                                if dict_trio_rct[nom_prop] <= 2:
                                    df_banque.at[idx_bank, "Solde"] -= 150
                                    df_banque.loc[df_banque["Nom Roblox"] == TARGET_RCT, "Solde"] += 150
                            
                            # Logique AVERIS
                            elif "AVERIS" in label_assurance:
                                df_banque.at[idx_bank, "Solde"] -= 130
                                df_banque.loc[df_banque["Nom Roblox"] == TARGET_AVERIS, "Solde"] += 130
                                
                    # Envoi vers GSheet
                    conn.update(worksheet="Banque", data=df_banque)
                    st.success("Paye et prélèvements assurances terminés avec succès !"); time.sleep(1); st.rerun()

    # RECHERCHE DE DOSSIER CITOYEN
    st.divider()
    find_citoyen = st.text_input("🔍 Rechercher un Dossier Citoyen (Tapez le Nom Roblox)").lower()
    
    if find_citoyen:
        result_citoyen = df_banque[df_banque["Nom Roblox"].str.lower().str.contains(find_citoyen, na=False)]
        
        for idx, c in result_citoyen.iterrows():
            with st.container(border=True):
                st.subheader(f"Dossier Officiel de : {c['Nom Roblox']}")
                st.write(f"🆔 Pseudo Discord : {c['Nom Discord']}")
                st.write(f"📌 Emploiement : {c['Emploiement']}")
                st.write(f"📅 Date d'arrivée : {c['Date d\'arrivée']}")
                
                # Affichage des Points de Permis
                row_points = df_pts[df_pts["Nom Roblox"] == c["Nom Roblox"]]
                if not row_points.empty:
                    valeur_actuelle_pts = row_points.iloc[0]['PTS']
                    st.metric("Points de Permis de Conduire", f"{valeur_actuelle_pts} / 25")
                    
                    # Modification des points (Autorisé pour Staff)
                    if st.session_state.role == "Staff":
                        new_pts_val = st.number_input("Modifier les points", value=int(valeur_actuelle_pts), key=f"pts_edit_{idx}")
                        if st.button("Mettre à jour le permis", key=f"pts_btn_{idx}"):
                            df_pts.loc[df_pts["Nom Roblox"] == c["Nom Roblox"], "PTS"] = new_pts_val
                            conn.update(worksheet="Points Permis", data=df_pts)
                            st.success("Permis mis à jour."); st.rerun()

    # CREATION DE PROFIL (Staff uniquement)
    if st.session_state.role == "Staff":
        with st.expander("👤 Ajouter un nouveau Citoyen à la base de données"):
            with st.form("form_nouveau_citoyen"):
                add_roblox = st.text_input("Nom d'utilisateur ROBLOX")
                add_discord = st.text_input("Identifiant Discord")
                if st.form_submit_button("Valider la Création"):
                    # AJOUT AUTOMATIQUE DE LA DATE DE CRÉATION
                    date_du_jour = maintenant.strftime("%d/%m/%Y")
                    
                    # Ligne Banque
                    new_bank_entry = pd.DataFrame([{"Solde": 15000, "Nom Discord": add_discord, "Nom Roblox": add_roblox, "Date d'arrivée": date_du_jour, "Emploiement": "Civil"}])
                    # Ligne Permis
                    new_pts_entry = pd.DataFrame([{"Nom Roblox": add_roblox, "PTS": 25}])
                    
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, new_bank_entry], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_pts_entry], ignore_index=True))
                    st.success(f"Dossier créé pour {add_roblox} !"); time.sleep(1); st.rerun()

# ------------------------------------------------------------------------------
# ONGLET 3 : GESTION BANCAIRE (RECHERCHE HYBRIDE)
# ------------------------------------------------------------------------------
with tab_banque:
    st.header("💰 Console de Gestion Bancaire")
    
    # RECHERCHE HYBRIDE : ROBLOX OU DISCORD
    find_bank = st.text_input("🔍 Rechercher un Compte Bancaire (Nom Roblox OU Pseudo Discord)").lower()
    
    if find_bank:
        # Masque de recherche hybride sur les deux colonnes
        search_mask = (df_banque["Nom Roblox"].str.lower().str.contains(find_bank, na=False)) | \
                      (df_banque["Nom Discord"].str.lower().str.contains(find_bank, na=False))
        bank_results = df_banque[search_mask]
        
        for idx, row_bank in bank_results.iterrows():
            with st.container(border=True):
                st.subheader(f"Titulaire : {row_bank['Nom Roblox']}")
                st.write(f"🆔 Discord : {row_bank['Nom Discord']}")
                st.metric("Solde Bancaire", f"{float(row_bank['Solde']):,.0f} $")
                
                # ACTIONS DE TRANSACTION (RCT et Staff)
                if st.session_state.role in ["RCT", "Staff"]:
                    with st.expander("⚙️ Effectuer une Opération Financière"):
                        col_bank_1, col_bank_2 = st.columns(2)
                        with col_bank_1:
                            montant_tx = st.number_input("Montant ($)", min_value=1, key=f"tx_m_{idx}")
                            motif_tx = st.text_input("Motif de l'opération", key=f"tx_r_{idx}")
                        with col_bank_2:
                            plaque_tx = st.text_input("Plaque du véhicule concerné", key=f"tx_p_{idx}")
                        
                        if st.button("Confirmer le Débit", key=f"tx_btn_{idx}"):
                            # Calcul du nouveau solde
                            df_banque.at[idx, "Solde"] = float(row_bank["Solde"]) - montant_tx
                            
                            statut_action = "Fonds retirés / Détruits"
                            if st.session_state.role == "RCT":
                                # Redirection vers la banque RCT (une10000)
                                df_banque.loc[df_banque["Nom Roblox"] == TARGET_RCT, "Solde"] += montant_tx
                                statut_action = f"Virement automatique vers {TARGET_RCT}"
                            
                            # Mise à jour GSheet
                            conn.update(worksheet="Banque", data=df_banque)
                            
                            # GÉNÉRATION DU REÇU NOIR (TICKET)
                            st.markdown(f"""
                            <div class="ticket-fix">
                                🧾 <b>REÇU DE TRANSACTION BANCAIRE - RCRP</b><br>
                                --------------------------------------<br>
                                Titulaire : {row_bank['Nom Roblox']}<br>
                                Montant : {montant_tx}$<br>
                                Motif : {motif_op}<br>
                                Plaque : {plaque_tx}<br>
                                Statut : {statut_action}<br>
                                Horodatage : {datetime.now().strftime('%H:%M:%S')}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            time.sleep(1)
                            st.rerun()

# ==============================================================================
# PIED DE PAGE
# ==============================================================================
st.markdown("---")
st.markdown("<center><small>RCRP Management System v16.0 | 2026 | Système Gouvernemental de Gestion</small></center>", unsafe_allow_html=True)
