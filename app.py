import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="RCRP - Fichier Central", layout="wide")

# --- LOGO ET TITRE ---
st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=697f2cf3&is=697ddb73&hm=dccb2edf0897deb4ccbdee22b3221134415bfed15b2cc808e439232c6f18bcab&", width=200)

st.title("🚓 Fichier Central de la Police")
st.write("### RCRPFR - Base de données officielle")

# Connexion Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

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
    except Exception:
        df = pd.DataFrame()

    liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])
    liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])

    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("inscription"):
            user = st.text_input("Nom d'utilisateur ROBLOX")
            marque = st.selectbox("Marque du véhicule", liste_marques)
            etat = st.selectbox("État", liste_etats)
            plaque = st.text_input("Numéro de la plaque")
            code_secret = st.text_input("Code secret (pour suppression)", type="password")
            
            if st.form_submit_button("Valider"):
                if user and plaque and code_secret:
                    new_row = pd.DataFrame([{
                        "Horodateur": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                        "Nom d'utilisateur ROBLOX": user,
                        "Marque du véhicule": marque,
                        "L'état de la plaque": etat,
                        "Numéro de la plaque": plaque,
                        "CODE": str(code_secret)
                    }])
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(worksheet=nom_feuille_immat, data=updated_df)
                    st.success("Véhicule enregistré !")
                    st.rerun()
                else:
                    st.error("Remplissez tous les champs.")

    st.divider()
    st.subheader("🔍 Recherche de véhicules")
    search_query = st.text_input("Rechercher par Pseudo, Plaque ou Marque", placeholder="Ex: Gemini, ZOT-4865...").strip().upper()

    if not df.empty:
        if search_query:
            mask = (df["Nom d'utilisateur ROBLOX"].astype(str).str.contains(search_query, case=False, na=False) | 
                    df["Numéro de la plaque"].astype(str).str.contains(search_query, case=False, na=False) |
                    df["Marque du véhicule"].astype(str).str.contains(search_query, case=False, na=False))
            display_df = df[mask]
        else:
            display_df = df

        if not display_df.empty:
            cols_to_show = [c for c in display_df.columns if c != "CODE"]
            st.dataframe(display_df[cols_to_show], use_container_width=True)
            
            st.write("---")
            st.write("### ⚙️ Gestion")
            for index, row in display_df.iterrows():
                p, u, real_code = row.get("Numéro de la plaque"), row.get("Nom d'utilisateur ROBLOX"), str(row.get("CODE", ""))
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(f"🏷️ **{p}** — 👤 **{u}**")
                input_code = c2.text_input("Code", key=f"code_{index}", type="password", label_visibility="collapsed", placeholder="Code secret")
                if c3.button("🗑️ Effacer", key=f"btn_{index}"):
                    if input_code == real_code:
                        df_dropped = df.drop(index)
                        conn.update(worksheet=nom_feuille_immat, data=df_dropped)
                        st.success("Supprimé !")
                        st.rerun()
                    else: st.error("Code incorrect")

# ==========================================
# ONGLET 2 : POINTS DE PERMIS
# ==========================================
with tabs[1]:
    st.subheader("🪪 Vérification des Points de Permis")
    nom_feuille_pts = "Points Permis"
    
    try:
        df_pts = conn.read(worksheet=nom_feuille_pts, ttl=0)
        df_pts.columns = [str(c).strip() for c in df_pts.columns]
    except:
        df_pts = pd.DataFrame()

    search_pts = st.text_input("Rechercher un Nom Roblox ou Discord", key="search_pts_input").strip()

    if not df_pts.empty and search_pts:
        # Recherche dans les colonnes Nom Discord ou Nom Roblox
        mask_pts = (df_pts["Nom Discord"].astype(str).str.contains(search_pts, case=False, na=False) | 
                    df_pts["Nom Roblox"].astype(str).str.contains(search_pts, case=False, na=False))
        res = df_pts[mask_pts]

        if not res.empty:
            for _, row in res.iterrows():
                pts = row.get("PTS", 0)
                valid = row.get("Validité", "NON")
                
                # Interface propre pour les points
                st.markdown(f"### 👤 {row.get('Nom Roblox')}")
                c1, c2, c3 = st.columns(3)
                c1.metric("Points restants", f"{pts}/25")
                c2.write(f"**Discord:** {row.get('Nom Discord')}")
                
                if valid == "OUI":
                    c3.success("✅ PERMIS VALIDE")
                elif valid == "DANGER":
                    c3.warning("⚠️ ATTENTION (DANGER)")
                else:
                    c3.error("🛑 PERMIS INVALIDE")
                st.divider()
        else:
            st.warning("Aucun dossier trouvé pour ce nom.")
    elif not df_pts.empty:
        st.info("Entrez un nom pour consulter le dossier du conducteur.")

# --- VERSION ---
st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 12px;'>Version v2.0 (Système Multi-Fiches)</div>", unsafe_allow_html=True)
