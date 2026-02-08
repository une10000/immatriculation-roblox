import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Système Central Complet", layout="wide")

# --- LOGO ET TITRE ---
st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=697f2cf3&is=697ddb73&hm=dccb2edf0897deb4ccbdee22b3221134415bfed15b2cc808e439232c6f18bcab&", width=200)
st.title("🚓 Fichier Central & 🏦 Banque RCT")

# --- PARAMÈTRES ET CODES ---
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26"
CODE_ENTREPRISE = "RCT-26-RCRPFR" 
MON_PSEUDO_ROBLOX = "une10000"

# --- LISTES COMPLÈTES (40 ÉTATS & 28 MARQUES) ---
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])
liste_assurances = ["Non assuré", "RCT", "Averis"]

# --- FONCTION LECTURE FORCÉE (ANTI-CACHE) ---
def get_data(sheet_name):
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

# --- FONCTION LOGS ---
def log_action(admin, action, cible):
    try:
        df_logs = get_data("Logs")
        new_log = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Admin": str(admin), "Action": str(action), "Cible": str(cible)}])
        conn.update(worksheet="Logs", data=pd.concat([df_logs, new_log], ignore_index=True))
    except: pass

# --- NAVIGATION ---
tabs = st.tabs(["🚗 Immatriculations", "🪪 Points de Permis", "💰 Banque & RCT Business", "📜 Logs"])

# ==========================================
# 🚗 ONGLET 1 : IMMATRICULATIONS
# ==========================================
with tabs[0]:
    nom_im = "Copie de Immatriculations"
    df_immat = get_data(nom_im)
    
    with st.expander("➕ Enregistrer un nouveau véhicule"):
        with st.form("add_full_v87"):
            u = st.text_input("Pseudo Roblox")
            m = st.selectbox("Marque du véhicule", liste_marques)
            e = st.selectbox("État de la plaque", liste_etats)
            p = st.text_input("Numéro de la plaque")
            a = st.selectbox("Assurance", liste_assurances)
            c = st.text_input("Code secret véhicule (pour modif/suppr)", type="password")
            if st.form_submit_button("Valider l'enregistrement"):
                if u and p and c:
                    fresh = get_data(nom_im)
                    new_row = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "L'état de la plaque": e, "Numéro de la plaque": p, "Assurance": a, "CODE": str(c)}])
                    conn.update(worksheet=nom_im, data=pd.concat([fresh, new_row], ignore_index=True))
                    log_action(u, "Immatriculation", p)
                    st.success("Véhicule enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    sq = st.text_input("🔍 Rechercher (Plaque, Nom, Marque)").strip().upper()
    if not df_immat.empty:
        mask = df_immat.apply(lambda r: sq in str(r).upper(), axis=1) if sq else [True]*len(df_immat)
        for idx, row in df_immat[mask].iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 2])
                c1.markdown(f"### 🚗 {row['Numéro de la plaque']} — **{row['Marque du véhicule']}**")
                c1.write(f"👤 **Propriétaire :** {row['Nom d\'utilisateur ROBLOX']} | 📍 **{row['L\'état de la plaque']}**")
                c1.write(f"🛡️ **Assurance :** {row['Assurance']}")
                
                # BOUTONS MODIFIER ET SUPPRIMER
                btn_col1, btn_col2 = c2.columns(2)
                if btn_col1.button(f"✏️ Modifier", key=f"edit_{idx}"): st.session_state[f"m_{idx}"] = True
                if btn_col2.button(f"🗑️ Supprimer", key=f"del_{idx}"): st.session_state[f"s_{idx}"] = True

                # FORMULAIRE MODIFIER
                if st.session_state.get(f"m_{idx}"):
                    with st.form(f"f_m_{idx}"):
                        new_p = st.text_input("Nouvelle Plaque", value=row['Numéro de la plaque'])
                        new_a = st.selectbox("Nouvelle Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']))
                        code_v = st.text_input("Code secret véhicule", type="password")
                        if st.form_submit_button("Sauvegarder"):
                            if code_v == str(row['CODE']):
                                df_immat.at[idx, 'Numéro de la plaque'] = new_p
                                df_immat.at[idx, 'Assurance'] = new_a
                                conn.update(worksheet=nom_im, data=df_immat)
                                log_action("SYSTÈME", "Modification", new_p)
                                st.success("Mis à jour !"); time.sleep(1); st.rerun()
                            else: st.error("Code incorrect")
                        if st.form_submit_button("Annuler"): st.session_state[f"m_{idx}"] = False; st.rerun()

                # FORMULAIRE SUPPRIMER
                if st.session_state.get(f"s_{idx}"):
                    with st.form(f"f_s_{idx}"):
                        st.error("⚠️ Supprimer définitivement ?")
                        code_s = st.text_input("Code secret véhicule", type="password")
                        if st.form_submit_button("CONFIRMER LA SUPPRESSION"):
                            if code_s == str(row['CODE']):
                                fresh_c = get_data(nom_im)
                                if not fresh_c.empty:
                                    updated = fresh_c[fresh_c['Numéro de la plaque'] != row['Numéro de la plaque']]
                                    conn.update(worksheet=nom_im, data=updated)
                                    log_action("SYSTÈME", "Suppression", row['Numéro de la plaque'])
                                    st.success("Supprimé !"); time.sleep(1); st.rerun()
                            else: st.error("Code incorrect")
                        if st.form_submit_button("Annuler"): st.session_state[f"s_{idx}"] = False; st.rerun()

# ==========================================
# 🪪 ONGLET 2 : POINTS DE PERMIS
# ==========================================
with tabs[1]:
    df_pts = get_data("Points Permis")
    with st.expander("👤 [ADMIN] Créer un nouveau dossier"):
        with st.form("form_pts_v87"):
            adm = st.text_input("Admin responsable"); rob = st.text_input("Pseudo Roblox"); disc = st.text_input("Discord (@)")
            pts_init = st.number_input("Points de départ", 0, 25, 25); c_adm = st.text_input("Code Admin Général", type="password")
            if st.form_submit_button("Créer dossier et compte"):
                if c_adm == CODE_ADMIN_GENERAL and rob:
                    v_p = "VALIDE" if pts_init >= 14 else ("OUI" if pts_init >= 1 else "NON")
                    new_p = pd.DataFrame([{"Nom Discord": disc, "Nom Roblox": rob, "PTS": pts_init, "Validité": v_p}])
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_p], ignore_index=True))
                    # Création Banque auto
                    df_b = get_data("Banque")
                    new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": disc, "Nom Roblox": rob, "Pseudo Admin": adm}])
                    conn.update(worksheet="Banque", data=pd.concat([df_b, new_b], ignore_index=True))
                    log_action(adm, "Nouveau Permis", rob); st.success("Dossier & 15k créés !"); time.sleep(1); st.rerun()

    st.divider()
    search_p = st.text_input("🔍 Rechercher un conducteur").strip().lower()
    if not df_pts.empty and search_p:
        res_p = df_pts[df_pts.apply(lambda r: search_p in str(r).lower(), axis=1)]
        for idx, row in res_p.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"### 👤 {row['Nom Roblox']} (@{row['Nom Discord']})")
                c1.write(f"État du permis : **{row['Validité']}**")
                c2.metric("Points", f"{int(row['PTS'])}/25")
                with st.expander("⚙️ Modifier points"):
                    with st.form(f"p_edit_{idx}"):
                        a_p = st.text_input("Admin"); cp = st.text_input("Code Admin", type="password")
                        nv_pts = st.number_input("Nouveau solde", 0, 25, int(row['PTS']))
                        if st.form_submit_button("Valider"):
                            if cp == CODE_ADMIN_GENERAL:
                                df_pts.at[idx, "PTS"] = nv_pts
                                df_pts.at[idx, "Validité"] = "VALIDE" if nv_pts >= 14 else ("OUI" if nv_pts >= 1 else "NON")
                                conn.update(worksheet="Points Permis", data=df_pts)
                                log_action(a_p, f"Points -> {nv_pts}", row['Nom Roblox']); st.rerun()

# ==========================================
# 💰 ONGLET 3 : BANQUE & RCT BUSINESS
# ==========================================
with tabs[2]:
    st.subheader("💰 Gestion RCT Business & Comptes")
    df_bank = get_data("Banque")
    search_b = st.text_input("🔍 Rechercher un compte bancaire").strip().lower()
    
    if not df_bank.empty and search_b:
        res_b = df_bank[df_bank.apply(lambda r: search_b in str(r).lower(), axis=1)]
        for idx, row in res_b.iterrows():
            solde_c = float(row.get('Solde', 0))
            st.metric(f"👤 Compte de {row['Nom Roblox']}", f"{solde_c:,.0f} $")
            
            with st.expander("💸 Effectuer une opération"):
                with st.form(f"bank_v87_{idx}"):
                    op_name = st.text_input("Opérateur")
                    in_code = st.text_input("Code (Admin ou RCT)", type="password")
                    mnt = st.number_input("Somme", min_value=0.0, step=100.0)
                    
                    c_r, c_a = st.columns(2)
                    
                    if c_r.form_submit_button("📉 FACTURER (Virement vers RCT)"):
                        if in_code == CODE_ENTREPRISE:
                            if solde_c >= mnt:
                                df_bank.at[idx, "Solde"] = solde_c - mnt
                                mask_moi = df_bank['Nom Roblox'].str.lower() == MON_PSEUDO_ROBLOX.lower()
                                if mask_moi.any():
                                    idx_m = df_bank[mask_moi].index[0]
                                    df_bank.at[idx_m, "Solde"] = float(df_bank.at[idx_m, "Solde"]) + mnt
                                    conn.update(worksheet="Banque", data=df_bank)
                                    log_action(op_name, f"Facture RCT {mnt}$", row['Nom Roblox'])
                                    st.success(f"Facturé ! Argent envoyé à {MON_PSEUDO_ROBLOX}")
                                    time.sleep(1); st.rerun()
                                else: st.error("Compte destinataire introuvable.")
                            else: st.error("Fonds insuffisants.")
                        elif in_code == CODE_ADMIN_GENERAL:
                            df_bank.at[idx, "Solde"] = solde_c - mnt
                            conn.update(worksheet="Banque", data=df_bank)
                            log_action(op_name, f"Retrait Admin {mnt}$", row['Nom Roblox']); st.rerun()
                        else: st.error("Code invalide.")

                    if c_a.form_submit_button("📈 AJOUTER (Admin seul)"):
                        if in_code == CODE_ADMIN_GENERAL:
                            df_bank.at[idx, "Solde"] = solde_c + mnt
                            conn.update(worksheet="Banque", data=df_bank)
                            log_action(op_name, f"Ajout Admin {mnt}$", row['Nom Roblox']); st.rerun()
                        else: st.error("Accès Admin requis.")

# ==========================================
# 📜 ONGLET 4 : LOGS
# ==========================================
with tabs[3]:
    if st.text_input("Code Logs", type="password") == CODE_ADMIN_GENERAL:
        st.dataframe(get_data("Logs").iloc[::-1], use_container_width=True)

st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: gray; font-size: 10px;'>Version 8.7 - Système Intégral Restauré</div>", unsafe_allow_html=True)
