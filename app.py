# ==============================================================================
# 🏛️ REPUBLIQUE DE CALIFORNIE RP - SYSTEME DE GESTION INTEGRAL (v9.80)
# ==============================================================================
# Plateforme de gestion centralisée pour l'économie et les transports.
# Développeur : RCRP Tech 
# 
# CONFIGURATION DES FLUX FINANCIERS :
# - Paiements Assurance RCT : Redirection vers 'une10000'
# - Paiements Assurance Averis : Redirection vers 'Moune2010'
# - Création de Profil : Date et Admin auto-générés.
# ==============================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION INITIALE DU PORTAIL ---
st.set_page_config(
    page_title="RCRP - Portail de l'État de Californie",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ENGINE CSS : DESIGN HAUTE DÉFINITION ---
st.markdown("""
    <style>
    /* Global Background */
    .main { background-color: #0b0d10; }
    
    /* Conteneurs de connexion - Format 600px */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(30, 34, 40, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 40px !important;
        height: 600px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0px 20px 40px rgba(0,0,0,0.6);
    }

    /* Ticket de transaction Premium */
    .transaction-ticket {
        background: linear-gradient(135deg, #1a1c20 0%, #0f1113 100%);
        border: 1px solid #2ecc71;
        border-left: 10px solid #2ecc71;
        padding: 25px;
        border-radius: 12px;
        margin: 20px 0;
        color: #ffffff;
        font-family: 'Consolas', monospace;
    }

    /* Métriques de solde */
    .stMetric {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }

    /* Logo Sidebar et Arrondis */
    [data-testid="stSidebar"] img {
        border-radius: 25px;
        border: 3px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 25px;
        transition: 0.3s;
    }
    [data-testid="stSidebar"] img:hover { transform: scale(1.02); }

    /* Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px 10px 0 0;
        padding: 12px 25px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e74c3c !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PARAMÈTRES ET CONSTANTES ---
CODE_STAFF_SECURE = "RCRPFR-25-26" 
CODE_RCT_SECURE = "RCT-26-RCRPFR" 
COMPTE_RCT = "une10000" 
COMPTE_AVERIS = "Moune2010"
LOGO_OFFICIEL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless"

# --- SYSTÈME DE SESSION ---
if "role" not in st.session_state:
    st.session_state.role = None
if "auth_time" not in st.session_state:
    st.session_state.auth_time = None

# --- MOTEUR DE CONNEXION GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db(sheet_name):
    """Charge les données brutes depuis Google Sheets."""
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except Exception as error_db:
        st.error(f"Erreur de communication Base de Données : {error_db}")
        return pd.DataFrame()

def record_activity(action_desc):
    """Enregistre les actions dans le journal d'audit."""
    try:
        df_logs = get_db("Logs")
        log_entry = pd.DataFrame([{
            "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Agent": st.session_state.role if st.session_state.role else "Système",
            "Action": action_desc
        }])
        conn.update(worksheet="Logs", data=pd.concat([df_logs, log_entry], ignore_index=True))
    except:
        pass

# ==============================================================================
# 🚪 SECTION 1 : PORTAIL D'ACCÈS SÉCURISÉ
# ==============================================================================
if st.session_state.role is None:
    st.title("🏛️ République de Californie - Accès Gouvernemental")
    st.write("Bienvenue sur le terminal de gestion sécurisé de l'État.")
    st.divider()
    
    col_civ, col_pro, col_staff = st.columns(3)
    
    with col_civ:
        with st.container(border=True):
            st.markdown("### 👤 Espace Citoyen")
            st.info("Consultez vos comptes, véhicules et points de permis.")
            if st.button("Se connecter comme Citoyen", use_container_width=True):
                st.session_state.role = "Civil"
                record_activity("Connexion Citoyen")
                st.rerun()

    with col_pro:
        with st.container(border=True):
            st.markdown("### 🛠️ Espace Entreprise")
            st.write("Interface réservée aux agents RCT et Averis.")
            code_input_pro = st.text_input("Code Entreprise", type="password", key="login_pro")
            if st.button("Accès Professionnel", use_container_width=True):
                if code_input_pro == CODE_RCT_SECURE:
                    st.session_state.role = "RCT"
                    record_activity("Connexion Entreprise RCT")
                    st.rerun()
                else:
                    st.error("Code d'accès invalide.")

    with col_staff:
        with st.container(border=True):
            st.markdown("### 👮 Espace Staff")
            st.write("Contrôle total des bases de données de l'État.")
            code_input_staff = st.text_input("Code de Sécurité", type="password", key="login_staff")
            if st.button("Accès Administration", use_container_width=True):
                if code_input_staff == CODE_STAFF_SECURE:
                    st.session_state.role = "Staff"
                    record_activity("Connexion Administration Staff")
                    st.rerun()
                else:
                    st.error("Accès refusé. Tentative loggée.")
    st.stop()

# ==============================================================================
# 🖥️ SECTION 2 : DASHBOARD ET SIDEBAR
# ==============================================================================
with st.sidebar:
    st.image(LOGO_OFFICIEL, use_container_width=True)
    st.markdown(f"🛂 Agent connecté : **{st.session_state.role}**")
    if st.button("🚪 Déconnexion du système", use_container_width=True):
        record_activity("Déconnexion")
        st.session_state.role = None
        st.rerun()
    st.divider()
    st.write(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"⏰ **Heure :** {datetime.now().strftime('%H:%M')}")
    if st.button("🔄 Actualiser les données"):
        st.rerun()

# CONFIGURATION DES ONGLETS SELON LES PRIVILÈGES
if st.session_state.role == "Staff":
    main_tabs = st.tabs(["🚗 Immatriculations", "💰 Banque Centrale", "🪪 Permis", "➕ Création Profils", "⚖️ Justice", "📊 Statistiques", "📜 Journal d'Audit"])
elif st.session_state.role == "RCT":
    main_tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation Pro", "📜 Mes Logs"])
else:
    main_tabs = st.tabs(["🚗 Mes Véhicules", "💰 Mon Portefeuille", "🪪 Mon Permis"])

# ==============================================================================
# 🚗 MODULE 3 : GESTION DES IMMATRICULATIONS (RCT/AVERIS)
# ==============================================================================
with main_tabs[0]:
    df_immat = get_db("Copie de Immatriculations")
    df_banque = get_db("Banque")
    liste_noms = sorted(df_banque["Nom Roblox"].unique().tolist()) if not df_banque.empty else []

    with st.expander("➕ Enregistrer un Nouveau Véhicule"):
        with st.form("creation_vehicule_form"):
            c1, c2 = st.columns(2)
            proprio = c1.selectbox("👤 Titulaire", ["--- Choisir ---"] + liste_noms)
            marque = c1.selectbox("🚘 Marque", sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"]))
            plaque = c2.text_input("🔢 Numéro de Plaque")
            assurance = c1.selectbox("🛡️ Type d'Assurance", ["Non assuré", "RCT", "Averis"])
            code_v = c2.text_input("🔑 Code Secret du Véhicule", type="password")
            
            # --- LOGIQUE DE CALCUL DE LA FACTURE ---
            f_etat, f_rct, f_ave, f_jeune = 175, 0, 0, 0
            if proprio != "--- Choisir ---":
                u_data = df_banque[df_banque["Nom Roblox"] == proprio]
                if not u_data.empty:
                    if assurance == "Averis":
                        f_ave = 130
                        try:
                            d_arr = datetime.strptime(str(u_data.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                            if datetime.now() - d_arr < timedelta(days=30): f_jeune = 50
                        except: pass
                    elif assurance == "RCT":
                        count_v = df_immat[(df_immat["Nom d'utilisateur ROBLOX"] == proprio) & (df_immat["Assurance"] == "RCT")].shape[0]
                        if count_v < 2: f_rct = 150

            total_taxe = f_etat + f_rct + f_ave + f_jeune
            
            st.markdown(f"""
            <div class='transaction-ticket'>
                <b>DÉTAIL DE LA FACTURATION :</b><br>
                • Frais de Dossier État : {f_etat}$<br>
                {f'• Prime Assurance RCT : {f_rct}$<br>' if f_rct > 0 else ''}
                {f'• Prime Assurance Averis : {f_ave}$<br>' if f_ave > 0 else ''}
                {f'• Taxe Jeune Citoyen : {f_jeune}$<br>' if f_jeune > 0 else ''}
                <hr style='border: 0.1px dashed #2ecc71'>
                <span style='font-size: 18px; color: #2ecc71;'>TOTAL À PAYER : {total_taxe}$</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.form_submit_button("💳 Confirmer et Enregistrer"):
                if proprio != "--- Choisir ---" and plaque and code_v:
                    cli_data = df_banque[df_banque["Nom Roblox"] == proprio]
                    solde_actuel = float(cli_data.iloc[0]["Solde"])
                    
                    if solde_actuel >= total_taxe:
                        # 1. Débit Citoyen
                        df_banque.at[cli_data.index[0], "Solde"] = solde_actuel - total_taxe
                        
                        # 2. Transfert RCT (une10000)
                        if f_rct > 0:
                            target_rct = df_banque[df_banque["Nom Roblox"] == COMPTE_RCT]
                            if not target_rct.empty:
                                df_banque.at[target_rct.index[0], "Solde"] = float(target_rct.iloc[0]["Solde"]) + f_rct
                        
                        # 3. Transfert Averis (Moune2010)
                        if f_ave > 0:
                            target_ave = df_banque[df_banque["Nom Roblox"] == COMPTE_AVERIS]
                            if not target_ave.empty:
                                df_banque.at[target_ave.index[0], "Solde"] = float(target_ave.iloc[0]["Solde"]) + f_ave
                        
                        # 4. Création Ligne Véhicule
                        new_vehicule = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Nom d'utilisateur ROBLOX": proprio,
                            "Marque du véhicule": marque,
                            "L'état de la plaque": "California",
                            "Numéro de la plaque": plaque,
                            "Assurance": assurance,
                            "CODE": str(code_v)
                        }])
                        
                        conn.update(worksheet="Banque", data=df_banque)
                        conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_immat, new_vehicule], ignore_index=True))
                        record_activity(f"Immat {plaque} pour {proprio}")
                        st.success("✅ Véhicule enregistré avec succès !"); time.sleep(1); st.rerun()
                    else:
                        st.error("❌ Solde insuffisant sur le compte citoyen.")

    st.divider()
    recherche = st.text_input("🔍 Rechercher une plaque, une marque ou un citoyen").lower()
    if not df_immat.empty:
        filtre = df_immat[df_immat.apply(lambda r: recherche in str(r).lower(), axis=1)]
        for idx, row in filtre.iterrows():
            with st.container(border=True):
                st.write(f"🚗 **Plaque : {row['Numéro de la plaque']}** | 🛡️ {row['Assurance']}")
                st.write(f"👤 Propriétaire : {row['Nom d\'utilisateur ROBLOX']} | 🚘 {row['Marque du véhicule']}")
                
                if st.button("🛠️ Options de gestion", key=f"opt_{idx}"):
                    st.session_state[f"edit_panel_{idx}"] = not st.session_state.get(f"edit_panel_{idx}", False)
                
                if st.session_state.get(f"edit_panel_{idx}"):
                    auth_c = st.text_input("Vérification du Code Secret", type="password", key=f"auth_v_{idx}")
                    if st.session_state.role == "Staff" or auth_c == str(row['CODE']):
                        with st.form(f"edit_form_{idx}"):
                            new_assurance = st.selectbox("Modifier l'Assurance", ["Non assuré", "RCT", "Averis"])
                            if st.form_submit_button("Sauvegarder les modifications"):
                                df_immat.at[idx, 'Assurance'] = new_assurance
                                conn.update(worksheet="Copie de Immatriculations", data=df_immat)
                                record_activity(f"Modif Immat {row['Numéro de la plaque']}")
                                st.rerun()
                        if st.button("🗑️ Supprimer le véhicule du registre", key=f"del_{idx}"):
                            df_final = df_immat.drop(idx)
                            conn.update(worksheet="Copie de Immatriculations", data=df_final)
                            record_activity(f"Suppression Immat {row['Numéro de la plaque']}")
                            st.rerun()

# ==============================================================================
# 💰 MODULE 4 : BANQUE ET GESTION MONÉTAIRE
# ==============================================================================
with main_tabs[1 if st.session_state.role != "Staff" else 1]:
    df_bank_sys = get_db("Banque")
    if st.session_state.role == "Civil":
        target_name = st.text_input("🔍 Entrez votre Nom Roblox pour voir votre solde").strip().lower()
        if target_name:
            compte = df_bank_sys[df_bank_sys["Nom Roblox"].str.lower() == target_name]
            if not compte.empty:
                st.metric("💵 Solde Bancaire Actuel", f"{float(compte.iloc[0]['Solde']):,.0f} $")
            else:
                st.warning("Compte introuvable.")
    else:
        st.write("### 🏦 Administration des Comptes Citoyens")
        recherche_b = st.text_input("🔍 Rechercher un citoyen (Nom, Discord, Admin...)").lower()
        if recherche_b:
            res_b = df_bank_sys[df_bank_sys.apply(lambda r: recherche_b in str(r).lower(), axis=1)]
            for ib, lb in res_b.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **{lb['Nom Roblox']}** | 💬 Discord : {lb['Nom Discord']}")
                    st.write(f"📅 Arrivée : {lb['Date d\'arrivée']} | 👮 Staff : {lb['Pseudo Admin']}")
                    val_s = float(lb['Solde'])
                    st.metric("Solde", f"{val_s:,.0f} $")
                    with st.form(f"bank_form_{ib}"):
                        montant_op = st.number_input("Montant", min_value=0.0, step=100.0)
                        bc1, bc2 = st.columns(2)
                        if bc1.form_submit_button("📉 Débiter"):
                            df_bank_sys.at[ib, 'Solde'] = val_s - montant_op
                            conn.update(worksheet="Banque", data=df_bank_sys)
                            record_activity(f"Débit {montant_op}$ -> {lb['Nom Roblox']}")
                            st.rerun()
                        if bc2.form_submit_button("📈 Créditer") and st.session_state.role == "Staff":
                            df_bank_sys.at[ib, 'Solde'] = val_s + montant_op
                            conn.update(worksheet="Banque", data=df_bank_sys)
                            record_activity(f"Crédit {montant_op}$ -> {lb['Nom Roblox']}")
                            st.rerun()

# ==============================================================================
# 🪪 MODULE 5 : PERMIS ET CRÉATION DE PROFILS (STAFF)
# ==============================================================================
if st.session_state.role == "Staff":
    with main_tabs[2]: # Onglet Permis
        st.write("### 🪪 Contrôle des Permis de Conduire")
        df_permis = get_db("Points Permis")
        rech_p = st.text_input("🔍 Chercher un titulaire de permis").lower()
        if rech_p:
            res_p = df_permis[df_permis.apply(lambda r: rech_p in str(r).lower(), axis=1)]
            for ip, lp in res_p.iterrows():
                with st.form(f"permis_form_{ip}"):
                    st.write(f"👤 Titulaire : **{lp['Nom Roblox']}**")
                    pts_n = st.number_input("Points", 0, 25, value=int(lp['PTS']))
                    if st.form_submit_button("💾 Actualiser les points"):
                        df_permis.at[ip, 'PTS'] = pts_n
                        conn.update(worksheet="Points Permis", data=df_permis)
                        record_activity(f"Maj Points Permis {lp['Nom Roblox']} -> {pts_n}")
                        st.rerun()

    with main_tabs[3]: # Onglet Profils
        st.write("### ➕ Créer un Nouveau Dossier Citoyen")
        st.info("Cette action crée simultanément le compte bancaire et le dossier de permis.")
        with st.form("creation_profil_global"):
            c_r, c_d = st.columns(2)
            n_roblox = c_r.text_input("Nom d'utilisateur ROBLOX")
            n_discord = c_d.text_input("Identifiant Discord")
            p_admin = c_r.text_input("Nom du Staff créateur")
            dotation = c_d.number_input("Dotation initiale", value=15000.0)
            
            if st.form_submit_button("🚀 Enregistrer le Nouveau Citoyen"):
                db_b, db_p = get_db("Banque"), get_db("Points Permis")
                # AJOUT AUTOMATIQUE DE LA DATE ET DE L'ADMIN
                nl_b = pd.DataFrame([{
                    "Solde": dotation, 
                    "Nom Discord": n_discord, 
                    "Nom Roblox": n_roblox, 
                    "Pseudo Admin": p_admin, 
                    "Date d'arrivée": datetime.now().strftime("%d/%m/%Y")
                }])
                nl_p = pd.DataFrame([{"Nom Roblox": n_roblox, "PTS": 25}])
                
                conn.update(worksheet="Banque", data=pd.concat([db_b, nl_b], ignore_index=True))
                conn.update(worksheet="Points Permis", data=pd.concat([db_p, nl_p], ignore_index=True))
                record_activity(f"Création profil complet : {n_roblox}")
                st.success(f"Profil de {n_roblox} créé avec succès !"); time.sleep(1); st.rerun()

    with main_tabs[4]: # Onglet Justice
        st.write("### ⚖️ Système Judiciaire et Amendes")
        with st.form("amende_form"):
            coupable = st.selectbox("Sélectionner le citoyen", liste_noms)
            montant_a = st.number_input("Montant de l'amende", min_value=0)
            motif = st.text_area("Motif de la sanction")
            if st.form_submit_button("⚖️ Appliquer l'Amende"):
                db_j = get_db("Banque")
                idx_j = db_j[db_j["Nom Roblox"] == coupable]
                if not idx_j.empty:
                    db_j.at[idx_j.index[0], "Solde"] = float(idx_j.iloc[0]["Solde"]) - montant_a
                    conn.update(worksheet="Banque", data=db_j)
                    record_activity(f"AMENDE {montant_a}$ -> {coupable} ({motif})")
                    st.success("Sanction appliquée et débitée."); st.rerun()

    with main_tabs[5]: # Onglet Statistiques
        st.write("### 📊 Analyse de l'Économie")
        s1, s2, s3 = st.columns(3)
        s1.metric("Masse Monétaire Totale", f"{df_banque['Solde'].astype(float).sum():,.0f} $")
        s2.metric("Véhicules en Circulation", len(df_immat))
        s3.metric("Citoyens Enregistrés", len(df_banque))

    with main_tabs[6]: # Onglet Logs
        st.write("### 📜 Registre National des Activités")
        st.dataframe(get_db("Logs").iloc[::-1], use_container_width=True)

# --- PIED DE PAGE ---
st.markdown("---")
st.markdown("<center><small>RCRP Integrated System v9.80 | Gouvernement de Californie | © 2026</small></center>", unsafe_allow_html=True)
