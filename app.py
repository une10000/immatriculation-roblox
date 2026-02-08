import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Portail Officiel", layout="wide")

# --- STYLE CSS (ALIGNEMENT & LOGO) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        display: flex;
        flex-direction: column;
        height: 450px !important;
        justify-content: space-between;
    }
    .stMetric { background-color: #f8f9fb; padding: 15px; border-radius: 12px; border: 1px solid #e0e0e0; }
    [data-testid="stSidebar"] img { border-radius: 10px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "role" not in st.session_state:
    st.session_state.role = None

conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26" 
CODE_ENTREPRISE = "RCT-26-RCRPFR" 
MON_PSEUDO_ROBLOX = "une10000"

# LOGO RÉPARÉ
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=1100&height=608"

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
    st.title("🏛️ Portail des Services RCRP")
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("### 👤 Citoyen")
            st.write("Accès public : registres, banque et permis.")
            st.markdown("<br><br><br><br>", unsafe_allow_html=True)
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"; st.rerun()
    with col2:
        with st.container(border=True):
            st.markdown("### 🛠️ Entreprise (RCT)")
            st.write("Interface RCT : Facturation et Assurances.")
            c_rct = st.text_input("Code RCT", type="password", key="login_rct")
            if st.button("Connexion Pro", use_container_width=True):
                if c_rct == CODE_ENTREPRISE: st.session_state.role = "RCT"; st.rerun()
                else: st.error("❌ Code incorrect.")
    with col3:
        with st.container(border=True):
            st.markdown("### 👮 Autorités / Staff")
            st.write("Administration totale et Logs.")
            c_pol = st.text_input("Code Autorisation", type="password", key="login_staff")
            if st.button("Connexion Sécurisée", use_container_width=True):
                if c_pol == CODE_ADMIN_GENERAL: st.session_state.role = "Staff"; st.rerun()
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

st.title(f"🏛️ Espace {st.session_state.role}")

# --- LISTES ---
liste_assurances = ["Non assuré", "RCT", "Averis"]
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Revolt", "Turismo", "Roamer", "Envy", "Mizuhara"])

# --- ONGLETS ---
if st.session_state.role == "Staff": tabs = st.tabs(["🚗 Immat", "🪪 Permis", "💰 Banque", "📜 Logs"])
elif st.session_state.role == "RCT": tabs = st.tabs(["🚗 Immat", "💰 Facturation"])
else: tabs = st.tabs(["🚗 Registre", "💰 Mon Compte"])

# 🚗 ONGLET 1 : IMMATRICULATIONS (MODIF & SUPPR)
with tabs[0]:
    df_im = get_data("Copie de Immatriculations")
    with st.expander("➕ Enregistrer un véhicule"):
        with st.form("add_v"):
            u = st.text_input("👤 Pseudo Roblox")
            p = st.text_input("🔢 Plaque")
            m = st.selectbox("🚘 Marque", liste_marques)
            a = st.selectbox("🛡️ Assurance", liste_assurances)
            if st.form_submit_button("✅ Valider"):
                new_r = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "Numéro de la plaque": p, "Assurance": a}])
                conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_r], ignore_index=True))
                st.success("🎉 Enregistré !"); time.sleep(1); st.rerun()

    st.divider()
    # RECHERCHE FLEXIBLE (Roblox ou Discord ou Plaque)
    search = st.text_input("🔍 Rechercher un véhicule (Plaque, Nom, Discord...)").strip().lower()
    if not df_im.empty:
        mask = df_im.apply(lambda row: row.astype(str).str.lower().str.contains(search).any(), axis=1)
        results = df_im[mask]
        for idx, row in results.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"**🚗 {row['Numéro de la plaque']}** — {row['Nom d\'utilisateur ROBLOX']}")
                c1.write(f"🛡️ Assurance : {row['Assurance']} | 🚘 {row['Marque du véhicule']}")
                if st.session_state.role in ["Staff", "RCT"]:
                    if c2.button("⚙️ Gérer", key=f"edit_{idx}"):
                        st.session_state[f"mode_{idx}"] = not st.session_state.get(f"mode_{idx}", False)
                    if st.session_state.get(f"mode_{idx}"):
                        with st.form(f"f_{idx}"):
                            np = st.text_input("Plaque", value=row['Numéro de la plaque'])
                            na = st.selectbox("Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']) if row['Assurance'] in liste_assurances else 0)
                            b1, b2 = st.columns(2)
                            if b1.form_submit_button("💾 Sauver"):
                                df_im.at[idx, 'Numéro de la plaque'] = np
                                df_im.at[idx, 'Assurance'] = na
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.rerun()
                            if b2.form_submit_button("🗑️ Supprimer"):
                                df_im = df_im.drop(idx)
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.rerun()

# 💰 ONGLET 2 : BANQUE & FACTURATION
with tabs[1]:
    df_b = get_data("Banque")
    if st.session_state.role == "Civil":
        nom_c = st.text_input("Votre Pseudo (Roblox ou Discord)").strip().lower()
        if nom_c:
            # Recherche flexible
            res_b = df_b[df_b.apply(lambda r: nom_c in str(r).lower(), axis=1)]
            if not res_b.empty:
                st.metric("💵 Votre Solde", f"{float(res_b.iloc[0]['Solde']):,.0f} $")
                # Affichage des points si l'onglet banque est partagé (pour les civils)
                df_p = get_data("Points Permis")
                res_p = df_p[df_p.apply(lambda r: nom_c in str(r).lower(), axis=1)]
                if not res_p.empty: st.metric("🪪 Points Permis", f"{res_p.iloc[0]['Points']} / 12")
            else: st.info("Aucun compte trouvé.")
    else:
        st.write("### 💸 Système de Facturation")
        search_b = st.text_input("🔍 Rechercher un compte (Roblox/Discord)").strip().lower()
        if search_b:
            res_b = df_b[df_b.apply(lambda r: search_b in str(r).lower(), axis=1)]
            for idx, row in res_b.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **Compte : {row['Nom Roblox']}**")
                    solde_actuel = float(row['Solde'])
                    st.write(f"💰 Solde : {solde_actuel:,.0f} $")
                    with st.form(f"fact_{idx}"):
                        montant = st.number_input("Montant de la transaction", min_value=0.0)
                        btn1, btn2 = st.columns(2)
                        if btn1.form_submit_button("📉 Facturer"):
                            if st.session_state.role == "RCT": # Transfert vers RCT
                                df_b.at[idx, 'Solde'] = solde_actuel - montant
                                rct_idx = df_b[df_b['Nom Roblox'].str.lower() == MON_PSEUDO_ROBLOX.lower()].index
                                if not rct_idx.empty: df_b.at[rct_idx[0], 'Solde'] = float(df_b.at[rct_idx[0], 'Solde']) + montant
                            else: # Staff retire simplement
                                df_b.at[idx, 'Solde'] = solde_actuel - montant
                            conn.update(worksheet="Banque", data=df_b)
                            st.success("Transaction validée !"); st.rerun()
                        if btn2.form_submit_button("📈 Ajouter") and st.session_state.role == "Staff":
                            df_b.at[idx, 'Solde'] = solde_actuel + montant
                            conn.update(worksheet="Banque", data=df_b)
                            st.rerun()

# 📜 SECTIONS STAFF
if st.session_state.role == "Staff":
    with tabs[2]: # Déjà géré par Banque ci-dessus mais peut être séparé
        st.write("### 🪪 Gestion des Permis")
        st.dataframe(get_data("Points Permis"), use_container_width=True)
    with tabs[3]:
        st.write("### 📜 Logs Système")
        st.dataframe(get_data("Logs").iloc[::-1], use_container_width=True)

st.markdown("---")
st.markdown("<center><small>République de Californie RP | Système v9.23</small></center>", unsafe_allow_html=True)
