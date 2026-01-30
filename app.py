import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="RCRP - Immatriculations", layout="centered")
st.title("🚗 Système d'Immatriculation")

# Connexion sécurisée
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LECTURE DE LA FEUILLE SPÉCIFIQUE ---
# On précise le nom exact que tu as montré sur ta capture
nom_feuille = "Copie de Immatriculations"

try:
    df = conn.read(worksheet=nom_feuille, ttl=0)
    df.columns = [str(c).strip() for c in df.columns]
except Exception as e:
    st.error(f"Erreur de lecture : Vérifie que l'onglet s'appelle bien '{nom_feuille}'")
    df = pd.DataFrame()

# --- TA LISTE D'ÉTATS ---
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])

# --- FORMULAIRE ---
with st.expander("➕ Enregistrer un nouveau véhicule"):
    with st.form("inscription"):
        user = st.text_input("Nom d'utilisateur ROBLOX")
        marque = st.text_input("Marque du véhicule")
        v_type = st.text_input("Type de véhicule")
        couleur = st.text_input("Couleur du véhicule")
        etat = st.selectbox("État / Province", liste_etats)
        plaque = st.text_input("Numéro de la plaque")
        sign = st.text_input("Signature")
        
        submit = st.form_submit_button("Valider l'immatriculation")

        if submit and user and plaque:
            new_row = pd.DataFrame([{
                "Horodateur": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                "Nom d'utilisateur ROBLOX": user,
                "Marque du véhicule": marque,
                "Type de véhicule": v_type,
                "Couleur du véhicule": couleur,
                "L'état de la plaque": etat,
                "Numéro de la plaque": plaque,
                "Signature (Nom d'utilisateur)": sign
            }])
            
            # On ajoute la ligne
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            # --- ENVOI VERS LA FEUILLE SPÉCIFIQUE ---
            conn.update(worksheet=nom_feuille, data=updated_df)
            st.success("✅ Véhicule enregistré dans la base !")
            st.rerun()

st.divider()

# --- RECHERCHE ---
st.subheader("Base de données")
search = st.text_input("🔍 Rechercher une plaque ou un pseudo")

if not df.empty:
    mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
    filtered_df = df[mask]
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.info("La base de données est vide.")
