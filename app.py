import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="RCRP - Immatriculations", layout="centered")
st.title("🚗 Système d'Immatriculation")

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)
df.columns = [c.strip() for c in df.columns]

with st.expander("➕ Enregistrer un véhicule"):
    with st.form("inscription"):
        user = st.text_input("Nom d'utilisateur ROBLOX")
        marque = st.text_input("Marque du véhicule")
        v_type = st.text_input("Type de véhicule")
        couleur = st.text_input("Couleur du véhicule")
        etat = st.selectbox("L'état de la plaque", ["Valide", "Périmée"])
        plaque = st.text_input("Numéro de la plaque")
        sign = st.text_input("Signature (Nom d'utilisateur)")
        submit = st.form_submit_button("Valider")
        if submit:
            new_row = pd.DataFrame([{"Horodateur": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": user, "Marque du véhicule": marque, "Type de véhicule": v_type, "Couleur du véhicule": couleur, "L'état de la plaque": etat, "Numéro de la plaque": plaque, "Signature (Nom d'utilisateur)": sign}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Enregistré !")
            st.rerun()

st.subheader("Véhicules en base")
for index, row in df.iterrows():
    col1, col2 = st.columns([4, 1])
    col1.write(f"**{row['Numéro de la plaque']}** | {row['Nom d'utilisateur ROBLOX']}")
    if col2.button("🗑️", key=f"btn_{index}"):
        df = df.drop(index)
        conn.update(data=df)
        st.rerun()
