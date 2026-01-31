import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# Configuration de la page
st.set_page_config(page_title="RCRP - Fichier Central", layout="wide")

# --- LOGO ET TITRE ---
st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=697f2cf3&is=697ddb73&hm=dccb2edf0897deb4ccbdee22b3221134415bfed15b2cc808e439232c6f18bcab&", width=200)

st.title("🚓 Fichier Central & 🏦 Banque")

# Connexion aux Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26"

tabs = st.tabs(["🚗 Immatriculations", "🪪 Points de Permis", "💰 Banque"])

# ... (Onglets 1 et 2 restent identiques) ...

# ==========================================
# ONGLET 3 : BANQUE 🏦
# ==========================================
with tabs[2]:
    st.subheader("💰 Banque Centrale de RCRP")
    nom_feuille_banque = "Banque"
    
    try:
        df_bank = conn.read(worksheet=nom_feuille_banque, ttl=0)
        df_bank.columns = [str(c).strip() for c in df_bank.columns]
    except:
        df_bank = pd.DataFrame(columns=["Nom Roblox", "Solde"])

    # --- 1. INSCRIPTION (CIVILS) ---
    with st.expander("✨ Pas encore de compte ? Ouvre le tien ici !"):
        with st.form("public_register"):
            new_user = st.text_input("Ton nom Roblox").strip()
            st.info("Solde de bienvenue : 15 000 $")
            if st.form_submit_button("Confirmer l'ouverture"):
                if new_user:
                    if not df_bank.empty and new_user.lower() in df_bank["Nom Roblox"].str.lower().values:
                        st.error("❌ Ce compte existe déjà.")
                    else:
                        new_acc = pd.DataFrame([{"Nom Roblox": new_user, "Solde": 15000.0}])
                        conn.update(worksheet=nom_feuille_banque, data=pd.concat([df_bank, new_acc], ignore_index=True))
                        st.success(f"🎊 Bienvenue {new_user} !")
                        time.sleep(1)
                        st.rerun()

    st.divider()

    # --- 2. CONSULTATION (CIVILS & ADMINS) ---
    st.markdown("### 🔍 Consulter un solde")
    search_b = st.text_input("Entre ton nom Roblox pour voir ton argent").strip()

    if not df_bank.empty and search_b:
        mask_b = df_bank["Nom Roblox"].astype(str).str.contains(search_b, case=False, na=False)
        res_b = df_bank[mask_b]

        for idx, row in res_b.iterrows():
            solde_actuel = float(row.get("Solde", 0))
            
            # Affichage public du solde
            st.markdown(f"### 👤 {row.get('Nom Roblox')}")
            st.metric("Solde Bancaire", f"{solde_actuel:,.0f} $".replace(",", " "))

            # --- 3. GESTION (ADMINS UNIQUEMENT) ---
            with st.expander("🛡️ Administration (Amendes / Salaires)"):
                with st.form(key=f"form_admin_bank_{idx}"):
                    auth_bank = st.text_input("Code Admin", type="password", placeholder="Code requis")
                    montant = st.number_input("Montant ($)", min_value=0.0, step=500.0)
                    
                    c1, c2 = st.columns(2)
                    retrait = c1.form_submit_button("📉 Retirer")
                    depot = c2.form_submit_button("📈 Ajouter")

                    if retrait or depot:
                        if auth_bank == CODE_ADMIN_GENERAL:
                            nouveau_solde = solde_actuel - montant if retrait else solde_actuel + montant
                            df_bank.at[idx, "Solde"] = nouveau_solde
                            conn.update(worksheet=nom_feuille_banque, data=df_bank)
                            st.toast("Transaction effectuée", icon="💰")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Code Admin incorrect")
            st.divider()
    elif not df_bank.empty:
        st.info("Recherchez un nom pour afficher le solde.")

# --- VERSION v3.4 ---
st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 12px;'>Version v3.4</div>", unsafe_allow_html=True)
