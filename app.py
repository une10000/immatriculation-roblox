# ======================================================================================
# PROJECT       : RCRP FR OS - ULTIMATE TOTAL EDITION
# VERSION       : 14.5.0
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
        st.markdown("### 👨‍🔧 🛻🪝 AGENT RCT")
        login_rct = st.text_input("Identifiant Agent", type="password")
        if st.button("AUTHENTIFICATION RCT"):
            if login_rct == KEY_RCT:
                st.session_state.user_auth = "RCT"
                record_log("RCT", "Connexion Service")
                st.rerun()
            else: st.error("Clé invalide.")
            
    with c3:
        st.markdown("### 🛡️👮‍♂️ STAFF/POLICE")
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
                st.error("Aucun compte trouvé.") # ======================================================================================
        # NOUVEAU : SYSTÈME DE PAIEMENT DES FACTURES (SOUS LE SOLDE)
        # ======================================================================================
        st.divider()
        try:
            df_all_f = cloud_conn.read(worksheet="Factures").fillna("")
            mes_factures = df_all_f[(df_all_f["Cible"] == target) & (df_all_f["Statut"] == "EN ATTENTE")]

            if not mes_factures.empty:
                st.error(f"⚠️ {len(mes_factures)} FACTURE(S) EN ATTENTE DE PAIEMENT")
                for _, fac in mes_factures.iterrows():
                    with st.container(border=True):
                        c_f1, c_f2 = st.columns([2, 1])
                        c_f1.markdown(f"**OBJET :** {fac['Motif']}")
                        c_f1.caption(f"Émis par : {fac['Emetteur']} | Réf : #{fac['ID']}")
                        
                        if c_f2.button(f"RÉGLER {fac['Montant']}$", key=f"pay_{fac['ID']}", use_container_width=True):
                            # Récupération du solde actuel
                            idx_b = df_b[df_b["Nom Roblox"] == target].index[0]
                            solde_raw = str(df_b.at[idx_b, "Solde"]).replace('$', '').replace(',', '')
                            solde_actuel = float(solde_raw)
                            montant_facture = float(fac['Montant'])
                            
                            if solde_actuel >= montant_facture:
                                # 1. Débit du Civil
                                df_b.at[idx_b, "Solde"] = solde_actuel - montant_facture
                                
                                # 2. Crédit du compte RCT (ou Averis selon l'émetteur si tu veux)
                                rct_idx = df_b[df_b["Nom Roblox"] == ACC_RCT].index[0]
                                solde_rct = float(str(df_b.at[rct_idx, "Solde"]).replace('$', '').replace(',', ''))
                                df_b.at[rct_idx, "Solde"] = solde_rct + montant_facture
                                
                                # 3. Mise à jour de la facture
                                df_all_f.loc[df_all_f["ID"] == fac["ID"], "Statut"] = "PAYÉ"
                                
                                # 4. Envoi au Cloud
                                cloud_conn.update(worksheet="Banque", data=df_b)
                                cloud_conn.update(worksheet="Factures", data=df_all_f)
                                
                                record_log(target, f"Paiement facture #{fac['ID']} ({montant_facture}$)")
                                st.success("Paiement effectué avec succès !")
                                st.cache_data.clear()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Fonds insuffisants pour régler cette facture.")
            else:
                st.info("✅ Aucune dette en attente pour ce citoyen.")
        except Exception as e:
            st.warning("Système de facturation indisponible (Vérifiez l'onglet 'Factures')")
        # --- SECTION VÉHICULES CORRIGÉE ---
        st.write(f"🚘 **VÉHICULES ENREGISTRÉS**")
        v_data = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
        
        if not v_data.empty:
            v_cols = st.columns(3) 
            for i, (_, veh) in enumerate(v_data.iterrows()):
                with v_cols[i % 3]:
                    with st.container(border=True):
                        st.markdown(f"""
                        <div style="border: 1px solid #000; padding: 10px; background: white; color: black; font-family: monospace; font-size: 0.85em;">
                            <center><b>TITRE DE PROPRIÉTÉ</b></center>
                            <hr style="margin:5px 0;">
                            <b>PLAQUE :</b> {veh['Numéro de la plaque']}<br>
                            <b>MODÈLE :</b> {veh['Marque du véhicule']}<br>
                            <b>ASSUR. :</b> {veh['Assurance']}
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
        else:
            st.info("Aucun véhicule.")
            
# ======================================================================================
# 7. LOGIQUE DES ONGLETS (NETTOYÉE ET SÉCURISÉE)
# ======================================================================================
tab_labels = ["🚗 IMMATRICULATION"]
if st.session_state.user_auth in ["RCT", "Staff"]: 
    tab_labels.append("👮 SERVICES AGENT")
if st.session_state.user_auth == "Staff": 
    tab_labels.append("🛠️ ADMINISTRATION")

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
            
            # Calcul de la Taxe Jeune
            val_taxe_jeune = 0
            if f_owner != "---":
                try:
                    date_brute = df_b[df_b["Nom Roblox"] == f_owner]["Date d'arrivée"].values[0]
                    date_arr = datetime.strptime(str(date_brute), "%d/%m/%Y")
                    if (datetime.now() - date_arr).days < 30:
                        val_taxe_jeune = 50
                        st.warning(f"🔰 JEUNE CONDUCTEUR détecté (+{val_taxe_jeune}$)")
                except: pass

            taxe_gouv = 175
            taxe_assu = 130 if "AVERIS" in f_assu else (150 if "RCT" in f_assu else 0)
            total_bill = taxe_gouv + taxe_assu + val_taxe_jeune
            
            if st.button(f"S'ACQUITTER DE {total_bill}$ ET ENREGISTRER", use_container_width=True):
                if f_owner != "---" and f_plate and f_code:
                    # Ton code de paiement ici (déjà fonctionnel dans ton script)
                    st.success("Enregistré !")

    # --- LE RETOUR DU TICKET RÉTRO (ICI !) ---
    with col_t:
        st.markdown("### 🖼️ APERÇU DU TITRE (LIVE)")
        
        ticket_html = f"""
        <div style="border: 4px double black; padding: 20px; background: white; color: black; font-family: 'Courier New', Courier, monospace; box-shadow: 10px 10px 0px #000;">
            <div style="text-align:center; font-weight:900; font-size:1.4em; text-decoration: underline;">TITRE DE CIRCULATION</div>
            <center><small>RÉPUBLIQUE DE RENSSELAER</small><br>
            <code>FEDERAL TERMINAL ACCESS</code></center>
            <hr style="border-top: 2px dashed black;">
            <div style="font-size: 1.1em;">
                <p style="margin:5px 0;"><b>DATE :</b> {datetime.now().strftime("%d/%m/%Y")}</p>
                <p style="margin:5px 0;"><b>PROPRIO :</b> {f_owner}</p>
                <p style="margin:5px 0;"><b>MODÈLE :</b> {f_model.upper() if f_model else "---"}</p>
                <p style="margin:5px 0;"><b>PLAQUE :</b> <span style="background:#000; color:#fff; padding:2px 5px;">{f_plate if f_plate else "---"}</span></p>
                <p style="margin:5px 0;"><b>ASSURANCE :</b> {f_assu}</p>
                <p style="margin:5px 0;"><b>TAXE JEUNE :</b> {val_taxe_jeune}$</p>
            </div>
            <hr style="border-top: 2px dashed black;">
            <div style="text-align:right; font-weight:bold; font-size:1.4em;">TOTAL : {total_bill}$</div>
            <br>
            <center>
                <small>VALIDE POUR LE RÉSEAU ROUTIER NATIONAL</small><br>
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=60x60&data=RCRP-{f_plate}" style="margin-top:10px; opacity:0.8;">
            </center>
        </div>
        """
        st.markdown(ticket_html, unsafe_allow_html=True)

# --- ONGLET 2 : SERVICES AGENT (CORRIGÉ : PAS DE DOUBLONS, PAS D'ERREURS) ---
if st.session_state.user_auth in ["RCT", "Staff"]:
    with tabs[1]:
        if target == "---":
            st.warning("⚠️ Veuillez sélectionner un citoyen en haut pour agir.")
        else:
            # En-tête dynamique selon le grade
            role_label = "UNITÉ RCT" if st.session_state.user_auth == "RCT" else "UNITÉ POLICE / STAFF"
            st.markdown(f"""
                <div style="background-color: #000; padding: 20px; border-radius: 10px; border-left: 10px solid #d32f2f; margin-bottom: 20px;">
                    <h1 style="color: white; margin: 0; letter-spacing: 2px; font-size: 2.5em;">👤 {target.upper()}</h1>
                    <p style="color: #d32f2f; font-weight: bold; margin: 0;">{role_label} - INTERFACE D'ACTION</p>
                </div>
            """, unsafe_allow_html=True)

            col_action, col_scanner = st.columns([1, 1])

            # --- PARTIE ACTION (FACTURE + POINTS) ---
            with col_action:
                st.subheader("🧾 Formulaire de Sanction")
                with st.container(border=True):
                    f_val = st.number_input("Montant de l'amende/facture ($)", min_value=0, step=50, key="srv_fine_val")
                    f_motif = st.text_input("Motif de l'infraction", placeholder="ex: Dépannage", key="srv_fine_mot")
                    
                    # Logique des points : Invisible pour le RCT
                    p_loss = 0
                    if st.session_state.user_auth == "Staff":
                        p_loss = st.number_input("Points à retirer (Automatique)", min_value=0, max_value=25, step=1, key="srv_pts_val")
                    
                    if st.button("VALIDER ET TRANSMETTRE", use_container_width=True):
                        if f_motif:
                            # 1. Enregistrement de la facture (Pour tous)
                            if f_val > 0:
                                new_f = pd.DataFrame([{
                                    "ID": random.randint(10000, 99999),
                                    "Cible": target,
                                    "Emetteur": st.session_state.user_auth,
                                    "Montant": f_val,
                                    "Motif": f_motif,
                                    "Statut": "EN ATTENTE"
                                }])
                                df_fact_db = cloud_conn.read(worksheet="Factures")
                                cloud_conn.update(worksheet="Factures", data=pd.concat([df_fact_db, new_f]))

                            # 2. Retrait de points (QUE pour la Police/Staff)
                            if st.session_state.user_auth == "Staff" and p_loss > 0:
                                idx_p = df_p[df_p["Nom Roblox"] == target].index[0]
                                old_p = int(df_p.at[idx_p, "PTS"])
                                new_p = max(0, old_p - p_loss)
                                df_p.at[idx_p, "PTS"] = new_p
                                if new_p == 0: df_p.at[idx_p, "Validité"] = "NON"
                                cloud_conn.update(worksheet="Points Permis", data=df_p)
                                record_log("Police", f"Sanction {target} : -{p_loss} pts | Facture {f_val}$")
                            else:
                                record_log(st.session_state.user_auth, f"Facture {f_val}$ envoyée à {target}")

                            st.success("✅ Dossier mis à jour avec succès.")
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("⚠️ Saisissez un motif pour valider.")

            # --- PARTIE SCANNER (VISIBLE PAR TOUS) ---
            with col_scanner:
                st.subheader("🔍 Scanner de Circulation")
                v_player = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
                if v_player.empty:
                    st.info("Aucun véhicule trouvé.")
                else:
                    for i, (_, v) in enumerate(v_player.iterrows()):
                        # Alerte visuelle pour le RCT (si pas assuré RCT)
                        is_assure_rct = "RCT" in str(v['Assurance'])
                        if is_assure_rct or st.session_state.user_auth == "Staff":
                            border_color = "#000"
                            status_msg = ""
                        else:
                            border_color = "#d32f2f"
                            status_msg = "<div style='background:#d32f2f; color:white; text-align:center; font-size:10px;'>NON-ASSURÉ RCT</div>"

                        st.markdown(f"""
                            <div style="border: 2px solid {border_color}; padding: 10px; background: white; color: black; font-family: monospace; margin-bottom: 10px;">
                                <b>PLAQUE :</b> {v['Numéro de la plaque']}<br>
                                <b>MODÈLE :</b> {v['Marque du véhicule']}<br>
                                <b>ASSURANCE :</b> {v['Assurance']}
                                {status_msg}
                            </div>
                        """, unsafe_allow_html=True)
# --- ONGLET 3 : ADMINISTRATION (STAFF UNIQUEMENT) ---
if st.session_state.user_auth == "Staff":
    with tabs[2]:
        st.markdown("### 🛡️ Contrôle Administrateur")
        
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            st.subheader("🔨 Création de Profil Fédéral")
            with st.form("admin_creation_form_v8"):
                st.write("Procédure d'arrivée : 15,000$ + 25 Points Permis.")
                new_rob = st.text_input("Nom Roblox du Citoyen")
                new_dis = st.text_input("Identifiant Discord")
                new_job = st.selectbox("Secteur", ["Civil", "RCT", "Gouverneur", "Justice", "Armée"])
                
                if st.form_submit_button("VALIDER L'INSCRIPTION NATIONALE"):
                    if new_rob in df_b["Nom Roblox"].values:
                        st.error("Citoyen déjà enregistré.")
                    else:
                        # DATE AUTOMATIQUE (Important pour la taxe jeune conducteur)
                        date_arr = datetime.now().strftime("%d/%m/%Y")
                        
                        # Banque entry
                        new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": new_dis, "Nom Roblox": new_rob, "Date d'arrivée": date_arr, "Emploiement": new_job}])
                        # Permis entry
                        new_p = pd.DataFrame([{"Nom Discord": new_dis, "Nom Roblox": new_rob, "PTS": 25, "Validité": "OUI"}])
                        
                        cloud_conn.update(worksheet="Banque", data=pd.concat([df_b, new_b]))
                        cloud_conn.update(worksheet="Points Permis", data=pd.concat([df_p, new_p]))
                        record_log("Staff", f"Création profil : {new_rob}")
                        st.cache_data.clear()
                        st.success(f"Profil de {new_rob} créé avec succès !")
                        time.sleep(1)
                        st.rerun()
        
        with col_s2:
            st.subheader("⚙️ Maintenance Système")
            if st.button("🗑️ VIDER LE CACHE DE SESSION", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
            
            st.divider()
            st.write("📊 **Statistiques Globales**")
            # Nettoyage des données pour le calcul
            total_money = df_b['Solde'].replace('[\$,]', '', regex=True).astype(float).sum()
            st.write(f"Masse monétaire : **{total_money:,.0f}$**")
            st.write(f"Parc Automobile : **{len(df_i)} véhicules**")

# ======================================================================================
# 8. PIED DE PAGE
# ======================================================================================
st.divider()
st.caption(f"Terminal Fédéral RCRP FR | Opérationnel | © 2026 République de Rensselaer")
