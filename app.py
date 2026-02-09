# ======================================================================================
# PROJECT       : RCRP FR OS - ULTIMATE TOTAL EDITION
# VERSION       : 34.5.0
# BUILD DATE    : 09/02/2026
# ======================================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random

# ======================================================================================
# 1. INTERFACE & DESIGN SYSTEM (BORDURES NOIRES 2PX)
# ======================================================================================

st.set_page_config(
    page_title="RCRP FR OS - SYSTÈME NATIONAL",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Global Styles */
    .main { background-color: #f8f9fa; }
    
    /* Inputs avec bordures noires massives pour captures d'écran */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, 
    .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
        border: 2px solid #000000 !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* En-tête RCRP FR */
    .header-box {
        background: linear-gradient(90deg, #121212 0%, #2c3e50 100%);
        color: #ffffff;
        padding: 35px;
        border-radius: 12px;
        border-left: 20px solid #d32f2f;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }

    /* Info Cards pour instructions */
    .info-card {
        background-color: #ffffff;
        padding: 20px;
        border: 1px solid #dee2e6;
        border-left: 5px solid #d32f2f;
        margin-bottom: 20px;
    }

    /* Reçu Fédéral (Look Officiel) */
    .receipt-container {
        background-color: #ffffff;
        padding: 30px;
        border: 4px double #000000;
        font-family: 'Courier New', Courier, monospace;
        color: #000;
        box-shadow: 10px 10px 0px #000000;
    }
    
    .receipt-title { 
        text-align: center; 
        font-weight: 900; 
        font-size: 1.4em; 
        text-decoration: underline;
    }

    /* Boutons RCRP */
    .stButton>button {
        border: 2px solid #000 !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        height: 3.8em;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #000 !important;
        color: #fff !important;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# ======================================================================================
# 2. MOTEUR DE DONNÉES (CLOUD SYNC)
# ======================================================================================

cloud_conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def fetch_database():
    """Récupération synchronisée de toutes les tables"""
    try:
        df_bank = cloud_conn.read(worksheet="Banque").dropna(how='all').fillna("")
        df_immat = cloud_conn.read(worksheet="Copie de Immatriculations").dropna(how='all').fillna("")
        df_pts = cloud_conn.read(worksheet="Points Permis").dropna(how='all').fillna("")
        return df_bank, df_immat, df_pts
    except Exception as e:
        st.error(f"⚠️ ERREUR DE LIAISON BDD : {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_b, df_i, df_p = fetch_database()

# ======================================================================================
# 3. ÉTAT DE LA SESSION & SÉCURITÉ
# ======================================================================================

if "user_auth" not in st.session_state: st.session_state.user_auth = None
if "last_action" not in st.session_state: st.session_state.last_action = None
if "audit_logs" not in st.session_state: st.session_state.audit_logs = []

# Paramètres Banques Centrales
ACC_RCT = "une10000"
ACC_AVERIS = "Moune2010"

# Codes de Service
KEY_RCT = "RCT-26-RCRPFR"
KEY_STAFF = "RCRPFR-25-26"

def record_log(user, action):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.audit_logs.append(f"[{now}] {user} : {action}")

# ======================================================================================
# 4. SIDEBAR CONDITIONNELLE (LOGO & INFOS)
# ======================================================================================

if st.session_state.user_auth is not None:
    with st.sidebar:
        # LOGO RCRP
        st.image("https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=698a61b3&is=69891033&hm=8210184eaca7e5b311b5e00c11ba2e30e86bd67228f54e1f148577592ecfb090&=&format=webp&quality=lossless&width=2732&height=1508", use_container_width=True)
        
        st.divider()
        # HEURE ET DATE A GAUCHE
        t_now = datetime.now()
        st.markdown(f"### 📅 {t_now.strftime('%d/%m/%Y')}")
        st.markdown(f"### ⏰ {t_now.strftime('%H:%M:%S')}")
        st.divider()
        
        st.write(f"🔐 Accréditation : **{st.session_state.user_auth}**")
        
        if st.button("🔄 FORCER SYNCHRO"):
            st.cache_data.clear()
            record_log(st.session_state.user_auth, "Synchro Cloud Manuelle")
            st.rerun()
            
        if st.button("🚪 DÉCONNEXION"):
            record_log(st.session_state.user_auth, "Déconnexion")
            st.session_state.user_auth = None
            st.rerun()
        
        st.divider()
        st.caption("📜 JOURNAUX D'AUDIT (SESSION)")
        for log in reversed(st.session_state.audit_logs[-8:]):
            st.caption(log)

# ======================================================================================
# 5. LOCKSCREEN (CONNEXION)
# ======================================================================================

if st.session_state.user_auth is None:
    st.markdown("""
        <div class="header-box">
            <center>
                <h1>🏛️ RÉPUBLIQUE DE RENSSELAER</h1>
                <p style="font-size: 1.2em;">TERMINAL FÉDÉRAL D'OPÉRATIONS NATIONALES</p>
                <hr style="border-color: rgba(255,255,255,0.2);">
                <small>VERSION 34.5.0 | SÉCURISÉ PAR PROTOCOLE RCRP-OS</small>
            </center>
        </div>
    """, unsafe_allow_html=True)
    
    st.warning("⚠️ **AVERTISSEMENT :** Toute action effectuée sur ce terminal est enregistrée. L'usurpation d'identité d'agent est punie par la loi fédérale.")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("### 👥 CIVIL")
        st.write("Accès libre pour consultation et immatriculation.")
        if st.button("ACCÉDER AU TERMINAL"):
            st.session_state.user_auth = "Civil"
            record_log("Civil", "Connexion Public")
            st.rerun()
            
    with c2:
        st.markdown("### 👮 AGENT RCT")
        login_rct = st.text_input("Identifiant Agent", type="password")
        if st.button("AUTHENTIFICATION RCT"):
            if login_rct == KEY_RCT:
                st.session_state.user_auth = "RCT"
                record_log("RCT", "Connexion Service")
                st.rerun()
            else: st.error("Clé invalide.")
            
    with c3:
        st.markdown("### 🛡️ STAFF")
        login_staff = st.text_input("Clé Maîtresse", type="password")
        if st.button("ACCÈS ADMINISTRATEUR"):
            if login_staff == KEY_STAFF:
                st.session_state.user_auth = "Staff"
                record_log("Staff", "Connexion Admin")
                st.rerun()
            else: st.error("Accès refusé.")
    st.stop()

# ======================================================================================
# 6. MODULE : DOSSIER CITOYEN UNIFIÉ (VISIBILITÉ TOTALE)
# ======================================================================================

st.markdown('<div class="header-box"><h2>📂 REGISTRE NATIONAL DES CITOYENS</h2></div>', unsafe_allow_html=True)

with st.container():
    st.markdown("""
    <div class="info-card">
        <b>GUIDE DE RECHERCHE :</b> Sélectionnez un nom dans la liste déroulante pour extraire instantanément le dossier financier, 
        le casier de conduite et les titres de propriété de véhicules.
    </div>
    """, unsafe_allow_html=True)
    
    search_list = ["---"] + sorted(df_b["Nom Roblox"].unique().tolist())
    target = st.selectbox("Sélectionner un citoyen :", search_list)
    
    if target != "---":
        col1, col2, col3 = st.columns(3)
        
        # Section Points & Permis
        with col1:
            p_data = df_p[df_p["Nom Roblox"] == target]
            if not p_data.empty:
                pts_val = int(p_data.iloc[0]["PTS"])
                st.metric("POINTS PERMIS", f"{pts_val}/25")
                status_color = "green" if pts_val > 0 else "red"
                st.markdown(f"Statut : <b style='color:{status_color};'>{'VALIDE' if pts_val > 0 else 'SUSPENDU'}</b>", unsafe_allow_html=True)
            else: st.error("Aucun permis trouvé.")
            
        # Section Banque
        with col2:
            b_data = df_b[df_b["Nom Roblox"] == target]
            if not b_data.empty:
                st.metric("SOLDE BANCAIRE", f"{b_data.iloc[0]['Solde']}$")
                st.write(f"🏢 Métier : **{b_data.iloc[0]['Emploiement']}**")
                st.caption(f"📅 Date d'arrivée : {b_data.iloc[0]['Date d\'arrivée']}")
            else: st.error("Aucun compte bancaire.")
            
        # Section Véhicules
        with col3:
            v_data = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
            st.write(f"🚘 **VÉHICULES ({len(v_data)})**")
            if not v_data.empty:
                for _, veh in v_data.iterrows():
                    st.caption(f"• **{veh['Numéro de la plaque']}** — {veh['Marque du véhicule']}")
            else: st.write("Aucun véhicule enregistré.")

st.divider()

# ======================================================================================
# 7. LOGIQUE DES ONGLETS (RESTREINTS PAR GRADE)
# ======================================================================================

# Définition des étiquettes d'onglets selon le grade
tab_labels = ["🚗 IMMATRICULATION"]
if st.session_state.user_auth in ["RCT", "Staff"]: tab_labels.append("👮 SERVICES AGENT")
if st.session_state.user_auth == "Staff": tab_labels.append("🛠️ ADMINISTRATION")

tabs = st.tabs(tab_labels)

# --- ONGLET 1 : IMMATRICULATION & RADIATION ---
with tabs[0]:
    st.markdown("### 📝 Gestion des Titres de Circulation")
    st.write("Formulaire officiel pour l'enregistrement de véhicules civils et demandes de radiation.")
    
    col_f, col_t = st.columns([1.3, 1])
    
    with col_f:
        with st.container(border=True):
            f_owner = st.selectbox("Propriétaire du véhicule", ["---"] + df_b["Nom Roblox"].tolist())
            f_model = st.text_input("Marque & Modèle précis")
            f_plate = st.text_input("Numéro de Plaque souhaité").upper()
            f_assu = st.selectbox("Type d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            f_code = st.text_input("Définir un Code de Radiation (Secret)", type="password")
            
            # --- AJOUT DE LA MENTION JEUNE CONDUCTEUR ---
            f_jeune = st.checkbox("Mention Jeune Conducteur (Affiche ⚠️ sur le reçu)")
            
            # Calcul financier dynamique
            taxe_gouv = 175
            taxe_assu = 130 if "AVERIS" in f_assu else (150 if "RCT" in f_assu else 0)
            
            # Bonus "Trio RCT" (3ème voiture assurance offerte)
            if "RCT" in f_assu and f_owner != "---":
                if len(df_i[df_i["Nom d'utilisateur ROBLOX"] == f_owner]) >= 2:
                    taxe_assu = 0
                    st.success("🎁 BONUS : Assurance offerte (Trio RCT)")

            total_bill = taxe_gouv + taxe_assu
            
            if st.button(f"S'ACQUITTER DE {total_bill}$ ET ENREGISTRER", use_container_width=True):
                if f_owner != "---" and f_plate and f_code:
                    # Vérif Doublon Plaque
                    if f_plate in df_i["Numéro de la plaque"].astype(str).values:
                        st.error("❌ Cette plaque est déjà attribuée.")
                    else:
                        u_idx = df_b[df_b["Nom Roblox"] == f_owner].index[0]
                        u_solde = float(str(df_b.at[u_idx, "Solde"]).replace('$', ''))
                        
                        if u_solde >= total_bill:
                            # Débit Propriétaire
                            df_b.at[u_idx, "Solde"] = u_solde - total_bill
                            # Crédit Assureur
                            if taxe_assu > 0:
                                target_acc = ACC_AVERIS if "AVERIS" in f_assu else ACC_RCT
                                a_idx = df_b[df_b["Nom Roblox"] == target_acc].index[0]
                                df_b.at[a_idx, "Solde"] = float(str(df_b.at[a_idx, "Solde"]).replace('$', '')) + taxe_assu
                            
                            # Création Entrée
                            new_row = pd.DataFrame([{
                                "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                                "Nom d'utilisateur ROBLOX": f_owner,
                                "Marque du véhicule": f_model,
                                "Numéro de la plaque": f_plate,
                                "Assurance": f_assu,
                                "CODE": f_code
                            }])
                            
                            cloud_conn.update(worksheet="Banque", data=df_b)
                            cloud_conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_i, new_row]))
                            
                            # Stockage de l'action avec l'info 'jeune' pour le ticket
                            st.session_state.last_action = {
                                "nom": f_owner, 
                                "plq": f_plate, 
                                "mod": f_model, 
                                "prix": total_bill,
                                "jeune": f_jeune # On sauve l'info ici
                            }
                            
                            record_log(st.session_state.user_auth, f"Immat {f_plate} pour {f_owner}")
                            st.cache_data.clear(); st.rerun()
                        else: st.error("❌ Solde bancaire insuffisant.")
                else: st.warning("⚠️ Veuillez remplir tous les champs.")

        st.divider()
        st.markdown("#### 🗑️ Radiation de Plaque")
        rad_plate = st.text_input("Plaque à radier", key="rad_plate").upper()
        rad_key = st.text_input("Code de sécurité", type="password", key="rad_key")
        if st.button("RADIER LE VÉHICULE DU REGISTRE", use_container_width=True):
            match = df_i[df_i["Numéro de la plaque"].astype(str).str.upper() == rad_plate]
            if not match.empty:
                if str(rad_key) == str(match.iloc[0]["CODE"]) or st.session_state.user_auth == "Staff":
                    df_i = df_i.drop(match.index[0])
                    cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i)
                    record_log(st.session_state.user_auth, f"Radiation plaque {rad_plate}")
                    st.cache_data.clear(); st.success("Véhicule radié avec succès."); time.sleep(1); st.rerun()
                else: st.error("Code de sécurité incorrect.")
            else: st.error("Plaque introuvable.")

        st.divider()
        st.markdown("#### 🗑️ Radiation de Plaque")
        rad_plate = st.text_input("Plaque à radier", key="rad_plate").upper()
        rad_key = st.text_input("Code de sécurité", type="password", key="rad_key")
        if st.button("RADIER LE VÉHICULE DU REGISTRE", use_container_width=True):
            match = df_i[df_i["Numéro de la plaque"].astype(str).str.upper() == rad_plate]
            if not match.empty:
                if str(rad_key) == str(match.iloc[0]["CODE"]) or st.session_state.user_auth == "Staff":
                    df_i = df_i.drop(match.index[0])
                    cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i)
                    record_log(st.session_state.user_auth, f"Radiation plaque {rad_plate}")
                    st.cache_data.clear(); st.success("Véhicule radié avec succès."); time.sleep(1); st.rerun()
                else: st.error("Code de sécurité incorrect.")
            else: st.error("Plaque introuvable.")

    with col_t:
        st.markdown("### 🖼️ APERÇU DU TITRE (LIVE)")
        d_name = f_owner if f_owner != "---" else ".................."
        d_mod = f_model if f_model else ".................."
        d_plq = f_plate if f_plate else ".................."
        
        st.markdown(f"""
            <div class="receipt-container">
                <div class="receipt-title">TITRE DE CIRCULATION</div>
                <center><small>RÉPUBLIQUE DE RENSSELAER</small></center>
                <hr style="border: 1px dashed #000;">
                <p><b>DATE D'ÉMISSION :</b> {datetime.now().strftime("%d/%m/%Y")}</p>
                <p><b>PROPRIÉTAIRE :</b> {d_name}</p>
                <p><b>MODÈLE :</b> {d_mod}</p>
                <p><b>NUMÉRO PLAQUE :</b> <span style="background:#eee; padding:2px 8px; border:1px solid #000;">{d_plq}</span></p>
                <p><b>CONTRAT ASSU :</b> {f_assu}</p>
                <hr style="border: 1px dashed #000;">
                <div style="text-align:right; font-size:1.2em;"><b>TOTAL : {total_bill}$</b></div>
                <br>
                <center><small>Document certifié conforme par le terminal fédéral</small></center>
            </div>
        """, unsafe_allow_html=True)
        if st.session_state.last_action:
            st.success("✅ TRANSACTION CONFIRMÉE")

# --- ONGLET 2 : SERVICES RCT (AMENDES & POINTS) ---
if st.session_state.user_auth in ["RCT", "Staff"]:
    with tabs[1]:
        st.markdown("### 👮 Interface de Service RCT")
        st.info("Utilisez cette interface pour réguler la circulation et sanctionner les infractions.")
        
        if target == "---":
            st.warning("⚠️ Veuillez sélectionner un citoyen dans le dossier en haut pour agir.")
        else:
            st.write(f"Actions en cours sur : **{target}**")
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("⚖️ Sanctions Permis")
                p_loss = st.number_input("Nombre de points à retirer", min_value=0, max_value=25, step=1)
                if st.button("RETIRER LES POINTS", use_container_width=True):
                    idx_p = df_p[df_p["Nom Roblox"] == target].index[0]
                    df_p.at[idx_p, "PTS"] = max(0, int(df_p.at[idx_p, "PTS"]) - p_loss)
                    cloud_conn.update(worksheet="Points Permis", data=df_p)
                    record_log("RCT", f"Points -{p_loss} sur {target}")
                    st.cache_data.clear(); st.success(f"{p_loss} points retirés."); st.rerun()
            
            with c2:
                st.subheader("💰 Amendes de Service")
                tax_val = st.number_input("Montant de l'amende ($)", min_value=0, step=50)
                if st.button("PERCEVOIR L'AMENDE", use_container_width=True):
                    idx_b = df_b[df_b["Nom Roblox"] == target].index[0]
                    curr_solde = float(str(df_b.at[idx_b, "Solde"]).replace('$', ''))
                    df_b.at[idx_b, "Solde"] = curr_solde - tax_val
                    
                    # Versement à la RCT
                    rct_idx = df_b[df_b["Nom Roblox"] == ACC_RCT].index[0]
                    df_b.at[rct_idx, "Solde"] = float(str(df_b.at[rct_idx, "Solde"]).replace('$', '')) + tax_val
                    
                    cloud_conn.update(worksheet="Banque", data=df_b)
                    record_log("RCT", f"Amende {tax_val}$ sur {target}")
                    st.cache_data.clear(); st.success("Amende perçue et transférée au compte RCT."); st.rerun()

# --- ONGLET 3 : ADMINISTRATION (STAFF ONLY) ---
if st.session_state.user_auth == "Staff":
    with tabs[2]:
        st.markdown("### 🛡️ Contrôle Administrateur")
        
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            st.subheader("🔨 Création de Profil Fédéral")
            with st.form("admin_creation_form"):
                st.write("Procédure d'arrivée : 15,000$ + 25 Points Permis.")
                new_rob = st.text_input("Nom Roblox du Citoyen")
                new_dis = st.text_input("Identifiant Discord")
                new_job = st.selectbox("Secteur", ["Civil", "RCT", "Gouverneur", "Justice", "Armée"])
                
                if st.form_submit_button("VALIDER L'INSCRIPTION NATIONALE"):
                    if new_rob in df_b["Nom Roblox"].values:
                        st.error("Citoyen déjà enregistré.")
                    else:
                        # DATE AUTOMATIQUE
                        date_arr = datetime.now().strftime("%d/%m/%Y")
                        
                        # Banque entry
                        new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": new_dis, "Nom Roblox": new_rob, "Date d'arrivée": date_arr, "Emploiement": new_job}])
                        # Permis entry
                        new_p = pd.DataFrame([{"Nom Discord": new_dis, "Nom Roblox": new_rob, "PTS": 25, "Validité": "OUI"}])
                        
                        cloud_conn.update(worksheet="Banque", data=pd.concat([df_b, new_b]))
                        cloud_conn.update(worksheet="Points Permis", data=pd.concat([df_p, new_p]))
                        record_log("Staff", f"Création profil : {new_rob}")
                        st.cache_data.clear(); st.success(f"Profil de {new_rob} créé avec succès !"); st.rerun()
        
        with col_s2:
            st.subheader("⚙️ Maintenance Système")
            if st.button("🗑️ VIDER LE CACHE DE SESSION"):
                st.cache_data.clear()
                st.rerun()
            
            st.divider()
            st.write("📊 **Statistiques Globales**")
            st.write(f"Masse monétaire : {df_b['Solde'].astype(float).sum():,.0f}$")
            st.write(f"Parc Automobile : {len(df_i)} véhicules")

# ======================================================================================
# 8. PIED DE PAGE
# ======================================================================================
st.divider()
st.caption(f"Terminal Fédéral RCRP FR | Opérationnel | © 2026 République de Rensselaer")
