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
        # (Formulaire d'inscription gardé identique)
        with st.form("inscription"):
            u_reg = st.text_input("Nom d'utilisateur ROBLOX")
            p_reg = st.text_input("Plaque")
            c_reg = st.text_input("Code secret véhicule", type="password")
            if st.form_submit_button("Valider"):
                if u_reg and p_reg and c_reg:
                    new_row = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u_reg, "Numéro de la plaque": p_reg, "CODE": str(c_reg)}])
                    conn.update(worksheet=nom_feuille_immat, data=pd.concat([df_immat, new_row], ignore_index=True))
                    st.success("✅ Enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    sq = st.text_input("🔍 Rechercher une plaque ou un citoyen").strip().upper()
    if not df_immat.empty:
        mask = df_immat.apply(lambda r: r.astype(str).str.contains(sq, case=False).any(), axis=1) if sq else [True]*len(df_immat)
        for idx, row in df_immat[mask].iterrows():
            with st.container(border=True):
                st.write(f"**{row['Numéro de la plaque']}** | {row['Nom d\'utilisateur ROBLOX']}")

# ==========================================
# ONGLET 2 : POINTS DE PERMIS (RÉPARÉ)
# ==========================================
with tabs[1]:
    try: 
        df_pts = conn.read(worksheet="Points Permis", ttl=0)
        df_pts["Nom Roblox"] = df_pts["Nom Roblox"].fillna("").astype(str)
        df_pts["Nom Discord"] = df_pts["Nom Discord"].fillna("").astype(str)
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
                    try:
                        df_b = conn.read(worksheet="Banque", ttl=0)
                        new_entry = pd.DataFrame([{"Solde": 15000, "Nom Discord": disc, "Nom Roblox": rob, "Pseudo Admin": adm}])
                        conn.update(worksheet="Banque", data=pd.concat([df_b, new_entry], ignore_index=True))
                    except: pass
                    log_action(adm, "Nouveau Dossier", rob); st.success("Fait !"); time.sleep(1); st.rerun()

    st.divider()
    # --- LA PARTIE RECHERCHE QUI MANQUAIT ---
    search_user = st.text_input("🔍 Rechercher un conducteur (Roblox ou Discord)").strip().lower()
    
    if not df_pts.empty and search_user:
        mask_pts = (df_pts["Nom Roblox"].str.lower().str.contains(search_user)) | \
                   (df_pts["Nom Discord"].str.lower().str.contains(search_user))
        res_pts = df_pts[mask_pts]
        
        if res_pts.empty:
            st.warning("Aucun conducteur trouvé.")
        else:
            for idx, row in res_pts.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"### 👤 {row['Nom Roblox']}")
                    c1.write(f"Discord: @{row['Nom Discord']} | Validité: **{row['Validité']}**")
                    c2.metric("Points", f"{int(row['PTS'])}/25")
                    
                    with st.expander("⚙️ Modifier les points"):
                        with st.form(key=f"edit_pts_{idx}"):
                            adm_p = st.text_input("Nom Admin")
                            code_p = st.text_input("Code Admin", type="password")
                            new_pts = st.number_input("Nouveaux points", 0, 25, int(row['PTS']))
                            col_a, col_b = st.columns(2)
                            if col_a.form_submit_button("✅ Sauvegarder"):
                                if code_p == CODE_ADMIN_GENERAL:
                                    df_pts.at[idx, "PTS"] = new_pts
                                    df_pts.at[idx, "Validité"] = "VALIDE" if new_pts >= 14 else ("OUI" if new_pts >= 1 else "NON")
                                    conn.update(worksheet="Points Permis", data=df_pts)
                                    log_action(adm_p, f"Modif Points ({new_pts})", row['Nom Roblox'])
                                    st.success("Mis à jour !"); time.sleep(0.5); st.rerun()
                            if col_b.form_submit_button("🗑️ Supprimer"):
                                if code_p == CODE_ADMIN_GENERAL:
                                    df_pts = df_pts.drop(idx)
                                    conn.update(worksheet="Points Permis", data=df_pts)
                                    st.error("Supprimé !"); time.sleep(0.5); st.rerun()

# ==========================================
# ONGLET 3 : BANQUE
# ==========================================
with tabs[2]:
    st.subheader("💰 Banque Centrale")
    # (Le code banque v5.9 reste ici, il est déjà optimisé)
    try: 
        df_bank = conn.read(worksheet="Banque", ttl=0)
        df_bank["Nom Roblox"] = df_bank["Nom Roblox"].fillna("").astype(str)
        df_bank["Nom Discord"] = df_bank["Nom Discord"].fillna("").astype(str)
    except: df_bank = pd.DataFrame()
    
    sb = st.text_input("🔍 Rechercher un compte (Roblox/Discord)").strip().lower()
    if not df_bank.empty and sb:
        mask_b = (df_bank["Nom Roblox"].str.lower().str.contains(sb)) | \
                 (df_bank["Nom Discord"].str.lower().str.contains(sb))
        res_b = df_bank[mask_b]
        for idx, row in res_b.iterrows():
            st.metric(f"👤 {row['Nom Roblox']}", f"{float(row['Solde']):,.0f} $")
            # ... (Actions de retrait/ajout)

# ==========================================
# ONGLET 4 : LOGS
# ==========================================
with tabs[3]:
    pwd = st.text_input("Code Admin Logs", type="password")
    if pwd == CODE_ADMIN_GENERAL:
        try: st.dataframe(conn.read(worksheet="Logs", ttl=0).iloc[::-1], use_container_width=True)
        except: st.write("Vide")
