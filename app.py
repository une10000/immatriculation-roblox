import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Portail Officiel", layout="wide")

# --- STYLE CSS (ALIGNEMENT ET ESPACEMENT) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    div[data-testid="stExpander"] { border: 1px solid #f0f2f6; border-radius: 10px; }
    .stMetric { background-color: #f8f9fb; padding: 10px; border-radius: 10px; border: 1px solid #e0e0e0; }
    [data-testid="stHorizontalBlock"] { align-items: center; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION SESSION ---
if "role" not in st.session_state:
    st.session_state.role = None

# --- PARAMÈTRES ET CODES ---
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26" 
CODE_ENTREPRISE = "RCT-26-RCRPFR" 
MON_PSEUDO_ROBLOX = "une10000"
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=1100&height=608"

# --- FONCTION LECTURE ---
def get_data(sheet_name):
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except: return pd.DataFrame()

# ==========================================
# 🚪 PAGE DE CONNEXION
# ==========================================
if st.session_state.role is None:
    head_col1, head_col2 = st.columns([1, 4])
    with head_col1:
        st.image(LOGO_URL, use_container_width=True)
    with head_col2:
        st.markdown("<h1 style='margin:0;'>🏛️ Portail des Services RCRP</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 18px; margin:0;'>Accès sécurisé au Fichier Central de la République</p>", unsafe_allow_html=True)
    
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.write("### 👤 Citoyen")
            st.write("Consulter vos points, votre solde et vos véhicules.")
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"; st.rerun()
    with col2:
        with st.container(border=True):
            st.write("### 🛠️ Entreprise (RCT)")
            st.write("Interface de facturation et gestion assurance.")
            c_rct = st.text_input("Code RCT", type="password", key="log_rct")
            if st.button("Connexion Pro", use_container_width=True):
                if c_rct == CODE_ENTREPRISE:
                    st.session_state.role = "RCT"; st.rerun()
                else: st.error("❌ Code incorrect.")
    with col3:
        with st.container(border=True):
            st.write("### 👮 Autorités / Staff")
            st.write("Administration complète et Archives.")
            c_pol = st.text_input("Code Autorisation", type="password", key="log_pol")
            if st.button("Connexion Sécurisée", use_container_width=True):
                if c_pol == CODE_ADMIN_GENERAL:
                    st.session_state.role = "Staff"; st.rerun()
                else: st.error("❌ Code incorrect.")
    st.stop()

# ==========================================
# 🖥️ INTERFACE CONNECTÉE
# ==========================================
main_h1, main_h2 = st.columns([1, 5])
with main_h1:
    st.image(LOGO_URL, use_container_width=True)
with main_h2:
    st.title(f"🏛️ Espace {st.session_state.role}")

with st.sidebar:
    st.write(f"🎭 Session : **{st.session_state.role}**")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()
    st.divider()
    st.info(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

# --- DÉFINITION DES ONGLETS ---
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers Permis", "💰 Banque Centrale", "📜 Logs"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation RCT"])
else:
    tabs = st.tabs(["🚗 Registre Véhicules", "💰 Mon Compte (Solde & Points)"])

# --- LISTES (Immuables) ---
liste_assurances = ["Non assuré", "RCT", "Averis"]
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])

# ==========================================
# 🚗 ONGLET 1 : IMMATRICULATIONS (TOUS)
# ==========================================
with tabs[0]:
    df_im = get_data("Copie de Immatriculations")
    st.metric("🚗 Véhicules enregistrés", len(df_im))
    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("add_v10"):
            c1, c2 = st.columns(2)
            u = c1.text_input("👤 Pseudo Roblox"); m = c1.selectbox("🚘 Marque", liste_marques)
            e = c2.selectbox("📍 État", liste_etats); p = c2.text_input("🔢 Plaque")
            a = c1.selectbox("🛡️ Assurance", liste_assurances); c = c2.text_input("🔑 Code secret", type="password")
            if st.form_submit_button("✅ Valider"):
                if u and p and c:
                    new_r = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "L'état de la plaque": e, "Numéro de la plaque": p, "Assurance": a, "CODE": str(c)}])
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_r], ignore_index=True))
                    st.success("Enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    sq = st.text_input("🔍 Rechercher une plaque ou un propriétaire").strip().upper()
    if not df_im.empty:
        mask = df_im.apply(lambda r: sq in str(r).upper(), axis=1) if sq else [True]*len(df_im)
        for idx, row in df_im[mask].iterrows():
            with st.container(border=True):
                co1, co2 = st.columns([3, 1])
                co1.markdown(f"### 🚗 {row['Numéro de la plaque']} — {row['Marque du véhicule']}")
                co1.write(f"👤 **{row['Nom d\'utilisateur ROBLOX']}** | 📍 {row['L\'état de la plaque']} | 🛡️ **Assurance : {row['Assurance']}**")
                if st.session_state.role in ["Staff", "RCT"]:
                    if co2.button(f"⚙️ Gérer", key=f"g_{idx}"): st.session_state[f"op_{idx}"] = not st.session_state.get(f"op_{idx}", False)
                    if st.session_state.get(f"op_{idx}"):
                        with st.form(f"fo_{idx}"):
                            np = st.text_input("Plaque", value=row['Numéro de la plaque'])
                            na = st.selectbox("Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']))
                            if st.form_submit_button("💾 Sauver"):
                                df_im.at[idx, 'Numéro de la plaque'] = np
                                df_im.at[idx, 'Assurance'] = na
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.success("Mis à jour !"); time.sleep(1); st.rerun()

# ==========================================
# 💰 ONGLET 2 : BANQUE & POINTS (CIVIL)
# ==========================================
with tabs[1]:
    if st.session_state.role == "Civil":
        st.write("### 🏦 Consultation de votre dossier Citoyen")
        nom_search = st.text_input("Entrez votre Pseudo Roblox EXACT").strip().lower()
        if nom_search:
            c_solde, c_points = st.columns(2)
            
            # Récupération Solde
            df_b = get_data("Banque")
            res_b = df_b[df_b['Nom Roblox'].str.lower() == nom_search]
            if not res_b.empty:
                c_solde.metric("💵 Votre Solde", f"{float(res_b.iloc[0]['Solde']):,.0f} $")
            else: c_solde.warning("⚠️ Compte bancaire non trouvé.")
            
            # Récupération Points (NOUVEAUTÉ)
            df_p = get_data("Points Permis")
            res_p = df_p[df_p['Nom Roblox'].str.lower() == nom_search]
            if not res_p.empty:
                pts = res_p.iloc[0]['Points']
                # Couleur selon les points
                color = "normal" if int(pts) > 2 else "inverse"
                c_points.metric("🪪 Points restants", f"{pts} / 12", delta_color=color)
            else: c_points.warning("⚠️ Dossier permis non trouvé.")
    
    # --- Interface Banque pour Staff/RCT (Virements/Factures) ---
    else:
        df_b = get_data("Banque")
        sb = st.text_input("🔍 Rechercher un compte").strip().lower()
        if not df_b.empty and sb:
            res_b = df_b[df_b.apply(lambda r: sb in str(r).lower(), axis=1)]
            for idx, row in res_b.iterrows():
                solde = float(row.get('Solde', 0))
                with st.container(border=True):
                    st.metric(f"👤 {row['Nom Roblox']}", f"{solde:,.0f} $")
                    with st.form(f"fb_{idx}"):
                        mt = st.number_input("Montant", min_value=0.0, step=100.0)
                        if st.form_submit_button("📉 FACTURER / RETIRER"):
                            if st.session_state.role == "RCT" and solde >= mt:
                                df_b.at[idx, "Solde"] = solde - mt
                                mask = df_b['Nom Roblox'].str.lower() == MON_PSEUDO_ROBLOX.lower()
                                if mask.any():
                                    df_b.at[df_b[mask].index[0], "Solde"] = float(df_b.at[df_b[mask].index[0], "Solde"]) + mt
                                    conn.update(worksheet="Banque", data=df_b)
                                    st.success("Payé !"); time.sleep(1); st.rerun()

# ==========================================
# 🪪 & 📜 STAFF ONLY
# ==========================================
if st.session_state.role == "Staff":
    with tabs[2]:
        st.write("### 🪪 Gestion des Permis")
        st.dataframe(get_data("Points Permis"), use_container_width=True)
    with tabs[3]:
        st.write("### 📜 Archives")
        st.dataframe(get_data("Logs").iloc[::-1], use_container_width=True)

st.markdown("---")
st.markdown("<center><small>République de Californie RP | Système v9.10</small></center>", unsafe_allow_html=True)
