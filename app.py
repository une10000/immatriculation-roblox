import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Portail Officiel", layout="wide")

# --- STYLE CSS (LOGO SIDEBAR & ALIGNEMENT STRICT) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    
    /* Alignement parfait des 3 boîtes de connexion */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        display: flex;
        flex-direction: column;
        height: 480px !important;
        justify-content: space-between;
    }

    .stMetric { 
        background-color: #f8f9fb; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid #e0e0e0; 
    }
    
    /* Logo Sidebar Section A */
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
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=1100&height=608"

def get_data(sheet_name):
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

# ==========================================
# 🚪 PAGE DE CONNEXION (ALIGNEMENT TOTAL)
# ==========================================
if st.session_state.role is None:
    st.title("🏛️ Portail des Services RCRP")
    st.markdown("<p style='font-size: 20px; color: #555;'>République de Californie - Système Centralisé</p>", unsafe_allow_html=True)
    
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 👤 Citoyen")
            st.write("Accès public : consultez vos immatriculations, votre solde bancaire et vos points de permis de conduire.")
            # Bloc de compensation pour simuler le champ input et aligner le bouton
            st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"; st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### 🛠️ Entreprise (RCT)")
            st.write("Interface RCT : Facturation Business, gestion des assurances et suivi des dossiers clients.")
            st.text_input("Code RCT", type="password", key="login_rct")
            if st.button("Connexion Pro", use_container_width=True):
                if st.session_state.login_rct == CODE_ENTREPRISE:
                    st.session_state.role = "RCT"; st.rerun()
                else: st.error("❌ Code incorrect.")

    with col3:
        with st.container(border=True):
            st.markdown("### 👮 Autorités / Staff")
            st.write("Administration totale : Fichier Central, modification des permis, accès aux logs et finances.")
            st.text_input("Code Autorisation", type="password", key="login_staff")
            if st.button("Connexion Sécurisée", use_container_width=True):
                if st.session_state.login_staff == CODE_ADMIN_GENERAL:
                    st.session_state.role = "Staff"; st.rerun()
                else: st.error("❌ Code incorrect.")
    st.stop()

# ==========================================
# 🖥️ INTERFACE CONNECTÉE
# ==========================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.write(f"🎭 Session : **{st.session_state.role}**")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()
    st.divider()
    st.write(f"📅 **Date : {datetime.now().strftime('%d/%m/%Y')}**")

st.title(f"🏛️ Espace {st.session_state.role}")

# --- LISTES DONNÉES ---
liste_assurances = ["Non assuré", "RCT", "Averis"]
liste_etats = sorted(["California", "Washington", "Texas", "New York", "Florida", "Quebec", "Ontario", "Nevada", "Colorado"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])

# --- ONGLETS ---
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers Permis", "💰 Banque Centrale", "📜 Logs Système"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation RCT"])
else:
    tabs = st.tabs(["🚗 Registre Véhicules", "💰 Mon Compte"])

# ==========================================
# 🚗 ONGLET : IMMATRICULATIONS (GRAS & GESTION)
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
            if st.form_submit_button("✅ Valider"):
                new_r = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "L'état de la plaque": e, "Numéro de la plaque": p, "Assurance": a}])
                conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_r], ignore_index=True))
                st.success("🎉 Enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    search = st.text_input("🔍 Rechercher (Plaque, Roblox ou Discord)").strip().lower()
    
    if not df_im.empty:
        mask = df_im.apply(lambda r: search in str(r).lower(), axis=1)
        for idx, row in df_im[mask].iterrows():
            with st.container(border=True):
                col_text, col_btn = st.columns([3, 1])
                # AFFICHAGE EN GRAS AVEC DATE
                col_text.markdown(f"### 🚗 **{row['Numéro de la plaque']}**")
                col_text.markdown(f"👤 **Propriétaire :** {row['Nom d\'utilisateur ROBLOX']}")
                col_text.markdown(f"🚘 **Véhicule :** {row['Marque du véhicule']} ({row['L\'état de la plaque']})")
                col_text.markdown(f"🛡️ **Assurance :** {row['Assurance']}")
                col_text.markdown(f"📅 **Date d'enregistrement :** {row['Horodateur']}")
                
                if st.session_state.role in ["Staff", "RCT"]:
                    if col_btn.button("⚙️ Modifier / Supprimer", key=f"edit_{idx}"):
                        st.session_state[f"mode_{idx}"] = not st.session_state.get(f"mode_{idx}", False)
                    
                    if st.session_state.get(f"mode_{idx}"):
                        with st.form(f"form_{idx}"):
                            new_p = st.text_input("Numéro de plaque", value=row['Numéro de la plaque'])
                            new_a = st.selectbox("Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']) if row['Assurance'] in liste_assurances else 0)
                            b_save, b_del = st.columns(2)
                            if b_save.form_submit_button("💾 Sauvegarder"):
                                df_im.at[idx, 'Numéro de la plaque'] = new_p
                                df_im.at[idx, 'Assurance'] = new_a
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.success("Mis à jour !"); time.sleep(1); st.rerun()
                            if b_del.form_submit_button("🗑️ Supprimer"):
                                df_im = df_im.drop(idx)
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.error("Supprimé."); time.sleep(1); st.rerun()

# ==========================================
# 💰 ONGLET : BANQUE & COMPTE
# ==========================================
with tabs[1]:
    df_b = get_data("Banque")
    if st.session_state.role == "Civil":
        s_civil = st.text_input("Entrez votre Pseudo (Roblox ou Discord)").strip().lower()
        if s_civil:
            res = df_b[df_b.apply(lambda r: s_civil in str(r).lower(), axis=1)]
            if not res.empty:
                st.metric("💵 Votre Solde Bancaire", f"{float(res.iloc[0]['Solde']):,.0f} $")
                # Affichage des points
                df_p = get_data("Points Permis")
                res_p = df_p[df_p.apply(lambda r: s_civil in str(r).lower(), axis=1)]
                if not res_p.empty: st.metric("🪪 Points de Permis", f"{res_p.iloc[0]['Points']} / 12")
            else: st.info("Compte non trouvé.")
    else:
        st.write("### 💳 Administration Financière")
        s_staff = st.text_input("🔍 Rechercher un compte").strip().lower()
        if s_staff:
            res_s = df_b[df_b.apply(lambda r: s_staff in str(r).lower(), axis=1)]
            for idx, row in res_s.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **{row['Nom Roblox']}**")
                    cur_s = float(row['Solde'])
                    st.write(f"💰 Solde actuel : **{cur_s:,.0f} $**")
                    with st.form(f"bank_{idx}"):
                        mt = st.number_input("Montant", min_value=0.0)
                        b1, b2 = st.columns(2)
                        if b1.form_submit_button("📉 Facturer"):
                            df_b.at[idx, 'Solde'] = cur_s - mt
                            if st.session_state.role == "RCT":
                                r_idx = df_b[df_b['Nom Roblox'].str.lower() == MON_PSEUDO_ROBLOX.lower()].index
                                if not r_idx.empty: df_b.at[r_idx[0], 'Solde'] = float(df_b.at[r_idx[0], 'Solde']) + mt
                            conn.update(worksheet="Banque", data=df_b)
                            st.rerun()
                        if b2.form_submit_button("📈 Ajouter") and st.session_state.role == "Staff":
                            df_b.at[idx, 'Solde'] = cur_s + mt
                            conn.update(worksheet="Banque", data=df_b)
                            st.rerun()

# 🪪 & 📜 STAFF ONLY
if st.session_state.role == "Staff":
    with tabs[2]: st.dataframe(get_data("Points Permis"), use_container_width=True)
    with tabs[3]: st.dataframe(get_data("Logs").iloc[::-1], use_container_width=True)

st.markdown("---")
st.markdown("<center><small>République de Californie RP | Système v9.24</small></center>", unsafe_allow_html=True)
