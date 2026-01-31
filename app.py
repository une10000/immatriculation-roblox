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

# --- FORMULAIRE D'ENREGISTREMENT ---
with st.expander("➕ Enregistrer un véhicule"):
    with st.form("inscription"):
        user = st.text_input("Pseudo ROBLOX")
        marque = st.text_input("Marque du véhicule")
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

# --- SYSTÈME DE RECHERCHE ---
st.subheader("🔍 Recherche dans le fichier central")
search_query = st.text_input("Rechercher par Pseudo ou Plaque", placeholder="Ex: ZOT-4865 ou Ibrahim...").strip().upper()

# --- FILTRAGE ET AFFICHAGE ---
if not df.empty:
    # On crée une copie filtrée du DataFrame si une recherche est active
