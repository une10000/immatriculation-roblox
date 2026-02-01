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

# --- LISTES ---
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])
liste_assurances = ["Non assuré", "RCT", "Averis"] # Global Assurance supprimé

# --- NAVIGATION PAR ONGLETS ---
tabs = st.tabs(["🚗 Immatriculations", "🪪 Points de Permis", "💰 Banque"])

# ==========================================
# ONGLET 1 : IMMATRICULATIONS
# ==========================================
with tabs[0]:
    nom_feuille_immat = "Copie de Immatriculations"
    try:
        df = conn.read(worksheet=nom_feuille_immat, ttl=0)
        df.columns = [str(c).strip() for c in df.columns]
    except: df = pd.DataFrame()

    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("inscription"):
            u_reg = st.text_input("Nom d'utilisateur ROBLOX")
            m_reg = st.selectbox("Marque du véhicule", liste_marques)
            e_reg = st.selectbox("État", liste_etats)
            p_reg = st.text_input("Numéro de la plaque")
            a_reg = st.selectbox("Assurance", liste_assurances)
            c_reg = st.text_input("Code secret (pour suppression/modification)", type="password")
            
            if st.form_submit_button("Valider"):
                if u_reg and p_reg and c_reg:
                    heure_locale = (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M")
                    new_row = pd.DataFrame([{
                        "Horodateur": heure_locale, 
                        "Nom d'utilisateur ROBLOX": u_reg, 
                        "Marque du véhicule": m_reg, 
                        "L'état de la plaque": e_reg, 
                        "Numéro de la plaque": p_reg, 
                        "Assurance": a_reg,
                        "CODE": str(c_reg)
                    }])
                    conn.update(worksheet=nom_feuille_immat, data=pd.concat([df, new_row], ignore_index=True))
                    st.success("✅ Véhicule enregistré !")
                    time.sleep(1)
                    st.rerun()

    st.divider()
    s_query = st.text_input("🔍 Rechercher véhicule (Pseudo, Plaque, Marque)").strip().upper()
    if not df.empty:
        mask = df.apply(lambda r: r.astype(str).str.contains(s_query, case=False).any(), axis=1) if s_query else [True]*len(df)
        display_df = df[mask]
        st.dataframe(display_df[[c for c in display_df.columns if c != "CODE"]], use_container_width=True)
        
        st.markdown("### 🛠️ Gérer mes fiches")
        for idx, row in display_df.iterrows():
            label_expander = f"⚙️ Modifier / Supprimer : {row.get('Numéro de la plaque')} ({row.get('Nom d\'utilisateur ROBLOX')})"
            with st.expander(label_expander):
                c_auth = st.text_input("Ton code secret", key=f"auth_{idx}", type="password")
                
                col_mod1, col_mod2 = st.columns(2)
                with col_mod1:
                    m_val = row.get('Marque du véhicule', '')
                    new_m = st.selectbox("Marque", liste_marques, index=liste_marques.index(m_val) if m_val in liste_marques else 0, key=f"m_{idx}")
                    e_val = row.get("L'état de la plaque", '')
                    new_e = st.selectbox("État", liste_etats, index=liste_etats.index(e_val) if e_val in liste_etats else 0, key=f"e_{idx}")
                with col_mod2:
                    new_p = st.text_input("Plaque", value=row.get('Numéro de la plaque', ''), key=f"p_{idx}")
                    a_val = row.get('Assurance', 'Non assuré')
                    new_a = st.selectbox("Assurance", liste_assurances, index=liste_assurances.index(a_val) if a_val in liste_assurances else 0, key=f"a_{idx}")
                
                b1, b2 = st.columns(2)
                if b1.button("💾 Enregistrer modifications", key=f"save_{idx}"):
                    if c_auth == str(row.get("CODE")):
                        df.at[idx, 'Marque du véhicule'] = new_m
                        df.at[idx, "L'état de la plaque"] = new_e
                        df.at[idx, 'Numéro de la plaque'] = new_p
                        df.at[idx, 'Assurance'] = new_a
                        conn.update(worksheet=nom_feuille_immat, data=df)
                        st.success("Mise à jour réussie !")
                        time.sleep(1)
                        st.rerun()
                    else: st.error("Code incorrect")
                
                if b2.button("🗑️ Supprimer la fiche", key=f"del_{idx}"):
                    if c_auth == str(row.get("CODE")):
                        conn.update(worksheet=nom_feuille_immat, data=df.drop(idx))
                        st.toast("Fiche supprimée")
                        time.sleep(1)
                        st.rerun()
                    else: st.error("Code incorrect")

# ==========================================
# ONGLET 2 : POINTS DE PERMIS
# ==========================================
with tabs[1]:
    st.subheader("🪪 Gestion des Permis")
    nom_feuille_pts = "Points Permis"
    try:
        df_pts = conn.read(worksheet=nom_feuille_pts, ttl=0)
        df_pts.columns = [str(c).strip() for c in df_pts.columns]
    except: df_pts = pd.DataFrame()

    # --- RECHERCHE PAR ROBLOX OU DISCORD ---
    search_p = st.text_input("🔍 Rechercher conducteur (Nom Roblox ou Pseudo Discord)").strip()
    
    if not df_pts.empty and search_p:
        # On cherche dans les deux colonnes possibles
        mask_roblox = df_pts["Nom Roblox"].astype(str).str.contains(search_p, case=False, na=False)
        mask_discord = pd.Series([False] * len(df_pts)) # Par défaut si la colonne n'existe pas
        
        if "Utilisateur Discord" in df_pts.columns:
            mask_discord = df_pts["Utilisateur Discord"].astype(str).str.contains(search_p, case=False, na=False)
            
        res = df_pts[mask_roblox | mask_discord]
        
        for idx, row in res.iterrows():
            try: pts_actuels = int(row.get("PTS", 0))
            except: pts_actuels = 0
            
            if pts_actuels >= 14: st_label, st_icon, st_color = "VALIDE", "✅", "green"
            elif pts_actuels >= 1: st_label, st_icon, st_color = "DANGER", "⚠️", "orange"
            else: st_label, st_icon, st_color = "INVALIDE", "❌", "red"
            
            st.markdown(f"### 👤 {row.get('Nom Roblox')}")
            if "Utilisateur Discord" in row:
                st.caption(f"Discord: {row.get('Utilisateur Discord')}")
                
            col1, col2, col3 = st.columns([1, 1, 1])
            col1.metric("Points", f"{pts_actuels}/25")
            
            if st_color == "green": col3.success(f"{st_icon} {st_label}")
            elif st_color == "orange": col3.warning(f"{st_icon} {st_label}")
            else: col3.error(f"{st_icon} {st_label}")

            with st.expander(f"⚙️ Modifier les points"):
                with st.form(key=f"f_pts_{idx}"):
                    auth = st.text_input("Code Admin", type="password")
                    nb = st.number_input("Nombre de points", min_value=1, max_value=25, value=1)
                    cb1, cb2 = st.columns(2)
                    sub = cb1.form_submit_button("➖ Retirer")
                    add = cb2.form_submit_button("➕ Ajouter")
                    if (sub or add) and auth == CODE_ADMIN_GENERAL:
                        nouveau = max(0, pts_actuels - nb) if sub else min(25, pts_actuels + nb)
                        if nouveau >= 14: n_statut = "VALIDE"
                        elif nouveau >= 1: n_statut = "DANGER"
                        else: n_statut = "INVALIDE"
                        df_pts.at[idx, "PTS"] = nouveau
                        df_pts.at[idx, "Validité"] = n_statut
                        conn.update(worksheet=nom_feuille_pts, data=df_pts)
                        st.toast("Succès", icon="✅")
                        time.sleep(0.5)
                        st.rerun()
                    elif (sub or add): st.error("Code Admin incorrect")
            st.divider()

# ==========================================
# ONGLET 3 : BANQUE 🏦
# ==========================================
with tabs[2]:
    st.subheader("💰 Banque Centrale de RCRP")
    nom_feuille_banque = "Banque"
    try:
        df_bank = conn.read(worksheet=nom_feuille_banque, ttl=0)
        df_bank.columns = [str(c).strip() for c in df_bank.columns]
    except: df_bank = pd.DataFrame(columns=["Nom Roblox", "Solde"])

    with st.expander("✨ Pas encore de compte ? Ouvre le tien ici !"):
        with st.form("pub_reg"):
            n_u = st.text_input("Nom Roblox").strip()
            if st.form_submit_button("Confirmer"):
                if n_u:
                    if not df_bank.empty and n_u.lower() in df_bank["Nom Roblox"].str.lower().values:
                        st.error("❌ Ce compte existe déjà.")
                    else:
                        new_acc = pd.DataFrame([{"Nom Roblox": n_u, "Solde": 15000.0}])
                        conn.update(worksheet=nom_feuille_banque, data=pd.concat([df_bank, new_acc], ignore_index=True))
                        st.success(f"Bienvenue {n_u} !")
                        time.sleep(1)
                        st.rerun()

    st.divider()
    search_b = st.text_input("🔍 Rechercher solde (Nom Roblox)").strip()
    if not df_bank.empty and search_b:
        mask_b = df_bank["Nom Roblox"].astype(str).str.contains(search_b, case=False, na=False)
        res_b = df_bank[mask_b]
        for idx, row in res_b.iterrows():
            try: solde_actuel = float(row.get("Solde", 0))
            except: solde_actuel = 0.0
            st.markdown(f"### 👤 {row.get('Nom Roblox')}")
            st.metric("Solde", f"{solde_actuel:,.0f} $".replace(",", " "))
            
            with st.expander("🛡️ Admin (Amendes / Salaires)"):
                with st.form(key=f"f_bank_{idx}"):
                    a_b = st.text_input("Code Admin", type="password")
                    m_b = st.number_input("Montant", min_value=0.0, step=500.0)
                    col_b1, col_b2 = st.columns(2)
                    ret_b = col_b1.form_submit_button("📉 Retirer")
                    dep_b = col_b2.form_submit_button("📈 Ajouter")
                    
                    if (ret_b or dep_b) and a_b == CODE_ADMIN_GENERAL:
                        n_solde = solde_actuel - m_b if ret_b else solde_actuel + m_b
                        df_bank.at[idx, "Solde"] = n_solde
                        conn.update(worksheet=nom_feuille_banque, data=df_bank)
                        st.toast("Transaction effectuée")
                        time.sleep(0.5)
                        st.rerun()
                    elif (ret_b or dep_b): st.error("Code Admin incorrect")
            st.divider()

# --- VERSION v3.9 ---
st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 12px;'>Version v3.9 - Recherche Discord & Suppression Global</div>", unsafe_allow_html=True)
