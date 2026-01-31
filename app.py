import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="RCRP - Immatriculations", layout="wide")
st.title("🚗 Système d'Immatriculation")

# Connexion sécurisée au robot (Service Account)
conn = st.connection("gsheets", type=GSheetsConnection)
nom_feuille = "Copie de Immatriculations"

# Lecture des données en temps réel
try:
    df = conn.read(worksheet=nom_feuille, ttl=0)
    df.columns = [str(c).strip() for c in df.columns]
except:
    df = pd.DataFrame()

# Liste des états mise à jour (avec le Wisconsin !)
liste_etats = sorted([
    "Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", 
    "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", 
    "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", 
    "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", 
    "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", 
    "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", 
    "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"
])

# --- FORMULAIRE D'ENREGISTREMENT ---
with st.expander("➕ Enregistrer un nouveau véhicule"):
    with st.form("inscription"):
        c1, c2 = st.columns(2)
        user = c1.text_input("Pseudo ROBLOX")
        marque = c2.text_input("Marque du véhicule")
        
        c3, c4 = st.columns(2)
        plaque = c3.text_input("Numéro de la plaque")
        etat = c4.selectbox("État / Province", liste_etats)
        
        if st.form_submit_button("Valider l'immatriculation"):
            if user and plaque:
                new_row = pd.DataFrame([{
                    "Horodateur": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                    "Nom d'utilisateur ROBLOX": user,
                    "Marque du véhicule": marque,
                    "L'état de la plaque": etat,
                    "Numéro de la plaque": plaque
                }])
                # On ajoute la ligne et on renvoie tout à Google
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet=nom_feuille, data=updated_df)
                st.success(f"Véhicule {plaque} enregistré avec succès !")
                st.rerun()
            else:
                st.error("Remplis au moins le Pseudo et la Plaque !")

st.divider()

# --- RECHERCHE ET SUPPRESSION ---
st.subheader("Base de données")
search = st.text_input("🔍 Rechercher (Plaque ou Pseudo)")

if not df.empty:
    # Filtrer selon la recherche
    mask = df.astype(str).apply(lambda x: search.lower() in x.str.lower().values, axis=1)
    df_filtered = df[mask]
    
    # Affichage ligne par ligne avec bouton supprimer
    for index, row in df_filtered.iterrows():
        col_info, col_del = st.columns([5, 1])
        
        p = row.get("Numéro de la plaque", "N/A")
        u = row.get("Nom d'utilisateur ROBLOX", "Inconnu")
        e = row.get("L'état de la plaque", "N/A")
        
        col_info.write(f"🔹 **{p}** ({e}) — Propriétaire : `{u}`")
        
        if col_del.button("🗑️ Effacer", key=f"del_{index}"):
            df_final = df.drop(index)
            conn.update(worksheet=nom_feuille, data=df_final)
            st.rerun()
else:
    st.info("Aucune donnée enregistrée pour le moment.")
