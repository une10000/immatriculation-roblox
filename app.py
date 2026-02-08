import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Portail Officiel", layout="wide")

# --- STYLE CSS (LOGO & ALIGNEMENT FORCE) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    
    /* Force les conteneurs à avoir la même hauteur et aligne les boutons en bas */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        display: flex;
        flex-direction: column;
        height: 520px !important;
    }
    
    /* Cible spécifiquement le bouton dans chaque conteneur pour le pousser vers le bas */
    div[data-testid="stVerticalBlockBorderWrapper"] .stButton {
        margin-top: auto !important;
    }

    .stMetric { 
        background-color: #f8f9fb; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid #e0e0e0; 
    }
    
    [data-testid="stSidebar"] img {
        border-radius: 10px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION SESSION ---
if "role" not in st.session_state:
    st.session_state.role = None

# --- CONNEXION & PARAMÈTRES ---
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26" 
CODE_ENTREPRISE = "RCT-26-RCRPFR" 
MON_PSEUDO_ROBLOX = "une10000"

# URL DU LOGO
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless"

def get_data(sheet_name):
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

# ==========================================
# 🚪 PAGE DE CONNEXION (LOGIQUE ALIGNEMENT)
# ==========================================
if st.session_state.role is None:
    st.title("🏛️ Portail des Services RCRP")
    st.markdown("<p style='font-size: 20px; color: #555;'>République de Californie - Système Centralisé de Gestion</p>", unsafe_allow_html=True)
    
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 👤 Citoyen")
            st.write("Accès public pour consulter vos véhicules, votre solde bancaire et vos points de permis de conduire.")
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"; st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### 🛠️ Entreprise (RCT)")
            st.write("Interface RCT : Gestion de la facturation business, des assurances et des dossiers clients.")
            st.text_input("Code RCT", type="password", key="p_rct")
            if st.button("Connexion Pro", use_container_width=True):
                if st.session_state.p_rct == CODE_ENTREPRISE:
                    st.session_state.role = "RCT"; st.rerun()
                else: st.error("❌ Code incorrect.")

    with col3:
        with st.container(border=True):
            st.markdown("### 👮 Autorités / Staff")
            st.write("Administration totale : Fichier Central, modification des permis, logs et gestion financière.")
            st.text_input("Code Autorisation", type="password", key="p_staff")
            if st.button("Connexion Sécurisée", use_container_width=True):
                if st.session_state.p_staff == CODE_ADMIN_GENERAL:
                    st.session_state.role = "Staff"; st.rerun()
                else: st.error("❌ Code incorrect.")
    st.stop()

# ==========================================
# 🖥️ INTERFACE CONNECTÉE (COMPLÈTE)
# ==========================================

with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.write(f"🎭 Session active : **{st.session_state.role}**")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()
    st.divider()
    st.write(f"📅 **Date : {datetime.now().strftime('%d/%m/%Y')}**")

st.title(f"🏛️ Espace {st.session_state.role}")

# --- LISTES COMPLÈTES ---
liste_assurances = ["Non assuré", "RCT", "Averis"]
liste_etats = sorted(["California", "Washington", "Texas", "New York", "Florida", "Quebec", "Ontario", "Nevada", "Colorado"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])

# --- STRUCTURE DES ONGLETS ---
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers Permis", "💰 Banque Centrale", "➕ Gestion Profils", "📜 Logs Système"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation RCT"])
else:
    tabs = st.tabs(["🚗 Registre Véhicules", "💰 Mon Compte"])

# ==========================================
# 🚗 ONGLET 1 : IMMATRICULATIONS
# ==========================================
with tabs[0]:
    df_im = get_data("Copie de Immatriculations")
    df_b = get_data("Banque")
    
    with st.expander("➕ Enregistrer un nouveau véhicule"):
        with st.form("add_v"):
            c1, c2 = st.columns(2)
            u = c1.text_input("👤 Pseudo Roblox")
            m = c1.selectbox("🚘 Marque", liste_marques)
            p = c2.text_input("🔢 Plaque")
            e = c2.selectbox("📍 État", liste_etats)
            a = c1.selectbox("🛡️ Assurance", liste_assurances)
            pwd = c2.text_input("🔑 Code secret (pour modifier/supprimer)", type="password")
            
            if st.form_submit_button("✅ Valider l'enregistrement"):
                if u and p and pwd:
                    prix_total = 175 
                    user_row = df_b[df_b["Nom Roblox"].str.lower() == u.lower()]
                    
                    if not user_row.empty:
                        solde_actuel = float(user_row.iloc[0]["Solde"])
                        if a == "Averis":
                            prix_total += 130
                            try:
                                date_arr = datetime.strptime(str(user_row.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                                if datetime.now() - date_arr < timedelta(days=30):
                                    prix_total += 50
                                    st.info("💡 Taxe Jeune Conducteur (+50$) appliquée.")
                            except: pass
                        elif a == "RCT":
                            nb_rct = df_im[(df_im["Nom d'utilisateur ROBLOX"].str.lower() == u.lower()) & (df_im["Assurance"] == "RCT")].shape[0]
                            if nb_rct >= 2:
                                prix_total += 0
                                st.success("🎉 Prime TRIO RCT : Assurance offerte !")
                            else:
                                prix_total += 150
                        
                        if solde_actuel >= prix_total:
                            idx_b = user_row.index[0]
                            df_b.at[idx_b, "Solde"] = solde_actuel - prix_total
                            new_r = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "L'état de la plaque": e, "Numéro de la plaque": p, "Assurance": a, "CODE": str(pwd)}])
                            conn.update(worksheet="Banque", data=df_b)
                            conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_r], ignore_index=True))
                            st.success(f"🎉 Véhicule enregistré ! ({prix_total}$ débités)"); time.sleep(1); st.rerun()
                        else: st.error(f"❌ Solde insuffisant. Il vous faut {prix_total}$.")
                    else: st.error("❌ Pseudo introuvable dans la Banque.")
                else: st.warning("Remplissez tous les champs.")

    st.divider()
    search = st.text_input("🔍 Rechercher un véhicule (Partie du nom, Discord ou Plaque)").strip().lower()
    if not df_im.empty:
        mask = df_im.apply(lambda r: search in str(r).lower(), axis=1)
        res_im = df_im[mask]
        for idx, row in res_im.iterrows():
            with st.container(border=True):
                col_txt, col_ctrl = st.columns([3, 1])
                col_txt.markdown(f"### 🚗 **{row['Numéro de la plaque']}**")
                col_txt.markdown(f"👤 **Propriétaire :** {row['Nom d\'utilisateur ROBLOX']}")
                col_txt.markdown(f"🚘 **Véhicule :** {row['Marque du véhicule']} ({row['L\'état de la plaque']})")
                col_txt.markdown(f"🛡️ **Assurance :** {row['Assurance']}")
                if col_ctrl.button("⚙️ Gérer", key=f"m_{idx}"):
                    st.session_state[f"vis_{idx}"] = not st.session_state.get(f"vis_{idx}", False)
                if st.session_state.get(f"vis_{idx}"):
                    with st.form(f"auth_{idx}"):
                        in_code = st.text_input("Code secret", type="password")
                        if st.form_submit_button("🔓 Déverrouiller"):
                            if st.session_state.role == "Staff" or str(in_code) == str(row['CODE']):
                                st.session_state[f"auth_ok_{idx}"] = True
                            else: st.error("Code incorrect.")
                    if st.session_state.get(f"auth_ok_{idx}"):
                        with st.form(f"edit_{idx}"):
                            new_pl = st.text_input("Modifier Plaque", value=row['Numéro de la plaque'])
                            new_as = st.selectbox("Modifier Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']) if row['Assurance'] in liste_assurances else 0)
                            b1, b2 = st.columns(2)
                            if b1.form_submit_button("💾 Sauvegarder"):
                                df_im.at[idx, 'Numéro de la plaque'] = new_pl
                                df_im.at[idx, 'Assurance'] = new_as
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.success("Mis à jour !"); time.sleep(1); st.rerun()
                            if b2.form_submit_button("🗑️ Supprimer"):
                                df_im = df_im.drop(idx)
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.error("Véhicule supprimé."); time.sleep(1); st.rerun()

# ==========================================
# 💰 ONGLET 2 : BANQUE
# ==========================================
with tabs[1 if st.session_state.role != "Staff" else 2]:
    df_b = get_data("Banque")
    if st.session_state.role == "Civil":
        nom_c = st.text_input("🔍 Votre Pseudo").strip().lower()
        if nom_c:
            res_b = df_b[df_b.apply(lambda r: nom_c in str(r).lower(), axis=1)]
            if not res_b.empty:
                c1, c2 = st.columns(2)
                c1.metric("💵 Solde Bancaire", f"{float(res_b.iloc[0]['Solde']):,.0f} $")
                df_p = get_data("Points Permis")
                res_p = df_p[df_p.apply(lambda r: nom_c in str(r).lower(), axis=1)]
                if not res_p.empty: c2.metric("🪪 Points de Permis", f"{res_p.iloc[0]['PTS']} / 25")
    else:
        st.write("### 💳 Gestion Financière")
        s_staff = st.text_input("🔍 Rechercher un citoyen").strip().lower()
        if s_staff:
            res_s = df_b[df_b.apply(lambda r: s_staff in str(r).lower(), axis=1)]
            for idx, row in res_s.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **{row['Nom Roblox']}**")
                    cur_s = float(row['Solde'])
                    st.metric("Solde", f"{cur_s:,.0f} $")
                    with st.form(f"bank_{idx}"):
                        mnt = st.number_input("Montant", min_value=0.0)
                        b1, b2 = st.columns(2)
                        if b1.form_submit_button("📉 Facturer"):
                            df_b.at[idx, 'Solde'] = cur_s - mnt
                            conn.update(worksheet="Banque", data=df_b); st.rerun()
                        if b2.form_submit_button("📈 Ajouter") and st.session_state.role == "Staff":
                            df_b.at[idx, 'Solde'] = cur_s + mnt
                            conn.update(worksheet="Banque", data=df_b); st.rerun()

# ==========================================
# ➕ STAFF : GESTION PROFILS
# ==========================================
if st.session_state.role == "Staff":
    with tabs[1]:
        st.write("### 🪪 Gestion des Permis")
        df_pts = get_data("Points Permis")
        sp = st.text_input("🔍 Chercher citoyen (Permis)").strip().lower()
        if sp:
            res_p = df_pts[df_pts.apply(lambda r: sp in str(r).lower(), axis=1)]
            for idx, row in res_p.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **{row['Nom Roblox']}** | PTS : {row['PTS']}/25")
                    with st.form(f"p_{idx}"):
                        nv = st.number_input("PTS", 0, 25, value=int(row['PTS']))
                        if st.form_submit_button("Sauver"):
                            df_pts.at[idx, 'PTS'] = nv
                            conn.update(worksheet="Points Permis", data=df_pts); st.rerun()

    with tabs[3]:
        st.write("### ➕ Créer un nouveau Profil")
        with st.form("new_citoyen"):
            nu = st.text_input("Nom Roblox")
            ns = st.number_input("Solde de départ", value=15000.0) # 15k auto
            np = st.number_input("Points de permis au début", 0, 25, value=25)
            if st.form_submit_button("✅ Créer le profil complet"):
                df_b = get_data("Banque")
                df_p = get_data("Points Permis")
                if not df_b[df_b["Nom Roblox"].str.lower() == nu.lower()].empty:
                    st.error("❌ Ce citoyen existe déjà.")
                else:
                    # Ajout Banque avec Date d'arrivée auto
                    nc_b = pd.DataFrame([{"Nom Roblox": nu, "Solde": ns, "Date d'arrivée": datetime.now().strftime("%d/%m/%Y")}])
                    # Ajout Points Permis
                    nc_p = pd.DataFrame([{"Nom Roblox": nu, "PTS": np}])
                    conn.update(worksheet="Banque", data=pd.concat([df_b, nc_b], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_p, nc_p], ignore_index=True))
                    st.success(f"🎉 Profil créé ! {nu} a reçu {ns}$ et {np} PTS."); time.sleep(1); st.rerun()
                    
    with tabs[4]:
        st.write("### 📜 Logs")
        st.dataframe(get_data("Logs").iloc[::-1], use_container_width=True)

st.markdown("---")
st.markdown("<center><small>RCRP FR | Système de Gestion v9.36</small></center>", unsafe_allow_html=True)
