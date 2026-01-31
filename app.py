import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="RCRP - Immatriculations", layout="wide")
st.title("🚗 Système d'Immatriculation")

conn = st.connection("gsheets", type=GSheetsConnection)
nom_feuille = "Copie de Immatriculations"

# --- LECTURE DES DONNÉES ---
try:
    df = conn.read(worksheet=nom_feuille, ttl=0)
    df.columns = [str(c).strip() for c in df.columns]
except Exception:
    df = pd.DataFrame()

# --- LISTE DES ÉTATS ---
liste_etats = sorted([
    "Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", 
    "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", 
    "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", 
    "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", 
    "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", 
    "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", 
    "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"
])

# --- LISTE DES MARQUES RCRP ---
liste_marques = sorted([
    "Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", 
    "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", 
    "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", 
    "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"
])

# --- FORMULAIRE D'ENREGISTREMENT ---
with st.expander("➕ Enregistrer un véhicule"):
    with st.form("inscription"):
        user = st.text_input("Pseudo ROBLOX")
        # Remplacement du texte libre par une liste déroulante pour les marques
        marque = st.selectbox("Marque du véhicule", liste_marques)
        etat = st.selectbox("État", liste_etats)
        plaque = st.text_input("Numéro de la plaque")
        
        if st.form_submit_button("Valider"):
            if user and plaque:
                new_row = pd.DataFrame([{
                    "Horodateur": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                    "Nom d'utilisateur ROBLOX": user,
                    "Marque du véhicule": marque,
                    "L'état de la plaque": etat,
                    "Numéro de la plaque": plaque
                }])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet=nom_feuille, data=updated_df)
                st.success(f"Véhicule {marque} enregistré !")
                st.rerun()

st.divider()

# --- SYSTÈME DE RECHERCHE ---
st.subheader("🔍 Recherche dans le fichier central")
search_query = st.text_input("Rechercher par Pseudo ou Plaque", placeholder="Ex: ZOT-4865...").strip().upper()

# --- FILTRAGE ET AFFICHAGE ---
if not df.empty:
    if search_query:
        mask = (
            df["Nom d'utilisateur ROBLOX"].astype(str).str.contains(search_query, case=False, na=False) | 
            df["Numéro de la plaque"].astype(str).str.contains(search_query, case=False, na=False)
        )
        display_df = df[mask]
    else:
        display_df = df

    if not display_df.empty:
        st.dataframe(display_df, use_container_width=True)
        
        st.write("---")
        st.write("### ⚙️ Actions sur les résultats")
        
        for index, row in display_df.iterrows():
            p = row.get("Numéro de la plaque", "N/A")
            u = row.get("Nom d'utilisateur ROBLOX", "N/A")
            m = row.get("Marque du véhicule", "Inconnue")
            
            col_info, col_btn = st.columns([4, 1])
            col_info.write(f"🏷️ **{p}** — 👤 **{u}** ({m})")
            
            if col_btn.button("🗑️ Supprimer", key=f"del_{index}"):
                df_dropped = df.drop(index)
                conn.update(worksheet=nom_feuille, data=df_dropped)
                st.rerun()
    else:
        st.warning("⚠️ Aucun résultat trouvé.")
else:
    st.info("La base de données est vide.")
