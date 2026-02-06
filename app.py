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
        try:
            df_logs = conn.read(worksheet="Logs", ttl=0)
        except:
            df_logs = pd.DataFrame(columns=["Horodateur", "Admin", "Action", "Cible"])
        new_log = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Admin": str(admin_name), "Action": str(action), "Cible": str(cible)}])
        df_logs.columns = [str(c).strip() for c in df_logs.columns]
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
    try:
        df_immat = conn.read(worksheet=nom_feuille_immat, ttl=0)
    except: df_immat = pd.DataFrame()
    
    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("inscription"):
            u_reg = st.text_input("Nom d'utilisateur ROBLOX")
            m_reg = st.selectbox("Marque du véhicule", liste_marques)
            e_reg = st.selectbox("État", liste_etats)
            p_reg = st.text_input("Numéro de la plaque")
            a_reg = st.selectbox("Assurance", liste_assurances)
            c_reg = st.text_input("Code secret (pour modifier/supprimer)", type="password")
            if st.form_submit_button("Valider l'enregistrement"):
                if u_reg and p_reg and c_reg:
                    h = (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M")
                    new_row = pd.DataFrame([{"Horodateur": h, "Nom d'utilisateur ROBLOX": u_reg, "Marque du véhicule": m_reg, "L'état de la plaque": e_reg, "Numéro de la plaque": p_reg, "Assurance": a_reg, "CODE": str(c_reg)}])
                    conn.update(worksheet=nom_feuille_immat, data=pd.concat([df_immat, new_row], ignore_index=True))
                    log_action(u_reg, "Immatriculation", p_reg)
                    st.success("✅ Véhicule enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    s_query = st.text_input("🔍 Rechercher une plaque ou un citoyen").strip().upper()
    
    if not df_immat.empty:
        mask = df_immat.apply(lambda r: r.astype(str).str.contains(s_query, case=False).any(), axis=1) if s_query else [True]*len(df_immat)
        res_immat = df_immat[mask]
        
        for idx, row in res_immat.iterrows():
            with st.container(border=True):
                col_info, col_actions = st.columns([3, 2])
                with col_info:
                    st.markdown(f"### 🚗 {row['Numéro de la plaque']}")
                    st.markdown(f"**Modèle :** {row['Marque du véhicule']} | **État :** {row['L\'état de la plaque']}")
                    st.markdown(f"👤 **Propriétaire :** {row['Nom d\'utilisateur ROBLOX']} | 🛡️ **Assurance :** `{row['Assurance']}`")
                
                with col_actions:
                    if st.button(f"✏️ Modifier le véhicule", key=f"edit_{idx}", use_container_width=True):
                        st.session_state[f"mode_edit_{idx}"] = True
                    if st.button(f"🗑️ Supprimer le véhicule", key=f"del_{idx}", use_container_width=True):
                        st.session_state[f"mode_del_{idx}"] = True

                if st.session_state.get(f"mode_edit_{idx}"):
                    with st.form(f"f_edit_{idx}"):
                        new_plate = st.text_input("Nouvelle Plaque", value=row['Numéro de la plaque'])
                        new_assur = st.selectbox("Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']))
                        v_code = st.text_input("Code secret véhicule", type="password")
                        c1, c2 = st.columns(2)
                        if c1.form_submit_button("Sauvegarder"):
                            if v_code == str(row['CODE']):
                                df_immat.at[idx, 'Numéro de la plaque'] = new_plate
                                df_immat.at[idx, 'Assurance'] = new_assur
                                conn.update(worksheet=nom_feuille_immat, data=df_immat)
                                log_action(row['Nom d\'utilisateur ROBLOX'], f"Modif Plaque -> {new_plate}", "Véhicule")
                                st.success("C'est fait !"); time.sleep(0.5); st.rerun()
                            else: st.error("Code incorrect")
                        if c2.form_submit_button("Annuler"):
                            st.session_state[f"mode_edit_{idx}"] = False; st.rerun()

                if st.session_state.get(f"mode_del_{idx}"):
                    with st.form(f"f_del_{idx}"):
                        st.error(f"Supprimer {row['Numéro de la plaque']} ?")
                        del_code = st.text_input("Code secret", type="password")
                        d1, d2 = st.columns(2)
                        if d1.form_submit_button("🗑️ CONFIRMER"):
                            if del_code == str(row['CODE']):
                                df_immat = df_immat.drop(idx)
                                conn.update(worksheet=nom_feuille_immat, data=df_immat)
                                log_action(row['Nom d\'utilisateur ROBLOX'], "Suppression", row['Numéro de la plaque'])
                                st.success("Supprimé !"); time.sleep(0.5); st.rerun()
                            else: st.error("Code incorrect")
                        if d2.form_submit_button("Annuler"):
                            st.session_state[f"mode_del_{idx}"] = False; st.rerun()

# ==========================================
# ONGLET 2 : POINTS DE PERMIS
# ==========================================
with tabs[1]:
    nom_feuille_pts = "Points Permis"
    try: df_pts = conn.read(worksheet=nom_feuille_pts, ttl=0)
    except: df_pts = pd.DataFrame()

    with st.expander("👤 [ADMIN] Enregistrer un nouveau conducteur"):
        st.info("💡 **INFO ADMIN :** Lors de la création d'un dossier, un compte bancaire est automatiquement créé avec un solde initial de **15'000$**.")
        with st.form("admin_add_v57"):
            adm_n = st.text_input("Nom Admin")
            r_name = st.text_input("Nom Roblox")
            d_name = st.text_input("Nom Discord")
            pts_val = st.number_input("Points", 0, 25, 25)
            a_code = st.text_input("Code Admin", type="password")
            if st.form_submit_button("Valider et Créer le dossier"):
                if a_code == CODE_ADMIN_GENERAL and adm_n and r_name:
                    v_label = "VALIDE" if pts_val >= 14 else ("OUI" if pts_val >= 1 else "NON")
                    new_d = pd.DataFrame([{"Nom Discord": d_name, "Nom Roblox": r_name, "PTS": pts_val, "Validité": v_label}])
                    conn.update(worksheet=nom_feuille_pts, data=pd.concat([df_pts, new_d], ignore_index=True))
                    try:
                        df_b = conn.read(worksheet="Banque", ttl=0)
                        if r_name.lower() not in df_b["Nom Roblox"].astype(str).str.lower().values if not df_b.empty else [True]:
                            new_b = pd.DataFrame([{"Solde": 15000.0, "Nom Roblox": r_name, "Pseudo Admin": adm_n}])
                            conn.update(worksheet="Banque", data=pd.concat([df_b, new_b], ignore_index=True))
                    except: pass
                    log_action(adm_n, "Nouveau Dossier + Banque Auto", r_name)
                    st.success(f"Dossier de {r_name} créé !"); time.sleep(1); st.rerun()

    st.divider()
    search_p = st.text_input("🔍 Rechercher un conducteur (Roblox ou Discord)").strip()
    if not df_pts.empty and search_p:
        res_p = df_pts[df_pts.apply(lambda r: r.astype(str).str.contains(search_p, case=False).any(), axis=1)]
        for idx, row in res_p.iterrows():
            st.markdown(f"### 👤 {row.get('Nom Roblox')} (@{row.get('Nom Discord')})")
            st.write(f"Points: **{row.get('PTS')}** | Validité: **{row.get('Validité')}**")
            with st.expander("⚙️ Modifier / Supprimer"):
                with st.form(key=f"p_edit_{idx}"):
                    adm_auth = st.text_input("Nom Admin")
                    code_auth = st.text_input("Code Admin", type="password")
                    new_pts_val = st.number_input("Points", 0, 25, int(row.get("PTS", 0)))
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("Sauver"):
                        if code_auth == CODE_ADMIN_GENERAL:
                            df_pts.at[idx, "PTS"] = new_pts_val
                            df_pts.at[idx, "Validité"] = "VALIDE" if new_pts_val >= 14 else ("OUI" if new_pts_val >= 1 else "NON")
                            conn.update(worksheet=nom_feuille_pts, data=df_pts)
                            log_action(adm_auth, f"Points -> {new_pts_val}", row.get('Nom Roblox'))
                            st.rerun()
                    if c2.form_submit_button("🗑️ Supprimer"):
                        if code_auth == CODE_ADMIN_GENERAL:
                            conn.update(worksheet=nom_feuille_pts, data=df_pts.drop(idx))
                            log_action(adm_auth, "Suppression Permis", row.get('Nom Roblox'))
                            st.rerun()

# ==========================================
# ONGLET 3 : BANQUE (RECHERCHE DISCORD AJOUTÉE)
# ==========================================
with tabs[2]:
    st.subheader("💰 Banque Centrale")
    st.info("💡 **Note aux Citoyens :** Un compte bancaire est automatiquement créé dès l'obtention de votre dossier de conduite.")
    
    try: 
        df_bank = conn.read(worksheet="Banque", ttl=0)
        df_pts_ref = conn.read(worksheet="Points Permis", ttl=0) # Pour le lien Discord
    except: 
        df_bank = pd.DataFrame()
        df_pts_ref = pd.DataFrame()
    
    sb = st.text_input("🔍 Rechercher un compte (Nom Roblox ou Nom Discord)").strip()
    
    if not df_bank.empty and sb:
        # 1. On cherche d'abord les correspondances directes Roblox dans la Banque
        mask_rob = df_bank["Nom Roblox"].astype(str).str.contains(sb, case=False, na=False)
        
        # 2. On cherche si 'sb' correspond à un Nom Discord dans Points Permis
        roblox_names_from_discord = []
        if not df_pts_ref.empty:
            match_discord = df_pts_ref[df_pts_ref["Nom Discord"].astype(str).str.contains(sb, case=False, na=False)]
            roblox_names_from_discord = match_discord["Nom Roblox"].tolist()
        
        mask_disc = df_bank["Nom Roblox"].isin(roblox_names_from_discord)
        
        # On combine les deux recherches
        res_b = df_bank[mask_rob | mask_disc]
        
        if res_b.empty:
            st.warning("Aucun compte trouvé pour cette recherche.")
        
        for idx, row in res_b.iterrows():
            curr_s = float(row.get('Solde', 0))
            # Affichage du pseudo Discord s'il existe pour plus de clarté
            discord_tag = ""
            if not df_pts_ref.empty:
                d_match = df_pts_ref[df_pts_ref["Nom Roblox"] == row['Nom Roblox']]
                if not d_match.empty:
                    discord_tag = f" (@{d_match.iloc[0]['Nom Discord']})"
            
            st.metric(f"{row.get('Nom Roblox')}{discord_tag}", f"{curr_s:,.0f} $")
            
            with st.expander("🛡️ Actions Administratives"):
                with st.form(key=f"b_t_v57_{idx}"):
                    adm_b = st.text_input("Nom Admin")
                    code_b = st.text_input("Code Admin", type="password")
                    montant = st.number_input("Montant", step=500.0)
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("📉 Retirer"):
                        if code_b == CODE_ADMIN_GENERAL:
                            df_bank.at[idx, "Solde"] = curr_s - montant
                            conn.update(worksheet="Banque", data=df_bank)
                            log_action(adm_b, f"Retrait -{montant}", row.get('Nom Roblox')); st.rerun()
                    if b2.form_submit_button("📈 Ajouter"):
                        if code_b == CODE_ADMIN_GENERAL:
                            df_bank.at[idx, "Solde"] = curr_s + montant
                            conn.update(worksheet="Banque", data=df_bank)
                            log_action(adm_b, f"Ajout +{montant}", row.get('Nom Roblox')); st.rerun()

# ==========================================
# ONGLET 4 : LOGS
# ==========================================
with tabs[3]:
    st.subheader("📜 Historique")
    unlock = st.text_input("Code Admin", type="password")
    if unlock == CODE_ADMIN_GENERAL:
        try: st.dataframe(conn.read(worksheet="Logs", ttl=0).iloc[::-1], use_container_width=True)
        except: st.warning("Logs vides.")

st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 12px;'>Version v5.7 - Discord Search Support</div>", unsafe_allow_html=True)
