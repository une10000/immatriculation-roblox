# ======================================================================================
# PROJECT       : RCRP FR OS - ULTIMATE TOTAL EDITION
# VERSION       : 14.5.1
# BUILD DATE    : 09/02/2026
# ======================================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random

# 1. INTERFACE & DESIGN
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
        st.image("https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=698b0a73&is=6989b8f3&hm=76c2f537e9acfb1dd2c2dd1d930fa8e2cb88cce4e00e6109f20925d68d289d75&=&format=webp&quality=lossless&width=2732&height=1508", use_container_width=True)
        
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
    st.warning("⚠️ **AVERTISSEMENT :** Toute action effectuée sur ce terminal est enregistrée.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 👥 CIVIL")
        if st.button("ACCÉDER AU TERMINAL"):
            st.session_state.user_auth = "Civil"
            st.rerun()
            
    with c2:
        st.markdown("### 👨‍🔧 AGENT RCT")
        login_rct = st.text_input("Identifiant Agent", type="password")
        if st.button("AUTHENTIFICATION RCT"):
            if login_rct == KEY_RCT:
                st.session_state.user_auth = "RCT"
                st.rerun()
            else: st.error("Clé invalide.")
                
    with c3:
        st.markdown("### 🛡️ STAFF/POLICE")
        login_staff = st.text_input("Clé Maîtresse", type="password")
        if st.button("ACCÈS ADMINISTRATEUR"):
            if login_staff == KEY_STAFF:
                st.session_state.user_auth = "Staff"
                st.rerun()
            else: 
                st.error("Accès refusé.")
    
if st.session_state.user_auth is None:
    st.stop()

# --- LE RESTE DU CODE (SECTION 6, 7, 8) COMMENCE ICI ---
        
# ======================================================================================
# 6. MODULE : DOSSIER CITOYEN UNIFIÉ (VISIBILITÉ TOTALE)
# ======================================================================================

st.markdown('<div class="header-box"><h2>📂 REGISTRE NATIONAL DES CITOYENS</h2></div>', unsafe_allow_html=True)

with st.container():
    st.markdown("""
    <div class="info-card">
        <b>GUIDE DE RECHERCHE :</b> Sélectionnez un nom dans la liste déroulante pour extraire instantanément le dossier financier...
    </div>
    """, unsafe_allow_html=True)
    
    search_list = ["---"] + sorted(df_b["Nom Roblox"].unique().tolist())
    target = st.selectbox("Sélectionner un citoyen :", search_list)
    
    if target != "---":
        col1, col2, col3 = st.columns(3)
        
        # Section Points & Permis avec Bandeau de Sécurité
        with col1:
            p_data = df_p[df_p["Nom Roblox"] == target]
            if not p_data.empty:
                pts_val = int(p_data.iloc[0]["PTS"])
                
                # Organisation interne identique à la banque
                c_pts, c_vide, c_motif_p = st.columns([3, 0.5, 2])
                
                with c_pts:
                    st.metric("POINTS PERMIS", f"{pts_val}/25")
                    status_color = "green" if pts_val > 0 else "red"
                    st.markdown(f"Statut : <b style='color:{status_color};'>{'VALIDE' if pts_val > 0 else 'SUSPENDU'}</b>", unsafe_allow_html=True)
                
                with c_motif_p:
                    # MOTIFS ROUTIERS (Poussés à droite)
                    st.markdown("""
                        <div style="text-align: right; line-height: 1; padding-top: 5px;">
                            <div style="opacity: 0.15; font-size: 40px; margin-bottom: -10px;">🛡️</div>
                            <div style="opacity: 0.1; font-size: 50px; margin-bottom: -10px;">🚗</div>
                            <div style="height: 4px; width: 60px; background: linear-gradient(90deg, transparent, #d32f2f); display: inline-block; opacity: 0.2; border-radius: 2px;"></div>
                            <p style="font-size: 8px; opacity: 0.3; font-family: monospace; margin: 0;">DRIVER LICENSE<br>SECURITY CHECK<br>BY RCRP</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Aucun permis trouvé.")

        # Section Banque avec Bandeau de Sécurité
        with col2:
            b_data = df_b[df_b["Nom Roblox"] == target]
            if not b_data.empty:
                # Utilisation d'un container pour regrouper le tout
                with st.container(border=False):
                    # On crée 3 colonnes internes pour gérer l'alignement précis
                    c_info, c_vide, c_motif = st.columns([3, 1, 2])
                    
                    with c_info:
                        st.metric("SOLDE BANCAIRE", f"{b_data.iloc[0]['Solde']}$")
                        st.write(f"🏢 Métier : **{b_data.iloc[0]['Emploiement']}**")
                        st.caption(f"📅 Arrivée : {b_data.iloc[0]['Date d\'arrivée']}")
                    
                    with c_motif:
                        # SUPERPOSITION DE MOTIFS (Plus à droite et plus complet)
                        st.markdown("""
                            <div style="text-align: right; line-height: 1; padding-top: 5px;">
                                <div style="opacity: 0.15; font-size: 40px; margin-bottom: -10px;">🏛️</div>
                                <div style="opacity: 0.1; font-size: 50px; margin-bottom: -10px;">💳</div>
                                <div style="height: 4px; width: 60px; background: linear-gradient(90deg, transparent, #000); display: inline-block; opacity: 0.2; border-radius: 2px;"></div>
                                <p style="font-size: 8px; opacity: 0.3; font-family: monospace; margin: 0;">OFFICIAL BANK DATA<br>VERIFIED BY RCRP</p>
                            </div>
                        """, unsafe_allow_html=True)
            else: 
                st.error("Aucun compte trouvé.") 
# ======================================================================================
# NOUVEAU : SYSTÈME DE PAIEMENT DES FACTURES (STYLE TICKET)
# ======================================================================================
try:
    df_all_f = cloud_conn.read(worksheet="Factures").fillna("")
    mes_factures = df_all_f[(df_all_f["Cible"] == target) & (df_all_f["Statut"] == "EN ATTENTE")]

    if not mes_factures.empty:
        st.error(f"⚠️ {len(mes_factures)} FACTURE(S) EN ATTENTE DE PAIEMENT")
        for _, fac in mes_factures.iterrows():
            # --- LE TICKET FACTURE STYLE NOSTALGIQUE ---
            prefix_name = "POLICE NATIONALE" if fac['Emetteur'] == "Staff" else "RÉSEAU RCT"
            st.markdown(f"""
            <div style="border: 2px solid #000; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; margin-bottom: 5px; box-shadow: 6px 6px 0px #000;">
                <center><b style="font-size:1.1em; text-decoration: underline;">FACTURE OFFICIELLE</b><br>
                <small>{prefix_name}</small></center>
                <hr style="border-top: 1px dashed #000; margin: 10px 0;">
                <div style="font-size: 0.9em; line-height: 1.2;">
                    <b>RÉFÉRENCE :</b> #{fac['ID']}<br>
                    <b>AGENT     :</b> {fac['Emetteur']}<br>
                    <b>MOTIF     :</b> {fac['Motif']}<br>
                </div>
                <hr style="border-top: 1px dashed #000; margin: 10px 0;">
                <div style="text-align: center; color: #d32f2f; font-weight: bold; font-size: 1.3em;">
                    MONTANT : {fac['Montant']}$
                </div>
                <center><small style="font-size: 0.6em; opacity: 0.5; margin-top:10px; display:block;">RCRP SYSTEM - DOCUMENT OFFICIEL</small></center>
            </div>
            <div style="margin-bottom: 15px;"></div>
            """, unsafe_allow_html=True)

            # Bouton de paiement
            if st.button(f"💳 RÉGLER LA FACTURE #{fac['ID']}", key=f"pay_{fac['ID']}", use_container_width=True):
                idx_b = df_b[df_b["Nom Roblox"] == target].index[0]
                solde_raw = str(df_b.at[idx_b, "Solde"]).replace('$', '').replace(',', '')
                solde_actuel = float(solde_raw)
                montant_facture = float(fac['Montant'])
                
                if solde_actuel >= montant_facture:
                    # 1. Débit
                    df_b.at[idx_b, "Solde"] = solde_actuel - montant_facture
                    
                    # 2. Crédit (Vers RCT)
                    rct_idx = df_b[df_b["Nom Roblox"] == ACC_RCT].index[0]
                    solde_dest = float(str(df_b.at[rct_idx, "Solde"]).replace('$', '').replace(',', ''))
                    df_b.at[rct_idx, "Solde"] = solde_dest + montant_facture
                    
                    # 3. Statut
                    df_all_f.loc[df_all_f["ID"] == fac["ID"], "Statut"] = "PAYÉ"
                    
                    # 4. Sync
                    cloud_conn.update(worksheet="Banque", data=df_b)
                    cloud_conn.update(worksheet="Factures", data=df_all_f)
                    
                    record_log(target, f"Paiement facture {fac['Emetteur']} #{fac['ID']}")
                    st.success("✅ Paiement effectué !")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Fonds insuffisants.")
except Exception as e:
    st.error(f"Erreur technique : {e}")

# --- SECTION VÉHICULES CORRIGÉE ---
# --- SECTION VÉHICULES UNIFORMISÉE ---
st.write("### 🚗 VÉHICULES ENREGISTRÉS")
v_data = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]

if not v_data.empty:
    v_cols = st.columns(3)
    for i, (_, veh) in enumerate(v_data.iterrows()):
        with v_cols[i % 3]:
            # Logique de sécurité
            assu = str(veh['Assurance']).upper()
            is_rct = "RCT" in assu
            is_staff_ok = any(x in assu for x in ["RCT", "AVERIS"])
            
            color = "#000000" # Noir par défaut
            status_txt = "CERTIFIÉ CONFORME"
            
            if st.session_state.user_auth == "RCT" and not is_rct:
                color = "#d32f2f"
                status_txt = "⚠️ DANGER : NON-ASSURÉ RCT"
            elif st.session_state.user_auth == "Staff" and not is_staff_ok:
                color = "#d32f2f"
                status_txt = "⚠️ NON-ASSURÉ"

            # Design style "Reçu" (Capture 16:14:00)
            st.markdown(f"""
            <div style="border: 2px solid black; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; line-height: 1.2;">
                <center><b>TITRE DE CIRCULATION</b><br><small>RÉPUBLIQUE DE RENSSERLAER</small></center>
                <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                <b>DATE :</b> {datetime.now().strftime('%d/%m/%Y')}<br>
                <b>NOM :</b> {target}<br>
                <b>MODÈLE :</b> {veh['Marque du véhicule']}<br>
                <b>PLAQUE :</b> <span style="border: 1px solid black; padding: 0 3px;">{veh['Numéro de la plaque']}</span><br>
                <b>ASSURANCE :</b> {veh['Assurance']}
                <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                <div style="text-align: center; color: {color}; font-weight: bold; font-size: 0.8em;">
                    {status_txt}<br>
                    <small>Par le Terminal National</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
                        
                        # Utilisation d'une clé unique basée sur la plaque ET l'index pour éviter le "Duplicate Key"
            with st.expander("🗑️ Radier"):
                            r_cod_check = st.text_input("Code Secret", type="password", key=f"rad_input_{veh['Numéro de la plaque']}_{i}")
                            if st.button("CONFIRMER", key=f"btn_confirm_{veh['Numéro de la plaque']}_{i}", use_container_width=True):
                                if str(r_cod_check) == str(veh['CODE']) or st.session_state.user_auth == "Staff":
                                    # Logique de suppression
                                    df_all_immat = cloud_conn.read(worksheet="Copie de Immatriculations")
                                    df_updated = df_all_immat[df_all_immat["Numéro de la plaque"] != veh['Numéro de la plaque']]
                                    cloud_conn.update(worksheet="Copie de Immatriculations", data=df_updated)
                                    st.cache_data.clear()
                                    st.success("Radié !")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Code incorrect")
            
# ======================================================================================
# 7. LOGIQUE DES ONGLETS (CORRIGÉE)
# ======================================================================================
tab_labels = ["🚗 IMMATRICULATION"]
if st.session_state.user_auth in ["RCT", "Staff"]: tab_labels.append("👮 SERVICES AGENT")
if st.session_state.user_auth == "Staff": tab_labels.append("🛠️ ADMINISTRATION")

tabs = st.tabs(tab_labels)

# --- ONGLET 1 : IMMATRICULATION & RADIATION ---
with tabs[0]:
    st.markdown("### 📝 Gestion des Titres de Circulation")
    
    col_f, col_t = st.columns([1.3, 1])
    
    with col_f:
        with st.container(border=True):
            f_owner = st.selectbox("Propriétaire du véhicule", ["---"] + df_b["Nom Roblox"].tolist(), key="k_owner_v7")
            f_model = st.text_input("Marque & Modèle précis", key="k_model_v7")
            f_plate = st.text_input("Numéro de Plaque souhaité", key="k_plate_v7").upper()
            f_assu = st.selectbox("Type d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"], key="k_assu_v7")
            f_code = st.text_input("Définir un Code de Radiation (Secret)", type="password", key="k_code_v7")
            
            # --- CALCULS TAXE JEUNE (Fixe à 0 ou 50) ---
            val_taxe_jeune = 0
            est_jeune = False
            
            if f_owner != "---":
                try:
                    date_brute = df_b[df_b["Nom Roblox"] == f_owner]["Date d'arrivée"].values[0]
                    date_arr = datetime.strptime(str(date_brute), "%d/%m/%Y")
                    if (datetime.now() - date_arr).days < 30:
                        est_jeune = True
                        val_taxe_jeune = 50
                        st.warning(f"🔰 JEUNE CONDUCTEUR détecté (+{val_taxe_jeune}$)")
                except: pass

            taxe_gouv = 175
            taxe_assu = 130 if "AVERIS" in f_assu else (150 if "RCT" in f_assu else 0)
            
            # Offre Trio RCT
            if "RCT" in f_assu and f_owner != "---":
                if len(df_i[df_i["Nom d'utilisateur ROBLOX"] == f_owner]) >= 2:
                    taxe_assu = 0
                    st.success("🎁 OFFRE TRIO : Assurance offerte sur le 3ème véhicule !")

            total_bill = taxe_gouv + taxe_assu + val_taxe_jeune
            
            if st.button(f"S'ACQUITTER DE {total_bill}$ ET ENREGISTRER", use_container_width=True, key="btn_pay_final"):
                if f_owner != "---" and f_plate and f_code:
                    u_idx = df_b[df_b["Nom Roblox"] == f_owner].index[0]
                    u_solde = float(str(df_b.at[u_idx, "Solde"]).replace('$', ''))
                    
                    if u_solde >= total_bill:
                        # --- TRAITEMENT DU PAIEMENT ---
                        df_b.at[u_idx, "Solde"] = u_solde - total_bill
                        
                        # Redirection des fonds (Averis vers Moune2010, RCT vers compte RCT)
                        if taxe_assu > 0:
                            target_acc = "Moune2010" if "AVERIS" in f_assu else ACC_RCT
                            a_idx = df_b[df_b["Nom Roblox"] == target_acc].index[0]
                            df_b.at[a_idx, "Solde"] = float(str(df_b.at[a_idx, "Solde"]).replace('$', '')) + taxe_assu
                        
                        # --- ENREGISTREMENT ---
                        new_row = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y"), "Nom d'utilisateur ROBLOX": f_owner, "Marque du véhicule": f_model, "Numéro de la plaque": f_plate, "Assurance": f_assu, "CODE": f_code}])
                        cloud_conn.update(worksheet="Banque", data=df_b)
                        cloud_conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_i, new_row]))
                        
                        # --- MESSAGE DE CONFIRMATION (NOUVEAU) ---
                        st.balloons() # Optionnel : petites confettis pour le côté "cool"
                        st.success(f"✅ Paiement de {total_bill}$ validé ! Votre plaque {f_plate} est désormais enregistrée.")
                        
                        st.cache_data.clear()
                        time.sleep(2) # On attend 2 secondes pour que l'utilisateur voit le message
                        st.rerun()
                    else: 
                        st.error("❌ Solde insuffisant sur votre compte bancaire.")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs (Propriétaire, Plaque et Code).")

    with col_t:
        st.markdown("### 🖼️ APERÇU DU TITRE (LIVE)")
        
        # Le ticket avec la colonne Taxe Jeune FIXE
        ticket_html = f"""
        <div style="border: 4px double black; padding: 15px; background: white; color: black; font-family: monospace;">
            <div style="text-align:center; font-weight:900; font-size:1.2em;">TITRE DE CIRCULATION</div>
            <center><small>RÉPUBLIQUE DE RENSSELAER</small></center>
            <hr>
            <div style="font-size: 0.9em;">
                <p style="margin:2px 0;"><b>DATE :</b> {datetime.now().strftime("%d/%m/%Y")}</p>
                <p style="margin:2px 0;"><b>NOM :</b> {f_owner}</p>
                <p style="margin:2px 0;"><b>MODÈLE :</b> {f_model if f_model else "..."}</p>
                <p style="margin:2px 0;"><b>PLAQUE :</b> <span style="background:#eee; border:1px solid #000; padding:0 3px;">{f_plate if f_plate else "..."}</span></p>
                <p style="margin:2px 0;"><b>ASSURANCE :</b> {f_assu}</p>
                <p style="margin:2px 0;"><b>TAXE JEUNE :</b> {val_taxe_jeune}$</p>
            </div>
            <hr>
            <div style="text-align:right; font-weight:bold; font-size:1.2em;">TOTAL : {total_bill}$</div>
            <br>
            <center><small>Certifié conforme par le Terminal National</small></center>
        </div>
        """
        st.markdown(ticket_html, unsafe_allow_html=True)
# --- ONGLET 2 : SERVICES AGENT (FACTURES / POINTS / CONSULTATION) ---
with tabs[1]:
    st.markdown('<div class="header-box"><h2>👮 SERVICES AGENT RCT</h2></div>', unsafe_allow_html=True)

    # --- 1. RECHERCHE PAR RÉFÉRENCE ---
    st.markdown("### 🔍 Vérification de Facture")
    search_ref = st.text_input("Entrer le numéro de référence (ID)", placeholder="Ex: 48291", key="search_ref_agent")
    
    if search_ref:
        df_factures = cloud_conn.read(worksheet="Factures")
        facture_info = df_factures[df_factures["ID"].astype(str) == str(search_ref)]
        
        if not facture_info.empty:
            f = facture_info.iloc[0]
            status_color = "#2e7d32" if f["Statut"] == "PAYÉ" else "#d32f2f"
            st.markdown(f"""
            <div style="border: 2px solid {status_color}; padding: 15px; background: white; color: black; border-radius: 5px; font-family: monospace;">
                <b style="color:{status_color}; font-size: 1.2em;">● STATUT : {f['Statut']}</b><br>
                <hr>
                <b>RÉFÉRENCE :</b> #{f['ID']}<br>
                <b>ÉMETTEUR  :</b> {f['Emetteur']}<br>
                <b>CIBLE     :</b> {f['Cible']}<br>
                <b>MONTANT   :</b> {f['Montant']}$<br>
                <b>MOTIF     :</b> {f['Motif']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Référence introuvable dans la base nationale.")
    
    st.divider()

    # --- 2. GESTION DU CITOYEN SÉLECTIONNÉ ---
    if target == "---":
        st.warning("⚠️ Veuillez sélectionner un citoyen dans le dossier en haut pour agir.")
    else:
        st.markdown(f"""
            <div style="background-color: #000; padding: 20px; border-radius: 10px; border-left: 10px solid #d32f2f; margin-bottom: 20px;">
                <h1 style="color: white; margin: 0; letter-spacing: 2px; font-size: 2.5em;">👤 {target.upper()}</h1>
                <p style="color: #d32f2f; font-weight: bold; margin: 0;">UNITÉ D'INTERVENTION - ACCÈS AUTORISÉ</p>
            </div>
        """, unsafe_allow_html=True)

        col_saisie, col_ticket, col_vehicules = st.columns([1, 1, 1])

        # --- A. COLONNE SAISIE ---
        with col_saisie:
            st.markdown("### 📝 Saisie")
            with st.container(border=True):
                f_val = st.number_input("Montant de l'amende ($)", min_value=0, step=50, key="f_val_agent")
                
                # Restriction Points au Staff
                f_pts = 0
                if st.session_state.user_auth == "Staff":
                    f_pts = st.number_input("Points à retirer", min_value=0, max_value=12, step=1, key="f_pts_agent")
                else:
                    st.info("ℹ️ Retrait de points : Accès Staff uniquement.")
                
                f_motif = st.text_input("Motif de la sanction", placeholder="ex: Conduite dangereuse", key="f_mot_agent")
                
                v_list = ["AUCUN / PIÉTON"] + df_i[df_i["Nom d'utilisateur ROBLOX"] == target]["Numéro de la plaque"].tolist()
                f_plate_link = st.selectbox("Plaque concernée :", v_list, key="f_plate_agent")
                
                if st.button("🚨 ENVOYER LA SANCTION", use_container_width=True):
                    if f_motif:
                        with st.spinner("Transmission au serveur..."):
                            new_id = random.randint(10000, 99999) # Génération de la référence
                            
                            # Mise à jour points (Staff seulement)
                            if st.session_state.user_auth == "Staff" and f_pts > 0:
                                idx_p = df_p[df_p["Nom Roblox"] == target].index[0]
                                df_p.at[idx_p, "PTS"] = max(0, int(df_p.at[idx_p, "PTS"]) - f_pts)
                                cloud_conn.update(worksheet="Points Permis", data=df_p)
                            
                            # Enregistrement Facture
                            df_factures = cloud_conn.read(worksheet="Factures")
                            new_row = {
                                "ID": new_id, 
                                "Cible": target, 
                                "Emetteur": st.session_state.user_auth,
                                "Montant": f_val, 
                                "Motif": f"{f_motif} (Plaque: {f_plate_link} | -{f_pts}pts)",
                                "Statut": "EN ATTENTE"
                            }
                            df_factures = pd.concat([df_factures, pd.DataFrame([new_row])], ignore_index=True)
                            cloud_conn.update(worksheet="Factures", data=df_factures)
                            
                            record_log(st.session_state.user_auth, f"Sanction #{new_id} envoyée à {target}")
                            st.success(f"✅ Envoyé ! Réf: #{new_id}")
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("⚠️ Le motif est obligatoire.")

        # --- B. COLONNE APERÇU ---
        with col_ticket:
            st.markdown("### 🖼️ Aperçu Live")
            prefix = "POLICE NATIONALE" if st.session_state.user_auth == "Staff" else "UNITÉ RCT"
            st.markdown(f"""
            <div style="border: 2px solid #000; padding: 15px; background: white; color: black; font-family: monospace; box-shadow: 6px 6px 0px #000;">
                <center><b style="text-decoration: underline;">FACTURE OFFICIELLE</b><br><small>{prefix}</small></center>
                <hr style="border-top: 1px dashed #000;">
                <small>
                    <b>RÉFÉRENCE :</b> AUTO-GEN<br>
                    <b>CIBLE     :</b> {target}<br>
                    <b>PLAQUE    :</b> {f_plate_link}<br>
                    <b>MOTIF     :</b> {f_motif if f_motif else "..."}
                </small>
                <hr style="border-top: 1px dashed #000;">
                <div style="display: flex; justify-content: space-between; font-weight: bold;">
                    <span style="color:red;">PTS: -{f_pts}</span>
                    <span>TOTAL: {f_val}$</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # --- C. COLONNE GARAGE ---
        with col_vehicules:
            st.markdown("### 🚗 Garage du Citoyen")
            mes_v = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
            if not mes_v.empty:
                for _, v in mes_v.iterrows():
                    assu = str(v['Assurance']).upper()
                    is_ok = any(x in assu for x in ["RCT", "AVERIS"])
                    color = "#000000" if is_ok else "#d32f2f"
                    st.markdown(f"""
                    <div style="border: 2px solid black; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; margin-bottom: 10px;">
                        <center><b>TITRE DE CIRCULATION</b><br><small>RÉPUBLIQUE DE RENSSERLAER</small></center>
                        <hr style="border-top: 1px solid #ccc; margin: 8px 0;">
                        <b>DATE :</b> {datetime.now().strftime('%d/%m/%Y')}<br>
                        <b>MODÈLE :</b> {v['Marque du véhicule']}<br>
                        <b>PLAQUE :</b> <span style="border: 1px solid black; padding: 0 3px;">{v['Numéro de la plaque']}</span><br>
                        <b>ASSURANCE :</b> {v['Assurance']}
                        <hr style="border-top: 1px solid #ccc; margin: 8px 0;">
                        <div style="text-align: center; color: {color}; font-weight: bold; font-size: 0.8em;">
                            ● {"CERTIFIÉ CONFORME" if is_ok else "DÉFAUT D'ASSURANCE"}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun véhicule.")
# --- ONGLET 3 : ADMINISTRATION (STAFF ONLY) ---
if st.session_state.user_auth == "Staff":
    with tabs[2]:
        st.markdown('<div class="header-box"><h2>🛠️ PANNEAU D\'ADMINISTRATION High-Sec</h2></div>', unsafe_allow_html=True)
        
        # --- SECTION 1 : CRÉATION DE PROFIL ---
        st.markdown("### 👤 Création de Dossier Citoyen")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                new_name = st.text_input("Nom d'utilisateur ROBLOX", placeholder="Pseudo exact", key="admin_new_name")
                new_discord = st.text_input("Utilisateur Discord", placeholder="pseudo#0000", key="admin_new_discord")
            with c2:
                new_job = st.selectbox("Emploiement initial", ["Sans-Emploi", "Agent RCT", "Entreprise Privée", "Service Public"], key="admin_new_job")
                new_pts = st.slider("Points Permis (Départ)", 0, 25, 25, key="admin_new_pts")

            if st.button("🆕 GÉNÉRER LE DOSSIER (15k + Date Auto)", use_container_width=True):
                if new_name and new_name not in df_b["Nom Roblox"].values:
                    with st.spinner("Initialisation du citoyen..."):
                        today_str = datetime.now().strftime("%d/%m/%Y")
                        
                        # Banque (Solde 15000 auto)
                        new_bank_row = pd.DataFrame([{
                            "Nom Roblox": new_name,
                            "Utilisateur Discord": new_discord,
                            "Solde": 15000, 
                            "Emploiement": new_job,
                            "Date d'arrivée": today_str
                        }])
                        df_b_new = pd.concat([df_b, new_bank_row], ignore_index=True)
                        cloud_conn.update(worksheet="Banque", data=df_b_new)

                        # Permis
                        new_pts_row = pd.DataFrame([{
                            "Nom Roblox": new_name,
                            "PTS": new_pts,
                            "Validité": "OUI" if new_pts > 0 else "NON"
                        }])
                        df_p_new = pd.concat([df_p, new_pts_row], ignore_index=True)
                        cloud_conn.update(worksheet="Points Permis", data=df_p_new)

                        record_log(st.session_state.user_auth, f"Création profil : {new_name} (Solde: 15k)")
                        st.success(f"✅ Dossier créé pour {new_name} !")
                        st.cache_data.clear()
                        time.sleep(1.5)
                        st.rerun()
                else:
                    st.error("⚠️ Nom invalide ou déjà existant.")

        st.divider()

        # --- SECTION 2 : LOGS ET STATISTIQUES ---
        col_admin_left, col_admin_right = st.columns(2)
        
        with col_admin_left:
            st.markdown("### 📜 Journaux d'Audit")
            with st.container(border=True):
                if st.session_state.audit_logs:
                    # Look style terminal pour les logs
                    log_text = "\n".join(list(reversed(st.session_state.audit_logs)))
                    st.code(log_text, language="bash")
                else:
                    st.info("Aucune activité enregistrée.")
            
            if st.button("🗑️ EFFACER LES LOGS"):
                st.session_state.audit_logs = []
                st.rerun()

        with col_admin_right:
            st.markdown("### 📊 État du Système")
            with st.container(border=True):
                # ICI TES COMPTEURS DE DONNÉES
                st.success(f"👥 **Citoyens enregistrés :** {len(df_b)}")
                st.info(f"🚗 **Véhicules immatriculés :** {len(df_i)}")
                st.warning(f"🪪 **Dossiers permis :** {len(df_p)}")
                
                st.divider()
                st.write("**Maintenance :**")
                if st.button("♻️ FORCER LA SYNCHRO CLOUD", use_container_width=True):
                    st.cache_data.clear()
                    st.success("Données synchronisées !")
                    time.sleep(1)
                    st.rerun()
# --- SÉCURITÉ : NETTOYAGE DES VARIABLES FANTÔMES ---
# Supprime ou commente absolument ces lignes si elles traînent encore en bas de ton fichier :
# with col_vehicule_view: <--- C'EST ÇA QUI FAIT PLANTER L'AFFICHAGE !

# ======================================================================================
# 8. PIED DE PAGE
# ======================================================================================
st.divider()
st.caption(f"Terminal Fédéral RCRP FR | Opérationnel | © 2026 République de Rensselaer")
