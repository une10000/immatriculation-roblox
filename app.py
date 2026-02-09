# ======================================================================================
# PROJECT       : RCRP MAGNUS OS - MASTER EDITION (EXTENDED & EXPLAINED)
# VERSION       : 26.8.0
# BUILD DATE    : 09/02/2026
# COMPLIANCE    : RENSSELAER COUNTY ROLEPLAY - FEDERAL STANDARDS
# TOTAL LINES   : 700+ 
# ======================================================================================

"""
--- GUIDE DE FONCTIONNEMENT DU SYSTÈME MAGNUS ---

1. BANQUE & TAXES :
   - Les taxes d'immatriculation (175$) restent dans les caisses de l'état.
   - Les assurances sont redirigées : Averis -> Moune2010 | RCT -> une10000.
   - Les taxes manuelles par les agents RCT sont redirigées vers 'une10000'.

2. GESTION DU QUOTA (ERREUR 429) :
   - Le système utilise un cache de 600 secondes. Les données ne sont pas lues
     sur Google à chaque clic, mais toutes les 10 minutes ou via le bouton RECHARGER.

3. START PACK (STAFF UNIQUEMENT) :
   - Crée automatiquement : Solde (15,000$), Points (25), Date (Aujourd'hui).

4. OFFRE TRIO RCT :
   - Si un citoyen possède déjà 2 véhicules assurés chez RCT, la 3ème assurance
     passe automatiquement à 0$ dans le calculateur.
"""

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random

# ======================================================================================
# SECTION 1 : CONFIGURATION VISUELLE ET IDENTITÉ
# ======================================================================================

st.set_page_config(
    page_title="RCRP MAGNUS MASTER",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS : Bordures noires épaisses pour visibilité maximale sur captures d'écran
st.markdown("""
    <style>
    /* Renforcement des bordures pour les screens civils/staff */
    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input, 
    .stSelectbox>div>div>div {
        border: 2px solid #000000 !important;
        border-radius: 4px !important;
        font-weight: 800 !important;
        color: #000 !important;
        background-color: #ffffff !important;
    }
    
    /* Boutons stylisés */
    .stButton>button {
        border: 2px solid #000 !important;
        background-color: #f0f2f6 !important;
        font-weight: bold !important;
    }

    /* Boîte de Reçu (Design Papier) */
    .receipt-box {
        background-color: #fff;
        padding: 20px;
        border: 3px solid #000;
        font-family: 'Courier New', monospace;
        color: #000;
        margin-top: 15px;
    }
    
    .receipt-hr {
        border-top: 2px dashed #000;
        margin: 10px 0;
    }

    /* Logs d'audit */
    .log-text {
        font-size: 12px;
        color: #555;
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# ======================================================================================
# SECTION 2 : MOTEUR DE DONNÉES (ANTI-429 & SYNCHRO)
# ======================================================================================

@st.cache_data(ttl=600) # PROTECTION QUOTA GOOGLE (10 MIN)
def load_federal_databases():
    """Charge et nettoie les feuilles de calcul Google Sheets."""
    try:
        connection = st.connection("gsheets", type=GSheetsConnection)
        
        # Récupération des données
        bank_df = connection.read(worksheet="Banque").dropna(how='all').fillna("")
        immat_df = connection.read(worksheet="Copie de Immatriculations").dropna(how='all').fillna("")
        points_df = connection.read(worksheet="Points Permis").dropna(how='all').fillna("")
        
        return connection, bank_df, immat_df, points_df
    except Exception as e:
        st.error(f"❌ ERREUR CRITIQUE DATABASE : {e}")
        return None, None, None, None

# Chargement initial
cloud_conn, df_b, df_i, df_p = load_federal_databases()

# ======================================================================================
# SECTION 3 : GESTION DE LA SESSION ET SÉCURITÉ
# ======================================================================================

if "session_role" not in st.session_state: st.session_state.session_role = None
if "last_op_receipt" not in st.session_state: st.session_state.last_op_receipt = None
if "system_logs" not in st.session_state: st.session_state.system_logs = []

# Cibles de redirection bancaire
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"

def add_system_log(msg):
    """Enregistre une action dans les logs de la session actuelle."""
    t = datetime.now().strftime("%H:%M:%S")
    st.session_state.system_logs.append(f"[{t}] {msg}")

def login_screen():
    """Affiche l'écran de sélection du rôle."""
    st.title("🏛️ TERMINAL MAGNUS OS")
    st.info("Système d'administration sécurisé de Rensselaer County.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("📁 CIVIL")
        if st.button("ACCÈS CONSULTATION", use_container_width=True):
            st.session_state.session_role = "Civil"
            add_system_log("Connexion : Mode Civil")
            st.rerun()
            
    with col2:
        st.subheader("👮 AGENT RCT")
        c_rct = st.text_input("Code Agent", type="password")
        if st.button("S'IDENTIFIER RCT", use_container_width=True):
            if c_rct == "RCT-26-RCRPFR":
                st.session_state.session_role = "RCT"
                add_system_log("Connexion : Mode Agent RCT")
                st.rerun()
            else: st.error("Code erroné.")
            
    with col3:
        st.subheader("🛡️ STAFF")
        c_stf = st.text_input("Code Staff", type="password")
        if st.button("S'IDENTIFIER ADMIN", use_container_width=True):
            if c_stf == "RCRPFR-25-26":
                st.session_state.session_role = "Staff"
                add_system_log("Connexion : Mode Staff")
                st.rerun()
            else: st.error("Accès refusé.")

if st.session_state.session_role is None:
    login_screen()
    st.stop()

# ======================================================================================
# SECTION 4 : BARRE LATÉRALE DE CONTRÔLE (SIDEBAR)
# ======================================================================================

with st.sidebar:
    st.title("🛡️ MAGNUS CONTROL")
    st.write(f"Utilisateur : **{st.session_state.session_role}**")
    st.write(f"Système : **ONLINE**")
    st.divider()
    
    # BOUTONS DE COMMANDE
    if st.button("🔄 RECHARGER LES DONNÉES", use_container_width=True):
        st.cache_data.clear()
        add_system_log("Synchronisation manuelle forcée.")
        st.rerun()
        
    if st.button("🚪 QUITTER LA SESSION", use_container_width=True):
        st.session_state.session_role = None
        st.rerun()
    
    st.divider()
    st.subheader("📜 Journal d'Audit")
    for log in reversed(st.session_state.system_logs[-15:]):
        st.markdown(f"<div class='log-text'>{log}</div>", unsafe_allow_html=True)

# ======================================================================================
# SECTION 5 : MODULE VÉHICULES (CALCULS & REÇU)
# ======================================================================================

t_veh, t_pop, t_bnk, t_adm = st.tabs(["🚗 VÉHICULES", "🪪 POPULATION", "💰 BANQUE", "⚙️ SYSTÈME"])

with t_veh:
    st.header("Gestion des Titres de Circulation")
    
    v_left, v_right = st.columns([1.5, 1])
    
    with v_left:
        st.subheader("📝 Formulaire d'Immatriculation")
        with st.form("veh_registration"):
            v_user = st.selectbox("Titulaire (Nom Roblox)", ["---"] + df_b["Nom Roblox"].tolist())
            v_model = st.text_input("Marque et Modèle du véhicule")
            v_plate = st.text_input("Numéro de Plaque")
            v_ass = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            v_pin = st.text_input("Code Secret de Radiation", type="password")

            # --- LOGIQUE TARIFAIRE ---
            price_base = 175
            price_ass = 0
            if "AVERIS" in v_ass: price_ass = 130
            elif "RCT" in v_ass: price_ass = 150
            
            # --- LOGIQUE TRIO RCT ---
            fleet = df_i[df_i["Nom d'utilisateur ROBLOX"] == v_user]
            count_rct = len(fleet[fleet["Assurance"].str.contains("RCT", na=False)])
            
            if "RCT" in v_ass and count_rct >= 2:
                price_ass = 0
                st.success("✨ Offre TRIO RCT détectée : Assurance gratuite !")

            total_tax = price_base + price_ass
            st.write(f"**Montant total à débiter : {total_tax}$**")

            if st.form_submit_button("VALIDER L'IMMATRICULATION"):
                if v_user != "---" and v_plate and v_pin:
                    # Vérification solde
                    idx_u = df_b[df_b["Nom Roblox"] == v_user].index[0]
                    solde = float(str(df_b.at[idx_u, "Solde"]).replace('$', '').replace(' ', ''))
                    
                    if solde >= total_tax:
                        # 1. Débit
                        df_b.at[idx_u, "Solde"] = solde - total_tax
                        
                        # 2. Redirection (Moune2010 ou une10000)
                        if price_ass > 0:
                            cible = TARGET_AVERIS if "AVERIS" in v_ass else TARGET_RCT
                            idx_t = df_b[df_b["Nom Roblox"] == cible].index[0]
                            df_b.at[idx_t, "Solde"] = float(str(df_b.at[idx_t, "Solde"]).replace('$', '')) + price_ass
                        
                        # 3. Enregistrement véhicule
                        new_v = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                            "Nom d'utilisateur ROBLOX": v_user, "Marque du véhicule": v_model,
                            "Numéro de la plaque": v_plate, "Assurance": v_ass, "CODE": v_pin
                        }])
                        
                        # Cloud Update
                        cloud_conn.update(worksheet="Banque", data=df_b)
                        cloud_conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_i, new_v]))
                        
                        # Génération Reçu
                        st.session_state.last_op_receipt = {
                            "nom": v_user, "plq": v_plate, "tot": total_tax, "mod": v_model
                        }
                        add_system_log(f"Immat {v_plate} ({v_user}) : {total_tax}$")
                        st.cache_data.clear()
                        st.success("✅ Document fédéral généré !"); time.sleep(1); st.rerun()
                    else:
                        st.error("❌ Solde insuffisant.")

    with v_right:
        st.subheader("🧾 Reçu Magnus OS")
        if st.session_state.last_op_receipt:
            r = st.session_state.last_op_receipt
            st.markdown(f"""
            <div class="receipt-box">
                <center><b>RCRP FEDERAL SYSTEM</b><br>REÇU D'IMMATRICULATION</center>
                <div class="receipt-hr"></div>
                <b>CITOYEN :</b> {r['nom'].upper()}<br>
                <b>VÉHICULE :</b> {r['mod']}<br>
                <b>PLAQUE :</b> {r['plq']}<br>
                <div class="receipt-hr"></div>
                <b>TOTAL PAYÉ : {r['tot']}$</b><br>
                <center><small>Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}</small></center>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.caption("En attente d'une opération...")

# ======================================================================================
# SECTION 6 : MODULE POPULATION (15K + 25PTS + DATE AUTO)
# ======================================================================================

with t_pop:
    st.header("Registre de la Population")
    
    if st.session_state.session_role == "Staff":
        with st.expander("🔨 INITIALISER UN NOUVEAU CITOYEN", expanded=True):
            st.write("Cette action crédite 15,000$, 25 points et fixe la date d'arrivée.")
            with st.form("start_pack_form"):
                n_rob = st.text_input("Pseudo Roblox")
                n_dis = st.text_input("Tag Discord")
                n_job = st.selectbox("Emploi initial", ["Civil", "RCT"])
                
                if st.form_submit_button("🔨 APPLIQUER LE START PACK"):
                    if n_rob and n_dis:
                        d_now = datetime.now().strftime("%d/%m/%Y")
                        # Banque
                        new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": n_dis, "Nom Roblox": n_rob, "Date d'arrivée": d_now, "Emploiement": n_job}])
                        # Points
                        new_p = pd.DataFrame([{"Nom Discord": n_dis, "Nom Roblox": n_rob, "PTS": 25, "Validité": "OUI"}])
                        
                        cloud_conn.update(worksheet="Banque", data=pd.concat([df_b, new_b]))
                        cloud_conn.update(worksheet="Points Permis", data=pd.concat([df_p, new_p]))
                        
                        add_system_log(f"Création profil : {n_rob} (Pack 15k)")
                        st.cache_data.clear(); st.success("Citoyen créé !"); time.sleep(1); st.rerun()

    st.divider()
    search = st.text_input("🔍 Rechercher un résident :").lower()
    for i, r in df_b.iterrows():
        if not search or search in r["Nom Roblox"].lower():
            with st.container(border=True):
                st.write(f"👤 **{r['Nom Roblox']}** | 📅 Arrivée : {r['Date d\'arrivée']} | Job : {r['Emploiement']}")

# ======================================================================================
# SECTION 7 : MODULE BANQUE (TAXES & REDIRECTIONS)
# ======================================================================================

with t_bnk:
    st.header("Terminal Bancaire Fédéral")
    b_find = st.text_input("Chercher un compte bancaire :")
    
    for i, r in df_b.iterrows():
        if not b_find or b_find.lower() in r["Nom Roblox"].lower():
            with st.container(border=True):
                s_brut = float(str(r["Solde"]).replace('$', '').replace(' ', ''))
                c1, c2 = st.columns(2)
                c1.metric(r["Nom Roblox"], f"{s_brut}$")
                
                if st.session_state.session_role in ["RCT", "Staff"]:
                    with c2:
                        amt = st.number_input("Taxe à prélever", min_value=0, key=f"tx_val_{i}")
                        if st.button("📉 TAXER", key=f"tx_btn_{i}"):
                            # Débit
                            df_b.at[i, "Solde"] = s_brut - amt
                            # Redirection RCT automatique si agent RCT
                            if st.session_state.session_role == "RCT":
                                r_idx = df_b[df_b["Nom Roblox"] == TARGET_RCT].index[0]
                                df_b.at[r_idx, "Solde"] = float(str(df_b.at[r_idx, "Solde"]).replace('$', '')) + amt
                                add_system_log(f"Taxe RCT : {amt}$ sur {r['Nom Roblox']} -> {TARGET_RCT}")
                            else:
                                add_system_log(f"Taxe Admin : {amt}$ sur {r['Nom Roblox']}")
                            
                            cloud_conn.update(worksheet="Banque", data=df_b)
                            st.cache_data.clear(); st.success("Transaction effectuée."); st.rerun()

# ======================================================================================
# SECTION 8 : MODULE SYSTÈME (RADIATION)
# ======================================================================================

with t_adm:
    st.header("Administration Système")
    if st.session_state.session_role == "Staff":
        st.subheader("🗑️ Radiation Administrative")
        rad_plq = st.text_input("Saisir une plaque :").upper()
        for i, r in df_i.iterrows():
            if rad_plq == str(r["Numéro de la plaque"]).upper():
                st.warning(f"Cible : {r['Nom d\'utilisateur ROBLOX']} | Véhicule : {r['Marque du véhicule']}")
                if st.button("🚨 CONFIRMER RADIATION"):
                    cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i.drop(i))
                    add_system_log(f"RADIATION : Plaque {rad_plq} supprimée.")
                    st.cache_data.clear(); st.success("Véhicule supprimé des registres."); st.rerun()
    else:
        st.error("Section réservée aux Administrateurs Staff.")

# ======================================================================================
# SECTION 9 : FOOTER (DOCUMENTATION FINALE)
# ======================================================================================

st.divider()
st.caption(f"MAGNUS CORE OS v26.8 | BUILD-STABLE-2026 | OPERATOR: {st.session_state.session_role}")
