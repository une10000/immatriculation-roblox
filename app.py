import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime, timedelta, timezone
from streamlit_gsheets import GSheetsConnection

# 1. INTERFACE & DESIGN
st.set_page_config(
    page_title="RCRP FR OS - SYSTÈME NATIONAL",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS DYNAMIQUE (DÉTECTION SYSTÈME) ---
st.markdown("""
    <style>
    /* Nettoyage des éléments Streamlit */
    #MainMenu, footer, header { visibility: hidden; }

    /* PAR DÉFAUT : MODE SOMBRE */
    :root {
        --bg-color: #0e1117;
        --text-color: #ffffff;
        --input-bg: #262730;
        --border-color: #444444;
    }

    /* SI L'APPAREIL EST EN MODE CLAIR */
    @media (prefers-color-scheme: light) {
        :root {
            --bg-color: #ffffff !important;
            --text-color: #000000 !important;
            --input-bg: #f0f2f6 !important;
            --border-color: #d3d3d3 !important;
        }
        /* Correction spécifique pour le fond Streamlit */
        .stApp { background-color: #ffffff !important; }
        .stMarkdown, p, label, span, div, h1, h2, h3 { color: #000000 !important; }
    }

    /* Application globale */
    .stApp { background-color: var(--bg-color); }

    /* Style des champs de saisie */
    input, .stSelectbox>div>div, textarea {
        background-color: var(--input-bg) !important;
        color: var(--text-color) !important;
        border: 2px solid var(--border-color) !important;
    }

    /* Style des boutons */
    .stButton>button {
        background-color: var(--input-bg) !important;
        color: var(--text-color) !important;
        border: 2px solid var(--border-color) !important;
        font-weight: 900 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ======================================================================================
# 2. MOTEUR DE DONNÉES (SYNC)
# ======================================================================================
cloud_conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def fetch_database():
    try:
        df_bank = cloud_conn.read(worksheet="Banque", ttl=20).dropna(how='all').fillna("")
        df_immat = cloud_conn.read(worksheet="Copie de Immatriculations", ttl=20).dropna(how='all').fillna("")
        df_pts = cloud_conn.read(worksheet="Points Permis", ttl=20).dropna(how='all').fillna("")
        df_apb = cloud_conn.read(worksheet="Signalements_APB")
        return df_bank, df_immat, df_pts, df_apb
    except Exception as e:
        st.error(f"Erreur de liaison : {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_b, df_i, df_p, df_a = fetch_database()

# ======================================================================================
# 3. ÉTAT DE LA SESSION & PARAMÈTRES
# ======================================================================================
if "user_auth" not in st.session_state: st.session_state.user_auth = None
if "audit_logs" not in st.session_state: st.session_state.audit_logs = []

# ======================================================================================
# CONFIGURATION ET FONCTIONS TECHNIQUES
# ======================================================================================

PRIME_JOB = {
    "Sans-Emploi": 0,
    "Agent RCT": 2000,
    "Averis": 2000,
    "Pompiers": 2000,
    "Police": 3000,
    "Staff": 4000,
    "Service Public": 1000,
    "Entreprise Privée": 500
}

def traiter_paiement_prime(target_name, metier, montant, df_b, cloud_conn):
    source_compte = None
    
    # Seuls ces métiers prélèvent de l'argent sur un compte spécifique
    if metier == "Averis":
        source_compte = "Moune2010"
    elif metier == "Agent RCT":
        source_compte = "une10000"
    
    try:
        # Si une source est définie, on prélève
        if source_compte:
            idx_source = df_b[df_b["Nom Roblox"] == source_compte].index[0]
            df_b.at[idx_source, "Solde"] -= montant
            msg = f"✅ Prime de {montant}$ versée (Payé par {source_compte})"
        else:
            # Sinon, création monétaire (Pompiers, Police, Staff, etc.)
            msg = f"✅ Prime de {montant}$ versée (Budget État - Création)"
        
        # Ajout du montant à la cible
        idx_target = df_b[df_b["Nom Roblox"] == target_name].index[0]
        df_b.at[idx_target, "Solde"] += montant
        
        cloud_conn.update(worksheet="Banque", data=df_b)
        return True, msg
        
    except Exception as e:
        return False, f"❌ Erreur lors du traitement : {e}"

# Codes de Service
KEY_RCT = "RCT-26-RCRPFR"
KEY_STAFF = "RCRPFR-25-26"
KEY_ENTREPRISES = "RCRPFR-2026-ENTRE-"

def record_log(user, action):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.audit_logs.append(f"[{now}] {user} : {action}")

# ======================================================================================
# 4. SIDEBAR CONDITIONNELLE (LOGO & INFOS)
# ======================================================================================

if st.session_state.user_auth is not None:
    with st.sidebar:
        st.image("https://image2url.com/r2/default/images/1775257035403-38cdfea2-f4f7-4ac5-b45b-9a9a8073babf.png", use_container_width=True)
        st.divider()
        import streamlit.components.v1 as components

        t_now = datetime.now(timezone.utc) + timedelta(hours=1)
        jours = {"Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi", "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche"}
        mois = {"January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril", "May": "Mai", "June": "Juin", "July": "Juillet", "August": "Août", "September": "Septembre", "October": "Octobre", "November": "Novembre", "December": "Décembre"}

        st.markdown(f"""
            <div style="text-align: left; line-height: 1.1; margin-left: 0; padding-left: 0;">
                <span style="font-size: 1.5em;">📅</span><br>
                <b style="font-size: 1.2em;">{jours[t_now.strftime('%A')]},</b><br>
                <span style="font-size: 1.1em;">{t_now.strftime('%d')} {mois[t_now.strftime('%B')]} {t_now.strftime('%Y')}</span>
            </div>
        """, unsafe_allow_html=True)

        st.write("") 
        st.markdown("<div style='text-align: left; font-size: 1.5em; margin-bottom: 0; margin-left: 0;'>⏰</div>", unsafe_allow_html=True)
        
        components.html(f"""
            <div id="clock" style="font-family: 'Source Sans Pro', sans-serif; font-size: 24px; font-weight: bold; text-align: left; color: #31333F; margin-left: -8px; margin-top: -5px;"></div>
            <script>
                function updateClock() {{
                    const now = new Date();
                    const options = {{ timeZone: 'Europe/Paris', hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }};
                    document.getElementById('clock').textContent = now.toLocaleTimeString('fr-FR', options);
                }}
                setInterval(updateClock, 1000); updateClock();
            </script>
        """, height=40)
        st.divider()

        st.write(f"🔐 Accréditation : **{st.session_state.user_auth}**")

        if st.button("🔄 FORCER SYNCHRO", use_container_width=True):
            st.cache_data.clear()
            record_log(st.session_state.user_auth, "Synchro Cloud Manuelle")
            st.rerun()

        if st.button("🚪 DÉCONNEXION", use_container_width=True):
            record_log(st.session_state.user_auth, "Déconnexion")
            st.cache_data.clear()
            for key in list(st.session_state.keys()): del st.session_state[key]
            components.html("<script>window.parent.location.reload();</script>", height=0)
            st.stop()
            
        st.divider()
        st.caption("📜 JOURNAUX D'AUDIT (SESSION)")
        if "audit_logs" in st.session_state:
            for log in reversed(st.session_state.audit_logs[-8:]):
                st.caption(log)

# ======================================================================================
# 5. LOCKSCREEN (CONNEXION)
# ======================================================================================
if st.session_state.user_auth is None:
    # Si MESSAGE_ACCUEIL est vide, le bandeau rouge disparaît et la hauteur s'adapte
    MESSAGE_ACCUEIL = "" 

    st.markdown("""
        <style>
            [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none; }
            [data-testid="stStatusWidget"] { display: none; }
            .block-container { padding-top: 2rem !important; }
            iframe { border: none !important; background: transparent !important; }
        </style>
    """, unsafe_allow_html=True)

    # Gestion de l'heure UTC+2 et du design dynamique
    from datetime import datetime, timezone, timedelta
    t_now_lock = datetime.now(timezone.utc) + timedelta(hours=2)
    h_lock = t_now_lock.hour

    if 5 <= h_lock < 18:
        salut_complet, t_color = "Bonjour☀️", "#1E1E1E"
        pattern_style = "background-color: #87CEEB; background-image: radial-gradient(circle at 85% 10%, #FFF9E3 0%, #FFD700 15%, rgba(255,215,0,0.4) 30%, transparent 60%);"
        glow_text = "0 0 30px rgba(255, 255, 255, 1), 0 0 60px rgba(255, 200, 0, 0.6)"
    else:
        salut_complet, t_color = "Bonsoir🌕", "#FFFFFF"
        pattern_style = "background-color: #05070a; background-image: radial-gradient(1px 1px at 25% 35%, white, transparent), radial-gradient(1px 1px at 50% 10%, white, transparent);"
        glow_text = "0 0 40px rgba(255,255,255,0.9), 0 0 80px rgba(255,255,255,0.4)"

    import streamlit.components.v1 as components
    
    # --- LOGIQUE DE HAUTEUR DYNAMIQUE ---
    display_annonce = "block" if MESSAGE_ACCUEIL else "none"
    # 650px est le réglage idéal pour ne rien couper sans laisser de blanc
    hauteur_composant = 820 if MESSAGE_ACCUEIL else 650

    components.html(f"""
        <style>
            :root {{ --bg-box: #f0f2f6; --text-main: #31333F; --text-muted: #555555; }}
            @media (prefers-color-scheme: dark) {{ :root {{ --bg-box: #1a1c23; --text-main: #ffffff; --text-muted: rgba(255,255,255,0.6); }} }}
            @keyframes border-glow {{
                0% {{ border-color: #ff0000; box-shadow: 0 0 25px #ff0000; }}
                50% {{ border-color: #00ff00; box-shadow: 0 0 25px #00ff00; }}
                100% {{ border-color: #ff0000; box-shadow: 0 0 25px #ff0000; }}
            }}
            .container-annonce {{ 
                display: {display_annonce}; 
                background-color: var(--bg-box); 
                color: var(--text-main); 
                padding: 40px 20px; 
                text-align: center; 
                border-top: 6px solid #ff0000; 
                border-bottom: 6px solid #ff0000; 
                animation: border-glow 1.5s linear infinite; 
            }}
            .footer-box {{ 
                background-color: var(--bg-box); 
                color: var(--text-main); 
                border-left: 10px solid #ff4b4b; 
                padding: 45px 20px; 
                text-align: center;
                margin-bottom: 10px;
            }}
        </style>

        <div style="font-family: 'Helvetica Neue', Arial; width: 100%; border-radius: 25px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
            <div style="text-align: center; padding: 70px 20px; color: {t_color}; {pattern_style}">
                <h1 style="font-size: 5.5em; margin: 0; font-weight: 900; text-shadow: {glow_text};">{salut_complet}</h1>
                <p style="letter-spacing: 5px; font-weight: bold; text-transform: uppercase;">Unité Fédérale de Rensselaer</p>
                <div id="clock" style="font-size: 3.8em; font-weight: bold; border-top: 2px solid {t_color}33;">00:00:00</div>
            </div>
            
            <div class="container-annonce">
                <div style="text-transform: uppercase; letter-spacing: 3px; font-size: 0.9em;">📢 Bulletin d'Information</div>
                <div style="font-size: 35px; font-weight: bold;">{MESSAGE_ACCUEIL}</div>
            </div>

            <div class="footer-box">
                <h2 style="font-size: 2.2em;">🏛️ RÉPUBLIQUE DE RENSSELAER</h2>
                <small style="opacity: 0.5;">VERSION 14.6.0 | SÉCURISÉ PAR PROTOCOLE RCRP-OS</small>
            </div>
        </div>

        <script>
            function update() {{
                const now = new Date();
                document.getElementById('clock').textContent = String(now.getHours()).padStart(2, '0') + ":" + String(now.getMinutes()).padStart(2, '0') + ":" + String(now.getSeconds()).padStart(2, '0');
            }}
            setInterval(update, 1000); update();
        </script>
    """, height=hauteur_composant)

    st.warning("⚠️ **AVERTISSEMENT :** Toute action effectuée sur ce terminal est enregistrée.")
    st.write("---")

    # 3. COLONNES D'ACCÈS
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("### 👥 CIVIL")
        st.text_input("Ecrivez quelque chose (Optionnel)", placeholder="Ex: Liberté...", key="input_civil_align")
        if st.button("ACCÉDER AU TERMINAL", key="l_civ_f", use_container_width=True):
            st.session_state.user_auth = "Civil"
            st.rerun()

    with c2:
        st.markdown("### 🏢 ENTREPRISE")
        login_entre = st.text_input("Code Entreprise", placeholder="Code RCRPFR...", type="password", key="l_entre_f")
        if st.button("ACCÈS ENTREPRISE", key="b_entre_f", use_container_width=True):
            if login_entre == KEY_ENTREPRISES:
                st.session_state.user_auth = "Entreprise"
                st.rerun()
            else: st.error("Code erroné.")

    with c3:
        st.markdown("### 👨‍🔧 AGENT RCT")
        login_rct = st.text_input("Identifiant Agent", placeholder="Code RCT", type="password", key="l_rct_ff")
        if st.button("AUTHENTIFICATION RCT", key="b_rct_f", use_container_width=True):
            if login_rct == KEY_RCT:
                st.session_state.user_auth = "RCT"
                st.rerun()
            else: st.error("Clé invalide.")

    with c4:
        st.markdown("### 🛡️👮‍♂️ POLSTA")
        login_staff = st.text_input("Clé Maîtresse", placeholder="Code STAFF", type="password", key="l_st_ff")
        if st.button("ACCÈS ADMINISTRATEUR", key="b_st_f", use_container_width=True):
            if login_staff == KEY_STAFF:
                st.session_state.user_auth = "Staff"
                st.rerun()
            else: st.error("Accès refusé.")

    st.stop()
# ======================================================================================
# LE RESTE DU CODE (S'affiche uniquement après connexion)
# ======================================================================================
# ======================================================================================
# 6. MODULE : DOSSIER CITOYEN UNIFIÉ (VERSION CORRIGÉE)
# ======================================================================================

# --- PRÉ-VÉRIFICATION : Y a-t-il au moins un avis de recherche ? ---
# 1. Check Citoyens
has_crim = not df_b[df_b["Statut"].str.upper().str.contains("RECHERCHÉ", na=False)].empty

# 2. Check Véhicules immatriculés
has_veh = False
if 'Statut' in df_i.columns:
    has_veh = not df_i[df_i["Statut"].str.upper().str.contains("RECHERCHÉ", na=False)].empty

# 3. Check APB (df_a) - On vérifie que le motif n'est pas vide
has_apb = False
if not df_a.empty:
    # On regarde si au moins une ligne possède un motif réel
    has_apb = any(str(m).strip() != "" for m in df_a["Motif"].tolist())

# ON N'AFFICHE LE CONTAINER QUE SI UN DES TROIS EST VRAI
if has_crim or has_veh or has_apb:
    with st.container():
        # --- A. TABLEAU PUBLIC DES AVIS DE RECHERCHE ---
        st.markdown("<h3 style='color: #ff4b4b; margin-bottom: 15px;'>🚨 AVIS DE RECHERCHE EN COURS</h3>", unsafe_allow_html=True)
        
        # 1. CITOYENS (df_b)
        recherches_publics = df_b[df_b["Statut"].str.upper().str.contains("RECHERCHÉ", na=False)]
        for _, crim in recherches_publics.iterrows():
            motif = crim.get('Motif Recherche', 'Motif non spécifié').upper()
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; background-color: #8B0000; padding: 12px 20px; border-radius: 8px; border: 3px solid #ff0000; margin-bottom: 10px; animation: blinker_citoyen 2s linear infinite;">
                    <div style="color: #ffffff !important; font-weight: bold; font-size: 1.3em;">👤 {crim['Nom Roblox']}</div>
                    <div style="color: #ffcccc !important; font-weight: 700; font-size: 0.9em;">MOTIF : {motif}</div>
                </div>
                <style> @keyframes blinker_citoyen {{ 50% {{ background-color: #ff4b4b; border-color: #8B0000; }} }} </style>
            """, unsafe_allow_html=True)

        # 2. VÉHICULES IMMATRICULÉS (df_i)
        if 'Statut' in df_i.columns:
            recherches_veh = df_i[df_i["Statut"].str.upper().str.contains("RECHERCHÉ", na=False)]
            for _, veh in recherches_veh.iterrows():
                st.markdown(f"""
                    <div style="display: flex; flex-direction: column; background-color: #b8860b; padding: 12px 20px; border-radius: 8px; border: 3px solid #ffd700; margin-bottom: 10px; animation: blinker_veh 2s linear infinite;">
                        <div style="color: #ffffff !important; font-weight: bold; font-size: 1.3em;">🚘 PLAQUE : {veh.get('Numéro de la plaque', 'INCONNUE')} | {veh.get('Marque du véhicule', 'INCONNU')}</div>
                        <div style="color: #fffacd !important; font-weight: 700; font-size: 0.9em;">MOTIF : {veh.get('Motif Recherche', 'Non spécifié').upper()}</div>
                    </div>
                    <style> @keyframes blinker_veh {{ 50% {{ background-color: #daa520; border-color: #b8860b; }} }} </style>
                """, unsafe_allow_html=True)
        # 3. VÉHICULES NON IMMATRICULÉS (APB - df_a) - VERSION ROUGE ALERTE
        if has_apb:
            for idx, apb in df_a.iterrows():
                if str(apb.get('Motif', '')).strip() != "":
                    st.markdown(f"""
                    <div style="display: flex; flex-direction: column; background-color: #B22222; padding: 12px 20px; border-radius: 8px; border: 3px solid #FF0000; margin-bottom: 10px; animation: blinker_apb 2s linear infinite;">
                    <div style="color: #ffffff !important; font-weight: bold; font-size: 1.3em;">🚨 APB (SANS PLAQUE) : {apb.get('Description', 'Véhicule suspect')}</div>
                    <div style="color: #ffcccc !important; font-weight: 700; font-size: 0.9em;">MOTIF : {apb.get('Motif', 'Non spécifié').upper()} | DATE : {apb.get('Date', '')}</div>
                    </div>
                    <style> @keyframes blinker_apb {{ 50% {{ background-color: #FF4500; border-color: #B22222; }} }} </style>
                    """, unsafe_allow_html=True)
# TITRE DU REGISTRE
st.markdown('<div class="header-box"><h2>📂 REGISTRE NATIONAL DES CITOYENS</h2></div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="info-card"><b>GUIDE :</b> Sélectionnez un citoyen pour extraire son dossier ou recherchez une plaque (Coût: 10$).</div>', unsafe_allow_html=True)
    
    search_list = ["---"] + sorted(df_b["Nom Roblox"].unique().tolist())
    target = st.selectbox("Sélectionner un citoyen :", search_list, key="main_selector")
    
    if target != "---":
        # --- RÉCUPÉRATION DES DONNÉES GLOBALES ---
        citoyen_info = df_b[df_b["Nom Roblox"] == target]
        
# --- B. ALERTES AUTOMATIQUES ---
        # 1. Alerte Mandat (Rouge Flashy)
        if not citoyen_info.empty and "RECHERCHÉ" in str(citoyen_info.iloc[0].get("Statut", "")).upper():
            motif_critique = citoyen_info.iloc[0].get("Motif Recherche", "Non spécifié")
            st.markdown(f"""
                <style>
                @keyframes blink {{
                    0% {{ opacity: 1; border-color: #ff0000; box-shadow: 0 0 10px #ff0000; }}
                    50% {{ opacity: 0.7; border-color: #ffffff; box-shadow: 0 0 30px #ff0000; }}
                    100% {{ opacity: 1; border-color: #ff0000; box-shadow: 0 0 10px #ff0000; }}
                }}
                .critical-alert {{
                    background-color: #900000;
                    padding: 30px;
                    border-radius: 15px;
                    border: 8px solid #ff0000;
                    color: white;
                    text-align: center;
                    margin-bottom: 20px;
                    animation: blink 1s infinite;
                    font-family: 'Arial Black', sans-serif;
                }}
                </style>
                <div class="critical-alert">
                    <h1 style="margin:0; font-size: 40px; color: white; text-shadow: 2px 2px #000000;">🚨 ALERTE INTERPOL : RECHERCHÉ 🚨</h1>
                    <p style="font-size: 25px; margin-top: 10px;">L'individu <b>{target.upper()}</b> est sous mandat d'arrêt immédiat !</p>
                    <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; margin-top: 10px;">
                        <b style="font-size: 20px;">MOTIF : {motif_critique}</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)
# 2. Alerte Permis Invalide (PKW / LKW)
        try:
            row_p = df_p[df_p["Nom Roblox"] == target].iloc[0]
            pts_pkw = float(row_p.get("PTS PKW", 25))
            pts_lkw = float(row_p.get("PTS LKW", 25))
            
            permis_revoques = []
            if pts_pkw <= 0:
                permis_revoques.append("PKW")
            if pts_lkw <= 0:
                permis_revoques.append("LKW")
                
            if permis_revoques:
                type_permis_str = " & ".join(permis_revoques)
                st.markdown(f"""
                    <div style="background-color: #ff9800; padding: 20px; border-radius: 10px; border: 4px solid #fb8c00; color: black; text-align: center; margin-bottom: 10px;">
                        <h2 style="margin:0;">⚠️ PERMIS RÉVOQUÉ ({type_permis_str}) ⚠️</h2>
                        <p style="font-size: 18px;">L'individu <b>{target}</b> a perdu tous ses points sur le permis <b>{type_permis_str}</b>.</p>
                    </div>
                """, unsafe_allow_html=True)
        except: pass

        # 2. Alerte Dette en retard (Orange)
        maintenant = datetime.now()
        try:
            df_f_check = cloud_conn.read(worksheet="Factures", ttl=20).fillna("")
            dettes = df_f_check[(df_f_check["Cible"] == target) & (df_f_check["Statut"] == "EN ATTENTE")]
            has_delay = False
            for _, r_f in dettes.iterrows():
                try:
                    limite = datetime.strptime(str(r_f['Date_Limite']), "%d/%m/%Y %H:%M:%S")
                    if maintenant > limite:
                        has_delay = True
                        break
                except: pass
            
            if has_delay:
                st.markdown('<div style="background-color: #E67E22; padding: 10px; border-radius: 8px; text-align: center; color: white; margin-bottom: 20px;">⚠️ ATTENTION : FACTURE(S) EN RETARD</div>', unsafe_allow_html=True)
        except: pass

        # --- C. RECHERCHE PAR PLAQUE (PAYANTE 10$) ---
        with st.expander("🔍 RECHERCHE D'IDENTITÉ PAR PLAQUE (Coût : 10$)", expanded=False):
            st.warning(f"Les 10$ seront prélevés sur le compte de : **{target}**.")
            c1, c2 = st.columns([3, 1])
            with c1:
                search_plate = st.text_input("Saisir une plaque", key="p_search", label_visibility="collapsed").upper()
            with c2:
                if st.button("Lancer", key="btn_p_search", use_container_width=True, type="primary"):
                    if search_plate:
                        idx_p = df_b[df_b["Nom Roblox"] == target].index[0]
                        solde_p = float(str(df_b.at[idx_p, "Solde"]).replace('$','').replace(',',''))
                        if solde_p >= 10:
                            res = df_i[df_i["Numéro de la plaque"] == search_plate]
                            if not res.empty:
                                owner = res.iloc[0]["Nom d'utilisateur ROBLOX"]
                                v_model = res.iloc[0]["Marque du véhicule"]
                                df_b.at[idx_p, "Solde"] = solde_p - 10
                                cloud_conn.update(worksheet="Banque", data=df_b)
                                st.success(f"🔍 Résultat : {search_plate} -> {owner} ({v_model})")
                                st.cache_data.clear() # Rafraîchir le solde
                            else: st.error("Plaque introuvable.")
                        else: st.error("Solde insuffisant.")
                    else: st.warning("Veuillez saisir une plaque.")

        st.markdown("---")
        # --- D. DOSSIER DÉTAILLÉ (3 COLONNES) ---
        col1, col2, col3 = st.columns(3)
# ---------------- COLONNE 1 : POINTS & PERMIS ----------------
        with col1:
            st.markdown("### 🪪 Permis de conduire")
            p_data = df_p[df_p["Nom Roblox"] == target]
            
            if not p_data.empty:
                row_p = p_data.iloc[0]
                
                # Récupération sécurisée des points PKW (défaut 25) et LKW (défaut 0)
                v_pkw = row_p.get("PTS PKW", 25)
                pts_pkw = int(v_pkw) if str(v_pkw).isdigit() else 25

                v_lkw = row_p.get("PTS LKW", 0)
                pts_lkw = int(v_lkw) if str(v_lkw).isdigit() else 0
                
                roles_autorises = ["Staff", "Admin", "Entreprise", "Police"]
                
                with st.container(border=True):
                    # --- NUMÉRO DE SÉRIE SÉCURISÉ ---
                    st.markdown("""
                        <div style="text-align: right; font-size: 10px; color: #b0b0b0; font-family: monospace; margin-bottom: -5px;">
                            🔒 DOC-ID: RCRP-P-8392<br>
                            <span style="letter-spacing: 2px;">||| | || || | ||| ||</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c_pkw, c_lkw = st.columns(2)
                    
                    # --- SECTION PKW ---
                    with c_pkw:
                        st.markdown("##### 🚗 Cat. PKW")
                        st.metric("Points actuels", f"{pts_pkw}/25")
                        
                        if pts_pkw > 0:
                            st.markdown("<div style='background-color: #d4edda; color: #155724; padding: 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 14px; border: 1px solid #c3e6cb;'>✅ VALIDE</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='background-color: #f8d7da; color: #721c24; padding: 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 14px; border: 1px solid #f5c6cb;'>❌ SUSPENDU</div>", unsafe_allow_html=True)
                        
                        if st.session_state.user_auth in roles_autorises and pts_pkw <= 0:
                            st.write("")
                            if st.button("🔓 Rendre PKW", key=f"res_pkw_{target}", use_container_width=True):
                                df_p.loc[df_p["Nom Roblox"] == target, "PTS PKW"] = 25
                                
                                # Nettoyage avant envoi
                                df_clean = df_p.astype(str)
                                cloud_conn.update(worksheet="Points Permis", data=df_clean)
                                
                                st.success("Permis PKW rendu !")
                                time.sleep(1)
                                st.rerun()

                    # --- SECTION LKW ---
                    with c_lkw:
                        st.markdown("##### 🚚 Cat. LKW")
                        st.metric("Points actuels", f"{pts_lkw}/25")
                        
                        if pts_lkw > 0:
                            st.markdown("<div style='background-color: #d4edda; color: #155724; padding: 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 14px; border: 1px solid #c3e6cb;'>✅ VALIDE</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='background-color: #fff3cd; color: #856404; padding: 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 14px; border: 1px solid #ffeeba;'>⚠️ NON ACQUIS</div>", unsafe_allow_html=True)
                        
                        if st.session_state.user_auth in roles_autorises and pts_lkw <= 0:
                            st.write("")
                            if st.button("🔓 Accorder LKW", key=f"res_lkw_{target}", use_container_width=True):
                                df_p.loc[df_p["Nom Roblox"] == target, "PTS LKW"] = 25
                                
                                # Nettoyage avant envoi
                                df_clean = df_p.astype(str)
                                cloud_conn.update(worksheet="Points Permis", data=df_clean)
                                
                                st.success("Permis LKW accordé !")
                                time.sleep(1)
                                st.rerun()
            else: 
                st.info("📭 Aucun permis trouvé.")
        # ---------------- COLONNE 2 : BANQUE & PAIE ----------------
        with col2:
            st.markdown("### 🏦 Dossier Bancaire")
            if not citoyen_info.empty:
                with st.container(border=True):
                    # --- NUMÉRO DE SÉRIE SÉCURISÉ ---
                    st.markdown("""
                        <div style="text-align: right; font-size: 10px; color: #b0b0b0; font-family: monospace; margin-bottom: -5px;">
                            🔒 SEC-KEY: BQ-2026-FR<br>
                            <span style="letter-spacing: 2px;">|| ||| | || | ||| ||</span>
                        </div>
                    """, unsafe_allow_html=True)

                    # Affichage principal
                    st.metric("SOLDE DISPONIBLE", f"{citoyen_info.iloc[0]['Solde']}$")
                    job_raw = str(citoyen_info.iloc[0]['Emploiement'])
                    st.markdown(f"🏢 **Métier(s) :** {job_raw}")
                    st.write("")

                    # --- CALCULATEUR DE PAIE ---
                    with st.expander("💳 Détails de la prochaine paie", expanded=False):
                        m_pol, m_rct = 0, 0
                        
                        try:
                            df_admin_clock = cloud_conn.read(worksheet="Clock", ttl=5).fillna("")
                            df_paie_clean = df_admin_clock.copy()
                            df_paie_clean.columns = df_paie_clean.columns.str.strip().str.lower()
                            
                            logs = df_paie_clean[
                                (df_paie_clean["nom"].str.strip() == target.strip()) & 
                                (df_paie_clean["statut"].str.contains("Valid", case=False, na=False))
                            ]
                            
                            for _, r in logs.iterrows():
                                t_debut = pd.to_datetime(r["début"], dayfirst=True, errors='coerce')
                                t_fin = pd.to_datetime(r["fin"], dayfirst=True, errors='coerce')
                                
                                if pd.notnull(t_debut) and pd.notnull(t_fin):
                                    diff = (t_fin - t_debut).total_seconds() / 60
                                    if diff > 0:
                                        job_str = str(r["job"]).upper()
                                        if "POL" in job_str: m_pol += diff
                                        elif "RCT" in job_str: m_rct += diff
                        except Exception as e:
                            st.error(f"Erreur calcul : {e}")

                        # Calcul des Primes et Taxes
                        ratio_pol = min(m_pol/1200, 1.0)
                        ratio_rct = min(m_rct/1200, 1.0)
                        
                        p_pol = int(3000 * ratio_pol) if "police" in job_raw.lower() else 0
                        p_rct = int(2000 * ratio_rct) if "agent rct" in job_raw.lower() else 0
                        p_staff = 4000 if "staff" in job_raw.lower() else 0
                        p_averis = 2000 if "averis" in job_raw.lower() else 0
                        p_sp = 1000 if "service public" in job_raw.lower() else 0
                        
                        mes_v = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
                        count_rct = len(mes_v[mes_v["Assurance"].str.contains("RCT", na=False, case=False)])
                        is_trio = count_rct >= 3
                        taxe_v = 200 if is_trio else (len(mes_v) * 150)

                        net = 15000 + p_pol + p_rct + p_staff + p_averis + p_sp - taxe_v

                        # Affichage Visuel
                        c_cred, c_deb = st.columns(2)
                        with c_cred:
                            st.markdown("<div style='color: #4CAF50; font-weight:bold; margin-bottom:5px;'>📥 REVENUS</div>", unsafe_allow_html=True)
                            st.markdown(f"➕ **Base** : `15,000$`")
                            if p_staff > 0: st.markdown(f"⭐ **Staff** : `{p_staff}$`")
                            if p_averis > 0: st.markdown(f"🛡️ **Averis** : `{p_averis}$`")
                            if p_sp > 0: st.markdown(f"👷 **Service P.** : `{p_sp}$`")
                            
                            if "police" in job_raw.lower():
                                st.markdown(f"👮 **Police** : `{p_pol}$`")
                                st.progress(ratio_pol, text=f"{int(m_pol/60)}h{int(m_pol%60):02d} / 15h")
                            if "agent rct" in job_raw.lower():
                                st.markdown(f"👷‍♂️ **RCT** : `{p_rct}$`")
                                st.progress(ratio_rct, text=f"{int(m_rct/60)}h{int(m_rct%60):02d} / 15h")

                        with c_deb:
                            st.markdown("<div style='color: #E53935; font-weight:bold; margin-bottom:5px;'>📤 DÉPENSES</div>", unsafe_allow_html=True)
                            st.markdown(f"🚗 **Assurances** : `{taxe_v}$`")
                            st.caption("Offre Trio RCT ✅" if is_trio else f"{len(mes_v)} véhicule(s)")

                        st.divider()
                        st.markdown(f"""
                            <div style="background-color: rgba(76, 175, 80, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(76, 175, 80, 0.3); border-left: 5px solid #4CAF50; display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 1.1em; font-weight: 500;">NET ESTIMÉ</span>
                                <span style="font-size: 1.5em; font-weight: bold; color: #4CAF50;">{int(net):,}$</span>
                            </div>
                        """, unsafe_allow_html=True)

                    # --- MODIFICATION MÉTIER ---
                    if st.session_state.user_auth in ["Staff", "Admin"]:
                        st.write("")
                        if st.button("✏️ Modifier Métier", key=f"edit_{target}", use_container_width=True):
                            st.session_state[f"mode_{target}"] = not st.session_state.get(f"mode_{target}", False)
                        
                        if st.session_state.get(f"mode_{target}", False):
                            opts = ["Sans-Emploi", "Agent RCT", "Averis", "Police", "Staff", "Service Public"]
                            cur = [j.strip() for j in job_raw.split("/") if j.strip() in opts]
                            new_m = st.multiselect("Accréditations :", opts, default=cur)
                            
                            if st.button("💾 Enregistrer", type="primary", use_container_width=True):
                                txt = " / ".join(new_m) if new_m else "Sans-Emploi"
                                df_b.loc[df_b["Nom Roblox"] == target, "Emploiement"] = txt
                                cloud_conn.update(worksheet="Banque", data=df_b)
                                st.success("Modifications enregistrées !")
                                st.session_state[f"mode_{target}"] = False
                                time.sleep(1)
                                st.rerun()

        # ---------------- COLONNE 3 : ARCHIVES & REMBOURSEMENT ----------------
        with col3:
            st.markdown("### 📁 Archives Judiciaires")
            with st.container(border=True):
                # --- NUMÉRO DE SÉRIE SÉCURISÉ ---
                st.markdown("""
                    <div style="text-align: right; font-size: 10px; color: #b0b0b0; font-family: monospace; margin-bottom: -5px;">
                        🔒 REF-ARC: JUS-9912<br>
                        <span style="letter-spacing: 2px;">||| || | || || | |||</span>
                    </div>
                """, unsafe_allow_html=True)
                
                try:
                    df_f_check = cloud_conn.read(worksheet="Factures", ttl=20).fillna("")
                    archives = df_f_check[(df_f_check["Cible"] == target) & (df_f_check["Statut"] == "PAYÉ")]
                    
                    if not archives.empty:
                        # Compteur clair
                        st.metric("Total des cas réglés", len(archives))
                        
                        with st.expander("👁️ Voir l'historique complet", expanded=False):
                            for _, f in archives.iterrows():
                                st.markdown(f"""
                                <div style="border: 1px solid #ddd; padding: 12px; background: #fafafa; color: #333; margin-bottom: 10px; border-left: 5px solid #28a745; border-radius: 4px; font-family: monospace;">
                                    <div style="display: flex; justify-content: space-between; font-size: 0.8em;">
                                        <b>REF: #{f['ID']}</b>
                                        <b style="color: #28a745;">ACQUITTÉE ✔</b>
                                    </div>
                                    <hr style="margin: 8px 0; border-top: 1px dashed #ccc;">
                                    <div style="font-size: 0.9em; line-height: 1.5;">
                                        <b>ÉMETTEUR :</b> {f.get('Agent_Signataire', 'N/A')}<br>
                                        <b>SERVICE :</b> {f.get('Emetteur', 'GÉNÉRAL')}<br>
                                        <hr style="margin: 8px 0; border-top: 1px dashed #eee;">
                                        <b>MOTIF :</b> {f['Motif']}<br>
                                        <b>MONTANT :</b> {f['Montant']}$<br>
                                        <b>POINTS :</b> {f.get('Points', 0)}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if st.session_state.user_auth in ["Staff", "Admin"]:
                                    if st.button(f"🔄 Rembourser #{f['ID']}", key=f"ref_{f['ID']}", use_container_width=True):
                                        try:
                                            # Calcul des montants
                                            solde_c = float(str(citoyen_info.iloc[0]['Solde']).replace('$','').replace(',',''))
                                            remb = float(str(f['Montant']).replace('$','').replace(',',''))
                                            
                                            # Mise à jour des DataFrames
                                            df_b.loc[df_b["Nom Roblox"] == target, "Solde"] = solde_c + remb
                                            df_f_check.loc[df_f_check["ID"] == f["ID"], "Statut"] = "REMBOURSÉ"
                                            
                                            # Envoi vers Google Sheets
                                            cloud_conn.update(worksheet="Banque", data=df_b)
                                            cloud_conn.update(worksheet="Factures", data=df_f_check)
                                            
                                            st.success(f"Ticket #{f['ID']} remboursé !")
                                            time.sleep(1)
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Erreur remboursement : {e}")
                    else:
                        st.info("📭 Casier judiciaire vierge ou aucun paiement archivé.")
                        
                except Exception as e:
                    st.error(f"Erreur chargement archives : {e}")
# ======================================================================================
# 7. LOGIQUE DES ONGLETS (CORRIGÉE)
# ======================================================================================

# 1. AFFICHAGE DES AVIS DE RECHERCHE (APB) - Uniquement s'il y en a
# On vérifie si df_apb existe et n'est pas vide avant d'afficher le titre
if 'df_apb' in locals() and not df_apb.empty:
    st.write("### 🚨 AVIS DE RECHERCHE EN COURS")
    for idx, apb in df_apb.iterrows():
        st.warning(f"**SIGNALEMENT :** {apb['Description']} | **MOTIF :** {apb['Motif']} ({apb['Date']})")
    st.write("---")

# ======================================================================================
# NOUVEAU : SYSTÈME DE PAIEMENT DES FACTURES (STYLE TICKET)
# ======================================================================================

df_all_f = cloud_conn.read(worksheet="Factures", ttl=20).fillna("")
mes_factures = df_all_f[(df_all_f["Cible"] == target) & (df_all_f["Statut"] == "EN ATTENTE")]

if not mes_factures.empty:
    st.error(f"⚠️ {len(mes_factures)} FACTURE(S) EN ATTENTE DE PAIEMENT")

for _, fac in mes_factures.iterrows():
    # 1. CALCUL DU TIMER (VERSION ROBUSTE)
    try:
        date_limite = pd.to_datetime(fac["Date_Limite"], dayfirst=True, errors="coerce")
        if pd.notnull(date_limite):
            maintenant = datetime.now()
            temps_restant = date_limite - maintenant
            if temps_restant.total_seconds() > 0:
                h, rem = divmod(int(temps_restant.total_seconds()), 3600)
                m, _ = divmod(rem, 60)
                if h >= 24:
                    jours = h // 24
                    heures = h % 24
                    timer_info = f"⌛ EXPIRE DANS : {jours}j {heures}h"
                else:
                    timer_info = f"⌛ EXPIRE DANS : {h}h {m}min"
                t_color = "#f39c12"
            else:
                timer_info = "⚠️ DÉLAI DÉPASSÉ (IMPAYÉ)"
                t_color = "#d32f2f"
        else:
            timer_info = "⌛ Date invalide"
            t_color = "#555"
    except Exception:
        timer_info = f"⌛ Échéance : {fac['Date_Limite']}"
        t_color = "#555"

    # 2. IDENTIFICATION ÉMETTEUR
    emetteur_label = str(fac.get("Emetteur", "INCONNU"))
    if "POL" in emetteur_label.upper():
        prefix_name = "POLICE NATIONALE"
    elif "AVERIS" in emetteur_label.upper():
        prefix_name = "SERVICES AVERIS"
    else:
        prefix_name = "RÉSEAU RCT"

    # 3. AFFICHAGE DU TICKET
    agent_nom = fac.get("Agent_Signataire", "Officier RCT")
    st.markdown(
        f"""
        <div style="border: 2px solid #000; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; margin-bottom: 5px; box-shadow: 6px 6px 0px #000;">
            <center>
                <b style="font-size:1.1em; text-decoration: underline;">FACTURE OFFICIELLE</b><br>
                <small>{prefix_name}</small>
            </center>
            <hr style="border-top: 1px dashed #000; margin: 10px 0;">
            <div style="font-size: 0.9em; line-height: 1.2;">
                <b>RÉFÉRENCE :</b> #{fac['ID']}<br>
                <b>OFFICIER :</b> {agent_nom}<br>
                <b>SERVICE :</b> {emetteur_label}<br>
                <b>MOTIF :</b> {fac['Motif']}<br>
                <b style="color: {t_color};">{timer_info}</b>
            </div>
            <hr style="border-top: 1px dashed #000; margin: 10px 0;">
            <div style="text-align: center; color: #d32f2f; font-weight: bold; font-size: 1.3em;">
                MONTANT : {fac['Montant']}$
            </div>
            <div style="text-align: center; font-weight: bold; font-size: 1em; margin-top: 5px;">
                POINTS : -{fac.get('Points', 0)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 4. BOUTON DE PAIEMENT
    if fac["Statut"] == "EN ATTENTE":
        if st.button(f"💳 RÉGLER LA FACTURE #{fac['ID']}", key=f"pay_{fac['ID']}", use_container_width=True):
            try:
                with st.spinner("Traitement du paiement..."):
                    df_b = cloud_conn.read(worksheet="Banque", ttl=0)
                    df_all_f = cloud_conn.read(worksheet="Factures", ttl=0)
                    target_val = fac["Cible"]
                    emetteur_val = str(fac["Emetteur"]).upper()
                    
                    # Récupération du solde du payeur
                    idx_b = df_b[df_b["Nom Roblox"] == target_val].index[0]
                    solde_actuel = float(str(df_b.at[idx_b, "Solde"]).replace("$", "").replace(",", ""))
                    montant_facture = float(str(fac["Montant"]).replace(",", ""))

                    if solde_actuel >= montant_facture:
                        # 1. Déduction du solde du payeur
                        df_b.at[idx_b, "Solde"] = solde_actuel - montant_facture
                        
                        # 2. REDIRECTION (Ajout au solde du destinataire)
                        dest_account = None
                        
                        if "CDC" in emetteur_val:
                            dest_account = "CDCB"
                        elif "RCT" in emetteur_val:
                            dest_account = "une10000"
                        elif "AVERIS" in emetteur_val:
                            dest_account = "Moune2010"
                        elif "RENSSELAER" in emetteur_val or "AFCM" in emetteur_val:
                            dest_account = "AFCM"

                        # Si un compte de destination est défini pour cet émetteur (POLSTA n'en a peut-être pas)
                        if dest_account:
                            try:
                                idx_dest = df_b[df_b["Nom Roblox"] == dest_account].index[0]
                                solde_dest = float(str(df_b.at[idx_dest, "Solde"]).replace("$", "").replace(",", ""))
                                df_b.at[idx_dest, "Solde"] = solde_dest + montant_facture
                            except IndexError:
                                st.warning(f"⚠️ Le compte destinataire '{dest_account}' n'existe pas dans la base Banque. L'argent a été déduit mais non transféré.")

                        # 3. Mise à jour du statut de la facture
                        df_all_f.loc[df_all_f["ID"] == fac["ID"], "Statut"] = "PAYÉ"
                        
                        # 4. Envoi à la base de données
                        cloud_conn.update(worksheet="Banque", data=df_b)
                        cloud_conn.update(worksheet="Factures", data=df_all_f)
                        
                        st.success("✅ Facture payée avec succès !")
                        st.cache_data.clear()
                        time.sleep(1) # Laisse le temps au message de s'afficher
                        st.rerun()
                    else:
                        st.error("❌ Solde insuffisant.")
            except Exception as e:
                st.error(f"Erreur lors du paiement : {e}")
# 5. ZONE D'ANNULATION
    if st.session_state.user_auth in ["Staff", "Admin", "POLSTA"]:
        with st.expander(f"🗑️ Zone d'annulation - Facture #{fac['ID']}"):
            code_confirm = st.text_input("Code Agent", type="password", key=f"code_confirm_{fac['ID']}")
            if st.button("Confirmer l'annulation", key=f"admin_del_{fac['ID']}", use_container_width=True):
                
                if code_confirm == "2504": 
                    try:
                        df_f_sync = cloud_conn.read(worksheet="Factures", ttl=0)
                        df_p_sync = cloud_conn.read(worksheet="Points Permis", ttl=0)
                        cible_f = fac.get("Cible")
                        pts_a_rendre = fac.get("Points", 0)
                        
                        # Récupère la valeur de la colonne E (Permis) du Sheet
                        type_p = str(fac.get("Permis", "PKW")).upper()
                        col_pts = "PTS LKW" if "LKW" in type_p else "PTS PKW"
                        
                        if pts_a_rendre and str(pts_a_rendre).isdigit() and int(pts_a_rendre) > 0:
                            if cible_f in df_p_sync["Nom Roblox"].values:
                                idx_p = df_p_sync[df_p_sync["Nom Roblox"] == cible_f].index[0]
                                
                                pts_actuels = int(df_p_sync.at[idx_p, col_pts]) if col_pts in df_p_sync.columns and str(df_p_sync.at[idx_p, col_pts]).isdigit() else 25
                                
                                # Restitution des points (max 25)
                                df_p_sync.at[idx_p, col_pts] = min(25, pts_actuels + int(pts_a_rendre))
                                cloud_conn.update(worksheet="Points Permis", data=df_p_sync)

                        df_f_sync.loc[df_f_sync["ID"] == fac["ID"], "Statut"] = "ANNULÉ"
                        cloud_conn.update(worksheet="Factures", data=df_f_sync)
                        st.success("Annulé !")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur : {e}")
                else:
                    st.error("Code incorrect.")
# ======================================================================================
# SECTION VÉHICULES (SÉCURISÉE : Vérification Agent OU Propriétaire)
# ======================================================================================

if target and target != "---":
    st.write("### 🚗 VÉHICULES ENREGISTRÉS")
    v_data = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]

    if not v_data.empty:
        v_cols = st.columns(3)
        for i, (_, veh) in enumerate(v_data.iterrows()):
            with v_cols[i % 3]:
                # On récupère les infos du véhicule
                plaque_actuelle = veh.get('Numéro de la plaque', '')
                code_prive_vehicule = str(veh.get('CODE', '')) # Le code mis par le civil à l'inscription
                
                date_display = str(veh.get("Horodateur", "Non spécifiée"))
                assu = str(veh.get("Assurance", "")).upper()
                role = st.session_state.user_auth
                
                # ... (Gestion des couleurs et affichage Markdown inchangée) ...
                color = "green"
                status_txt = "✅ VÉHICULE EN RÈGLE"
                if role == "RCT":
                    if "RCT" in assu: color, status_txt = "green", "✅ ASSURÉ RCT"
                    elif "AVERIS" in assu: color, status_txt = "#E67E22", "⚠️ ATTENTION : ASSURÉ AVERIS"
                    else: color, status_txt = "#d32f2f", "🚨 DANGER : NON-ASSURÉ"

                st.markdown(f"""
                    <div style="border: 2px solid black; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; line-height: 1.2;">
                        <center><b>TITRE DE CIRCULATION</b><br><small>RÉPUBLIQUE DE RENSSERLAER</small></center>
                        <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                        <b>DATE :</b> {date_display}<br>
                        <b>NOM :</b> {target}<br>
                        <b>MODÈLE :</b> {veh.get('Marque du véhicule', '')}<br>
                        <b>PLAQUE :</b> <span style="border: 1px solid black; padding: 0 3px;">{plaque_actuelle}</span><br>
                        <b>ASSURANCE :</b> {veh.get('Assurance', '')}
                        <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                        <div style="text-align: center; color: {color}; font-weight: bold; font-size: 0.8em;">{status_txt}</div>
                    </div>
                """, unsafe_allow_html=True)

                # --- ZONE DE RADIATION ---
                with st.expander("🗑️ Radier"):
                    st.warning("S.V.P., mettez votre code de radiation. ⚠️ Attention! Ceci est irréversible ")
                    
                    r_cod_check = st.text_input(
                        "Code de confirmation", 
                        type="password", 
                        key=f"rad_input_{plaque_actuelle}_{i}"
                    )
                    
                    if st.button("CONFIRMER LA RADIATION", key=f"btn_confirm_{plaque_actuelle}_{i}", use_container_width=True, type="primary"):
                        
                        # 1. Vérification dans la feuille BANQUE (pour les agents)
                        try:
                            df_banque = cloud_conn.read(worksheet="Banque", ttl=0)
                            liste_codes_agents = df_banque["Code"].astype(str).tolist()
                        except:
                            liste_codes_agents = []

                        # 2. LOGIQUE DE SÉCURITÉ
                        is_agent = str(r_cod_check) in liste_codes_agents
                        is_owner = str(r_cod_check) == code_prive_vehicule
                        is_staff = st.session_state.user_auth == "Staff"

                        if is_agent or is_owner or is_staff:
                            
                            # ACTION : Suppression
                            df_all_immat = cloud_conn.read(worksheet="Copie de Immatriculations", ttl=0)
                            df_updated = df_all_immat[df_all_immat["Numéro de la plaque"] != plaque_actuelle]
                            cloud_conn.update(worksheet="Copie de Immatriculations", data=df_updated)
                            
                            # LOGS (UTC+2)
                            try:
                                from datetime import datetime, timezone, timedelta
                                import pandas as pd
                                
                                horodateur_actuel = (datetime.now(timezone.utc) + timedelta(hours=2)).strftime("%d/%m/%Y %H:%M:%S")
                                type_user = "Agent/Staff" if (is_agent or is_staff) else "Civil"

                                new_log = {
                                    "Horodateur": horodateur_actuel, 
                                    "Utilisateur": f"{r_cod_check} ({type_user})",                                  
                                    "Action": "Radiation",                                 
                                    "Cible": plaque_actuelle               
                                }
                                
                                df_logs = cloud_conn.read(worksheet="Logs", ttl=0)
                                df_logs = pd.concat([df_logs, pd.DataFrame([new_log])], ignore_index=True)
                                cloud_conn.update(worksheet="Logs", data=df_logs)
                            except:
                                pass

                            st.success(f"✅ Véhicule {plaque_actuelle} radié.")
                            import time
                            time.sleep(1.5)
                            st.cache_data.clear()
                            st.rerun()
                            
                        else:
                            st.error("🚨 Code incorrect. Vous n'êtes ni l'agent autorisé, ni le propriétaire de ce véhicule.")
    else:
        st.info("Aucun véhicule trouvé.")
# ======================================================================================
# 7. LOGIQUE DES ONGLETS (CORRIGÉE ET MISE A JOUR INTERCHANGEABLES EN 1 ÉTAPE)
# ======================================================================================
tab_labels = ["🚗 IMMATRICULATION"]
if st.session_state.user_auth in ["RCT", "Staff", "Entreprise"]: 
    tab_labels.append("👮 SERVICES AGENT")

# Nouvel onglet Banque
if st.session_state.user_auth == "Entreprise":
    tab_labels.append("🏦 BANQUE")

if st.session_state.user_auth == "Staff": 
    tab_labels.append("🛠️ ADMINISTRATION")

tabs = st.tabs(tab_labels)
# --- ONGLET 1 : IMMATRICULATION & RADIATION (ALIGNÉ) ---
with tabs[0]:
    # On crée les colonnes DIRECTEMENT au début du tab
    col_f, col_t = st.columns([1.3, 1])
    
    with col_f:
        # On place le titre ICI pour l'aligner avec la droite
        st.markdown("### 📝 Gestion des Titres")
        
        with st.container(border=True):
            f_owner = st.selectbox("Propriétaire du véhicule", ["---"] + df_b["Nom Roblox"].tolist(), key="k_owner_v7")
            
            # --- CHOIX DU MODE D'IMMATRICULATION ---
            type_immat = st.radio("Type de plaque", ["Unique (1 véhicule)", "Interchangeables (2 véhicules)"], horizontal=True)
            
            # Affichage dynamique des champs selon le choix
            if "Interchangeables" in type_immat:
                c1, c2 = st.columns(2)
                with c1:
                    f_model_1 = st.text_input("Marque du Véhicule 1", key="k_m1_v7")
                with c2:
                    f_model_2 = st.text_input("Marque du Véhicule 2", key="k_m2_v7")
                f_model_display = f"{f_model_1} & {f_model_2}" if f_model_1 and f_model_2 else ""
            else:
                f_model_1 = st.text_input("Marque du véhicule", key="k_m1_v7")
                f_model_2 = None
                f_model_display = f_model_1

            f_plate = st.text_input("Numéro de Plaque souhaité", key="k_plate_v7").upper()
            f_assu = st.selectbox("Type d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"], key="k_assu_v7")
            f_code = st.text_input("Définir un Code de Radiation (Secret)", type="password", key="k_code_v7")
            
            # --- VÉRIFICATION BLACKLIST RCT ---
            is_banned = False
            raison_ban = ""
            if "RCT" in f_assu and f_owner != "---":
                try:
                    df_blacklist = cloud_conn.read(worksheet="Blacklist_RCT", ttl=20).fillna("")
                    if f_owner.strip() in df_blacklist['Nom'].str.strip().tolist():
                        is_banned = True
                        raison_ban = df_blacklist[df_blacklist['Nom'].str.strip() == f_owner.strip()]['Raison'].values[0]
                        st.error(f"🚫 **ACTION INTERDITE** : {f_owner} est banni du RCT.")
                        st.warning(f"⚠️ **Motif :** {raison_ban}")
                except:
                    pass

            # --- VÉRIFICATION DU QUOTA DYNAMIQUE SELON LE MÉTIER ---
            quota_atteint = False
            nb_plaques = 0
            quota_max = 3 # Quota de base (Civil)
            metier_user = "Civil"

            if f_owner != "---":
                # Récupération du métier dans la base de données (Attention au "E" majuscule !)
                try:
                    metier_user = str(df_b[df_b["Nom Roblox"] == f_owner]["Emploiement"].values[0])
                except:
                    pass # Reste sur "Civil" si le métier n'est pas trouvé

                # Ajustement du quota selon le rôle (on cherche si le mot est DANS la cellule)
                if "Staff" in metier_user:
                    quota_max = 6
                elif any(role in metier_user for role in ["Agent RCT", "Service Public", "Police", "Averis"]):
                    quota_max = 4
                else:
                    quota_max = 3 # On s'assure que tout le reste a 3

                # On compte le nombre de titres de circulation appartenant au joueur
                nb_plaques = len(df_i[df_i["Nom d'utilisateur ROBLOX"] == f_owner])
                
                if nb_plaques >= quota_max:
                    quota_atteint = True
                    st.error(f"🛑 **LIMITE ATTEINTE** : {f_owner} possède déjà {nb_plaques} plaques.")
                    st.info(f"En tant que {metier_user}, le quota maximum est de {quota_max} plaques. Une ancienne plaque doit être radiée pour procéder à une nouvelle immatriculation.")

            # --- VÉRIFICATION DE LA PLAQUE (Déjà prise ?) ---
            plaque_prise = False
            if f_plate:
                if not df_i[df_i["Numéro de la plaque"] == f_plate].empty:
                    st.error("❌ Cette plaque est déjà enregistrée dans la base de données. Veuillez en choisir une autre.")
                    plaque_prise = True

            # --- CALCULS TAXE JEUNE ---
            val_taxe_jeune = 0
            if f_owner != "---":
                try:
                    date_brute = df_b[df_b["Nom Roblox"] == f_owner]["Date d'arrivée"].values[0]
                    date_arr = datetime.strptime(str(date_brute), "%d/%m/%Y")
                    if (datetime.now() - date_arr).days < 30:
                        val_taxe_jeune = 50
                        st.warning(f"🔰 JEUNE CONDUCTEUR détecté (+{val_taxe_jeune}$)")
                except: pass

            # --- CALCUL DU TOTAL + OFFRE TRIO RCT ---
            taxe_gouv = 225 if "Interchangeables" in type_immat else 175 
            
            # On bloque la taxe RCT si banni ou quota atteint
            if is_banned or quota_atteint:
                taxe_assu = 0
            else:
                taxe_assu = 130 if "AVERIS" in f_assu else (150 if "RCT" in f_assu else 0)
            
            # Logique Offre Trio (Gratuit pour la 3ème plaque si RCT)
            if "RCT" in f_assu and f_owner != "---" and not is_banned and not quota_atteint:
                if nb_plaques >= 2:
                    taxe_assu = 0
                    st.success(f"🎁 OFFRE TRIO ACTIVÉE")

            total_bill = taxe_gouv + taxe_assu + val_taxe_jeune
            
            # --- BOUTON DE VALIDATION (LOGIQUE RÉELLE + SÉCURITÉ) ---
            
            form_incomplet = False
            if f_owner == "---" or not f_plate or not f_code:
                form_incomplet = True
            if "Unique" in type_immat and not f_model_1:
                form_incomplet = True
            if "Interchangeables" in type_immat and (not f_model_1 or not f_model_2):
                form_incomplet = True

            # Le bouton est désactivé si : Banni OU Plaque prise OU Quota atteint
            bouton_bloque = is_banned or plaque_prise or quota_atteint

            if st.button(f"S'ACQUITTER DE {total_bill}$ ET ENREGISTRER", 
                         use_container_width=True, 
                         key="btn_pay_final", 
                         type="primary", 
                         disabled=bouton_bloque):
                
                if form_incomplet:
                    st.error("⚠️ Formulaire incomplet ! Remplis tous les champs des véhicules.")
                else:
                    try:
                        with st.spinner("Paiement et enregistrement en cours..."):
                            # 1. Calcul du solde
                            idx_user = df_b[df_b["Nom Roblox"] == f_owner].index[0]
                            solde_raw = str(df_b.at[idx_user, "Solde"]).replace('$', '').replace(',', '')
                            solde_actuel = float(solde_raw)
                            
                            if solde_actuel < total_bill:
                                st.error(f"❌ Solde insuffisant ! (Solde: {solde_actuel}$)")
                            else:
                                # 2. Retrait de l'argent
                                df_b.at[idx_user, "Solde"] = solde_actuel - total_bill
                                
                                time_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                marque_fusionnee = f"{f_model_1} / {f_model_2}" if f_model_2 else f_model_1
                                
                                nouvelle_immat = {
                                    "Horodateur": time_now,
                                    "Nom d'utilisateur ROBLOX": f_owner,
                                    "Marque du véhicule": marque_fusionnee,
                                    "Numéro de la plaque": f_plate,
                                    "Assurance": f_assu.split(" (")[0],
                                    "CODE": f_code,
                                    "Points": 25
                                }
                                new_df_i = pd.concat([df_i, pd.DataFrame([nouvelle_immat])], ignore_index=True)
                                
                                cloud_conn.update(worksheet="Banque", data=df_b)
                                cloud_conn.update(worksheet="Copie de Immatriculations", data=new_df_i)
                                
                                # 5. Confirmation
                                st.balloons()
                                st.success(f"""
                                ### ✅ IMMATRICULATION RÉUSSIE !
                                ---
                                * **Propriétaire :** {f_owner}
                                * **Véhicule(s) :** {f_model_display}
                                * **Plaque :** {f_plate}
                                * **Montant débité :** {total_bill}$
                                
                                *Le titre de circulation a été enregistré dans la base nationale.*
                                """)
                                
                                time.sleep(3)
                                st.cache_data.clear()
                                st.rerun()
                                
                    except Exception as e:
                        st.error(f"⚠️ Erreur de connexion au Sheets : {e}")

    with col_t:
        st.markdown("### 🖼️ Aperçu du Titre")
        
        # Préparation des variables de l'aperçu
        date_actuelle = (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M")
        nom_user = f_owner if f_owner != "---" else "---"
        marque_v = f_model_display if f_model_display else "---"
        plaque_v = f_plate if f_plate else "---"
        nom_assu = f_assu if f_assu != "Aucune" else "NON ASSURÉ"
        label_immat = "Frais Interchangeables" if "Interchangeables" in type_immat else "Immatriculation"

        ticket_html = f"""
        <div style='border: 2px dashed #555; padding: 20px; background-color: #f9f9f9; color: #333; font-family: "Courier New", monospace; height: 440px;'>
            <div style='text-align:center;'>
                <h2 style='margin:0; font-size:1.2em;'>TITRE DE CIRCULATION</h2>
                <small>RÉPUBLIQUE DE RENSSERLAER</small><br>
                <h3 style='margin:10px 0; font-size:1em;'>RECU OFFICIEL</h3>
            </div>
            <div style='border-top: 1px dashed #ccc; border-bottom: 1px dashed #ccc; padding: 10px 0; margin: 10px 0; font-size: 0.9em;'>
                <p><strong>DATE :</strong> {date_actuelle}</p>
                <p><strong>UTILISATEUR :</strong> {nom_user}</p>
                <p><strong>MARQUE(S) :</strong> {marque_v}</p>
                <p><strong>PLAQUE :</strong> <span style='border:1px solid #333; padding:2px 6px; background:#eee;'>{plaque_v}</span></p>
                <p><strong>ASSURANCE :</strong> {nom_assu}</p>
            </div>
            <div style='font-size: 0.8em;'>
                <p style='display:flex; justify-content:space-between; margin:2px 0;'><span>{label_immat} :</span><span>{taxe_gouv}$</span></p>
                <p style='display:flex; justify-content:space-between; margin:2px 0;'><span>Assurance :</span><span>{taxe_assu}$</span></p>
                <p style='display:flex; justify-content:space-between; margin:2px 0;'><span>Taxe Jeune :</span><span>{val_taxe_jeune}$</span></p>
            </div>
            <div style='border-top:2px solid #333; padding-top:10px; text-align:right;'>
                <strong style='font-size:1.1em;'>TOTAL PAYÉ : {total_bill}$</strong>
            </div>
            <div style='text-align:center; margin-top:20px; font-size: 0.7em; opacity: 0.7;'>
                CERTIFIÉ CONFORME<br>Par le Terminal National
            </div>
        </div>
        """
        st.components.v1.html(ticket_html, height=500)
# --- ONGLET 2 : SERVICES AGENTS / ENTREPRISES ---
if len(tabs) > 1:
    with tabs[1]:
        # Ajout du rôle "Entreprise"
        roles_autorises = ["RCT", "Averis", "Police", "Staff", "Entreprise"]
        if any(r in st.session_state.user_auth for r in roles_autorises):
            
            # ==========================================
            # 1. ADMINISTRATION BLACKLIST (Masqué pour Entreprise)
            # ==========================================
            if st.session_state.user_auth != "Entreprise":
                st.markdown("## 🛡️ Administration & Blacklist RCT")
                with st.container(border=True):
                    col_add, col_list = st.columns([1, 1.5])
                    
                    # --- PARTIE GAUCHE : AJOUTER ---
                    with col_add:
                        st.markdown("#### 🚫 Bannir un client")
                        b_nom = st.selectbox("Citoyen à bannir", ["---"] + df_b["Nom Roblox"].tolist(), key="rct_ban_nom")
                        b_raison = st.text_area("Raison du bannissement", placeholder="Ex: Impayés récurrents...", key="rct_ban_raison")
                        
                        if st.button("🔴 AJOUTER À LA LISTE", use_container_width=True):
                            if b_nom != "---" and b_raison:
                                try:
                                    with st.spinner("Mise à jour..."):
                                        df_bl = cloud_conn.read(worksheet="Blacklist_RCT", ttl=60).fillna("")
                                        if b_nom in df_bl['Nom'].tolist():
                                            st.error("Cette personne est déjà blacklistée.")
                                        else:
                                            new_ban = pd.DataFrame([{"Nom": b_nom, "Raison": b_raison}])
                                            df_final = pd.concat([df_bl, new_ban], ignore_index=True)
                                            cloud_conn.update(worksheet="Blacklist_RCT", data=df_final)
                                            st.success(f"✅ {b_nom} banni.")
                                            time.sleep(1)
                                            st.cache_data.clear()
                                            st.rerun()
                                except Exception as e:
                                    st.error(f"Erreur : {e}")
                            else:
                                st.warning("Champs incomplets.")

                    # --- PARTIE DROITE : LISTE & UNBAN ---
                    with col_list:
                        st.markdown("#### 📜 Liste Noire Actuelle")
                        try:
                            df_show_bl = cloud_conn.read(worksheet="Blacklist_RCT", ttl=60).fillna("")
                            if not df_show_bl.empty:
                                st.dataframe(df_show_bl, use_container_width=True, hide_index=True, height=200)
                                st.divider()
                                unban_nom = st.selectbox("Sélectionner pour débannir", ["---"] + df_show_bl["Nom"].tolist(), key="unban_select")
                                if st.button("🟢 RETIRER DE LA LISTE", use_container_width=True):
                                    if unban_nom != "---":
                                        df_final = df_show_bl[df_show_bl["Nom"] != unban_nom]
                                        cloud_conn.update(worksheet="Blacklist_RCT", data=df_final)
                                        st.success(f"{unban_nom} autorisé.")
                                        time.sleep(1)
                                        st.cache_data.clear()
                                        st.rerun()
                            else:
                                st.info("La blacklist est vide.")
                        except:
                            st.error("Onglet 'Blacklist_RCT' introuvable dans le Sheets.")

            # ==========================================
            # 2. AUTHENTIFICATION & POINTAGE
            # ==========================================
            st.markdown("## ⏱️ Terminal de Pointage")
            with st.container(border=True):
                c_auth, c_stats = st.columns([1, 2.5])
                
                agent_identifie = None
                agent_valide = False
                
                with c_auth:
                    # Si c'est une entreprise
                    if st.session_state.user_auth == "Entreprise":
                        agent_identifie = st.selectbox(
                            "🏢 Sélection de l'entité", 
                            ["AFCM", "CDCB"], 
                            key="main_agent_auth_entre"
                        )
                        agent_valide = True 
                    # Sinon, code secret pour les agents
                    else:
                        agent_code_saisi = st.text_input("🔑 Code Agent", type="password", key="main_agent_auth")
                        if agent_code_saisi:
                            df_b.columns = df_b.columns.str.strip()
                            df_b["Code_Clean"] = df_b["Code"].astype(str).apply(lambda x: x.strip().split('.')[0])
                            res_agent = df_b[df_b["Code_Clean"] == agent_code_saisi.strip()]
                            
                            if not res_agent.empty:
                                agent_identifie = res_agent.iloc[0]["Nom Roblox"]
                                agent_valide = True
                            else:
                                st.error("❌ Code Agent Invalide")
                
                # Gestion du service si identifié
                if agent_valide and agent_identifie:
                    df_clock = cloud_conn.read(worksheet="Clock", ttl=60).fillna("")
                    df_clock.columns = df_clock.columns.str.strip().str.lower()
                    session_active = df_clock[(df_clock["nom"] == agent_identifie) & (df_clock["statut"] == "en cours")]
                    en_service = not session_active.empty

                    with c_stats:
                        st.markdown(f"### 🎖️ Identifiant : {agent_identifie}")
                        h_actuelle = datetime.now(timezone(timedelta(hours=1))).strftime("%H:%M")
                        m_actuelle, m_debut, m_fin = st.columns(3)
                        m_actuelle.metric("Heure Actuelle", h_actuelle)
                        
                        if en_service:
                            h_deb_brute = session_active.iloc[-1]['début']
                            h_deb_clean = h_deb_brute.split(' ')[1][:5] if ' ' in h_deb_brute else h_deb_brute[:5]
                            m_debut.metric("Heure de Début", h_deb_clean)
                            try:
                                diff = datetime.now(timezone(timedelta(hours=1))) - datetime.strptime(h_deb_brute, "%d/%m/%Y %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=1)))
                                duree_min = int(diff.total_seconds() / 60)
                                m_fin.metric("Temps de Service", f"{duree_min} min")
                            except:
                                m_fin.metric("Temps de Service", "Calcul...")
                        else:
                            m_debut.metric("Heure de Début", "--:--")
                            m_fin.metric("Temps de Service", "0 min")

                    st.divider()

                    # Détermination dynamique du job
                    job_auto = "POLSTA" if st.session_state.user_auth == "Staff" else "RCT"
                    if "Averis" in st.session_state.user_auth: job_auto = "Averis"
                    if st.session_state.user_auth == "Entreprise": job_auto = "Entreprise"
                    
                    if not en_service:
                        st.info(f"💡 **Information :** Vous êtes connecté en tant que **{job_auto}**.")
                        if st.button(f"▶️ DÉBUT DE SERVICE ({job_auto})", use_container_width=True, type="primary"):
                            h_deb = datetime.now(timezone(timedelta(hours=1))).strftime("%d/%m/%Y %H:%M:%S")
                            new_row = pd.DataFrame([{"nom": agent_identifie, "action": "SERVICE", "job": job_auto, "début": h_deb, "fin": "", "statut": "en cours"}])
                            cloud_conn.update(worksheet="Clock", data=pd.concat([df_clock, new_row], ignore_index=True))
                            st.success(f"✅ Session {job_auto} a débuté !")
                            time.sleep(1); st.rerun()
                    else:
                        st.warning(f"🚨 **Information :** Session **{job_auto}** en cours.")
                        if st.button(f"⏹️ FIN DE SERVICE ({job_auto})", use_container_width=True):
                            h_fin = datetime.now(timezone(timedelta(hours=1))).strftime("%d/%m/%Y %H:%M:%S")
                            df_clock.at[session_active.index[-1], "fin"] = h_fin
                            df_clock.at[session_active.index[-1], "statut"] = "à valider"
                            cloud_conn.update(worksheet="Clock", data=df_clock)
                            st.success(f"✅ Session {job_auto} a pris fin !")
                            time.sleep(1); st.rerun()
            # ==========================================
            # 3. GESTION DES FACTURES & RETARDS
            # ==========================================
            st.markdown("### 📑 GESTION DES FACTURES")
            
            df_f_check = cloud_conn.read(worksheet="Factures", ttl=60).fillna("")
            maintenant = datetime.now()
            df_f_check['Date_Limite_DT'] = pd.to_datetime(df_f_check['Date_Limite'], dayfirst=True, errors='coerce')
            
            def determiner_statut(row):
                s_sheets = str(row["Statut"]).strip().upper()
                statuts_regles = ["PAYÉ", "PAYÉE", "REMBOURSÉ", "REMBOURSÉE", "ANNULÉ", "ANNULÉE"]
                if s_sheets in statuts_regles: return s_sheets
                if pd.notnull(row['Date_Limite_DT']) and maintenant > row['Date_Limite_DT']:
                    return "EN RETARD"
                return "EN ATTENTE"
            
            df_f_check["Statut_Reel"] = df_f_check.apply(determiner_statut, axis=1)
            
            df_retards_auto = df_f_check[df_f_check["Statut_Reel"] == "EN RETARD"]
            if not df_retards_auto.empty:
                with st.expander(f"🚨 ALERTES : {len(df_retards_auto)} RETARDS DÉTECTÉS", expanded=True):
                    for _, row in df_retards_auto.sort_values(by="Date_Limite_DT").iterrows():
                        st.error(f"**[REF: {row['ID']}]** {row['Cible']} — **{row['Montant']}$** (Limite : {row['Date_Limite']})")
            else:
                st.success("✅ Aucune facture en retard pour le moment.")
            
            with st.container(border=True):
                c_s1, c_s2 = st.columns([2, 1])
                search_f = c_s1.text_input("🔍 Chercher un dossier spécifique", placeholder="Nom, Référence...", key="search_ui")
                filter_f = c_s2.selectbox("Filtrer par état", ["---", "En Attente", "En Retard", "Payé", "Remboursé", "Annulé"])
            
            if search_f != "" or filter_f != "---":
                query = search_f.lower()
                df_filtered = df_f_check[
                    (df_f_check["ID"].astype(str).str.contains(query)) | 
                    (df_f_check["Cible"].str.lower().str.contains(query)) |
                    (df_f_check["Motif"].str.lower().str.contains(query))
                ]
                
                if filter_f != "---":
                    f_val = filter_f.upper()
                    if f_val == "PAYÉ": df_filtered = df_filtered[df_filtered["Statut_Reel"].isin(["PAYÉ", "PAYÉE"])]
                    elif f_val == "REMBOURSÉ": df_filtered = df_filtered[df_filtered["Statut_Reel"].isin(["REMBOURSÉ", "REMBOURSÉE"])]
                    elif f_val == "ANNULÉ": df_filtered = df_filtered[df_filtered["Statut_Reel"].isin(["ANNULÉ", "ANNULÉE"])]
                    else: df_filtered = df_filtered[df_filtered["Statut_Reel"] == f_val]
            
                if not df_filtered.empty:
                    st.write(f"🔍 Résultats ({len(df_filtered)}) :")
                    for _, row in df_filtered.iterrows():
                        s = row["Statut_Reel"]
                        b_col = "#3498db" if "REMBOURS" in s else "#95a5a6" if "ANNUL" in s else "#27ae60" if "PAY" in s else "#e74c3c" if s == "EN RETARD" else "#f39c12"
                        
                        with st.container(border=True):
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.markdown(f"""
                                    <div style="border-left: 5px solid {b_col}; padding-left: 15px;">
                                        <b style="color:{b_col}; font-size: 1.1em;">{s} — RÉF : {row['ID']}</b><br>
                                        <span style="font-size: 1.2em; font-weight: bold;">{row['Cible']}</span><br>
                                        <small>Motif : {row['Motif']}</small>
                                    </div>
                                """, unsafe_allow_html=True)
                            with c2:
                                st.markdown(f"<h3 style='text-align: center; margin-top: 10px;'>{row['Montant']}$</h3>", unsafe_allow_html=True)
                else:
                    st.warning("🔎 Aucun dossier trouvé.")
                    
            # ======================================================================================
            # 4. MANDATS & RECHERCHE
            # ======================================================================================
            st.markdown("### 🔍 MANDATS & RECHERCHE")

            # Création des onglets
            tab_citoyens, tab_vehicules = st.tabs(["👤 Citoyens", "🚘 Véhicules"])

            # --------------------------------------------------------------------------------------
            # ONGLET 1 : CITOYENS
            # --------------------------------------------------------------------------------------
            with tab_citoyens:
                with st.container(border=True):
                    st.markdown("#### 📝 Lancer un Mandat d'Arrêt")
                    c1, c2, c3 = st.columns([1.5, 2, 1])
                    with c1:
                        liste_citoyens = sorted(df_b["Nom Roblox"].unique().tolist())
                        cible_mandat = st.selectbox("Suspect", ["---"] + liste_citoyens, key="mandat_cible")
                    with c2:
                        motif_mandat = st.text_input("Motif de recherche", placeholder="Ex: Braquage...", key="mandat_motif")
                    with c3:
                        st.write(" ")
                        if st.button("🚨 LANCER L'ALERTE", use_container_width=True, type="primary"):
                            if cible_mandat != "---" and motif_mandat:
                                idx = df_b[df_b["Nom Roblox"] == cible_mandat].index[0]
                                df_b.at[idx, "Statut"] = "RECHERCHÉ"
                                df_b.at[idx, "Motif Recherche"] = motif_mandat
                                cloud_conn.update(worksheet="Banque", data=df_b)
                                st.success(f"Mandat lancé contre {cible_mandat} !")
                                time.sleep(1); st.rerun()
                            else:
                                st.error("Champs requis !")

                col_m1, col_m2 = st.columns([2, 1])
                with col_m1:
                    with st.container(border=True):
                        st.markdown("#### 📢 Alertes Actives")
                        recherches = df_b[df_b["Statut"].str.upper().str.contains("RECHERCHÉ", na=False)]
                        if not recherches.empty:
                            for _, crim in recherches.iterrows():
                                with st.container(border=True):
                                    c1_r, c2_r = st.columns([3, 1])
                                    c1_r.warning(f"🚨 **{crim['Nom Roblox']}**\n\n**Motif :** {crim.get('Motif Recherche', 'N/A')}")
                                    if c2_r.button("A été interpellé", key=f"rel_{crim['Nom Roblox']}", use_container_width=True):
                                        idx = df_b[df_b["Nom Roblox"] == crim["Nom Roblox"]].index[0]
                                        df_b.at[idx, "Statut"], df_b.at[idx, "Motif Recherche"] = "RAS", ""
                                        cloud_conn.update(worksheet="Banque", data=df_b)
                                        st.rerun()
                        else: 
                            st.success("✅ Aucun mandat actif.")

                with col_m2:
                    with st.container(border=True):
                        st.markdown("#### 🔦 Scanner Plaque")
                        p_search = st.text_input("Saisir plaque", key="plate_ui").upper().strip()
                        if p_search:
                            m = df_i[df_i["Numéro de la plaque"].astype(str).str.contains(p_search, na=False)]
                            if not m.empty:
                                nom_proprio = m.iloc[0]["Nom d'utilisateur ROBLOX"]
                                is_wanted = not df_b[(df_b["Nom Roblox"] == nom_proprio) & (df_b["Statut"] == "RECHERCHÉ")].empty
                                if is_wanted: st.error(f"⚠️ **PROPRIO RECHERCHÉ**")
                                st.info(f"👤 **Proprio :** {nom_proprio}\n\n🚘 **Modèle :** {m.iloc[0]['Marque du véhicule']}")
                            else: 
                                st.error("❌ Plaque inconnue")

            # --------------------------------------------------------------------------------------
            # ONGLET 2 : VÉHICULES (Version Finale Sécurisée)
            # --------------------------------------------------------------------------------------
            with tab_vehicules:
                st.markdown("#### 📝 Lancer un Avis de Recherche Véhicule")
                
                # Choix du mode avec une clé unique pour forcer le rafraîchissement propre
                type_recherche = st.radio(
                    "Méthode de recherche :", 
                    ["Immatriculé (Plaque)", "Non Immatriculé (APB)"], 
                    horizontal=True,
                    key="selector_mode_recherche"
                )

                if type_recherche == "Immatriculé (Plaque)":
                    # --- INTERFACE POUR VÉHICULES AVEC PLAQUE ---
                    with st.container(border=True):
                        c1_v, c2_v, c3_v = st.columns([1.5, 2, 1])
                        with c1_v:
                            plaque_cible = st.text_input("Numéro de plaque", placeholder="Ex: OIH-5949", key="input_plaque_fix").upper().strip()
                        with c2_v:
                            motif_veh = st.text_input("Motif de recherche", placeholder="Ex: Délit de fuite...", key="motif_plaque_fix")
                        with c3_v:
                            st.write(" ")
                            if st.button("🚨 ALERTE PLAQUE", use_container_width=True, type="primary"):
                                if plaque_cible and motif_veh:
                                    mask = df_i["Numéro de la plaque"].astype(str).str.upper() == plaque_cible
                                    if mask.any():
                                        idx_veh = df_i[mask].index[0]
                                        df_i.at[idx_veh, "Statut"] = "RECHERCHÉ"
                                        df_i.at[idx_veh, "Motif Recherche"] = motif_veh
                                        cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i)
                                        st.success("Avis lancé !")
                                        time.sleep(1); st.rerun()
                                    else:
                                        st.error("Plaque introuvable dans la base.")
                                else:
                                    st.error("Champs requis !")

                    # --- LISTE DES VÉHICULES RECHERCHÉS (PLAQUES) ---
                    st.markdown("---")
                    st.markdown("#### 📢 Véhicules Immatriculés Recherchés")
                    veh_recherches = df_i[df_i["Statut"].str.upper().str.contains("RECHERCHÉ", na=False)] if 'Statut' in df_i.columns else pd.DataFrame()
                    
                    if not veh_recherches.empty:
                        for _, veh in veh_recherches.iterrows():
                            with st.container(border=True):
                                col1, col2 = st.columns([3, 1])
                                col1.warning(f"🚘 **Plaque:** {veh['Numéro de la plaque']} | **Motif:** {veh.get('Motif Recherche', 'N/A')}")
                                if col2.button("Intercepté", key=f"rel_veh_{veh['Numéro de la plaque']}", use_container_width=True):
                                    idx = df_i[df_i["Numéro de la plaque"] == veh["Numéro de la plaque"]].index[0]
                                    df_i.at[idx, "Statut"], df_i.at[idx, "Motif Recherche"] = "RAS", ""
                                    cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i)
                                    st.rerun()
                    else:
                        st.success("✅ Aucun véhicule immatriculé recherché.")

                else:
                    # --- INTERFACE APB (SANS PLAQUE) ---
                    # Ici, le code est totalement isolé du bloc précédent
                    with st.form("form_apb_unique", clear_on_submit=True):
                        st.markdown("##### 🚨 Nouveau Signalement APB (Signalement Visuel)")
                        ca1, ca2 = st.columns([1.5, 2])
                        with ca1:
                            desc_apb = st.text_input("Description du véhicule", placeholder="Ex: Berline noire, vitres teintées...")
                        with ca2:
                            motif_apb = st.text_input("Motif de l'avis", placeholder="Ex: Braquage de supérette...")
                        
                        submit = st.form_submit_button("🚨 DIFFUSER L'AVIS APB", use_container_width=True, type="primary")
                        
                        if submit:
                            if desc_apb and motif_apb:
                                from datetime import datetime
                                new_line = pd.DataFrame([{"Description": desc_apb, "Motif": motif_apb, "Date": datetime.now().strftime("%d/%m/%Y %H:%M")}])
                                df_a = pd.concat([df_a, new_line], ignore_index=True)
                                cloud_conn.update(worksheet="Signalements_APB", data=df_a)
                                st.success("APB diffusé avec succès !")
                                time.sleep(1); st.rerun()
                            else:
                                st.error("Veuillez remplir la description et le motif.")

                    # --- LISTE DES APB ACTIFS ---
                    st.markdown("---")
                    st.markdown("#### 📋 Signalements APB Actifs")
                    if not df_a.empty:
                        df_a_clean = df_a[df_a["Motif"].astype(str).str.strip() != ""]
                        if not df_a_clean.empty:
                            for idx, apb in df_a_clean.iterrows():
                                with st.container(border=True):
                                    c1, c2 = st.columns([3, 1])
                                    c1.error(f"🚨 **Description:** {apb.get('Description', 'N/A')}\n\n**Motif:** {apb.get('Motif', 'N/A')}")
                                    if c2.button("Levée APB", key=f"btn_apb_{idx}", use_container_width=True):
                                        df_a = df_a.drop(idx)
                                        cloud_conn.update(worksheet="Signalements_APB", data=df_a)
                                        st.rerun()
                        else:
                            st.info("Aucun APB actif.")
                    else:
                        st.success("✅ Aucun APB en cours.")
                        
# ==========================================
# 5. INTERVENTION SUR CITOYEN & FACTURATION
# ==========================================
st.divider()

if 'target' not in locals() or target == "---":
    st.warning("⚠️ Sélectionnez un citoyen en haut de la page pour ouvrir le module d'intervention.")

elif 'agent_identifie' not in locals() or not agent_identifie:
    st.info("🔒 Veuillez vous identifier (Section 2) pour accéder à la facturation.")

else:
    st.markdown(f"### ⚡ INTERVENTION : {target.upper()}")
    col_form, col_facture, col_vehicules = st.columns([1.2, 1, 1])

    with col_form:
        with st.form("form_intervention", border=True):
            # Gestion des rôles et émetteurs
            if st.session_state.user_auth == "Staff":
                f_emetteur = st.selectbox("Émetteur", ["POLSTA", "Averis", "RCT", "CDC", "AFCM"], key="em_ui")
            elif st.session_state.user_auth == "Entreprise":
                # Si l'agent est du CDC, on verrouille sur CDC, sinon AFCM
                if "CDC" in agent_identifie:
                    f_emetteur = "CDC"
                else:
                    f_emetteur = "AFCM"
                st.info(f"🏢 **Émetteur :** {f_emetteur}")
            elif "Averis" in st.session_state.user_auth:
                f_emetteur = "Averis"
                st.info(f"🏢 **Émetteur :** {f_emetteur}")
            else:
                f_emetteur = "RCT"
                st.info(f"🏢 **Émetteur :** {f_emetteur}")
            
            label_montant = "Frais de prestation ($)" if f_emetteur in ["AFCM", "CDC"] else "Amende ($)"
            f_val = st.number_input(label_montant, 0, 100000, 500, step=100, key="val_live")
            
            can_pull_points = (st.session_state.user_auth == "Staff" and f_emetteur == "POLSTA")
            
            # Choix du type de permis et retrait des points
            f_permis_type = st.selectbox("Permis concerné", ["PKW", "LKW"], key="permis_type_live", disabled=not can_pull_points)
            f_pts = st.slider("Retrait de points", 0, 25, 0, disabled=not can_pull_points, key="pts_live")
            
            f_motif = st.text_area("Motif / Prestation", key="mot_live", placeholder="Ex: Frais bancaires, Frais de dossier...")
            
            target_veh = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
            liste_plaques = ["AUCUN"] + target_veh["Numéro de la plaque"].tolist() if not target_veh.empty else ["AUCUN"]
            f_plate = st.selectbox("Véhicule lié", liste_plaques, key="plate_live")
            
            submit_facture = st.form_submit_button("🚨 ENVOYER LA FACTURE", use_container_width=True, type="primary")
            
            if submit_facture:
                if f_motif:
                    # L'argent va vers CDCB si l'émetteur est CDC
                    receveur_final = "CDCB" if f_emetteur == "CDC" else f_emetteur

                    with st.spinner("Enregistrement..."):
                        df_all_f = cloud_conn.read(worksheet="Factures", ttl=0).fillna("") 
                        new_f = {
                            "ID": random.randint(10000, 99999),
                            "Cible": target,
                            "Emetteur": receveur_final,
                            "Permis": f_permis_type if can_pull_points else "",
                            "Agent_Signataire": agent_identifie,
                            "Montant": f_val,
                            "Points": f_pts if can_pull_points else 0,
                            "Motif": f"{f_motif} [{f_plate}]",
                            "Statut": "EN ATTENTE",
                            "Date_Emission": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Date_Limite": (datetime.now() + timedelta(hours=24)).strftime("%d/%m/%Y %H:%M")
                        }
                        
                        if f_pts > 0 and can_pull_points:
                            try:
                                idx_p = df_p[df_p["Nom Roblox"] == target].index[0]
                                col_pts = "PTS LKW" if f_permis_type == "LKW" else "PTS PKW"
                                
                                # Récupération sécurisée du solde de points actuel
                                current_pts = int(df_p.at[idx_p, col_pts]) if col_pts in df_p.columns and str(df_p.at[idx_p, col_pts]).isdigit() else 25
                                df_p.at[idx_p, col_pts] = max(0, current_pts - f_pts)
                                cloud_conn.update(worksheet="Points Permis", data=df_p)
                            except Exception as e:
                                st.error(f"Erreur points: {e}")
                        
                        updated_df_f = pd.concat([df_all_f, pd.DataFrame([new_f])], ignore_index=True)
                        cloud_conn.update(worksheet="Factures", data=updated_df_f)
                        
                        st.success(f"✅ Facture envoyée au compte : {receveur_final}")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error("❌ Motif/Description obligatoire.")

    # --- COLONNE 2 : APERÇU ---
    with col_facture:
        st.markdown("#### 📄 Aperçu")
        
        if f_emetteur == "CDC":
            header_ticket = "FACTURE CDC"
        elif f_emetteur == "AFCM":
            header_ticket = "AFCM"
        else:
            header_ticket = "FACTURE OFFICIELLE"
        
        st.markdown(f"""
        <div style="border: 2px solid black; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; line-height: 1.2; box-shadow: 4px 4px 0px #888;">
            <center><b>{header_ticket}</b><br><small>RÉPUBLIQUE DE RENSSERLAER</small></center>
            <hr style="border-top: 1px dashed black; margin: 10px 0;">
            <b>SIGNATAIRE :</b> {str(agent_identifie).upper()}<br>
            <b>ÉMETTEUR   :</b> {str(f_emetteur).upper()}<br>
            <b>DATE       :</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
            <b>NOM        :</b> {target}<br>
            <b>OBJET      :</b> {str(st.session_state.get('mot_live', '...')).upper()}<br>
            <b>MONTANT    :</b> {st.session_state.get('val_live', 0)}$
            <hr style="border-top: 1px dashed black; margin: 10px 0;">
            <div style="text-align: center; font-weight: bold;">
                {"POINTS : -" + str(st.session_state.get('pts_live', 0)) if can_pull_points else "SERVICE PROFESSIONNEL"}<br>
                <small>Compte de dépôt : {"CDCB" if f_emetteur == "CDC" else f_emetteur}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- COLONNE 3 : VÉHICULES ---
    with col_vehicules:
        st.markdown("#### 🚗 Véhicules")
        if not target_veh.empty:
            for _, veh in target_veh.iterrows():
                assu_v = str(veh.get('Assurance', '')).upper()
                if "RCT" in assu_v: col_v, txt_v = "#27ae60", "✅ ASSURÉ RCT"
                elif "AVERIS" in assu_v: col_v, txt_v = "#E67E22", "⚠️ ASSURÉ AVERIS"
                else: col_v, txt_v = "#d32f2f", "🚨 NON-ASSURÉ"

                st.markdown(f"""
                <div style="border: 2px solid black; padding: 10px; background: white; color: black; font-family: 'Courier New', monospace; margin-bottom: 10px; font-size: 0.85em;">
                    <center><b>TITRE DE CIRCULATION</b></center>
                    <hr style="border-top: 1px solid #ccc; margin: 5px 0;">
                    <b>MODÈLE :</b> {veh.get('Marque du véhicule', 'Inconnu')}<br>
                    <b>PLAQUE :</b> <span style="border: 1px solid black; padding: 0 2px;">{veh.get('Numéro de la plaque', '???')}</span><br>
                    <hr style="border-top: 1px solid #ccc; margin: 5px 0;">
                    <div style="text-align: center; color: {col_v}; font-weight: bold;">{txt_v}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucun véhicule trouvé.")
# ======================================================================================
# --- ONGLET 3 : ADMINISTRATION (STAFF UNIQUEMENT) ---
# ======================================================================================
if len(tabs) > 2:
    with tabs[2]:
        if st.session_state.user_auth == "Staff":
            st.markdown("## 🛠️ ADMINISTRATION GÉNÉRALE")
            st.info("Espace réservé à la gestion nationale, validation des services et paies.")
            
            # --- A. MODULE DE VALIDATION DES HEURES (CLOCK) ---
            st.divider()
            st.subheader("🛡️ Validation des Services")
            
            try:
                df_admin_clock = cloud_conn.read(worksheet="Clock", ttl=20).fillna("")
                df_admin_clock.columns = df_admin_clock.columns.str.strip().str.lower()
                attente = df_admin_clock[df_admin_clock["statut"] == "à valider"]
                
                if not attente.empty:
                    for i, row in attente.iterrows():
                        with st.container(border=True):
                            c1, c2 = st.columns([3, 1])
                            c1.markdown(f"**🕵️ Agent :** {row['nom']} | **Job :** {row['job']}")
                            c1.caption(f"📅 Du {row['début']} au {row['fin']}")
                            
                            col_v, col_r = c2.columns(2)
                            if col_v.button("✔️", key=f"valid_{i}"):
                                df_admin_clock.at[i, "statut"] = "Validé"
                                cloud_conn.update(worksheet="Clock", data=df_admin_clock)
                                st.success("Service validé !")
                                time.sleep(0.5)
                                st.rerun()
                                
                            if col_r.button("❌", key=f"refus_{i}"):
                                df_admin_clock.at[i, "statut"] = "Refusé"
                                cloud_conn.update(worksheet="Clock", data=df_admin_clock)
                                st.warning("Service refusé.")
                                time.sleep(0.5)
                                st.rerun()
                else:
                    st.info("✅ Aucun service en attente de validation.")
            except Exception as e:
                st.error(f"Erreur d'accès à la feuille Clock : {e}")

# --- B. CRÉATION DE DOSSIER CITOYEN ---
            st.divider()
            st.subheader("👤 Nouveau Dossier Citoyen")
            with st.container(border=True):
                c_new1, c_new2 = st.columns(2)
                with c_new1:
                    new_name = st.text_input("Nom d'utilisateur ROBLOX", key="adm_create_name")
                    new_discord = st.text_input("Identifiant Discord", key="adm_create_discord")
                with c_new2:
                    new_jobs = st.multiselect("Emplois initiaux", ["Sans-Emploi", "Agent RCT", "Averis", "Police", "Staff", "Service Public"], default=["Sans-Emploi"])
                    new_pts_pkw = st.slider("Points Permis PKW", 0, 25, 25)

                if st.button("🆕 CRÉER LE DOSSIER", use_container_width=True, type="primary"):
                    if new_name:
                        today_str = datetime.now().strftime("%d/%m/%Y")
                        new_row_bank = pd.DataFrame([{
                            "Nom Roblox": new_name, "Nom Discord": new_discord, "Solde": 15000,
                            "Emploiement": " / ".join(new_jobs), "Date d'arrivée": today_str,
                            "Statut": "RAS", "Code": f"{new_name}123", "Code Agent": ""
                        }])
                        
                        # Attribution des points pour le permis PKW uniquement (LKW à 0 par défaut)
                        new_row_pts = pd.DataFrame([{
                            "Nom Roblox": new_name,
                            "PTS PKW": new_pts_pkw,
                            "PTS LKW": 0,
                            "Validité PKW": "OUI" if new_pts_pkw > 0 else "NON",
                            "Validité LKW": "NON"
                        }])
                        
                        try:
                            df_b_updated = pd.concat([df_b, new_row_bank], ignore_index=True)
                            df_p_updated = pd.concat([df_p, new_row_pts], ignore_index=True)
                            cloud_conn.update(worksheet="Banque", data=df_b_updated)
                            cloud_conn.update(worksheet="Points Permis", data=df_p_updated)
                            st.success(f"✅ Dossier créé pour {new_name} avec permis PKW ({new_pts_pkw} pts) !")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur : {e}")
            # --- C. TERMINAL DE PAIE NATIONALE (STAFF SEULEMENT) ---
            st.divider()
            st.markdown("### 🧧 Terminal de Paie Nationale")
            with st.container(border=True):
                tab_individuel, tab_global = st.tabs(["👤 Paie Individuelle", "🌐 Paie Globale"])
                
                # OPTION 1 : PAIE INDIVIDUELLE
                with tab_individuel:
                    list_users = sorted(df_b["Nom Roblox"].unique().tolist()) if not df_b.empty else []
                    target_paie = st.selectbox("Sélectionner le bénéficiaire :", ["---"] + list_users, key="paie_target_select")

                    if target_paie != "---":
                        user_data = df_b[df_b["Nom Roblox"] == target_paie].iloc[0]
                        user_jobs = str(user_data.get("Emploiement", "")).split(" / ")
                        solde_actuel = float(str(user_data.get("Solde", 0)).replace('$', '').replace(',', '').strip())

                        logs_paie = df_admin_clock[(df_admin_clock["nom"] == target_paie) & (df_admin_clock["statut"] == "Validé")]
                        min_rct, min_pol = 0, 0
                        for _, r in logs_paie.iterrows():
                            try:
                                d = (datetime.strptime(str(r["fin"]), "%d/%m/%Y %H:%M:%S") - datetime.strptime(str(r["début"]), "%d/%m/%Y %H:%M:%S")).total_seconds() / 60
                                if "RCT" in str(r["job"]).upper(): min_rct += d
                                elif "POL" in str(r["job"]).upper(): min_pol += d
                            except: continue

                        total_brut = 15000 + int(2000 * min(min_rct/1200, 1)) + int(3000 * min(min_pol/1200, 1))
                        if "Staff" in user_jobs: total_brut += 4000
                        
                        user_vehs = df_i[df_i["Nom d'utilisateur ROBLOX"] == target_paie]
                        total_deduc = len(user_vehs) * 150
                        net_to_pay = total_brut - total_deduc

                        st.markdown(f"**Net à verser : {net_to_pay:,} $** *(Inclut les primes Staff et autres bonus applicables)*")
                        
                        if st.button("🚀 VIRER LA PAIE", use_container_width=True, type="primary", key="btn_paie_indiv"):
                            if "Averis" in user_jobs and "Moune2010" in df_b["Nom Roblox"].values:
                                idx_m = df_b[df_b["Nom Roblox"] == "Moune2010"].index[0]
                                solde_m = float(str(df_b.at[idx_m, "Solde"]).replace('$', '').replace(',', '').strip())
                                df_b.at[idx_m, "Solde"] = solde_m + net_to_pay
                                st.success("Redirection effectuée vers Moune2010.")
                            else:
                                idx_c = df_b[df_b["Nom Roblox"] == target_paie].index[0]
                                df_b.at[idx_c, "Solde"] = solde_actuel + net_to_pay
                                
                            for idx_log in logs_paie.index: df_admin_clock.at[idx_log, "statut"] = "Payé"
                            
                            cloud_conn.update(worksheet="Banque", data=df_b)
                            cloud_conn.update(worksheet="Clock", data=df_admin_clock)
                            st.balloons()
                            st.rerun()

                # OPTION 2 : PAIE GLOBALE
                with tab_global:
                    st.write("Calcul et versement du salaire net pour **tous les citoyens**.")
                    
                    if st.button("🚀 VIRER LA PAIE À TOUT LE MONDE", use_container_width=True, type="primary", key="btn_paie_globale"):
                        if df_b.empty:
                            st.warning("Aucun citoyen trouvé dans la base.")
                        else:
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            total_users = len(df_b)
                            
                            for index, row in df_b.iterrows():
                                user_name = row["Nom Roblox"]
                                status_text.text(f"Traitement : {user_name}...")
                                
                                # Lecture dynamique du solde pour éviter les conflits d'écrasement
                                try:
                                    solde_actuel = float(str(df_b.at[index, "Solde"]).replace('$', '').replace(',', '').strip())
                                except:
                                    solde_actuel = 0.0

                                user_jobs = str(row.get("Emploiement", "")).split(" / ")

                                logs_paie = df_admin_clock[(df_admin_clock["nom"] == user_name) & (df_admin_clock["statut"] == "Validé")]
                                min_rct, min_pol = 0, 0
                                for _, r in logs_paie.iterrows():
                                    try:
                                        d = (datetime.strptime(str(r["fin"]), "%d/%m/%Y %H:%M:%S") - datetime.strptime(str(r["début"]), "%d/%m/%Y %H:%M:%S")).total_seconds() / 60
                                        if "RCT" in str(r["job"]).upper(): min_rct += d
                                        elif "POL" in str(r["job"]).upper(): min_pol += d
                                    except: continue

                                total_brut = 15000 + int(2000 * min(min_rct/1200, 1)) + int(3000 * min(min_pol/1200, 1))
                                if "Staff" in user_jobs: total_brut += 4000

                                user_vehs = df_i[df_i["Nom d'utilisateur ROBLOX"] == user_name]
                                total_deduc = len(user_vehs) * 150
                                net_to_pay = total_brut - total_deduc
                                
                                if "Averis" in user_jobs and "Moune2010" in df_b["Nom Roblox"].values:
                                    idx_moune = df_b[df_b["Nom Roblox"] == "Moune2010"].index[0]
                                    try:
                                        solde_moune = float(str(df_b.at[idx_moune, "Solde"]).replace('$', '').replace(',', '').strip())
                                    except:
                                        solde_moune = 0.0
                                    df_b.at[idx_moune, "Solde"] = solde_moune + net_to_pay
                                else:
                                    df_b.at[index, "Solde"] = solde_actuel + net_to_pay

                                for idx_log in logs_paie.index:
                                    df_admin_clock.at[idx_log, "statut"] = "Payé"

                                progress_bar.progress((index + 1) / total_users)

                            status_text.text("Sauvegarde en cours sur Google Sheets...")
                            cloud_conn.update(worksheet="Banque", data=df_b)
                            cloud_conn.update(worksheet="Clock", data=df_admin_clock)

                            st.success("Toutes les paies ont été versées avec succès !")
                            st.balloons()
                            st.rerun()

            # --- D. JOURNAUX D'AUDIT ---
            st.divider()
            st.markdown("### 📜 Journaux d'Audit (Session)")
            if "audit_logs" in st.session_state and st.session_state.audit_logs:
                with st.container(height=150, border=True):
                    for log in reversed(st.session_state.audit_logs): st.write(f"🔹 {log}")
# ==========================================
#         ONGLET 4 : BANQUE ENTREPRISE
# ==========================================
try:
    idx_bank = tab_labels.index("🏦 BANQUE")
    with tabs[idx_bank]:
        st.header("🏦 Système Bancaire Entreprise")
        
        if "auth_banque" not in st.session_state:
            st.session_state.auth_banque = False
            st.session_state.ent_active = "AFCM" # Par défaut

        if not st.session_state.auth_banque:
            col_auth, _ = st.columns([1, 2])
            with col_auth:
                st.subheader("Authentification Entreprise")
                code_saisi = st.text_input("Code Entreprise", type="password", key="pwd_ent_v8")
                if st.button("🔓 ACCÉDER", use_container_width=True):
                    # Gestion des accès par entreprise
                    if code_saisi == "AFCM-MA-RCT":
                        st.session_state.auth_banque = True
                        st.session_state.ent_active = "AFCM"
                        st.rerun()
                    elif code_saisi == "CountyDC-2026": # Code exemple pour CDC
                        st.session_state.auth_banque = True
                        st.session_state.ent_active = "CDCB"
                        st.rerun()
                    else:
                        st.error("Code incorrect.")
        else:
            # --- CONFIGURATION DYNAMIQUE ---
            nom_banque = st.session_state.ent_active
            label_ent = "CDC" if nom_banque == "CDCB" else "AFCM"
            
            # --- CHARGEMENT DES DONNÉES ---
            df_b = cloud_conn.read(worksheet="Banque", ttl=0)
            df_f = cloud_conn.read(worksheet="Factures", ttl=0)
            
            try:
                row_ent = df_b[df_b["Nom Roblox"] == nom_banque]
                solde_ent = float(str(row_ent["Solde"].values[0]).replace('$', '').replace(',', '').strip())
            except:
                solde_ent = 0

            # --- MISE EN PAGE EN COLONNES ---
            col_virement, col_aperçu = st.columns([1.3, 1])

            with col_virement:
                st.markdown(f"### 💸 Virement {label_ent}")
                
                with st.form("form_virement_v8", border=True):
                    st.info(f"🏢 **Compte :** {nom_banque}  \n💰 **Solde :** {solde_ent:,.0f} $".replace(",", " "))
                    
                    destinataire = st.selectbox("Destinataire", ["---"] + sorted(df_b["Nom Roblox"].dropna().unique().tolist()), key="k_dest_v8")
                    montant_v = st.number_input("Montant ($)", min_value=0, step=500, key="k_mnt_v8")
                    motif_v = st.text_input("Motif", placeholder="Ex: Salaire, Frais CDC...", key="k_mot_v8")
                    
                    submit_virement = st.form_submit_button("🚀 VALIDER LE TRANSFERT", use_container_width=True, type="primary")

                if submit_virement:
                    if destinataire == "---" or montant_v <= 0:
                        st.error("❌ Formulaire invalide.")
                    elif solde_ent < montant_v:
                        st.error(f"⚠️ Solde insuffisant ! (Manque {montant_v - solde_ent}$)")
                    else:
                        with st.spinner("Transfert en cours..."):
                            try:
                                idx_exp = df_b[df_b["Nom Roblox"] == nom_banque].index[0]
                                idx_dest = df_b[df_b["Nom Roblox"] == destinataire].index[0]
                                solde_dest_raw = float(str(df_b.at[idx_dest, "Solde"]).replace('$', '').replace(',', '').strip() or 0)
                                
                                # Update soldes
                                df_b.at[idx_exp, "Solde"] = solde_ent - montant_v
                                df_b.at[idx_dest, "Solde"] = solde_dest_raw + montant_v
                                
                                cloud_conn.update(worksheet="Banque", data=df_b)
                                
                                st.balloons()
                                st.success(f"✅ Virement de {montant_v}$ effectué depuis {nom_banque} !")
                                time.sleep(2)
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erreur : {e}")

                st.markdown("#### 📄 Revenus récents")
                # Filtre dynamique selon l'entreprise
                emetteur_filtre = "CDC" if nom_banque == "CDCB" else "AFCM"
                historique = df_f[(df_f["Emetteur"] == emetteur_filtre) & (df_f["Statut"] == "PAYÉ")].sort_index(ascending=False).head(5)
                if not historique.empty:
                    st.dataframe(historique[["Date_Emission", "Cible", "Montant"]], use_container_width=True, hide_index=True)

            with col_aperçu:
                st.markdown("### 🖼️ Reçu de Transaction")
                date_t = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                # Ticket adaptatif
                ticket_bank_html = f"""
                <div style='border: 2px solid #2e7d32; padding: 20px; background-color: #f1f8e9; color: #1b5e20; font-family: "Courier New", monospace; border-radius: 10px;'>
                    <div style='text-align:center;'>
                        <h2 style='margin:0;'>BANQUE {label_ent}</h2>
                        <small>TRANSACTION SÉCURISÉE</small>
                    </div>
                    <hr style='border: 0.5px dashed #2e7d32; margin: 15px 0;'>
                    <p style='font-size:0.9em;'><strong>COMPTE :</strong> {nom_banque}</p>
                    <p style='font-size:0.9em;'><strong>RÉF :</strong> TR-{random.randint(100000, 999999)}</p>
                    <p style='font-size:0.9em;'><strong>DATE :</strong> {date_t}</p>
                    <p style='font-size:0.9em;'><strong>STATUT :</strong> EN ATTENTE</p>
                    <p style='font-size:0.7em; color: #666; margin-top:20px;'>Détails disponibles après validation.</p>
                </div>
                """
                st.components.v1.html(ticket_bank_html, height=450)

            if st.button("🔒 SE DÉCONNECTER", use_container_width=True):
                st.session_state.auth_banque = False
                st.rerun()

except ValueError:
    pass
# ======================================================================================
# 8. PIED DE PAGE
# ======================================================================================
st.divider()
st.caption(f"Terminal Fédéral RCRP FR | Opérationnel | © 2026 République de Rensselaer")
