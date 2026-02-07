import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Fichier Central & Banque v8.2", layout="wide")

# --- LOGO ET TITRE ---
st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=697f2cf3&is=697ddb73&hm=dccb2edf0897deb4ccbdee22b3221134415bfed15b2cc808e439232c6f18bcab&", width=200)
st.title("🚓 Fichier Central & 🏦 Banque")

# --- CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26"

# --- LISTES COMPLÈTES (40 ÉTATS & 28 MARQUES) ---
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])
liste_marques = sorted(["Altstadt", "Bremen", "Bellicose", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])
liste_assurances = ["Non assuré", "RCT", "Averis"]

# --- FONCTION DE LECTURE FORCÉE ---
def get_data(sheet_name):
    st.cache_data.clear() # On vide le cache pour éviter le bug d'affichage
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

def log_action(admin_name, action, cible):
    try:
        df_logs = get_data("Logs")
        new_log = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Admin": str(admin_name), "Action": str(action), "Cible": str(cible)}])
        conn.update(worksheet="Logs", data=pd.concat([df_logs, new_log], ignore_index=True))
    except: pass

# --- NAVIGATION ---
tabs = st.tabs(["🚗 Immatriculations", "🪪 Points de Permis", "💰 Banque", "📜 Logs"])

# ==========================================
# 🚗 ONGLET 1 : IMMATRICULATIONS
# ==========================================
with tabs[0]:
    nom_immat = "Copie de Immatriculations"
    df_immat = get_data(nom_immat)
    
    with st.expander("➕ Enregistrer un nouveau véhicule"):
        with st.form("add_veh_v82"):
            u_reg = st.text_input("Pseudo Roblox")
            m_reg = st.selectbox("Marque du véhicule", liste_marques)
            e_reg = st.selectbox("État de la plaque", liste_etats)
            p_reg = st.text_input("Numéro de la plaque")
            a_reg = st.selectbox("Assurance", liste_assurances)
            c_reg = st.text_input("Code secret véhicule", type="password")
            if st.form_submit_button("Valider"):
                if u_reg and p_reg and c_reg:
                    fresh = get_data(nom_immat)
                    new_row = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u_reg, "Marque du véhicule": m_reg, "L'état de la plaque": e_reg, "Numéro de la plaque": p_reg, "Assurance": a_reg, "CODE": str(c_reg)}])
                    conn.update(worksheet=nom_immat, data=pd.concat([fresh, new_row], ignore_index=True))
                    log_action(u_reg, "Immatriculation", p_reg)
                    st.success("Enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    sq = st.text_input("🔍 Rechercher une plaque, un citoyen ou une marque").strip().upper()
    if not df_immat.empty:
        mask = df_immat.apply(lambda r: sq in str(r).upper(), axis=1) if sq else [True]*len(df_immat)
        for idx, row in df_immat[mask].iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 2])
                c1.markdown(f"### 🚗 {row['Numéro de la plaque']} — **{row['Marque du véhicule']}**")
                c1.write(f"👤 **{row['Nom d\'utilisateur ROBLOX']}** | 📍 **{row['L\'état de la plaque']}**")
                c1.write(f"🛡️ **Assurance :** {row['Assurance']}")
                
                # BOUTONS RESTAURÉS
                if c2.button(f"✏️ Modifier", key=f"edit_btn_{idx}"): st.session_state[f"em_{idx}"] = True
                if c2.button(f"🗑️ Supprimer", key=f"del_btn_{idx}"): st.session_state[f"dm_{idx}"] = True

                # FORMULAIRE DE MODIFICATION
                if st.session_state.get(f"em_{idx}"):
                    with st.form(f"fe_{idx}"):
                        np = st.text_input("Plaque", value=row['Numéro de la plaque'])
                        na = st.selectbox("Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']))
                        v_c = st.text_input("Code secret", type="password")
                        if st.form_submit_button("Sauvegarder"):
                            if v_c == str(row['CODE']):
                                # On modifie la ligne dans le DataFrame actuel
                                df_immat.at[idx, 'Numéro de la plaque'] = np
                                df_immat.at[idx, 'Assurance'] = na
                                conn.update(worksheet=nom_immat, data=df_immat)
                                st.success("Mis à jour !"); time.sleep(1); st.rerun()
                            else: st.error("Code incorrect")
                        if st.form_submit_button("Annuler"): st.session_state[f"em_{idx}"] = False; st.rerun()

                # FORMULAIRE DE SUPPRESSION SÉCURISÉ
                if st.session_state.get(f"dm_{idx}"):
                    with st.form(f"fd_{idx}"):
                        st.error("⚠️ Supprimer ce véhicule ?")
                        v_cd = st.text_input("Entrez le code secret", type="password")
                        if st.form_submit_button("CONFIRMER"):
                            if v_cd == str(row['CODE']):
                                fresh_check = get_data(nom_immat)
                                if len(fresh_check) > 0:
                                    updated = fresh_check[fresh_check['Numéro de la plaque'] != row['Numéro de la plaque']]
                                    # Sécurité ultime anti-wipe
                                    if len(updated) == 0 and len(fresh_check) > 1:
                                        st.error("Action bloquée : risque d'effacement total.")
                                    else:
                                        conn.update(worksheet=nom_immat, data=updated)
                                        st.success("Supprimé !"); time.sleep(1); st.rerun()
                            else: st.error("Code incorrect")

# ==========================================
# 🪪 ONGLET 2 : POINTS DE PERMIS (COMPLET)
# ==========================================
with tabs[1]:
    df_pts = get_data("Points Permis")
    with st.expander("👤 [ADMIN] Créer un dossier"):
        with st.form("form_pts_full"):
            adm = st.text_input("Admin responsable"); rob = st.text_input("Pseudo Roblox"); disc = st.text_input("Discord")
            pts = st.number_input("Points", 0, 25, 25); code = st.text_input("Code Admin", type="password")
            if st.form_submit_button("Créer"):
                if code == CODE_ADMIN_GENERAL and rob:
                    val = "VALIDE" if pts >= 14 else ("OUI" if pts >= 1 else "NON")
                    new_p = pd.DataFrame([{"Nom Discord": disc, "Nom Roblox": rob, "PTS": pts, "Validité": val}])
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_p], ignore_index=True))
                    # Banque automatique (15 000$)
                    df_b = get_data("Banque")
                    new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": disc, "Nom Roblox": rob, "Pseudo Admin": adm}])
                    conn.update(worksheet="Banque", data=pd.concat([df_b, new_b], ignore_index=True))
                    st.success("Dossier & Banque créés !"); time.sleep(1); st.rerun()

    st.divider()
    search_p = st.text_input("🔍 Rechercher un conducteur").strip().lower()
    if not df_pts.empty and search_p:
        res_p = df_pts[df_pts.apply(lambda r: search_p in str(r).lower(), axis=1)]
        for idx, row in res_p.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"### 👤 {row['Nom Roblox']} (@{row['Nom Discord']})")
                c1.write(f"État : **{row['Validité']}**")
                c2.metric("Points", f"{int(row['PTS'])}/25")
                with st.expander("⚙️ Gérer les points"):
                    with st.form(key=f"p_e_{idx}"):
                        a_p = st.text_input("Admin"); c_p = st.text_input("Code", type="password")
                        nv_pts = st.number_input("Points", 0, 25, int(row['PTS']))
                        if st.form_submit_button("Sauvegarder"):
                            if c_p == CODE_ADMIN_GENERAL:
                                df_pts.at[idx, "PTS"] = nv_pts
                                df_pts.at[idx, "Validité"] = "VALIDE" if nv_pts >= 14 else ("OUI" if nv_pts >= 1 else "NON")
                                conn.update(worksheet="Points Permis", data=df_pts)
                                st.success("Points mis à jour !"); time.sleep(1); st.rerun()

# ==========================================
# 💰 ONGLET 3 : BANQUE (COMPLET)
# ==========================================
with tabs[2]:
    df_bank = get_data("Banque")
    sb = st.text_input("🔍 Rechercher un compte bancaire").strip().lower()
    if not df_bank.empty and sb:
        res_b = df_bank[df_bank.apply(lambda r: sb in str(r).lower(), axis=1)]
        for idx, row in res_b.iterrows():
            solde = float(row.get('Solde', 0))
            st.metric(f"👤 {row['Nom Roblox']}", f"{solde:,.0f} $")
            with st.expander("🛡️ Transaction"):
                with st.form(f"bank_v82_{idx}"):
                    ad_b = st.text_input("Admin"); c_b = st.text_input("Code Admin", type="password")
                    mnt = st.number_input("Montant", step=100.0)
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("📉 Retirer"):
                        if c_b == CODE_ADMIN_GENERAL:
                            df_bank.at[idx, "Solde"] = solde - mnt
                            conn.update(worksheet="Banque", data=df_bank)
                            st.success("Retrait OK !"); time.sleep(1); st.rerun()
                    if col2.form_submit_button("📈 Ajouter"):
                        if c_b == CODE_ADMIN_GENERAL:
                            df_bank.at[idx, "Solde"] = solde + mnt
                            conn.update(worksheet="Banque", data=df_bank)
                            st.success("Ajout OK !"); time.sleep(1); st.rerun()

# ==========================================
# 📜 ONGLET 4 : LOGS (COMPLET)
# ==========================================
with tabs[3]:
    if st.text_input("Code d'accès Logs", type="password") == CODE_ADMIN_GENERAL:
        st.dataframe(get_data("Logs").iloc[::-1], use_container_width=True)

st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 10px;'>Version 8.2 Finale - Full Features & Modifier Bouton</div>", unsafe_allow_html=True)
