import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="RCRP - Fichier Central", layout="wide")

# --- LOGO ET TITRE ---
st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=697f2cf3&is=697ddb73&hm=dccb2edf0897deb4ccbdee22b3221134415bfed15b2cc808e439232c6f18bcab&", width=200)
st.title("🚓 Fichier Central & 🏦 Banque")

# --- CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26"

# --- FONCTION LOGS ---
def log_action(admin_name, action, cible):
    try:
        df_logs = conn.read(worksheet="Logs", ttl=0)
        new_log = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Admin": str(admin_name), "Action": str(action), "Cible": str(cible)}])
        conn.update(worksheet="Logs", data=pd.concat([df_logs, new_log], ignore_index=True))
    except: pass

# --- LISTES ---
liste_assurances = ["Non assuré", "RCT", "Averis"]

# --- NAVIGATION ---
tabs = st.tabs(["🚗 Immatriculations", "🪪 Points de Permis", "💰 Banque", "📜 Logs"])

# ==========================================
# 🚗 ONGLET 1 : IMMATRICULATIONS
# ==========================================
with tabs[0]:
    nom_feuille_immat = "Copie de Immatriculations"
    try:
        df_immat = conn.read(worksheet=nom_feuille_immat, ttl=0)
        df_immat = df_immat.fillna("")
    except: df_immat = pd.DataFrame()
    
    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("inscription_v7"):
            u_reg = st.text_input("Nom d'utilisateur ROBLOX")
            p_reg = st.text_input("Numéro de la plaque")
            a_reg = st.selectbox("Assurance", liste_assurances)
            c_reg = st.text_input("Code secret (pour modifier/supprimer)", type="password")
            if st.form_submit_button("Valider l'enregistrement"):
                if u_reg and p_reg and c_reg:
                    new_row = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u_reg, "Numéro de la plaque": p_reg, "Assurance": a_reg, "CODE": str(c_reg)}])
                    conn.update(worksheet=nom_feuille_immat, data=pd.concat([df_immat, new_row], ignore_index=True))
                    log_action(u_reg, "Immatriculation", p_reg)
                    st.success("✅ Véhicule enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    sq = st.text_input("🔍 Rechercher une plaque ou un citoyen").strip().upper()
    if not df_immat.empty:
        mask = df_immat.apply(lambda r: r.astype(str).str.contains(sq, case=False).any(), axis=1) if sq else [True]*len(df_immat)
        for idx, row in df_immat[mask].iterrows():
            with st.container(border=True):
                col_i, col_a = st.columns([3, 2])
                col_i.markdown(f"### 🚗 {row['Numéro de la plaque']}")
                col_i.write(f"👤 Propriétaire : {row['Nom d\'utilisateur ROBLOX']} | 🛡️ {row['Assurance']}")
                
                if col_a.button(f"✏️ Modifier", key=f"edit_im_{idx}", use_container_width=True): st.session_state[f"ei_{idx}"] = True
                if col_a.button(f"🗑️ Supprimer", key=f"del_im_{idx}", use_container_width=True): st.session_state[f"di_{idx}"] = True

                if st.session_state.get(f"ei_{idx}"):
                    with st.form(f"f_ei_{idx}"):
                        np = st.text_input("Nouvelle Plaque", value=row['Numéro de la plaque'])
                        na = st.selectbox("Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']))
                        cod = st.text_input("Code secret", type="password")
                        if st.form_submit_button("Sauvegarder"):
                            if cod == str(row['CODE']):
                                df_immat.at[idx, 'Numéro de la plaque'] = np
                                df_immat.at[idx, 'Assurance'] = na
                                conn.update(worksheet=nom_feuille_immat, data=df_immat)
                                st.success("OK !"); time.sleep(0.5); st.rerun()
                            else: st.error("Code faux")
                        if st.form_submit_button("Annuler"): st.session_state[f"ei_{idx}"] = False; st.rerun()

                if st.session_state.get(f"di_{idx}"):
                    with st.form(f"f_di_{idx}"):
                        st.error("Supprimer ?")
                        cod_d = st.text_input("Code secret", type="password")
                        if st.form_submit_button("OUI, SUPPRIMER"):
                            if cod_d == str(row['CODE']):
                                conn.update(worksheet=nom_feuille_immat, data=df_immat.drop(idx))
                                st.success("Supprimé"); time.sleep(0.5); st.rerun()
                            else: st.error("Code faux")

# ==========================================
# 🪪 ONGLET 2 : POINTS DE PERMIS
# ==========================================
with tabs[1]:
    try: 
        df_pts = conn.read(worksheet="Points Permis", ttl=0)
        df_pts = df_pts.fillna("")
    except: df_pts = pd.DataFrame()

    with st.expander("👤 [ADMIN] Créer un dossier conducteur"):
        st.info("💡 **AUTO :** Un compte bancaire avec 15'000$ sera créé en même temps.")
        with st.form("add_permis_v7"):
            a_n = st.text_input("Nom Admin"); r_n = st.text_input("Nom Roblox"); d_n = st.text_input("Nom Discord")
            p_v = st.number_input("Points", 0, 25, 25); c_a = st.text_input("Code Admin", type="password")
            if st.form_submit_button("Créer le dossier"):
                if c_a == CODE_ADMIN_GENERAL and r_n:
                    valid = "VALIDE" if p_v >= 14 else ("OUI" if p_v >= 1 else "NON")
                    new_p = pd.DataFrame([{"Nom Discord": d_n, "Nom Roblox": r_n, "PTS": p_v, "Validité": valid}])
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_p], ignore_index=True))
                    try:
                        df_b = conn.read(worksheet="Banque", ttl=0)
                        new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": d_n, "Nom Roblox": r_n, "Pseudo Admin": a_n}])
                        conn.update(worksheet="Banque", data=pd.concat([df_b, new_b], ignore_index=True))
                    except: pass
                    log_action(a_n, "Nouveau Dossier", r_n); st.success("Dossier créé !"); time.sleep(1); st.rerun()

    st.divider()
    search_p = st.text_input("🔍 Rechercher un conducteur (Roblox ou Discord)").strip().lower()
    if not df_pts.empty and search_p:
        res_p = df_pts[(df_pts["Nom Roblox"].str.lower().str.contains(search_user)) | (df_pts["Nom Discord"].str.lower().str.contains(search_user))] if 'search_user' in locals() else df_pts[df_pts.apply(lambda r: search_p in str(r).lower(), axis=1)]
        for idx, row in res_p.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"### 👤 {row['Nom Roblox']} (@{row['Nom Discord']})")
                c1.write(f"État : **{row['Validité']}**")
                c2.metric("Points", f"{int(row['PTS'])}/25")
                with st.expander("⚙️ Modifier / Supprimer"):
                    with st.form(key=f"edit_p_{idx}"):
                        ad = st.text_input("Admin"); cd = st.text_input("Code Admin", type="password")
                        nv_pts = st.number_input("Points", 0, 25, int(row['PTS']))
                        if st.form_submit_button("✅ Sauvegarder"):
                            if cd == CODE_ADMIN_GENERAL:
                                df_pts.at[idx, "PTS"] = nv_pts
                                df_pts.at[idx, "Validité"] = "VALIDE" if nv_pts >= 14 else ("OUI" if nv_pts >= 1 else "NON")
                                conn.update(worksheet="Points Permis", data=df_pts)
                                log_action(ad, f"Points -> {nv_pts}", row['Nom Roblox']); st.rerun()
                        if st.form_submit_button("🗑️ Supprimer"):
                            if cd == CODE_ADMIN_GENERAL:
                                conn.update(worksheet="Points Permis", data=df_pts.drop(idx))
                                st.rerun()

# ==========================================
# 💰 ONGLET 3 : BANQUE
# ==========================================
with tabs[2]:
    st.subheader("💰 Banque Centrale")
    try: 
        df_bank = conn.read(worksheet="Banque", ttl=0).fillna("")
    except: df_bank = pd.DataFrame()
    
    sb = st.text_input("🔍 Rechercher un compte (Nom ou Discord)").strip().lower()
    if not df_bank.empty and sb:
        res_b = df_bank[df_bank.apply(lambda r: sb in str(r).lower(), axis=1)]
        for idx, row in res_b.iterrows():
            s_val = float(row.get('Solde', 0))
            st.metric(f"👤 {row['Nom Roblox']}", f"{s_val:,.0f} $")
            with st.expander("🛡️ Transaction"):
                with st.form(f"tr_{idx}"):
                    a_b = st.text_input("Admin"); c_b = st.text_input("Code", type="password")
                    mnt = st.number_input("Montant", step=500.0)
                    if st.form_submit_button("📉 Retirer") and c_b == CODE_ADMIN_GENERAL:
                        df_bank.at[idx, "Solde"] = s_val - mnt
                        conn.update(worksheet="Banque", data=df_bank)
                        log_action(a_b, f"Retrait {mnt}", row['Nom Roblox']); st.rerun()
                    if st.form_submit_button("📈 Ajouter") and c_b == CODE_ADMIN_GENERAL:
                        df_bank.at[idx, "Solde"] = s_val + mnt
                        conn.update(worksheet="Banque", data=df_bank)
                        log_action(a_b, f"Ajout {mnt}", row['Nom Roblox']); st.rerun()

# ==========================================
# 📜 ONGLET 4 : LOGS
# ==========================================
with tabs[3]:
    pwd = st.text_input("Code Logs", type="password")
    if pwd == CODE_ADMIN_GENERAL:
        try: st.dataframe(conn.read(worksheet="Logs", ttl=0).iloc[::-1], use_container_width=True)
        except: st.write("Vide")

st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 12px;'>Version v7.0 Finale - Tout Inclus</div>", unsafe_allow_html=True)
