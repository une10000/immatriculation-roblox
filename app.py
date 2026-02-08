# ==============================================================================
# 🏛️ REPUBLIQUE DE CALIFORNIE RP - SYSTEME DE GESTION INTEGRAL (v11.0)
# ==============================================================================
# Plateforme de gestion centralisée : Économie, Transports, Justice et Logistique.
# Version : 11.0 | Date : 08/02/2026 | Développeur : RCRP Tech Division
# 
# [MEMOIRE DU SYSTEME]
# - Assurances Averis : Crédits transférés vers 'Moune2010'
# - Assurances RCT : Crédits transférés vers 'une10000'
# - Création Profil : Date d'arrivée générée AUTOMATIQUEMENT (Jour J).
# - Recherche Civile : Compatible Nom Roblox ET Nom Discord.
# - Permis : Affichage visuel (Vert/Orange/Rouge) pour les civils.
# ==============================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURATION DE L'INTERFACE GOUVERNEMENTALE ---
st.set_page_config(
    page_title="RCRP - Système Intégré de l'État",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ENGINE CSS : DESIGN COMPLET (Ne rien effacer ici) ---
st.markdown("""
    <style>
    /* Thème Global Sombre */
    .main { background-color: #0b0d10; color: #ecf0f1; }
    
    /* Conteneurs de connexion - Hauteur fixe 600px */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(30, 34, 40, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 40px !important;
        height: 600px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
    }

    /* Ticket de Transaction Financière */
    .transaction-ticket {
        background: linear-gradient(135deg, #1e272e 0%, #050505 100%);
        border: 1px solid #27ae60;
        border-left: 12px solid #27ae60;
        padding: 25px;
        border-radius: 12px;
        margin: 20px 0;
        color: #ffffff;
        font-family: 'Consolas', 'Courier New', monospace;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
    }

    /* Carte d'Identité Civil (Banque) */
    .id-card {
        background: rgba(52, 152, 219, 0.1);
        border: 1px solid #3498db;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Indicateur de Permis */
    .license-box {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-top: 10px;
        background: rgba(0,0,0,0.3);
    }

    /* Métriques */
    .stMetric {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }

    /* Logo Sidebar */
    [data-testid="stSidebar"] img {
        border-radius: 25px;
        border: 3px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 25px;
        transition: transform 0.3s;
    }
    [data-testid="stSidebar"] img:hover { transform: scale(1.02); }

    /* Onglets de navigation */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px 10px 0 0;
        padding: 15px 30px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #c0392b !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONSTANTES ET SÉCURITÉ ---
AUTH_ADMIN_KEY = "RCRPFR-25-26" 
AUTH_PRO_KEY = "RCT-26-RCRPFR" 
TARGET_RCT = "une10000" 
TARGET_AVERIS = "Moune2010"
ASSET_LOGO = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless"

# --- 4. GESTION DE SESSION ET BASE DE DONNEES ---
if "role" not in st.session_state:
    st.session_state.role = None

conn = st.connection("gsheets", type=GSheetsConnection)

def load_table(name):
    """Charge les données sans cache pour avoir toujours les dernières modifications."""
    st.cache_data.clear()
    try:
        return conn.read(worksheet=name, ttl=0).dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

def commit_log(agent, category, info):
    """Fonction d'archivage des logs."""
    try:
        logs = load_table("Logs")
        entry = pd.DataFrame([{
            "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Opérateur": agent,
            "Catégorie": category,
            "Description": info
        }])
        conn.update(worksheet="Logs", data=pd.concat([logs, entry], ignore_index=True))
    except: pass

# ==============================================================================
# 🚪 SECTION 5 : PORTAIL D'AUTHENTIFICATION (LOBBY)
# ==============================================================================
if st.session_state.role is None:
    st.title("🏛️ État de Californie - Portail Central")
    st.markdown("---")
    
    col_c, col_p, col_s = st.columns(3)
    
    # --- COLONNE CIVIL ---
    with col_c:
        with st.container(border=True):
            st.markdown("### 👤 Citoyen")
            st.info("Accès libre : Consultez vos comptes, vos véhicules et votre permis.")
            if st.button("Entrer dans l'espace Civil", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()

    # --- COLONNE PRO ---
    with col_p:
        with st.container(border=True):
            st.markdown("### 🛠️ Professionnel")
            st.write("Espace réservé (RCT / Averis). Gestion des contrats.")
            key_p = st.text_input("Code Entreprise", type="password")
            if st.button("Connexion Pro", use_container_width=True):
                if key_p == AUTH_PRO_KEY:
                    st.session_state.role = "RCT"
                    st.rerun()
                else: st.error("Accès refusé.")

    # --- COLONNE STAFF ---
    with col_s:
        with st.container(border=True):
            st.markdown("### 👮 Administration")
            st.write("Accès haute sécurité pour la gestion de l'État.")
            key_s = st.text_input("Code Staff", type="password")
            if st.button("Connexion Staff", use_container_width=True):
                if key_s == AUTH_ADMIN_KEY:
                    st.session_state.role = "Staff"
                    st.rerun()
                else: st.error("Code erroné.")
    st.stop()

# ==============================================================================
# 🖥️ SECTION 6 : INTERFACE PRINCIPALE (SIDEBAR + ONGLETS)
# ==============================================================================
with st.sidebar:
    st.image(ASSET_LOGO, use_container_width=True)
    st.markdown(f"🛂 **Session active :** {st.session_state.role}")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    st.divider()
    st.write(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"⏰ **Heure :** {datetime.now().strftime('%H:%M')}")

# --- DEFINITION DES ONGLETS PAR ROLE ---
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immat", "💰 Banque", "🪪 Permis", "➕ Profils", "⚖️ Justice", "📊 Stats", "📜 Logs"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation Pro", "📜 Historique"])
else:
    # Ordre spécifique pour les civils
    tabs = st.tabs(["💰 Mon Compte", "🪪 Mon Permis", "🚗 Mes Véhicules"])

# ==============================================================================
# 💰 MODULE : BANQUE & IDENTITÉ (Avec Date et Recherche Hybride)
# ==============================================================================
# Ce module est partagé : Onglet 2 pour Staff, Onglet 1 pour Civil
current_tab_bank = tabs[1] if st.session_state.role == "Staff" else tabs[0]
if st.session_state.role == "RCT": current_tab_bank = tabs[1] # Pas utilisé par RCT mais pour éviter erreur

with current_tab_bank:
    df_bk = load_table("Banque")
    
    # Entête différent selon le rôle
    if st.session_state.role == "Civil":
        st.write("### 🏦 Espace Personnel Bancaire")
        search_query = st.text_input("🔍 Entrez votre Nom Roblox OU Discord pour vous identifier").lower()
    else:
        st.write("### 🏦 Gestion Bancaire Nationale")
        search_query = st.text_input("🔍 Rechercher un citoyen (Roblox/Discord)").lower()

    if search_query:
        # LOGIQUE DE RECHERCHE DOUBLE (ROBLOX OU DISCORD)
        res_bk = df_bk[(df_bk["Nom Roblox"].str.lower().str.contains(search_query)) | 
                       (df_bk["Nom Discord"].str.lower().str.contains(search_query))]
        
        if not res_bk.empty:
            for i, row in res_bk.iterrows():
                with st.container():
                    # Affichage complet des infos civiles (DONT LA DATE)
                    st.markdown(f"""
                    <div class="id-card">
                        <h3>👤 Dossier Citoyen : {row['Nom Roblox']}</h3>
                        <ul>
                            <li><b>Discord :</b> {row['Nom Discord']}</li>
                            <li><b>📅 Date d'arrivée :</b> {row["Date d'arrivée"]}</li>
                            <li><b>Enregistré par :</b> {row['Pseudo Admin']}</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Solde
                    st.metric("Solde Bancaire Disponible", f"{float(row['Solde']):,.0f} $")
                    
                    # Actions Staff uniquement
                    if st.session_state.role == "Staff":
                        with st.form(f"bk_act_{i}"):
                            amount = st.number_input("Montant de la transaction", min_value=0.0, step=100.0)
                            c1, c2 = st.columns(2)
                            if c1.form_submit_button("📉 Débiter"):
                                df_bk.at[i, 'Solde'] = float(row['Solde']) - amount
                                conn.update(worksheet="Banque", data=df_bk)
                                commit_log(st.session_state.role, "DEBIT", f"-{amount}$ pour {row['Nom Roblox']}")
                                st.rerun()
                            if c2.form_submit_button("📈 Créditer"):
                                df_bk.at[i, 'Solde'] = float(row['Solde']) + amount
                                conn.update(worksheet="Banque", data=df_bk)
                                commit_log(st.session_state.role, "CREDIT", f"+{amount}$ pour {row['Nom Roblox']}")
                                st.rerun()
        else:
            st.warning("Aucun dossier trouvé. Vérifiez l'orthographe (Roblox ou Discord).")

# ==============================================================================
# 🪪 MODULE : PERMIS DE CONDUIRE (Visuel Vert/Rouge)
# ==============================================================================
# Onglet 3 pour Staff, Onglet 2 pour Civil
target_tab_permis = tabs[2] if st.session_state.role == "Staff" else tabs[1]

with target_tab_permis:
    if st.session_state.role == "RCT": pass # RCT n'a pas accès
    else:
        st.write("### 🪪 Registre National des Permis")
        df_permis = load_table("Points Permis")
        
        # Barre de recherche (si pas déjà remplie par le contexte global, on redemande)
        search_permis = st.text_input("🔍 Vérification Permis (Nom Roblox ou Discord)", key="s_permis").lower()
        
        if search_permis:
            # On doit d'abord trouver le nom Roblox si l'utilisateur a tapé son Discord
            # On utilise la table Banque pour faire la correspondance
            df_ref = load_table("Banque")
            users_matches = df_ref[(df_ref["Nom Roblox"].str.lower().str.contains(search_permis)) | 
                                   (df_ref["Nom Discord"].str.lower().str.contains(search_permis))]
            
            if not users_matches.empty:
                target_names = users_matches["Nom Roblox"].tolist()
                # Maintenant on cherche dans la table Permis
                res_p = df_permis[df_permis["Nom Roblox"].isin(target_names)]
                
                if not res_p.empty:
                    for ip, lp in res_p.iterrows():
                        pts = int(lp['PTS'])
                        
                        # LOGIQUE VISUELLE (COULEURS)
                        if pts >= 15:
                            color = "#2ecc71" # Vert
                            msg = "PERMIS VALIDE - Conduite Exemplaire"
                        elif pts >= 6:
                            color = "#f1c40f" # Orange
                            msg = "PERMIS VALIDE - Attention"
                        else:
                            color = "#e74c3c" # Rouge
                            msg = "PERMIS SUSPENDU - Danger"
                        
                        st.markdown(f"""
                        <div class="license-box" style="border: 2px solid {color}; box-shadow: 0 0 10px {color};">
                            <h1 style="color:{color}; margin:0;">{pts} / 25</h1>
                            <h4 style="color:white;">{lp['Nom Roblox']}</h4>
                            <p style="color:{color}; font-weight:bold;">{msg}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Actions Staff
                        if st.session_state.role == "Staff":
                            st.write("---")
                            new_pts = st.slider(f"Modifier les points de {lp['Nom Roblox']}", 0, 25, pts, key=f"sl_{ip}")
                            if st.button("Sauvegarder Points", key=f"btn_p_{ip}"):
                                df_permis.at[ip, 'PTS'] = new_pts
                                conn.update(worksheet="Points Permis", data=df_permis)
                                commit_log("Staff", "PERMIS", f"Mis à {new_pts} pts pour {lp['Nom Roblox']}")
                                st.rerun()
                else:
                    st.info("Utilisateur trouvé en banque, mais aucun dossier Permis existant.")
            else:
                st.warning("Aucun citoyen trouvé.")

# ==============================================================================
# 🚗 MODULE : IMMATRICULATIONS (Transactions & Liste)
# ==============================================================================
target_tab_immat = tabs[0] if st.session_state.role != "Civil" else tabs[2]

with target_tab_immat:
    df_immat = load_table("Copie de Immatriculations")
    # Pour la liste déroulante des proprios
    df_users = load_table("Banque")
    owners_list = sorted(df_users["Nom Roblox"].unique().tolist()) if not df_users.empty else []

    # --- FORMULAIRE D'AJOUT (PRO & STAFF SEULEMENT) ---
    if st.session_state.role != "Civil":
        with st.expander("➕ Enregistrer une nouvelle immatriculation", expanded=True):
            with st.form("form_new_immat"):
                c1, c2 = st.columns(2)
                user_select = c1.selectbox("Propriétaire du véhicule", ["---"] + owners_list)
                car_brand = c1.selectbox("Marque", sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"]))
                plate_num = c2.text_input("Numéro de Plaque")
                assurance_type = c1.selectbox("Contrat Assurance", ["Non assuré", "RCT", "Averis"])
                secret_code = c2.text_input("Code Secret Véhicule", type="password")
                
                # --- CALCULATRICE FINANCIÈRE ---
                cost_ville, cost_rct, cost_averis, cost_jeune = 175, 0, 0, 0
                
                if user_select != "---":
                    user_data = df_users[df_users["Nom Roblox"] == user_select]
                    if not user_data.empty:
                        # Calcul Taxe Jeune Conducteur (< 30 jours)
                        try:
                            date_str = str(user_data.iloc[0]["Date d'arrivée"])
                            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                            if datetime.now() - date_obj < timedelta(days=30):
                                cost_jeune = 50
                        except: pass # Si erreur de date, on ignore la taxe
                        
                        # Calcul Frais Assurance
                        if assurance_type == "Averis":
                            cost_averis = 130
                        elif assurance_type == "RCT":
                            # Vérif si premier véhicule RCT
                            nb_cars = df_immat[(df_immat["Nom d'utilisateur ROBLOX"] == user_select) & (df_immat["Assurance"] == "RCT")].shape[0]
                            if nb_cars < 2: 
                                cost_rct = 150

                total_bill = cost_ville + cost_rct + cost_averis + cost_jeune
                
                # Affichage du Ticket
                st.markdown(f"""
                <div class='transaction-ticket'>
                    <b>FACTURE OFFICIELLE</b><br>
                    <small>Détail des frais appliqués</small>
                    <hr style='border: 0.5px dashed gray'>
                    Frais Administratifs : {cost_ville} $<br>
                    {'Frais RCT (Premier vhc) : ' + str(cost_rct) + ' $<br>' if cost_rct > 0 else ''}
                    {'Frais Averis : ' + str(cost_averis) + ' $<br>' if cost_averis > 0 else ''}
                    {'Majoration Jeune Permis : ' + str(cost_jeune) + ' $<br>' if cost_jeune > 0 else ''}
                    <hr>
                    <b style='font-size:1.2em'>TOTAL À PAYER : {total_bill} $</b>
                </div>
                """, unsafe_allow_html=True)
                
                if st.form_submit_button("💳 Valider la transaction"):
                    if user_select != "---" and plate_num and secret_code:
                        u_row = df_users[df_users["Nom Roblox"] == user_select]
                        current_solde = float(u_row.iloc[0]["Solde"])
                        
                        if current_solde >= total_bill:
                            # 1. Débit Client
                            df_users.at[u_row.index[0], "Solde"] = current_solde - total_bill
                            
                            # 2. Virement RCT (une10000)
                            if cost_rct > 0:
                                t_rct = df_users[df_users["Nom Roblox"] == TARGET_RCT]
                                if not t_rct.empty:
                                    df_users.at[t_rct.index[0], "Solde"] = float(t_rct.iloc[0]["Solde"]) + cost_rct
                            
                            # 3. Virement Averis (Moune2010)
                            if cost_averis > 0:
                                t_ave = df_users[df_users["Nom Roblox"] == TARGET_AVERIS]
                                if not t_ave.empty:
                                    df_users.at[t_ave.index[0], "Solde"] = float(t_ave.iloc[0]["Solde"]) + cost_averis
                            
                            # 4. Enregistrement Véhicule
                            new_car = pd.DataFrame([{
                                "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "Nom d'utilisateur ROBLOX": user_select,
                                "Marque du véhicule": car_brand,
                                "L'état de la plaque": "California",
                                "Numéro de la plaque": plate_num,
                                "Assurance": assurance_type,
                                "CODE": str(secret_code)
                            }])
                            
                            conn.update(worksheet="Banque", data=df_users)
                            conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_immat, new_car], ignore_index=True))
                            st.success("✅ Véhicule immatriculé et paiement effectué !")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Solde insuffisant sur le compte du citoyen.")

    # --- LISTE DES VÉHICULES (POUR TOUS) ---
    st.write("### 🚔 Base de Données Véhicules")
    q_veh = st.text_input("Rechercher par Plaque, Marque ou Propriétaire").lower()
    
    if q_veh:
        # Recherche simple
        res_v = df_immat[df_immat.apply(lambda r: q_veh in str(r).lower(), axis=1)]
        # Recherche croisée via Discord si besoin (comme pour les permis)
        if st.session_state.role == "Civil":
             # Si le civil tape son discord, on veut qu'il trouve ses voitures
          # ... (Le code juste avant : q_veh = st.text_input...)

    if q_veh:
        # Recherche simple
        res_v = df_immat[df_immat.apply(lambda r: q_veh in str(r).lower(), axis=1)]
        # Recherche croisée via Discord
        if st.session_state.role == "Civil":
             res_d = df_users[df_users["Nom Discord"].str.lower().str.contains(q_veh)]
             if not res_d.empty:
                 names = res_d["Nom Roblox"].tolist()
                 res_v = pd.concat([res_v, df_immat[df_immat["Nom d'utilisateur ROBLOX"].isin(names)]]).drop_duplicates()

        for iv, rv in res_v.iterrows():
            with st.container(border=True):
                # CORRECTION ICI : On sort la variable avant pour éviter le bug de l'apostrophe
                proprio = rv["Nom d'utilisateur ROBLOX"]
                
                st.markdown(f"**🚗 {rv['Marque du véhicule']}** | Plaque : `{rv['Numéro de la plaque']}`")
                st.caption(f"Propriétaire : {proprio} | Assurance : {rv['Assurance']}")
                
                # Options de gestion (Staff/Pro)
                if st.session_state.role != "Civil":
                    if st.button("Modifier Assurance", key=f"btn_m_{iv}"):
                        st.session_state[f"edit_v_{iv}"] = True
                    
                    if st.session_state.get(f"edit_v_{iv}", False):
                        verif = st.text_input("Code Sécurité requis", type="password", key=f"verif_{iv}")
                        if st.session_state.role == "Staff" or verif == str(rv['CODE']):
                            new_assu = st.selectbox("Nouvelle Assurance", ["Non assuré", "RCT", "Averis"], key=f"sel_{iv}")
                            if st.button("Valider Modification", key=f"save_{iv}"):
                                df_immat.at[iv, 'Assurance'] = new_assu
                                conn.update(worksheet="Copie de Immatriculations", data=df_immat)
                                st.rerun()
                            if st.button("🗑️ Supprimer le véhicule", key=f"del_{iv}"):
                                conn.update(worksheet="Copie de Immatriculations", data=df_immat.drop(iv))
                                st.rerun()
# ==============================================================================
# ➕ MODULE STAFF : CRÉATION PROFILS & JUSTICE
# ==============================================================================
if st.session_state.role == "Staff":
    
    # --- ONGLET 4 : CRÉATION PROFIL ---
    with tabs[3]:
        st.markdown("### ➕ Création Dossier Citoyen")
        st.info("Cette action crée le compte Bancaire ET le Permis. La date est automatique.")
        
        with st.form("form_create_profile"):
            new_roblox = st.text_input("Nom d'utilisateur Roblox")
            new_discord = st.text_input("Identifiant Discord")
            admin_name = st.text_input("Votre Pseudo Staff (Créateur)")
            start_money = st.number_input("Solde de départ", value=15000)
            
            if st.form_submit_button("🚀 Créer le Profil"):
                if new_roblox and new_discord and admin_name:
                    db_b = load_table("Banque")
                    db_p = load_table("Points Permis")
                    
                    # DATE AUTOMATIQUE (Important !)
                    today_str = datetime.now().strftime("%d/%m/%Y")
                    
                    # 1. Ajout Banque
                    line_b = pd.DataFrame([{
                        "Solde": start_money,
                        "Nom Discord": new_discord,
                        "Nom Roblox": new_roblox,
                        "Pseudo Admin": admin_name,
                        "Date d'arrivée": today_str
                    }])
                    
                    # 2. Ajout Permis
                    line_p = pd.DataFrame([{
                        "Nom Roblox": new_roblox,
                        "PTS": 25
                    }])
                    
                    conn.update(worksheet="Banque", data=pd.concat([db_b, line_b], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([db_p, line_p], ignore_index=True))
                    
                    commit_log("Staff", "CREATION", f"Nouveau citoyen : {new_roblox} ({today_str})")
                    st.success(f"Dossier créé pour {new_roblox} avec succès !")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Merci de remplir tous les champs.")

    # --- ONGLET 5 : JUSTICE ---
    with tabs[4]:
        st.markdown("### ⚖️ Tribunal - Sanctions Financières")
        with st.form("justice_form"):
            guilty = st.selectbox("Citoyen à sanctionner", owners_list)
            fine_amount = st.number_input("Montant de l'amende", min_value=0)
            reason = st.text_area("Motif de la sanction")
            
            if st.form_submit_button("⚖️ Appliquer la Sentence"):
                db_justice = load_table("Banque")
                target_idx = db_justice[db_justice["Nom Roblox"] == guilty].index
                
                if not target_idx.empty:
                    idx = target_idx[0]
                    current = float(db_justice.at[idx, "Solde"])
                    db_justice.at[idx, "Solde"] = current - fine_amount
                    conn.update(worksheet="Banque", data=db_justice)
                    commit_log("Justice", "AMENDE", f"{guilty} -{fine_amount}$ ({reason})")
                    st.success("Sanction appliquée.")
                    st.rerun()

    # --- ONGLET 6 : STATISTIQUES ---
    with tabs[5]:
        st.markdown("### 📊 Indicateurs Économiques")
        c1, c2, c3 = st.columns(3)
        c1.metric("Masse Monétaire Totale", f"{load_table('Banque')['Solde'].astype(float).sum():,.0f} $")
        c2.metric("Véhicules en circulation", len(load_table('Copie de Immatriculations')))
        c3.metric("Population Enregistrée", len(load_table('Banque')))

    # --- ONGLET 7 : LOGS ---
    with tabs[6]:
        st.markdown("### 📜 Registre des Activités")
        st.dataframe(load_table("Logs").iloc[::-1], use_container_width=True)

# --- FIN DU DOCUMENT ---
st.markdown("---")
st.markdown("<center><small>RCRP Integrated System v11.0 | République de Californie | © 2026</small></center>", unsafe_allow_html=True)
