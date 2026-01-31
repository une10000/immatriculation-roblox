import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# Configuration de la page
st.set_page_config(page_title="RCRP - Fichier Central", layout="wide")

# --- LOGO ET TITRE ---
st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=697f2cf3&is=697ddb73&hm=dccb2edf0897deb4ccbdee22b3221134415bfed15b2cc808e439232c6f18bcab&", width=200)

st.title("🚓 Fichier Central de la Police")
st.write("### RCRPFR - Base de données officielle")

# Connexion aux Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CONFIGURATION ADMIN ---
CODE_ADMIN_GENERAL = "RCRPFR-25-26"

# --- NAVIGATION PAR ONGLETS ---
tabs = st.tabs(["🚗 Immatriculations", "🪪 Points de Permis"])

# ==========================================
# ONGLET 1 : IMMATRICULATIONS
# ==========================================
with tabs[0]:
    nom_feuille_immat = "Copie de Immatriculations"
    try:
        df = conn.read(worksheet=nom_feuille_immat, ttl=0)
        df.columns = [str(c).strip() for c in df.columns]
    except: df = pd.DataFrame()

    liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])
    liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])

    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("inscription"):
            u_reg = st.text_input("Nom d'utilisateur ROBLOX")
            m_reg = st.selectbox("Marque du véhicule", liste_marques)
            e_reg = st.selectbox("État", liste_etats)
            p_reg = st.text_input("Numéro de la plaque")
            c_reg = st.text_input("Code secret (pour suppression)", type="password")
            if st.form_submit_button("Valider"):
                if u_reg and p_reg and c_reg:
                    heure_locale = (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M")
                    new_row = pd.DataFrame([{"Horodateur": heure_locale, "Nom d'utilisateur ROBLOX": u_reg, "Marque du véhicule": m_reg, "L'état de la plaque": e_reg, "Numéro de la plaque": p_reg, "CODE": str(c_reg)}])
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
        
        with st.expander("⚙️ Supprimer ma fiche"):
            for idx, row in display_df.iterrows():
                p_val = row.get("Numéro de la plaque", "N/A")
                u_val = row.get("Nom d'utilisateur ROBLOX", "N/A")
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(f"🏷️ **{p_val}** — 👤 **{u_val}**")
                i_code = c2.text_input("Code", key=f"del_{idx}", type="password", placeholder="Code", label_visibility="collapsed")
                if c3.button("🗑️", key=f"btn_del_{idx}"):
                    if i_code == str(row.get("CODE")):
                        conn.update(worksheet=nom_feuille_immat, data=df.drop(idx))
                        st.toast(f"Fiche supprimée", icon="🗑️")
                        time.sleep(1)
                        st.rerun()

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

    search_p = st.text_input("🔍 Rechercher conducteur (Roblox ou Discord)").strip()

    if not df_pts.empty and search_p:
        mask_p = (df_pts["Nom Discord"].astype(str).str.contains(search_p, case=False, na=False) | 
                  df_pts["Nom Roblox"].astype(str).str.contains(search_p, case=False, na=False))
        res = df_pts[mask_p]

        for idx, row in res.iterrows():
            try:
                pts_actuels = int(row.get("PTS", 0))
            except:
                pts_actuels = 0
            
            # --- CALCUL DU STATUT v2.7 (Avec Emoji Croix Rouge ❌) ---
            if pts_actuels >= 20:
                st_label = "VALIDE"
                st_icon = "✅"
                st_color = "green"
            elif pts_actuels >= 10:
                st_label = "DANGER"
                st_icon = "⚠️"
                st_color = "orange"
            else:
                st_label = "INVALIDE"
                st_icon = "❌" # Changement demandé : Panneau Stop -> Croix Rouge
                st_color = "red"
            
            st.markdown(f"### 👤 {row.get('Nom Roblox')}")
            col1, col2, col3 = st.columns([1, 1, 1])
            col1.metric("Points", f"{pts_actuels}/25")
            col2.write(f"**Discord:** {row.get('Nom Discord')}")
            
            if st_color == "green": col3.success(f"{st_icon} {st_label}")
            elif st_color == "orange": col3.warning(f"{st_icon} {st_label}")
            else: col3.error(f"{st_icon} {st_label}")

            with st.expander(f"⚙️ Modifier les points de {row.get('Nom Roblox')}"):
                with st.form(key=f"form_pts_{idx}"):
                    auth_code = st.text_input("Code Admin", type="password", placeholder="Code")
                    nb_pts = st.number_input("Points à modifier", min_value=1, max_value=25, value=1)
                    
                    c_btn1, c_btn2 = st.columns(2)
                    sub = c_btn1.form_submit_button("➖ Retirer")
                    add = c_btn2.form_submit_button("➕ Ajouter")

                    if sub or add:
                        if auth_code == CODE_ADMIN_GENERAL:
                            nouveau = max(0, pts_actuels - nb_pts) if sub else min(25, pts_actuels + nb_pts)
                            
                            if nouveau >= 20: n_statut = "VALIDE"
                            elif nouveau >= 10: n_statut = "DANGER"
                            else: n_statut = "INVALIDE"
                            
                            df_pts.at[idx, "PTS"] = nouveau
                            df_pts.at[idx, "Validité"] = n_statut
                            
                            conn.update(worksheet=nom_feuille_pts, data=df_pts)
                            st.toast(f"Mise à jour réussie : {nouveau}/25", icon="✅")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Code Admin incorrect")
            st.divider()
    elif not df_pts.empty:
        st.info("Recherchez un nom pour agir sur le permis.")

# --- VERSION v2.7 ---
st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 12px;'>Version v2.7</div>", unsafe_allow_html=True)
