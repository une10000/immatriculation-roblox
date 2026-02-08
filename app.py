# ==============================================================================
# 🏛️ REPUBLIQUE DE CALIFORNIE RP - SYSTEME DE GESTION INTEGRAL (v9.98)
# ==============================================================================
# Plateforme de gestion centralisée : Économie, Transports, Justice et Logistique.
# Version : 9.98 | Date : 08/02/2026 | Développeur : RCRP Tech Division
# 
# PROTOCOLES DE TRANSFERT ET RÈGLES MÉTIER :
# 1. Flux Financiers :
#    - Paiements Assurance RCT : Transfert direct vers l'IBAN 'une10000'.
#    - Paiements Assurance Averis : Transfert direct vers l'IBAN 'Moune2010'.
# 2. Gestion des Profils :
#    - L'horodatage de création est injecté automatiquement.
#    - Le pseudo du Staff créateur est sauvegardé dans le registre.
# 3. Sécurité :
#    - Accès restreints par codes alphanumériques.
# ==============================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION DE L'INTERFACE GOUVERNEMENTALE ---
st.set_page_config(
    page_title="RCRP - Système Intégré de l'État",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ENGINE CSS : DESIGN HAUTE DÉFINITION ---
# Ce bloc définit l'identité visuelle et l'expérience utilisateur du portail.
st.markdown("""
    <style>
    /* Configuration globale du thème sombre */
    .main { background-color: #0b0d10; color: #ecf0f1; }
    
    /* Conteneurs de connexion - Format 600px de hauteur garanti */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(30, 34, 40, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 40px !important;
        height: 600px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0px 20px 50px rgba(0,0,0,0.7);
    }

    /* Ticket financier - Design "Papier" pour le RP */
    .transaction-ticket {
        background: linear-gradient(135deg, #1e272e 0%, #050505 100%);
        border: 1px solid #27ae60;
        border-left: 12px solid #27ae60;
        padding: 25px;
        border-radius: 12px;
        margin: 20px 0;
        color: #ffffff;
        font-family: 'Consolas', 'Courier New', monospace;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.3);
    }

    /* Métriques bancaires stylisées */
    .stMetric {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 22px !important;
        transition: 0.3s;
    }
    .stMetric:hover { background: rgba(255, 255, 255, 0.05) !important; }

    /* Logo Sidebar et bordures dynamiques */
    [data-testid="stSidebar"] img {
        border-radius: 25px;
        border: 3px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 25px;
        filter: drop-shadow(0px 10px 10px rgba(0,0,0,0.5));
    }

    /* Onglets de navigation interactifs */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px 10px 0 0;
        padding: 15px 30px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #c0392b !important;
        color: white !important;
        box-shadow: 0px 5px 15px rgba(192, 57, 43, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONSTANTES ET PARAMÈTRES DE SÉCURITÉ ---
AUTH_ADMIN_KEY = "RCRPFR-25-26" 
AUTH_PRO_KEY = "RCT-26-RCRPFR" 
TARGET_RCT = "une10000" 
TARGET_AVERIS = "Moune2010"
ASSET_LOGO = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless"

# --- GESTION DE LA PERSISTANCE DE SESSION ---
if "role" not in st.session_state:
    st.session_state.role = None
if "update_time" not in st.session_state:
    st.session_state.update_time = time.time()

# --- MOTEUR D'INTERFAÇAGE GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_table(name):
    """Charge une table spécifique depuis le cloud avec forçage de mise à jour."""
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=name, ttl=0)
        return data.dropna(how='all').fillna("")
    except Exception as e:
        st.error(f"🚨 Déconnexion Base de Données : {e}")
        return pd.DataFrame()

def commit_log(agent, category, info):
    """Archive les actions administratives dans le journal d'audit national."""
    try:
        logs = load_table("Logs")
        entry = pd.DataFrame([{
            "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Opérateur": agent,
            "Catégorie": category,
            "Description": info
        }])
        conn.update(worksheet="Logs", data=pd.concat([logs, entry], ignore_index=True))
    except:
        pass

# ==============================================================================
# 🚪 SECTION 1 : PORTAIL D'ACCÈS SÉCURISÉ (LOBBY)
# ==============================================================================
if st.session_state.role is None:
    st.title("🏛️ État de Californie - Portail Central")
    st.write("Bienvenue sur l'infrastructure numérique de gestion de la République.")
    st.divider()
    
    col_c, col_p, col_s = st.columns(3)
    
    with col_c:
        with st.container(border=True):
            st.markdown("### 👤 Citoyen")
            st.info("Consultez vos comptes, véhicules et points de permis en libre accès.")
            if st.button("Session Civile", use_container_width=True):
                st.session_state.role = "Civil"
                commit_log("Anonyme", "AUTH", "Accès Citoyen")
                st.rerun()

    with col_p:
        with st.container(border=True):
            st.markdown("### 🛠️ Professionnel")
            st.write("Espace réservé RCT & Averis. Gestion des contrats d'assurance et immatriculations.")
            key_p = st.text_input("Code Entreprise", type="password", key="l_p")
            if st.button("Accès Pro", use_container_width=True):
                if key_p == AUTH_PRO_KEY:
                    st.session_state.role = "RCT"
                    commit_log("RCT", "AUTH", "Accès Entreprise")
                    st.rerun()
                else: st.error("Accès Entreprise Invalide.")

    with col_s:
        with st.container(border=True):
            st.markdown("### 👮 Administration")
            st.write("Panel Haute-Sécurité réservé au Staff. Contrôle total des bases de données.")
            key_s = st.text_input("Code Sécurité Staff", type="password", key="l_s")
            if st.button("Accès Staff", use_container_width=True):
                if key_s == AUTH_ADMIN_KEY:
                    st.session_state.role = "Staff"
                    commit_log("Staff", "AUTH", "Accès Administrateur")
                    st.rerun()
                else: st.error("Code erroné. Tentative d'intrusion enregistrée.")
    st.stop()

# ==============================================================================
# 🖥️ SECTION 2 : DASHBOARD ET NAVIGATION SIDEBAR
# ==============================================================================
with st.sidebar:
    st.image(ASSET_LOGO, use_container_width=True)
    st.markdown(f"🛂 **Statut actuel :** {st.session_state.role}")
    if st.button("🚪 Terminer la Session", use_container_width=True):
        commit_log(st.session_state.role, "AUTH", "Déconnexion manuelle")
        st.session_state.role = None
        st.rerun()
    st.divider()
    st.write(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"⏰ **Heure :** {datetime.now().strftime('%H:%M')}")
    if st.button("🔄 Actualiser les Flux"):
        st.rerun()

# ARCHITECTURE DES ONGLETS SELON LES DROITS D'ACCÈS
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immat", "💰 Banque", "🪪 Permis", "➕ Profils", "⚖️ Justice", "📊 Stats", "📜 Logs"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation Pro", "📜 Historique"])
else:
    tabs = st.tabs(["🚗 Mes Véhicules", "💰 Mon Portefeuille", "🪪 Mon Permis"])

# ==============================================================================
# 🚗 MODULE 3 : GESTION DES IMMATRICULATIONS (LOGIQUE RCT/AVERIS)
# ==============================================================================
with tabs[0]:
    df_immat = load_table("Copie de Immatriculations")
    df_bank = load_table("Banque")
    owners = sorted(df_bank["Nom Roblox"].unique().tolist()) if not df_bank.empty else []

    with st.expander("➕ Enregistrer un Nouveau Véhicule"):
        with st.form("form_add_v"):
            c1, c2 = st.columns(2)
            u = c1.selectbox("👤 Citoyen concerné", ["---"] + owners)
            m = c1.selectbox("🚘 Marque", sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"]))
            p = c2.text_input("🔢 Numéro de Plaque")
            a = c1.selectbox("🛡️ Contrat d'Assurance", ["Non assuré", "RCT", "Averis"])
            pw = c2.text_input("🔑 Code Secret de Sécurité", type="password")
            
            # --- CALCUL DES TAXES ET REDIRECTIONS FINANCIÈRES ---
            f_v, f_r, f_a, f_j = 175, 0, 0, 0
            if u != "---":
                udat = df_bank[df_bank["Nom Roblox"] == u]
                if not udat.empty:
                    if a == "Averis":
                        f_a = 130
                        try:
                            da = datetime.strptime(str(udat.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                            if datetime.now() - da < timedelta(days=30): f_j = 50
                        except: pass
                    elif a == "RCT":
                        count = df_immat[(df_immat["Nom d'utilisateur ROBLOX"] == u) & (df_immat["Assurance"] == "RCT")].shape[0]
                        if count < 2: f_r = 150

            total = f_v + f_r + f_a + f_j
            st.markdown(f"""
            <div class='transaction-ticket'>
                <b>FACTURE OFFICIELLE DE L'ÉTAT</b><br>
                ---<br>
                Frais de Dossier Ville : {f_v}$<br>
                {f'Frais Assurance RCT : {f_r}$<br>' if f_r > 0 else ''}
                {f'Frais Assurance Averis : {f_a}$<br>' if f_a > 0 else ''}
                {f'Taxe Jeune Citoyen : {f_j}$<br>' if f_j > 0 else ''}
                <hr style='border: 0.1px dashed #27ae60'>
                <b>TOTAL À DÉBITER : {total}$</b>
            </div>
            """, unsafe_allow_html=True)
            
            if st.form_submit_button("💳 Valider le Paiement"):
                if u != "---" and p and pw:
                    ur = df_bank[df_bank["Nom Roblox"] == u]
                    if float(ur.iloc[0]["Solde"]) >= total:
                        # 1. Débit Compte Citoyen
                        df_bank.at[ur.index[0], "Solde"] = float(ur.iloc[0]["Solde"]) - total
                        # 2. Transfert Entreprise RCT
                        if f_r > 0:
                            tr = df_bank[df_bank["Nom Roblox"] == TARGET_RCT]
                            if not tr.empty: df_bank.at[tr.index[0], "Solde"] = float(tr.iloc[0]["Solde"]) + f_r
                        # 3. Transfert Entreprise Averis
                        if f_a > 0:
                            ta = df_bank[df_bank["Nom Roblox"] == TARGET_AVERIS]
                            if not ta.empty: df_bank.at[ta.index[0], "Solde"] = float(ta.iloc[0]["Solde"]) + f_a
                        
                        # 4. Enregistrement du Véhicule
                        nv = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Nom d'utilisateur ROBLOX": u,
                            "Marque du véhicule": m,
                            "L'état de la plaque": "California",
                            "Numéro de la plaque": p,
                            "Assurance": a,
                            "CODE": str(pw)
                        }])
                        conn.update(worksheet="Banque", data=df_bank)
                        conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_immat, nv], ignore_index=True))
                        commit_log(st.session_state.role, "VEHICULE", f"Immat {p} pour {u}")
                        st.success("✅ Transaction effectuée !"); time.sleep(1); st.rerun()
                    else: st.error("❌ Solde insuffisant.")

    st.divider()
    q = st.text_input("🔍 Recherche par Plaque, Marque ou Citoyen").lower()
    if not df_immat.empty:
        res = df_immat[df_immat.apply(lambda r: q in str(r).lower(), axis=1)]
        for i, r in res.iterrows():
            with st.container(border=True):
                st.write(f"🚗 **Plaque : {r['Numéro de la plaque']}** ({r['Marque du véhicule']})")
                st.write(f"👤 Propriétaire : {r['Nom d\'utilisateur ROBLOX']} | 🛡️ {r['Assurance']}")
                if st.button("🛠️ Options", key=f"opt_{i}"):
                    st.session_state[f"ed_{i}"] = not st.session_state.get(f"ed_{i}", False)
                if st.session_state.get(f"ed_{i}"):
                    chk = st.text_input("Code de Sécurité", type="password", key=f"c_{i}")
                    if st.session_state.role == "Staff" or chk == str(r['CODE']):
                        with st.form(f"f_mod_{i}"):
                            na = st.selectbox("Type d'Assurance", ["Non assuré", "RCT", "Averis"])
                            if st.form_submit_button("Appliquer"):
                                df_immat.at[i, 'Assurance'] = na
                                conn.update(worksheet="Copie de Immatriculations", data=df_immat); st.rerun()
                        if st.button("🗑️ Supprimer le registre", key=f"del_{i}"):
                            conn.update(worksheet="Copie de Immatriculations", data=df_immat.drop(i)); st.rerun()

# ==============================================================================
# 💰 MODULE 4 : BANQUE ET GESTION MONÉTAIRE
# ==============================================================================
with tabs[1 if st.session_state.role != "Staff" else 1]:
    df_bk = load_table("Banque")
    if st.session_state.role == "Civil":
        my_n = st.text_input("🔍 Votre Nom Roblox").strip().lower()
        if my_n:
            me = df_bk[df_bk["Nom Roblox"].str.lower() == my_n]
            if not me.empty: st.metric("💵 Mon Solde", f"{float(me.iloc[0]['Solde']):,.0f} $")
    else:
        sb = st.text_input("🔍 Rechercher un compte citoyen").lower()
        if sb:
            rb = df_bk[df_bk.apply(lambda r: sb in str(r).lower(), axis=1)]
            for ib, lb in rb.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **{lb['Nom Roblox']}** | 💬 Discord : {lb['Nom Discord']}")
                    st.write(f"📅 Arrivée : {lb['Date d\'arrivée']} | 👮 Staff : {lb['Pseudo Admin']}")
                    val_s = float(lb['Solde'])
                    st.metric("Solde Bancaire", f"{val_s:,.0f} $")
                    with st.form(f"bk_f_{ib}"):
                        m_op = st.number_input("Montant", min_value=0.0, step=100.0)
                        bc1, bc2 = st.columns(2)
                        if bc1.form_submit_button("📉 Débiter"):
                            df_bk.at[ib, 'Solde'] = val_s - m_op
                            conn.update(worksheet="Banque", data=df_bk)
                            commit_log(st.session_state.role, "BANQUE", f"Débit {m_op}$ -> {lb['Nom Roblox']}")
                            st.rerun()
                        if bc2.form_submit_button("📈 Créditer") and st.session_state.role == "Staff":
                            df_bk.at[ib, 'Solde'] = val_s + m_op
                            conn.update(worksheet="Banque", data=df_bk)
                            commit_log(st.session_state.role, "BANQUE", f"Crédit {m_op}$ -> {lb['Nom Roblox']}")
                            st.rerun()

# ==============================================================================
# 🪪 MODULE 5 : ADMINISTRATION (STAFF ONLY)
# ==============================================================================
if st.session_state.role == "Staff":
    with tabs[2]: # Permis
        df_p = load_table("Points Permis")
        sp = st.text_input("🔍 Rechercher un dossier permis").lower()
        if sp:
            rp = df_p[df_p.apply(lambda r: sp in str(r).lower(), axis=1)]
            for ip, lp in rp.iterrows():
                with st.form(f"p_f_{ip}"):
                    st.write(f"👤 Titulaire : {lp['Nom Roblox']}")
                    nv = st.number_input("Points", 0, 25, value=int(lp['PTS']))
                    if st.form_submit_button("Sauver"):
                        df_p.at[ip, 'PTS'] = nv
                        conn.update(worksheet="Points Permis", data=df_p)
                        commit_log("Staff", "PERMIS", f"{nv} pts pour {lp['Nom Roblox']}")
                        st.rerun()

    with tabs[3]: # Création de Profils
        st.write("### ➕ Créer un Dossier National Complet")
        with st.form("fc_full"):
            n_r = st.text_input("Nom d'utilisateur Roblox")
            n_d = st.text_input("Identifiant Discord")
            p_adm = st.text_input("Pseudo du Staff Créateur")
            dot = st.number_input("Solde de Bienvenue ($)", value=15000.0)
            if st.form_submit_button("🚀 Finaliser l'Enregistrement"):
                db_b, db_p = load_table("Banque"), load_table("Points Permis")
                # AUTOMATISATION DES PARAMÈTRES FIXES
                nb = pd.DataFrame([{
                    "Solde": dot, 
                    "Nom Discord": n_d, 
                    "Nom Roblox": n_r, 
                    "Pseudo Admin": p_adm, 
                    "Date d'arrivée": datetime.now().strftime("%d/%m/%Y")
                }])
                np = pd.DataFrame([{"Nom Roblox": n_r, "PTS": 25}])
                conn.update(worksheet="Banque", data=pd.concat([db_b, nb], ignore_index=True))
                conn.update(worksheet="Points Permis", data=pd.concat([db_p, np], ignore_index=True))
                commit_log("Staff", "PROFIL", f"Citoyen {n_r} créé")
                st.success(f"Dossier de {n_r} initialisé avec succès !"); time.sleep(1); st.rerun()

    with tabs[4]: # Justice
        st.write("### ⚖️ Tribunal et Sanctions")
        with st.form("f_justice"):
            target = st.selectbox("Coupable", owners)
            amt_j = st.number_input("Montant de l'Amende", min_value=0)
            motif = st.text_area("Motif Judiciaire")
            if st.form_submit_button("⚖️ Appliquer"):
                db_j = load_table("Banque")
                idx = db_j[db_j["Nom Roblox"] == target]
                if not idx.empty:
                    db_j.at[idx.index[0], "Solde"] = float(idx.iloc[0]["Solde"]) - amt_j
                    conn.update(worksheet="Banque", data=db_j)
                    commit_log("Staff", "JUSTICE", f"Amende {amt_j}$ pour {target} ({motif})")
                    st.success("Sanction financière appliquée."); st.rerun()

    with tabs[5]: # Statistiques
        st.write("### 📊 Données Macro-Économiques")
        c1, c2, c3 = st.columns(3)
        c1.metric("Masse Monétaire", f"{df_bank['Solde'].astype(float).sum():,.0f} $")
        c2.metric("Total Flotte", len(df_immat))
        c3.metric("Population", len(df_bank))

    with tabs[6]: # Logs
        st.write("### 📜 Archives d'Audit")
        st.dataframe(load_table("Logs").iloc[::-1], use_container_width=True)

# --- PIED DE PAGE ---
st.markdown("---")
st.markdown("<center><small>RCRP Enterprise v9.98 | Gouvernement de Californie | © 2026</small></center>", unsafe_allow_html=True)
