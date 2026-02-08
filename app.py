import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# ==========================================
# 1. CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(
    page_title="RCRP - Système Intégral Professionnel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. STYLE CSS DÉTAILLÉ (DÉPLOYÉ)
# ==========================================
st.markdown("""
    <style>
    /* Ajustement de l'espace supérieur pour les onglets */
    .block-container { 
        padding-top: 6rem !important; 
    }
    
    /* Style spécifique pour le logo dans la sidebar */
    [data-testid="stSidebar"] img { 
        border-radius: 15px; 
        width: 250px !important; 
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 25px;
        display: block;
        border: 1px solid #333;
    }

    /* Badges d'état pour les assurances */
    .badge-assu {
        background-color: #ff4b4b;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }

    /* Design du ticket de caisse RCRP (Mode Sombre) */
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
    
    /* Alertes personnalisées */
    .stAlert {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VARIABLES ET CONSTANTES DE SÉCURITÉ
# ==========================================
if "role" not in st.session_state:
    st.session_state.role = None

# Connexion Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Comptes de destination (Instructions spécifiques)
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"

# Codes de sécurité Admin et Pro
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"

# Logo Officiel
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

# ==========================================
# 4. FONCTIONS DE GESTION DES DONNÉES
# ==========================================
def get_data(sheet_name):
    """Récupère les données d'une feuille spécifique sans cache persistant."""
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        df_clean = data.dropna(how='all')
        df_final = df_clean.fillna("")
        return df_final
    except Exception as e:
        st.error(f"Erreur de lecture sur {sheet_name} : {e}")
        return pd.DataFrame()

# Chargement des DataFrames
df_banque = get_data("Banque")
df_im = get_data("Copie de Immatriculations")
df_pts = get_data("Points Permis")

# ==========================================
# 5. PORTAIL DE CONNEXION (LOGIQUE COMPLÈTE)
# ==========================================
if st.session_state.role is None:
    st.title("🏛️ Système de Gestion RCRP - Portail d'Accès")
    st.write("Veuillez sélectionner votre secteur d'activité pour continuer.")
    
    col_civ, col_pro, col_staff = st.columns(3)
    
    with col_civ:
        with st.container(border=True):
            st.subheader("👤 Secteur Civil")
            st.info("Accès libre pour la consultation des points et plaques.")
            if st.button("Accéder au Portail Public", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()
                
    with col_pro:
        with st.container(border=True):
            st.subheader("🛠️ Secteur Professionnel")
            st.write("Réservé aux employés RCT.")
            input_pro = st.text_input("Code Employé", type="password", key="login_p")
            if st.button("Authentification Pro", use_container_width=True):
                if input_pro == CODE_PRO:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("Code RCT invalide.")
                    
    with col_staff:
        with st.container(border=True):
            st.subheader("👮 Gouvernement")
            st.write("Accès Administration & Autorités.")
            input_staff = st.text_input("Code Gouvernement", type="password", key="login_s")
            if st.button("Authentification Staff", use_container_width=True):
                if input_staff == CODE_ADMIN:
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    st.error("Code Administration invalide.")
    st.stop()

# ==========================================
# 6. BARRE LATÉRALE ET NAVIGATION
# ==========================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.divider()
    
    st.markdown(f"### 🔑 Session active")
    st.info(f"Rôle actuel : **{st.session_state.role}**")
    
    if st.button("🚪 Déconnexion du système", use_container_width=True):
        st.session_state.role = None
        st.rerun()
        
    st.divider()
    
    # Affichage des informations temporelles
    now = datetime.now()
    st.write(f"📅 **Date :** {now.strftime('%d/%m/%Y')}")
    st.write(f"⏰ **Heure :** {now.strftime('%H:%M:%S')}")
    
    st.divider()
    st.caption("RCRP Management System v14.0")

# ==========================================
# 7. INTERFACE PRINCIPALE (ONGLETS)
# ==========================================
tab_immat, tab_dossier, tab_banque = st.tabs([
    "🚗 Registre Immatriculations", 
    "🪪 Dossiers Citoyens", 
    "💰 Gestion Bancaire Centrale"
])

# --- ONGLET 1 : IMMATRICULATIONS & LOGIQUE FINANCIÈRE ---
with tab_immat:
    st.header("🚗 Registre National des Véhicules")
    
    # Formulaire d'enregistrement
    with st.expander("➕ Enregistrer un nouveau véhicule (Paiement automatique)", expanded=True):
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            proprio = st.selectbox("Propriétaire du véhicule", ["---"] + df_banque["Nom Roblox"].tolist())
            marque = st.text_input("Marque et Modèle précis")
            plaque = st.text_input("Numéro de plaque d'immatriculation")
            
        with col_f2:
            assurance = st.selectbox("Choisir un contrat d'assurance", [
                "Aucune", 
                "AVERIS (130$ / mois)", 
                "RCT (150$ / mois)"
            ])
            code_secret = st.text_input("🔑 Créer un code secret pour ce véhicule", type="password")
        
        # --- CALCULATEUR DE FRAIS DÉPLOYÉ ---
        frais_fixe = 175
        frais_assu = 0
        frais_taxe_jeune = 0
        
        # Détermination du coût d'assurance
        if "AVERIS" in assurance:
            frais_assu = 130
        elif "RCT" in assurance:
            frais_assu = 150
            
        # Vérification Offre Trio RCT (3ème gratuit)
        exist_rct = df_im[
            (df_im["Nom d'utilisateur ROBLOX"] == proprio) & 
            (df_im["Assurance"].str.contains("RCT"))
        ]
        nb_rct = len(exist_rct)
        
        if "RCT" in assurance and nb_rct >= 2:
            frais_assu = 0
            st.success("🎁 Offre Trio : Ce citoyen bénéficie de la gratuité sur cette assurance RCT !")

        # Calcul de la Taxe Jeune Conducteur (-30 jours)
        if proprio != "---":
            user_data = df_banque[df_banque["Nom Roblox"] == proprio]
            if not user_data.empty:
                try:
                    date_val = str(user_data.iloc[0]["Date d'arrivée"])
                    date_dt = datetime.strptime(date_val, "%d/%m/%Y")
                    jours_presence = (datetime.now() - date_dt).days
                    if jours_presence < 30:
                        frais_taxe_jeune = 50
                except:
                    pass
        
        total_transaction = frais_fixe + frais_assu + frais_taxe_jeune
        
        # Affichage du reçu détaillé
        st.markdown(f"""
        <div class="ticket-fix">
            <b>🧾 REÇU DE PAIEMENT - IMMATRICULATION</b><br>
            ------------------------------------------<br>
            • Frais d'immatriculation : 175$<br>
            • Contrat d'assurance : {frais_assu}$<br>
            • Taxe Nouveau Citoyen : {frais_taxe_jeune}$<br>
            ------------------------------------------<br>
            <b>MONTANT TOTAL À PRÉLEVER : {total_transaction}$</b>
        </div>
        """, unsafe_allow_html=True)

        # Validation de l'achat
        if st.button("✅ Confirmer l'achat et l'enregistrement"):
            if proprio != "---" and plaque and code_secret:
                # Vérification du solde
                idx_client = df_banque[df_banque["Nom Roblox"] == proprio].index[0]
                solde_c = float(df_banque.at[idx_client, "Solde"])
                
                if solde_c >= total_transaction:
                    # 1. Débit du compte citoyen
                    df_banque.at[idx_client, "Solde"] = solde_c - total_transaction
                    
                    # 2. Redirection des fonds d'assurance
                    if frais_assu > 0:
                        cible_f = TARGET_AVERIS if "AVERIS" in assurance else TARGET_RCT
                        idx_dest_f = df_banque[df_banque["Nom Roblox"] == cible_f].index[0]
                        solde_dest_old = float(df_banque.at[idx_dest_f, "Solde"])
                        df_banque.at[idx_dest_f, "Solde"] = solde_dest_old + frais_assu
                    
                    # 3. Préparation de la nouvelle ligne
                    new_row_v = pd.DataFrame([{
                        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                        "Nom d'utilisateur ROBLOX": proprio,
                        "Marque du véhicule": marque,
                        "Numéro de la plaque": plaque,
                        "Assurance": assurance,
                        "CODE": str(code_secret)
                    }])
                    
                    # 4. Mise à jour des bases
                    conn.update(worksheet="Banque", data=df_banque)
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_row_v], ignore_index=True))
                    
                    st.balloons()
                    st.success("Véhicule enregistré et paiement validé !")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("Le solde du citoyen est insuffisant pour finaliser l'opération.")
            else:
                st.warning("Informations manquantes (Propriétaire, Plaque ou Code Secret).")

    # Affichage de la liste des véhicules
    st.divider()
    search_veh = st.text_input("🔍 Recherche par plaque ou par nom").lower()
    
    if not df_im.empty:
        # Filtre de recherche
        mask = df_im.apply(lambda x: search_veh in str(x).lower(), axis=1)
        df_filtered = df_im[mask]
        
        for i, r in df_filtered.iterrows():
            with st.container(border=True):
                col_i1, col_i2 = st.columns([3, 1])
                with col_i1:
                    st.write(f"🚗 **Plaque : {r['Numéro de la plaque']}**")
                    st.write(f"👤 Propriétaire : {r['Nom d\'utilisateur ROBLOX']} | Modèle : {r['Marque du véhicule']}")
                with col_i2:
                    st.markdown(f"<span class='badge-assu'>{r['Assurance']}</span>", unsafe_allow_html=True)
                
                # Gestion de la suppression (avec code secret)
                with st.expander("🗑️ Supprimer ce véhicule"):
                    input_del = st.text_input("Entrer le code secret du véhicule", type="password", key=f"del_{i}")
                    if input_del == str(r['CODE']) or st.session_state.role == "Staff":
                        if st.button("Confirmer la radiation du registre", key=f"btn_del_{i}"):
                            new_df_im = df_im.drop(i)
                            conn.update(worksheet="Copie de Immatriculations", data=new_df_im)
                            st.success("Véhicule supprimé.")
                            st.rerun()

# --- ONGLET 2 : DOSSIERS & PAYE ADMINISTRATIVE ---
with tab_dossier:
    st.header("🪪 Dossiers Citoyens & Administration")
    
    # --- BOUTON DE PAYE GLOBALE (ADMIN SEULEMENT) ---
    if st.session_state.role == "Staff":
        with st.container(border=True):
            st.subheader("🏦 Script de Gestion Mensuelle")
            st.write("Cette commande va verser 15,000$ à chaque citoyen et prélever automatiquement les assurances.")
            
            if st.button("🧧 DÉCLENCHER LA PAYE GÉNÉRALE & LES PRÉLÈVEMENTS", use_container_width=True):
                with st.status("Exécution de la procédure en cours..."):
                    # 1. Augmentation des soldes (+15,000)
                    df_banque["Solde"] = df_banque["Solde"].apply(lambda x: float(x) + 15000)
                    
                    # 2. Prélèvement automatique par véhicule
                    tracker_rct_paye = {}
                    
                    for idx_v, veh_row in df_im.iterrows():
                        owner_v = veh_row["Nom d'utilisateur ROBLOX"]
                        type_v = veh_row["Assurance"]
                        
                        # Vérifier si le propriétaire existe en banque
                        if owner_v in df_banque["Nom Roblox"].values:
                            idx_banque_o = df_banque[df_banque["Nom Roblox"] == owner_v].index[0]
                            
                            # Traitement RCT
                            if "RCT" in type_v:
                                tracker_rct_paye[owner_v] = tracker_rct_paye.get(owner_v, 0) + 1
                                if tracker_rct_paye[owner_v] <= 2: # Applique l'offre Trio
                                    # Débit client
                                    df_banque.at[idx_banque_o, "Solde"] -= 150
                                    # Crédit Entreprise
                                    idx_rct_compte = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                    df_banque.at[idx_rct_compte, "Solde"] += 150
                            
                            # Traitement AVERIS
                            elif "AVERIS" in type_v:
                                # Débit client
                                df_banque.at[idx_banque_o, "Solde"] -= 130
                                # Crédit Entreprise
                                idx_ave_compte = df_banque[df_banque["Nom Roblox"] == TARGET_AVERIS].index[0]
                                df_banque.at[idx_ave_compte, "Solde"] += 130
                    
                    # Sauvegarde globale
                    conn.update(worksheet="Banque", data=df_banque)
                    st.success("Opération terminée : 15k distribués et prélèvements assurances effectués.")
                    time.sleep(2)
                    st.rerun()

    # Recherche de points (Hybride Roblox/Discord)
    st.divider()
    search_dos = st.text_input("🔍 Rechercher un dossier (Roblox ou Discord)").lower()
    
    if search_dos:
        match_dos = df_banque[
            (df_banque["Nom Roblox"].str.lower().str.contains(search_dos, na=False)) | 
            (df_banque["Nom Discord"].str.lower().str.contains(search_dos, na=False))
        ]
        
        if not match_dos.empty:
            for _, c_row in match_dos.iterrows():
                with st.container(border=True):
                    st.subheader(f"Dossier de {c_row['Nom Roblox']}")
                    st.write(f"🎮 Pseudo Discord : @{c_row['Nom Discord']}")
                    
                    # Récupération des points
                    points_val = df_pts[df_pts["Nom Roblox"] == c_row["Nom Roblox"]]
                    if not points_val.empty:
                        st.metric("Points de Permis", f"{points_val.iloc[0]['PTS']} / 25")
        else:
            st.warning("Aucun dossier trouvé.")

    # Création de profil (Staff)
    if st.session_state.role == "Staff":
        st.divider()
        with st.expander("👤 Création d'un nouveau profil citoyen"):
            with st.form("form_nouveau"):
                new_rob = st.text_input("Nom d'utilisateur Roblox")
                new_disc = st.text_input("Pseudo Discord")
                if st.form_submit_button("🚀 Valider la création"):
                    date_c = datetime.now().strftime("%d/%m/%Y")
                    # Ligne Banque
                    row_b = pd.DataFrame([{
                        "Solde": 15000, 
                        "Nom Discord": new_disc, 
                        "Nom Roblox": new_rob, 
                        "Date d'arrivée": date_c
                    }])
                    # Ligne Points
                    row_p = pd.DataFrame([{
                        "Nom Roblox": new_rob, 
                        "PTS": 25
                    }])
                    
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, row_b], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, row_p], ignore_index=True))
                    st.success(f"Profil créé pour {new_rob} !")
                    st.rerun()

# --- ONGLET 3 : BANQUE CENTRALE ---
with tab_banque:
    st.header("💰 Gestion Bancaire Centrale")
    
    search_b = st.text_input("🔍 Rechercher un compte bancaire").lower()
    
    if search_b:
        res_b = df_banque[
            (df_banque["Nom Roblox"].str.lower().str.contains(search_b, na=False)) | 
            (df_banque["Nom Discord"].str.lower().str.contains(search_b, na=False))
        ]
        
        for idx_b, r_bank in res_b.iterrows():
            with st.container(border=True):
                st.subheader(f"Compte : {r_bank['Nom Roblox']}")
                st.metric("Solde actuel", f"{float(r_bank['Solde']):,.0f} $")
                
                # Actions professionnelles
                if st.session_state.role in ["RCT", "Staff"]:
                    st.divider()
                    with st.expander(f"⚙️ Opération financière sur le compte de {r_bank['Nom Roblox']}"):
                        montant_op = st.number_input("Montant de l'opération ($)", min_value=1, key=f"op_{idx_b}")
                        raison_op = st.text_input("Motif de l'opération", key=f"rai_{idx_b}")
                        
                        if st.button("Confirmer le retrait", key=f"btn_op_{idx_b}"):
                            current_s = float(r_bank['Solde'])
                            if current_s >= montant_op:
                                # Débit citoyen
                                idx_c_cible = df_banque[df_banque["Nom Roblox"] == r_bank['Nom Roblox']].index[0]
                                df_banque.at[idx_c_cible, "Solde"] = current_s - montant_op
                                
                                # Logique de transfert RCT vs Staff
                                info_txt = ""
                                if st.session_state.role == "RCT":
                                    # Argent vers Entreprise
                                    idx_ent = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                    df_banque.at[idx_ent, "Solde"] = float(df_banque.at[idx_ent, "Solde"]) + montant_op
                                    info_txt = f"Virement vers compte Entreprise ({TARGET_RCT})"
                                else:
                                    # Staff : Argent supprimé
                                    info_txt = "Saisie Administrative (Fonds détruits)"
                                
                                conn.update(worksheet="Banque", data=df_banque)
                                st.markdown(f"""
                                <div class="ticket-fix">
                                    <b>🧾 REÇU DE TRANSACTION</b><br>
                                    Cible : {r_bank['Nom Roblox']}<br>
                                    Montant : {montant_op}$<br>
                                    Nature : {info_txt}
                                </div>
                                """, unsafe_allow_html=True)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Solde insuffisant.")

# ==========================================
# 8. FOOTER ET INFORMATIONS LÉGALES
# ==========================================
st.markdown("---")
col_f1, col_f2 = st.columns(2)
with col_f1:
    st.caption("© 2026 RCRP - Système de gestion sécurisé")
with col_f2:
    st.markdown("<div style='text-align: right;'><small>Version Stable 14.0.2</small></div>", unsafe_allow_html=True)
