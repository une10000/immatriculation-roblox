import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURATION PAGE ---
st.set_page_config(
    page_title="RCRP - Système Intégral",
    layout="wide"
)

# --- 2. STYLE CSS COMPLET (DÉPLOYÉ) ---
st.markdown("""
    <style>
    /* Correction de l'affichage des onglets */
    .block-container { 
        padding-top: 6rem !important; 
    }
    
    /* Logo Sidebar Haute Définition */
    [data-testid="stSidebar"] img { 
        border-radius: 12px; 
        width: 250px !important; 
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 20px;
        display: block;
    }

    /* Badge pour l'état de l'assurance */
    .badge-assu {
        background-color: #ff4b4b;
        color: white;
        padding: 3px 12px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.85rem;
    }

    /* Style du reçu noir (Mode Nuit) */
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

# Paramètres de redirection financière
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"

# Codes de sécurité
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"

# Lien Image Logo
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

# Fonction de récupération des données
def get_data(sheet_name):
    st.cache_data.clear()
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        return df.dropna(how='all').fillna("")
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        return pd.DataFrame()

# Chargement des bases
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
            st.subheader("🛠️ Employés RCT")
            kp = st.text_input("Code d'accès", type="password", key="p_login")
            if st.button("Connexion Pro", use_container_width=True):
                if kp == CODE_PRO:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("Code erroné")
                    
    with col3:
        with st.container(border=True):
            st.subheader("👮 Gouvernement")
            ks = st.text_input("Code d'accès", type="password", key="s_login")
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
    st.write(f"📅 Date : {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"⏰ Heure : {datetime.now().strftime('%H:%M')}")

# Navigation par Onglets
tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers & Points", "💰 Banque"])

# --- ONGLET 1 : IMMATRICULATIONS (LOGIQUE LONGUE) ---
with tabs[0]:
    st.header("🚗 Registre des Véhicules")
    
    with st.expander("➕ Enregistrer un véhicule", expanded=True):
        # Widgets hors formulaire pour l'actualisation du prix RCT/AVERIS en direct
        user_select = st.selectbox("Propriétaire", ["---"] + df_banque["Nom Roblox"].tolist())
        marque_v = st.text_input("Marque / Modèle du véhicule")
        plaque_v = st.text_input("Numéro de la plaque (ex: ABC-123)")
        assu_select = st.selectbox("Type d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
        code_v = st.text_input("🔑 Code Secret du véhicule (Indispensable)", type="password")
        
        # --- LOGIQUE DE CALCUL DÉTAILLÉE ---
        cost_ville = 175
        cost_assu = 0
        
        if "AVERIS" in assu_select:
            cost_assu = 130
        elif "RCT" in assu_select:
            cost_assu = 150
            
        # Promo Trio RCT (le 3ème véhicule assuré chez RCT est gratuit)
        rct_count = len(df_im[(df_im["Nom d'utilisateur ROBLOX"] == user_select) & (df_im["Assurance"].str.contains("RCT"))])
        if "RCT" in assu_select and rct_count >= 2:
            cost_assu = 0
            st.success("🎁 Offre Trio : 3ème assurance gratuite chez RCT !")

        # Taxe Jeune Conducteur (Moins de 30 jours en ville)
        cost_jeune = 0
        if user_select != "---":
            u_row = df_banque[df_banque["Nom Roblox"] == user_select]
            if not u_row.empty:
                try:
                    date_arr = datetime.strptime(str(u_row.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                    delta_jours = (datetime.now() - date_arr).days
                    if delta_jours < 30:
                        cost_jeune = 50
                except Exception:
                    pass
        
        total_facture = cost_ville + cost_assu + cost_jeune
        
        # Affichage du reçu (Noir)
        st.markdown(f"""
        <div class="ticket-fix">
            <b>📄 REÇU DE PAIEMENT - RCRP</b><br>
            --------------------------------<br>
            Frais d'Immatriculation : 175$<br>
            Service Assurance : {cost_assu}$<br>
            Taxe Jeune Conducteur : {cost_jeune}$<br>
            --------------------------------<br>
            <b>TOTAL À PRÉLEVER : {total_facture}$</b>
        </div>
        """, unsafe_allow_html=True)

        # Validation du paiement
        if st.button("✅ Valider l'enregistrement et Payer"):
            if user_select != "---" and plaque_v and code_v:
                idx_user = df_banque[df_banque["Nom Roblox"] == user_select].index[0]
                current_solde = float(df_banque.at[idx_user, "Solde"])
                
                if current_solde >= total_facture:
                    # Débit du compte citoyen
                    df_banque.at[idx_user, "Solde"] = current_solde - total_facture
                    
                    # Virement aux comptes entreprises (RCT ou Averis)
                    dest_account = None
                    if "AVERIS" in assu_select:
                        dest_account = TARGET_AVERIS
                    elif "RCT" in assu_select:
                        dest_account = TARGET_RCT
                    
                    if dest_account and cost_assu > 0:
                        idx_dest = df_banque[df_banque["Nom Roblox"] == dest_account].index[0]
                        df_banque.at[idx_dest, "Solde"] = float(df_banque.at[idx_dest, "Solde"]) + cost_assu
                    
                    # Création de la nouvelle ligne d'immatriculation
                    new_immat = pd.DataFrame([{
                        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                        "Nom d'utilisateur ROBLOX": user_select,
                        "Marque du véhicule": marque_v,
                        "Numéro de la plaque": plaque_v,
                        "Assurance": assu_select,
                        "CODE": str(code_v)
                    }])
                    
                    # Mise à jour des Google Sheets
                    conn.update(worksheet="Banque", data=df_banque)
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_immat], ignore_index=True))
                    
                    st.success("Opération réussie ! Le véhicule est enregistré.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Solde bancaire insuffisant.")
            else:
                st.warning("Veuillez remplir les informations obligatoires (Propriétaire, Plaque, Code Secret).")

    # Affichage de la liste existante
    st.divider()
    search_q = st.text_input("🔍 Rechercher une plaque ou un propriétaire").lower()
    
    if not df_im.empty:
        filtered_im = df_im[df_im.apply(lambda x: search_q in str(x).lower(), axis=1)]
        
        for i, row in filtered_im.iterrows():
            with st.container(border=True):
                st.markdown(f"<span class='badge-assu'>{row['Assurance']}</span>", unsafe_allow_html=True)
                st.write(f"🚗 **Plaque : {row['Numéro de la plaque']}**")
                st.write(f"👤 Propriétaire : {row['Nom d\'utilisateur ROBLOX']} | Modèle : {row['Marque du véhicule']}")
                
                with st.expander("⚙️ Options de gestion"):
                    check_code = st.text_input("Entrer le Code Secret", type="password", key=f"manage_{i}")
                    if check_code == str(row['CODE']) or st.session_state.role == "Staff":
                        if st.button("🗑️ Supprimer l'immatriculation", key=f"del_{i}"):
                            new_df_im = df_im.drop(i)
                            conn.update(worksheet="Copie de Immatriculations", data=new_df_im)
                            st.success("Supprimé !")
                            st.rerun()

# --- ONGLET 2 : POINTS (RECHERCHE CROISÉE DISCORD/ROBLOX) ---
with tabs[1]:
    st.header("🪪 Dossiers Citoyens")
    
    query_pts = st.text_input("🔍 Rechercher par Pseudo Roblox ou Discord (Points)").lower()
    
    if query_pts:
        # On cherche d'abord dans la banque pour lier Roblox et Discord
        matches = df_banque[
            (df_banque["Nom Roblox"].str.lower().str.contains(query_pts, na=False)) | 
            (df_banque["Nom Discord"].str.lower().str.contains(query_pts, na=False))
        ]
        
        if not matches.empty:
            for _, citoyen in matches.iterrows():
                # On récupère ses points dans la table Points
                pts_data = df_pts[df_pts["Nom Roblox"] == citoyen["Nom Roblox"]]
                if not pts_data.empty:
                    st.metric(
                        label=f"Points de {citoyen['Nom Roblox']} (@{citoyen['Nom Discord']})", 
                        value=f"{pts_data.iloc[0]['PTS']} / 25"
                    )
        else:
            st.warning("Aucun dossier trouvé pour cette recherche.")
    
    # Section Création (Staff seulement)
    if st.session_state.role == "Staff":
        st.divider()
        with st.expander("👤 Créer un nouveau profil citoyen"):
            with st.form("creation_profil_form"):
                new_rob = st.text_input("Nom d'utilisateur Roblox")
                new_disc = st.text_input("Nom d'utilisateur Discord")
                
                if st.form_submit_button("🚀 Créer le dossier complet"):
                    # Date d'arrivée automatique
                    current_date = datetime.now().strftime("%d/%m/%Y")
                    
                    # Préparation des lignes
                    new_bank_row = pd.DataFrame([{
                        "Solde": 15000, 
                        "Nom Discord": new_disc, 
                        "Nom Roblox": new_rob, 
                        "Date d'arrivée": current_date
                    }])
                    
                    new_pts_row = pd.DataFrame([{
                        "Nom Roblox": new_rob, 
                        "PTS": 25
                    }])
                    
                    # Envoi vers Google Sheets
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, new_bank_row], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_pts_row], ignore_index=True))
                    
                    st.success(f"Profil créé pour {new_rob} à la date du {current_date} !")
                    time.sleep(1)
                    st.rerun()

# --- ONGLET 3 : BANQUE (RECHERCHE CROISÉE + POINTS) ---
with tabs[2]:
    st.header("💰 État de la Banque")
    
    # Barre de recherche spécifique pour le solde
    query_bank = st.text_input("🔍 Rechercher par Pseudo Roblox ou Discord (Banque)").lower()
    
    if query_bank:
        # Recherche croisée Roblox ou Discord
        res_bank = df_banque[
            (df_banque["Nom Roblox"].str.lower().str.contains(query_bank, na=False)) | 
            (df_banque["Nom Discord"].str.lower().str.contains(query_bank, na=False))
        ]
        
        if not res_bank.empty:
            for _, row_b in res_bank.iterrows():
                with st.container(border=True):
                    st.subheader(f"👤 {row_b['Nom Roblox']} (@{row_b['Nom Discord']})")
                    
                    col_solde, col_pts_bank = st.columns(2)
                    
                    with col_solde:
                        st.metric(
                            label="Solde Bancaire", 
                            value=f"{float(row_b['Solde']):,.0f} $"
                        )
                        
                    with col_pts_bank:
                        # On affiche aussi les points ici pour la banque
                        pts_info = df_pts[df_pts["Nom Roblox"] == row_b["Nom Roblox"]]
                        if not pts_info.empty:
                            st.metric(
                                label="Points de Permis", 
                                value=f"{pts_info.iloc[0]['PTS']} / 25"
                            )
                    
                    st.write(f"📅 Date d'arrivée enregistrée : {row_b['Date d\'arrivée']}")
        else:
            st.warning("Aucun compte bancaire trouvé.")
    else:
        st.info("Veuillez entrer un nom pour consulter un compte.")

# --- FOOTER ---
st.markdown("---")
st.markdown("<center><small>RCRP Système de Gestion Intégral v13.3 | 2026</small></center>", unsafe_allow_html=True)
