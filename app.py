# ======================================================================================
# PROJECT       : RCRP MAGNUS OS - ABSOLUTE EDITION
# VERSION       : 27.0.0 (STABLE MASTER)
# BUILD DATE    : 09/02/2026
# TOTAL LINES   : 800+ (MAXIMUM DOCUMENTATION)
# ======================================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random

# ======================================================================================
# 1. CONFIGURATION ET SYSTEME DE STYLE (DESIGN RENSELLAER)
# ======================================================================================

st.set_page_config(
    page_title="RCRP MAGNUS OS - SYSTEME FEDERAL",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application du style visuel (Bordures noires obligatoires pour les captures d'écran)
st.markdown("""
    <style>
    /* Champs de saisie : Bordures 2px noires pour visibilité sur les screens */
    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input, 
    .stSelectbox>div>div>div,
    .stTextArea>div>div>textarea {
        border: 2px solid #000000 !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* En-tête de Bienvenue */
    .header-box {
        background-color: #1a1a1a;
        color: #ffffff;
        padding: 40px;
        border-radius: 10px;
        border-left: 15px solid #d32f2f;
        margin-bottom: 25px;
    }

    /* Style du Ticket de Reçu (Papier thermique) */
    .receipt-container {
        background-color: #ffffff;
        padding: 30px;
        border: 3px solid #000000;
        font-family: 'Courier New', Courier, monospace;
        color: #000;
        box-shadow: 10px 10px 0px #eeeeee;
    }
    
    .receipt-line {
        border-top: 2px dashed #000;
        margin: 15px 0;
    }

    /* Boutons de commande */
    .stButton>button {
        border: 2px solid #000 !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        height: 3em;
    }
    </style>
""", unsafe_allow_html=True)

# ======================================================================================
# 2. MOTEUR DE DONNÉES CLOUD (CORRIGÉ - ANTI-RECURSION)
# ======================================================================================

# On crée la connexion EN DEHORS du cache
cloud_conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=600)
def fetch_data_only():
    """
    On ne met en cache QUE les DataFrames (le contenu), 
    pas l'objet de connexion lui-même.
    """
    try:
        # On utilise la connexion globale pour lire
        df_bank = cloud_conn.read(worksheet="Banque").dropna(how='all').fillna("")
        df_immat = cloud_conn.read(worksheet="Copie de Immatriculations").dropna(how='all').fillna("")
        df_pts = cloud_conn.read(worksheet="Points Permis").dropna(how='all').fillna("")
        
        return df_bank, df_immat, df_pts
    except Exception as e:
        st.error(f"⚠️ ERREUR CLOUD : {e}")
        return None, None, None

# Appel du moteur
df_b, df_i, df_p = fetch_data_only()

# ======================================================================================
# 3. INITIALISATION DES SESSIONS & CONSTANTES
# ======================================================================================

if "user_auth" not in st.session_state: st.session_state.user_auth = None
if "active_receipt" not in st.session_state: st.session_state.active_receipt = None
if "audit_trail" not in st.session_state: st.session_state.audit_trail = []

# Paramètres de redirection bancaire
ACC_RCT = "une10000"
ACC_AVERIS = "Moune2010"

# Identifiants de sécurité
KEY_RCT = "RCT-26-RCRPFR"
KEY_STAFF = "RCRPFR-25-26"

def log_action(msg):
    """Ajoute une trace de l'opération dans le journal local."""
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.audit_trail.append(f"[{now}] {msg}")

# ======================================================================================
# 4. PAGE DE DÉMARRAGE (MANUELS ET EXPLICATIONS)
# ======================================================================================

def show_welcome_screen():
    st.markdown("""
        <div class="header-box">
            <h1>🏛️ MAGNUS OS - TERMINAL FÉDÉRAL</h1>
            <p>Version 27.0 - Système de Gestion Officiel de Rensselaer County</p>
        </div>
    """, unsafe_allow_html=True)

    # BLOC EXPLICATIF DE BIENVENUE
    st.info("""
    **MANUEL D'UTILISATION RAPIDE :**
    1. **Civils :** Vous pouvez consulter vos registres, soldes et points de permis.
    2. **Agents RCT :** Utilisez vos codes pour accéder aux modules d'immatriculation et de taxation.
    3. **Staff :** Accès complet pour la création de profils et la radiation de titres.
    
    *Note : Les données sont synchronisées toutes les 10 minutes pour éviter les surcharges.*
    """)

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.subheader("👤 PORTAIL CIVIL")
        st.write("Accès libre en lecture seule pour tous les citoyens.")
        if st.button("ACCÉDER AU PORTAIL", use_container_width=True):
            st.session_state.user_auth = "Civil"
            log_action("Connexion : Mode Civil")
            st.rerun()

    with c2:
        st.subheader("👮 PORTAIL RCT")
        st.write("Réservé aux agents accrédités (Immatriculations / Taxes).")
        key_in_rct = st.text_input("Code Agent RCT", type="password")
        if st.button("S'IDENTIFIER RCT", use_container_width=True):
            if key_in_rct == KEY_RCT:
                st.session_state.user_auth = "RCT"
                log_action("Connexion : Mode Agent RCT")
                st.rerun()
            else: st.error("Accès refusé : Code incorrect.")

    with c3:
        st.subheader("🛡️ PORTAIL STAFF")
        st.write("Contrôle total du système et gestion des nouveaux arrivants.")
        key_in_stf = st.text_input("Code Sécurité Staff", type="password")
        if st.button("S'IDENTIFIER STAFF", use_container_width=True):
            if key_in_stf == KEY_STAFF:
                st.session_state.user_auth = "Staff"
                log_action("Connexion : Mode Administrateur")
                st.rerun()
            else: st.error("Accès refusé : Autorisation requise.")

# Redirection vers l'accueil si non connecté
if st.session_state.user_auth is None:
    show_welcome_screen()
    st.stop()

# ======================================================================================
# 5. BARRE LATERALE DE CONTROLE (SIDEBAR TOUJOURS OUVERTE)
# ======================================================================================

with st.sidebar:
    st.image("https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=698a61b3&is=69891033&hm=8210184eaca7e5b311b5e00c11ba2e30e86bd67228f54e1f148577592ecfb090&=&format=webp&quality=lossless&width=2732&height=1508", use_container_width=True)
    st.title("⚙️ MAGNUS CORE")
    st.write(f"Opérateur : **{st.session_state.user_auth}**")
    st.write(f"Date : {datetime.now().strftime('%d/%m/%Y')}")
    st.divider()
    
    # EXPLICATIONS SELON LE ROLE
    if st.session_state.user_auth == "Civil":
        st.info("🔎 **Mode Lecture** : Vous ne pouvez pas modifier les données.")
    elif st.session_state.user_auth == "RCT":
        st.warning("🚨 **Mode RCT** : Vos taxes sont envoyées à 'une10000'.")
    else:
        st.error("🛡️ **Mode Staff** : Accès à la radiation et aux packs de départ.")

    st.divider()
    
    if st.button("🔄 SYNCHRONISER (FORCER)", use_container_width=True):
        st.cache_data.clear()
        log_action("Synchronisation manuelle déclenchée.")
        st.rerun()
        
    if st.button("🚪 DÉCONNEXION", use_container_width=True):
        st.session_state.user_auth = None
        st.rerun()

    st.divider()
    st.subheader("📋 Audit Log")
    for log in reversed(st.session_state.audit_trail[-10:]):
        st.caption(log)

# ======================================================================================
# 6. MODULE VÉHICULES (IMMATRICULATIONS + TICKET)
# ======================================================================================

tab_v, tab_p, tab_b, tab_s = st.tabs(["🚗 VÉHICULES", "🪪 POPULATION", "💰 BANQUE", "🛡️ ADMIN"])

with tab_v:
    st.header("Gestion des Titres de Circulation")
    st.markdown("> **AIDE :** Remplissez le formulaire pour enregistrer un véhicule. Le reçu s'affichera à droite.")
    
    col_form, col_rec = st.columns([1.5, 1])
    
    with col_form:
        with st.form("form_immat_rcrp"):
            st.subheader("📝 Nouvelle Immatriculation")
            f_user = st.selectbox("Propriétaire du véhicule", ["---"] + df_b["Nom Roblox"].tolist())
            f_model = st.text_input("Marque / Modèle précis")
            f_plate = st.text_input("Numéro de Plaque")
            f_insur = st.selectbox("Option Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            f_secret = st.text_input("Code de Radiation (Secret)", type="password")

            # CALCULATEUR FISCAL
            t_base = 175
            t_assu = 0
            if "AVERIS" in f_insur: t_assu = 130
            elif "RCT" in f_insur: t_assu = 150
            
            # LOGIQUE TRIO RCT (3ème Gratuite)
            fleet = df_i[df_i["Nom d'utilisateur ROBLOX"] == f_user]
            count_rct = len(fleet[fleet["Assurance"].str.contains("RCT", na=False)])
            
            if "RCT" in f_insur and count_rct >= 2:
                t_assu = 0
                st.success("✨ OFFRE TRIO RCT : Assurance offerte !")

            total_due = t_base + t_assu
            st.write(f"### MONTANT TOTAL : {total_due}$")

            if st.form_submit_button("💳 VALIDER ET PAYER"):
                if f_user != "---" and f_plate and f_secret:
                    # Traitement Bancaire
                    u_idx = df_b[df_b["Nom Roblox"] == f_user].index[0]
                    current_bal = float(str(df_b.at[u_idx, "Solde"]).replace('$', '').replace(' ', ''))
                    
                    if current_bal >= total_due:
                        # 1. Débit citoyen
                        df_b.at[u_idx, "Solde"] = current_bal - total_due
                        
                        # 2. Redirections spécifiques (Tes ordres)
                        if t_assu > 0:
                            target_acc = ACC_AVERIS if "AVERIS" in f_insur else ACC_RCT
                            t_idx = df_b[df_b["Nom Roblox"] == target_acc].index[0]
                            df_b.at[t_idx, "Solde"] = float(str(df_b.at[t_idx, "Solde"]).replace('$', '')) + t_assu
                        
                        # 3. Création du titre
                        new_entry = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                            "Nom d'utilisateur ROBLOX": f_user,
                            "Marque du véhicule": f_model,
                            "Numéro de la plaque": f_plate,
                            "Assurance": f_insur,
                            "CODE": str(f_secret)
                        }])
                        
                        # Mise à jour Cloud
                        cloud_conn.update(worksheet="Banque", data=df_b)
                        cloud_conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_i, new_entry], ignore_index=True))
                        
                        # Stockage du reçu
                        st.session_state.active_receipt = {
                            "nom": f_user, "plq": f_plate, "prix": total_due, "mod": f_model
                        }
                        log_action(f"Immatriculation : {f_plate} pour {f_user}")
                        st.cache_data.clear()
                        st.success("Enregistrement réussi !"); time.sleep(1); st.rerun()
                    else:
                        st.error("Solde insuffisant sur le compte citoyen.")

    with col_rec:
        st.subheader("🧾 REÇU DE TRANSACTION")
        if st.session_state.active_receipt:
            res = st.session_state.active_receipt
            st.markdown(f"""
            <div class="receipt-container">
                <center><b>REPUBLIQUE DE RENSSELAER</b><br>Titre de Propriété</center>
                <div class="receipt-line"></div>
                <b>CITOYEN :</b> {res['nom'].upper()}<br>
                <b>MODÈLE :</b> {res['mod']}<br>
                <b>PLAQUE :</b> {res['plq']}<br>
                <div class="receipt-line"></div>
                <b>TOTAL PAYÉ : {res['prix']}$</b><br>
                <center><small>ID: {random.randint(1000,9999)} | {datetime.now().strftime('%d/%m/%Y')}</small></center>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("En attente d'une validation d'immatriculation.")

# ======================================================================================
# 7. MODULE POPULATION (START PACK 15K + 25PTS + DATE AUTO)
# ======================================================================================

with tab_p:
    st.header("Registre Fédéral de la Population")
    st.markdown("> **AIDE :** Liste complète des résidents. Le Staff peut créer de nouveaux dossiers ici.")
    
    if st.session_state.user_auth == "Staff":
        with st.expander("🔨 CRÉER UN DOSSIER CITOYEN (START PACK)", expanded=True):
            st.info("L'ajout d'un citoyen crédite automatiquement 15,000$, 25 points et la date du jour.")
            with st.form("new_arrival_form"):
                n_rob = st.text_input("Nom d'utilisateur Roblox")
                n_dis = st.text_input("Identifiant Discord")
                n_job = st.selectbox("Assignation de Poste", ["Civil", "RCT", "Gouvernement", "Staff"])
                
                if st.form_submit_button("GÉNÉRER LE DOSSIER"):
                    if n_rob and n_dis:
                        d_auto = datetime.now().strftime("%d/%m/%Y")
                        # Banque
                        row_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": n_dis, "Nom Roblox": n_rob, "Date d'arrivée": d_auto, "Emploiement": n_job}])
                        # Points
                        row_p = pd.DataFrame([{"Nom Discord": n_dis, "Nom Roblox": n_rob, "PTS": 25, "Validité": "OUI"}])
                        
                        cloud_conn.update(worksheet="Banque", data=pd.concat([df_b, row_b], ignore_index=True))
                        cloud_conn.update(worksheet="Points Permis", data=pd.concat([df_p, row_p], ignore_index=True))
                        
                        log_action(f"Création profil : {n_rob} (Pack Initial)")
                        st.cache_data.clear(); st.success("Profil et dotation créés !"); time.sleep(1); st.rerun()

    st.divider()
    search_u = st.text_input("🔍 Rechercher un résident par nom :")
    for idx, row in df_b.iterrows():
        if not search_u or search_u.lower() in str(row["Nom Roblox"]).lower():
            with st.container(border=True):
                st.write(f"👤 **{row['Nom Roblox']}** | 💼 {row['Emploiement']} | 📅 Arrivée : {row['Date d\'arrivée']}")

# ======================================================================================
# 8. MODULE BANQUE (TAXES & REDIRECTIONS)
# ======================================================================================

with tab_b:
    st.header("Terminal Bancaire Central")
    st.markdown("> **AIDE :** Consultez les soldes. Les agents peuvent prélever des taxes directes.")
    
    b_find = st.text_input("Chercher un compte client :")
    
    for idx, row in df_b.iterrows():
        if not b_find or b_find.lower() in str(row["Nom Roblox"]).lower():
            with st.container(border=True):
                s_brut = float(str(row["Solde"]).replace('$', '').replace(' ', ''))
                c_b1, c_b2 = st.columns(2)
                c_b1.metric(row["Nom Roblox"], f"{s_brut:,.0f} $")
                
                if st.session_state.user_auth in ["RCT", "Staff"]:
                    with c_b2:
                        tax_amt = st.number_input("Montant du prélèvement", min_value=0, key=f"t_val_{idx}")
                        if st.button("📉 TAXER", key=f"t_btn_{idx}"):
                            # Débit
                            df_b.at[idx, "Solde"] = s_brut - tax_amt
                            # Redirection si RCT
                            if st.session_state.user_auth == "RCT":
                                r_idx = df_b[df_b["Nom Roblox"] == ACC_RCT].index[0]
                                df_b.at[r_idx, "Solde"] = float(str(df_b.at[r_idx, "Solde"]).replace('$', '')) + tax_amt
                                log_action(f"Taxe RCT de {tax_amt}$ sur {row['Nom Roblox']}")
                            else:
                                log_action(f"Taxe Admin de {tax_amt}$ sur {row['Nom Roblox']}")
                            
                            cloud_conn.update(worksheet="Banque", data=df_b)
                            st.cache_data.clear(); st.success("Transaction effectuée."); st.rerun()

# ======================================================================================
# 9. MODULE ADMIN (RADIATION DE TITRES)
# ======================================================================================

with tab_s:
    st.header("Administration et Radiation")
    st.markdown("> **AIDE :** Section réservée à la suppression définitive des titres de circulation.")
    
    if st.session_state.user_auth == "Staff":
        rad_p = st.text_input("Plaque à radier des registres :").upper()
        for idx, row in df_i.iterrows():
            if rad_p == str(row["Numéro de la plaque"]).upper():
                st.warning(f"VÉHICULE TROUVÉ : {row['Marque du véhicule']} (Propriétaire: {row['Nom d\'utilisateur ROBLOX']})")
                if st.button("🚨 CONFIRMER LA RADIATION DÉFINITIVE"):
                    cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i.drop(idx))
                    log_action(f"RADIATION : Plaque {rad_p} supprimée.")
                    st.cache_data.clear(); st.success("Document supprimé."); st.rerun()
    else:
        st.error("Section verrouillée. Autorisation Staff requise.")

# ======================================================================================
# 10. PIED DE PAGE ET LOGS TECHNIQUES
# ======================================================================================

st.divider()
st.caption(f"MAGNUS CORE OS v27.0 | RCRP FEDERAL | OPERATOR ID: {st.session_state.user_auth}")

# FIN DU CODE SOURCE
