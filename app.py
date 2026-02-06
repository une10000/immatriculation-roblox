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
def log_action(admin_name, action, cible):
    try:
        df_logs = conn.read(worksheet="Logs", ttl=0)
    except:
        df_logs = pd.DataFrame(columns=["Horodateur", "Admin", "Action", "Cible"])
    
    new_log = pd.DataFrame([{
        "Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"),
        "Admin": str(admin_name),
        "Action": str(action),
        "Cible": str(cible)
    }])
    conn.update(worksheet="Logs", data=pd.concat([df_logs, new_log], ignore_index=True))

# --- LISTES ---
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])
liste_assurances = ["Non assuré", "RCT", "Averis"]

# --- NAVIGATION ---
tabs = st.tabs(["🚗 Immatriculations", "🪪 Points de Permis", "💰 Banque", "📜 Logs"])

# ==========================================
# ONGLET 1 : IMMATRICULATIONS
# ==========================================
with tabs[0]:
    nom_feuille_immat = "Copie de Immatriculations"
    try:
        df_immat = conn.read(worksheet=nom_feuille_immat, ttl=0)
    except: df_immat = pd.DataFrame()
    
    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("inscription"):
            u_reg = st.text_input("Nom d'utilisateur ROBLOX")
            m_reg = st.selectbox("Marque du véhicule", liste_marques)
            e_reg = st.selectbox("État", liste_etats)
            p_reg = st.text_input("Numéro de la plaque")
            a_reg = st.selectbox("Assurance", liste_assurances)
            c_reg = st.text_input("Code secret (perso)", type="password")
            if st.form_submit_button("Valider"):
                if u_reg and p_reg and c_reg:
                    h = (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M")
                    new_row = pd.DataFrame([{"Horodateur": h, "Nom d'utilisateur ROBLOX": u_reg, "Marque du véhicule": m_reg, "L'état de la plaque": e_reg, "Numéro de la plaque": p_reg, "Assurance": a_reg, "CODE": str(c_reg)}])
                    conn.update(worksheet=nom_feuille_immat, data=pd.concat([df_immat, new_row], ignore_index=True))
                    st.success("✅ Véhicule enregistré !")
                    time.sleep(1); st.rerun()

    st.divider()
    s_query = st.text_input("🔍 Rechercher véhicule").strip().upper()
    if not df_immat.empty:
        mask = df_immat.apply(lambda r: r.astype(str).str.contains(s_query, case=False).any(), axis=1) if s_query else [True]*len(df_immat)
        st.dataframe(df_immat[mask][[c for c in df_immat.columns if c != "CODE"]], use_container_width=True)

# ==========================================
# ONGLET 2 : POINTS DE PERMIS
# ==========================================
with tabs[1]:
    nom_feuille_pts = "Points Permis"
    nom_feuille_banque = "Banque"
    try:
        df_pts = conn.read(worksheet=nom_feuille_pts, ttl=0)
        df_bank = conn.read(worksheet=nom_feuille_banque, ttl=0)
    except: 
        df_pts = pd.DataFrame(); df_bank = pd.DataFrame()

    with st.expander("👤 [ADMIN] Ajouter un nouveau conducteur"):
        with st.form("admin_add_driver"):
            adm_name = st.text_input("Ton Nom Admin")
            new_discord = st.text_input("Nom Discord")
            new_roblox = st.text_input("Nom Roblox")
            new_pts = st.number_input("Points", 0, 25, 25)
            admin_code = st.text_input("Code Admin", type="password")
            if st.form_submit_button("Créer le dossier"):
                if admin_code == CODE_ADMIN_GENERAL and adm_name:
                    if new_roblox:
                        v_label = "VALIDE" if new_pts >= 14 else ("OUI" if new_pts >= 1 else "NON")
                        new_driver = pd.DataFrame([{"Nom Discord": new_discord, "Nom Roblox": new_roblox, "PTS": new_pts, "Validité": v_label}])
                        conn.update(worksheet=nom_feuille_pts, data=pd.concat([df_pts, new_driver], ignore_index=True))
                        
                        existing_users = []
                        if not df_bank.empty and "Nom Roblox" in df_bank.columns:
                            existing_users = df_bank["Nom Roblox"].astype(str).str.lower().values
                        
                        if new_roblox.lower() not in existing_users:
                            new_b = pd.DataFrame([{"Solde": 15000.0, "Nom Roblox": new_roblox, "Pseudo Admin": adm_name}])
                            conn.update(worksheet=nom_feuille_banque, data=pd.concat([df_bank, new_b], ignore_index=True))
                        
                        log_action(adm_name, "Création Dossier + Banque", new_roblox)
                        st.success("✅ Fait !"); time.sleep(1); st.rerun()
                else: st.error("❌ Code ou Nom Admin manquant")

    st.divider()
    search_p = st.text_input("🔍 Chercher conducteur").strip()
    if not df_pts.empty and search_p:
        res = df_pts[df_pts["Nom Roblox"].astype(str).str.contains(search_p, case=False, na=False)]
        for idx, row in res.iterrows():
            st.markdown(f"### 👤 {row.get('Nom Roblox')}")
            with st.expander("⚙️ Modifier / Supprimer"):
                with st.form(key=f"p_{idx}"):
                    adm_n = st.text_input("Ton Nom Admin")
                    ac = st.text_input("Code Admin", type="password")
                    n_p = st.number_input("Points", 0, 25, int(row.get("PTS", 0)))
                    col_b1, col_b2 = st.columns(2)
                    if col_b1.form_submit_button("Sauver"):
                        if ac == CODE_ADMIN_GENERAL and adm_n:
                            df_pts.at[idx, "PTS"] = n_p
                            df_pts.at[idx, "Validité"] = "VALIDE" if n_p >= 14 else ("OUI" if n_p >= 1 else "NON")
                            conn.update(worksheet=nom_feuille_pts, data=df_pts)
                            log_action(adm_n, f"Points -> {n_p}", row.get('Nom Roblox'))
                            st.rerun()
                    if col_b2.form_submit_button("🗑️ SUPPRIMER"):
                        if ac == CODE_ADMIN_GENERAL and adm_n:
                            log_action(adm_n, "Suppression Profil", row.get('Nom Roblox'))
                            conn.update(worksheet=nom_feuille_pts, data=df_pts.drop(idx))
                            st.rerun()

# ==========================================
# ONGLET 3 : BANQUE
# ==========================================
with tabs[2]:
    st.subheader("💰 Banque Centrale")
    # PHRASE ASTUCE MISE À JOUR v5.1
    st.info("💡 **Astuce :** un compte bancaire est automatiquement crée avec un solde de 15'000$ par mois, lorsque votre permis est réussie")
    
    try: 
        df_bank = conn.read(worksheet="Banque", ttl=0)
    except: df_bank = pd.DataFrame()
    
    sb = st.text_input("🔍 Rechercher compte").strip()
    if not df_bank.empty and sb:
        res_b = df_bank[df_bank["Nom Roblox"].astype(str).str.contains(sb, case=False, na=False)]
        for idx, row in res_b.iterrows():
            current_solde = float(row.get('Solde', 0))
            st.metric(row.get('Nom Roblox'), f"{current_solde:,.0f} $")
            with st.expander("🛡️ Transaction Admin"):
                with st.form(key=f"bt_{idx}"):
                    adm_b = st.text_input("Ton Nom Admin")
                    abc = st.text_input("Code Admin", type="password")
                    mnt = st.number_input("Montant", step=500.0)
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("📉 Retirer") and abc == CODE_ADMIN_GENERAL and adm_b:
                        df_bank.at[idx, "Solde"] = current_solde - mnt
                        conn.update(worksheet="Banque", data=df_bank)
                        log_action(adm_b, f"Retrait (-{mnt})", row.get('Nom Roblox')); st.rerun()
                    if c2.form_submit_button("📈 Ajouter") and abc == CODE_ADMIN_GENERAL and adm_b:
                        df_bank.at[idx, "Solde"] = current_solde + mnt
                        conn.update(worksheet="Banque", data=df_bank)
                        log_action(adm_b, f"Ajout (+{mnt})", row.get('Nom Roblox')); st.rerun()

# ==========================================
# ONGLET 4 : LOGS
# ==========================================
with tabs[3]:
    st.subheader("📜 Accès aux Logs")
    unlock = st.text_input("Code de sécurité requis", type="password")
    
    if unlock == CODE_ADMIN_GENERAL:
        try:
            df_l = conn.read(worksheet="Logs", ttl=0)
            st.success("🔓 Accès autorisé")
            st.dataframe(df_l.iloc[::-1], use_container_width=True)
        except: st.warning("Feuille 'Logs' non trouvée.")
    elif unlock != "":
        # ÉMOJI CADENAS APPLE (STYLE)
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>🔒</h1>", unsafe_allow_html=True)
        st.error("ACCÈS REFUSÉ")
    else:
        # ÉMOJI CADENAS PAR DÉFAUT
        st.markdown("<h1 style='text-align: center; font-size: 80px; opacity: 0.5;'>🔒</h1>", unsafe_allow_html=True)
        st.info("Veuillez entrer le code Admin.")

st.markdown("<div style='position: fixed; left: 10px; bottom: 10px; color: grey; font-size: 12px;'>Version v5.1 - Final Style</div>", unsafe_allow_html=True)
