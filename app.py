# ==============================================================================
# 🏛️ REPUBLIQUE DE CALIFORNIE RP - SYSTEME DE GESTION INTEGRAL (v11.2)
# ==============================================================================
# Plateforme de gestion centralisée : Économie, Transports, Justice et Logistique.
# Version : 11.2 | Date : 08/02/2026 | Développeur : RCRP Tech Division
# 
# [MEMOIRE DU SYSTEME]
# - Assurances Averis : Crédits transférés vers 'Moune2010'
# - Assurances RCT : Crédits transférés vers 'une10000'
# - Création Profil : Date d'arrivée générée AUTOMATIQUEMENT (Jour J).
# - Recherche Civile : Compatible Nom Roblox ET Nom Discord.
# - Permis : Affichage visuel (Vert/Orange/Rouge) pour les civils.
# - Logo : Correction du rendu visuel et des proportions.
# ==============================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time
import random

# --- 1. CONFIGURATION DE L'INTERFACE GOUVERNEMENTALE ---
st.set_page_config(
    page_title="RCRP - Système Intégré de l'État",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ENGINE CSS : DESIGN COMPLET (EXTRÊMEMENT DÉTAILLÉ) ---
st.markdown("""
    <style>
    /* Importation Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400;700&display=swap');

    .main { background-color: #0b0d10; color: #ecf0f1; font-family: 'Roboto', sans-serif; }
    
    /* Global Animations */
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .stApp { animation: fadeIn 0.6s ease-out; }

    /* Login Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(145deg, #161b22 0%, #0d1117 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        padding: 45px !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.6) !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #c0392b !important;
        transform: translateY(-5px);
    }

    /* Financial Ticket - Style Reçu Fiscal */
    .transaction-ticket {
        background: #fdfdfd;
        border-left: 10px solid #27ae60;
        padding: 30px;
        border-radius: 4px;
        margin: 25px 0;
        color: #1a1a1a;
        font-family: 'Courier New', monospace;
        box-shadow: 10px 10px 0px rgba(39, 174, 96, 0.2);
        position: relative;
    }
    .transaction-ticket::after {
        content: "OFFICIEL CALIFORNIE";
        position: absolute;
        top: 10px; right: 10px;
        font-size: 8px; color: #ccc; transform: rotate(15deg);
    }

    /* Dossier Civil (Carte ID) */
    .id-card {
        background: linear-gradient(135deg, rgba(44, 62, 80, 0.8) 0%, rgba(52, 73, 94, 0.8) 100%);
        border: 1px solid rgba(52, 152, 219, 0.3);
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
        position: relative; overflow: hidden;
    }
    .id-card::before {
        content: ""; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
    }

    /* License Box */
    .license-box {
        padding: 25px; border-radius: 20px; text-align: center;
        margin-top: 15px; background: rgba(0,0,0,0.4);
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .license-box:hover { transform: scale(1.03); }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0b0d10; }
    ::-webkit-scrollbar-thumb { background: #c0392b; border-radius: 10px; }

    /* Metrics Styling */
    [data-testid="stMetricValue"] { font-family: 'Orbitron', sans-serif; color: #e74c3c !important; }
    
    /* Sidebar Logo Fix */
    [data-testid="stSidebarNav"] { padding-top: 20px; }
    .sidebar-logo-container { text-align: center; padding: 10px; }
    
    /* Status Labels */
    .status-badge {
        padding: 5px 12px; border-radius: 50px; font-size: 12px; font-weight: bold; text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONSTANTES ET SÉCURITÉ ---
AUTH_ADMIN_KEY = "RCRPFR-25-26" 
AUTH_PRO_KEY = "RCT-26-RCRPFR" 
TARGET_RCT = "une10000" 
TARGET_AVERIS = "Moune2010"
ASSET_LOGO = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless"

# --- 4. ENGINE DE DONNÉES (RÉSILIENCE ACCRUE) ---
if "role" not in st.session_state: st.session_state.role = None
if "msg_queue" not in st.session_state: st.session_state.msg_queue = []

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(table_name):
    """Chargement sécurisé avec gestion des erreurs Sheets"""
    try:
        st.cache_data.clear()
        data = conn.read(worksheet=table_name, ttl=0).dropna(how='all').fillna("")
        return data
    except Exception as e:
        st.error(f"Erreur de liaison Base de Données ({table_name}): {str(e)}")
        return pd.DataFrame()

def save_data(table_name, dataframe):
    """Sauvegarde avec vérification d'intégrité"""
    try:
        conn.update(worksheet=table_name, data=dataframe)
        return True
    except Exception as e:
        st.error(f"Échec de synchronisation Cloud : {str(e)}")
        return False

def audit_log(user, action, details):
    """Système de traçabilité gouvernementale"""
    logs = load_data("Logs")
    new_log = pd.DataFrame([{
        "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Opérateur": user,
        "Catégorie": action,
        "Description": details,
        "ID_Session": random.randint(1000, 9999)
    }])
    save_data("Logs", pd.concat([logs, new_log], ignore_index=True))

# ==============================================================================
# 🚪 PORTAIL D'ACCÈS SÉCURISÉ
# ==============================================================================
if st.session_state.role is None:
    st.markdown("<h1 style='text-align: center; color: #c0392b; font-family: Orbitron;'>🏛️ RÉPUBLIQUE DE CALIFORNIE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.6;'>Système Centralisé de Gestion des Services de l'État</p>", unsafe_allow_html=True)
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("### 👤 Citoyen")
        st.caption("Consultez vos comptes, véhicules et permis en libre-service.")
        if st.button("ACCÈS PUBLIC", use_container_width=True, type="secondary"):
            st.session_state.role = "Civil"
            st.rerun()

    with c2:
        st.markdown("### 🛠️ Entreprises")
        st.caption("Espace réservé RCT & Averis. Gestion de la facturation client.")
        p_key = st.text_input("Clé d'accès Pro", type="password", key="login_pro")
        if st.button("CONNEXION PRO", use_container_width=True, type="primary"):
            if p_key == AUTH_PRO_KEY:
                st.session_state.role = "RCT"
                audit_log("SYSTÈME", "AUTH", "Connexion réussie Espace Professionnel")
                st.rerun()
            else: st.error("Clé invalide.")

    with c3:
        st.markdown("### 👮 Administration")
        st.caption("Haute autorité. Modification des registres nationaux.")
        s_key = st.text_input("Clé d'accès Staff", type="password", key="login_staff")
        if st.button("ACCÈS SÉCURISÉ", use_container_width=True, type="primary"):
            if s_key == AUTH_ADMIN_KEY:
                st.session_state.role = "Staff"
                audit_log("SYSTÈME", "AUTH", "Connexion ADMIN détectée")
                st.rerun()
            else: st.error("Accès refusé.")
    st.stop()

# ==============================================================================
# 🖥️ DASHBOARD INTERACTIF
# ==============================================================================
with st.sidebar:
    st.markdown(f"""<div class='sidebar-logo-container'><img src='{ASSET_LOGO}' width='180'></div>""", unsafe_allow_html=True)
    st.markdown(f"### 🛂 {st.session_state.role}")
    st.info(f"Connecté le: {datetime.now().strftime('%d/%m/%Y')}")
    if st.button("🚪 QUITTER LA SESSION", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    st.divider()
    st.markdown("#### 🚀 Raccourcis")
    if st.session_state.role == "Staff":
        st.button("Vider le Cache", on_click=st.cache_data.clear)
    st.caption("v11.2 © 2026 RCRP Tech")

# --- SÉLECTION DES MODULES SELON LE RÔLE ---
if st.session_state.role == "Staff":
    t1, t2, t3, t4, t5, t6, t7 = st.tabs(["🚗 IMMAT", "🏦 BANQUE", "🪪 PERMIS", "👥 PROFILS", "⚖️ JUSTICE", "📊 STATS", "📜 AUDIT"])
elif st.session_state.role == "RCT":
    t1, t2, t3 = st.tabs(["🚗 IMMATRICULATIONS", "💰 FACTURATION", "📜 HISTORIQUE PRO"])
else:
    t1, t2, t3 = st.tabs(["🏦 MON COMPTE", "🪪 MON PERMIS", "🚗 MES VÉHICULES"])

# ==============================================================================
# 💰 MODULE FINANCIER (BANQUE & IDENTITÉ)
# ==============================================================================
tab_bank = t2 if st.session_state.role == "Staff" else t1
with tab_bank:
    df_bank = load_data("Banque")
    st.subheader("🏦 Registre Central des Comptes")
    
    search = st.text_input("🔍 Rechercher un citoyen (Nom Roblox ou Discord)", placeholder="Ex: Jean_Dupont...").lower()
    
    if search:
        results = df_bank[(df_bank["Nom Roblox"].str.lower().str.contains(search)) | 
                         (df_bank["Nom Discord"].str.lower().str.contains(search))]
        
        if not results.empty:
            for idx, row in results.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="id-card">
                        <span style='position:absolute; right:15px; top:15px; color:rgba(255,255,255,0.2); font-weight:bold;'>ID #{idx}</span>
                        <h2 style='margin:0; color:#3498db;'>{row['Nom Roblox']}</h2>
                        <p style='margin:0; opacity:0.8;'>Identifiant Discord : <b>{row['Nom Discord']}</b></p>
                        <hr style='border: 0.1px solid rgba(255,255,255,0.1);'>
                        <p style='font-size: 0.9em;'>📅 Enregistré le : {row["Date d'arrivée"]} | 👮 Agent : {row['Pseudo Admin']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.metric("DISPONIBILITÉS BANCAIRES", f"{float(row['Solde']):,.0f} $", delta="Compte Actif")
                    
                    if st.session_state.role == "Staff":
                        with st.expander("⚙️ OPÉRATIONS BANCAIRES"):
                            col1, col2 = st.columns(2)
                            m_val = col1.number_input(f"Montant ({row['Nom Roblox']})", min_value=0.0, step=500.0, key=f"amt_{idx}")
                            action = col2.selectbox("Type d'opération", ["CRÉDIT (Ajouter)", "DÉBIT (Retirer)"], key=f"act_{idx}")
                            
                            if st.button("CONFIRMER LA TRANSACTION", key=f"btn_tx_{idx}"):
                                if action == "DÉBIT (Retirer)":
                                    df_bank.at[idx, 'Solde'] = float(row['Solde']) - m_val
                                    audit_log("Staff", "DEBIT", f"-{m_val}$ pour {row['Nom Roblox']}")
                                else:
                                    df_bank.at[idx, 'Solde'] = float(row['Solde']) + m_val
                                    audit_log("Staff", "CREDIT", f"+{m_val}$ pour {row['Nom Roblox']}")
                                
                                if save_data("Banque", df_bank):
                                    st.success("Transaction validée par la Banque Centrale.")
                                    st.rerun()
        else: st.warning("⚠️ Aucun dossier trouvé pour cette recherche.")

# ==============================================================================
# 🚗 MODULE DE GESTION DES VÉHICULES (IMMATRICULATIONS)
# ==============================================================================
tab_immat = t1 if st.session_state.role != "Civil" else t3
with tab_immat:
    df_immat = load_data("Copie de Immatriculations")
    df_b = load_data("Banque")
    
    if st.session_state.role != "Civil":
        st.subheader("📋 Nouvelle Immatriculation")
        with st.container(border=True):
            with st.form("immat_engine"):
                c1, c2 = st.columns(2)
                proprio = c1.selectbox("Sélectionner le Propriétaire", sorted(df_b["Nom Roblox"].unique().tolist()))
                marque = c1.selectbox("Marque du véhicule", sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"]))
                plaque = c2.text_input("Numéro de Plaque (Ex: ABC-123)")
                assu = c2.selectbox("Assurance", ["Non assuré", "RCT", "Averis"])
                v_code = c2.text_input("Code de Sécurité (CODE)", type="password", help="Code unique pour modifier le dossier plus tard.")
                
                # --- LOGIQUE FINANCIÈRE COMPLEXE ---
                base, rct_f, ave_f, j_f = 175, 0, 0, 0
                u_data = df_b[df_b["Nom Roblox"] == proprio]
                
                if not u_data.empty:
                    try:
                        d_in = datetime.strptime(str(u_data.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                        if datetime.now() - d_in < timedelta(days=30): j_f = 50
                    except: j_f = 0
                    
                    if assu == "Averis": ave_f = 130
                    elif assu == "RCT":
                        nb_v = df_immat[(df_immat["Nom d'utilisateur ROBLOX"] == proprio) & (df_immat["Assurance"] == "RCT")].shape[0]
                        if nb_v < 2: rct_f = 150
                
                total = base + rct_f + ave_f + j_f
                st.markdown(f"""<div class='transaction-ticket'><b>BON D'IMMATRICULATION</b><br>Détail: Admin({base}) | RCT({rct_f}) | Ave({ave_f}) | Jeune({j_f})<br><hr><b>TOTAL : {total} $</b></div>""", unsafe_allow_html=True)
                
                if st.form_submit_button("VALIDER ET PAYER"):
                    if proprio and plaque and v_code:
                        solde_actuel = float(u_data.iloc[0]["Solde"])
                        if solde_actuel >= total:
                            # Prélèvement
                            df_b.at[u_data.index[0], "Solde"] = solde_actuel - total
                            # Reversement Assurances
                            if rct_f > 0:
                                t_rct = df_b[df_b["Nom Roblox"] == TARGET_RCT].index
                                if not t_rct.empty: df_b.at[t_rct[0], "Solde"] += rct_f
                            if ave_f > 0:
                                t_ave = df_b[df_b["Nom Roblox"] == TARGET_AVERIS].index
                                if not t_ave.empty: df_b.at[t_ave[0], "Solde"] += ave_f
                            
                            # Enregistrement Véhicule
                            new_v = pd.DataFrame([{
                                "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "Nom d'utilisateur ROBLOX": proprio,
                                "Marque du véhicule": marque,
                                "L'état de la plaque": "California",
                                "Numéro de la plaque": plaque.upper(),
                                "Assurance": assu,
                                "CODE": str(v_code)
                            }])
                            
                            save_data("Banque", df_b)
                            save_data("Copie de Immatriculations", pd.concat([df_immat, new_v], ignore_index=True))
                            st.success("Immatriculation terminée. Paiement traité.")
                            st.rerun()
                        else: st.error("Fonds insuffisants.")
    
    # --- LISTE DES VÉHICULES ---
    st.subheader("🚗 Registre des Véhicules")
    v_search = st.text_input("Filtrer par Plaque ou Nom", key="v_search").lower()
    v_results = df_immat[df_immat.apply(lambda r: v_search in str(r).lower(), axis=1)]
    
    for v_idx, v_row in v_results.iterrows():
        with st.container(border=True):
            col_v1, col_v2 = st.columns([3, 1])
            col_v1.markdown(f"**{v_row['Marque du véhicule']}** | Plaque: `{v_row['Numéro de la plaque']}`")
            col_v1.caption(f"👤 {v_row['Nom d'utilisateur ROBLOX']} | 🛡️ {v_row['Assurance']}")
            
            if st.session_state.role != "Civil":
                if col_v2.button("MAJ ASSURANCE", key=f"up_assu_{v_idx}"):
                    st.session_state[f"edit_v_{v_idx}"] = True
                
                if st.session_state.get(f"edit_v_{v_idx}", False):
                    code_check = st.text_input("Code de sécurité requis", type="password", key=f"chk_{v_idx}")
                    if st.session_state.role == "Staff" or code_check == str(v_row['CODE']):
                        new_a = st.selectbox("Nouveau contrat", ["Non assuré", "RCT", "Averis"], key=f"sel_a_{v_idx}")
                        if st.button("Enregistrer", key=f"save_v_{v_idx}"):
                            df_immat.at[v_idx, 'Assurance'] = new_a
                            save_data("Copie de Immatriculations", df_immat)
                            st.rerun()

# ==============================================================================
# ➕ MODULE STAFF : CRÉATION DE PROFIL (AUTOMATIQUE)
# ==============================================================================
if st.session_state.role == "Staff":
    with t4:
        st.subheader("👥 Création d'Identité Judiciaire")
        with st.form("new_profile"):
            st.info("La date d'arrivée sera réglée sur la date actuelle automatiquement.")
            f_roblox = st.text_input("Nom Roblox Officiel")
            f_discord = st.text_input("Identifiant Discord")
            f_admin = st.text_input("Pseudo Staff Référent")
            f_money = st.number_input("Solde Initial ($)", value=15000)
            
            if st.form_submit_button("GÉNÉRER LE DOSSIER"):
                if f_roblox and f_discord:
                    db_bank = load_data("Banque")
                    db_permis = load_data("Points Permis")
                    
                    today = datetime.now().strftime("%d/%m/%Y")
                    
                    # Entry 1: Banque
                    entry_b = pd.DataFrame([{
                        "Solde": f_money, "Nom Discord": f_discord, "Nom Roblox": f_roblox,
                        "Pseudo Admin": f_admin, "Date d'arrivée": today
                    }])
                    # Entry 2: Permis
                    entry_p = pd.DataFrame([{"Nom Roblox": f_roblox, "PTS": 25}])
                    
                    save_data("Banque", pd.concat([db_bank, entry_b], ignore_index=True))
                    save_data("Points Permis", pd.concat([db_permis, entry_p], ignore_index=True))
                    
                    audit_log("Staff", "CREATION", f"Dossier créé pour {f_roblox}")
                    st.success(f"Dossier actif pour {f_roblox}. Date: {today}")
                    st.rerun()

    # --- JUSTICE MODULE ---
    with t5:
        st.subheader("⚖️ Tribunal de Grande Instance")
        with st.form("justice_engine"):
            target_civil = st.selectbox("Citoyen jugé", sorted(df_b["Nom Roblox"].unique().tolist()))
            fine = st.number_input("Amende forfaitaire", min_value=0)
            reason = st.text_area("Motif du jugement")
            
            if st.form_submit_button("APPLIQUER LA SENTENCE"):
                db_justice = load_data("Banque")
                idx_guilty = db_justice[db_justice["Nom Roblox"] == target_civil].index[0]
                db_justice.at[idx_guilty, "Solde"] -= fine
                save_data("Banque", db_justice)
                audit_log("Justice", "SANCTION", f"{target_civil} a reçu une amende de {fine}$")
                st.success("Sentence exécutée.")
                st.rerun()

# ==============================================================================
# 🪪 MODULE PERMIS (VISUEL)
# ==============================================================================
tab_permis = t3 if st.session_state.role == "Staff" else t2
with tab_permis:
    if st.session_state.role != "RCT":
        st.subheader("🪪 Contrôle des Titres de Conduite")
        df_p = load_data("Points Permis")
        p_search = st.text_input("Rechercher un titulaire", key="p_search").lower()
        
        if p_search:
            p_res = df_p[df_p["Nom Roblox"].str.lower().str.contains(p_search)]
            for p_idx, p_row in p_res.iterrows():
                pts = int(p_row['PTS'])
                color = "#2ecc71" if pts >= 15 else ("#f1c40f" if pts >= 6 else "#e74c3c")
                st.markdown(f"""
                <div class="license-box" style="border-left: 15px solid {color}; border-right: 1px solid {color};">
                    <h1 style="color:{color}; margin:0; font-family:Orbitron;">{pts} / 25</h1>
                    <h3 style="margin:0;">{p_row['Nom Roblox']}</h3>
                    <p style="color:{color};"><b>STATUT : {'ACTIF' if pts >= 6 else 'SUSPENDU'}</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.session_state.role == "Staff":
                    new_pts = st.slider(f"Ajuster points - {p_row['Nom Roblox']}", 0, 25, pts)
                    if st.button("Mettre à jour", key=f"p_btn_{p_idx}"):
                        df_p.at[p_idx, 'PTS'] = new_pts
                        save_data("Points Permis", df_p)
                        st.rerun()

# ==============================================================================
# 📊 MODULE STATISTIQUES (FULL)
# ==============================================================================
if st.session_state.role == "Staff":
    with t6:
        st.subheader("📊 État de l'Économie")
        c_s1, c_s2, c_s3 = st.columns(3)
        c_s1.metric("Masse Monétaire", f"{df_bank['Solde'].astype(float).sum():,.0f} $")
        c_s2.metric("Véhicules Enregistrés", len(df_immat))
        c_s3.metric("Population Totale", len(df_bank))
        st.divider()
        st.write("Distribution des Assurances")
        st.bar_chart(df_immat["Assurance"].value_counts())

    with t7:
        st.subheader("📜 Journal d'Audit Système")
        st.dataframe(load_data("Logs").sort_index(ascending=False), use_container_width=True)

# --- FIN DU DOCUMENT ---
st.markdown("---")
st.markdown(f"<center><small>RCRP INTEGRATED SYSTEM v11.2 | RÉPUBLIQUE DE CALIFORNIE | {datetime.now().year}</small></center>", unsafe_allow_html=True)
