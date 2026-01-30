import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="RCRP - Immatriculations", layout="centered")
st.title("🚗 Système d'Immatriculation")

# Connexion simplifiée
conn = st.connection("gsheets", type=GSheetsConnection)

# Lecture des données
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
        etat = st.selectbox("État / Province (State/Province)", liste_etats)
        plaque = st.text_input("Numéro de la plaque")
        sign = st.text_input("Signature")
        
        submit = st.form_submit_button("Valider l'immatriculation")

        if submit:
            if user and plaque: # Vérifie que les champs importants sont remplis
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
                # On ajoute la ligne au tableau existant
                updated_df = pd.concat([df, new_row], ignore_index=True)
                # On renvoie TOUT le tableau mis à jour
                conn.update(data=updated_df)
                st.success("✅ Véhicule enregistré avec succès !")
                st.rerun()
            else:
                st.error("⚠️ Merci de remplir au moins le pseudo et la plaque.")

st.divider()

# --- RECHERCHE ET LISTE ---
st.subheader("Base de données")
search = st.text_input("🔍 Rechercher une plaque ou un pseudo")

if not df.empty:
    # Recherche insensible à la casse
    mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
    filtered_df = df[mask]
    
    for index, row in filtered_df.iterrows():
        col1, col2 = st.columns([4, 1])
        info = f"**{row.get('Numéro de la plaque', 'N/A')}** ({row.get('L\'état de la plaque', 'N/A')}) — {row.get('Nom d\'utilisateur ROBLOX', 'Inconnu')}"
        col1.write(info)
        
        if col2.button("🗑️", key=f"btn_{index}"):
            df = df.drop(index)
            conn.update(data=df)
            st.warning("Entrée supprimée.")
            st.rerun()
else:
    st.info("Aucun véhicule dans la base.")
