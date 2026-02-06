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

# Connexion aux Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26"

# --- FONCTION DE LOGGING ---
def log_action(admin_name, action, cible):
    try:
        df_logs = conn.read(worksheet="Logs", ttl=0)
        new_log = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Admin": str(admin_name), "Action": str(action), "Cible": str(cible)}])
        conn.update(worksheet="Logs", data=pd.concat([df_logs, new_log], ignore_index=True))
    except: pass

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
    try: df_immat = conn.read(worksheet=nom_feuille_immat, ttl=0)
    except: df_immat = pd.DataFrame()
    
    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("inscription"):
            u_reg = st.text_input("Nom d'utilisateur ROBLOX")
            m_reg = st.selectbox("Marque", liste_marques); e_reg = st.selectbox("État", liste_etats)
            p_reg = st.text_input("Plaque"); a_reg = st.selectbox("Assurance", liste_assurances)
            c_reg = st.text_input("Code secret", type="password")
            if st.form_submit_button("Valider"):
                if u_reg and p_reg and c_reg:
                    new_row = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u_reg, "Marque du véhicule": m_reg, "L'état de la plaque": e_reg, "Numéro de la plaque": p_reg, "Assurance": a_reg, "CODE": str(c_reg)}])
                    conn.update(worksheet=nom_feuille_immat, data=pd.concat([df_immat, new_row], ignore_index=True))
                    log_action(u_reg, "Immatriculation", p_reg)
                    st.success("✅ Enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    s_query = st.text_input("🔍 Rechercher une plaque ou un citoyen").strip().upper()
    if not df_immat.empty:
        mask = df_immat.apply(lambda r: r.astype(str).str.contains(s_query, case=False).any(), axis=1) if s_query else [True]*len(df_immat)
        for idx, row in df_immat[mask].iterrows():
            with st.container(border=True):
                c_inf, c_act = st.columns([3, 2])
                c_inf.markdown(f"**{row['Numéro de la plaque']}** | {row['Marque du véhicule']} | {row['Nom d\'utilisateur ROBLOX']}")
                if c_act.button("✏️ Modifier", key=f"e_{idx}", use_container_width=True): st.session_state[f"me_{idx}"] = True
                if c_act.button("🗑️ Supprimer", key=f"d_{idx}", use_container_width=True): st.session_state[f"md_{idx}"] = True
                # ... (Logique modif/suppr identique à v5.7)

# ==========================================
# ONGLET 2 : POINTS DE PERMIS
# ==========================================
with tabs[1]:
    try: df_pts = conn.read(worksheet="Points Permis", ttl=0)
    except: df_pts = pd.DataFrame()
    with st.expander("👤 [ADMIN] Nouveau conducteur"):
        st.info("💡 **INFO :** Le compte bancaire est créé AUTO avec 15'000$.")
        with st.form("add_p"):
            adm = st.text_input("Nom Admin"); rob = st.text_input("Nom Roblox"); disc = st.text_input("Nom Discord")
            pts = st.number_input("Points", 0, 25, 25); code = st.text_input("Code Admin", type="password")
            if st.form_submit_button("Créer"):
                if code == CODE_ADMIN_GENERAL and rob:
                    val = "VALIDE" if pts >= 14 else ("OUI" if pts >= 1 else "NON")
                    new_p = pd.DataFrame([{"Nom Discord": disc, "Nom Roblox": rob, "PTS": pts, "Validité": val}])
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_p], ignore_index=True))
                    # Correction Bug Banque : On écrit bien dans Nom Roblox
                    try:
                        df_b = conn.read(worksheet="Banque", ttl=0)
                        new_entry = pd.DataFrame([{"Solde": 15000, "Nom Discord": disc, "Nom Roblox": rob, "Pseudo Admin": adm}])
                        conn.update(worksheet="Banque", data=pd.concat([df_b, new_entry], ignore_index=True))
                    except: pass
                    log_action(adm, "Nouveau Dossier", rob); st.success("Fait !"); time.sleep(1); st.rerun()

# ==========================================
# ONGLET 3 : BANQUE (CORRIGÉ POUR TON TABLEAU)
# ==========================================
with tabs[2]:
    st.subheader("💰 Banque Centrale")
    try: 
        df_bank = conn.read(worksheet="Banque", ttl=0)
        df_pts_ref = conn.read(worksheet="Points Permis", ttl=0)
    except: df_bank = pd.DataFrame(); df_pts_ref = pd.DataFrame()
    
    sb = st.text_input("🔍 Rechercher compte bancaire (Roblox ou Discord)").strip()
    if not df_bank.empty and sb:
        # Recherche intelligente : regarde dans Nom Roblox OU Nom Discord
        mask = (df_bank["Nom Roblox"].astype(str).str.contains(sb, case=False, na=False)) | \
               (df_bank["Nom Discord"].astype(str).str.contains(sb, case=False, na=False))
        res_b = df_bank[mask]
        
        for idx, row in res_b.iterrows():
            solde = float(row.get('Solde', 0))
            name_r = row.get('Nom Roblox', 'Inconnu')
            name_d = row.get('Nom Discord', 'Non lié')
            
            st.metric(f"👤 {name_r} (Discord: {name_d})", f"{solde:,.0f} $")
            with st.expander("🛡️ Gérer le solde"):
                with st.form(key=f"bt_{idx}"):
                    ad_b = st.text_input("Admin"); c_b = st.text_input("Code", type="password")
                    mnt = st.number_input("Montant", step=500.0)
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("📉 Retirer") and c_b == CODE_ADMIN_GENERAL:
                        df_bank.at[idx, "Solde"] = solde - mnt
                        conn.update(worksheet="Banque", data=df_bank)
                        log_action(ad_b, f"Retrait -{mnt}", name_r); st.rerun()
                    if col2.form_submit_button("📈 Ajouter") and c_b == CODE_ADMIN_GENERAL:
                        df_bank.at[idx, "Solde"] = solde + mnt
                        conn.update(worksheet="Banque", data=df_bank)
                        log_action(ad_b, f"Ajout +{mnt}", name_r); st.rerun()

# ==========================================
# ONGLET 4 : LOGS
# ==========================================
with tabs[3]:
    pwd = st.text_input("Code Admin Logs", type="password")
    if pwd == CODE_ADMIN_GENERAL:
        try: st.dataframe(conn.read(worksheet="Logs", ttl=0).iloc[::-1], use_container_width=True)
        except: st.write("Vide")
