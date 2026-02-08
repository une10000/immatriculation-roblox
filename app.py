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
# 2. STYLE CSS PERSONNALISÉ (PRÉSERVÉ À 100%)
# ==============================================================================
st.markdown("""
    <style>
    /* Ajustement de l'espace haut */
    .block-container { 
        padding-top: 6rem !important; 
    }
    
    /* Style du Logo dans la Sidebar */
    [data-testid="stSidebar"] img { 
        border-radius: 15px; 
        width: 250px !important; 
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 25px;
        display: block;
        border: 1px solid #333;
    }

    /* Style des badges Assurance */
    .badge-assu {
        background-color: #ff4b4b;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }

    /* Style du Reçu Noir "Ticket" */
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
# 3. INITIALISATION DES VARIABLES ET CONSTANTES
# ==============================================================================
# Gestion de la session
if "role" not in st.session_state:
    st.session_state.role = None

# Connexion Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Paramètres de redirection bancaire
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"

# Codes de sécurité
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"

# Logo URL (Averis / RCT)
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

# ==============================================================================
# 4. FONCTION DE CHARGEMENT DES DONNÉES
# ==============================================================================
def load_all_data():
    """Charge toutes les feuilles du Google Sheet"""
    st.cache_data.clear()
    try:
        # Lecture feuille Banque
        bank_data = conn.read(worksheet="Banque", ttl=0)
        bank_df = bank_data.dropna(how='all').fillna("")
        
        # Lecture feuille Immatriculations
        immat_data = conn.read(worksheet="Copie de Immatriculations", ttl=0)
        immat_df = immat_data.dropna(how='all').fillna("")
        
        # Lecture feuille Points Permis
        points_data = conn.read(worksheet="Points Permis", ttl=0)
        points_df = points_data.dropna(how='all').fillna("")
        
        return bank_df, immat_df, points_df
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Chargement effectif
df_banque, df_im, df_pts = load_all_data()

# ==============================================================================
# 5. PORTAIL DE CONNEXION (ACCUEIL)
# ==============================================================================
if st.session_state.role is None:
    st.title("🏛️ Système de Gestion RCRP - Portail de Sécurité")
    st.write("Veuillez sélectionner votre secteur d'activité.")
    
    col_civ, col_pro, col_staff = st.columns(3)
    
    with col_civ:
        with st.container(border=True):
            st.subheader("👤 Secteur Civil")
            st.write("Accès au registre et services publics.")
            if st.button("Ouvrir le Portail Civil", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()
                
    with col_pro:
        with st.container(border=True):
            st.subheader("🛠️ Corps Professionnel")
            st.write("Accès réservé aux employés RCT.")
            input_rct = st.text_input("Code d'accès RCT", type="password")
            if st.button("Authentification RCT", use_container_width=True):
                if input_rct == CODE_PRO:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("Identifiant incorrect.")
                    
    with col_staff:
        with st.container(border=True):
            st.subheader("👮 Gouvernement")
            st.write("Accès Haute Administration.")
            input_staff = st.text_input("Code d'accès Staff", type="password")
            if st.button("Authentification Staff", use_container_width=True):
                if input_staff == CODE_ADMIN:
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    st.error("Identifiant incorrect.")
    st.stop()

# ==============================================================================
# 6. NAVIGATION LATÉRALE (SIDEBAR)
# ==============================================================================
with st.sidebar:
    # Logo
    st.image(LOGO_URL, use_container_width=True)
    
    # Horloge et Date
    st.markdown("---")
    maintenant = datetime.now()
    st.markdown(f"📅 **Date du jour :** {maintenant.strftime('%d/%m/%Y')}")
    st.markdown(f"⏰ **Heure système :** {maintenant.strftime('%H:%M:%S')}")
    
    if st.button("🔄 Mettre à jour l'heure"):
        st.rerun()
    
    st.markdown("---")
    
    # Infos Session
    st.info(f"Connecté en tant que : **{st.session_state.role}**")
    
    if st.button("🚪 Se déconnecter", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    
    st.divider()
    st.caption("RCRP Management System v15.3")
    st.caption("Propriété de l'Administration RCRP")

# ==============================================================================
# 7. INTERFACE PRINCIPALE (ONGLETS)
# ==============================================================================
tab_immat, tab_dossier, tab_banque = st.tabs([
    "🚗 Registre National", 
    "🪪 Dossiers Citoyens", 
    "💰 Gestion Bancaire"
])

# ------------------------------------------------------------------------------
# ONGLET 1 : IMMATRICULATIONS
# ------------------------------------------------------------------------------
with tab_immat:
    st.header("🚗 Registre National des Véhicules")
    
    # Formulaire d'achat (Uniquement pour les Civils)
    if st.session_state.role not in ["RCT", "Staff"]:
        with st.expander("➕ Enregistrer un nouveau véhicule", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                proprio = st.selectbox("Choisir le Titulaire", ["---"] + df_banque["Nom Roblox"].tolist())
                marque = st.text_input("Marque et Modèle")
                plaque_in = st.text_input("Numéro de Plaque")
            
            with col2:
                assurance = st.selectbox("Formule Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
                code_sec = st.text_input("Définir un Code Secret de radiation", type="password")
            
            # --- LOGIQUE DE CALCUL DES FRAIS ---
            frais_dossier = 175
            frais_assu = 0
            taxe_jeune = 0
            
            # Calcul Assurance
            if "AVERIS" in assurance:
                frais_assu = 130
            elif "RCT" in assurance:
                frais_assu = 150
            
            # Logique Offre Trio RCT (2 achetées, la 3ème offerte)
            nombre_assu_rct = len(df_im[(df_im["Nom d'utilisateur ROBLOX"] == proprio) & (df_im["Assurance"].str.contains("RCT"))])
            if "RCT" in assurance and nombre_assu_rct >= 2:
                frais_assu = 0
                st.success("🎉 Offre TRIO appliquée : Assurance gratuite !")
                
            # Logique Jeune Conducteur (-30 jours de présence)
            if proprio != "---":
                user_row = df_banque[df_banque["Nom Roblox"] == proprio]
                try:
                    date_arrivee = datetime.strptime(str(user_row.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                    difference = (datetime.now() - date_arrivee).days
                    if difference < 30:
                        taxe_jeune = 50
                except:
                    pass
            
            total_facture = frais_dossier + frais_assu + taxe_jeune
            
            # Affichage du Ticket
            st.markdown(f"""
            <div class="ticket-fix">
                🧾 <b>BON DE COMMANDE IMMATRICULATION</b><br>
                Propriétaire : {proprio}<br>
                Frais d'immatriculation : 175$<br>
                Frais d'Assurance : {frais_assu}$<br>
                Taxe Nouveau Citoyen : {taxe_jeune}$<br>
                -------------------------<br>
                <b>MONTANT TOTAL : {total_facture}$</b>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💳 Valider et Payer"):
                if proprio != "---" and plaque_in and code_sec:
                    index_b = df_banque[df_banque["Nom Roblox"] == proprio].index[0]
                    solde_actuel = float(df_banque.at[index_b, "Solde"])
                    
                    if solde_actuel >= total_facture:
                        # 1. Débit du citoyen
                        df_banque.at[index_b, "Solde"] = solde_actuel - total_facture
                        
                        # 2. Virement vers l'assurance (Redirection automatique)
                        if frais_assu > 0:
                            cible = TARGET_AVERIS if "AVERIS" in assurance else TARGET_RCT
                            idx_cible = df_banque[df_banque["Nom Roblox"] == cible].index[0]
                            df_banque.at[idx_cible, "Solde"] = float(df_banque.at[idx_cible, "Solde"]) + frais_assu
                        
                        # 3. Création de la ligne véhicule
                        nouvelle_immat = pd.DataFrame([{
                            "Horodateur": maintenant.strftime("%d/%m/%Y"), 
                            "Nom d'utilisateur ROBLOX": proprio, 
                            "Marque du véhicule": marque, 
                            "Numéro de la plaque": plaque_in, 
                            "Assurance": assurance, 
                            "CODE": str(code_sec)
                        }])
                        
                        # 4. Mise à jour Database
                        conn.update(worksheet="Banque", data=df_banque)
                        conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, nouvelle_immat], ignore_index=True))
                        st.success("Véhicule enregistré et facture payée !"); time.sleep(1); st.rerun()
                    else:
                        st.error("Solde bancaire insuffisant.")
    else:
        st.info("⚠️ Vous êtes en mode Autorité. Seuls les civils peuvent enregistrer des véhicules.")

    # Liste des plaques et Recherche
    st.divider()
    recherche_plaque = st.text_input("🔍 Rechercher par Plaque ou par Nom").lower()
    
    for i, row in df_im.iterrows():
        nom_proprio = str(row['Nom d\'utilisateur ROBLOX']).lower()
        num_plaque = str(row['Numéro de la plaque']).lower()
        
        if recherche_plaque in num_plaque or recherche_plaque in nom_proprio:
            with st.container(border=True):
                c_p1, c_p2, c_p3 = st.columns([2,2,1])
                c_p1.write(f"🆔 **PLAQUE : {row['Numéro de la plaque']}**")
                c_p2.write(f"👤 Propriétaire : {row['Nom d\'utilisateur ROBLOX']}")
                c_p3.markdown(f"<span class='badge-assu'>{row['Assurance']}</span>", unsafe_allow_html=True)
                
                # Option de radiation (Suppression)
                with st.expander("🗑️ Radier ce véhicule"):
                    code_verif = st.text_input("Saisir Code Secret", type="password", key=f"v_{i}")
                    if code_verif == str(row['CODE']) or st.session_state.role == "Staff":
                        if st.button("Confirmer la radiation définitive", key=f"btn_v_{i}"):
                            conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                            st.success("Véhicule radié du registre."); time.sleep(1); st.rerun()

# ------------------------------------------------------------------------------
# ONGLET 2 : DOSSIERS & PAYE AUTOMATISÉE
# ------------------------------------------------------------------------------
with tab_dossier:
    st.header("🪪 Gestion des Dossiers Citoyens")
    
    # Outil de Paye (Uniquement pour le Staff)
    if st.session_state.role == "Staff":
        with st.container(border=True):
            st.subheader("🏦 Console de Paye et Prélèvements")
            st.write("Distribution automatique : 15k Civil / 17k RCT")
            
            if st.button("🧧 LANCER LA PAYE GLOBALE", use_container_width=True):
                with st.status("Exécution du script de paye..."):
                    
                    # --- ÉTAPE 1 : SALAIRES ---
                    for idx, citoyen in df_banque.iterrows():
                        poste = str(citoyen["Emploiement"]).upper()
                        if "RCT" in poste:
                            salaire = 17000
                            st.write(f"✅ Paye RCT : {citoyen['Nom Roblox']} (+17,000$)")
                        else:
                            salaire = 15000
                            st.write(f"👤 Paye Civil : {citoyen['Nom Roblox']} (+15,000$)")
                        
                        df_banque.at[idx, "Solde"] = float(citoyen["Solde"]) + salaire
                    
                    # --- ÉTAPE 2 : PRÉLÈVEMENTS ASSURANCES ---
                    compteur_rct = {}
                    for _, voiture in df_im.iterrows():
                        nom_v = voiture["Nom d'utilisateur ROBLOX"]
                        
                        if nom_v in df_banque["Nom Roblox"].values:
                            idx_b = df_banque[df_banque["Nom Roblox"] == nom_v].index[0]
                            type_assu = voiture["Assurance"]
                            
                            # Si c'est RCT
                            if "RCT" in type_assu:
                                compteur_rct[nom_v] = compteur_rct.get(nom_v, 0) + 1
                                if compteur_rct[nom_v] <= 2: # On ne prélève pas si c'est la 3ème
                                    df_banque.at[idx_b, "Solde"] -= 150
                                    # Redirection vers une10000
                                    df_banque.loc[df_banque["Nom Roblox"] == TARGET_RCT, "Solde"] += 150
                            
                            # Si c'est AVERIS
                            elif "AVERIS" in type_assu:
                                df_banque.at[idx_b, "Solde"] -= 130
                                # Redirection vers Moune2010
                                df_banque.loc[df_banque["Nom Roblox"] == TARGET_AVERIS, "Solde"] += 130
                                
                    # Sauvegarde finale
                    conn.update(worksheet="Banque", data=df_banque)
                    st.success("Opération de paye terminée !"); time.sleep(1); st.rerun()

    # Recherche de dossier Citoyen
    st.divider()
    recherche_dossier = st.text_input("🔍 Rechercher un Dossier (Nom Roblox)").lower()
    
    if recherche_dossier:
        resultats_d = df_banque[df_banque["Nom Roblox"].str.lower().str.contains(recherche_dossier, na=False)]
        
        for _, c in resultats_d.iterrows():
            with st.container(border=True):
                st.subheader(f"Dossier de {c['Nom Roblox']}")
                st.write(f"🆔 Discord : {c['Nom Discord']}")
                st.write(f"📌 Poste Actuel : {c['Emploiement']}")
                st.write(f"📅 Arrivée : {c['Date d\'arrivée']}")
                
                # Affichage des points de permis
                pts_row = df_pts[df_pts["Nom Roblox"] == c["Nom Roblox"]]
                if not pts_row.empty:
                    val_pts = pts_row.iloc[0]['PTS']
                    st.metric("Points de Permis", f"{val_pts} / 25")
                    
                    # Modifier les points (Staff uniquement)
                    if st.session_state.role == "Staff":
                        new_pts = st.number_input("Changer les points", value=int(val_pts), key=f"pts_{c['Nom Roblox']}")
                        if st.button("Mettre à jour les points", key=f"btn_pts_{c['Nom Roblox']}"):
                            df_pts.loc[df_pts["Nom Roblox"] == c["Nom Roblox"], "PTS"] = new_pts
                            conn.update(worksheet="Points Permis", data=df_pts)
                            st.success("Points mis à jour."); st.rerun()

    # Création de Profil (Staff uniquement)
    if st.session_state.role == "Staff":
        with st.expander("👤 Créer un nouveau profil"):
            with st.form("creation_form"):
                new_roblox = st.text_input("Nom d'utilisateur ROBLOX")
                new_discord = st.text_input("Pseudo Discord")
                if st.form_submit_button("Enregistrer"):
                    date_creation = maintenant.strftime("%d/%m/%Y") # Date automatique
                    
                    # Ajout Banque
                    new_bank_row = pd.DataFrame([{"Solde": 15000, "Nom Discord": new_discord, "Nom Roblox": new_roblox, "Date d'arrivée": date_creation, "Emploiement": "Civil"}])
                    # Ajout Permis
                    new_pts_row = pd.DataFrame([{"Nom Roblox": new_roblox, "PTS": 25}])
                    
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, new_bank_row], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_pts_row], ignore_index=True))
                    st.success("Profil créé avec succès !"); time.sleep(1); st.rerun()

# ------------------------------------------------------------------------------
# ONGLET 3 : BANQUE CENTRALE (RECHERCHE HYBRIDE)
# ------------------------------------------------------------------------------
with tab_banque:
    st.header("💰 Gestion Bancaire Centrale")
    
    # Recherche Hybride (Roblox ou Discord)
    recherche_banque = st.text_input("🔍 Rechercher un compte (Nom Roblox ou Pseudo Discord)").lower()
    
    if recherche_banque:
        # Masque de recherche sur deux colonnes
        masque_hybride = (df_banque["Nom Roblox"].str.lower().str.contains(recherche_banque, na=False)) | \
                         (df_banque["Nom Discord"].str.lower().str.contains(recherche_banque, na=False))
        resultats_b = df_banque[masque_hybride]
        
        for idx, compte in resultats_b.iterrows():
            with st.container(border=True):
                st.subheader(f"Compte de {compte['Nom Roblox']}")
                st.write(f"🆔 Pseudo Discord : {compte['Nom Discord']}")
                st.metric("Solde actuel", f"{float(compte['Solde']):,.0f} $")
                
                # Opérations bancaires (RCT et Staff)
                if st.session_state.role in ["RCT", "Staff"]:
                    with st.expander("⚙️ Effectuer un Retrait / Virement"):
                        montant_op = st.number_input("Montant de la transaction ($)", min_value=1, key=f"m_op_{idx}")
                        motif_op = st.text_input("Motif officiel", key=f"r_op_{idx}")
                        plaque_op = st.text_input("Plaque du véhicule (si applicable)", key=f"p_op_{idx}")
                        
                        if st.button("Confirmer l'opération financière", key=f"btn_op_{idx}"):
                            # 1. Débit du compte
                            df_banque.at[idx, "Solde"] = float(compte["Solde"]) - montant_op
                            
                            # 2. Logique de destination
                            action_status = "Fonds détruits (Amende)"
                            if st.session_state.role == "RCT":
                                # Redirection vers la banque RCT
                                df_banque.loc[df_banque["Nom Roblox"] == TARGET_RCT, "Solde"] += montant_op
                                action_status = f"Virement vers compte {TARGET_RCT}"
                            
                            # 3. Mise à jour Database
                            conn.update(worksheet="Banque", data=df_banque)
                            
                            # 4. Affichage du Reçu Noir "Ticket"
                            st.markdown(f"""
                            <div class="ticket-fix">
                                🧾 <b>REÇU DE TRANSACTION BANCAIRE</b><br>
                                Titulaire : {compte['Nom Roblox']}<br>
                                Montant débité : {montant_op}$<br>
                                Motif : {motif_op}<br>
                                Plaque : {plaque_op}<br>
                                Statut : {action_status}<br>
                                Heure de transaction : {datetime.now().strftime('%H:%M:%S')}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            time.sleep(1)
                            st.rerun()

# ==============================================================================
# PIED DE PAGE
# ==============================================================================
st.markdown("---")
st.markdown("<center><small>RCRP Management System v15.3 | 2026 | Administration Gouvernementale</small></center>", unsafe_allow_html=True)
