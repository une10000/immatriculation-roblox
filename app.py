import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="RCRP - Fichier Central", layout="wide")

# --- LOGO ET TITRE ---
st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=697f2cf3&is=697ddb73&hm=dccb2edf0897deb4ccbdee22b3221134415bfed15b2cc808e439232c6f18bcab&", width=200)

st.title("🚓 Fichier Central de la Police")
st.write("### RCRPFR - Base de données officielle")

# Connexion aux Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CONFIGURATION ADMIN ---
CODE_ADMIN_GENERAL = "RCRP2026"  # <--- TON CODE SECRET ADMIN

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
                    new_row = pd.DataFrame([{"Horodateur": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u_reg, "Marque du véhicule": m_reg, "L'état de la plaque": e_reg, "Numéro de la plaque": p_reg, "CODE": str(c_reg)}])
                    conn.update(worksheet=nom_feuille_immat, data=pd.concat([df, new_row], ignore_index=True))
                    st.success("Véhicule enregistré !")
                    st.rerun()

    st.divider()
    s_query = st.text_input("🔍 Rechercher véhicule (Pseudo, Plaque, Marque)").strip().upper()
    if not df.empty:
        mask = df.apply(lambda r: r.astype(str).str.contains(s_query, case=False).any(), axis=1) if s_query else [True]*len(df)
        display_df = df[mask]
        st.dataframe(display_df[[c for c in display_df.columns if c != "CODE"]], use_container_width=True)
        
        with st.expander("⚙️ Supprimer ma fiche"):
            for idx, row in display_df.iterrows():
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(f"🏷️ **{row['Numéro de la plaque']}**")
                i_code = c2.text_input("Code", key=f"del_{idx}", type="password", placeholder="Code secret", label_visibility="collapsed")
                if c3.button("🗑️", key=f"btn_del_{idx}"):
                    if i_code == str(row.get("CODE")):
                        conn.update(worksheet=nom_feuille_immat, data=df.drop(idx))
                        st.success("Supprimé !")
                        st.rerun()
                    else: st.error("Faux")

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
            pts_actuels = int(row.get("PTS", 0))
            valid = str(row.get("Validité", "NON")).strip().upper()
            
            st.markdown(f"### 👤 {row.get('Nom Roblox')}")
            col1, col2, col3 = st.columns([1, 1, 1])
            col1.metric("Points", f"{pts_actuels}/25")
            col2.write(f"**Discord:** {row.get('Nom Discord')}")
            
            # Logique de couleur (accepte OUI et OK)
            if valid in ["OUI", "OK"]: col3.success("✅ VALIDE")
            elif valid == "DANGER": col3.warning("⚠️ DANGER")
            else: col3.error("🛑 INVALIDE")

            # --- ZONE ADMIN POUR LES POINTS ---
            with st.expander(f"⚙️ Gérer les points de {row.get('Nom Roblox')}"):
                c_adm1, c_adm2, c_adm3 = st.columns([2, 1, 1])
                auth_code = c_adm1.text_input("Code Admin", key=f"adm_code_{idx}", type="password", placeholder="Code")
                nb_pts = c_adm2.number_input("Nbr", min_value=1, max_value=25, key=f"val_{idx}")
                
                if c_adm3.button("➖ Retirer", key=f"sub_{idx}"):
                    if auth_code == CODE_ADMIN_GENERAL:
                        nouveau_solde = max(0, pts_actuels - nb_pts)
                        df_pts.at[idx, "PTS"] = nouveau_solde
                        conn.update(worksheet=nom_feuille_pts, data=df_pts)
                        st.toast(f"Points retirés ! Nouveau solde : {nouveau_solde}", icon="📉")
                        st.rerun()
                    else: st.error("Code faux")
                
                if c_adm3.button("➕ Ajouter", key=f"add_{idx}"):
                    if auth_code == CODE_ADMIN_GENERAL:
                        nouveau_solde = min(25, pts_actuels + nb_pts)
                        df_pts.at[idx, "PTS"] = nouveau_solde
                        conn.update(worksheet=nom_feuille_pts, data=df_pts)
                        st.toast(f"Points ajoutés ! Nouveau solde : {nouveau_solde}", icon="📈")
                        st.rerun()
                    else: st.error("Code faux")
            st.divider()
    elif not df_pts.empty:
        st.info("Recherchez un nom pour voir ou modifier ses points.")

# --- VERSION ---
st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 12px;'>Version v2</div>", unsafe_allow_html=True)
