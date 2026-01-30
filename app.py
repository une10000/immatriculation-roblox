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

# --- FORMULAIRE ---
with st.expander("➕ Enregistrer un nouveau véhicule"):
    with st.form("inscription"):
        user = st.text_input("Nom d'utilisateur ROBLOX")
        marque = st.text_input("Marque du véhicule")
        v_type = st.text_input("Type de véhicule")
        couleur = st.text_input("Couleur du véhicule")
        # --- TA MODIFICATION ICI ---
        etat = st.selectbox("État (State)", ["Californie", "Florida", "Liberty County", "New York", "Texas"])
        # ----------------------------
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
    # Filtrer les résultats si on écrit dans la barre de recherche
    filtered_df = df[df.astype(str).apply(lambda x: search.lower() in x.str.lower().values, axis=1)]
    
    for index, row in filtered_df.iterrows():
        col1, col2 = st.columns([4, 1])
        info = f"**{row.get('Numéro de la plaque', 'N/A')}** ({row.get('L\'état de la plaque', 'N/A')}) — {row.get('Nom d\'utilisateur ROBLOX', 'Inconnu')}"
        col1.write(info)
        if col2.button("🗑️", key=f"btn_{index}"):
            df = df.drop(index)
            conn.update(data=df)
            st.rerun()
else:
    st.info("Aucun véhicule enregistré.")
