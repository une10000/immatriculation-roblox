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

# --- FONCTION DE LOGGING ---
def log_action(action, cible):
    try:
        df_logs = conn.read(worksheet="Logs", ttl=0)
    except:
        df_logs = pd.DataFrame(columns=["Horodateur", "Action", "Cible"])
    
    new_log = pd.DataFrame([{
        "Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"),
        "Action": action,
        "Cible": cible
    }])
    conn.update(worksheet="Logs", data=pd.concat([df_logs, new_log], ignore_index=True))

# --- NAVIGATION ---
tabs = st.tabs(["🚗 Immatriculations", "🪪 Points de Permis", "💰 Banque", "📜 Logs"])

# ==========================================
# ONGLET 2 : POINTS DE PERMIS (MODIFIÉ)
# ==========================================
with tabs[1]:
    nom_feuille_pts = "Points Permis"
    nom_feuille_banque = "Banque"
    try:
        df_pts = conn.read(worksheet=nom_feuille_pts, ttl=0)
        df_bank = conn.read(worksheet=nom_feuille_banque, ttl=0)
    except: 
        df_pts = pd.DataFrame()
        df_bank = pd.DataFrame(columns=["Nom Roblox", "Solde"])

    with st.expander("👤 [ADMIN] Ajouter un nouveau conducteur"):
        with st.form("admin_add_driver"):
            new_discord = st.text_input("Nom Discord")
            new_roblox = st.text_input("Nom Roblox")
            new_pts = st.number_input("Points", 0, 25, 25)
            admin_code = st.text_input("Code Admin requis", type="password")
            
            if st.form_submit_button("Créer le dossier"):
                if admin_code == CODE_ADMIN_GENERAL:
                    if new_roblox:
                        # 1. Créer le permis
                        val_label = "VALIDE" if new_pts >= 14 else ("OUI" if new_pts >= 1 else "NON")
                        new_driver = pd.DataFrame([{"Nom Discord": new_discord, "Nom Roblox": new_roblox, "PTS": new_pts, "Validité": val_label}])
                        conn.update(worksheet=nom_feuille_pts, data=pd.concat([df_pts, new_driver], ignore_index=True))
                        
                        # 2. Créer le compte bancaire si inexistant
                        if not (new_roblox.lower() in df_bank["Nom Roblox"].str.lower().values):
                            new_acc = pd.DataFrame([{"Nom Roblox": new_roblox, "Solde": 15000.0}])
                            conn.update(worksheet=nom_feuille_banque, data=pd.concat([df_bank, new_acc], ignore_index=True))
                        
                        log_action("Création Dossier + Banque", new_roblox)
                        st.success(f"Dossier et Banque créés pour {new_roblox} !")
                        time.sleep(1); st.rerun()
                else: st.error("❌ Code Admin incorrect.")

    # ... (Le reste de la recherche et modification reste avec log_action ajouté) ...
    st.divider()
    search_p = st.text_input("🔍 Rechercher Conducteur").strip()
    if not df_pts.empty and search_p:
        res = df_pts[df_pts["Nom Roblox"].astype(str).str.contains(search_p, case=False, na=False)]
        for idx, row in res.iterrows():
            st.markdown(f"### 👤 {row.get('Nom Roblox')}")
            pts_actuels = int(row.get("PTS", 0))
            
            c_mod, c_del = st.columns(2)
            with c_mod:
                with st.form(key=f"mod_{idx}"):
                    a = st.text_input("Code Admin", type="password")
                    nb = st.number_input("Points", 1, 25, 1)
                    if st.form_submit_button("Appliquer") and a == CODE_ADMIN_GENERAL:
                        df_pts.at[idx, "PTS"] = nb # Exemple simplifié
                        conn.update(worksheet=nom_feuille_pts, data=df_pts)
                        log_action(f"Modif Points ({nb})", row.get('Nom Roblox'))
                        st.rerun()

            with c_del:
                if st.button(f"🗑️ Supprimer", key=f"pre_del_{idx}"):
                    st.session_state[f"confirm_delete_{idx}"] = True
                if st.session_state.get(f"confirm_delete_{idx}", False):
                    d_code = st.text_input("Confirmer Code", type="password", key=f"code_del_{idx}")
                    if st.button("CONFIRMER", key=f"real_del_{idx}") and d_code == CODE_ADMIN_GENERAL:
                        log_action("Suppression Profil", row.get('Nom Roblox'))
                        conn.update(worksheet=nom_feuille_pts, data=df_pts.drop(idx))
                        st.session_state[f"confirm_delete_{idx}"] = False
                        st.rerun()

# ==========================================
# ONGLET 3 : BANQUE (NETTOYÉ)
# ==========================================
with tabs[2]:
    st.subheader("💰 Banque Centrale")
    try:
        df_bank = conn.read(worksheet="Banque", ttl=0)
    except: df_bank = pd.DataFrame()

    st.info("ℹ️ Les comptes sont créés automatiquement lors de l'enregistrement au permis.")
    
    search_b = st.text_input("🔍 Rechercher solde").strip()
    if not df_bank.empty and search_b:
        res_b = df_bank[df_bank["Nom Roblox"].astype(str).str.contains(search_b, case=False, na=False)]
        for idx, row in res_b.iterrows():
            solde = float(row.get("Solde", 0))
            st.metric(row.get('Nom Roblox'), f"{solde:,.0f} $")
            
            with st.form(key=f"f_bank_{idx}"):
                a_b = st.text_input("Code Admin", type="password")
                m_b = st.number_input("Montant", min_value=0.0)
                if st.form_submit_button("Valider Transaction") and a_b == CODE_ADMIN_GENERAL:
                    df_bank.at[idx, "Solde"] = solde + m_b # Pour l'exemple
                    conn.update(worksheet="Banque", data=df_bank)
                    log_action(f"Transaction Banque ({m_b})", row.get('Nom Roblox'))
                    st.rerun()

# ==========================================
# ONGLET 4 : LOGS
# ==========================================
with tabs[3]:
    st.subheader("📜 Historique des actions Admin")
    try:
        df_logs = conn.read(worksheet="Logs", ttl=0)
        st.dataframe(df_logs.sort_index(ascending=False), use_container_width=True)
    except:
        st.write("Aucun log disponible. Créez la feuille 'Logs' dans votre Google Sheets.")

st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 12px;'>Version v4.5 - Auto-Bank & Logs</div>", unsafe_allow_html=True)
