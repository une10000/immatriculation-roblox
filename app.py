import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="RCRP - Fichier Central", layout="wide")

# --- LOGO ET TITRE ---
st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=697f2cf3&is=697ddb73&hm=dccb2edf0897deb4ccbdee22b3221134415bfed15b2cc808e439232c6f18bcab&", width=200)
st.title("🚓 Fichier Central & 🏦 Banque")

# --- CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26"

# --- LISTES COMPLÈTES (RÉTABLIES) ---
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])
liste_assurances = ["Non assuré", "RCT", "Averis"]

# --- FONCTIONS DE SÉCURITÉ ---
def safe_read(sheet_name):
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

def log_action(admin_name, action, cible):
    try:
        df_logs = safe_read("Logs")
        new_log = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Admin": str(admin_name), "Action": str(action), "Cible": str(cible)}])
        conn.update(worksheet="Logs", data=pd.concat([df_logs, new_log], ignore_index=True))
    except: pass

# --- NAVIGATION ---
tabs = st.tabs(["🚗 Immatriculations", "🪪 Points de Permis", "💰 Banque", "📜 Logs"])

# ==========================================
# 🚗 ONGLET 1 : IMMATRICULATIONS (VERSION COMPLÈTE)
# ==========================================
with tabs[0]:
    nom_feuille_immat = "Copie de Immatriculations"
    df_immat = safe_read(nom_feuille_immat)
    
    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("inscription_full"):
            u_reg = st.text_input("Nom d'utilisateur ROBLOX")
            m_reg = st.selectbox("Marque du véhicule", liste_marques)
            e_reg = st.selectbox("État", liste_etats)
            p_reg = st.text_input("Numéro de la plaque")
            a_reg = st.selectbox("Assurance", liste_assurances)
            c_reg = st.text_input("Code secret véhicule (pour modifier/supprimer)", type="password")
            
            if st.form_submit_button("Valider l'enregistrement"):
                if u_reg and p_reg and c_reg:
                    # On reprend la version la plus récente pour éviter d'écraser
                    fresh_df = safe_read(nom_feuille_immat)
                    new_row = pd.DataFrame([{
                        "Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"),
                        "Nom d'utilisateur ROBLOX": u_reg,
                        "Marque du véhicule": m_reg,
                        "L'état de la plaque": e_reg,
                        "Numéro de la plaque": p_reg,
                        "Assurance": a_reg,
                        "CODE": str(c_reg)
                    }])
                    conn.update(worksheet=nom_feuille_immat, data=pd.concat([fresh_df, new_row], ignore_index=True))
                    log_action(u_reg, "Immatriculation", p_reg)
                    st.success(f"✅ Véhicule {p_reg} enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    sq = st.text_input("🔍 Rechercher une plaque ou un citoyen").strip().upper()
    if not df_immat.empty:
        mask = df_immat.apply(lambda r: sq in str(r).upper(), axis=1) if sq else [True]*len(df_immat)
        res_immat = df_immat[mask]
        
        for idx, row in res_immat.iterrows():
            with st.container(border=True):
                c_i, c_a = st.columns([3, 2])
                c_i.markdown(f"### 🚗 {row['Numéro de la plaque']}")
                c_i.write(f"👤 Propriétaire : **{row['Nom d\'utilisateur ROBLOX']}**")
                c_i.write(f"📍 État : {row.get('L\'état de la plaque', 'N/A')} | 🏷️ Marque : {row.get('Marque du véhicule', 'N/A')} | 🛡️ {row['Assurance']}")
                
                if c_a.button(f"✏️ Modifier", key=f"edit_veh_{idx}", use_container_width=True): st.session_state[f"mode_edit_{idx}"] = True
                if c_a.button(f"🗑️ Supprimer", key=f"del_veh_{idx}", use_container_width=True): st.session_state[f"mode_del_{idx}"] = True

                if st.session_state.get(f"mode_edit_{idx}"):
                    with st.form(f"f_edit_v_{idx}"):
                        new_p = st.text_input("Plaque", value=row['Numéro de la plaque'])
                        new_a = st.selectbox("Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']))
                        v_cod = st.text_input("Code secret", type="password")
                        if st.form_submit_button("Sauvegarder"):
                            if v_cod == str(row['CODE']):
                                df_immat.at[idx, 'Numéro de la plaque'] = new_p
                                df_immat.at[idx, 'Assurance'] = new_a
                                conn.update(worksheet=nom_feuille_immat, data=df_immat)
                                st.success("Modifié !"); time.sleep(0.5); st.rerun()
                            else: st.error("Code faux")

                if st.session_state.get(f"mode_del_{idx}"):
                    with st.form(f"f_del_v_{idx}"):
                        st.error("Supprimer ce véhicule ?")
                        v_cod_d = st.text_input("Code secret", type="password")
                        if st.form_submit_button("OUI, SUPPRIMER"):
                            if v_cod_d == str(row['CODE']):
                                conn.update(worksheet=nom_feuille_immat, data=df_immat.drop(idx))
                                st.success("Supprimé"); time.sleep(0.5); st.rerun()

# ==========================================
# 🪪 ONGLET 2 : POINTS DE PERMIS (COMPLET)
# ==========================================
with tabs[1]:
    df_pts = safe_read("Points Permis")
    with st.expander("👤 [ADMIN] Créer un dossier conducteur"):
        st.info("💡 **INFO ADMIN :** L'argent (15'000$) se met automatiquement dans la banque.")
        with st.form("add_p_final"):
            a_n = st.text_input("Nom Admin"); r_n = st.text_input("Nom Roblox"); d_n = st.text_input("Nom Discord")
            p_v = st.number_input("Points", 0, 25, 25); c_a = st.text_input("Code Admin", type="password")
            if st.form_submit_button("Créer le dossier"):
                if c_a == CODE_ADMIN_GENERAL and r_n:
                    valid = "VALIDE" if p_v >= 14 else ("OUI" if p_v >= 1 else "NON")
                    new_p = pd.DataFrame([{"Nom Discord": d_n, "Nom Roblox": r_n, "PTS": p_v, "Validité": valid}])
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_p], ignore_index=True))
                    # Création Banque auto
                    df_b = safe_read("Banque")
                    new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": d_n, "Nom Roblox": r_n, "Pseudo Admin": a_n}])
                    conn.update(worksheet="Banque", data=pd.concat([df_b, new_b], ignore_index=True))
                    log_action(a_n, "Nouveau Dossier", r_n); st.success("Dossier créé !"); time.sleep(1); st.rerun()

    st.divider()
    search_p = st.text_input("🔍 Rechercher un conducteur (Roblox/Discord)").strip().lower()
    if not df_pts.empty and search_p:
        res_p = df_pts[df_pts.apply(lambda r: search_p in str(r).lower(), axis=1)]
        for idx, row in res_p.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"### 👤 {row['Nom Roblox']} (@{row['Nom Discord']})")
                c1.write(f"État : **{row['Validité']}**")
                c2.metric("Points", f"{int(row['PTS'])}/25")
                with st.expander("⚙️ Modifier / Supprimer"):
                    with st.form(key=f"edit_p_v72_{idx}"):
                        ad = st.text_input("Admin"); cd = st.text_input("Code Admin", type="password")
                        nv_pts = st.number_input("Points", 0, 25, int(row['PTS']))
                        if st.form_submit_button("✅ Sauvegarder"):
                            if cd == CODE_ADMIN_GENERAL:
                                df_pts.at[idx, "PTS"] = nv_pts
                                df_pts.at[idx, "Validité"] = "VALIDE" if nv_pts >= 14 else ("OUI" if nv_pts >= 1 else "NON")
                                conn.update(worksheet="Points Permis", data=df_pts)
                                log_action(ad, f"Points -> {nv_pts}", row['Nom Roblox']); st.rerun()
                        if st.form_submit_button("🗑️ Supprimer"):
                            if cd == CODE_ADMIN_GENERAL:
                                conn.update(worksheet="Points Permis", data=df_pts.drop(idx))
                                st.rerun()

# ==========================================
# 💰 ONGLET 3 : BANQUE (COMPLET)
# ==========================================
with tabs[2]:
    st.subheader("💰 Banque Centrale")
    df_bank = safe_read("Banque")
    sb = st.text_input("🔍 Rechercher un compte (Nom/Discord)").strip().lower()
    if not df_bank.empty and sb:
        res_b = df_bank[df_bank.apply(lambda r: sb in str(r).lower(), axis=1)]
        for idx, row in res_b.iterrows():
            s_val = float(row.get('Solde', 0))
            st.metric(f"👤 {row['Nom Roblox']}", f"{s_val:,.0f} $")
            with st.expander("🛡️ Transaction"):
                with st.form(f"tr_v72_{idx}"):
                    a_b = st.text_input("Nom de l'Admin"); c_b = st.text_input("Code ADMIN", type="password")
                    mnt = st.number_input("Montant", step=500.0)
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("📉 Retirer") and c_b == CODE_ADMIN_GENERAL:
                        df_bank.at[idx, "Solde"] = s_val - mnt
                        conn.update(worksheet="Banque", data=df_bank)
                        log_action(a_b, f"Retrait {mnt}", row['Nom Roblox']); st.rerun()
                    if col2.form_submit_button("📈 Ajouter") and c_b == CODE_ADMIN_GENERAL:
                        df_bank.at[idx, "Solde"] = s_val + mnt
                        conn.update(worksheet="Banque", data=df_bank)
                        log_action(a_b, f"Ajout {mnt}", row['Nom Roblox']); st.rerun()

# ==========================================
# 📜 ONGLET 4 : LOGS
# ==========================================
with tabs[3]:
    pwd = st.text_input("Code Logs", type="password")
    if pwd == CODE_ADMIN_GENERAL:
        st.dataframe(safe_read("Logs").iloc[::-1], use_container_width=True)

st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 12px;'>Version v7.2 - Full Features Restored</div>", unsafe_allow_html=True)
