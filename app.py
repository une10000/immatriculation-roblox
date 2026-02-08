import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Système Intégral v8.9", layout="wide")

# --- LOGO ET TITRE ---
st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=697f2cf3&is=697ddb73&hm=dccb2edf0897deb4ccbdee22b3221134415bfed15b2cc808e439232c6f18bcab&", width=200)
st.title("🚓 Fichier Central & 🏦 Banque RCT")

# --- PARAMÈTRES ET CODES ---
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26" 
CODE_ENTREPRISE = "RCT-26-RCRPFR" 
MON_PSEUDO_ROBLOX = "une10000"

# --- LISTES ---
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])
liste_assurances = ["Non assuré", "RCT", "Averis"]

# --- FONCTION LECTURE ---
def get_data(sheet_name):
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

def log_action(admin, action, cible):
    try:
        df_l = get_data("Logs")
        new_l = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Admin": str(admin), "Action": str(action), "Cible": str(cible)}])
        conn.update(worksheet="Logs", data=pd.concat([df_l, new_l], ignore_index=True))
    except: pass

# --- NAVIGATION ---
tabs = st.tabs(["🚗 Immatriculations", "🪪 Points de Permis", "💰 Banque & RCT", "📜 Logs"])

# ==========================================
# 🚗 ONGLET 1 : IMMATRICULATIONS
# ==========================================
with tabs[0]:
    nom_im = "Copie de Immatriculations"
    df_immat = get_data(nom_im)
    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("f_add"):
            u = st.text_input("Pseudo Roblox"); m = st.selectbox("Marque", liste_marques)
            e = st.selectbox("État", liste_etats); p = st.text_input("Plaque")
            a = st.selectbox("Assurance", liste_assurances); c = st.text_input("Code secret véhicule", type="password")
            if st.form_submit_button("Valider"):
                if u and p and c:
                    fresh = get_data(nom_im)
                    new_r = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "L'état de la plaque": e, "Numéro de la plaque": p, "Assurance": a, "CODE": str(c)}])
                    conn.update(worksheet=nom_im, data=pd.concat([fresh, new_r], ignore_index=True))
                    log_action(u, "Immatriculation", p); st.success("OK !"); time.sleep(1); st.rerun()

    st.divider()
    sq = st.text_input("🔍 Rechercher (Plaque, Nom, Marque)").strip().upper()
    if not df_immat.empty:
        mask = df_immat.apply(lambda r: sq in str(r).upper(), axis=1) if sq else [True]*len(df_immat)
        for idx, row in df_immat[mask].iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 2])
                c1.markdown(f"### 🚗 {row['Numéro de la plaque']} — **{row['Marque du véhicule']}**")
                c1.write(f"👤 **{row['Nom d\'utilisateur ROBLOX']}** | 📍 **{row['L\'état de la plaque']}**")
                
                b1, b2 = c2.columns(2)
                if b1.button(f"✏️ Modifier", key=f"e_{idx}"): st.session_state[f"edit_{idx}"] = True
                if b2.button(f"🗑️ Supprimer", key=f"d_{idx}"): st.session_state[f"del_{idx}"] = True

                if st.session_state.get(f"edit_{idx}"):
                    with st.form(f"fe_{idx}"):
                        np = st.text_input("Plaque", value=row['Numéro de la plaque'])
                        na = st.selectbox("Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']))
                        vc = st.text_input("Code secret", type="password")
                        if st.form_submit_button("Sauvegarder"):
                            if vc == str(row['CODE']):
                                df_immat.at[idx, 'Numéro de la plaque'] = np
                                df_immat.at[idx, 'Assurance'] = na
                                conn.update(worksheet=nom_im, data=df_immat)
                                st.success("Mis à jour !"); time.sleep(1); st.rerun()
                        if st.form_submit_button("Annuler"): st.session_state[f"edit_{idx}"] = False; st.rerun()

                if st.session_state.get(f"del_{idx}"):
                    with st.form(f"fd_{idx}"):
                        vcd = st.text_input("Code secret", type="password")
                        if st.form_submit_button("CONFIRMER"):
                            if vcd == str(row['CODE']):
                                fresh_c = get_data(nom_im)
                                updated = fresh_c[fresh_c['Numéro de la plaque'] != row['Numéro de la plaque']]
                                conn.update(worksheet=nom_im, data=updated)
                                st.success("Supprimé"); time.sleep(1); st.rerun()

# ==========================================
# 🪪 ONGLET 2 : POINTS DE PERMIS
# ==========================================
with tabs[1]:
    df_pts = get_data("Points Permis")
    with st.expander("👤 Créer un dossier"):
        with st.form("f_pts"):
            adm = st.text_input("Admin"); rob = st.text_input("Roblox"); disc = st.text_input("Discord")
            pts_i = st.number_input("Points", 0, 25, 25); c_a = st.text_input("Code Admin", type="password")
            if st.form_submit_button("Créer"):
                if c_a == CODE_ADMIN_GENERAL:
                    v = "VALIDE" if pts_i >= 14 else ("OUI" if pts_i >= 1 else "NON")
                    new_p = pd.DataFrame([{"Nom Discord": disc, "Nom Roblox": rob, "PTS": pts_i, "Validité": v}])
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_p], ignore_index=True))
                    # Banque 15k
                    df_b = get_data("Banque")
                    new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": disc, "Nom Roblox": rob, "Pseudo Admin": adm}])
                    conn.update(worksheet="Banque", data=pd.concat([df_b, new_b], ignore_index=True))
                    st.success("Dossier & 15k créés !"); time.sleep(1); st.rerun()

    st.divider()
    sp = st.text_input("🔍 Rechercher conducteur").strip().lower()
    if not df_pts.empty and sp:
        res_p = df_pts[df_pts.apply(lambda r: sp in str(r).lower(), axis=1)]
        for idx, row in res_p.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"### {row['Nom Roblox']} | {row['Validité']}")
                c2.metric("Points", f"{int(row['PTS'])}")
                with st.expander("Modifier points"):
                    with st.form(f"fp_{idx}"):
                        nv = st.number_input("Nouveau solde", 0, 25, int(row['PTS']))
                        ca = st.text_input("Code Admin", type="password")
                        if st.form_submit_button("OK"):
                            if ca == CODE_ADMIN_GENERAL:
                                df_pts.at[idx, "PTS"] = nv
                                df_pts.at[idx, "Validité"] = "VALIDE" if nv >= 14 else ("OUI" if nv >= 1 else "NON")
                                conn.update(worksheet="Points Permis", data=df_pts)
                                st.success("Points mis à jour !"); time.sleep(1); st.rerun()

# ==========================================
# 💰 ONGLET 3 : BANQUE & RCT
# ==========================================
with tabs[2]:
    df_bank = get_data("Banque")
    sb = st.text_input("🔍 Rechercher compte").strip().lower()
    if not df_bank.empty and sb:
        res_b = df_bank[df_bank.apply(lambda r: sb in str(r).lower(), axis=1)]
        for idx, row in res_b.iterrows():
            solde = float(row.get('Solde', 0))
            st.metric(f"👤 {row['Nom Roblox']}", f"{solde:,.0f} $")
            with st.expander("Opération"):
                with st.form(f"fb_{idx}"):
                    code = st.text_input("Code", type="password"); mnt = st.number_input("Montant", step=100.0)
                    c_ret, c_aj = st.columns(2)
                    if c_ret.form_submit_button("📉 Retirer / Facturer"):
                        if code == CODE_ENTREPRISE: # RCT
                            df_bank.at[idx, "Solde"] = solde - mnt
                            mask = df_bank['Nom Roblox'].str.lower() == MON_PSEUDO_ROBLOX.lower()
                            if mask.any():
                                im = df_bank[mask].index[0]
                                df_bank.at[im, "Solde"] = float(df_bank.at[im, "Solde"]) + mnt
                                conn.update(worksheet="Banque", data=df_bank)
                                st.success("Virement RCT OK !"); time.sleep(1); st.rerun()
                        elif code == CODE_ADMIN_GENERAL: # Police
                            df_bank.at[idx, "Solde"] = solde - mnt
                            conn.update(worksheet="Banque", data=df_bank)
                            st.success("Amende/Retrait OK !"); time.sleep(1); st.rerun()
                    if c_aj.form_submit_button("📈 Ajouter (Police)"):
                        if code == CODE_ADMIN_GENERAL:
                            df_bank.at[idx, "Solde"] = solde + mnt
                            conn.update(worksheet="Banque", data=df_bank)
                            st.success("Ajout OK !"); time.sleep(1); st.rerun()

# ==========================================
# 📜 ONGLET 4 : LOGS
# ==========================================
with tabs[3]:
    if st.text_input("Accès Logs", type="password") == CODE_ADMIN_GENERAL:
        st.dataframe(get_data("Logs").iloc[::-1], use_container_width=True)
