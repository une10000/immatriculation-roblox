import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuration large pour mieux voir
st.set_page_config(page_title="RCRP - Immatriculations", layout="wide")
st.title("🚗 Système d'Immatriculation")

# Connexion aux secrets
conn = st.connection("gsheets", type=GSheetsConnection)
nom_feuille = "Copie de Immatriculations"

# Chargement des données
try:
    df = conn.read(worksheet=nom_feuille, ttl=0)
    df.columns = [str(c).strip() for c in df.columns]
except:
    df = pd.DataFrame()

# Liste des états
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])

# --- FORMULAIRE ---
with st.expander("➕ Enregistrer un nouveau véhicule"):
    with st.form("inscription"):
        col1, col2 = st.columns(2)
        user = col1.text_input("Pseudo ROBLOX")
        marque = col2.text_input("Marque du véhicule")
        
        col3, col4 = st.columns(2)
        plaque = col3.text_input("Numéro de la plaque")
        etat = col4.selectbox("État / Province", liste_etats)
        
        submit = st.form_submit_button("Valider l'immatriculation")

        if submit and user and plaque:
            new_row = pd.DataFrame([{
                "Horodateur": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                "Nom d'utilisateur ROBLOX": user,
                "Marque du véhicule": marque,
                "L'état de la plaque": etat,
                "Numéro de la plaque": plaque
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet=nom_feuille, data=updated_df)
            st.success("✅ Enregistré sur la feuille 3 !")
            st.rerun()

st.divider()

# --- RECHERCHE ET SUPPRESSION ---
st.subheader("Base de données (Feuille 3)")
search = st.text_input("🔍 Rechercher une plaque ou un pseudo")

if not df.empty:
    # On filtre selon la recherche
    mask = df.astype(str).apply(lambda x: search.lower() in x.str.lower().values, axis=1)
    df_filtered = df[mask]
    
    # Affichage ligne par ligne avec bouton supprimer
    for index, row in df_filtered.iterrows():
        c1, c2 = st.columns([5, 1])
        
        # On récupère les infos
        txt_plaque = row.get("Numéro de la plaque", "???")
        txt_etat = row.get("L'état de la plaque", "???")
        txt_user = row.get("Nom d'utilisateur ROBLOX", "Inconnu")
        
        c1.write(f"🔹 **{txt_plaque}** [{txt_etat}] — Propriétaire : `{txt_user}`")
        
        # Le bouton pour effacer la ligne
        if c2.button("🗑️ Effacer", key=f"btn_{index}"):
            df = df.drop(index)
            conn.update(worksheet=nom_feuille, data=df)
            st.warning("Suppression en cours...")
            st.rerun()
else:
    st.info("Aucune donnée sur cette feuille.")
