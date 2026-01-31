import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="RCRP - Immatriculations", layout="wide")
st.title("🚗 Système d'Immatriculation")

conn = st.connection("gsheets", type=GSheetsConnection)
nom_feuille = "Copie de Immatriculations"

# Lecture des données
try:
    df = conn.read(worksheet=nom_feuille, ttl=0)
    df.columns = [str(c).strip() for c in df.columns]
except:
    df = pd.DataFrame()

# --- LISTE COMPLÈTE DES ÉTATS ---
liste_etats = sorted([
    "Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", 
    "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", 
    "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", 
    "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", 
    "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", 
    "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", 
    "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"
])

# --- FORMULAIRE ---
with st.expander("➕ Enregistrer un véhicule"):
    with st.form("inscription"):
        user = st.text_input("Pseudo ROBLOX")
        marque = st.text_input("Marque du véhicule")
        # On utilise maintenant la variable liste_etats ici
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
                st.success("Véhicule enregistré !")
                st.rerun()

st.divider()

# --- AFFICHAGE ET SUPPRESSION ---
st.subheader("Base de données")

if not df.empty:
    # On affiche le tableau pour voir toutes les colonnes
    st.dataframe(df, use_container_width=True)
    
    st.write("---")
    # Liste pour supprimer
    for index, row in df.iterrows():
        # On utilise .get pour éviter les erreurs si une colonne manque
        p = row.get("Numéro de la plaque", "Sans Plaque")
        u = row.get("Nom d'utilisateur ROBLOX", "Inconnu")
        
        c1, c2 = st.columns([5, 1])
        c1.write(f"🏷️ Plaque: **{p}** | 👤 Proprio: **{u}**")
        
        if c2.button("🗑️ Effacer", key=f"del_{index}"):
            # On supprime la ligne du tableau
            df_dropped = df.drop(index)
            # On renvoie le tableau entier SANS cette ligne à Google Sheets
            conn.update(worksheet=nom_feuille, data=df_dropped)
            st.rerun()
else:
    st.info("Aucune donnée trouvée. Vérifie tes titres en ligne 1 de ton Google Sheet.")
