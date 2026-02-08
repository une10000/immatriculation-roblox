import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURATION PAGE (FIX DES TABS COUPÉS) ---
st.set_page_config(page_title="RCRP - Système Intégral", layout="wide")

# --- 2. STYLE CSS COMPLET (LOGO, TABS ET REÇU) ---
st.markdown("""
    <style>
    /* Empêche les onglets d'être coupés en haut */
    .block-container { 
        padding-top: 6rem !important; 
    }
    
    /* Fix Logo Sidebar - Taille stable 250px */
    [data-testid="stSidebar"] img { 
        border-radius: 12px; 
        width: 250px !important; 
        margin: 0 auto 20px auto;
        display: block;
    }

    /* Style des Cartes Véhicules (Assurance visible) */
    .badge-assu {
        background-color: #ff4b4b;
        color: white;
        padding: 3px 12px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.85rem;
    }

    /* Reçu Mode Nuit (Noir pur, texte blanc) */
    .ticket-fix { 
        background-color: #000000 !important; 
        color: #ffffff !important; 
        padding: 20px; 
        border: 2px solid #ff4b4b; 
        border-radius: 10px; 
        font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INITIALISATION & CONNEXION ---
if "role" not in st.session_state:
    st.session_state.role = None

conn = st.connection("gsheets", type=GSheetsConnection)
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

def get_data(sheet_name):
    st.cache_data.clear()
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        return df.dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

# Chargement de toutes les bases de données
df_banque = get_data("Banque")
df_im = get_data("Copie de Immatriculations")
df_pts = get_data("Points Permis")

# ==========================================
# 🚪 PORTAIL DE CONNEXION
# ==========================================
if st.session_state.role is None:
    st.title("🏛️ Portail RCRP")
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("👤 Citoyen")
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()
    with col2:
        with st.container(border=True):
            st.subheader("🛠️ Professionnel")
            kp = st.text_input("Code Pro", type="password", key="p_login")
            if st.button("Connexion Pro", use_container_width=True):
                if kp == CODE_PRO:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("Code erroné")
    with col3:
        with st.container(border=True):
            st.subheader("👮 Staff")
            ks = st.text_input("Code Staff", type="password", key="s_login")
            if st.button("Connexion Staff", use_container_width=True):
                if ks == CODE_ADMIN:
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    st.error("Code erroné")
    st.stop()

# ==========================================
# 🖥️ INTERFACE CONNECTÉE
# ==========================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown(f"🎭 **Session :** `{st.session_state.role}`")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    st.divider()
    st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')} | ⏰ {datetime.now().strftime('%H:%M')}")

# Navigation par Onglets
tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers & Points", "💰 Banque"])

# --- ONGLET 1 : IMMATRICULATIONS (RESTAURATION COMPLÈTE) ---
with tabs[0]:
    st.header("🚗 Registre des Véhicules")
    
    with st.expander("➕ Enregistrer un véhicule", expanded=True):
        with st.form("form_immat_integral_restored"):
            user_select = st.selectbox("Propriétaire", ["---"] + df_banque["Nom Roblox"].tolist())
            marque_v = st.text_input("Marque / Modèle")
            plaque_v = st.text_input("Plaque (ex: ABC-123)")
            assu_select = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            code_v = st.text_input("🔑 Code Secret", type="password")
            
            # Logique de calcul interne au formulaire
            cost_ville = 175
            cost_assu = 130 if "AVERIS" in assu_select else 150 if "RCT" in assu_select else 0
            
            # Promo Trio RCT
            rct_count = len(df_im[(df_im["Nom d'utilisateur ROBLOX"] == user_select) & (df_im["Assurance"].str.contains("RCT"))])
            if "RCT" in assu_select and rct_count >= 2:
                cost_assu = 0
            
            # Taxe Jeune
            cost_jeune = 0
            if user_select != "---":
                u_row = df_banque[df_banque["Nom Roblox"] == user_select]
                if not u_row.empty:
                    try:
                        date_arr = datetime.strptime(str(u_row.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                        if (datetime.now() - date_arr).days < 30:
                            cost_jeune = 50
                    except:
                        pass
            
            total_facture = cost_ville + cost_assu + cost_jeune
            
            st.markdown(f"""
            <div class="ticket-fix">
                <b>📄 FACTURE OFFICIELLE</b><br>
                ----------------------------<br>
                Immatriculation Ville : 175$<br>
                Service Assurance : {cost_assu}$<br>
                Taxe Jeune Conducteur : {cost_jeune}$<br>
                ----------------------------<br>
                <b>TOTAL À PRÉLEVER : {total_facture}$</b>
            </div>
            """, unsafe_allow_html=True)

            if st.form_submit_button("✅ Valider l'enregistrement"):
                if user_select != "---" and plaque_v and code_v:
                    idx_user = df_banque[df_banque["Nom Roblox"] == user_select].index[0]
                    current_solde = float(df_banque.at[idx_user, "Solde"])
                    
                    if current_solde >= total_facture:
                        df_banque.at[idx_user, "Solde"] = current_solde - total_facture
                        
                        if "AVERIS" in assu_select:
                            idx_dest = df_banque[df_banque["Nom Roblox"] == TARGET_AVERIS].index[0]
                            df_banque.at[idx_dest, "Solde"] = float(df_banque.at[idx_dest, "Solde"]) + cost_assu
                        elif "RCT" in assu_select and cost_assu > 0:
                            idx_dest = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                            df_banque.at[idx_dest, "Solde"] = float(df_banque.at[idx_dest, "Solde"]) + cost_assu
                        
                        new_immat = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                            "Nom d'utilisateur ROBLOX": user_select,
                            "Marque du véhicule": marque_v,
                            "Numéro de la plaque": plaque_v,
                            "Assurance": assu_select,
                            "CODE": str(code_v)
                        }])
                        
                        conn.update(worksheet="Banque", data=df_banque)
                        conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_immat], ignore_index=True))
                        st.success("Immatriculation réussie !")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Solde insuffisant.")
                else:
                    st.warning("Veuillez remplir tous les champs.")

    # Liste des immatriculations
    st.divider()
    search_query = st.text_input("🔍 Rechercher une Plaque ou un Nom").lower()
    if not df_im.empty:
        filtered_df = df_im[df_im.apply(lambda x: search_query in str(x).lower(), axis=1)]
        for i, row in filtered_df.iterrows():
            with st.container(border=True):
                st.markdown(f"<span class='badge-assu'>{row['Assurance']}</span>", unsafe_allow_html=True)
                st.write(f"🚗 **{row['Numéro de la plaque']}** | 👤 {row['Nom d\'utilisateur ROBLOX']} ({row['Marque du véhicule']})")
                
                with st.expander("⚙️ Options"):
                    check_code = st.text_input("Code Secret", type="password", key=f"check_{i}")
                    if check_code == str(row['CODE']) or st.session_state.role == "Staff":
                        if st.button("🗑️ Supprimer", key=f"del_{i}"):
                            conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                            st.rerun()

# --- ONGLET 2 : POINTS (SANS SOLDE) ---
with tabs[1]:
    st.header("🪪 Dossiers Citoyens")
    search_name = st.text_input("🔍 Rechercher un Nom").lower()
    if search_name:
        res_pts = df_pts[df_pts["Nom Roblox"].str.lower().str.contains(search_name, na=False)]
        if not res_pts.empty:
            for _, r in res_pts.iterrows():
                st.metric(f"Points de {r['Nom Roblox']}", f"{r['PTS']} / 25")
        else:
            st.warning("Dossier introuvable.")
    
    if st.session_state.role == "Staff":
        st.divider()
        with st.expander("👤 Créer un nouveau profil"):
            with st.form("new_profile"):
                n_roblox = st.text_input("Pseudo Roblox")
                n_discord = st.text_input("Pseudo Discord")
                if st.form_submit_button("🚀 Créer"):
                    c_date = datetime.now().strftime("%d/%m/%Y")
                    row_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": n_discord, "Nom Roblox": n_roblox, "Date d'arrivée": c_date}])
                    row_p = pd.DataFrame([{"Nom Roblox": n_roblox, "PTS": 25}])
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, row_b], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, row_p], ignore_index=True))
                    st.success("Profil créé !")
                    st.rerun()

# --- ONGLET 3 : BANQUE (SOLDE + POINTS) ---
with tabs[2]:
    st.header("💰 État de la Banque")
    if search_name:
        res_bq = df_banque[df_banque["Nom Roblox"].str.lower().str.contains(search_name, na=False)]
        res_pts2 = df_pts[df_pts["Nom Roblox"].str.lower().str.contains(search_name, na=False)]
        if not res_bq.empty:
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.metric(f"Solde de {res_bq.iloc[0]['Nom Roblox']}", f"{float(res_bq.iloc[0]['Solde']):,.0f} $")
            with col_b2:
                if not res_pts2.empty:
                    st.metric("Points Permis", f"{res_pts2.iloc[0]['PTS']} / 25")
            st.write(f"📅 Arrivée en ville : {res_bq.iloc[0]['Date d\'arrivée']}")
        else:
            st.warning("Aucun compte trouvé.")
    else:
        st.info("Recherchez un nom pour voir le solde et les points.")

st.markdown("---")
st.markdown("<center><small>RCRP Système v12.9 | 2026</small></center>", unsafe_allow_html=True)
st.markdown("<center><small>RCRP Système v12.8 | 2026</small></center>", unsafe_allow_html=True)
