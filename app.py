import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# ======================================================================================
# 1. CONFIGURATION DE L'INTERFACE ET DE LA PAGE (PROPRIÉTÉS STREAMLIT)
# ======================================================================================
st.set_page_config(
    page_title="RCRP - Système de Gestion Intégral Professionnel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================================================
# 2. DESIGN ET STYLE CSS PERSONNALISÉ (DESIGN DARK & TICKETS)
# ======================================================================================
st.markdown("""
    <style>
    /* Ajustement de la zone de contenu principale */
    .main .block-container {
        padding-top: 5rem !important;
        padding-bottom: 5rem !important;
    }

    /* Style du Logo dans la barre latérale */
    [data-testid="stSidebar"] img {
        border-radius: 20px;
        width: 100% !important;
        margin-bottom: 20px;
        border: 2px solid #333;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }

    /* Style des Badges d'Assurance */
    .badge-assu {
        background-color: #ff4b4b;
        color: white;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
    }

    /* Style du Reçu Noir (Ticket de caisse) */
    .ticket-fix {
        background-color: #000000 !important;
        color: #00FF00 !important;
        padding: 30px;
        border: 2px dashed #ff4b4b;
        border-radius: 15px;
        font-family: 'Courier New', Courier, monospace;
        line-height: 1.6;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Boutons personnalisés */
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s;
        font-weight: bold;
    }
    
    /* Input style */
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# ======================================================================================
# 3. INITIALISATION DES SYSTÈMES ET VARIABLES DE SESSION
# ======================================================================================

# Gestion du rôle utilisateur (Civil, RCT, Staff)
if "role" not in st.session_state:
    st.session_state.role = None

# Connexion au Google Sheet (Database RCRP)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de connexion au serveur de données : {e}")

# Configuration des comptes de destination (Sauvegardé)
# Pour Averis, l'argent va à Moune2010
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"

# Codes de sécurité (Administration)
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"

# URL du Logo Officiel
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

# ======================================================================================
# 4. FONCTIONS DE CHARGEMENT DES DONNÉES (DATABASE)
# ======================================================================================

def fetch_bank_data():
    """Récupère les données bancaires depuis GSheet"""
    data = conn.read(worksheet="Banque", ttl=0)
    # Nettoyage des données vides
    df = data.dropna(how='all').fillna("")
    return df

def fetch_immat_data():
    """Récupère le registre des immatriculations depuis GSheet"""
    data = conn.read(worksheet="Copie de Immatriculations", ttl=0)
    # Nettoyage des données vides
    df = data.dropna(how='all').fillna("")
    return df

def fetch_points_data():
    """Récupère le registre des points de permis depuis GSheet"""
    data = conn.read(worksheet="Points Permis", ttl=0)
    # Nettoyage des données vides
    df = data.dropna(how='all').fillna("")
    return df

# Exécution du chargement initial des DataFrames
df_banque = fetch_bank_data()
df_im = fetch_immat_data()
df_pts = fetch_points_data()

# ======================================================================================
# 5. PORTAIL D'ACCÈS (AUTHENTIFICATION)
# ======================================================================================

if st.session_state.role is None:
    st.title("🏛️ Système de Gestion Centralisé - RCRP")
    st.subheader("Bienvenue sur l'interface officielle du Gouvernement et de la RCT.")
    
    st.write("---")
    
    # Création des trois colonnes d'accès pour les différents rôles
    col_access_1, col_access_2, col_access_3 = st.columns(3)
    
    with col_access_1:
        with st.container(border=True):
            st.header("👤 Civil")
            st.write("Accès citoyen standard.")
            st.write("Permet l'immatriculation et la consultation du registre public.")
            if st.button("Accéder au Portail Public", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()
                
    with col_access_2:
        with st.container(border=True):
            st.header("🛠️ Agent RCT")
            st.write("Espace réservé aux agents en service.")
            st.write("Veuillez saisir votre code d'habilitation.")
            input_code_rct = st.text_input("Code d'accès Agent", type="password", key="auth_rct")
            if st.button("Connexion Agent RCT", use_container_width=True):
                if input_code_rct == CODE_PRO:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("Code RCT non valide. Accès refusé.")
                    
    with col_access_3:
        with st.container(border=True):
            st.header("👮 Gouvernement")
            st.write("Haute sécurité (Staff).")
            st.write("Gestion des dossiers et de la banque centrale.")
            input_code_staff = st.text_input("Code Administrateur", type="password", key="auth_staff")
            if st.button("Connexion Administrateur", use_container_width=True):
                if input_code_staff == CODE_ADMIN:
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    st.error("Code Staff non valide. Alerte de sécurité.")
    st.stop()

# ======================================================================================
# 6. BARRE LATÉRALE (NAVIGATION ET HORLOGE TEMPS RÉEL)
# ======================================================================================

with st.sidebar:
    # Affichage du Logo Officiel
    st.image(LOGO_URL)
    
    st.markdown("---")
    
    # Récupération du temps actuel
    now = datetime.now()
    
    # Affichage de la Date
    st.write(f"📅 **Date du jour :**")
    st.info(now.strftime('%d / %m / %Y'))
    
    # Affichage de l'Heure
    st.write(f"⏰ **Heure du serveur :**")
    st.info(now.strftime('%H : %M : %S'))
    
    if st.button("🔄 Actualiser les données", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    
    # Statut de la session utilisateur
    st.write("👤 **Utilisateur :**")
    st.success(f"Mode {st.session_state.role} actif")
    
    if st.button("🚪 Déconnexion du système", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    
    st.divider()
    st.caption("Développé pour RCRP Management")
    st.caption("Version 16.7 - Février 2026")

# ======================================================================================
# 7. INTERFACE PRINCIPALE - GESTION DES ONGLETS
# ======================================================================================

tab_reg, tab_dos, tab_ban = st.tabs([
    "🚗 REGISTRE VÉHICULES", 
    "🪪 DOSSIERS CITOYENS", 
    "💰 BANQUE CENTRALE"
])

# --------------------------------------------------------------------------------------
# ONGLET 1 : REGISTRE DES VÉHICULES (IMMATRICULATIONS ET ASSURANCES)
# --------------------------------------------------------------------------------------

with tab_reg:
    st.header("🚗 Registre National des Immatriculations")
    
    # SECTION 1.1 : FORMULAIRE D'ACHAT (UNIQUEMENT POUR LES CIVILS)
    if st.session_state.role not in ["RCT", "Staff"]:
        with st.expander("➕ Enregistrer un nouveau véhicule (Achat Immatriculation)", expanded=True):
            
            # Mise en page du formulaire sur deux colonnes
            c_left, c_right = st.columns(2)
            
            with c_left:
                sel_proprio = st.selectbox("Titulaire du véhicule (Nom Roblox)", ["---"] + df_banque["Nom Roblox"].tolist())
                in_marque = st.text_input("Marque et Modèle du véhicule", placeholder="Ex: Mercedes-Benz AMG")
                in_plaque = st.text_input("Numéro de Plaque souhaité", placeholder="Ex: RC-123-RP")
            
            with c_right:
                sel_assu = st.selectbox("Sélectionner une Formule d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
                in_code = st.text_input("Code Secret de sécurité (Pour radiation future)", type="password")
            
            # --- BLOC DE LOGIQUE : CALCUL DES FRAIS DÉTAILLÉS ---
            
            # 1. Frais de dossier fixes
            frais_base = 175
            
            # 2. Initialisation des variables de calcul
            frais_assurance = 0
            taxe_jeune = 0
            
            # 3. Calcul du prix de l'assurance selon le choix
            if "AVERIS" in sel_assu:
                frais_assurance = 130
            elif "RCT" in sel_assu:
                frais_assurance = 150
            
            # 4. Application de l'Offre Commerciale Trio RCT (2 achetées, la 3ème est gratuite)
            # On compte combien de véhicules le citoyen possède déjà avec l'assurance RCT
            veh_rct_check = df_im[(df_im["Nom d'utilisateur ROBLOX"] == sel_proprio) & (df_im["Assurance"].str.contains("RCT"))]
            
            if "RCT" in sel_assu and len(veh_rct_check) >= 2:
                # Si déjà 2 véhicules RCT, le 3ème est gratuit au niveau assurance
                frais_assurance = 0
                st.info("💡 **PROMOTION :** Offre Trio RCT appliquée ! L'assurance de ce 3ème véhicule est offerte.")
            
            # 5. Calcul de la Taxe Jeune Conducteur (Moins de 30 jours de ville)
            if sel_proprio != "---":
                user_record = df_banque[df_banque["Nom Roblox"] == sel_proprio]
                try:
                    # Conversion de la date d'arrivée en objet datetime
                    date_arrivee_str = str(user_record.iloc[0]["Date d'arrivée"])
                    date_arr_dt = datetime.strptime(date_arrivee_str, "%d/%m/%Y")
                    
                    # Calcul de l'ancienneté en jours
                    anciennete = (datetime.now() - date_arr_dt).days
                    
                    if anciennete < 30:
                        taxe_jeune = 50
                        st.warning("⚠️ **TAXE :** Nouveau citoyen détecté (-30 jours). Taxe de 50$ appliquée.")
                except Exception as e:
                    # En cas d'erreur de format de date, on ne taxe pas par défaut
                    pass
            
            # 6. Somme totale finale
            total_facture = frais_base + frais_assurance + taxe_jeune
            
            # --- AFFICHAGE DU REÇU (STYLE TICKET CAISSE) ---
            
            st.markdown(f"""
            <div class="ticket-fix">
                🧾 <b>PRÉ-VISUALISATION DE VOTRE FACTURE</b><br>
                ------------------------------------------------<br>
                Titulaire : {sel_proprio}<br>
                Véhicule : {in_marque}<br>
                Plaque : {in_plaque}<br>
                ------------------------------------------------<br>
                Frais d'immatriculation : 175$<br>
                Assurance choisie : {frais_assurance}$<br>
                Taxe Jeune Conducteur : {taxe_jeune}$<br>
                ------------------------------------------------<br>
                <b>MONTANT TOTAL À RÉGLER : {total_facture}$</b>
            </div>
            """, unsafe_allow_html=True)
            
if st.button("💳 Procéder au Paiement et à l'Enregistrement", use_container_width=True):
                # Vérification que les champs sont remplis
                if sel_proprio == "---" or not in_plaque or not in_code:
                    st.error("Erreur : Veuillez remplir tous les champs du formulaire.")
                else:
                    # Récupération sécurisée du solde
                    idx_b = df_banque[df_banque["Nom Roblox"] == sel_proprio].index[0]
                    
                    try:
                        # Nettoyage des caractères invisibles (fréquent sur Mac)
                        val_brute = str(df_banque.at[idx_b, "Solde"]).replace('$', '').replace(' ', '').replace(',', '')
                        solde_actuel = float(val_brute) if val_brute != "" else 0.0
                    except:
                        st.error("⚠️ Format bancaire invalide dans le GSheet (caractères non numériques).")
                        st.stop()
                    
                    if solde_actuel >= total_facture:
                        # ÉTAPE A : Débit du compte du citoyen
                        df_banque.at[idx_b, "Solde"] = solde_actuel - total_facture
                        
                        # ÉTAPE B : Virement vers l'assurance correspondante
                        if frais_assurance > 0:
                            target_compte = TARGET_AVERIS if "AVERIS" in sel_assu else TARGET_RCT
                            if target_compte in df_banque["Nom Roblox"].values:
                                idx_target = df_banque[df_banque["Nom Roblox"] == target_compte].index[0]
                                try:
                                    val_cible = str(df_banque.at[idx_target, "Solde"]).replace('$', '').replace(' ', '').replace(',', '')
                                    solde_cible = float(val_cible) if val_cible != "" else 0.0
                                    df_banque.at[idx_target, "Solde"] = solde_cible + frais_assurance
                                except:
                                    df_banque.at[idx_target, "Solde"] = frais_assurance
                        
                        # ÉTAPE C : Création de la nouvelle ligne dans le registre immat
                        new_vehicule_entry = pd.DataFrame([{
                            "Horodateur": now.strftime("%d/%m/%Y"),
                            "Nom d'utilisateur ROBLOX": sel_proprio,
                            "Marque du véhicule": in_marque,
                            "Numéro de la plaque": in_plaque,
                            "Assurance": sel_assu,
                            "CODE": str(in_code)
                        }])
                        
                        # ÉTAPE D : Synchronisation avec Google Sheets
                        try:
                            conn.update(worksheet="Banque", data=df_banque)
                            conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_vehicule_entry], ignore_index=True))
                            st.success("Transaction terminée ! Votre véhicule est désormais enregistré.")
                            time.sleep(1.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur lors de l'envoi vers Google Sheets : {e}")
                    else:
                        st.error("Transaction échouée : Votre solde bancaire est insuffisant.")

# --- ON SORT DE TOUS LES BLOCS PRÉCÉDENTS : RETOUR À LA LIGNE ZÉRO ---

st.divider()
st.subheader("🔍 Consultation du Registre Public")

# Barre de recherche dynamique
search_query = st.text_input("Rechercher par Numéro de Plaque ou par Nom de Propriétaire").lower()
    # Barre de recherche dynamique
    search_query = st.text_input("Rechercher par Numéro de Plaque ou par Nom de Propriétaire").lower()
    
    # Parcours et affichage des véhicules
    for i, row in df_im.iterrows():
        # Variables de filtrage
        nom_db = str(row['Nom d\'utilisateur ROBLOX']).lower()
        plaque_db = str(row['Numéro de la plaque']).lower()
        
        # Filtre de recherche
        if search_query in nom_db or search_query in plaque_db:
            with st.container(border=True):
                # Mise en page en colonnes pour l'affichage
                col_i1, col_i2, col_i3 = st.columns([2, 2, 1])
                
                with col_i1:
                    # AFFICHAGE DU NUMÉRO DE PLAQUE (IMPORTANT)
                    st.write(f"🆔 **PLAQUE : {row['Numéro de la plaque']}**")
                    st.write(f"🚗 Marque : {row['Marque du véhicule']}")
                
                with col_i2:
                    st.write(f"👤 Propriétaire : **{row['Nom d\'utilisateur ROBLOX']}**")
                    st.write(f"📅 Enregistré le : {row['Horodateur']}")
                
                with col_i3:
                    # Affichage du type d'assurance sous forme de badge
                    st.markdown(f"<span class='badge-assu'>{row['Assurance']}</span>", unsafe_allow_html=True)
                
                # SECTION DE RADIATION (SUPPRESSION)
                with st.expander("⚙️ Options de gestion du véhicule"):
                    st.write("Pour radier un véhicule, veuillez saisir son code secret.")
                    
                    col_rad_1, col_rad_2 = st.columns(2)
                    
                    with col_rad_1:
                        check_code_sec = st.text_input("Code Secret", type="password", key=f"del_key_{i}")
                        
                    with col_rad_2:
                        # Seul le détenteur du code ou le Staff peut supprimer
                        if st.button("🚫 Confirmer la Radiation", key=f"del_btn_{i}", use_container_width=True):
                            if check_code_sec == str(row['CODE']) or st.session_state.role == "Staff":
                                # Suppression de la ligne et mise à jour
                                updated_immat_df = df_im.drop(i)
                                conn.update(worksheet="Copie de Immatriculations", data=updated_immat_df)
                                st.success("Le véhicule a été retiré du registre national.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Code de sécurité incorrect. Radiation refusée.")

# --------------------------------------------------------------------------------------
# ONGLET 2 : DOSSIERS CITOYENS (GESTION ADMINISTRATIVE)
# --------------------------------------------------------------------------------------

with tab_dos:
    st.header("🪪 Dossiers Administratifs des Citoyens")
    
    # SECTION 2.1 : SYSTÈME DE PAYE ET TAXES (ACCÈS STAFF UNIQUEMENT)
    if st.session_state.role == "Staff":
        with st.container(border=True):
            st.subheader("🏦 Console de Paye et Prélèvements Automatisés")
            st.write("Ce système permet de distribuer les salaires et de prélever les assurances mensuelles.")
            
            if st.button("🧧 EXECUTER LA PROCÉDURE DE PAYE TOTALE", use_container_width=True):
                with st.status("Exécution des transactions bancaires en cours..."):
                    
                    # A. DISTRIBUTION DES SALAIRES
                    st.write("1. Calcul des salaires par poste...")
                    for idx, citoyen in df_banque.iterrows():
                        # Définition du salaire (RCT = 17k, Autres = 15k)
                        poste = str(citoyen["Emploiement"]).upper()
                        montant_salaire = 17000 if "RCT" in poste else 15000
                        
                        # Crédit du solde
                        df_banque.at[idx, "Solde"] = float(citoyen["Solde"]) + montant_salaire
                    
                    # B. PRÉLÈVEMENTS DES ASSURANCES ET REDIRECTIONS
                    st.write("2. Prélèvements des cotisations d'assurance...")
                    # Dictionnaire pour gérer le Trio RCT (2 payantes, les suivantes gratuites lors de la paye)
                    compteur_rct_paye = {}
                    
                    for _, vehicule in df_im.iterrows():
                        proprietaire_nom = vehicule["Nom d'utilisateur ROBLOX"]
                        
                        # On vérifie si le propriétaire existe en banque
                        if proprietaire_nom in df_banque["Nom Roblox"].values:
                            idx_banque_citoyen = df_banque[df_banque["Nom Roblox"] == proprietaire_nom].index[0]
                            type_assu = vehicule["Assurance"]
                            
                            # Logique RCT
                            if "RCT" in type_assu:
                                # On incrémente le compteur pour ce citoyen
                                compteur_rct_paye[proprietaire_nom] = compteur_rct_paye.get(proprietaire_nom, 0) + 1
                                
                                # Seuls les deux premiers véhicules sont facturés lors de la paye
                                if compteur_rct_paye[proprietaire_nom] <= 2:
                                    df_banque.at[idx_banque_citoyen, "Solde"] -= 150
                                    # Virement vers le compte RCT (une10000)
                                    df_banque.loc[df_banque["Nom Roblox"] == TARGET_RCT, "Solde"] += 150
                            
                            # Logique AVERIS
                            elif "AVERIS" in type_assu:
                                df_banque.at[idx_banque_citoyen, "Solde"] -= 130
                                # Virement vers le compte Averis (Moune2010)
                                df_banque.loc[df_banque["Nom Roblox"] == TARGET_AVERIS, "Solde"] += 130
                    
                    # ÉTAPE FINALE : Mise à jour globale de la feuille Banque
                    conn.update(worksheet="Banque", data=df_banque)
                    st.success("La paye globale et les prélèvements ont été effectués avec succès !")
                    time.sleep(2)
                    st.rerun()

    # SECTION 2.2 : RECHERCHE DE DOSSIER (HYBRIDE ROBLOX / DISCORD)
    
    st.divider()
    st.subheader("🔍 Consultation des Dossiers Citoyens")
    
    # Barre de recherche hybride (Permet de chercher par Discord également)
    search_dos = st.text_input("Saisir le Nom Roblox ou le Pseudo Discord à rechercher", key="search_dos_input").lower()
    
    if search_dos:
        # Création du masque de recherche sur deux colonnes
        mask_dos = (df_banque["Nom Roblox"].str.lower().str.contains(search_dos, na=False)) | \
                   (df_banque["Nom Discord"].str.lower().str.contains(search_dos, na=False))
        
        resultats_dossiers = df_banque[mask_dos]
        
        if not resultats_dossiers.empty:
            for idx, citoyen_row in resultats_dossiers.iterrows():
                with st.container(border=True):
                    # Titre du dossier
                    st.subheader(f"Dossier Civil de : {citoyen_row['Nom Roblox']}")
                    
                    col_d1, col_d2 = st.columns(2)
                    
                    with col_d1:
                        st.write(f"🆔 **Pseudo Discord :** {citoyen_row['Nom Discord']}")
                        st.write(f"📌 **Emploiement :** {citoyen_row['Emploiement']}")
                    
                    with col_d2:
                        st.write(f"📅 **Date d'arrivée en ville :** {citoyen_row['Date d\'arrivée']}")
                        st.write(f"💰 **Solde Bancaire Actuel :** {float(citoyen_row['Solde']):,.0f} $")
                    
                    st.divider()
                    
                    # SYSTÈME DE POINTS DE PERMIS (RECUPÉRATION)
                    permis_record = df_pts[df_pts["Nom Roblox"] == citoyen_row["Nom Roblox"]]
                    
                    if not permis_record.empty:
                        points_actuels = permis_record.iloc[0]['PTS']
                        
                        # Affichage du score
                        st.metric("Points de Permis de Conduire (sur 25)", f"{points_actuels} / 25")
                        
                        # Modification des points (Staff uniquement)
                        if st.session_state.role == "Staff":
                            with st.expander("✏️ Modifier le capital de points"):
                                new_pts_val = st.number_input("Nouveau solde de points", min_value=0, max_value=25, value=int(points_actuels), key=f"pts_edit_{idx}")
                                if st.button("Sauvegarder les points", key=f"pts_save_{idx}"):
                                    # Mise à jour locale
                                    df_pts.loc[df_pts["Nom Roblox"] == citoyen_row["Nom Roblox"], "PTS"] = new_pts_val
                                    # Mise à jour GSheet
                                    conn.update(worksheet="Points Permis", data=df_pts)
                                    st.success("Capital de points mis à jour dans la base de données.")
                                    st.rerun()
        else:
            st.info("Aucun citoyen trouvé avec ces critères de recherche.")

    # SECTION 2.3 : CRÉATION DE PROFIL (STAFF UNIQUEMENT)
    
    if st.session_state.role == "Staff":
        st.divider()
        with st.expander("👤 Ajouter un Nouveau Citoyen à la Base de Données"):
            st.write("Ce formulaire crée un compte bancaire et un dossier de permis.")
            
            with st.form("form_creation_citoyen"):
                f_nom_rob = st.text_input("Nom d'utilisateur Roblox (Identifiant exact)")
                f_nom_dis = st.text_input("Identifiant Discord")
                f_job = st.selectbox("Type d'emploiement", ["Civil", "Agent RCT", "Staff Gouvernement"])
                
                if st.form_submit_button("Valider la Création du Profil"):
                    if f_nom_rob and f_nom_dis:
                        # AJOUT AUTOMATIQUE DE LA DATE DE CRÉATION
                        date_creation_auto = now.strftime("%d/%m/%Y")
                        
                        # A. Préparation de l'entrée Banque (Prime d'arrivée de 15,000$)
                        new_bank_line = pd.DataFrame([{
                            "Solde": 15000,
                            "Nom Discord": f_nom_dis,
                            "Nom Roblox": f_nom_rob,
                            "Date d'arrivée": date_creation_auto,
                            "Emploiement": f_job
                        }])
                        
                        # B. Préparation de l'entrée Permis (25 points de base)
                        new_pts_line = pd.DataFrame([{
                            "Nom Roblox": f_nom_rob,
                            "PTS": 25
                        }])
                        
                        # C. Envoi vers GSheets
                        conn.update(worksheet="Banque", data=pd.concat([df_banque, new_bank_line], ignore_index=True))
                        conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_pts_line], ignore_index=True))
                        
                        st.success(f"Profil créé avec succès pour {f_nom_rob} ! Date enregistrée : {date_creation_auto}")
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("Veuillez remplir les informations obligatoires.")

# --------------------------------------------------------------------------------------
# ONGLET 3 : BANQUE CENTRALE (OPÉRATIONS FINANCIÈRES)
# --------------------------------------------------------------------------------------

with tab_ban:
    st.header("💰 Gestion Bancaire et Flux Financiers")
    st.write("Interface de contrôle des comptes et des transactions inter-organisations.")
    
    # RECHERCHE HYBRIDE BANQUE
    search_bank_main = st.text_input("🔍 Rechercher un compte (Nom Roblox ou Discord)", key="bank_search_main").lower()
    
    if search_bank_main:
        # Masque de recherche hybride sur les deux colonnes
        mask_bank_search = (df_banque["Nom Roblox"].str.lower().str.contains(search_bank_main, na=False)) | \
                           (df_banque["Nom Discord"].str.lower().str.contains(search_bank_main, na=False))
        
        resultats_banque = df_banque[mask_bank_search]
        
        for idx, bank_row in resultats_banque.iterrows():
            with st.container(border=True):
                # Affichage des informations bancaires
                st.subheader(f"Compte de : {bank_row['Nom Roblox']}")
                
                # Metric pour le solde
                st.metric("Solde Bancaire Disponible", f"{float(bank_row['Solde']):,.0f} $")
                
                # SECTION DES OPÉRATIONS (RESERVÉ RCT ET STAFF)
                if st.session_state.role in ["RCT", "Staff"]:
                    with st.expander("⚙️ Effectuer une Opération Financière (Débit)"):
                        st.write("Saisissez les détails de l'opération ci-dessous.")
                        
                        col_ban_1, col_ban_2 = st.columns(2)
                        
                        with col_ban_1:
                            montant_operation = st.number_input("Montant à débiter ($)", min_value=1, key=f"tx_val_{idx}")
                            motif_operation = st.text_input("Motif du prélèvement", placeholder="Ex: Amende, Taxes spéciales...", key=f"tx_mot_{idx}")
                            
                        with col_ban_2:
                            plaque_concernee = st.text_input("Numéro de Plaque (Si applicable)", key=f"tx_pla_{idx}")
                            st.write("L'argent sera automatiquement redirigé vers le compte organisationnel.")
                        
                        if st.button("Confirmer le Débit", key=f"tx_btn_{idx}", use_container_width=True):
                            # Étape 1 : Calcul et mise à jour locale du solde
                            ancien_solde = float(bank_row["Solde"])
                            nouveau_solde = ancien_solde - montant_operation
                            df_banque.at[idx, "Solde"] = nouveau_solde
                            
                            # Texte de statut pour le reçu
                            statut_transfert = "Fonds retirés / Détruits"
                            
                            # Étape 2 : Virement RCT automatique (Si l'agent est RCT)
                            if st.session_state.role == "RCT":
                                # Redirection vers le compte une10000
                                df_banque.loc[df_banque["Nom Roblox"] == TARGET_RCT, "Solde"] += montant_operation
                                statut_transfert = f"Virement automatique vers compte RCT ({TARGET_RCT})"
                            
                            # Étape 3 : Mise à jour GSheet
                            conn.update(worksheet="Banque", data=df_banque)
                            
                            # Étape 4 : GÉNÉRATION DU REÇU NOIR (STYLE TICKET)
                            st.markdown(f"""
                            <div class="ticket-fix">
                                🧾 <b>REÇU OFFICIEL DE TRANSACTION BANCAIRE</b><br>
                                ------------------------------------------------<br>
                                Titulaire du compte : {bank_row['Nom Roblox']}<br>
                                Montant débité : {montant_operation}$<br>
                                Motif : {motif_operation}<br>
                                Référence Plaque : {plaque_concernee}<br>
                                ------------------------------------------------<br>
                                Statut : {statut_transfert}<br>
                                Horodatage : {datetime.now().strftime('%H:%M:%S')}<br>
                                Signature : Administration RCRP
                            </div>
                            """, unsafe_allow_html=True)
                            
                            time.sleep(2)
                            st.rerun()

# ======================================================================================
# 8. PIED DE PAGE ET INFORMATIONS LÉGALES
# ======================================================================================

st.markdown("---")
st.markdown("<center><small>RCRP Management System v16.7 | Base de Données Sécurisée | Propriété du Gouvernement RCRP 2026</small></center>", unsafe_allow_html=True)
st.markdown("<center><small>Toute utilisation frauduleuse est passible de sanctions administratives.</small></center>", unsafe_allow_html=True)

# FIN DU SCRIPT (TOTAL 485 LIGNES)
