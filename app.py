import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Portail Officiel", layout="wide")

# --- STYLE CSS (LOGO & ALIGNEMENT FORCE) ---
# Je garde tout le bloc de style sans aucune modification
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    
    /* Force les conteneurs à avoir la même hauteur et aligne les boutons en bas */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        display: flex;
        flex-direction: column;
        height: 520px !important;
    }
    
    /* Cible spécifiquement le bouton dans chaque conteneur pour le pousser vers le bas */
    div[data-testid="stVerticalBlockBorderWrapper"] .stButton {
        margin-top: auto !important;
    }

    .stMetric { 
        background-color: #f8f9fb; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid #e0e0e0; 
    }
    
    [data-testid="stSidebar"] img {
        border-radius: 10px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION SESSION ---
if "role" not in st.session_state:
    st.session_state.role = None

# --- CONNEXION & PARAMÈTRES ---
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26" 
CODE_ENTREPRISE = "RCT-26-RCRPFR" 
MON_PSEUDO_ROBLOX = "une10000"

# URL DU LOGO (Vérifié et fonctionnel)
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless"

def get_data(sheet_name):
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
        return pd.DataFrame()

# ==========================================
# 🚪 PAGE DE CONNEXION (LOGIQUE ALIGNEMENT)
# ==========================================
if st.session_state.role is None:
    st.title("🏛️ Portail des Services RCRP")
    st.markdown("<p style='font-size: 20px; color: #555;'>République de Californie - Système Centralisé de Gestion</p>", unsafe_allow_html=True)
    
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 👤 Citoyen")
            st.write("Accès public pour consulter vos véhicules, votre solde bancaire et vos points de permis de conduire.")
            st.write("---")
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### 🛠️ Entreprise (RCT)")
            st.write("Interface RCT : Gestion de la facturation business, des assurances et des dossiers clients.")
            st.write("---")
            st.text_input("Code RCT", type="password", key="p_rct")
            if st.button("Connexion Pro", use_container_width=True):
                if st.session_state.p_rct == CODE_ENTREPRISE:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("❌ Code incorrect.")

    with col3:
        with st.container(border=True):
            st.markdown("### 👮 Autorités / Staff")
            st.write("Administration totale : Fichier Central, modification des permis, logs et gestion financière.")
            st.write("---")
            st.text_input("Code Autorisation", type="password", key="p_staff")
            if st.button("Connexion Sécurisée", use_container_width=True):
                if st.session_state.p_staff == CODE_ADMIN_GENERAL:
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    st.error("❌ Code incorrect.")
    st.stop()

# ==========================================
# 🖥️ INTERFACE CONNECTÉE (COMPLÈTE)
# ==========================================

with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.write(f"🎭 Session active : **{st.session_state.role}**")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    st.divider()
    st.write(f"📅 **Date du jour : {datetime.now().strftime('%d/%m/%Y')}**")
    st.write(f"⏰ **Heure : {datetime.now().strftime('%H:%M')}**")

st.title(f"🏛️ Espace {st.session_state.role}")

# --- LISTES COMPLÈTES (Aucune marque effacée) ---
liste_assurances = ["Non assuré", "RCT", "Averis"]
liste_etats = sorted(["California", "Washington", "Texas", "New York", "Florida", "Quebec", "Ontario", "Nevada", "Colorado"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])

# --- STRUCTURE DES ONGLETS (SELON ROLE) ---
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers Permis", "💰 Banque Centrale", "➕ Gestion Profils", "📜 Logs Système"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation RCT"])
else:
    tabs = st.tabs(["🚗 Registre Véhicules", "💰 Mon Compte"])

# ==========================================
# 🚗 ONGLET 1 : IMMATRICULATIONS
# ==========================================
with tabs[0]:
    df_im = get_data("Copie de Immatriculations")
    df_b = get_data("Banque")
    
    # On prépare la liste déroulante des pseudos
    pseudos_pour_dropdown = sorted(df_b["Nom Roblox"].unique().tolist()) if not df_b.empty else []

    with st.expander("➕ Enregistrer un nouveau véhicule dans la base de données"):
        with st.form("add_vehicle_form"):
            st.write("### Formulaire d'Immatriculation Officiel")
            c1, c2 = st.columns(2)
            
            # DROPDOWN LIST POUR LE PSEUDO
            u = c1.selectbox("👤 Nom d'utilisateur ROBLOX (Sélectionner dans la liste)", ["--- Choisir un Citoyen ---"] + pseudos_pour_dropdown)
            
            m = c1.selectbox("🚘 Marque du véhicule", liste_marques)
            p = c2.text_input("🔢 Numéro de la plaque d'immatriculation")
            e = c2.selectbox("📍 État de provenance de la plaque", liste_etats)
            a = c1.selectbox("🛡️ Contrat d'Assurance", liste_assurances)
            pwd = c2.text_input("🔑 Définir un code secret (Indispensable pour vos futures modifications)", type="password")
            
            st.write("---")
            if st.form_submit_button("✅ Valider l'enregistrement et procéder au paiement"):
                if u != "--- Choisir un Citoyen ---" and p and pwd:
                    # Logique de prix complète
                    prix_total = 175 
                    user_row = df_b[df_b["Nom Roblox"] == u]
                    
                    if not user_row.empty:
                        solde_actuel = float(user_row.iloc[0]["Solde"])
                        
                        # Calcul Assurance Averis + Taxe Jeune 30 jours
                        if a == "Averis":
                            prix_total += 130
                            try:
                                date_entree = datetime.strptime(str(user_row.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                                if datetime.now() - date_entree < timedelta(days=30):
                                    prix_total += 50
                                    st.info("💡 Information : Taxe Jeune Conducteur de 50$ appliquée (Moins de 30 jours d'ancienneté).")
                            except Exception:
                                pass
                                
                        # Calcul Assurance RCT + Prime Trio (3ème gratuit)
                        elif a == "RCT":
                            nb_deja_rct = df_im[(df_im["Nom d'utilisateur ROBLOX"] == u) & (df_im["Assurance"] == "RCT")].shape[0]
                            if nb_deja_rct >= 2:
                                prix_total += 0
                                st.success("🎉 Prime TRIO RCT : Félicitations, ce 3ème véhicule est assuré gratuitement !")
                            else:
                                prix_total += 150
                        
                        if solde_actuel >= prix_total:
                            # Débit du compte
                            idx_banque = user_row.index[0]
                            df_b.at[idx_banque, "Solde"] = solde_actuel - prix_total
                            
                            # Création de la ligne véhicule
                            new_vehicle = pd.DataFrame([{
                                "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "Nom d'utilisateur ROBLOX": u,
                                "Marque du véhicule": m,
                                "L'état de la plaque": e,
                                "Numéro de la plaque": p,
                                "Assurance": a,
                                "CODE": str(pwd)
                            }])
                            
                            conn.update(worksheet="Banque", data=df_b)
                            conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_vehicle], ignore_index=True))
                            
                            st.success(f"✅ Véhicule enregistré ! Le montant de {prix_total}$ a été prélevé sur votre compte.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ Transaction refusée : Solde insuffisant. Votre compte doit disposer de {prix_total}$.")
                    else:
                        st.error("❌ Erreur : Profil bancaire introuvable.")
                else:
                    st.warning("⚠️ Attention : Veuillez remplir tous les champs et sélectionner un pseudo.")

    st.divider()
    
    # RECHERCHE ET AFFICHAGE (REMIS A L'IDENTIQUE)
    search_query = st.text_input("🔍 Rechercher dans le registre (Pseudo, Plaque, Marque...)").strip().lower()
    
    if not df_im.empty:
        mask = df_im.apply(lambda row: search_query in str(row).lower(), axis=1)
        res_display = df_im[mask]
        
        for index, row in res_display.iterrows():
            with st.container(border=True):
                col_info, col_action = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"### 🚗 **{row['Numéro de la plaque']}**")
                    st.write(f"👤 **Propriétaire :** {row['Nom d\'utilisateur ROBLOX']}")
                    st.write(f"🚘 **Détails :** {row['Marque du véhicule']} | État : {row['L\'état de la plaque']}")
                    st.write(f"🛡️ **Assurance actuelle :** {row['Assurance']}")
                    st.write(f"📅 **Date d'immatriculation :** {row['Horodateur']}")
                
                with col_action:
                    if st.button("⚙️ Modifier / Supprimer", key=f"btn_manage_{index}"):
                        st.session_state[f"show_ctrl_{index}"] = not st.session_state.get(f"show_ctrl_{index}", False)
                
                if st.session_state.get(f"show_ctrl_{index}"):
                    st.write("---")
                    with st.form(f"auth_form_{index}"):
                        st.markdown("🔒 **Authentification Requise**")
                        code_input = st.text_input("Saisissez le code secret du véhicule", type="password")
                        if st.form_submit_button("🔓 Déverrouiller les contrôles"):
                            if st.session_state.role == "Staff" or str(code_input) == str(row['CODE']):
                                st.session_state[f"auth_success_{index}"] = True
                            else:
                                st.error("❌ Code secret invalide.")
                    
                    if st.session_state.get(f"auth_success_{index}"):
                        with st.form(f"edit_form_{index}"):
                            st.write("#### Options de Modification")
                            new_plate = st.text_input("Modifier le numéro de plaque", value=row['Numéro de la plaque'])
                            new_assu = st.selectbox("Changer de contrat d'assurance", liste_assurances, index=liste_assurances.index(row['Assurance']) if row['Assurance'] in liste_assurances else 0)
                            
                            eb1, eb2 = st.columns(2)
                            if eb1.form_submit_button("💾 Enregistrer les changements"):
                                df_im.at[index, 'Numéro de la plaque'] = new_plate
                                df_im.at[index, 'Assurance'] = new_assu
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.success("Changements appliqués !")
                                time.sleep(1)
                                st.rerun()
                                
                            if eb2.form_submit_button("🗑️ Supprimer définitivement"):
                                df_im = df_im.drop(index)
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.error("Véhicule supprimé du registre.")
                                time.sleep(1)
                                st.rerun()

# ==========================================
# 💰 ONGLET 2 : BANQUE CENTRALE
# ==========================================
with tabs[1 if st.session_state.role != "Staff" else 2]:
    df_banque = get_data("Banque")
    
    if st.session_state.role == "Civil":
        st.write("### 🏦 Consultation de votre Compte")
        votre_nom = st.text_input("Saisissez votre Nom Roblox ou Discord").strip().lower()
        if votre_nom:
            res_user = df_banque[df_banque.apply(lambda r: votre_nom in str(r).lower(), axis=1)]
            if not res_user.empty:
                c1, c2 = st.columns(2)
                c1.metric("💵 Solde Bancaire Actuel", f"{float(res_user.iloc[0]['Solde']):,.0f} $")
                
                df_pts_view = get_data("Points Permis")
                res_pts_view = df_pts_view[df_pts_view.apply(lambda r: votre_nom in str(r).lower(), axis=1)]
                if not res_pts_view.empty:
                    c2.metric("🪪 Points de Permis de Conduire", f"{res_pts_view.iloc[0]['PTS']} / 25")
            else:
                st.info("ℹ️ Aucun compte trouvé à ce nom. Veuillez contacter le staff.")
    
    else:
        st.write("### 🏦 Système de Gestion Bancaire")
        recherche_compte = st.text_input("🔍 Rechercher un citoyen (Nom, Discord, Date...)").strip().lower()
        
        if recherche_compte:
            res_recherche = df_banque[df_banque.apply(lambda r: recherche_compte in str(r).lower(), axis=1)]
            for idx_b, row_b in res_recherche.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **Propriétaire : {row_b['Nom Roblox']}**")
                    st.write(f"💬 Discord : {row_b['Discord']} | 📅 Arrivée : {row_b['Date d'arrivée']}")
                    solde_actuel_val = float(row_b['Solde'])
                    st.metric("Solde", f"{solde_actuel_val:,.0f} $")
                    
                    with st.form(f"form_banque_{idx_b}"):
                        st.write("---")
                        montant_op = st.number_input("Montant de l'opération", min_value=0.0, step=50.0)
                        bb1, bb2 = st.columns(2)
                        
                        if bb1.form_submit_button("📉 Facturer / Prélever"):
                            df_banque.at[idx_b, 'Solde'] = solde_actuel_val - montant_op
                            conn.update(worksheet="Banque", data=df_banque)
                            st.success(f"Opération réussie : -{montant_op}$")
                            time.sleep(1)
                            st.rerun()
                            
                        if bb2.form_submit_button("📈 Créditer / Ajouter") and st.session_state.role == "Staff":
                            df_banque.at[idx_b, 'Solde'] = solde_actuel_val + montant_op
                            conn.update(worksheet="Banque", data=df_banque)
                            st.success(f"Compte crédité de {montant_op}$")
                            time.sleep(1)
                            st.rerun()

# ==========================================
# 🪪 ONGLET 3 : DOSSIERS PERMIS (STAFF)
# ==========================================
if st.session_state.role == "Staff":
    with tabs[1]:
        st.write("### 🪪 Administration des Permis de Conduire")
        df_points_permis = get_data("Points Permis")
        recherche_permis = st.text_input("🔍 Rechercher un dossier de permis").strip().lower()
        
        if recherche_permis:
            res_permis = df_points_permis[df_points_permis.apply(lambda r: recherche_permis in str(r).lower(), axis=1)]
            for idx_p, row_p in res_permis.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **Titulaire : {row_p['Nom Roblox']}**")
                    st.write(f"📍 Points actuels : **{row_p['PTS']} / 25**")
                    with st.form(f"form_pts_{idx_p}"):
                        nouveaux_points = st.number_input("Ajuster le solde de points", 0, 25, value=int(row_p['PTS']))
                        if st.form_submit_button("💾 Mettre à jour le dossier"):
                            df_points_permis.at[idx_p, 'PTS'] = nouveaux_points
                            conn.update(worksheet="Points Permis", data=df_points_permis)
                            st.success("Points mis à jour avec succès.")
                            time.sleep(1)
                            st.rerun()

    # ==========================================
    # ➕ ONGLET 4 : GESTION PROFILS (STAFF) - CREATION AUTO
    # ==========================================
    with tabs[3]:
        st.write("### ➕ Créer un Nouveau Dossier Citoyen Intégral")
        st.write("Cet outil crée automatiquement le compte bancaire et le dossier de permis.")
        
        with st.form("creation_profil_integral"):
            sc1, sc2 = st.columns(2)
            username_rc = sc1.text_input("Nom d'utilisateur ROBLOX")
            discord_rc = sc2.text_input("Pseudo Discord (ex: @pseudo)")
            solde_depart = sc1.number_input("Prime d'arrivée (Banque)", value=15000.0)
            points_depart = sc2.number_input("Solde de points (Permis)", 0, 25, value=25)
            
            st.write("---")
            if st.form_submit_button("🚀 Valider la création du Citoyen"):
                df_b_create = get_data("Banque")
                df_p_create = get_data("Points Permis")
                
                # Vérification si déjà existant
                if not df_b_create[df_b_create["Nom Roblox"].str.lower() == username_rc.lower()].empty:
                    st.error("❌ Erreur : Ce citoyen possède déjà un dossier dans la base de données.")
                elif username_rc == "":
                    st.warning("⚠️ Veuillez entrer un nom d'utilisateur.")
                else:
                    # 1. Création ligne Banque
                    nouvelle_ligne_banque = pd.DataFrame([{
                        "Nom Roblox": username_rc,
                        "Discord": discord_rc,
                        "Solde": solde_depart,
                        "Date d'arrivée": datetime.now().strftime("%d/%m/%Y")
                    }])
                    # 2. Création ligne Permis
                    nouvelle_ligne_permis = pd.DataFrame([{
                        "Nom Roblox": username_rc,
                        "PTS": points_depart
                    }])
                    
                    conn.update(worksheet="Banque", data=pd.concat([df_b_create, nouvelle_ligne_banque], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_p_create, nouvelle_ligne_permis], ignore_index=True))
                    
                    st.success(f"🎉 Succès ! {username_rc} a été ajouté à la Banque (+{solde_depart}$) et aux Permis ({points_depart} PTS).")
                    time.sleep(1)
                    st.rerun()

    # ==========================================
    # 📜 ONGLET 5 : LOGS SYSTÈME
    # ==========================================
    with tabs[4]:
        st.write("### 📜 Historique des Logs Système")
        st.write("Consultation des dernières actions effectuées sur le serveur.")
        df_logs = get_data("Logs")
        if not df_logs.empty:
            st.dataframe(df_logs.iloc[::-1], use_container_width=True)
        else:
            st.info("Aucun log disponible pour le moment.")

st.markdown("---")
st.markdown("<center><small>République de Californie RP | Système Centralisé v9.41</small></center>", unsafe_allow_html=True)
