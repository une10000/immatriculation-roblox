import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="RCRP - Fichier Central v7.9", layout="wide")
st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=697f2cf3&is=697ddb73&hm=dccb2edf0897deb4ccbdee22b3221134415bfed15b2cc808e439232c6f18bcab&", width=200)

conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26"

# --- LISTES ---
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])

# --- FONCTION DE LECTURE ---
def safe_read(sheet_name):
    try:
        data = conn.read(worksheet=sheet_name, ttl=0) # ttl=0 pour forcer la lecture réelle
        if data is None: return pd.DataFrame()
        return data.dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

# --- NAVIGATION ---
tabs = st.tabs(["🚗 Immatriculations", "🪪 Points de Permis", "💰 Banque", "📜 Logs"])

# ==========================================
# 🚗 ONGLET 1 : IMMATRICULATIONS
# ==========================================
with tabs[0]:
    nom_immat = "Copie de Immatriculations"
    df_immat = safe_read(nom_immat)
    
    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("form_v79"):
            u = st.text_input("Pseudo Roblox"); m = st.selectbox("Marque", liste_marques)
            e = st.selectbox("État", liste_etats); p = st.text_input("Plaque")
            a = st.selectbox("Assurance", ["Non assuré", "RCT", "Averis"]); c = st.text_input("Code secret", type="password")
            if st.form_submit_button("Valider"):
                if u and p and c:
                    fresh = safe_read(nom_immat)
                    new_row = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "L'état de la plaque": e, "Numéro de la plaque": p, "Assurance": a, "CODE": str(c)}])
                    conn.update(worksheet=nom_immat, data=pd.concat([fresh, new_row], ignore_index=True))
                    st.success("Enregistré ! Voir la liste ci-dessous.")
                    time.sleep(1)
                    st.rerun() # Rafraîchissement immédiat

    st.divider()
    sq = st.text_input("🔍 Rechercher une plaque, un citoyen ou une marque").strip().upper()
    if not df_immat.empty:
        mask = df_immat.apply(lambda r: sq in str(r).upper(), axis=1) if sq else [True]*len(df_immat)
        res = df_immat[mask]
        
        for idx, row in res.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 2])
                # AJOUT DE LA MARQUE ICI :
                c1.markdown(f"### 🚗 {row['Numéro de la plaque']} — **{row['Marque du véhicule']}**")
                c1.write(f"👤 **Propriétaire :** {row['Nom d\'utilisateur ROBLOX']} | 📍 **État :** {row['L\'état de la plaque']}")
                c1.write(f"🛡️ **Assurance :** {row['Assurance']}")
                
                if c2.button(f"🗑️ Supprimer", key=f"del_{idx}"):
                    st.session_state[f"confirm_{idx}"] = True
                
                if st.session_state.get(f"confirm_{idx}"):
                    v_c = st.text_input("Code secret du véhicule", type="password", key=f"v_{idx}")
                    if st.button("Confirmer la suppression", key=f"b_{idx}"):
                        if v_c == str(row['CODE']):
                            # SÉCURITÉ : Lecture fraîche pour éviter le wipe
                            check_df = safe_read(nom_immat)
                            if not check_df.empty:
                                updated = check_df[check_df['Numéro de la plaque'] != row['Numéro de la plaque']]
                                conn.update(worksheet=nom_immat, data=updated)
                                st.success("Véhicule supprimé. Rechargement...")
                                time.sleep(1)
                                # L'ASTUCE : On vide le cache et on force le rerun
                                st.rerun() 
                        else:
                            st.error("Code secret incorrect.")
                    if st.button("Annuler", key=f"ann_{idx}"):
                        st.session_state[f"confirm_{idx}"] = False
                        st.rerun()

# ==========================================
# 🪪 ONGLET 2 : POINTS DE PERMIS
# ==========================================
with tabs[1]:
    df_pts = safe_read("Points Permis")
    with st.expander("👤 [ADMIN] Créer un dossier"):
        with st.form("form_pts_v77"):
            adm = st.text_input("Admin"); rob = st.text_input("Roblox"); disc = st.text_input("Discord")
            pts = st.number_input("Points", 0, 25, 25); code = st.text_input("Code Admin", type="password")
            if st.form_submit_button("Créer"):
                if code == CODE_ADMIN_GENERAL and rob:
                    val = "VALIDE" if pts >= 14 else ("OUI" if pts >= 1 else "NON")
                    new_p = pd.DataFrame([{"Nom Discord": disc, "Nom Roblox": rob, "PTS": pts, "Validité": val}])
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_p], ignore_index=True))
                    # Banque automatique
                    df_b = safe_read("Banque")
                    new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": disc, "Nom Roblox": rob, "Pseudo Admin": adm}])
                    conn.update(worksheet="Banque", data=pd.concat([df_b, new_b], ignore_index=True))
                    log_action(adm, "Nouveau Permis", rob); st.success("OK !"); time.sleep(1); st.rerun()

    st.divider()
    search_p = st.text_input("🔍 Chercher un conducteur").strip().lower()
    if not df_pts.empty and search_p:
        res_p = df_pts[df_pts.apply(lambda r: search_p in str(r).lower(), axis=1)]
        for idx, row in res_p.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"### 👤 {row['Nom Roblox']} (@{row['Nom Discord']})")
                c2.metric("Points", f"{int(row['PTS'])}/25")
                with st.expander("⚙️ Gérer"):
                    with st.form(key=f"p_e_{idx}"):
                        a_p = st.text_input("Admin"); c_p = st.text_input("Code", type="password")
                        nv = st.number_input("Points", 0, 25, int(row['PTS']))
                        if st.form_submit_button("Mettre à jour"):
                            if c_p == CODE_ADMIN_GENERAL:
                                df_pts.at[idx, "PTS"] = nv
                                df_pts.at[idx, "Validité"] = "VALIDE" if nv >= 14 else ("OUI" if nv >= 1 else "NON")
                                conn.update(worksheet="Points Permis", data=df_pts)
                                log_action(a_p, f"Points {nv}", row['Nom Roblox']); st.rerun()

# ==========================================
# 💰 ONGLET 3 : BANQUE
# ==========================================
with tabs[2]:
    df_bank = safe_read("Banque")
    sb = st.text_input("🔍 Chercher un compte").strip().lower()
    if not df_bank.empty and sb:
        res_b = df_bank[df_bank.apply(lambda r: sb in str(r).lower(), axis=1)]
        for idx, row in res_b.iterrows():
            solde = float(row.get('Solde', 0))
            st.metric(f"👤 {row['Nom Roblox']}", f"{solde:,.0f} $")
            with st.expander("🛡️ Transaction"):
                with st.form(f"b_t_{idx}"):
                    ad_b = st.text_input("Admin"); c_b = st.text_input("Code", type="password")
                    mnt = st.number_input("Montant", step=100.0)
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("📉 Retirer") and c_b == CODE_ADMIN_GENERAL:
                        df_bank.at[idx, "Solde"] = solde - mnt
                        conn.update(worksheet="Banque", data=df_bank)
                        log_action(ad_b, f"Retrait {mnt}", row['Nom Roblox']); st.rerun()
                    if col2.form_submit_button("📈 Ajouter") and c_b == CODE_ADMIN_GENERAL:
                        df_bank.at[idx, "Solde"] = solde + mnt
                        conn.update(worksheet="Banque", data=df_bank)
                        log_action(ad_b, f"Ajout {mnt}", row['Nom Roblox']); st.rerun()

# ==========================================
# 📜 ONGLET 4 : LOGS
# ==========================================
with tabs[3]:
    if st.text_input("Code Logs", type="password") == CODE_ADMIN_GENERAL:
        st.dataframe(safe_read("Logs").iloc[::-1], use_container_width=True)

st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 10px;'>Version 7.7 - Shield Active</div>", unsafe_allow_html=True)
