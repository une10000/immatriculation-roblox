# ======================================================================================
# PROJECT       : RCRP FR OS - ULTIMATE EDITION
# VERSION       : 14.6.0
# BUILD DATE    : 09/02/2026
# ======================================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time
import random
from textwrap import dedent

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
        from datetime import datetime, timedelta, timezone
        import streamlit.components.v1 as components

        # 1. Calcul de l'heure UTC+1
        t_now = datetime.now(timezone.utc) + timedelta(hours=1)

        # 2. Dictionnaires de traduction
        jours = {"Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi", "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche"}
        mois = {"January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril", "May": "Mai", "June": "Juin", "July": "Juillet", "August": "Août", "September": "Septembre", "October": "Octobre", "November": "Novembre", "December": "Décembre"}

        # 3. Variables de date
        nom_jour = jours[t_now.strftime('%A')]
        num_jour = t_now.strftime('%d')
        nom_mois = mois[t_now.strftime('%B')]
        annee = t_now.strftime('%Y')

        # 4. Bloc Date (Forcé à gauche)
        st.markdown(f"""
            <div style="text-align: left; line-height: 1.1; margin-left: 0; padding-left: 0;">
                <span style="font-size: 1.5em;">📅</span><br>
                <b style="font-size: 1.2em;">{nom_jour},</b><br>
                <span style="font-size: 1.1em;">{num_jour} {nom_mois} {annee}</span>
            </div>
        """, unsafe_allow_html=True)

        st.write("") 

        # 5. Bloc Horloge Dynamique (Correction du décalage)
        st.markdown("<div style='text-align: left; font-size: 1.5em; margin-bottom: 0; margin-left: 0;'>⏰</div>", unsafe_allow_html=True)
        
        # Le secret est dans le "margin-left: -8px" pour compenser la marge naturelle de l'iframe Streamlit
        components.html(f"""
            <div id="clock" style="
                font-family: 'Source Sans Pro', sans-serif; 
                font-size: 24px; 
                font-weight: bold; 
                text-align: left; 
                color: #31333F;
                margin-left: -8px; 
                margin-top: -5px;
            "></div>
            <script>
                function updateClock() {{
                    const now = new Date();
                    const options = {{ timeZone: 'Europe/Paris', hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }};
                    const timeString = now.toLocaleTimeString('fr-FR', options);
                    document.getElementById('clock').textContent = timeString;
                }}
                setInterval(updateClock, 1000);
                updateClock();
            </script>
        """, height=40)
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
# 5. LOCKSCREEN (CONNEXION) - UNITÉ FÉDÉRALE DE RENSSELAER
# ======================================================================================
if st.session_state.user_auth is None:
    # --- CONFIGURATION INTERFACE & CORRECTIFS ---
    st.markdown("""
        <style>
            [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none; }
            [data-testid="stStatusWidget"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

    # 1. CALCUL DU MOMENT ET DE L'HEURE (UTC+1)
    import time
    from datetime import datetime, timedelta, timezone
    
    t_now_lock = datetime.now(timezone.utc) + timedelta(hours=1)
    h_lock = t_now_lock.hour
    heure_formattee = t_now_lock.strftime("%H:%M")
# --- LOGIQUE JOUR / NUIT ---
    if 5 <= h_lock < 18:
        salut_complet = "Bonjour☀️"
        # Ajout d'un soleil physique en haut à droite + rayons synchronisés
        pattern_style = (
            "background-color: #87CEEB; "
            "background-image: "
            # 1. Les rayons qui partent du coin haut-droite (85% 10%)
            "conic-gradient(from 200deg at 85% 10%, "
            "transparent 0deg, rgba(255,255,255,0.4) 15deg, transparent 30deg, "
            "rgba(255,223,137,0.5) 45deg, transparent 60deg, "
            "rgba(255,255,255,0.4) 75deg, transparent 90deg), "
            # 2. Le petit soleil brillant dans l'angle
            "radial-gradient(circle at 85% 10%, #FFF9E3 0%, #FFD700 15%, rgba(255,215,0,0.4) 30%, transparent 60%), "
            # 3. Les nuages vaporeux habituels
            "radial-gradient(circle at 50% 25%, rgba(255,255,255,0.8) 0%, transparent 60%), "
            "radial-gradient(circle at 50% 75%, rgba(255,255,255,0.6) 0%, transparent 65%); "
            "background-repeat: no-repeat; "
            "background-size: cover;"
        )
        t_color = "#1E1E1E"
        glow = "0 0 30px rgba(255, 255, 255, 1), 0 0 60px rgba(255, 200, 0, 0.6)"
    else:
        salut_complet = "Bonsoir🌕"
        pattern_style = (
            "background-color: #05070a; "
            "background-image: "
            "radial-gradient(1px 1px at 25% 35%, white, transparent), "
            "radial-gradient(1px 1px at 50% 10%, white, transparent), "
            "radial-gradient(2px 2px at 10% 80%, white, transparent), "
            "radial-gradient(1px 1px at 90% 20%, white, transparent), "
            "radial-gradient(1.5px 1.5px at 70% 60%, white, transparent); "
            "background-size: 150px 150px, 200px 200px, 250px 250px, 180px 180px, 220px 220px;"
        )
        t_color = "#FFFFFF"
        glow = "0 0 40px rgba(255,255,255,0.9), 0 0 80px rgba(255,255,255,0.4)"

    # --- AFFICHAGE UNITAIRE ---
    st.markdown(f"""
        <div style="text-align: center; margin-top: -30px; padding: 70px 20px 45px 20px; border-radius: 20px 20px 0 0; color: {t_color}; {pattern_style}">
            <h1 style="font-size: 5.5em; margin: 0; font-weight: 900; letter-spacing: -3px; text-shadow: {glow};">
                {salut_complet}
            </h1>
            <p style="font-size: 1.1em; opacity: 0.7; letter-spacing: 5px; font-weight: bold; text-transform: uppercase; margin-top: 20px;">Unité Fédérale de Rensselaer</p>
            <div style="font-family: monospace; font-size: 2.2em; letter-spacing: 5px; opacity: 0.8; font-weight: bold; border-top: 1px solid {t_color}33; display: inline-block; padding-top: 10px; margin-top: 5px;">
                {heure_formattee}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. EN-TÊTE RÉPUBLIQUE
    st.markdown("""
    <div class="header-box" style="margin-top: 0px; border-radius: 0 0 20px 20px; border-top: 1px solid rgba(255,255,255,0.05); padding: 20px;">
    <center>
        <span style="font-size: 40px;">👤</span> <h2 style="margin-bottom:0; margin-top:10px;">🏛️ RÉPUBLIQUE DE RENSSELAER</h2>
        <p style="font-size: 1em; opacity: 0.8;">TERMINAL FÉDÉRAL D'OPÉRATIONS NATIONALES</p>
        <hr style="border-color: rgba(255,255,255,0.1); margin: 10px 0;">
        <small style="opacity: 0.6;">VERSION 14.6.0 | SÉCURISÉ PAR PROTOCOLE RCRP-OS</small>
    </center>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("⚠️ **AVERTISSEMENT :** Toute action effectuée sur ce terminal est enregistrée.")
    st.write("---")

    # 3. COLONNES D'ACCÈS
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 👥 CIVIL")
        if st.button("ACCÉDER AU TERMINAL", use_container_width=True):
            st.session_state.user_auth = "Civil"
            st.rerun()
    with c2:
        st.markdown("### 👨‍🔧 AGENT RCT")
        login_rct = st.text_input("Identifiant Agent", type="password", key="l_rct")
        if st.button("AUTHENTIFICATION RCT", use_container_width=True):
            if login_rct == KEY_RCT:
                st.session_state.user_auth = "RCT"
                st.rerun()
            else: st.error("Clé invalide.")
    with c3:
        st.markdown("### 🛡️ STAFF/POLICE")
        login_staff = st.text_input("Clé Maîtresse", type="password", key="l_staff")
        if st.button("ACCÈS ADMINISTRATEUR", use_container_width=True):
            if login_staff == KEY_STAFF:
                st.session_state.user_auth = "Staff"
                st.rerun()
            else: st.error("Accès refusé.")

    time.sleep(60)
    st.rerun()
    st.stop()
# ======================================================================================
# LE RESTE DU CODE (S'affiche uniquement après connexion)
# ======================================================================================
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
        
        # --- COLONNE 1 : POINTS & PERMIS ---
        with col1:
            p_data = df_p[df_p["Nom Roblox"] == target]
            if not p_data.empty:
                pts_val = int(p_data.iloc[0]["PTS"])
                
                c_pts, c_vide, c_motif_p = st.columns([3, 0.5, 2])
                
                with c_pts:
                    st.metric("POINTS PERMIS", f"{pts_val}/25")
                    status_color = "green" if pts_val > 0 else "red"
                    st.markdown(f"Statut : <b style='color:{status_color};'>{'VALIDE' if pts_val > 0 else 'SUSPENDU'}</b>", unsafe_allow_html=True)
                
                with c_motif_p:
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

        # --- COLONNE 2 : BANQUE ---
        with col2:
            b_data = df_b[df_b["Nom Roblox"] == target]
            if not b_data.empty:
                with st.container(border=False):
                    c_info, c_vide, c_motif = st.columns([3, 1, 2])
                    
                    with c_info:
                        st.metric("SOLDE BANCAIRE", f"{b_data.iloc[0]['Solde']}$")
                        st.write(f"🏢 Métier : **{b_data.iloc[0]['Emploiement']}**")
                        st.caption(f"📅 Arrivée : {b_data.iloc[0]['Date d\'arrivée']}")
                    
                    with c_motif:
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

# --- FIN DE LA COLONNE 2 (Vérifie bien que ton code précédent finit ici) ---
        
        with col3:
            st.markdown("### 📁 ARCHIVES")
            try:
                # 1. Lecture des données
                df_f_history = cloud_conn.read(worksheet="Factures").fillna("")
                
                # 2. Filtre sur les factures PAYÉES
                historique = df_f_history[
                    (df_f_history["Cible"] == target) & 
                    (df_f_history["Statut"] == "PAYÉ")
                ]

                if not historique.empty:
                    with st.container(height=400):
                        for _, f in historique.iterrows():
                            # --- BOUTON DE REMBOURSEMENT ADMIN ---
                            if st.session_state.user_auth in ["Staff", "Admin"]:
                                if st.button(f"🔄 Rembourser #{f['ID']}", key=f"refund_{f['ID']}", use_container_width=True):
                                    try:
                                        # On récupère les données fraîches
                                        df_b_sync = cloud_conn.read(worksheet="Banque")
                                        df_f_sync = cloud_conn.read(worksheet="Factures")
                                        
                                        idx_civil = df_b_sync[df_b_sync["Nom Roblox"] == target].index[0]
                                        montant = float(str(f['Montant']).replace('$', '').replace(',', ''))
                                        
                                        # Remboursement
                                        solde_c = float(str(df_b_sync.at[idx_civil, "Solde"]).replace('$', ''))
                                        df_b_sync.at[idx_civil, "Solde"] = solde_c + montant
                                        
                                        idx_rct = df_b_sync[df_b_sync["Nom Roblox"] == ACC_RCT].index[0]
                                        solde_rct = float(str(df_b_sync.at[idx_rct, "Solde"]).replace('$', ''))
                                        df_b_sync.at[idx_rct, "Solde"] = solde_rct - montant
                                        
                                        # Mise à jour statut
                                        df_f_sync.loc[df_f_sync["ID"] == f["ID"], "Statut"] = "REMBOURSÉ"
                                        
                                        # Envoi groupé
                                        cloud_conn.update(worksheet="Banque", data=df_b_sync)
                                        cloud_conn.update(worksheet="Factures", data=df_f_sync)
                                        
                                        st.success(f"Facture #{f['ID']} remboursée !")
                                        st.cache_data.clear()
                                        time.sleep(1)
                                        st.rerun()
                                    except Exception as e_inner:
                                        st.error(f"Détail erreur : {e_inner}")
                            
                            # --- TICKET VISUEL ---
                            st.markdown(f"""
                            <div style="border: 1px solid #000; padding: 10px; background: #f9f9f9; color: black; font-family: 'Courier New', monospace; margin-bottom: 8px; border-left: 5px solid green;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.8em;">
                                    <b>REF: #{f['ID']}</b>
                                    <b style="color: green;">ACQUITTÉE ✔</b>
                                </div>
                                <hr style="margin: 5px 0; border-top: 1px dashed #000;">
                                <div style="font-size: 0.9em;">
                                    <b>MOTIF :</b> {f['Motif']}<br>
                                    <b>MONTANT :</b> {f['Montant']}$
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Aucun paiement archivé.")
            except Exception as e_outer:
                st.error(f"Erreur d'accès aux archives : {e_outer}")
# ======================================================================================
# 7. LOGIQUE DES ONGLETS (CORRIGÉE)
# ======================================================================================

# =============================================================

# ======================================================================================
# NOUVEAU : SYSTÈME DE PAIEMENT DES FACTURES (STYLE TICKET)
# ======================================================================================
# --- RÉCUPÉRATION DES DONNÉES (À ajouter avant le if) ---
df_all_f = cloud_conn.read(worksheet="Factures").fillna("")
# On filtre pour ne voir que les factures du citoyen sélectionné (target)
mes_factures = df_all_f[(df_all_f["Cible"] == target) & (df_all_f["Statut"] == "EN ATTENTE")]

# --- NOUVEAU : SYSTÈME DE PAIEMENT DES FACTURES (STYLE TICKET) ---
if not mes_factures.empty:
    st.error(f"⚠️ {len(mes_factures)} FACTURE(S) EN ATTENTE DE PAIEMENT")
    for _, fac in mes_factures.iterrows():
        # ... le reste de ton code (Calcul timer + Ticket HTML)
            
            # --- CALCUL DU TIMER ---
            try:
                date_limite = datetime.strptime(str(fac['Date_Limite']), "%d/%m/%Y %H:%M:%S")
                temps_restant = date_limite - datetime.now()
                
                if temps_restant.total_seconds() > 0:
                    h, rem = divmod(int(temps_restant.total_seconds()), 3600)
                    m, _ = divmod(rem, 60)
                    timer_info = f"⌛ EXPIRE DANS : {h}h {m}min"
                    t_color = "#f39c12" 
                else:
                    timer_info = "⚠️ DÉLAI DÉPASSÉ (IMPAYÉ)"
                    t_color = "#d32f2f"
            except:
                timer_info = "⌛ Délai : 24 heures"
                t_color = "#555"

            # --- LE TICKET ---
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
                    <b style="color: {t_color};">{timer_info}</b>
                </div>
                <hr style="border-top: 1px dashed #000; margin: 10px 0;">
                <div style="text-align: center; color: #d32f2f; font-weight: bold; font-size: 1.3em;">
                    MONTANT : {fac['Montant']}$
                </div>
                <center><small style="font-size: 0.6em; opacity: 0.5; margin-top:10px; display:block;">RCRP SYSTEM - DOCUMENT OFFICIEL</small></center>
            </div>
            """, unsafe_allow_html=True)

            # --- BOUTON DE PAIEMENT (Aligné avec le ticket) ---
            if st.button(f"💳 RÉGLER LA FACTURE #{fac['ID']}", key=f"pay_{fac['ID']}", use_container_width=True):
                try:
                    idx_b = df_b[df_b["Nom Roblox"] == target].index[0]
                    solde_raw = str(df_b.at[idx_b, "Solde"]).replace('$', '').replace(',', '')
                    solde_actuel = float(solde_raw)
                    montant_facture = float(fac['Montant'])
                    
                    if solde_actuel >= montant_facture:
                        df_b.at[idx_b, "Solde"] = solde_actuel - montant_facture
                        rct_idx = df_b[df_b["Nom Roblox"] == ACC_RCT].index[0]
                        solde_dest = float(str(df_b.at[rct_idx, "Solde"]).replace('$', '').replace(',', ''))
                        df_b.at[rct_idx, "Solde"] = solde_dest + montant_facture
                        df_all_f.loc[df_all_f["ID"] == fac["ID"], "Statut"] = "PAYÉ"
                        
                        cloud_conn.update(worksheet="Banque", data=df_b)
                        cloud_conn.update(worksheet="Factures", data=df_all_f)
                        
                        record_log(target, f"Paiement facture {fac['Emetteur']} #{fac['ID']}")
                        st.success("✅ Paiement effectué !")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Solde insuffisant.")
                except Exception as e:
                    st.error(f"Erreur lors du paiement : {e}")

            # --- BOUTON ANNULER (Aligné aussi) ---
            if st.session_state.user_auth in ["Staff", "Admin"]:
                if st.button(f"🗑️ ANNULER LA FACTURE #{fac['ID']}", key=f"admin_del_{fac['ID']}", use_container_width=True):
                    try:
                        df_f_sync = cloud_conn.read(worksheet="Factures")
                        row_up = df_f_sync[df_f_sync["ID"] == fac["ID"]].index[0] + 2
                        cloud_conn.update(worksheet="Factures", range=f"E{row_up}", data=[["ANNULÉ"]])
                        record_log(st.session_state.user_auth, f"Annulation #{fac['ID']}")
                        st.warning("Facture annulée.")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur d'annulation : {e}")
                    except Exception as e:
                        st.error(f"Erreur d'affichage profil : {e}")
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

# --- ONGLET 1 : IMMATRICULATION & RADIATION (AVEC OFFRE TRIO) ---
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
            
            # --- CALCULS TAXE JEUNE ---
            val_taxe_jeune = 0
            if f_owner != "---":
                try:
                    date_brute = df_b[df_b["Nom Roblox"] == f_owner]["Date d'arrivée"].values[0]
                    date_arr = datetime.strptime(str(date_brute), "%d/%m/%Y")
                    if (datetime.now() - date_arr).days < 30:
                        val_taxe_jeune = 50
                        st.warning(f"🔰 JEUNE CONDUCTEUR détecté (+{val_taxe_jeune}$)")
                except:
                    pass

            # --- CALCUL DU TOTAL + OFFRE TRIO RCT ---
            taxe_gouv = 175
            taxe_assu = 130 if "AVERIS" in f_assu else (150 if "RCT" in f_assu else 0)
            
            if "RCT" in f_assu and f_owner != "---":
                nb_vehicules = len(df_i[df_i["Nom d'utilisateur ROBLOX"] == f_owner])
                if nb_vehicules >= 2:
                    taxe_assu = 0
                    st.success(f"🎁 OFFRE TRIO : {f_owner} possède déjà {nb_vehicules} véhicules. Assurance RCT offerte !")

            total_bill = taxe_gouv + taxe_assu + val_taxe_jeune
            
            if st.button(f"S'ACQUITTER DE {total_bill}$ ET ENREGISTRER", use_container_width=True, key="btn_pay_final"):
                if f_owner != "---" and f_plate and f_code:
                    u_idx = df_b[df_b["Nom Roblox"] == f_owner].index[0]
                    u_solde = float(str(df_b.at[u_idx, "Solde"]).replace('$', '').replace(',', ''))
                    
                    if u_solde >= total_bill:
                        df_b.at[u_idx, "Solde"] = u_solde - total_bill
                        
                        if taxe_assu > 0:
                            target_acc = "Moune2010" if "AVERIS" in f_assu else ACC_RCT
                            a_idx = df_b[df_b["Nom Roblox"] == target_acc].index[0]
                            old_solde = float(str(df_b.at[a_idx, "Solde"]).replace('$', '').replace(',', ''))
                            df_b.at[a_idx, "Solde"] = old_solde + taxe_assu
                        
                        new_row = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                            "Nom d'utilisateur ROBLOX": f_owner, 
                            "Marque du véhicule": f_model, 
                            "Numéro de la plaque": f_plate, 
                            "Assurance": f_assu, 
                            "CODE": f_code
                        }])
                        
                        cloud_conn.update(worksheet="Banque", data=df_b)
                        cloud_conn.update(
                            worksheet="Copie de Immatriculations",
                            data=pd.concat([df_i, new_row], ignore_index=True)
                        )
                        
                        st.balloons()
                        st.success(f"✅ Véhicule enregistré ! Total payé : {total_bill}$")
                        st.cache_data.clear()
                        time.sleep(2)
                        st.rerun()
                    else: 
                        st.error("❌ Solde insuffisant.")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs.")

    # ===================== APERÇU À DROITE =====================
    from textwrap import dedent
    import streamlit.components.v1 as components

with col_t:
    st.write("### 🖼️ APERÇU DU TITRE (LIVE)")

    date_actuelle = datetime.now().strftime("%d/%m/%Y")
    nom_user = f_owner if f_owner != "---" else "---"
    marque_v = f_model if f_model else "---"
    plaque_v = f_plate if f_plate else "---"
    nom_assu = f_assu if f_assu != "Aucune" else "NON ASSURÉ"

    ticket_html = dedent(f"""
<div style='border: 2px dashed #555; padding: 20px; background-color: #f9f9f9; color: #333; font-family: "Courier New", Courier, monospace;'>
    
    <!-- EN-TÊTE OFFICIEL -->
    <div style='text-align:center; margin-bottom: 10px;'>
        <h2 style='margin:0; font-size:1.4em;'>TITRE DE CIRCULATION</h2>
        <small>RÉPUBLIQUE DE RENSSERLAER</small>
    </div>

    <!-- RECU OFFICIEL -->
    <div style='text-align:center; margin-bottom: 10px;'>
        <h3 style='margin:0; font-size:1.2em;'>RECU OFFICIEL</h3>
    </div>

    <!-- INFORMATIONS VEHICULE -->
    <div style='border-top: 1px dashed #ccc; border-bottom: 1px dashed #ccc; padding: 10px 0; margin: 10px 0;'>
        <p><strong>DATE :</strong> {date_actuelle}</p>
        <p><strong>UTILISATEUR :</strong> {nom_user}</p>
        <p><strong>MARQUE :</strong> {marque_v}</p>
        <p><strong>NUMÉRO DE PLAQUE :</strong>
            <span style='border:1px solid #333; padding:2px 6px; background:#eee;'>{plaque_v}</span>
        </p>
        <p><strong>ASSURANCE :</strong> {nom_assu}</p>
    </div>

    <!-- FRAIS -->
    <div>
        <p style='display:flex; justify-content:space-between; margin:2px 0;'>
            <span>Frais d'immatriculation :</span><span>175$</span>
        </p>
        <p style='display:flex; justify-content:space-between; margin:2px 0;'>
            <span>Frais d'assurance :</span><span>{taxe_assu}$</span>
        </p>
        <p style='display:flex; justify-content:space-between; margin:2px 0;'>
            <span>Supplément jeune conducteur :</span><span>{val_taxe_jeune}$</span>
        </p>
    </div>

    <!-- TOTAL -->
    <div style='border-top:2px solid #333; padding-top:10px; text-align:right;'>
        <strong style='font-size:1.3em;'>TOTAL PAYÉ : {total_bill}$</strong>
    </div>

    <!-- PIED DE PAGE OFFICIEL -->
    <div style='text-align:center; margin-top:15px;'>
        <small>CERTIFIÉ CONFORME<br>Par le Terminal National.</small>
    </div>
    
</div>
""")

    components.html(ticket_html, height=500)

# --- ONGLET 2 : SERVICES AGENT (FACTURES / POINTS / CONSULTATION) ---
if st.session_state.user_auth in ["RCT", "Staff"]:
    with tabs[1]:
        if target == "---":
            st.warning("⚠️ Sélectionnez un citoyen en haut de la page.")
        else:
            # 3 colonnes : Saisie | Facture (Milieu) | Véhicules (Droite)
            col_saisie, col_facture, col_vehicules = st.columns([1, 1.2, 0.8])

            with col_saisie:
                with st.container(border=True):
                    st.markdown("#### 📝 Saisie")
                    f_val = st.number_input("Montant ($)", min_value=0, step=50, key="v_val_final")
                    
                    is_rct = (st.session_state.user_auth == "RCT")
                    f_pts = st.number_input(
                        "Points à retirer", 
                        min_value=0, max_value=12, step=1, 
                        key="v_pts_final", 
                        disabled=is_rct
                    )
                    
                    f_motif = st.text_input("Motif", key="v_mot_final")
                    
                    # Récupération des données véhicules pour la cible
                    target_veh = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
                    v_list = ["AUCUN / PIÉTON"] + target_veh["Numéro de la plaque"].tolist()
                    f_plate = st.selectbox("Véhicule concerné", v_list, key="v_plate_final")
                    
                    st.write("---")
                    label = "🚨 ENVOYER & DÉBITER" if not is_rct else "🚨 ENVOYER FACTURE"
                    
                    if st.button(label, use_container_width=True, type="primary"):
                        if not f_motif:
                            st.error("Motif obligatoire.")
                        else:
                            # Logique d'envoi (Points + Facture)
                            if f_pts > 0 and not is_rct:
                                idx_p = df_p[df_p["Nom Roblox"] == target].index[0]
                                df_p.at[idx_p, "PTS"] = max(0, int(df_p.at[idx_p, "PTS"]) - f_pts)
                                cloud_conn.update(worksheet="Points Permis", data=df_p)
                            
                            df_f = cloud_conn.read(worksheet="Factures")
                            new_row = {
                                "ID": random.randint(1000, 9999),
                                "Cible": target,
                                "Emetteur": st.session_state.user_auth,
                                "Montant": f_val,
                                "Motif": f"{f_motif} [{f_plate}]",
                                "Statut": "EN ATTENTE"
                                "Date_Limite": (datetime.now() + timedelta(hours=24)).sftrtime("%d/%m/%Y %H:%M:%S")
                            }
                            df_f = pd.concat([df_f, pd.DataFrame([new_row])], ignore_index=True)
                            cloud_conn.update(worksheet="Factures", data=df_f)
                            st.success("✅ Envoyé !")
                            st.cache_data.clear()
                            st.rerun()

            with col_facture:
                st.markdown("#### 📄 Aperçu")
                st.markdown(f"""
                <div style="border: 2px solid black; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; line-height: 1.2;">
                    <center><b>FACTURE</b><br><small>RÉPUBLIQUE DE RENSSERLAER</small></center>
                    <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                    <b>DATE   :</b> {datetime.now().strftime('%d/%m/%Y')}<br>
                    <b>NOM    :</b> {target}<br>
                    <b>MOTIF  :</b> {f_motif.upper() if f_motif else '...'}<br>
                    <b>PLAQUE :</b> <span style="border: 1px solid black; padding: 0 3px;">{f_plate}</span><br>
                    <b>MONTANT:</b> {f_val}$
                    <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                    <div style="text-align: center; color: black; font-weight: bold; font-size: 0.8em;">
                        POINTS À DÉBITER : -{f_pts}<br>
                        <small>Par le Terminal National</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_vehicules:
                st.markdown("#### 🚗 Véhicules")
                if not target_veh.empty:
                    for _, veh in target_veh.iterrows():
                        # Logique des couleurs d'assurance
                        assurance = str(veh['Assurance'])
                        if assurance == "Averis":
                            color, status_txt, icon = "green", "VÉHICULE EN ORDRE", "✅"
                        elif assurance == "RCT":
                            color, status_txt, icon = "green", "ASSURÉ RCT", "🛡️"
                        else:
                            color, status_txt, icon = "#d32f2f", "🚨 NON-ASSURÉ RCT", "⚠️"

                        st.markdown(f"""
                        <div style="border: 2px solid black; padding: 10px; background: white; color: black; font-family: 'Courier New', monospace; line-height: 1.1; margin-bottom: 10px; font-size: 0.8em;">
                            <center><b>TITRE DE CIRCULATION</b></center>
                            <hr style="border-top: 1px solid #ccc; margin: 5px 0;">
                            <b>NOM :</b> {target}<br>
                            <b>MODÈLE :</b> {veh['Marque du véhicule']}<br>
                            <b>PLAQUE :</b> <span style="border: 1px solid black; padding: 0 2px;">{veh['Numéro de la plaque']}</span><br>
                            <b>ASSUR. :</b> {assurance}
                            <hr style="border-top: 1px solid #ccc; margin: 5px 0;">
                            <div style="text-align: center; color: {color}; font-weight: bold;">
                                {icon} {status_txt}<br>
                                <small style="color: gray; font-size: 0.7em;">Terminal National</small>
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
