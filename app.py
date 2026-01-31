import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="RCRP - Immatriculations", layout="wide")

# --- LOGO ET TITRE ---
st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=697f2cf3&is=697ddb73&hm=dccb2edf0897deb4ccbdee22b3221134415bfed15b2cc808e439232c6f18bcab&", width=200)

st.title("🚗 Système d'Immatriculation")
st.write("### RCRPFR - Fichier Central de la Police")

conn = st.connection("gsheets", type=GSheetsConnection)
nom_feuille = "Copie de Immatriculations"

# --- LECTURE DES DONNÉES ---
try:
    df = conn.read(worksheet=nom_feuille, ttl=0)
    df.columns = [str(c).strip() for c in df.columns]
except Exception:
    df = pd.DataFrame()

# --- LISTES (MARQUES & ÉTATS) ---
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])

# --- FORMULAIRE D'ENREGISTREMENT ---
with st.expander("➕ Enregistrer un véhicule"):
    with st.form("inscription"):
        user = st.text_input("Pseudo ROBLOX")
        marque = st.selectbox("Marque du véhicule", liste_marques)
        etat = st.selectbox("État", liste_etats)
        plaque = st.text_input("Numéro de la plaque")
        code_secret = st.text_input("Code secret (pour suppression)", type="password", help="Code obligatoire pour effacer votre fiche plus tard.")
        
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
                conn.update(worksheet=nom_feuille, data=updated_df)
                st.success("Véhicule enregistré sur rcrpfr.ch !")
                st.rerun()
            else:
                st.error("Remplissez tous les champs.")

st.divider()

# --- RECHERCHE ---
st.subheader("🔍 Recherche dans le fichier central")
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
        st.write("### ⚙️ Gestion de mes immatriculations")
        
        for index, row in display_df.iterrows():
            p = row.get("Numéro de la plaque", "N/A")
            u = row.get("Nom d'utilisateur ROBLOX", "N/A")
            real_code = str(row.get("CODE", ""))
            
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(f"🏷️ **{p}** — 👤 **{u}**")
            input_code = c2.text_input("Code", key=f"code_{index}", type="password", label_visibility="collapsed", placeholder="Code secret")
            
            if c3.button("🗑️ Effacer", key=f"btn_{index}"):
                if input_code == real_code:
                    df_dropped = df.drop(index)
                    conn.update(worksheet=nom_feuille, data=df_dropped)
                    st.success("Supprimé !")
                    st.rerun()
                else:
                    st.error("Code incorrect")
    else:
        st.warning("⚠️ Aucun résultat.")
else:
    st.info("La base de données est vide.")

# --- VERSION FINALE v1.6 ---
st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 12px;'>Version v1.6 (Domaine Actif)</div>", unsafe_allow_html=True)
