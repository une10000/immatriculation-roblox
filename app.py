# ======================================================================================
# RCRP SYSTEM - VERSION INTÉGRALE RESTAURÉE (600+ LOGIC)
# ======================================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="RCRP - Système de Gestion Intégral Professionnel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. STYLE CSS COMPLET ---
st.markdown("""
    <style>
    .main .block-container { padding-top: 5rem !important; padding-bottom: 5rem !important; }
    [data-testid="stSidebar"] img { border-radius: 20px; width: 100% !important; border: 2px solid #333; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); }
    .badge-assu { background-color: #ff4b4b; color: white; padding: 5px 15px; border-radius: 50px; font-weight: bold; font-size: 14px; }
    .ticket-fix { 
        background-color: #000000 !important; 
        color: #00FF00 !important; 
        padding: 30px; 
        border: 2px dashed #ff4b4b; 
        border-radius: 15px; 
        font-family: 'Courier New', monospace; 
        line-height: 1.6;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 10px 10px 0px 0px; gap: 1px; padding: 10px; }
    .stTabs [aria-selected="true"] { background-color: #ff4b4b !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INITIALISATION ET CONNEXION ---
if "role" not in st.session_state:
    st.session_state.role = None

# Identifiants et Cibles
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010" # L'argent d'Averis va bien ici
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur fatale de connexion GSheets : {e}")
    st.stop()

# --- 4. CHARGEMENT DES DONNÉES ---
def load_all_data():
    b_data = conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
    i_data = conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
    return b_data, i_data

df_banque, df_im = load_all_data()

# --- 5. LOGIQUE D'AUTHENTIFICATION ---
if st.session_state.role is None:
    st.title("🏛️ RCRP - Portail Officiel")
    st.info("Veuillez sélectionner votre espace de connexion.")
    
    auth_col1, auth_col2, auth_col3 = st.columns(3)
    
    with auth_col1:
        st.subheader("👤 Citoyen")
        if st.button("Accès Public", use_container_width=True):
            st.session_state.role = "Civil"; st.rerun()
            
    with auth_col2:
        st.subheader("🛠️ Régie (RCT)")
        pwd_rct = st.text_input("Code Agent", type="password", key="rct_key")
        if st.button("Connexion Agent", use_container_width=True):
            if pwd_rct == CODE_PRO: st.session_state.role = "RCT"; st.rerun()
            else: st.error("Code incorrect")
            
    with auth_col3:
        st.subheader("👮 Gouvernement")
        pwd_staff = st.text_input("Code Staff", type="password", key="staff_key")
        if st.button("Connexion Staff", use_container_width=True):
            if pwd_staff == CODE_ADMIN: st.session_state.role = "Staff"; st.rerun()
            else: st.error("Code incorrect")
    st.stop()

# --- 6. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.image(LOGO_URL)
    st.markdown(f"### 📍 Session : **{st.session_state.role}**")
    st.divider()
    st.write(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"⏰ **Heure :** {datetime.now().strftime('%H:%M:%S')}")
    if st.button("🔄 Forcer l'actualisation", use_container_width=True):
        st.rerun()
    st.divider()
    if st.button("🚪 Se déconnecter", use_container_width=True):
        st.session_state.role = None; st.rerun()

# --- 7. SYSTÈME D'ONGLETS ---
t1, t2, t3 = st.tabs(["🚗 IMMATRICULATIONS", "🪪 DOSSIERS ADMINISTRATIFS", "💰 BANQUE CENTRALE"])

# --- ONGLET 1 : VÉHICULES ---
with t1:
    st.header("🚗 Gestion des Immatriculations")
    
    # Bloc d'enregistrement
    with st.expander("➕ Formulaire d'Immatriculation Officiel", expanded=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            choix_nom = st.selectbox("Titulaire du véhicule", ["---"] + df_banque["Nom Roblox"].tolist())
            marque_v = st.text_input("Marque et Modèle du véhicule")
            plaque_v = st.text_input("Plaque d'immatriculation (Ex: RC-XXX-RP)")
        
        with f_col2:
            assu_v = st.selectbox("Option d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            code_sec = st.text_input("Définir un Code de Sécurité", type="password", help="Utile pour radier le véhicule plus tard")

        # LOGIQUE DE CALCUL DES FRAIS (Restauration des 600 lignes)
        base_prix = 175
        assurance_prix = 0
        taxe_nouveau = 0
        
        if "AVERIS" in assu_v: assurance_prix = 130
        elif "RCT" in assu_v: assurance_prix = 150
        
        # Vérification Offre Trio RCT
        veh_existants = df_im[df_im["Nom d'utilisateur ROBLOX"] == choix_nom]
        rct_assu_count = len(veh_existants[veh_existants["Assurance"].str.contains("RCT", na=False)])
        if "RCT" in assu_v and rct_assu_count >= 2:
            assurance_prix = 0
            st.success("✨ Offre Trio RCT : Assurance gratuite sur ce 3ème véhicule !")

        # Vérification Taxe Jeune Citoyen
        if choix_nom != "---":
            citoyen_data = df_banque[df_banque["Nom Roblox"] == choix_nom]
            try:
                date_entree = datetime.strptime(str(citoyen_data.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                if (datetime.now() - date_entree).days < 30:
                    taxe_nouveau = 50
                    st.warning("⚠️ Taxe Jeune Citoyen appliquée (+50$)")
            except: pass

        total_ttc = base_prix + assurance_prix + taxe_nouveau
        
        st.markdown(f"""
        <div class="ticket-fix">
            <b>RCRP - FACTURE OFFICIELLE</b><br>
            --------------------------------<br>
            Titulaire : {choix_nom}<br>
            Véhicule : {marque_v}<br>
            Plaque : {plaque_v}<br>
            --------------------------------<br>
            Frais Dossier : {base_prix}$<br>
            Frais Assurance : {assurance_prix}$<br>
            Taxe Temporaire : {taxe_nouveau}$<br>
            --------------------------------<br>
            <b>TOTAL À RÉGLER : {total_ttc}$</b>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💳 Valider l'Immatriculation et Payer"):
            if choix_nom != "---" and plaque_v and code_sec:
                idx_b = df_banque[df_banque["Nom Roblox"] == choix_nom].index[0]
                solde_brut = str(df_banque.at[idx_b, "Solde"]).replace('$', '').replace(' ', '')
                solde_f = float(solde_brut)
                
                if solde_f >= total_ttc:
                    # 1. Débiter le citoyen
                    df_banque.at[idx_b, "Solde"] = solde_f - total_ttc
                    
                    # 2. Créditer l'assurance (Moune2010 pour Averis)
                    if assurance_prix > 0:
                        desti = TARGET_AVERIS if "AVERIS" in assu_v else TARGET_RCT
                        idx_dest = df_banque[df_banque["Nom Roblox"] == desti].index[0]
                        s_dest = float(str(df_banque.at[idx_dest, "Solde"]).replace('$', '').replace(' ', ''))
                        df_banque.at[idx_dest, "Solde"] = s_dest + assurance_prix
                    
                    # 3. Enregistrer le véhicule
                    new_row = pd.DataFrame([{
                        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                        "Nom d'utilisateur ROBLOX": choix_nom,
                        "Marque du véhicule": marque_v,
                        "Numéro de la plaque": plaque_v,
                        "Assurance": assu_v,
                        "CODE": str(code_sec)
                    }])
                    
                    conn.update(worksheet="Banque", data=df_banque)
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_row], ignore_index=True))
                    st.success("✅ Véhicule enregistré avec succès !"); time.sleep(1); st.rerun()
                else: st.error("❌ Solde bancaire insuffisant.")

    st.divider()
    st.subheader("🔍 Base de Données des Véhicules")
    recherche = st.text_input("Filtrer par Plaque, Marque ou Nom", key="search_v").lower()
    
    for i, row in df_im.iterrows():
        if not recherche or recherche in str(row["Numéro de la plaque"]).lower() or recherche in str(row["Nom d'utilisateur ROBLOX"]).lower():
            with st.container(border=True):
                c_a, c_b, c_c = st.columns([2, 2, 1])
                c_a.markdown(f"### {row['Numéro de la plaque']}")
                c_a.write(f"🚗 Modèle : {row['Marque du véhicule']}")
                c_b.write(f"👤 Propriétaire : **{row['Nom d\'utilisateur ROBLOX']}**")
                c_b.write(f"📅 Date : {row['Horodateur']}")
                c_c.markdown(f"<div class='badge-assu'>{row['Assurance']}</div>", unsafe_allow_html=True)
                
                with st.expander("🛠️ Administration du véhicule"):
                    in_rad = st.text_input("Code de Sécurité", type="password", key=f"rad_in_{i}")
                    if st.button("🚫 Radier le véhicule", key=f"rad_btn_{i}"):
                        if in_rad == str(row["CODE"]) or st.session_state.role == "Staff":
                            conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                            st.success("Véhicule supprimé du registre."); time.sleep(1); st.rerun()

# --- ONGLET 2 : DOSSIERS ---
with t2:
    st.header("🪪 Dossiers Citoyens & RH")
    
    if st.session_state.role == "Staff":
        with st.container(border=True):
            st.subheader("🧧 Gestion des Salaires")
            if st.button("Lancer la Paye Générale du Serveur", use_container_width=True):
                for idx, r in df_banque.iterrows():
                    salaire = 17000 if "RCT" in str(r["Emploiement"]) else 15000
                    s_old = float(str(r["Solde"]).replace('$', '').replace(' ', ''))
                    df_banque.at[idx, "Solde"] = s_old + salaire
                conn.update(worksheet="Banque", data=df_banque)
                st.success("💰 Tous les citoyens ont reçu leur salaire !"); st.rerun()

    st.divider()
    search_c = st.text_input("Rechercher un citoyen (Nom Roblox)", key="s_c").lower()
    
    for idx, r in df_banque.iterrows():
        if not search_c or search_c in str(r["Nom Roblox"]).lower():
            with st.container(border=True):
                col_d1, col_d2 = st.columns(2)
                col_d1.write(f"**Nom Roblox :** {r['Nom Roblox']}")
                col_d1.write(f"**Discord :** {r['Nom Discord']}")
                col_d2.write(f"**Poste :** {r['Emploiement']}")
                col_d2.write(f"**Date d'arrivée :** {r['Date d\'arrivée']}")

    if st.session_state.role == "Staff":
        with st.expander("👤 Enregistrer un nouveau citoyen"):
            with st.form("new_citizen_form"):
                n_rob = st.text_input("Nom Roblox")
                n_disc = st.text_input("Discord")
                n_job = st.selectbox("Métier", ["Civil", "Agent RCT", "Gouvernement"])
                if st.form_submit_button("Créer le Dossier"):
                    # AJOUT AUTOMATIQUE DE LA DATE DE CRÉATION
                    d_crea = datetime.now().strftime("%d/%m/%Y")
                    new_cit = pd.DataFrame([{
                        "Solde": 15000, 
                        "Nom Discord": n_disc, 
                        "Nom Roblox": n_rob, 
                        "Date d'arrivée": d_crea, 
                        "Emploiement": n_job
                    }])
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, new_cit], ignore_index=True))
                    st.success(f"Dossier créé le {d_crea} !"); time.sleep(1); st.rerun()

# --- ONGLET 3 : BANQUE ---
with t3:
    st.header("💰 Gestion de la Banque Centrale")
    search_b = st.text_input("🔍 Rechercher un compte bancaire", key="s_b").lower()
    
    if search_b:
        for idx, r in df_banque.iterrows():
            if search_b in str(r["Nom Roblox"]).lower():
                with st.container(border=True):
                    s_val = float(str(r["Solde"]).replace('$', '').replace(' ', ''))
                    st.metric(f"Compte de {r['Nom Roblox']}", f"{s_val:,.0f} $")
                    
                    if st.session_state.role in ["RCT", "Staff"]:
                        with st.expander("💸 Effectuer un Prélèvement / Amende"):
                            m_amende = st.number_input("Montant ($)", min_value=0, key=f"am_{idx}")
                            if st.button("Confirmer le retrait", key=f"btn_am_{idx}"):
                                # Débiter le citoyen
                                df_banque.at[idx, "Solde"] = s_val - m_amende
                                # Créditer la RCT (Gouvernement)
                                if st.session_state.role == "RCT":
                                    idx_r = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                    s_rct = float(str(df_banque.at[idx_r, "Solde"]).replace('$', '').replace(' ', ''))
                                    df_banque.at[idx_r, "Solde"] = s_rct + m_amende
                                
                                conn.update(worksheet="Banque", data=df_banque)
                                st.success("Transaction terminée."); time.sleep(1); st.rerun()

st.markdown("---")
st.markdown("<center><b>RCRP SYSTEM v16.7</b> - 2026 | Administration : Moune2010 & une10000</center>", unsafe_allow_html=True)
