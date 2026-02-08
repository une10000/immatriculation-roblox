import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
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
    st.markdown("<p style='font-size: 20px; color: #555;'>Rensselaer County Roleplay FR - Système Centralisé de Gestion</p>", unsafe_allow_html=True)
    
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
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers Permis", "💰 Banque Centrale", "📜 Logs Système"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation RCT"])
else:
    tabs = st.tabs(["🚗 Registre Véhicules", "💰 Mon Compte"])

# ==========================================
# 🚗 ONGLET 1 : IMMATRICULATIONS
# ==========================================
with tabs[0]:
    df_im = get_data("Copie de Immatriculations")
    
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
                    new_r = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "L'état de la plaque": e, "Numéro de la plaque": p, "Assurance": a, "CODE": str(pwd)}])
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_r], ignore_index=True))
                    st.success("🎉 Véhicule enregistré !"); time.sleep(1); st.rerun()
                else: st.warning("Remplissez tous les champs, y compris le code secret.")

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
                col_txt.markdown(f"📅 **Enregistré le :** {row['Horodateur']}")
                
                if col_ctrl.button("⚙️ Gérer le véhicule", key=f"m_{idx}"):
                    st.session_state[f"vis_{idx}"] = not st.session_state.get(f"vis_{idx}", False)
                
                if st.session_state.get(f"vis_{idx}"):
                    with st.form(f"auth_{idx}"):
                        st.write("🔐 **Authentification requise**")
                        in_code = st.text_input("Entrez le code secret du véhicule", type="password")
                        if st.form_submit_button("🔓 Déverrouiller"):
                            if st.session_state.role == "Staff" or str(in_code) == str(row['CODE']):
                                st.session_state[f"auth_ok_{idx}"] = True
                            else: st.error("Code incorrect.")
                    
                    if st.session_state.get(f"auth_ok_{idx}"):
                        with st.form(f"edit_{idx}"):
                            new_pl = st.text_input("Modifier Plaque", value=row['Numéro de la plaque'])
                            new_as = st.selectbox("Modifier Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']) if row['Assurance'] in liste_assurances else 0)
                            b1, b2 = st.columns(2)
                            if b1.form_submit_button("💾 Sauvegarder les modifications"):
                                df_im.at[idx, 'Numéro de la plaque'] = new_pl
                                df_im.at[idx, 'Assurance'] = new_as
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.success("Mis à jour !"); time.sleep(1); st.rerun()
                            if b2.form_submit_button("🗑️ Supprimer définitivement"):
                                df_im = df_im.drop(idx)
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.error("Véhicule supprimé."); time.sleep(1); st.rerun()

# ==========================================
# 💰 ONGLET 2 : BANQUE & GESTION FINANCIÈRE
# ==========================================
with tabs[1 if st.session_state.role != "Staff" else 2]:
    df_b = get_data("Banque")
    
    if st.session_state.role == "Civil":
        nom_c = st.text_input("🔍 Entrez votre Pseudo (Roblox ou Discord)").strip().lower()
        if nom_c:
            res_b = df_b[df_b.apply(lambda r: nom_c in str(r).lower(), axis=1)]
            if not res_b.empty:
                c1, c2 = st.columns(2)
                c1.metric("💵 Votre Solde Bancaire", f"{float(res_b.iloc[0]['Solde']):,.0f} $")
                df_p = get_data("Points Permis")
                res_p = df_p[df_p.apply(lambda r: nom_c in str(r).lower(), axis=1)]
                if not res_p.empty:
                    pts_val = res_p.iloc[0]['PTS']
                    c2.metric("🪪 Points de Permis", f"{pts_val} / 25")
            else: st.info("Aucun compte trouvé.")
    
    else:
        st.write("### 💳 Gestion Financière Centrale")
        s_staff = st.text_input("🔍 Rechercher un compte citoyen pour facturer/amender").strip().lower()
        if s_staff:
            res_s = df_b[df_b.apply(lambda r: s_staff in str(r).lower(), axis=1)]
            for idx, row in res_s.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **Compte : {row['Nom Roblox']}**")
                    cur_solde = float(row['Solde'])
                    st.metric("Solde actuel", f"{cur_solde:,.0f} $")
                    with st.form(f"bank_op_{idx}"):
                        montant = st.number_input("Montant de la transaction", min_value=0.0)
                        btn_fact, btn_add = st.columns(2)
                        
                        if btn_fact.form_submit_button("📉 Facturer / Amende"):
                            df_b.at[idx, 'Solde'] = cur_solde - montant
                            if st.session_state.role == "RCT":
                                rct_idx = df_b[df_b['Nom Roblox'].str.lower() == MON_PSEUDO_ROBLOX.lower()].index
                                if not rct_idx.empty:
                                    df_b.at[rct_idx[0], 'Solde'] = float(df_b.at[rct_idx[0], 'Solde']) + montant
                            conn.update(worksheet="Banque", data=df_b)
                            st.success(f"Transaction de {montant}$ effectuée !"); time.sleep(1); st.rerun()
                            
                        if btn_add.form_submit_button("📈 Ajouter (Staff uniquement)") and st.session_state.role == "Staff":
                            df_b.at[idx, 'Solde'] = cur_solde + montant
                            conn.update(worksheet="Banque", data=df_b)
                            st.success(f"Compte crédité de {montant}$ !"); time.sleep(1); st.rerun()

# ==========================================
# 🪪 & 📜 SECTIONS STAFF
# ==========================================
if st.session_state.role == "Staff":
    with tabs[1]:
        st.write("### 🪪 Gestion des Permis de Conduire")
        df_pts = get_data("Points Permis")
        search_p = st.text_input("🔍 Rechercher un citoyen pour ses points").strip().lower()
        if search_p:
            res_p_staff = df_pts[df_pts.apply(lambda r: search_p in str(r).lower(), axis=1)]
            for idx, row in res_p_staff.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **{row['Nom Roblox']}** | Points actuels : **{row['PTS']}/25**")
                    with st.form(f"pts_edit_{idx}"):
                        new_pts = st.number_input("Nouveau solde PTS", 0, 25, value=int(row['PTS']))
                        if st.form_submit_button("Mettre à jour PTS"):
                            df_pts.at[idx, 'PTS'] = new_pts
                            conn.update(worksheet="Points Permis", data=df_pts)
                            st.success("Points mis à jour !"); time.sleep(1); st.rerun()
                    
    with tabs[3]:
        st.write("### 📜 Archives des Logs Système")
        st.dataframe(get_data("Logs").iloc[::-1], use_container_width=True)

st.markdown("---")
st.markdown("<center><small>RCRP FR | Système de Gestion Intégral v9.32</small></center>", unsafe_allow_html=True)
