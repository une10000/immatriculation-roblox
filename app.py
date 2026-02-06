import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# Configuration de la page
st.set_page_config(page_title="RCRP - Fichier Central", layout="wide")

# --- LOGO ET TITRE ---
st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=697f2cf3&is=697ddb73&hm=dccb2edf0897deb4ccbdee22b3221134415bfed15b2cc808e439232c6f18bcab&", width=200)

st.title("🚓 Fichier Central & 🏦 Banque")
st.write("### RCRPFR - Base de données officielle")

# Connexion aux Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CONFIGURATION ADMIN ---
CODE_ADMIN_GENERAL = "RCRPFR-25-26"

# --- FONCTION DE LOGGING ---
def log_action(action, cible):
    try:
        df_logs = conn.read(worksheet="Logs", ttl=0)
        df_logs.columns = [str(c).strip() for c in df_logs.columns]
    except:
        df_logs = pd.DataFrame(columns=["Horodateur", "Action", "Cible"])
    
    new_log = pd.DataFrame([{
        "Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"),
        "Action": action,
        "Cible": cible
    }])
    conn.update(worksheet="Logs", data=pd.concat([df_logs, new_log], ignore_index=True))

# --- LISTES ---
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])
liste_assurances = ["Non assuré", "RCT", "Averis"]

# --- NAVIGATION ---
tabs = st.tabs(["🚗 Immatriculations", "🪪 Points de Permis", "💰 Banque", "📜 Logs"])

# ==========================================
# ONGLET 1 : IMMATRICULATIONS
# ==========================================
with tabs[0]:
    nom_feuille_immat = "Copie de Immatriculations"
    try:
        df_immat = conn.read(worksheet=nom_feuille_immat, ttl=0)
        df_immat.columns = [str(c).strip() for c in df_immat.columns]
    except: df_immat = pd.DataFrame()

    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("inscription"):
            u_reg = st.text_input("Nom d'utilisateur ROBLOX")
            m_reg = st.selectbox("Marque du véhicule", liste_marques)
            e_reg = st.selectbox("État", liste_etats)
            p_reg = st.text_input("Numéro de la plaque")
            a_reg = st.selectbox("Assurance", liste_assurances)
            c_reg = st.text_input("Code secret (pour toi)", type="password")
            
            if st.form_submit_button("Valider"):
                if u_reg and p_reg and c_reg:
                    heure_locale = (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M")
                    new_row = pd.DataFrame([{"Horodateur": heure_locale, "Nom d'utilisateur ROBLOX": u_reg, "Marque du véhicule": m_reg, "L'état de la plaque": e_reg, "Numéro de la plaque": p_reg, "Assurance": a_reg, "CODE": str(c_reg)}])
                    conn.update(worksheet=nom_feuille_immat, data=pd.concat([df_immat, new_row], ignore_index=True))
                    st.success("✅ Véhicule enregistré !")
                    time.sleep(1); st.rerun()

    st.divider()
    s_query = st.text_input("🔍 Rechercher véhicule").strip().upper()
    if not df_immat.empty:
        mask = df_immat.apply(lambda r: r.astype(str).str.contains(s_query, case=False).any(), axis=1) if s_query else [True]*len(df_immat)
        display_df = df_immat[mask]
        st.dataframe(display_df[[c for c in display_df.columns if c != "CODE"]], use_container_width=True)

# ==========================================
# ONGLET 2 : POINTS DE PERMIS
# ==========================================
with tabs[1]:
    nom_feuille_pts = "Points Permis"
    nom_feuille_banque = "Banque"
    try:
        df_pts = conn.read(worksheet=nom_feuille_pts, ttl=0)
        df_pts.columns = [str(c).strip() for c in df_pts.columns]
        df_bank = conn.read(worksheet=nom_feuille_banque, ttl=0)
        df_bank.columns = [str(c).strip() for c in df_bank.columns]
    except: 
        df_pts = pd.DataFrame()
        df_bank = pd.DataFrame(columns=["Nom Roblox", "Solde"])

    with st.expander("👤 [ADMIN] Ajouter un nouveau conducteur"):
        with st.form("admin_add_driver"):
            new_discord = st.text_input("Nom Discord")
            new_roblox = st.text_input("Nom Roblox")
            new_pts = st.number_input("Points", 0, 25, 25)
            admin_code = st.text_input("Code Admin requis", type="password")
            
            if st.form_submit_button("Créer le dossier"):
                if admin_code == CODE_ADMIN_GENERAL:
                    if new_roblox:
                        # 1. Créer le permis
                        val_label = "VALIDE" if new_pts >= 14 else ("OUI" if new_pts >= 1 else "NON")
                        new_driver = pd.DataFrame([{"Nom Discord": new_discord, "Nom Roblox": new_roblox, "PTS": new_pts, "Validité": val_label}])
                        conn.update(worksheet=nom_feuille_pts, data=pd.concat([df_pts, new_driver], ignore_index=True))
                        
                        # 2. Créer la banque auto
                        if not (new_roblox.lower() in df_bank["Nom Roblox"].str.lower().values):
                            new_bank = pd.DataFrame([{"Nom Roblox": new_roblox, "Solde": 15000.0}])
                            conn.update(worksheet=nom_feuille_banque, data=pd.concat([df_bank, new_bank], ignore_index=True))
                        
                        log_action("Création Dossier + Banque Auto", new_roblox)
                        st.success("✅ Dossier créé !")
                        time.sleep(1); st.rerun()
                else: st.error("❌ Code Admin incorrect")

    st.divider()
    search_p = st.text_input("🔍 Rechercher Conducteur (Pseudo)").strip()
    if not df_pts.empty and search_p:
        res = df_pts[df_pts["Nom Roblox"].astype(str).str.contains(search_p, case=False, na=False)]
        for idx, row in res.iterrows():
            st.markdown(f"### 👤 {row.get('Nom Roblox')}")
            p_act = int(row.get("PTS", 0))
            
            col_m, col_d = st.columns(2)
            with col_m:
                with st.expander("⚙️ Modifier Points"):
                    with st.form(key=f"mod_pts_{idx}"):
                        ac = st.text_input("Code Admin", type="password")
                        n_p = st.number_input("Nouveau total", 0, 25, p_act)
                        if st.form_submit_button("Sauvegarder"):
                            if ac == CODE_ADMIN_GENERAL:
                                df_pts.at[idx, "PTS"] = n_p
                                df_pts.at[idx, "Validité"] = "VALIDE" if n_p >= 14 else ("OUI" if n_p >= 1 else "NON")
                                conn.update(worksheet=nom_feuille_pts, data=df_pts)
                                log_action(f"Modif Points -> {n_p}", row.get('Nom Roblox'))
                                st.rerun()
                            else: st.error("Code incorrect")
            with col_d:
                if st.button("🗑️ Supprimer", key=f"pre_del_{idx}"):
                    st.session_state[f"del_{idx}"] = True
                if st.session_state.get(f"del_{idx}", False):
                    dc = st.text_input("Code Admin de confirmation", type="password", key=f"conf_{idx}")
                    if st.button("🔥 CONFIRMER", key=f"real_del_{idx}"):
                        if dc == CODE_ADMIN_GENERAL:
                            log_action("Suppression Profil", row.get('Nom Roblox'))
                            conn.update(worksheet=nom_feuille_pts, data=df_pts.drop(idx))
                            st.session_state[f"del_{idx}"] = False
                            st.rerun()
                        else: st.error("Code incorrect")

# ==========================================
# ONGLET 3 : BANQUE
# ==========================================
with tabs[2]:
    st.subheader("💰 Banque Centrale")
    try:
        df_bank = conn.read(worksheet="Banque", ttl=0)
        df_bank.columns = [str(c).strip() for c in df_bank.columns]
    except: df_bank = pd.DataFrame()

    st.info("💡 Les comptes sont créés automatiquement via l'onglet Permis.")
    
    sb = st.text_input("🔍 Rechercher un compte").strip()
    if not df_bank.empty and sb:
        res_b = df_bank[df_bank["Nom Roblox"].astype(str).str.contains(sb, case=False, na=False)]
        for idx, row in res_b.iterrows():
            solde = float(row.get("Solde", 0))
            st.metric(row.get('Nom Roblox'), f"{solde:,.0f} $")
            with st.expander("🛡️ Transaction Admin"):
                with st.form(key=f"b_tr_{idx}"):
                    abc = st.text_input("Code Admin", type="password")
                    mnt = st.number_input("Montant", step=100.0)
                    b_ret, b_add = st.columns(2)
                    if b_ret.form_submit_button("📉 Retirer") and abc == CODE_ADMIN_GENERAL:
                        df_bank.at[idx, "Solde"] = solde - mnt
                        conn.update(worksheet="Banque", data=df_bank)
                        log_action(f"Retrait Banque (-{mnt})", row.get('Nom Roblox'))
                        st.rerun()
                    if b_add.form_submit_button("📈 Ajouter") and abc == CODE_ADMIN_GENERAL:
                        df_bank.at[idx, "Solde"] = solde + mnt
                        conn.update(worksheet="Banque", data=df_bank)
                        log_action(f"Ajout Banque (+{mnt})", row.get('Nom Roblox'))
                        st.rerun()

# ==========================================
# ONGLET 4 : LOGS
# ==========================================
with tabs[3]:
    st.subheader("📜 Historique des actions")
    try:
        df_l = conn.read(worksheet="Logs", ttl=0)
        st.dataframe(df_l.sort_index(ascending=False), use_container_width=True)
    except: st.warning("Feuille 'Logs' introuvable dans le GSheet.")

st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 12px;'>Version v4.5 - Full Security</div>", unsafe_allow_html=True)
