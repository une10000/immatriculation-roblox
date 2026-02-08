import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Portail Officiel", layout="wide")

# --- STYLE CSS (LOGO SIDEBAR & ALIGNEMENT STRICT) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        display: flex;
        flex-direction: column;
        height: 520px !important;
        justify-content: space-between;
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
# 🚪 PAGE DE CONNEXION
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
            st.markdown("<div style='height: 125px;'></div>", unsafe_allow_html=True) 
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
# 🖥️ INTERFACE CONNECTÉE
# ==========================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.write(f"🎭 Session active : **{st.session_state.role}**")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()
    st.divider()
    st.write(f"📅 **Date : {datetime.now().strftime('%d/%m/%Y')}**")

st.title(f"🏛️ Espace {st.session_state.role}")

liste_assurances = ["Non assuré", "RCT", "Averis"]
liste_etats = sorted(["California", "Washington", "Texas", "New York", "Florida", "Quebec", "Ontario", "Nevada", "Colorado"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])

if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers Permis", "💰 Banque Centrale", "📜 Logs Système"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation RCT"])
else:
    tabs = st.tabs(["🚗 Registre Véhicules", "💰 Mon Compte"])

# --- ONGLET 1 : IMMATRICULATIONS ---
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
            pwd = c2.text_input("🔑 Code secret", type="password")
            if st.form_submit_button("✅ Valider"):
                if u and p and pwd:
                    new_r = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "L'état de la plaque": e, "Numéro de la plaque": p, "Assurance": a, "CODE": str(pwd)}])
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_r], ignore_index=True))
                    st.success("🎉 Enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    search = st.text_input("🔍 Rechercher (Plaque, Roblox ou Discord)").strip().lower()
    if not df_im.empty:
        mask = df_im.apply(lambda r: search in str(r).lower(), axis=1)
        for idx, row in df_im[mask].iterrows():
            with st.container(border=True):
                col_txt, col_ctrl = st.columns([3, 1])
                col_txt.markdown(f"### 🚗 **{row['Numéro de la plaque']}**")
                col_txt.markdown(f"👤 **Propriétaire :** {row['Nom d\'utilisateur ROBLOX']}")
                col_txt.markdown(f"🚘 **Véhicule :** {row['Marque du véhicule']} ({row['L\'état de la plaque']})")
                col_txt.markdown(f"🛡️ **Assurance :** {row['Assurance']}")
                col_txt.markdown(f"📅 **Enregistré le :** {row['Horodateur']}")
                
                if col_ctrl.button("⚙️ Gérer", key=f"m_{idx}"):
                    st.session_state[f"vis_{idx}"] = not st.session_state.get(f"vis_{idx}", False)
                if st.session_state.get(f"vis_{idx}"):
                    with st.form(f"auth_{idx}"):
                        in_code = st.text_input("Code secret", type="password")
                        if st.form_submit_button("🔓 Déverrouiller"):
                            if st.session_state.role == "Staff" or str(in_code) == str(row['CODE']):
                                st.session_state[f"ok_{idx}"] = True
                            else: st.error("Code incorrect.")
                    if st.session_state.get(f"ok_{idx}"):
                        with st.form(f"edit_{idx}"):
                            new_pl = st.text_input("Plaque", value=row['Numéro de la plaque'])
                            new_as = st.selectbox("Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']) if row['Assurance'] in liste_assurances else 0)
                            b1, b2 = st.columns(2)
                            if b1.form_submit_button("💾 Sauvegarder"):
                                df_im.at[idx, 'Numéro de la plaque'] = new_pl
                                df_im.at[idx, 'Assurance'] = new_as
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.success("Mis à jour !"); time.sleep(1); st.rerun()
                            if b2.form_submit_button("🗑️ Supprimer"):
                                df_im = df_im.drop(idx)
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.error("Supprimé."); time.sleep(1); st.rerun()

# --- ONGLET 2 : BANQUE & POINTS (CORRIGÉ) ---
with tabs[1]:
    df_b = get_data("Banque")
    df_p = get_data("Points Permis")
    
    if st.session_state.role == "Civil":
        nom_c = st.text_input("🔍 Entrez votre Pseudo (Roblox ou Discord)").strip().lower()
        if nom_c:
            # Recherche Banque
            res_b = df_b[df_b.apply(lambda r: nom_c in str(r).lower(), axis=1)]
            # Recherche Points (Colonne 'PTS' selon ton image)
            res_p = df_p[df_p.apply(lambda r: nom_c in str(r).lower(), axis=1)]
            
            if not res_b.empty or not res_p.empty:
                c1, c2 = st.columns(2)
                if not res_b.empty:
                    c1.metric("💵 Votre Solde Bancaire", f"{float(res_b.iloc[0]['Solde']):,.0f} $")
                
                if not res_p.empty:
                    # CORRECTION ICI : Utilisation de 'PTS' au lieu de 'Points'
                    valeur_points = res_p.iloc[0]['PTS']
                    c2.metric("🪪 Points de Permis", f"{valeur_points} / 25") # J'ai mis /25 car ton sheet montre 25
            else: st.info("Aucun compte trouvé.")
    else:
        st.write("### 💳 Gestion Financière")
        # Logique Staff... (Identique au précédent)

if st.session_state.role == "Staff":
    with tabs[2]:
        st.write("### 🪪 Base des Permis")
        st.dataframe(df_p, use_container_width=True)
    with tabs[3]:
        st.write("### 📜 Logs")
        st.dataframe(get_data("Logs").iloc[::-1], use_container_width=True)

st.markdown("---")
st.markdown("<center><small>RCRP FR | Système de Gestion v9.27</small></center>", unsafe_allow_html=True)
