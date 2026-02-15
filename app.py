import streamlit as st
import pandas as pd
import time  # <--- AJOUTE CETTE LIGNE ICI
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
# Maintenant GSheetsConnection est bien reconnu grâce à l'import en haut
cloud_conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def fetch_database():
    try:
        df_bank = cloud_conn.read(worksheet="Banque").dropna(how='all').fillna("")
        df_immat = cloud_conn.read(worksheet="Copie de Immatriculations").dropna(how='all').fillna("")
        df_pts = cloud_conn.read(worksheet="Points Permis").dropna(how='all').fillna("")
        return df_bank, df_immat, df_pts
    except Exception as e:
        st.error(f"Erreur de liaison : {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_b, df_i, df_p = fetch_database()
# ======================================================================================
# 3. ÉTAT DE LA SESSION & PARAMÈTRES
# ======================================================================================
if "user_auth" not in st.session_state: st.session_state.user_auth = None
if "audit_logs" not in st.session_state: st.session_state.audit_logs = []

# ======================================================================================
# CONFIGURATION ET FONCTIONS TECHNIQUES (À METTRE EN HAUT)
# ======================================================================================

PRIME_JOB = {
    "Sans-Emploi": 0,
    "Agent RCT": 2000,
    "Averis": 2000,
    "Police": 3000,
    "Staff": 4000,
    "Service Public": 1000,
    "Entreprise Privée": 500
}

def traiter_paiement_prime(target_name, metier, montant, df_b, cloud_conn):
    """Gère le prélèvement sur l'employeur et l'ajout sur l'employé"""
    source_compte = None
    if "Averis" in metier:
        source_compte = "Moune2010"
    elif "Agent RCT" in metier:
        source_compte = "une10000"
    
    if source_compte:
        try:
            # --- PRÉLÈVEMENT SUR L'EMPLOYEUR ---
            idx_source = df_b[df_b["Nom Roblox"] == source_compte].index[0]
            df_b.at[idx_source, "Solde"] -= montant
            
            # --- AJOUT SUR L'EMPLOYÉ ---
            idx_target = df_b[df_b["Nom Roblox"] == target_name].index[0]
            df_b.at[idx_target, "Solde"] += montant
            
            # Sauvegarde globale
            cloud_conn.update(worksheet="Banque", data=df_b)
            return True, f"✅ Prime de {montant}$ versée (Payé par {source_compte})"
        except Exception as e:
            return False, f"❌ Erreur lors du virement : {e}"
    else:
        return False, "⚠️ Aucun employeur configuré pour prélever cette prime (Averis ou RCT uniquement)."

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
        st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1471115849631793256/Capture_decran_2025-12-01_a_21.03.31.png?ex=698dc2e6&is=698c7166&hm=ddabf40f0fad8139ed693e02221341fe14e01ad84b35317af6a101c62986b79b&", use_container_width=True)
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

# --- BOUTON SYNCHRO ---
        if st.button("🔄 FORCER SYNCHRO", use_container_width=True):
            st.cache_data.clear()
            record_log(st.session_state.user_auth, "Synchro Cloud Manuelle")
            st.rerun()

        if st.button("🚪 DÉCONNEXION", use_container_width=True):
            # 1. On enregistre le log avant de tout couper
            try:
                record_log(st.session_state.user_auth, "Déconnexion")
            except:
                pass
            
            # 2. On vide la session côté serveur
            st.cache_data.clear()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            # 3. LE HACK RADICAL : On force le navigateur à recharger la page proprement
            # Cela va réinitialiser l'URL et vider le cache visuel
            components.html("""
                <script>
                    window.parent.location.reload();
                </script>
            """, height=0)
            
            # 4. Sécurité pour arrêter le script Streamlit
            st.stop()
            
        st.divider()
        st.caption("📜 JOURNAUX D'AUDIT (SESSION)")
        # On vérifie si audit_logs existe pour éviter une erreur après le del
        if "audit_logs" in st.session_state:
            for log in reversed(st.session_state.audit_logs[-8:]):
                st.caption(log)
# ======================================================================================
# 5. LOCKSCREEN (CONNEXION) - UNITÉ FÉDÉRALE DE RENSSELAER
# ======================================================================================
if st.session_state.user_auth is None:
    # --- CONFIGURATION INTERFACE ---
    st.markdown("""
        <style>
            [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none; }
            [data-testid="stStatusWidget"] { display: none; }
            .block-container { padding-top: 2rem !important; }
            
            /* ON SUPPRIME L'ENCADRÉ GRIS ET L'OMBRE DE L'IFRAME */
            iframe { 
                border: none !important; 
                box-shadow: none !important; 
                background: transparent !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # 1. CALCUL DU MOMENT (UTC+1)
    from datetime import datetime, timedelta, timezone
    t_now_lock = datetime.now(timezone.utc) + timedelta(hours=1)
    h_lock = t_now_lock.hour

    if 5 <= h_lock < 18:
        salut_complet = "Bonjour☀️"
        pattern_style = "background-color: #87CEEB; background-image: conic-gradient(from 200deg at 85% 10%, transparent 0deg, rgba(255,255,255,0.4) 15deg, transparent 30deg, rgba(255,223,137,0.5) 45deg, transparent 60deg, rgba(255,255,255,0.4) 75deg, transparent 90deg), radial-gradient(circle at 85% 10%, #FFF9E3 0%, #FFD700 15%, rgba(255,215,0,0.4) 30%, transparent 60%);"
        t_color = "#1E1E1E"
        glow = "0 0 30px rgba(255, 255, 255, 1), 0 0 60px rgba(255, 200, 0, 0.6)"
    else:
        salut_complet = "Bonsoir🌕"
        pattern_style = "background-color: #05070a; background-image: radial-gradient(1px 1px at 25% 35%, white, transparent), radial-gradient(1px 1px at 50% 10%, white, transparent); background-size: 150px 150px, 200px 200px;"
        t_color = "#FFFFFF"
        glow = "0 0 40px rgba(255,255,255,0.9), 0 0 80px rgba(255,255,255,0.4)"

    # --- LE BLOC MONOLITHIQUE (Haut + Bas soudés) ---
    import streamlit.components.v1 as components
    components.html(f"""
        <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; width: 100%; border-radius: 25px; overflow: hidden; border: none;">
            
            <div style="text-align: center; padding: 70px 20px; color: {t_color}; {pattern_style} height: 350px; box-sizing: border-box;">
                <h1 style="font-size: 5.5em; margin: 0; font-weight: 900; letter-spacing: -3px; text-shadow: {glow}; line-height: 1.1;">
                    {salut_complet}
                </h1>
                <p style="font-size: 1.1em; opacity: 0.8; letter-spacing: 5px; font-weight: bold; text-transform: uppercase; margin: 25px 0;">
                    Unité Fédérale de Rensselaer
                </p>
                <div id="clock" style="font-size: 3.8em; letter-spacing: 3px; font-weight: bold; border-top: 2px solid {t_color}33; display: inline-block; padding-top: 10px;">
                    00:00:00
                </div>
            </div>

            <div style="background-color: #1a1c23; border-left: 10px solid #ff4b4b; padding: 45px 20px; text-align: center; color: white;">
                <div style="font-size: 45px; margin-bottom: 15px;">👤</div>
                <h2 style="margin: 0; font-size: 2em; letter-spacing: 2px;">🏛️ RÉPUBLIQUE DE RENSSELAER</h2>
                <p style="margin: 5px 0 25px 0; font-size: 1em; opacity: 0.7; text-transform: uppercase; letter-spacing: 1px;">Terminal Fédéral d'Opérations Nationales</p>
                <div style="width: 70%; height: 1px; background: rgba(255,255,255,0.1); margin: 0 auto 20px auto;"></div>
                <small style="opacity: 0.5; font-size: 0.8em;">VERSION 14.6.0 | SÉCURISÉ PAR PROTOCOLE RCRP-OS</small>
            </div>

        </div>

        <script>
            function update() {{
                const now = new Date();
                const h = String(now.getHours()).padStart(2, '0');
                const m = String(now.getMinutes()).padStart(2, '0');
                const s = String(now.getSeconds()).padStart(2, '0');
                document.getElementById('clock').textContent = h + ":" + m + ":" + s;
            }}
            setInterval(update, 1000);
            update();
        </script>
    """, height=650) # Hauteur totale ajustée
    
    st.write("")
    st.warning("⚠️ **AVERTISSEMENT :** Toute action effectuée sur ce terminal est enregistrée.")
    st.write("---")

    # 3. COLONNES D'ACCÈS (Inchangé)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 👥 CIVIL")
        nom_civil = st.text_input("Ecrivez quelque chose (Optionnel)", placeholder="Ex: Liberté, Egalité, Renault Coupé.", key="input_civil_align")
        if st.button("ACCÉDER AU TERMINAL", key="l_civ_f", use_container_width=True):
            st.session_state.user_auth = "Civil"
            st.rerun()
    with c2:
        st.markdown("### 👨‍🔧 AGENT RCT")
        login_rct = st.text_input("Identifiant Agent", placeholder="Code RCT", type="password", key="l_rct_ff")
        if st.button("AUTHENTIFICATION RCT", key="b_rct_f", use_container_width=True):
            if login_rct == KEY_RCT:
                st.session_state.user_auth = "RCT"
                st.rerun()
            else: st.error("Clé invalide.")
    with c3:
        st.markdown("### 🛡️👮‍♂️ Portail POLSTA(RIS)")
        login_staff = st.text_input("Clé Maîtresse", placeholder="Code POLSTA(RIS)", type="password", key="l_st_ff")
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
# 6. MODULE : DOSSIER CITOYEN UNIFIÉ (VERSION FINALE & COMPLETE)
# ======================================================================================

with st.container():
    # --- A. TABLEAU PUBLIC DES AVIS DE RECHERCHE ---
    recherches_publics = df_b[df_b["Statut"].str.upper().str.contains("RECHERCHÉ", na=False)]
    
    if not recherches_publics.empty:
        st.markdown("<h3 style='color: #ff4b4b; margin-bottom: 15px;'>🚨 AVIS DE RECHERCHE EN COURS</h3>", unsafe_allow_html=True)
        for _, crim in recherches_publics.iterrows():
            motif = crim.get('Motif Recherche', 'Motif non spécifié').upper()
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; background-color: #8B0000; padding: 12px 20px; border-radius: 8px; border: 3px solid #ff0000; margin-bottom: 10px; animation: blinker_universal 2s linear infinite;">
                    <div style="color: #ffffff !important; font-weight: bold; font-size: 1.3em;">👤 {crim['Nom Roblox']}</div>
                    <div style="color: #ffcccc !important; font-weight: 700; font-size: 0.9em;">MOTIF : {motif}</div>
                </div>
                <style> @keyframes blinker_universal {{ 50% {{ background-color: #ff4b4b; border-color: #8B0000; }} }} </style>
            """, unsafe_allow_html=True)
        st.divider()

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

        # 2. Alerte Permis Invalide (Orange Flashy)
        # Tu peux aussi l'ajouter si tu veux que ce soit aussi visible
        try:
            pts_permis = df_p[df_p["Nom Roblox"] == target].iloc[0]["PTS"]
            if pts_permis <= 0:
                st.markdown(f"""
                    <div style="background-color: #ff9800; padding: 20px; border-radius: 10px; border: 4px solid #fb8c00; color: black; text-align: center; margin-bottom: 10px;">
                        <h2 style="margin:0;">⚠️ PERMIS RÉVOQUÉ (0 PTS) ⚠️</h2>
                        <p style="font-size: 18px;">L'individu <b>{target}</b> circule sans points valides.</p>
                    </div>
                """, unsafe_allow_html=True)
        except: pass
        # 2. Alerte Dette en retard (Orange)
        maintenant = datetime.now()
        try:
            df_f_check = cloud_conn.read(worksheet="Factures").fillna("")
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
            p_data = df_p[df_p["Nom Roblox"] == target]
            if not p_data.empty:
                pts = int(p_data.iloc[0]["PTS"])
                
                # Filigrane ultra-discret à droite
                st.markdown("""
                    <style>
                    .wm-p { position: absolute; right: -20px; top: 10px; font-size: 16px; 
                            color: rgba(0,0,0,0.1); transform: rotate(-10deg); font-weight: bold; }
                    </style>
                    <div class="wm-p">🚙 PERMIS OFFICIEL 🪪</div>
                """, unsafe_allow_html=True)

                st.metric("POINTS PERMIS", f"{pts}/25")
                color = "green" if pts > 0 else "red"
                st.markdown(f"Statut : <b style='color:{color};'>{'VALIDE' if pts > 0 else 'SUSPENDU'}</b>", unsafe_allow_html=True)
                
                if st.session_state.user_auth in ["Staff", "Admin"] and pts <= 0:
                    if st.button("🔓 Rendre le permis", key=f"res_{target}", use_container_width=True):
                        df_p.loc[df_p["Nom Roblox"] == target, "PTS"] = 25
                        cloud_conn.update(worksheet="Points Permis", data=df_p)
                        st.success("Permis rendu !")
                        time.sleep(1)
                        st.rerun()
            else: 
                st.info("Aucun permis trouvé.")

        # ---------------- COLONNE 2 : BANQUE & PAIE ----------------
        with col2:
            if not citoyen_info.empty:
                # Filigrane ultra-discret à droite
                st.markdown("""
                    <style>
                    .wm-b { position: absolute; right: -20px; top: 10px; font-size: 16px; 
                            color: rgba(0,0,0,0.1); transform: rotate(-10deg); font-weight: bold; }
                    </style>
                    <div class="wm-b">💳 DOSSIER BANCAIRE 💵</div>
                """, unsafe_allow_html=True)

                st.metric("SOLDE BANCAIRE", f"{citoyen_info.iloc[0]['Solde']}$")
                job_raw = str(citoyen_info.iloc[0]['Emploiement'])
                st.write(f"🏢 Métier : **{job_raw}**")
                
                # ... Ton code pour l'expander de paie continue ici ...
                # ... reste du code paie ...
                # ... (le reste de ton code pour le métier et la paie)
                job_raw = str(citoyen_info.iloc[0]['Emploiement'])
                st.write(f"🏢 Métier : **{job_raw}**")

                # --- CALCULATEUR DE PAIE (VERSION STAFF & PRIMES) ---
                with st.expander("💳 Détails de ma prochaine paie", expanded=False):
                    # 1. Calcul des minutes (via Logs)
                    m_pol, m_rct = 0, 0
                    try:
                        logs = df_admin[(df_admin["nom"] == target) & (df_admin["statut"] == "Validé")]
                        for _, r in logs.iterrows():
                            t_debut = pd.to_datetime(r["début"], dayfirst=True)
                            t_fin = pd.to_datetime(r["fin"], dayfirst=True)
                            diff = (t_fin - t_debut).total_seconds() / 60
                            if "POL" in str(r["job"]).upper(): m_pol += diff
                            elif "RCT" in str(r["job"]).upper(): m_rct += diff
                    except: pass

                    # 2. Détection des Primes
                    ratio_pol = min(m_pol/1200, 1.0)
                    ratio_rct = min(m_rct/1200, 1.0)
                    
                    p_pol = int(3000 * ratio_pol) if "police" in job_raw.lower() else 0
                    p_rct = int(2000 * ratio_rct) if "agent rct" in job_raw.lower() else 0
                    p_staff = 4000 if "staff" in job_raw.lower() else 0
                    p_extra = 0 
                    
                    # Taxes Véhicules (Trio RCT)
                    mes_v = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
                    count_rct = len(mes_v[mes_v["Assurance"].str.contains("RCT", na=False, case=False)])
                    is_trio = count_rct >= 3
                    taxe_v = 200 if is_trio else (len(mes_v) * 150)

                    # --- CALCUL DU NET (BASE 15K + TOUS LES BONUS) ---
                    net = 15000 + p_pol + p_rct + p_staff + p_extra - taxe_v

                    # 3. Affichage visuel
                    c_cred, c_deb = st.columns(2)
                    
                    with c_cred:
                        st.markdown("<div style='color: #4CAF50; font-weight:bold; margin-bottom:5px;'>📥 REVENUS</div>", unsafe_allow_html=True)
                        st.markdown(f"➕ **Base Civile** : `15,000$`")
                        if p_staff > 0: st.markdown(f"⭐ **Prime Staff** : `{p_staff}$`")
                        if "police" in job_raw.lower():
                            st.markdown(f"👮 **Prime Police** : `{p_pol}$`")
                            st.progress(ratio_pol, text=f"{int(m_pol/60)}h / 20h")
                        if "agent rct" in job_raw.lower():
                            st.markdown(f"👷‍♂️ **Prime RCT** : `{p_rct}$`")
                            st.progress(ratio_rct, text=f"{int(m_rct/60)}h / 20h")
                        if p_extra > 0: st.markdown(f"🎁 **Bonus** : `{p_extra}$`")

                    with c_deb:
                        st.markdown("<div style='color: #E53935; font-weight:bold; margin-bottom:5px;'>📤 DÉPENSES</div>", unsafe_allow_html=True)
                        if len(mes_v) > 0:
                            label_taxe = "Offre Trio RCT ✅" if is_trio else f"{len(mes_v)} véhicule(s)"
                            st.markdown(f"🚗 **Assurances** : `{taxe_v}$`")
                            st.caption(label_taxe)
                        else:
                            st.markdown("🚗 **Assurances** : `0$`")

                    st.markdown("---")
                    st.markdown(f"""
                        <div style="background-color: #1E1E1E; padding: 15px; border-radius: 8px; border-left: 5px solid #4CAF50; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 1.1em; color: #bbb;">NET ESTIMÉ</span>
                            <span style="font-size: 1.5em; font-weight: bold; color: #fff;">{int(net):,}$</span>
                        </div>
                    """, unsafe_allow_html=True)

                # --- MODIFICATION MÉTIER (STAFF) ---
                if st.session_state.user_auth in ["Staff", "Admin"]:
                    if st.button("✏️ Modifier Métier", key=f"edit_{target}", use_container_width=True):
                        st.session_state[f"mode_{target}"] = not st.session_state.get(f"mode_{target}", False)
                    
                    if st.session_state.get(f"mode_{target}", False):
                        opts = ["Sans-Emploi", "Agent RCT", "Averis", "Police", "Staff", "Service Public"]
                        cur = [j.strip() for j in job_raw.split("/") if j.strip() in opts]
                        new_m = st.multiselect("Nouveau :", opts, default=cur)
                        if st.button("💾 Sauver"):
                            txt = " / ".join(new_m) if new_m else "Sans-Emploi"
                            df_b.loc[df_b["Nom Roblox"] == target, "Emploiement"] = txt
                            cloud_conn.update(worksheet="Banque", data=df_b)
                            st.success("Enregistré !")
                            st.session_state[f"mode_{target}"] = False
                            st.rerun()
# ---------------- COLONNE 3 : ARCHIVES & REMBOURSEMENT ----------------
        with col3:
            st.markdown("### 📁 ARCHIVES")
            try:
                # On recharge les factures pour être à jour
                df_f_check = cloud_conn.read(worksheet="Factures").fillna("")
                archives = df_f_check[(df_f_check["Cible"] == target) & (df_f_check["Statut"] == "PAYÉ")]
                
                if not archives.empty:
                    # Bouton déroulant pour voir l'historique
                    with st.expander(f"👁️ Voir l'historique ({len(archives)} factures)"):
                        for _, f in archives.iterrows():
                            # --- AFFICHAGE DU PETIT TICKET D'ARCHIVE ---
                            st.markdown(f"""
                            <div style="border: 1px solid #000; padding: 10px; background: #f9f9f9; color: black; margin-bottom: 8px; border-left: 5px solid green;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.8em;">
                                    <b>REF: #{f['ID']}</b>
                                    <b style="color: green;">ACQUITTÉE ✔</b>
                                </div>
                                <hr style="margin: 5px 0; border-top: 1px dashed #000;">
                                <div style="font-size: 0.9em;">
                                    <b>MOTIF :</b> {f['Motif']}<br>
                                    <b>MONTANT :</b> {f['Montant']}$<br>
                                    <b>POINTS :</b> {f.get('Points', 0)}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # --- OPTION REMBOURSEMENT (STAFF/ADMIN) ---
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
                    st.info("Aucun paiement archivé.")
                    
            except Exception as e:
                st.error(f"Erreur chargement archives : {e}")
# ======================================================================================
# 7. LOGIQUE DES ONGLETS (CORRIGÉE)
# ======================================================================================

# ======================================================================================
# NOUVEAU : SYSTÈME DE PAIEMENT DES FACTURES (STYLE TICKET)
# ======================================================================================
df_all_f = cloud_conn.read(worksheet="Factures").fillna("")
mes_factures = df_all_f[(df_all_f["Cible"] == target) & (df_all_f["Statut"] == "EN ATTENTE")]

if not mes_factures.empty:
    st.error(f"⚠️ {len(mes_factures)} FACTURE(S) EN ATTENTE DE PAIEMENT")
    
    for _, fac in mes_factures.iterrows():
        # 1. CALCUL DU TIMER
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
            timer_info = "⌛ Délai : 24 heures"; t_color = "#555"

        # 2. IDENTIFICATION ÉMETTEUR
        emetteur_label = str(fac.get('Emetteur', 'INCONNU'))
        if "POL" in emetteur_label.upper(): prefix_name = "POLICE NATIONALE"
        elif "AVERIS" in emetteur_label.upper(): prefix_name = "SERVICES AVERIS"
        else: prefix_name = "RÉSEAU RCT"

        # 3. AFFICHAGE DU TICKET
        agent_nom = fac.get('Agent_Signataire', 'Officier RCT')
        st.markdown(f"""
        <div style="border: 2px solid #000; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; margin-bottom: 5px; box-shadow: 6px 6px 0px #000;">
            <center><b style="font-size:1.1em; text-decoration: underline;">FACTURE OFFICIELLE</b><br>
            <small>{prefix_name}</small></center>
            <hr style="border-top: 1px dashed #000; margin: 10px 0;">
            <div style="font-size: 0.9em; line-height: 1.2;">
                <b>RÉFÉRENCE :</b> #{fac['ID']}<br>
                <b>OFFICIER   :</b> {agent_nom}<br>
                <b>SERVICE   :</b> {emetteur_label}<br>
                <b>MOTIF     :</b> {fac['Motif']}<br>
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
        """, unsafe_allow_html=True)

        # 4. BOUTON DE PAIEMENT
        if st.button(f"💳 RÉGLER LA FACTURE #{fac['ID']}", key=f"pay_{fac['ID']}", use_container_width=True):
            try:
                idx_b = df_b[df_b["Nom Roblox"] == target].index[0]
                solde_actuel = float(str(df_b.at[idx_b, "Solde"]).replace('$', '').replace(',', ''))
                montant_facture = float(str(fac['Montant']).replace(',', ''))
                
                if solde_actuel >= montant_facture:
                    df_b.at[idx_b, "Solde"] = solde_actuel - montant_facture
                    
                    # --- REDIRECTION DES FONDS ---
                    if "RCT" in emetteur_label.upper():
                        idx_p = df_b[df_b["Nom Roblox"] == "une10000"].index[0]
                        df_b.at[idx_p, "Solde"] = float(str(df_b.at[idx_p, "Solde"]).replace('$', '')) + montant_facture
                    elif "AVERIS" in emetteur_label.upper():
                        # Argent envoyé à Moune2010 pour Averis
                        idx_p = df_b[df_b["Nom Roblox"] == "Moune2010"].index[0]
                        df_b.at[idx_p, "Solde"] = float(str(df_b.at[idx_p, "Solde"]).replace('$', '')) + montant_facture
                    
                    df_all_f.loc[df_all_f["ID"] == fac["ID"], "Statut"] = "PAYÉ"
                    cloud_conn.update(worksheet="Banque", data=df_b)
                    cloud_conn.update(worksheet="Factures", data=df_all_f)
                    
                    st.success("✅ Facture payée !")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Solde insuffisant.")
            except Exception as e:
                st.error(f"Erreur paiement : {e}")

        # 5. BOUTON ANNULER (Staff/Admin)
        if st.session_state.user_auth in ["Staff", "Admin", "POLSTA"]:
            if st.button(f"🗑️ ANNULER LA FACTURE #{fac['ID']}", key=f"admin_del_{fac['ID']}", use_container_width=True):
                try:
                    with st.spinner("Annulation..."):
                        df_f_sync = cloud_conn.read(worksheet="Factures")
                        df_p_sync = cloud_conn.read(worksheet="Points Permis")
                        
                        pts_a_rendre = fac.get('Points', 0)
                        
                        if pts_a_rendre and str(pts_a_rendre).isdigit() and int(pts_a_rendre) > 0:
                            try:
                                idx_p = df_p_sync[df_p_sync["Nom Roblox"] == fac["Cible"]].index[0]
                                current_pts = int(df_p_sync.at[idx_p, "PTS"])
                                df_p_sync.at[idx_p, "PTS"] = min(12, current_pts + int(pts_a_rendre))
                                cloud_conn.update(worksheet="Points Permis", data=df_p_sync)
                                st.info(f"🔄 {pts_a_rendre} points restitués.")
                            except: pass

                        df_f_sync.loc[df_f_sync["ID"] == fac["ID"], "Statut"] = "ANNULÉ"
                        cloud_conn.update(worksheet="Factures", data=df_f_sync)

                        qui_annule = st.session_state.get('staff_name', 'Agent Staff')
                        record_log(qui_annule, f"Annulation facture #{fac['ID']} de {fac['Cible']}")
                        
                        st.warning(f"Facture #{fac['ID']} annulée.")
                        st.cache_data.clear()
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur annulation : {e}")

st.write("---")

# --- SECTION VÉHICULES UNIFORMISÉE ---
st.write("### 🚗 VÉHICULES ENREGISTRÉS")
v_data = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]

if not v_data.empty:
    v_cols = st.columns(3)
    for i, (_, veh) in enumerate(v_data.iterrows()):
        with v_cols[i % 3]:
            # --- RÉCUPÉRATION TECHNIQUE DE LA DATE (SANS COUPURE) ---
            date_display = str(veh.get('Horodateur', 'Non spécifiée'))

            # --- LOGIQUE DE SÉCURITÉ ---
            assu = str(veh.get('Assurance', '')).upper()
            role = st.session_state.user_auth
            
            color = "green"
            status_txt = "✅ VÉHICULE EN RÈGLE"
            
            if role == "RCT":
                if "RCT" in assu:
                    color = "green"
                    status_txt = "✅ ASSURÉ RCT"
                elif "AVERIS" in assu:
                    color = "#E67E22"
                    status_txt = "⚠️ ATTENTION : ASSURÉ AVERIS"
                else:
                    color = "#d32f2f"
                    status_txt = "🚨 DANGER : NON-ASSURÉ"

            # --- DESIGN TITRE DE CIRCULATION ---
            st.markdown(f"""
            <div style="border: 2px solid black; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; line-height: 1.2;">
                <center><b>TITRE DE CIRCULATION</b><br><small>RÉPUBLIQUE DE RENSSERLAER</small></center>
                <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                <b>DATE :</b> {date_display}<br>
                <b>NOM :</b> {target}<br>
                <b>MODÈLE :</b> {veh.get('Marque du véhicule', '')}<br>
                <b>PLAQUE :</b> <span style="border: 1px solid black; padding: 0 3px;">{veh.get('Numéro de la plaque', '')}</span><br>
                <b>ASSURANCE :</b> {veh.get('Assurance', '')}
                <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                <div style="text-align: center; color: {color}; font-weight: bold; font-size: 0.8em;">
                    {status_txt}<br>
                    <small>Par le Terminal National</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
                                        
            with st.expander("🗑️ Radier"):
                r_cod_check = st.text_input("Code Secret", type="password", key=f"rad_input_{veh['Numéro de la plaque']}_{i}")
                if st.button("CONFIRMER", key=f"btn_confirm_{veh['Numéro de la plaque']}_{i}", use_container_width=True):
                    if str(r_cod_check) == str(veh.get('CODE', '')) or st.session_state.user_auth == "Staff":
                        try:
                            df_all_immat = cloud_conn.read(worksheet="Copie de Immatriculations")
                            df_updated = df_all_immat[df_all_immat["Numéro de la plaque"] != veh['Numéro de la plaque']]
                            cloud_conn.update(worksheet="Copie de Immatriculations", data=df_updated)
                            st.cache_data.clear()
                            st.success("Radié !")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur : {e}")
                    else:
                        st.error("Code incorrect")
else:
    st.info("Aucun véhicule trouvé.")
# ======================================================================================
# 7. LOGIQUE DES ONGLETS (CORRIGÉE)
# ======================================================================================
tab_labels = ["🚗 IMMATRICULATION"]
if st.session_state.user_auth in ["RCT", "Staff"]: tab_labels.append("👮 SERVICES AGENT")
if st.session_state.user_auth == "Staff": tab_labels.append("🛠️ ADMINISTRATION")

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
            f_model = st.text_input("Marque", key="k_model_v7")
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
                except: pass

            # --- CALCUL DU TOTAL + OFFRE TRIO RCT ---
            taxe_gouv = 175
            taxe_assu = 130 if "AVERIS" in f_assu else (150 if "RCT" in f_assu else 0)
            
            if "RCT" in f_assu and f_owner != "---":
                nb_vehicules = len(df_i[df_i["Nom d'utilisateur ROBLOX"] == f_owner])
                if nb_vehicules >= 2:
                    taxe_assu = 0
                    st.success(f"🎁 OFFRE TRIO ACTIVÉE")

            total_bill = taxe_gouv + taxe_assu + val_taxe_jeune
            
            # --- BOUTON DE VALIDATION (LOGIQUE RÉELLE) ---
            if st.button(f"S'ACQUITTER DE {total_bill}$ ET ENREGISTRER", use_container_width=True, key="btn_pay_final", type="primary"):
                if f_owner == "---" or not f_model or not f_plate or not f_code:
                    st.error("⚠️ Formulaire incomplet ! Remplis tous les champs.")
                else:
                    try:
                        with st.spinner("Paiement et enregistrement en cours..."):
                            # 1. Calcul du solde
                            idx_user = df_b[df_b["Nom Roblox"] == f_owner].index[0]
                            solde_actuel = float(str(df_b.at[idx_user, "Solde"]).replace('$', '').replace(',', ''))
                            
                            if solde_actuel < total_bill:
                                st.error(f"❌ Solde insuffisant ! (Solde: {solde_actuel}$)")
                            else:
                                # 2. Retrait de l'argent
                                df_b.at[idx_user, "Solde"] = solde_actuel - total_bill
                                
                                # 3. Création de la ligne
                                nouvelle_immat = {
                                    "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                    "Nom d'utilisateur ROBLOX": f_owner,
                                    "Marque du véhicule": f_model,
                                    "Numéro de la plaque": f_plate,
                                    "Assurance": f_assu.split(" (")[0],
                                    "CODE": f_code,
                                    "Points": 25
                                }

                                # Ajout au tableau local
                                new_df_i = pd.concat([df_i, pd.DataFrame([nouvelle_immat])], ignore_index=True)
                                
                                # 4. Envoi au Google Sheets
                                cloud_conn.update(worksheet="Banque", data=df_b)
                                cloud_conn.update(worksheet="Copie de Immatriculations", data=new_df_i)
                                
                                # 5. Confirmation
                                st.balloons()
                                st.success(f"""
                                ### ✅ IMMATRICULATION RÉUSSIE !
                                ---
                                * **Propriétaire :** {f_owner}
                                * **Véhicule :** {f_model}
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
        marque_v = f_model if f_model else "---"
        plaque_v = f_plate if f_plate else "---"
        nom_assu = f_assu if f_assu != "Aucune" else "NON ASSURÉ"

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
                <p><strong>MARQUE :</strong> {marque_v}</p>
                <p><strong>PLAQUE :</strong> <span style='border:1px solid #333; padding:2px 6px; background:#eee;'>{plaque_v}</span></p>
                <p><strong>ASSURANCE :</strong> {nom_assu}</p>
            </div>
            <div style='font-size: 0.8em;'>
                <p style='display:flex; justify-content:space-between; margin:2px 0;'><span>Immatriculation :</span><span>175$</span></p>
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
# --- ONGLET 2 : SERVICES AGENTS ---
if len(tabs) > 1:
    with tabs[1]:
        roles_autorises = ["RCT", "Averis", "Police", "Staff"]
        if any(r in st.session_state.user_auth for r in roles_autorises):
            
            # --- 1. AUTHENTIFICATION & POINTAGE ---
            with st.container(border=True):
                c_auth, c_stats = st.columns([1, 2.5])
                
                with c_auth:
                    agent_code_saisi = st.text_input("🔑 Code Agent", type="password", key="main_agent_auth")
                
                agent_identifie = None
                en_service = False
                
                if agent_code_saisi:
                    # Nettoyage des données
                    df_b.columns = df_b.columns.str.strip()
                    df_b["Code_Clean"] = df_b["Code"].astype(str).apply(lambda x: x.strip().split('.')[0])
                    res_agent = df_b[df_b["Code_Clean"] == agent_code_saisi.strip()]
                    
                    if not res_agent.empty:
                        agent_identifie = res_agent.iloc[0]["Nom Roblox"]
                        
                        # Lecture Clock
                        df_clock = cloud_conn.read(worksheet="Clock", ttl=0).fillna("")
                        df_clock.columns = df_clock.columns.str.strip().str.lower()
                        session_active = df_clock[(df_clock["nom"] == agent_identifie) & (df_clock["statut"] == "en cours")]
                        en_service = not session_active.empty

                        with c_stats:
                            st.markdown(f"### 🎖️ Agent : {agent_identifie}")
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

                        # --- LOGIQUE DE JOB AUTO ---
                        job_auto = "POLSTA" if st.session_state.user_auth == "Staff" else "RCT"
                        if "Averis" in st.session_state.user_auth: job_auto = "Averis"
                        
                        if not en_service:
                            st.info(f"💡 **Information :** Vous êtes connecté en tant que **{job_auto}**.")
                            if st.button(f"▶️ DÉBUT DE SERVICE ({job_auto})", use_container_width=True, type="primary"):
                                h_deb = datetime.now(timezone(timedelta(hours=1))).strftime("%d/%m/%Y %H:%M:%S")
                                new_row = pd.DataFrame([{"nom": agent_identifie, "action": "SERVICE", "job": job_auto, "début": h_deb, "fin": "", "statut": "en cours"}])
                                cloud_conn.update(worksheet="Clock", data=pd.concat([df_clock, new_row], ignore_index=True))
                                st.rerun()
                        else:
                            st.warning(f"🚨 **Information :** Session **{job_auto}** en cours.")
                            if st.button(f"⏹️ FIN DE SERVICE ({job_auto})", use_container_width=True):
                                h_fin = datetime.now(timezone(timedelta(hours=1))).strftime("%d/%m/%Y %H:%M:%S")
                                df_clock.at[session_active.index[-1], "fin"] = h_fin
                                df_clock.at[session_active.index[-1], "statut"] = "à valider"
                                cloud_conn.update(worksheet="Clock", data=df_clock)
                                st.success(f"✅ Session {job_auto} enregistrée !")
                                time.sleep(1)
                                st.rerun()
                    else:
                        st.error("❌ Code Agent Invalide")
        # --- 2. RECHERCHE & MANDATS ---
        st.markdown("### 🔍 MANDATS & RECHERCHE")
        
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

        # --- 3. INTERVENTION SUR CITOYEN (BLOC COMPLET) ---
        st.divider()
        if target == "---":
            st.warning("⚠️ Sélectionnez un citoyen en haut de la page pour ouvrir le module d'intervention.")
        else:
            # Sécurité : On vérifie si l'agent est bien identifié par son code
            if not agent_identifie:
                # S'il n'est pas identifié, on ne montre RIEN ou juste un message simple
                st.info("🔒 Veuillez pointer votre code agent ci-dessus pour accéder à la facturation.")
            else:
                st.markdown(f"### ⚡ INTERVENTION : {target.upper()}")
                col_form, col_facture, col_vehicules = st.columns([1.2, 1, 1])

                # --- COLONNE 1 : FORMULAIRE D'ACTION ---
                with col_form:
                    with st.container(border=True):
                        # Choix de l'émetteur selon le grade
                        if st.session_state.user_auth == "Staff":
                            f_emetteur = st.selectbox("Émetteur", ["POLSTA", "Averis", "RCT"], key="em_ui")
                        elif "Averis" in st.session_state.user_auth:
                            f_emetteur = "Averis"
                            st.info(f"🏢 **Émetteur :** {f_emetteur}")
                        else:
                            f_emetteur = "RCT"
                            st.info(f"🏢 **Émetteur :** {f_emetteur}")
                        
                        f_val = st.number_input("Amende ($)", 0, 100000, 500, step=100)
                        
                        can_pull_points = (st.session_state.user_auth == "Staff" and f_emetteur == "POLSTA")
                        f_pts = st.slider("Retrait de points", 0, 12, 0, disabled=not can_pull_points)
                        
                        f_motif = st.text_area("Motif détaillé", key="mot_ui", placeholder="Décrivez l'infraction...")
                        
                        target_veh = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
                        f_plate = st.selectbox("Véhicule lié", ["AUCUN"] + target_veh["Numéro de la plaque"].tolist())
                        
                        # Bouton d'envoi
                        if st.button("🚨 ENVOYER FACTURE", use_container_width=True, type="primary"):
                            if f_motif:
                                with st.spinner("Transmission au central..."):
                                    import random
                                    df_all_f = cloud_conn.read(worksheet="Factures").fillna("")
                                    new_f = {
                                        "ID": random.randint(10000, 99999),
                                        "Cible": target,
                                        "Emetteur": f_emetteur,
                                        "Agent_Signataire": agent_identifie,
                                        "Montant": f_val,
                                        "Points": f_pts if can_pull_points else 0,
                                        "Motif": f"{f_motif} [{f_plate}]",
                                        "Statut": "EN ATTENTE",
                                        "Date_Emission": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                        "Date_Limite": (datetime.now() + timedelta(hours=24)).strftime("%d/%m/%Y %H:%M")
                                    }
                                    # Logique de retrait de points si applicable
                                    if f_pts > 0 and can_pull_points:
                                        try:
                                            idx_p = df_p[df_p["Nom Roblox"] == target].index[0]
                                            df_p.at[idx_p, "PTS"] = max(0, int(df_p.at[idx_p, "PTS"]) - f_pts)
                                            cloud_conn.update(worksheet="Points Permis", data=df_p)
                                        except: pass
                                        
                                    cloud_conn.update(worksheet="Factures", data=pd.concat([df_all_f, pd.DataFrame([new_f])], ignore_index=True))
                                    st.success(f"✅ PV enregistré par {agent_identifie}")
                                    time.sleep(1); st.rerun()
                            else:
                                st.error("❌ Le motif est obligatoire.")

                    # Alertes de vigilance sous le formulaire
                    # On récupère les infos du citoyen sélectionné
                    citoyen_info = df_b[df_b["Nom Roblox"] == target]
                    is_wanted = "RECHERCHÉ" in str(citoyen_info.iloc[0].get("Statut", "")).upper() if not citoyen_info.empty else False
                    motif_recherche = citoyen_info.iloc[0].get("Motif Recherche", "Non spécifié") if is_wanted else ""
                    
                    df_check_f = cloud_conn.read(worksheet="Factures").fillna("")
                    impayes = df_check_f[(df_check_f["Cible"] == target) & (df_check_f["Statut"] == "EN ATTENTE")]
                    total_dette = impayes["Montant"].astype(int).sum() if not impayes.empty else 0

                    st.markdown("""
                        <style>
                        @keyframes pulse-red { 0% { box-shadow: 0 0 0 0px rgba(211, 47, 47, 0.7); border-color:white; } 50% { box-shadow: 0 0 0 15px rgba(211, 47, 47, 0); border-color:red; } 100% { box-shadow: 0 0 0 0px rgba(211, 47, 47, 0); border-color:white; } }
                        .alert-mandat { background-color: #d32f2f; color: white; padding: 15px; border-radius: 10px; border: 2px solid white; animation: pulse-red 1s infinite; text-align: center; margin-top:10px; }
                        .alert-dette { background-color: #e67e22; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-top:5px; }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    if is_wanted:
                        st.markdown(f'<div class="alert-mandat">🚨 <b>INDIVIDU RECHERCHÉ</b> 🚨<br>{motif_recherche.upper()}</div>', unsafe_allow_html=True)
                    if total_dette > 0:
                        st.markdown(f'<div class="alert-dette">⚠️ FACTURES IMPAYÉES : {total_dette}$</div>', unsafe_allow_html=True)

                # --- COLONNE 2 : APERÇU DE LA FACTURE (STYLE TICKET) ---
                with col_facture:
                    st.markdown("#### 📄 Aperçu")
                    header_ticket = "FACTURE AVERIS" if f_emetteur == "Averis" else "FACTURE OFFICIELLE"
                    
                    st.markdown(f"""
                    <div style="border: 2px solid black; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; line-height: 1.2; box-shadow: 4px 4px 0px #888;">
                        <center><b>{header_ticket}</b><br><small>RÉPUBLIQUE DE RENSSERLAER</small></center>
                        <hr style="border-top: 1px dashed black; margin: 10px 0;">
                        <b>SIGNATAIRE :</b> {agent_identifie.upper()}<br>
                        <b>ÉMETTEUR   :</b> {f_emetteur.upper()}<br>
                        <b>DATE       :</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
                        <b>NOM        :</b> {target}<br>
                        <b>MOTIF      :</b> {f_motif.upper() if f_motif else '...'}<br>
                        <b>PLAQUE     :</b> <span style="border: 1px solid black; padding: 0 3px;">{f_plate}</span><br>
                        <b>MONTANT    :</b> {f_val}$
                        <hr style="border-top: 1px dashed black; margin: 10px 0;">
                        <div style="text-align: center; font-weight: bold;">
                            POINTS : -{f_pts if can_pull_points else 0}<br>
                            <small>Document certifié conforme</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # --- COLONNE 3 : VÉHICULES DU CITOYEN (BOUCLE COMPLÈTE) ---
                with col_vehicules:
                    st.markdown("#### 🚗 Véhicules")
                    if not target_veh.empty:
                        for _, veh in target_veh.iterrows():
                            assu_v = str(veh['Assurance']).upper()
                            
                            # Logique de couleur Assurance
                            if "RCT" in assu_v:
                                col_v, txt_v = "#27ae60", "✅ ASSURÉ RCT"
                            elif "AVERIS" in assu_v:
                                col_v, txt_v = "#E67E22", "⚠️ ASSURÉ AVERIS"
                            elif any(word in assu_v for word in ["OUI", "✅"]):
                                col_v, txt_v = "#27ae60", "✅ VÉHICULE EN RÈGLE"
                            else:
                                col_v, txt_v = "#d32f2f", "🚨 NON-ASSURÉ"

                            st.markdown(f"""
                            <div style="border: 2px solid black; padding: 10px; background: white; color: black; font-family: 'Courier New', monospace; margin-bottom: 10px; font-size: 0.85em;">
                                <center><b>TITRE DE CIRCULATION</b></center>
                                <hr style="border-top: 1px solid #ccc; margin: 5px 0;">
                                <b>MODÈLE :</b> {veh['Marque du véhicule']}<br>
                                <b>PLAQUE :</b> <span style="border: 1px solid black; padding: 0 2px;">{veh['Numéro de la plaque']}</span><br>
                                <hr style="border-top: 1px solid #ccc; margin: 5px 0;">
                                <div style="text-align: center; color: {col_v}; font-weight: bold;">
                                    {txt_v}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Aucun véhicule trouvé.")

# ======================================================================================
# --- ONGLET 3 : ADMINISTRATION (STAFF UNIQUEMENT) ---
# ======================================================================================

# Sécurité : On vérifie qu'il y a bien au moins 3 onglets créés (index 0, 1, 2)
if len(tabs) > 2:
    with tabs[2]:
        # Sécurité supplémentaire : On ne rend le contenu que si l'utilisateur est Staff
        if st.session_state.user_auth == "Staff":
            st.markdown("## 🛠️ ADMINISTRATION GÉNÉRALE")
            st.info("Espace réservé à la gestion nationale, validation des services et paies.")
            
            # --- A. MODULE DE VALIDATION DES HEURES (CLOCK) ---
            st.divider()
            st.subheader("🛡️ Validation des Services")
            
            try:
                # Lecture en temps réel pour l'administration
                df_admin_clock = cloud_conn.read(worksheet="Clock", ttl=0).fillna("")
                df_admin_clock.columns = df_admin_clock.columns.str.strip().str.lower()
                
                # On ne traite que les demandes "à valider"
                attente = df_admin_clock[df_admin_clock["statut"] == "à valider"]
                
                if not attente.empty:
                    for i, row in attente.iterrows():
                        with st.container(border=True):
                            c1, c2 = st.columns([3, 1])
                            
                            # Détails du service
                            c1.markdown(f"**🕵️ Agent :** {row['nom']} | **Job :** {row['job']}")
                            c1.caption(f"📅 Du {row['début']} au {row['fin']}")
                            
                            # Actions de validation
                            col_v, col_r = c2.columns(2)
                            if col_v.button("✔️", key=f"valid_{i}", help="Valider"):
                                df_admin_clock.at[i, "statut"] = "Validé"
                                cloud_conn.update(worksheet="Clock", data=df_admin_clock)
                                st.success("Service validé !")
                                time.sleep(0.5)
                                st.rerun()
                                
                            if col_r.button("❌", key=f"refus_{i}", help="Refuser"):
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
                    new_pts = st.slider("Points Permis", 0, 25, 25)

                if st.button("🆕 CRÉER LE DOSSIER", width="stretch", type="primary"):
                    if new_name:
                        # Application des règles : 15k solde et Date Auto
                        today_str = datetime.now().strftime("%d/%m/%Y")
                        
                        new_row_bank = pd.DataFrame([{
                            "Nom Roblox": new_name,
                            "Nom Discord": new_discord,
                            "Solde": 15000,
                            "Emploiement": " / ".join(new_jobs),
                            "Date d'arrivée": today_str,
                            "Statut": "RAS",
                            "Code": f"{new_name}123",
                            "Motif Recherche": ""
                        }])
                        
                        new_row_pts = pd.DataFrame([{
                            "Nom Roblox": new_name, 
                            "PTS": new_pts, 
                            "Validité": "OUI"
                        }])
                        
                        try:
                            # Mise à jour des DataFrames et du Cloud
                            df_b_updated = pd.concat([df_b, new_row_bank], ignore_index=True)
                            df_p_updated = pd.concat([df_p, new_row_pts], ignore_index=True)
                            
                            cloud_conn.update(worksheet="Banque", data=df_b_updated)
                            cloud_conn.update(worksheet="Points Permis", data=df_p_updated)
                            
                            st.success(f"✅ Dossier créé pour {new_name} avec un solde de 15,000$ !")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur lors de la création : {e}")
                    else:
                        st.error("Veuillez saisir au moins le nom Roblox.")

# ======================================================================================
        # --- SECTION C : SURVEILLANCE DU CUMUL DES HEURES ---
        # ======================================================================================
        st.divider()
        st.markdown("### 📊 Surveillance du Cumul des Heures")
        st.caption("Visualisation du temps de service accumulé par les agents (validé mais non payé).")

        with st.container(border=True):
            list_agents = sorted(df_admin_clock["nom"].unique().tolist()) if not df_admin_clock.empty else []
            agent_view = st.selectbox("🔍 Sélectionner un agent pour vérification :", ["---"] + list_agents, key="cumul_view_select")

            if agent_view != "---":
                # Extraction des logs validés non payés
                logs_view = df_admin_clock[(df_admin_clock["nom"] == agent_view) & (df_admin_clock["statut"] == "Validé")]
                
                v_min_rct, v_min_pol = 0, 0
                for _, r in logs_view.iterrows():
                    try:
                        t_deb = datetime.strptime(str(r["début"]), "%d/%m/%Y %H:%M:%S")
                        t_fin = datetime.strptime(str(r["fin"]), "%d/%m/%Y %H:%M:%S")
                        duree = (t_fin - t_deb).total_seconds() / 60
                        if "RCT" in str(r["job"]).upper(): v_min_rct += duree
                        elif "POL" in str(r["job"]).upper(): v_min_pol += duree
                    except: continue

                # Affichage des metrics d'activité
                m1, m2, m3 = st.columns(3)
                m1.metric("Minutes RCT", f"{int(v_min_rct)} min")
                m2.metric("Minutes Police", f"{int(v_min_pol)} min")
                m3.metric("Sessions en attente", len(logs_view))

                if not logs_view.empty:
                    with st.expander("📄 Voir le détail des sessions"):
                        st.table(logs_view[["job", "début", "fin"]])
                else:
                    st.info("Aucune heure validée en attente pour cet agent.")

        # ======================================================================================
        # --- SECTION D : TERMINAL DE PAIE NATIONALE ---
        # ======================================================================================
        st.divider()
        st.markdown("### 🧧 Terminal de Paie Nationale")
        st.caption("Génération automatique de la fiche de paie et exécution des virements.")

        with st.container(border=True):
            list_users = sorted(df_b["Nom Roblox"].unique().tolist()) if not df_b.empty else []
            target_paie = st.selectbox("👤 Sélectionner le bénéficiaire du virement :", ["---"] + list_users, key="paie_target_select")

            if target_paie != "---":
                # 1. Données & Calculs
                user_data = df_b[df_b["Nom Roblox"] == target_paie].iloc[0]
                user_jobs = str(user_data.get("Emploiement", "")).split(" / ")
                
                try: solde_actuel = float(str(user_data.get("Solde", 0)).replace('$', '').replace(',', '').strip())
                except: solde_actuel = 0.0

                # Calcul des heures pour la paie
                logs_paie = df_admin_clock[(df_admin_clock["nom"] == target_paie) & (df_admin_clock["statut"] == "Validé")]
                min_rct, min_pol = 0, 0
                for _, r in logs_paie.iterrows():
                    try:
                        d = (datetime.strptime(str(r["fin"]), "%d/%m/%Y %H:%M:%S") - datetime.strptime(str(r["début"]), "%d/%m/%Y %H:%M:%S")).total_seconds() / 60
                        if "RCT" in str(r["job"]).upper(): min_rct += d
                        elif "POL" in str(r["job"]).upper(): min_pol += d
                    except: continue

                # Barème financier
                base_sal = 15000
                p_rct = int(2000 * min(min_rct / 1200, 1.0))
                p_pol = int(3000 * min(min_pol / 1200, 1.0))
                b_staff = 4000 if "Staff" in user_jobs else 0
                b_averis = 2000 if "Averis" in user_jobs else 0
                b_sp = 1000 if "Service Public" in user_jobs else 0
                total_brut = base_sal + p_rct + p_pol + b_staff + b_averis + b_sp

                # Assurances & Routage
                user_vehs = df_i[df_i["Nom d'utilisateur ROBLOX"] == target_paie]
                c_rct, c_averis, c_std, count_rct_cars = 0, 0, 0, 0
                for _, v in user_vehs.iterrows():
                    assu = str(v.get("Assurance", "")).upper()
                    if "RCT" in assu: count_rct_cars += 1
                    elif "AVERIS" in assu: c_averis += 130
                    else: c_std += 150
                
                c_rct_final = 300 if count_rct_cars >= 2 else count_rct_cars * 150
                total_deduc = c_rct_final + c_averis + c_std
                net_to_pay = total_brut - total_deduc

                # --- AFFICHAGE PAIE DÉTAILLÉE ---
                st.markdown(f"#### 📄 Fiche de Paie : {target_paie}")
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**💰 REVENUS**")
                    st.write(f"- Base : `15,000$`")
                    st.write(f"- Primes (Heures) : `{p_rct + p_pol}$`")
                    if b_staff: st.write(f"- Bonus Staff : `+{b_staff}$` 🌟")
                    if b_averis: st.write(f"- Bonus Averis : `+{b_averis}$` 🛡️")
                    if b_sp: st.write(f"- Bonus Service Public : `+{b_sp}$` 👷")
                    st.write(f"**Brut Total : {total_brut:,}$**")
                with c2:
                    st.write("**📉 DÉDUCTIONS**")
                    st.write(f"- Assurances : `-{total_deduc}$`")
                    st.write(f"(RCT: {c_rct_final}$ | Autres: {c_averis+c_std}$)")

                st.success(f"### 💵 NET À VERSER : {net_to_pay:,} $")

                # BOUTON D'ACTION
                if st.button(f"✅ VALIDER LE VIREMENT POUR {target_paie.upper()}", use_container_width=True, type="primary"):
                    try:
                        with st.spinner("Virement en cours..."):
                            # A. Solde Citoyen
                            idx_c = df_b[df_b["Nom Roblox"] == target_paie].index[0]
                            df_b.at[idx_c, "Solde"] = solde_actuel + net_to_pay
                            
                            # B. Routage Assurances
                            def route_money(patron, amount):
                                try:
                                    ix = df_b[df_b["Nom Roblox"] == patron].index[0]
                                    curr = float(str(df_b.at[ix, "Solde"]).replace('$','').replace(',',''))
                                    df_b.at[ix, "Solde"] = curr + amount
                                except: pass

                            if c_rct_final > 0: route_money("une10000", c_rct_final)
                            if c_averis > 0: route_money("Moune2010", c_averis)
                            
                            # C. Reset Points & Archivage
                            if target_paie in df_p["Nom Roblox"].values:
                                df_p.at[df_p[df_p["Nom Roblox"] == target_paie].index[0], "PTS"] = 25
                            
                            for idx_log in logs_paie.index:
                                df_admin_clock.at[idx_log, "statut"] = "Payé"

                            # D. Sauvegarde Cloud
                            cloud_conn.update(worksheet="Banque", data=df_b)
                            cloud_conn.update(worksheet="Points Permis", data=df_p)
                            cloud_conn.update(worksheet="Clock", data=df_admin_clock)
                            
                            st.balloons()
                            st.success("Paie versée avec succès !")
                            time.sleep(1.5)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erreur lors de la transaction : {e}")
            # --- D. JOURNAUX D'AUDIT ---
            st.divider()
            st.markdown("### 📜 Journaux d'Audit (Session)")
            if "audit_logs" in st.session_state and st.session_state.audit_logs:
                with st.container(height=150, border=True):
                    for log in reversed(st.session_state.audit_logs):
                        st.write(f"🔹 {log}")
            else:
                st.info("Aucun log disponible.")

        # Le 'else' (Accès refusé) a été supprimé ici pour que l'onglet reste vide pour les non-staff.
# ======================================================================================
# 8. PIED DE PAGE
# ======================================================================================
st.divider()
st.caption(f"Terminal Fédéral RCRP FR | Opérationnel | © 2026 République de Rensselaer")
