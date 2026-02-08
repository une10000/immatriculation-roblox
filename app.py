import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURATION PAGE (FIX TABS COUPÉS) ---
st.set_page_config(page_title="RCRP - Système Intégral", layout="wide")

# --- 2. STYLE CSS COMPLET (LOGO, TABS ET REÇU) ---
st.markdown("""
    <style>
    /* Empêche les onglets d'être coupés en haut */
    .block-container { 
        padding-top: 6rem !important; 
    }
    
    /* Fix Logo Sidebar - Taille stable */
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
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

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

# --- ONGLET 1 : IMMATRICULATIONS (ACCÈS TOTAL) ---
with tabs[0]:
    st.header("🚗 Registre des Véhicules")
    
    # Formulaire d'immatriculation accessible à TOUS
    with st.expander("➕ Enregistrer un véhicule", expanded=True):
        with st.form("form_immat_integral"):
            user_select = st.selectbox("Propriétaire", ["---"] + df_banque["Nom Roblox"].tolist())
            marque_v = st.text_input("Marque / Modèle")
            plaque_v = st.text_input("Plaque (ex: ABC-123)")
            assu_select = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            code_v = st.text_input("🔑 Code Secret (pour gérer le véhicule plus tard)", type="password")
            
            # Calculs des coûts
            cost_ville = 175
            cost_assu = 130 if "AVERIS" in assu_select else 150 if "RCT" in assu_select else 0
            
            # Promo Trio RCT (le 3ème est gratuit)
            rct_count = len(df_im[(df_im["Nom d'utilisateur ROBLOX"] == user_select) & (df_im["Assurance"].str.contains("RCT"))])
            if "RCT" in assu_select and rct_count >= 2:
                cost_assu = 0
                st.info("🎁 Offre Trio : Assurance gratuite pour ce véhicule !")

            # Taxe Jeune Conducteur (-1 mois)
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
                <b>📄 FACTURE DÉTAILLÉE</b><br>
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
                        # Prélèvement citoyen
                        df_banque.at[idx_user, "Solde"] = current_solde - total_facture
                        
                        # Virement Assurance
                        if "AVERIS" in assu_select:
                            idx_dest = df_banque[df_banque["Nom Roblox"] == TARGET_AVERIS].index[0]
                            df_banque.at[idx_dest, "Solde"] = float(df_banque.at[idx_dest, "Solde"]) + cost_assu
                        elif "RCT" in assu_select and cost_assu > 0:
                            idx_dest = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                            df_banque.at[idx_dest, "Solde"] = float(df_banque.at[idx_dest, "Solde"]) + cost_assu
                        
                        # Mise à jour Immat
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
                        st.success("Véhicule immatriculé avec succès !")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Solde bancaire insuffisant pour cette opération.")
                else:
                    st.warning("Veuillez remplir tous les champs (Propriétaire, Plaque, Code Secret).")

    # Liste des immatriculations avec recherche
    st.divider()
    search_query = st.text_input("🔍 Rechercher une Plaque ou un Nom").lower()
    if not df_im.empty:
        filtered_df = df_im[df_im.apply(lambda x: search_query in str(x).lower(), axis=1)]
        for i, row in filtered_df.iterrows():
            with st.container(border=True):
                st.markdown(f"<span class='badge-assu'>{row['Assurance']}</span>", unsafe_allow_html=True)
                st.write(f"🚗 **{row['Numéro de la plaque']}** | 👤 {row['Nom d\'utilisateur ROBLOX']} ({row['Marque du véhicule']})")
                
                with st.expander("⚙️ Options de gestion"):
                    check_code = st.text_input("Code Secret du véhicule", type="password", key=f"check_{i}")
                    if check_code == str(row['CODE']) or st.session_state.role == "Staff":
                        if st.button("🗑️ Supprimer l'immatriculation", key=f"del_{i}"):
                            updated_immat = df_im.drop(i)
                            conn.update(worksheet="Copie de Immatriculations", data=updated_immat)
                            st.success("Supprimé !")
                            st.rerun()

# --- ONGLET 2 : POINTS & DOSSIERS ---
with tabs[1]:
    st.header("🪪 Dossiers Citoyens")
    search_name = st.text_input("🔍 Tapez un Nom Roblox pour voir les points et le solde").lower()
    
    if search_name:
        # Affichage Points
        res_pts = df_pts[df_pts["Nom Roblox"].str.lower().str.contains(search_name, na=False)]
        if not res_pts.empty:
            for _, r in res_pts.iterrows():
                st.metric(f"Points de {r['Nom Roblox']}", f"{r['PTS']} / 25")
        
        # Affichage Solde (Accessible Civils)
        res_bq = df_banque[df_banque["Nom Roblox"].str.lower().str.contains(search_name, na=False)]
        if not res_bq.empty:
            st.metric(f"Solde Bancaire de {res_bq.iloc[0]['Nom Roblox']}", f"{float(res_bq.iloc[0]['Solde']):,.0f} $")
    
    if st.session_state.role == "Staff":
        st.divider()
        st.subheader("🛠️ Administration Staff")
        with st.expander("👤 Créer un nouveau profil"):
            with st.form("new_profile_form"):
                new_roblox = st.text_input("Pseudo Roblox")
                new_discord = st.text_input("Pseudo Discord")
                if st.form_submit_button("🚀 Créer le Dossier"):
                    creation_date = datetime.now().strftime("%d/%m/%Y")
                    # Ajout Banque
                    row_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": new_discord, "Nom Roblox": new_roblox, "Date d'arrivée": creation_date}])
                    # Ajout Points
                    row_p = pd.DataFrame([{"Nom Roblox": new_roblox, "PTS": 25}])
                    
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, row_b], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, row_p], ignore_index=True))
                    st.success("Profil créé avec succès !")
                    st.rerun()

# --- ONGLET 3 : BANQUE ---
with tabs[2]:
    st.header("💰 État de la Banque")
    if not search_name:
        st.info("Utilisez la barre de recherche dans l'onglet 'Dossiers & Points' pour consulter un compte.")
    else:
        # Doublon d'affichage ici pour plus de clarté
        res_bq_full = df_banque[df_banque["Nom Roblox"].str.lower().str.contains(search_name, na=False)]
        if not res_bq_full.empty:
            st.write(f"### Détails du compte : {res_bq_full.iloc[0]['Nom Roblox']}")
            st.write(f"💳 Solde : **{float(res_bq_full.iloc[0]['Solde']):,.0f} $**")
            st.write(f"📅 Arrivée : {res_bq_full.iloc[0]['Date d\'arrivée']}")

st.markdown("---")
st.markdown("<center><small>RCRP Système v12.7 | 2026</small></center>", unsafe_allow_html=True)
