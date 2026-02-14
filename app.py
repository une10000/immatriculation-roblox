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
        # 1. Alerte Mandat (Rouge)
        if not citoyen_info.empty and "RECHERCHÉ" in str(citoyen_info.iloc[0].get("Statut", "")).upper():
            st.markdown(f"""
                <div style="background-color: #d32f2f; padding: 20px; border-radius: 10px; border: 4px solid #ff0000; color: white; text-align: center; margin-bottom: 10px;">
                    <h2 style="margin:0; color: white;">🚨 SIGNALEMENT : INDIVIDU RECHERCHÉ 🚨</h2>
                    <p>L'individu <b>{target}</b> fait l'objet d'un mandat d'arrêt actif.</p>
                </div>
            """, unsafe_allow_html=True)

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
                st.metric("POINTS PERMIS", f"{pts}/25")
                color = "green" if pts > 0 else "red"
                st.markdown(f"Statut : <b style='color:{color};'>{'VALIDE' if pts > 0 else 'SUSPENDU'}</b>", unsafe_allow_html=True)
                
                # Bouton Reset pour Staff
                if st.session_state.user_auth in ["Staff", "Admin"] and pts <= 0:
                    if st.button("🔓 Rendre le permis", key=f"res_{target}", use_container_width=True):
                        df_p.loc[df_p["Nom Roblox"] == target, "PTS"] = 25
                        cloud_conn.update(worksheet="Points Permis", data=df_p)
                        st.success("Permis rendu !")
                        st.rerun()
            else: st.info("Aucun permis trouvé.")

        # ---------------- COLONNE 2 : BANQUE & PAIE ----------------
        with col2:
            if not citoyen_info.empty:
                st.metric("SOLDE BANCAIRE", f"{citoyen_info.iloc[0]['Solde']}$")
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
                    
                    # Prime Staff (Automatique si le job contient "Staff")
                    p_staff = 4000 if "staff" in job_raw.lower() else 0
                    
                    # Prime Exceptionnelle (Exemple : Bonus événement ou autre)
                    p_extra = 0 # À modifier manuellement ou via une autre colonne si besoin
                    
                    # Taxes Véhicules (Trio RCT)
                    mes_v = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
                    count_rct = len(mes_v[mes_v["Assurance"].str.contains("RCT", na=False, case=False)])
                    is_trio = count_rct >= 3
                    taxe_v = 200 if is_trio else (len(mes_v) * 150)

                    net = 15000 + p_pol + p_rct + p_staff + p_extra - taxe_v

                    # 3. Affichage visuel
                    c_cred, c_deb = st.columns(2)
                    
                    with c_cred:
                        st.markdown("<div style='color: #4CAF50; font-weight:bold; margin-bottom:5px;'>📥 REVENUS</div>", unsafe_allow_html=True)
                        st.markdown(f"➕ **Base Civile** : `15,000$`")
                        
                        if p_staff > 0:
                            st.markdown(f"⭐ **Prime Staff** : `{p_staff}$`")
                        
                        if "police" in job_raw.lower():
                            st.markdown(f"👮 **Prime Police** : `{p_pol}$`")
                            st.progress(ratio_pol, text=f"{int(m_pol/60)}h / 20h")
                        
                        if "agent rct" in job_raw.lower():
                            st.markdown(f"👷‍♂️ **Prime RCT** : `{p_rct}$`")
                            st.progress(ratio_rct, text=f"{int(m_rct/60)}h / 20h")
                            
                        if p_extra > 0:
                            st.markdown(f"🎁 **Bonus** : `{p_extra}$`")

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
                            <span style="font-size: 1.5em; font-weight: bold; color: #fff;">{int(net):,}$$</span>
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
                    for _, f in archives.iterrows():
                        with st.container(border=True):
                            st.write(f"**{f['Motif']}**")
                            st.caption(f"{f['Montant']}$ | ID: {f['ID']}")
                            
                            # Option Remboursement (Staff)
                            if st.session_state.user_auth in ["Staff", "Admin"]:
                                if st.button(f"🔄 Rembourser #{f['ID']}", key=f"ref_{f['ID']}"):
                                    try:
                                        solde_c = float(str(citoyen_info.iloc[0]['Solde']).replace('$','').replace(',',''))
                                        remb = float(str(f['Montant']).replace('$','').replace(',',''))
                                        
                                        df_b.loc[df_b["Nom Roblox"] == target, "Solde"] = solde_c + remb
                                        df_f_check.loc[df_f_check["ID"] == f["ID"], "Statut"] = "REMBOURSÉ"
                                        
                                        cloud_conn.update(worksheet="Banque", data=df_b)
                                        cloud_conn.update(worksheet="Factures", data=df_f_check)
                                        st.success("Remboursé !")
                                        st.rerun()
                                    except: st.error("Erreur remboursement")
                else: st.write("∅ Aucune archive.")
            except: st.error("Erreur chargement archives.")
# ======================================================================================
# 7. LOGIQUE DES ONGLETS (CORRIGÉE)
# ======================================================================================
# ======================================================================================
# NOUVEAU : SYSTÈME DE PAIEMENT DES FACTURES (STYLE TICKET)
# ======================================================================================
# --- SYSTÈME DE PAIEMENT DES FACTURES (STYLE TICKET) ---
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
        emetteur_label = str(fac.get('Emetteur', fac.get('Emetteur', 'INCONNU')))
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
                    
                    # Redirection des fonds (Patrons)
                    if "RCT" in emetteur_label.upper():
                        idx_p = df_b[df_b["Nom Roblox"] == "une10000"].index[0]
                        df_b.at[idx_p, "Solde"] = float(str(df_b.at[idx_p, "Solde"]).replace('$', '')) + montant_facture
                    elif "AVERIS" in emetteur_label.upper():
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
# 4. BOUTON ANNULER (Staff/Admin) avec remise des points
        if st.session_state.user_auth in ["Staff", "Admin", "POLSTA"]: # J'ai ajouté POLSTA au cas où
            if st.button(f"🗑️ ANNULER LA FACTURE #{fac['ID']}", key=f"admin_del_{fac['ID']}", use_container_width=True):
                try:
                    with st.spinner("Annulation et restitution des points..."):
                        # 1. On récupère les données fraîches
                        df_f_sync = cloud_conn.read(worksheet="Factures")
                        df_p_sync = cloud_conn.read(worksheet="Points Permis")
                        
                        # 2. On récupère le nombre de points sur la facture
                        pts_a_rendre = fac.get('Points', 0)
                        
                        # 3. Logique de restitution des points
                        if pts_a_rendre and str(pts_a_rendre).isdigit() and int(pts_a_rendre) > 0:
                            try:
                                idx_p = df_p_sync[df_p_sync["Nom Roblox"] == fac["Cible"]].index[0]
                                current_pts = int(df_p_sync.at[idx_p, "PTS"])
                                df_p_sync.at[idx_p, "PTS"] = min(12, current_pts + int(pts_a_rendre))
                                cloud_conn.update(worksheet="Points Permis", data=df_p_sync)
                                st.info(f"🔄 {pts_a_rendre} points restitués au civil.")
                            except Exception as e_pts:
                                st.error(f"Erreur restitution points : {e_pts}")

                        # 4. On change le statut de la facture en ANNULÉ
                        df_f_sync.loc[df_f_sync["ID"] == fac["ID"], "Statut"] = "ANNULÉ"
                        
                        # 5. Sauvegarde de la facture
                        cloud_conn.update(worksheet="Factures", data=df_f_sync)

                        # --- LA MODIFICATION DU LOG ICI ---
                        qui_annule = st.session_state.get('staff_name', 'Agent Staff')
                        record_log(qui_annule, f"Rembourser la facture #{fac['ID']} de {fac['Cible']}")
                        
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
            # --- RÉCUPÉRATION TECHNIQUE DE LA DATE ---
            date_val = veh.get('Horodateur', 'N/A')
            # On retire le [:10] qui coupait l'heure
            date_display = str(date_val) if date_val != 'N/A' else "Non spécifiée"

            # --- LOGIQUE DE SÉCURITÉ RCT ---
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

            # --- TON DESIGN D'ORIGINE ---
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
                # Vérification que le formulaire n'est pas vide
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
                                
                                # 3. Création de la ligne (CORRIGÉE POUR TON SHEETS)
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
                                
                                # 5. Effet de fête et Confirmation
                                st.balloons() # 🎈
                                
                                st.success(f"""
                                ### ✅ IMMATRICULATION RÉUSSIE !
                                ---
                                * **Propriétaire :** {f_owner}
                                * **Véhicule :** {f_model}
                                * **Plaque :** {f_plate}
                                * **Montant débité :** {total_bill}$
                                
                                *Le titre de circulation a été enregistré dans la base nationale.*
                                """)
                                
                                import time
                                time.sleep(3)
                                
                                # Rafraîchissement
                                st.cache_data.clear()
                                st.rerun()
                                
                    except Exception as e:
                        st.error(f"⚠️ Erreur de connexion au Sheets : {e}")
    with col_t:
        # Titre de droite aligné sur le titre de gauche
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
# --- ONGLET 2 : SERVICES AGENT (FEUILLE CLOCK) ---
if st.session_state.user_auth in ["RCT", "Staff"]:
    with tabs[1]:
        with st.container(border=True):
            col_code, col_infos = st.columns([1, 2])
            with col_code:
                agent_code_saisi = st.text_input("🔑 Code Agent", type="password", key="pnt_clock_auth")
                job_actuel = st.selectbox("🎭 Service", ["POLSTA"], key="pnt_job_staff") if st.session_state.user_auth == "Staff" else "RCT"
            
            if agent_code_saisi:
                # Identification Agent dans la table Banque
                df_b.columns = df_b.columns.str.strip()
                res_agent = df_b[df_b["Code"].astype(str).str.contains(agent_code_saisi.strip())]
                
                if not res_agent.empty:
                    agent_identifie = res_agent.iloc[0]["Nom Roblox"]
                    now_ch = datetime.now(timezone(timedelta(hours=1)))
                    
                    # Lecture de la nouvelle feuille "Clock"
                    try:
                        df_clock = cloud_conn.read(worksheet="Clock", ttl=0).fillna("")
                        df_clock.columns = df_clock.columns.str.strip().str.lower()
                        
                        # On cherche une session active (statut "en cours")
                        session_active = df_clock[(df_clock["nom"] == agent_identifie) & (df_clock["statut"] == "en cours")]
                        en_service = not session_active.empty
                    except:
                        df_clock = pd.DataFrame(columns=["nom", "action", "job", "début", "fin", "statut"])
                        en_service = False
                    
                    # Affichage des infos
                    start_disp = "--:--"
                    if en_service:
                        val_debut = str(session_active.iloc[-1]["début"])
                        start_disp = val_debut.split(" ")[1][:5] if " " in val_debut else val_debut[:5]

                    with col_infos:
                        c1, c2, c3 = st.columns(3)
                        c1.metric("🕒 Heure", now_ch.strftime("%H:%M"))
                        c2.metric("🎬 Début", start_disp)
                        c3.metric("🏁 Fin", "--:--")
                        
                        st.write(f"Agent : **{agent_identifie}** " + ("(🟢 EN SERVICE)" if en_service else "(🔴 HORS SERVICE)"))
                        
                        b_in, b_out = st.columns(2)
                        
                        # --- BOUTON DÉBUT ---
                        with b_in:
                            if st.button("✅ DÉBUT", use_container_width=True, type="primary", disabled=en_service):
                                h_debut = now_ch.strftime("%d/%m/%Y %H:%M:%S")
                                new_row = pd.DataFrame([{
                                    "nom": agent_identifie, 
                                    "action": "WORK", # On peut mettre WORK pour dire "en travail"
                                    "job": job_actuel, 
                                    "début": h_debut, 
                                    "fin": "", 
                                    "statut": "en cours"
                                }])
                                df_clock_up = pd.concat([df_clock, new_row], ignore_index=True)
                                cloud_conn.update(worksheet="Clock", data=df_clock_up)
                                st.success("Service démarré !")
                                time.sleep(1); st.rerun()
                                
                        # --- BOUTON FIN ---
                        with b_out:
                            if st.button("🛑 FIN", use_container_width=True, disabled=not en_service):
                                h_fin = now_ch.strftime("%d/%m/%Y %H:%M:%S")
                                
                                # On trouve l'index de la ligne à modifier
                                idx_ligne = session_active.index[-1]
                                
                                # Mise à jour de la ligne existante
                                df_clock.at[idx_ligne, "fin"] = h_fin
                                df_clock.at[idx_ligne, "statut"] = "à valider"
                                
                                cloud_conn.update(worksheet="Clock", data=df_clock)
                                st.success("Service terminé !")
                                st.balloons()
                                time.sleep(1); st.rerun()
                else:
                    st.error("Code incorrect.")
        # 1. PANEL D'ALERTE : FACTURES IMPAYÉES
        df_all_f = cloud_conn.read(worksheet="Factures").fillna("")
        alertes = []
        maintenant = datetime.now()

        for idx, f in df_all_f.iterrows():
            if f["Statut"] == "EN ATTENTE":
                try:
                    limite = datetime.strptime(str(f['Date_Limite']), "%d/%m/%Y %H:%M:%S")
                    if maintenant > limite:
                        alertes.append(f)
                except: pass 

        if alertes:
            st.error(f"⚠️ {len(alertes)} FACTURE(S) EN SOUFFRANCE")
            with st.expander("🔍 VOIR LES REQUÊTES PRIORITAIRES"):
                for _, row in pd.DataFrame(alertes).iterrows():
                    st.write(f"🆔 **#{row['ID']}** | 👤 **{row['Cible']}** ({row['Montant']}$)")

        # --- RECHERCHE PAR NUMÉRO DE FACTURE ---
        with st.container(border=True):
            st.markdown("##### 🔎 Recherche Rapide de Facture")
            f_search_id = st.text_input("Entrer le N° de facture (#)", key="agent_f_search", placeholder="Ex: 4502").replace("#", "")
            
            if f_search_id:
                # Filtrage sur l'ID
                res_f = df_all_f[df_all_f["ID"].astype(str).str.contains(f_search_id, na=False)]
                
                if not res_f.empty:
                    f_dat = res_f.iloc[0]
                    statut_actuel = str(f_dat['Statut']).upper()

                    # --- ALERTE VISUELLE SELON LE STATUT ---
                    if "ATTENTE" in statut_actuel:
                        st.markdown("""
                            <div style="background-color: #E67E22; padding: 12px; border-radius: 8px; text-align: center; border: 2px solid white; animation: blinker_status 1.5s linear infinite; margin-bottom: 15px;">
                                <b style="color: white; font-size: 1.1em;">⚠️ FACTURE NON PAYÉE (EN ATTENTE)</b>
                            </div>
                            <style>
                            @keyframes blinker_status { 50% { opacity: 0.4; } }
                            </style>
                        """, unsafe_allow_html=True)
                    elif "PAY" in statut_actuel:
                        st.markdown("""
                            <div style="background-color: #27ae60; padding: 12px; border-radius: 8px; text-align: center; border: 2px solid white; margin-bottom: 15px;">
                                <b style="color: white; font-size: 1.1em;">✅ FACTURE EN RÈGLE (PAYÉE)</b>
                            </div>
                        """, unsafe_allow_html=True)

                    # --- AFFICHAGE DES DÉTAILS ---
                    col_res1, col_res2 = st.columns(2)
                    with col_res1:
                        st.info(f"**Cible :** {f_dat['Cible']}\n\n**Montant :** {f_dat['Montant']}$\n\n**Statut :** {f_dat['Statut']}")
                    with col_res2:
                        st.info(f"**Émetteur :** {f_dat['Emetteur']}\n\n**Motif :** {f_dat['Motif']}\n\n**Points :** -{f_dat['Points']}")
                else:
                    st.warning("Aucune facture trouvée avec cet ID.")
        
        st.divider()

        # ======================================================================================
        # 2. MODULE : BUREAU DES MANDATS
        # ======================================================================================
        st.markdown("#### ⚖️ Bureau des Mandats & Avis de Recherche")
        recherches_actuels = df_b[df_b["Statut"].str.upper().str.contains("RECHERCHÉ", na=False)]

        col_liste, col_ajout = st.columns([1.5, 1])

        with col_liste:
            with st.container(border=True):
                st.markdown("##### 📋 Individus en cavale")
                if not recherches_actuels.empty:
                    for _, criminel in recherches_actuels.iterrows():
                        with st.expander(f"🔴 {criminel['Nom Roblox']}"):
                            st.write(f"**Motif :** {criminel.get('Motif Recherche', 'Non précisé')}")
                            if st.button("✅ Individu Interpellé (RAS)", key=f"clear_{criminel['Nom Roblox']}", use_container_width=True):
                                idx = df_b[df_b["Nom Roblox"] == criminel["Nom Roblox"]].index[0]
                                df_b.at[idx, "Statut"] = "RAS"
                                df_b.at[idx, "Motif Recherche"] = ""
                                cloud_conn.update(worksheet="Banque", data=df_b)
                                st.cache_data.clear()
                                st.rerun()
                else:
                    st.success("✅ Aucun mandat d'arrêt actif en République.")

        with col_ajout:
            with st.container(border=True):
                st.markdown("##### 🚨 Lancer un Mandat")
                target_crim = st.selectbox("Citoyen :", ["---"] + sorted(df_b["Nom Roblox"].unique().tolist()), key="select_crim_agent")
                motif_crim = st.text_input("Motif du mandat :", placeholder="Braquage...", key="motif_crim_agent")
                
                if st.button("PUBLIER L'AVIS", type="primary", use_container_width=True):
                    if target_crim != "---" and motif_crim:
                        idx_c = df_b[df_b["Nom Roblox"] == target_crim].index[0]
                        df_b.at[idx_c, "Statut"] = "RECHERCHÉ"
                        df_b.at[idx_c, "Motif Recherche"] = motif_crim
                        cloud_conn.update(worksheet="Banque", data=df_b)
                        st.cache_data.clear()
                        st.rerun()

        st.divider()

        # ======================================================================================
        # 3. MODULE : CONSULTATION FICHIER NATIONAL (PLAQUE)
        # ======================================================================================
        st.markdown("#### 🚔 Consultation du Fichier des Immatriculations")
        with st.container(border=True):
            c1_srv, c2_srv = st.columns([3, 1])
            with c1_srv:
                plate_srv = st.text_input("Saisir une plaque", key="plate_srv_agent_unique", label_visibility="collapsed", placeholder="Ex: ABC-123").upper()
            with c2_srv:
                search_triggered = st.button("🔎 CHERCHER", key="btn_srv_plate_unique", use_container_width=True)

            if search_triggered and plate_srv:
                match_srv = df_i[df_i["Numéro de la plaque"] == plate_srv]
                if not match_srv.empty:
                    prop_srv = match_srv.iloc[0]["Nom d'utilisateur ROBLOX"]
                    v_srv = match_srv.iloc[0]["Marque du véhicule"]
                    citoyen_info = df_b[df_b["Nom Roblox"] == prop_srv]
                    if not citoyen_info.empty and "RECHERCHÉ" in str(citoyen_info.iloc[0].get("Statut", "")).upper():
                        st.error(f"🚨 INDIVIDU RECHERCHÉ : {prop_srv} (Véhicule: {v_srv})")
                    else:
                        st.info(f"📍 IDENTIFICATION : {v_srv} appartient à {prop_srv}")
                else:
                    st.error(f"❌ Plaque {plate_srv} inconnue.")

        st.divider()
# ======================================================================================
# 4. SYSTÈME DE SAISIE ET CONSULTATION (COMPLET ET SÉCURISÉ)
# ======================================================================================
with tabs[1]: # Onglet Services Agents
    if st.session_state.user_auth in ["Staff", "Agent RCT"]:
        st.markdown("### 🎯 INTERVENTION ET FACTURATION")

        if target == "---":
            st.warning("⚠️ Sélectionnez un citoyen en haut de la page.")
        else:
            # Préparation des données et du fuseau horaire
            df_b.columns = df_b.columns.str.strip() 
            tz_ch = timezone(timedelta(hours=1))
            now_ch = datetime.now(tz_ch)
            
            # Layout en 3 colonnes
            col_saisie, col_facture, col_vehicules = st.columns([1.1, 1, 0.9])
            
            # --- COLONNE 1 : SAISIE ---
            with col_saisie:
                with st.container(border=True):
                    st.markdown("#### 📝 Saisie")
                    
                    # Authentification Agent
                    agent_code_saisi = st.text_input("🔑 CODE AGENT :", type="password", key="auth_agent_code")
                    agent_identifie = None
                    
                    if "Code" in df_b.columns and agent_code_saisi:
                        def clean_code(x): return str(x).strip().split('.')[0]
                        df_b["Code_Clean"] = df_b["Code"].apply(clean_code)
                        res_agent = df_b[df_b["Code_Clean"] == str(agent_code_saisi).strip()]
                        if not res_agent.empty:
                            agent_identifie = res_agent.iloc[0]["Nom Roblox"]
                            st.success(f"Agent : **{agent_identifie}** ✅")
                        else:
                            st.error("❌ Code inconnu.")

                    # Choix de l'émetteur
                    if st.session_state.user_auth == "Staff":
                        f_emetteur = st.selectbox("Entité Émettrice", ["POLSTA", "Averis"], key="v_emetteur_final")
                    else:
                        f_emetteur = "RCT"
                        st.info("Émetteur : RCT")

                    f_val = st.number_input("Montant ($)", min_value=0, step=50, key="v_val_final")
                    can_pull_points = (st.session_state.user_auth == "Staff" and f_emetteur == "POLSTA")
                    f_pts = st.number_input("Points à retirer", 0, 12, 0, key="v_pts_final", disabled=not can_pull_points)
                    f_motif = st.text_input("Motif", key="v_mot_final")
                    
                    target_veh = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
                    v_list = ["AUCUN / PIÉTON"] + target_veh["Numéro de la plaque"].tolist()
                    f_plate = st.selectbox("Véhicule concerné", v_list, key="v_plate_final")

                    # BOUTON D'ENVOI ET ENREGISTREMENT
                    if st.button("🚨 ENVOYER FACTURE", use_container_width=True, type="primary"):
                        if not agent_identifie:
                            st.error("Code agent requis.")
                        elif not f_motif:
                            st.error("Motif obligatoire.")
                        else:
                            import random
                            
                            # 1. Mise à jour des points si nécessaire
                            if f_pts > 0 and can_pull_points:
                                try:
                                    idx_p = df_p[df_p["Nom Roblox"] == target].index[0]
                                    df_p.at[idx_p, "PTS"] = max(0, int(df_p.at[idx_p, "PTS"]) - f_pts)
                                    cloud_conn.update(worksheet="Points Permis", data=df_p)
                                except: pass

                            # 2. Préparation de la ligne complète pour le Sheets
                            nom_agent = agent_identifie
                            new_row = {
                                "ID": random.randint(1000, 9999),
                                "Cible": target,
                                "Emetteur": f_emetteur,
                                "Agent_Signataire": nom_agent,
                                "Montant": f_val,
                                "Points": f_pts if can_pull_points else 0,
                                "Motif": f"{f_motif} [{f_plate}]",
                                "Statut": "EN ATTENTE",
                                "Date_Emission": now_ch.strftime("%d/%m/%Y %H:%M:%S"),
                                "Date_Limite": (now_ch + timedelta(hours=24)).strftime("%d/%m/%Y %H:%M:%S")
                            }

                            # 3. Fusion et envoi
                            df_f_updated = pd.concat([df_all_f, pd.DataFrame([new_row])], ignore_index=True)
                            cloud_conn.update(worksheet="Factures", data=df_f_updated)
                            
                            st.success(f"✅ Facture envoyée par {nom_agent} !")
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()

            # --- COLONNE 2 : APERÇU ET HISTORIQUE ---
            with col_facture:
                st.markdown("#### 📄 Aperçu")
                header_ticket = "FACTURE AVERIS" if f_emetteur == "Averis" else "FACTURE OFFICIELLE"
                nom_signature = agent_identifie if agent_identifie else "..."
                
                st.markdown(f"""
                <div style="border: 2px solid black; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; line-height: 1.2;">
                    <center><b>{header_ticket}</b><br><small>RÉPUBLIQUE DE RENSSERLAER</small></center>
                    <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                    <b>SIGNATURE :</b> {nom_signature.upper()}<br>
                    <b>SERVICE   :</b> {f_emetteur.upper()}<br>
                    <b>DATE      :</b> {now_ch.strftime('%d/%m/%Y')}<br>
                    <b>CITOYEN   :</b> {target}<br>
                    <b>MONTANT   :</b> {f_val}$
                    <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                    <div style="text-align: center; color: black; font-weight: bold; font-size: 0.8em;">
                        POINTS : -{f_pts if can_pull_points else 0}<br>
                        <small>Authentifié numériquement</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.divider()
                st.markdown("#### 📜 Historique Factures")
                # Filtrage des factures pour le citoyen sélectionné
                if not df_all_f.empty:
                    hist_f = df_all_f[df_all_f["Cible"] == target].sort_index(ascending=False)
                    if not hist_f.empty:
                        st.dataframe(
                            hist_f[["Date_Emission", "Emetteur", "Montant", "Statut"]], 
                            hide_index=True, 
                            use_container_width=True
                        )
                    else:
                        st.info("Aucun antécédent pour ce citoyen.")

            # --- COLONNE 3 : VÉHICULES ---
            with col_vehicules:
                st.markdown("#### 🚗 Véhicules")
                if not target_veh.empty:
                    for _, veh in target_veh.iterrows():
                        assu_v = str(veh['Assurance']).upper()
                        col_v = "green" if "RCT" in assu_v else ("#E67E22" if "AVERIS" in assu_v else "#d32f2f")
                        
                        st.markdown(f"""
                        <div style="border: 2px solid black; padding: 10px; background: white; color: black; font-family: 'Courier New', monospace; margin-bottom: 10px; font-size: 0.8em;">
                            <center><b>TITRE DE CIRCULATION</b></center>
                            <hr style="border-top: 1px solid #ccc; margin: 5px 0;">
                            <b>MODÈLE :</b> {veh['Marque du véhicule']}<br>
                            <b>PLAQUE :</b> <span style="border: 1px solid black; padding: 0 2px;">{veh['Numéro de la plaque']}</span><br>
                            <hr style="border-top: 1px solid #ccc; margin: 5px 0;">
                            <div style="text-align: center; color: {col_v}; font-weight: bold;">{assu_v}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Aucun véhicule.")
    else:
        pass
# --- ONGLET 3 : ADMINISTRATION (STAFF ONLY) ---
if st.session_state.user_auth == "Staff":
    with tabs[2]:
        st.markdown('<div class="header-box"><h2>🛠️ ADMINISTRATION</h2></div>', unsafe_allow_html=True)
        
        # --- SECTION A : VALIDATION DES SERVICES (FEUILLE CLOCK) ---
        st.subheader("🛡️ Validation des Pointages")
        try:
            # Lecture de la nouvelle feuille
            df_admin = cloud_conn.read(worksheet="Clock", ttl=0)
            df_admin.columns = df_admin.columns.str.strip()
            
            # Filtrage des sessions terminées qui attendent une validation
            attente = df_admin[df_admin["statut"] == "à valider"]
            
            if not attente.empty:
                for i, row in attente.iterrows():
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        # Affichage clair du début et de la fin sur la même ligne
                        c1.write(f"**Agent :** {row['nom']} | **Job :** {row['job']}")
                        c1.caption(f"🕒 Durée : du {row['début']} au {row['fin']}")
                        
                        v_col, r_col = c2.columns(2)
                        if v_col.button("✔️", key=f"v_{i}", type="primary"):
                            df_admin.at[i, "statut"] = "Validé"
                            cloud_conn.update(worksheet="Clock", data=df_admin)
                            st.success(f"Validé pour {row['nom']}")
                            time.sleep(0.5); st.rerun()
                            
                        if r_col.button("❌", key=f"r_{i}"):
                            df_admin.at[i, "statut"] = "Refusé"
                            cloud_conn.update(worksheet="Clock", data=df_admin)
                            st.error(f"Refusé pour {row['nom']}")
                            time.sleep(0.5); st.rerun()
            else:
                st.info("⛱️ Aucun service en attente de validation.")
        except Exception as e:
            st.error(f"Erreur Pointages : {e}")

        st.divider()
# ======================================================================================
# 5. ONGLET ADMINISTRATION (INTÉGRALITÉ ABSOLUE : CRÉATION + HEURES + PAIE + LOGS + STATS)
# ======================================================================================
with tabs[2]:
    if st.session_state.user_auth == "Staff":
        st.markdown("## 🛡️ SYSTÈME D'ADMINISTRATION GÉNÉRAL")

        # --- SECTION 1 : CRÉATION DE PROFIL AVEC SLIDER DE POINTS ---
        st.subheader("🆕 Enregistrement Nouveau Citoyen")
        with st.container(border=True):
            with st.form("form_creation_totale"):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    new_nom = st.text_input("Nom d'utilisateur Roblox :")
                    new_jobs = st.multiselect("Grades / Emplois :", 
                                            ["Citoyen", "Agent RCT", "Police", "Staff", "Averis", "Service Public"], 
                                            default=["Citoyen"])
                with col_c2:
                    # Slider pour les points de permis (0 à 50)
                    pts_initial = 25 # <-- À AJOUTER
                    solde_depart = 15000
                    date_auto = datetime.now().strftime("%d/%m/%Y")
                    st.info(f"💰 Solde : {solde_depart}$ | 📅 Date : {date_auto}")

                if st.form_submit_button("🔨 CRÉER LE PROFIL COMPLET"):
                    if new_nom:
                        if new_nom in df_b["Nom Roblox"].values:
                            st.error("❌ Ce citoyen existe déjà.")
                        else:
                            try:
                                # A. Base Banque (15k + Date auto)
                                new_user_b = {
                                    "Nom Roblox": new_nom, "Solde": solde_depart,
                                    "Emploiement": "/".join(new_jobs), "Date d'arrivée": date_auto,
                                    "Code": random.randint(1000, 9999)
                                }
                                df_b = pd.concat([df_b, pd.DataFrame([new_user_b])], ignore_index=True)
                                cloud_conn.update(worksheet="Banque", data=df_b)
                                
                                # B. Base Permis (Points via Slider)
                                new_user_p = {"Nom Roblox": new_nom, "PTS": pts_initial}
                                try:
                                    df_p = pd.concat([df_p, pd.DataFrame([new_user_p])], ignore_index=True)
                                    cloud_conn.update(worksheet="Permis", data=df_p)
                                except:
                                    cloud_conn.update(worksheet="Points Permis", data=pd.concat([df_p, pd.DataFrame([new_user_p])], ignore_index=True))
                                
                                # C. Audit Log
                                if "audit_logs" not in st.session_state: st.session_state.audit_logs = []
                                st.session_state.audit_logs.append(f"[{datetime.now().strftime('%H:%M')}] CRÉATION : {new_nom} ({pts_initial} PTS)")
                                
                                st.success(f"✅ Profil créé !"); st.cache_data.clear(); time.sleep(1); st.rerun()
                            except Exception as e: st.error(f"Erreur : {e}")
                    else: st.warning("Nom requis.")

        st.divider()

        # --- SECTION 2 : CUMUL DES HEURES (CONSULTATION) ---
        st.subheader("📊 Cumul des Heures de Service")
        if 'df_clock' not in locals():
            try: df_clock = cloud_conn.read(worksheet="Clock")
            except: df_clock = pd.DataFrame()

        liste_citoyens = sorted(df_b["Nom Roblox"].unique().tolist())
        agent_select = st.selectbox("Sélectionner un agent pour analyse :", liste_citoyens, key="admin_clock_view")

        m_rct, m_pol = 0, 0
        if agent_select and not df_clock.empty:
            logs_valid = df_clock[(df_clock["nom"] == agent_select) & (df_clock["statut"] == "Validé")]
            for _, r in logs_valid.iterrows():
                try:
                    diff = (datetime.strptime(str(r["fin"]), "%d/%m/%Y %H:%M:%S") - datetime.strptime(str(r["début"]), "%d/%m/%Y %H:%M:%S")).total_seconds() / 60
                    if "RCT" in str(r["job"]).upper(): m_rct += diff
                    elif "POL" in str(r["job"]).upper(): m_pol += diff
                except: continue

            c1, c2, c3 = st.columns(3)
            c1.metric("Minutes RCT", f"{int(m_rct)}m")
            c2.metric("Minutes Police", f"{int(m_pol)}m")
            c3.metric("Total Semaine", f"{int(m_rct + m_pol)}m")

        st.divider()

        # --- SECTION 3 : TERMINAL DE PAIEMENT NATIONAL (COMPLET) ---
        st.subheader("🧧 Terminal de Paiement National")
        with st.container(border=True):
            target_paie = st.selectbox("Bénéficiaire du virement :", liste_citoyens, key="admin_pay_terminal")
            
            if target_paie:
                # 1. Calcul des Primes & Bonus
                u_data = df_b[df_b["Nom Roblox"] == target_paie]
                u_jobs = [j.strip() for j in str(u_data["Emploiement"].values[0]).split("/")]
                s_primes, T_LIMITE = 0, 1200
                
                for j in u_jobs:
                    if j == "Police": s_primes += int(3000 * min(m_pol/T_LIMITE, 1.0))
                    elif j == "Agent RCT": s_primes += int(2000 * min(m_rct/T_LIMITE, 1.0))
                    elif j == "Staff": s_primes += 4000
                    elif j == "Averis": s_primes += 2000
                    elif j == "Service Public": s_primes += 1000

                # 2. Calcul Assurances & Redirection Patrons
                v_agent = df_i[df_i["Nom d'utilisateur ROBLOX"] == target_paie]
                c_rct, v_av, v_std = 0, 0, 0
                for _, v in v_agent.iterrows():
                    a = str(v["Assurance"]).upper()
                    if "RCT" in a: c_rct += 1
                    elif "AVERIS" in a: v_av += 130
                    else: v_std += 150
                p_rct = 200 if c_rct >= 3 else (c_rct * 150)
                
                t_brut = 15000 + s_primes
                t_taxes = p_rct + v_av + v_std
                t_net = t_brut - t_taxes

                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**💰 REVENUS**")
                    st.write("Base : 15,000$")
                    st.write(f"Bonus/Primes : +{s_primes:,}$")
                with col_b:
                    st.write("**📉 DÉDUCTIONS**")
                    st.write(f"Assurances : -{t_taxes:,}$")
                
                st.markdown(f"### NET À VERSER : {int(t_net):,}$")

                if st.button(f"🚀 EXÉCUTER LE VIREMENT POUR {target_paie.upper()}", use_container_width=True, type="primary"):
                    try:
                        idx_rct = df_b[df_b["Nom Roblox"] == "une10000"].index[0]
                        idx_av = df_b[df_b["Nom Roblox"] == "Moune2010"].index[0]
                        df_b.at[idx_rct, "Solde"] = float(df_b.at[idx_rct, "Solde"]) + p_rct
                        df_b.at[idx_av, "Solde"] = float(df_b.at[idx_av, "Solde"]) + v_av
                        
                        idx_target = df_b[df_b["Nom Roblox"] == target_paie].index[0]
                        df_b.at[idx_target, "Solde"] = float(df_b.at[idx_target, "Solde"]) + t_net
                        
                        df_clock.loc[(df_clock["nom"] == target_paie) & (df_clock["statut"] == "Validé"), "statut"] = "Payé"
                        df_i.loc[df_i["Nom d'utilisateur ROBLOX"] == target_paie, "Assurance"] = \
                            df_i.loc[df_i["Nom d'utilisateur ROBLOX"] == target_paie, "Assurance"].apply(lambda x: f"✅ {str(x).replace('✅','')}")
                        
                        cloud_conn.update(worksheet="Banque", data=df_b)
                        cloud_conn.update(worksheet="Clock", data=df_clock)
                        cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i)
                        
                        st.session_state.audit_logs.append(f"[{datetime.now().strftime('%H:%M')}] PAYE : {target_paie} ({int(t_net)}$)")
                        st.success("Paie versée !"); st.balloons(); st.cache_data.clear(); time.sleep(1); st.rerun()
                    except Exception as e: st.error(f"Erreur : {e}")

        st.divider()

        # --- SECTION 4 : JOURNAUX D'AUDIT & STATISTIQUES ---
        col_end_1, col_end_2 = st.columns([2, 1])

        with col_end_1:
            st.subheader("📜 Journaux d'Audit Staff")
            with st.container(border=True):
                if "audit_logs" in st.session_state and st.session_state.audit_logs:
                    st.code("\n".join(list(reversed(st.session_state.audit_logs))), language="bash")
                    if st.button("🗑️ Vider les logs"): st.session_state.audit_logs = []; st.rerun()
                else: st.info("Aucun log.")

        with col_end_2:
            st.subheader("📊 État du Système")
            with st.container(border=True):
                st.write(f"👥 Citoyens : **{len(df_b)}**")
                st.write(f"🚗 Véhicules : **{len(df_i)}**")
                st.write(f"📋 Logs d'heures : **{len(df_clock)}**")
                st.divider()
                if st.button("♻️ FORCER SYNCHRO", use_container_width=True):
                    st.cache_data.clear(); st.rerun()

    else:
        st.warning("🔒 Accès Administration : Staff uniquement.")
# ======================================================================================
# 8. PIED DE PAGE
# ======================================================================================
st.divider()
st.caption(f"Terminal Fédéral RCRP FR | Opérationnel | © 2026 République de Rensselaer")
