import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuration
st.set_page_config(page_title="RCRP - Immatriculations", layout="centered")
st.title("🚗 Système d'Immatriculation")

# Connexion
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)
df.columns = [str(c).strip() for c in df.columns]

# --- TA LISTE PERSONNALISÉE ---
liste_etats = [
    "Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", 
    "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", 
    "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", 
    "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", 
    "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", 
    "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", 
    "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"
]
liste_etats.sort()

# --- FORMULAIRE ---
with st.expander("➕ Enregistrer un nouveau véhicule"):
    with st.form("inscription"):
        user = st.text_input("Nom d'utilisateur ROBLOX")
        marque = st.text_input("Marque du véhicule")
        v_type = st.text_input("Type de véhicule")
        couleur = st.text_input("Couleur du véhicule")
        
        # Le menu déroulant avec ta liste exacte
        etat = st.selectbox("État / Province (State/Province)", liste_etats)
        
        plaque = st.text_input("Numéro de la plaque")
        sign = st.text_input("Signature")
        
        submit = st.form_submit_button("Valider")

        if submit:
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
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Enregistré !")
            st.rerun()

st.divider()

# --- RECHERCHE ET LISTE ---
st.subheader("Base de données")
search = st.text_input("🔍 Rechercher une plaque ou un pseudo")

if not df.empty:
    # Filtrer les données en fonction de la recherche
    filtered_df = df[df.astype(str).apply(lambda x: search.lower() in x.str.lower().values, axis=1)]
    
    for index, row in filtered_df.iterrows():
        col1, col2 = st.columns([4, 1])
        # Affiche la plaque, l'état et le pseudo
        info = f"**{row.get('Numéro de la plaque', 'N/A')}** ({row.get('L\'état de la plaque', 'N/A')}) — {row.get('Nom d\'utilisateur ROBLOX', 'Inconnu')}"
        col1.write(info)
        
        # Bouton pour supprimer une ligne
        if col2.button("🗑️", key=f"btn_{index}"):
            df = df.drop(index)
            conn.update(data=df)
            st.warning("Entrée supprimée.")
            st.rerun()
else:
    st.info("La base de données est vide.")
