import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Portail Officiel", layout="wide")

# --- INITIALISATION SESSION ---
if "role" not in st.session_state:
    st.session_state.role = None

# --- PARAMÈTRES ET CODES ---
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26" 
CODE_ENTREPRISE = "RCT-26-RCRPFR" 
MON_PSEUDO_ROBLOX = "une10000"

def get_data(sheet_name):
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except: return pd.DataFrame()

# ==========================================
# 🚪 PAGE DE CONNEXION (S'AFFICHE SI ROLE EST VIDE)
# ==========================================
if st.session_state.role is None:
    st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png", width=150)
    st.title("🏛️ Bienvenue sur le Portail RCRP")
    st.subheader("Veuillez sélectionner votre mode d'accès")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.write("### 👤 Civil")
            st.write("Consulter les registres et enregistrer un véhicule.")
            if st.button("Continuer en tant que Civil", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()
                
    with col2:
        with st.container(border=True):
            st.write("### 🛠️ Entreprise (RCT)")
            st.write("Accès aux services de facturation et gestion business.")
            code_rct = st.text_input("Code Entreprise", type="password", key="c_rct")
            if st.button("Connexion RCT", use_container_width=True):
                if code_rct == CODE_ENTREPRISE:
                    st.session_state.role = "RCT"
                    st.rerun()
                else: st.error("Code invalide.")

    with col3:
        with st.container(border=True):
            st.write("### 👮 Police / Staff")
            st.write("Accès complet aux fichiers et à la gestion des permis.")
            code_pol = st.text_input("Code Autorisation", type="password", key="c_pol")
            if st.button("Connexion Autorités", use_container_width=True):
                if code_pol == CODE_ADMIN_GENERAL:
                    st.session_state.role = "Staff"
                    st.rerun()
                else: st.error("Code invalide.")
    st.stop() # Arrête le code ici tant qu'on n'a pas choisi de rôle

# ==========================================
# 🖥️ INTERFACE UNE FOIS CONNECTÉ
# ==========================================

# Bouton de déconnexion en haut
if st.sidebar.button("🚪 Déconnexion"):
    st.session_state.role = None
    st.rerun()

st.sidebar.write(f"Connecté en tant que : **{st.session_state.role}**")

# On définit les onglets selon le rôle
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Permis", "💰 Banque", "📜 Logs"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation RCT"])
else: # Civil
    tabs = st.tabs(["🚗 Registre Véhicules", "💰 Mon Solde"])

# --- LISTES (Identiques) ---
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])
liste_assurances = ["Non assuré", "RCT", "Averis"]

# ==========================================
# 🚗 ONGLET 1 : IMMATRICULATIONS (TOUS)
# ==========================================
with tabs[0]:
    df_im = get_data("Copie de Immatriculations")
    st.metric("🚗 Véhicules en base", len(df_im))
    
    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("add_v95"):
            u = st.text_input("👤 Pseudo Roblox"); m = st.selectbox("🚘 Marque", liste_marques)
            e = st.selectbox("📍 État", liste_etats); p = st.text_input("🔢 Plaque")
            a = st.selectbox("🛡️ Assurance", liste_assurances); c = st.text_input("🔑 Code secret véhicule", type="password")
            if st.form_submit_button("Valider"):
                if u and p and c:
                    new_r = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "L'état de la plaque": e, "Numéro de la plaque": p, "Assurance": a, "CODE": str(c)}])
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_r], ignore_index=True))
                    st.success("Enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    sq = st.text_input("🔍 Recherche").strip().upper()
    if not df_im.empty:
        mask = df_im.apply(lambda r: sq in str(r).upper(), axis=1) if sq else [True]*len(df_im)
        for idx, row in df_im[mask].iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"### 🚗 {row['Numéro de la plaque']} — {row['Marque du véhicule']}")
                c1.write(f"👤 {row['Nom d\'utilisateur ROBLOX']} | 📍 {row['L\'état de la plaque']} | 🛡️ {row['Assurance']}")
                
                # SEULS STAFF ET RCT (ou civil avec code secret) PEUVENT GERER
                if st.session_state.role in ["Staff", "RCT"]:
                    if c2.button(f"⚙️ Gérer", key=f"g_{idx}"): st.session_state[f"op_{idx}"] = not st.session_state.get(f"op_{idx}", False)
                
                if st.session_state.get(f"op_{idx}"):
                    with st.form(f"fo_{idx}"):
                        np = st.text_input("Plaque", value=row['Numéro de la plaque'])
                        na = st.selectbox("Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']))
                        vc = st.text_input("Code secret véhicule", type="password")
                        if st.form_submit_button("Sauvegarder"):
                            if vc == str(row['CODE']) or st.session_state.role == "Staff":
                                df_im.at[idx, 'Numéro de la plaque'] = np
                                df_im.at[idx, 'Assurance'] = na
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.success("OK !"); time.sleep(1); st.rerun()
                            else: st.error("Code secret faux.")

# ==========================================
# 💰 ONGLET BANQUE (SELON ROLE)
# ==========================================
with tabs[1]:
    df_b = get_data("Banque")
    if st.session_state.role == "Civil":
        st.write("### 🏦 Consultez votre solde")
        nom = st.text_input("Entrez votre Pseudo exact").strip().lower()
        if nom:
            res = df_b[df_b['Nom Roblox'].str.lower() == nom]
            if not res.empty:
                st.metric(f"Solde de {nom}", f"{float(res.iloc[0]['Solde']):,.0f} $")
            else: st.error("Compte introuvable.")

    else: # Staff ou RCT
        st.write(f"### 💰 Interface de Paiement ({st.session_state.role})")
        sb = st.text_input("🔍 Rechercher un compte").strip().lower()
        if not df_b.empty and sb:
            res_b = df_b[df_b.apply(lambda r: sb in str(r).lower(), axis=1)]
            for idx, row in res_b.iterrows():
                solde = float(row.get('Solde', 0))
                with st.container(border=True):
                    st.metric(f"👤 {row['Nom Roblox']}", f"{solde:,.0f} $")
                    with st.form(f"fb_{idx}"):
                        mt = st.number_input("Montant", min_value=0.0, step=100.0)
                        c_ret, c_aj = st.columns(2)
                        if c_ret.form_submit_button("📉 RETIRER / FACTURER"):
                            if st.session_state.role == "RCT":
                                if solde >= mt:
                                    df_b.at[idx, "Solde"] = solde - mt
                                    mask = df_b['Nom Roblox'].str.lower() == MON_PSEUDO_ROBLOX.lower()
                                    if mask.any():
                                        df_b.at[df_b[mask].index[0], "Solde"] = float(df_b[df_b[mask].index[0]]["Solde"]) + mt
                                        conn.update(worksheet="Banque", data=df_b)
                                        st.success("Virement RCT OK !"); time.sleep(1); st.rerun()
                            else: # Staff
                                df_b.at[idx, "Solde"] = solde - mt
                                conn.update(worksheet="Banque", data=df_b)
                                st.success("Amende effectuée."); time.sleep(1); st.rerun()
                        if c_aj.form_submit_button("📈 AJOUTER (Police/Staff)"):
                            if st.session_state.role == "Staff":
                                df_b.at[idx, "Solde"] = solde + mt
                                conn.update(worksheet="Banque", data=df_b)
                                st.success("Ajout OK."); time.sleep(1); st.rerun()
                            else: st.error("Action réservée au Staff.")

# Les onglets Permis (tabs[2]) et Logs (tabs[3]) pour le Staff sont à la suite...
# ==========================================
# 🪪 ONGLET 2 : POINTS DE PERMIS
# ==========================================
with tabs[1]:
    df_pts = get_data("Points Permis")
    p1, p2, p3 = st.columns([1,1,2])
    p1.metric("🪪 Dossiers", len(df_pts))
    p2.metric("🚫 Suspendus", len(df_pts[df_pts['Validité'] == "NON"]))
    p3.warning("👮 Attention : La création d'un dossier génère automatiquement 15 000 $ en banque.")

    with st.expander("👤 Ouvrir un nouveau dossier citoyen"):
        with st.form("f_pts_v93"):
            c1, c2 = st.columns(2)
            adm = c1.text_input("👮 Admin responsable")
            rob = c1.text_input("👤 Pseudo Roblox")
            disc = c2.text_input("💬 Discord (@)")
            pts_i = c2.number_input("📉 Points initiaux", 0, 25, 25)
            c_a = st.text_input("🔑 Code Admin Général", type="password")
            if st.form_submit_button("💾 Créer le profil"):
                if c_a == CODE_ADMIN_GENERAL and rob:
                    v = "VALIDE" if pts_i >= 14 else ("OUI" if pts_i >= 1 else "NON")
                    new_p = pd.DataFrame([{"Nom Discord": disc, "Nom Roblox": rob, "PTS": pts_i, "Validité": v}])
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_p], ignore_index=True))
                    df_b = get_data("Banque")
                    new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": disc, "Nom Roblox": rob, "Pseudo Admin": adm}])
                    conn.update(worksheet="Banque", data=pd.concat([df_b, new_b], ignore_index=True))
                    st.success("✅ Citoyen enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    sp = st.text_input("🔍 Rechercher un conducteur par nom").strip().lower()
    if not df_pts.empty and sp:
        res_p = df_pts[df_pts.apply(lambda r: sp in str(r).lower(), axis=1)]
        for idx, row in res_p.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"### 👤 {row['Nom Roblox']}")
                c1.write(f"Discord : {row['Nom Discord']}")
                c2.metric("Points", f"{int(row['PTS'])}/25")
                c2.write(f"État : **{row['Validité']}**")
                with c3.expander("⚙️ Editer"):
                    with st.form(f"fp_{idx}"):
                        nv = st.number_input("Nouveau solde", 0, 25, int(row['PTS']))
                        ca = st.text_input("Code Admin", type="password")
                        if st.form_submit_button("OK"):
                            if ca == CODE_ADMIN_GENERAL:
                                df_pts.at[idx, "PTS"] = nv
                                df_pts.at[idx, "Validité"] = "VALIDE" if nv >= 14 else ("OUI" if nv >= 1 else "NON")
                                conn.update(worksheet="Points Permis", data=df_pts)
                                st.success("✅ Mis à jour"); time.sleep(1); st.rerun()

# ==========================================
# 💰 ONGLET 3 : BANQUE & RCT
# ==========================================
with tabs[2]:
    df_bank = get_data("Banque")
    # Calcul de la richesse totale
    total_bank = sum([float(x) for x in df_bank['Solde'] if str(x).replace('.','').isdigit()])
    
    b1, b2, b3 = st.columns(3)
    b1.metric("🏦 Masse Monétaire", f"{total_bank:,.0f} $")
    b2.metric("👥 Comptes Actifs", len(df_bank))
    b3.success("💡 RCT Business : Utilisez le code entreprise pour vos facturations.")

    sb = st.text_input("🔍 Rechercher un compte bancaire").strip().lower()
    if not df_bank.empty and sb:
        res_b = df_bank[df_bank.apply(lambda r: sb in str(r).lower(), axis=1)]
        for idx, row in res_b.iterrows():
            solde = float(row.get('Solde', 0))
            with st.container(border=True):
                c_info, c_op = st.columns([2, 2])
                c_info.metric(f"👤 {row['Nom Roblox']}", f"{solde:,.0f} $")
                with c_op:
                    with st.form(f"fb_v93_{idx}"):
                        cd = st.text_input("🔑 Code", type="password")
                        mt = st.number_input("💵 Somme", min_value=0.0, step=500.0)
                        r, a = st.columns(2)
                        if r.form_submit_button("📉 RETIRER"):
                            if cd == CODE_ENTREPRISE:
                                if solde >= mt:
                                    df_bank.at[idx, "Solde"] = solde - mt
                                    mask = df_bank['Nom Roblox'].str.lower() == MON_PSEUDO_ROBLOX.lower()
                                    if mask.any():
                                        im = df_bank[mask].index[0]
                                        df_bank.at[im, "Solde"] = float(df_bank.at[im, "Solde"]) + mt
                                        conn.update(worksheet="Banque", data=df_bank)
                                        st.success("💸 Virement RCT OK !"); time.sleep(1); st.rerun()
                                    else: st.error("Compte destinataire 'une10000' absent.")
                                else: st.error("Solde insuffisant.")
                            elif cd == CODE_ADMIN_GENERAL:
                                df_bank.at[idx, "Solde"] = solde - mt
                                conn.update(worksheet="Banque", data=df_bank)
                                st.success("📉 Retrait effectué."); time.sleep(1); st.rerun()
                            else: st.error("Code incorrect.")
                        if a.form_submit_button("📈 AJOUTER"):
                            if cd == CODE_ADMIN_GENERAL:
                                df_bank.at[idx, "Solde"] = solde + mt
                                conn.update(worksheet="Banque", data=df_bank)
                                st.success("📈 Ajouté."); time.sleep(1); st.rerun()
                            else: st.error("Accès Admin requis.")

# ==========================================
# 📜 ONGLET 4 : ARCHIVES LOGS
# ==========================================
with tabs[3]:
    st.info("🔐 Accès restreint au haut commandement.")
    pwd_log = st.text_input("🔑 Entrez le Code d'Accès Archives", type="password")
    if pwd_log == CODE_ADMIN_GENERAL:
        st.dataframe(get_data("Logs").iloc[::-1], use_container_width=True)
    elif pwd_log:
        st.error("❌ Accès refusé.")

st.markdown("---")
st.markdown("<center><small>RCRP FR - Système de Gestion Centralisé v9.3 | Développé pour le RP</small></center>", unsafe_allow_html=True)
