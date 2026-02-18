import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta, timezone
from st_supabase_connection import SupabaseConnection # <--- On remplace GSheets par ça

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
# 2. MOTEUR DE DONNÉES (SYNC) - SUPABASE VERSION
# ======================================================================================
# Connexion forcée (on bypass la détection automatique qui bug)
conn = st.connection(
    "supabase",
    type=SupabaseConnection,
    url=st.secrets["connections"]["supabase"]["url"],
    key=st.secrets["connections"]["supabase"]["key"]
)

@st.cache_data(ttl=300)
def fetch_database():
    try:
        # On récupère les données de chaque table
        # .select("*") signifie "prends toutes les colonnes"
        res_bank = conn.table("Banque").select("*").execute()
        res_immat = conn.table("Copie de Immatriculations").select("*").execute()
        res_pts = conn.table("Points Permis").select("*").execute()

        # On transforme les résultats en DataFrames Pandas
        df_bank = pd.DataFrame(res_bank.data).fillna("")
        df_immat = pd.DataFrame(res_immat.data).fillna("")
        df_pts = pd.DataFrame(res_pts.data).fillna("")

        return df_bank, df_immat, df_pts
    except Exception as e:
        st.error(f"Erreur de liaison Supabase : {e}")
        # On renvoie des tableaux vides pour éviter que l'app crash
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# On lance la récupération initiale
df_b, df_i, df_p = fetch_database()
# ======================================================================================
# 3. ÉTAT DE LA SESSION & PARAMÈTRES
# ======================================================================================
if "user_auth" not in st.session_state: st.session_state.user_auth = None
if "audit_logs" not in st.session_state: st.session_state.audit_logs = []

# ======================================================================================
# CONFIGURATION ET FONCTIONS TECHNIQUES (À METTRE EN HAUT)
# ======================================================================================
# ======================================================================================
# CONFIGURATION ET FONCTIONS TECHNIQUES (SUPABASE)
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

def verifier_ou_creer_profil(nom_roblox):
    """Vérifie si le joueur existe, sinon crée son profil avec 15k et la date."""
    try:
        # On cherche le joueur
        res = conn.table("Banque").select("*").eq("Nom Roblox", nom_roblox).execute()
        
        if not res.data:
            # LE JOUEUR N'EXISTE PAS -> CRÉATION AUTOMATIQUE
            nouveau_profil = {
                "Nom Roblox": nom_roblox,
                "Solde": 15000,  # Ton solde de départ
                "Date de création": datetime.now().strftime("%d/%m/%Y") # Date auto
            }
            conn.table("Banque").insert(nouveau_profil).execute()
            return 15000, True # Retourne le solde et confirme la création
        
        return res.data[0]["Solde"], False # Retourne le solde existant
    except Exception as e:
        st.error(f"Erreur vérification profil : {e}")
        return 0, False

def traiter_paiement_prime(target_name, metier, montant):
    """Gère le prélèvement sur l'employeur et l'ajout sur l'employé via Supabase"""
    source_compte = None
    if "Averis" in metier:
        source_compte = "Moune2010" # Pour Averis, l'argent va à Moune2010
    elif "Agent RCT" in metier:
        source_compte = "une10000"
    
    if source_compte:
        try:
            # 1. On s'assure que l'employé a un compte (et on récupère son solde)
            solde_target, _ = verifier_ou_creer_profil(target_name)
            
            # 2. On récupère le solde de l'employeur
            res_source = conn.table("Banque").select("Solde").eq("Nom Roblox", source_compte).execute()
            if not res_source.data:
                return False, f"❌ Le compte employeur ({source_compte}) n'existe pas."
            
            solde_source = res_source.data[0]["Solde"]

            # 3. MISE À JOUR DES SOLDES (Prélèvement et Ajout)
            # Retrait employeur
            conn.table("Banque").update({"Solde": solde_source - montant}).eq("Nom Roblox", source_compte).execute()
            # Ajout employé
            conn.table("Banque").update({"Solde": solde_target + montant}).eq("Nom Roblox", target_name).execute()
            
            return True, f"✅ Prime de {montant}$ versée (Payé par {source_compte})"
        except Exception as e:
            return False, f"❌ Erreur lors du virement : {e}"
    else:
        return False, "⚠️ Aucun employeur configuré (Averis ou RCT uniquement)."

# Codes de Service
KEY_RCT = "RCT-26-RCRPFR"
KEY_STAFF = "RCRPFR-25-26"

def record_log(user, action):
    """Enregistre les logs dans la session (sans code pour les civils)"""
    now = datetime.now().strftime("%H:%M:%S")
    if "audit_logs" not in st.session_state:
        st.session_state.audit_logs = []
    st.session_state.audit_logs.append(f"[{now}] {user} : {action}")
# ======================================================================================
# 4. SIDEBAR CONDITIONNELLE (LOGO & INFOS)
# ======================================================================================

if st.session_state.user_auth is not None:
    with st.sidebar:
        # LOGO RCRP 
        # Si ton logo ne s'affiche pas, vérifie que ce lien finit bien par .png ou .jpg
        # Sinon, télécharge l'image et mets-la sur PostImages/Imgur
        st.image("https://cdn.discordapp.com/attachments/1441508709024006315/1471115849631793256/Capture_decran_2025-12-01_a_21.03.31.png?ex=698dc2e6&is=698c7166&hm=ddabf40f0fad8139ed693e02221341fe14e01ad84b35317af6a101c62986b79b&", use_container_width=True)
        
        st.divider()
        
        # Imports optimisés (déjà fait en haut normalement, mais on garde pour la structure)
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

        # 4. Bloc Date
        st.markdown(f"""
            <div style="text-align: left; line-height: 1.1;">
                <span style="font-size: 1.5em;">📅</span><br>
                <b style="font-size: 1.2em;">{nom_jour},</b><br>
                <span style="font-size: 1.1em;">{num_jour} {nom_mois} {annee}</span>
            </div>
        """, unsafe_allow_html=True)

        st.write("") 

        # 5. Bloc Horloge Dynamique
        st.markdown("<div style='text-align: left; font-size: 1.5em; margin-bottom: 0;'>⏰</div>", unsafe_allow_html=True)
        
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
            # Avec Supabase, on vide le cache Streamlit pour forcer le prochain fetch_database()
            st.cache_data.clear()
            record_log(st.session_state.user_auth, "Synchro Base de Données")
            st.rerun()

        # --- BOUTON DÉCONNEXION ---
        if st.button("🚪 DÉCONNEXION", use_container_width=True):
            try:
                record_log(st.session_state.user_auth, "Déconnexion")
            except:
                pass
            
            # Nettoyage complet
            st.cache_data.clear()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            # Rechargement de la page (Hack pour vider l'UI)
            components.html("<script>window.parent.location.reload();</script>", height=0)
            st.stop()
            
        st.divider()
        st.caption("📜 JOURNAUX D'AUDIT (SESSION)")
        if "audit_logs" in st.session_state:
            # On affiche les 8 derniers logs
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
    """, height=650)
    
    st.write("")
    st.warning("⚠️ **AVERTISSEMENT :** Toute action effectuée sur ce terminal est enregistrée.")
    st.write("---")

    # 3. COLONNES D'ACCÈS
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 👥 CIVIL")
        nom_civil = st.text_input("Ecrivez quelque chose (Optionnel)", placeholder="Ex: Liberté, Egalité, Renault Coupé.", key="input_civil_align")
        if st.button("ACCÉDER AU TERMINAL", key="l_civ_f", use_container_width=True):
            st.cache_data.clear() # On s'assure que les données Supabase seront fraîches
            st.session_state.user_auth = "Civil"
            st.rerun()
            
    with c2:
        st.markdown("### 👨‍🔧 AGENT RCT")
        login_rct = st.text_input("Identifiant Agent", placeholder="Code RCT", type="password", key="l_rct_ff")
        if st.button("AUTHENTIFICATION RCT", key="b_rct_f", use_container_width=True):
            if login_rct == KEY_RCT:
                st.cache_data.clear()
                st.session_state.user_auth = "RCT"
                st.rerun()
            else: 
                st.error("Clé invalide.")
                
    with c3:
        st.markdown("### 🛡️👮‍♂️ Portail POLSTA(RIS)")
        login_staff = st.text_input("Clé Maîtresse", placeholder="Code POLSTA(RIS)", type="password", key="l_st_ff")
        if st.button("ACCÈS ADMINISTRATEUR", key="b_st_f", use_container_width=True):
            if login_staff == KEY_STAFF:
                st.cache_data.clear()
                st.session_state.user_auth = "Staff"
                st.rerun()
            else: 
                st.error("Accès refusé.")

    st.stop()
# ======================================================================================
# LE RESTE DU CODE (S'affiche uniquement après connexion)
# ======================================================================================
# ======================================================================================
# 6. MODULE : DOSSIER CITOYEN UNIFIÉ (VERSION SUPABASE)
# ======================================================================================

with st.container():
    # --- A. TABLEAU PUBLIC DES AVIS DE RECHERCHE ---
    # On filtre sur df_b (le DataFrame récupéré par fetch_database)
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
    
    # On trie la liste des citoyens
    search_list = ["---"] + sorted(df_b["Nom Roblox"].unique().tolist())
    target = st.selectbox("Sélectionner un citoyen :", search_list, key="main_selector")
    
    if target != "---":
        # On récupère les infos de la ligne sélectionnée
        citoyen_info = df_b[df_b["Nom Roblox"] == target]
        
        # --- B. ALERTES AUTOMATIQUES (INTERPOL / PERMIS) ---
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
                    background-color: #900000; padding: 30px; border-radius: 15px;
                    border: 8px solid #ff0000; color: white; text-align: center;
                    margin-bottom: 20px; animation: blink 1s infinite;
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

        # Alerte Permis
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

        # --- C. RECHERCHE PAR PLAQUE (PAYANTE 10$) ---
        with st.expander("🔍 RECHERCHE D'IDENTITÉ PAR PLAQUE (Coût : 10$)", expanded=False):
            st.warning(f"Les 10$ seront prélevés sur le compte de : **{target}**.")
            c1, c2 = st.columns([3, 1])
            with c1:
                search_plate = st.text_input("Saisir une plaque", key="p_search", label_visibility="collapsed").upper()
            with c2:
                if st.button("Lancer", key="btn_p_search", use_container_width=True, type="primary"):
                    if search_plate:
                        # 1. On récupère le solde actuel en direct sur Supabase pour éviter les erreurs
                        res_s = conn.table("Banque").select("Solde").eq("Nom Roblox", target).execute()
                        if res_s.data:
                            solde_p = float(res_s.data[0]["Solde"])
                            if solde_p >= 10:
                                # 2. Recherche de la plaque dans la table immatriculations
                                res_i = conn.table("public.Copie de Immatriculations").select("*").eq("Numéro de la plaque", search_plate).execute()
                                
                                if res_i.data:
                                    owner = res_i.data[0]["Nom d'utilisateur ROBLOX"]
                                    v_model = res_i.data[0]["Marque du véhicule"]
                                    
                                    # 3. On prélève les 10$ sur Supabase
                                    conn.table("Banque").update({"Solde": solde_p - 10}).eq("Nom Roblox", target).execute()
                                    
                                    st.success(f"🔍 Résultat : {search_plate} -> {owner} ({v_model})")
                                    st.cache_data.clear() # On force le refresh pour voir le nouveau solde
                                else: 
                                    st.error("Plaque introuvable dans le Registre National.")
                            else: 
                                st.error("Solde insuffisant (10$ requis).")
                    else: 
                        st.warning("Veuillez saisir une plaque.")

        st.markdown("---")
        
# ==============================================================================
# --- RÉCUPÉRATION DES DONNÉES (Table Banque) ---
# ==============================================================================
try:
    # On force la récupération des infos pour le "target" (le citoyen sélectionné)
    res_b = conn.table("Banque").select("*").eq("Nom Roblox", target).execute()
    citoyen_info = pd.DataFrame(res_b.data)
except Exception as e:
    st.error(f"Erreur Supabase (Table Banque) : {e}")
    citoyen_info = pd.DataFrame()

# ==============================================================================
# --- D. DOSSIER DÉTAILLÉ (3 COLONNES) ---
# ==============================================================================
if not citoyen_info.empty:
    col1, col2, col3 = st.columns(3)

    # ---------------- COLONNE 1 : POINTS & PERMIS ----------------
    with col1:
        st.markdown("### 🪪 PERMIS")
        p_data = df_p[df_p["Nom Roblox"] == target]
        
        if not p_data.empty:
            pts = int(p_data.iloc[0]["PTS"])
            st.metric("POINTS PERMIS", f"{pts}/25")
            color = "green" if pts > 0 else "red"
            st.markdown(f"Statut : <b style='color:{color};'>{'VALIDE' if pts > 0 else 'SUSPENDU'}</b>", unsafe_allow_html=True)
            
            # Action Staff : Restauration
            if st.session_state.user_auth in ["Staff", "Admin"] and pts <= 0:
                if st.button("🔓 Rendre le permis", key=f"res_{target}", use_container_width=True):
                    conn.table("points_permis").update({"PTS": 25}).eq("Nom Roblox", target).execute()
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.info("Aucun permis trouvé.")

    # ---------------- COLONNE 2 : BANQUE & PAIE ----------------
    with col2:
        st.markdown("### 💳 BANQUE")
        solde_actuel = citoyen_info.iloc[0]['Solde']
        job_raw = str(citoyen_info.iloc[0]['Emploiement'])
        
        st.metric("SOLDE ACTUEL", f"{solde_actuel:,}$")
        st.write(f"🏢 Métier : **{job_raw}**")

        # --- CALCULATEUR DE PAIE DÉTAILLÉ ---
        with st.expander("💳 Détails de la prochaine paie", expanded=False):
            # 1. Calcul du temps de service (Table Clock)
            m_pol, m_rct = 0, 0
            try:
                res_clock = conn.table("clock").select("*").eq("nom", target).execute()
                df_paie_clean = pd.DataFrame(res_clock.data)
                if not df_paie_clean.empty:
                    logs = df_paie_clean[df_paie_clean["statut"].str.contains("Valid", case=False, na=False)]
                    for _, r in logs.iterrows():
                        t_debut = pd.to_datetime(r["début"], dayfirst=True, errors='coerce')
                        t_fin = pd.to_datetime(r["fin"], dayfirst=True, errors='coerce')
                        if pd.notnull(t_debut) and pd.notnull(t_fin):
                            diff = (t_fin - t_debut).total_seconds() / 60
                            job_log = str(r["job"]).upper()
                            if "POL" in job_log: m_pol += diff
                            elif "RCT" in job_log: m_rct += diff
            except: pass

            # 2. Primes Métiers
            ratio_pol = min(m_pol/1200, 1.0)
            ratio_rct = min(m_rct/1200, 1.0)
            
            p_pol = int(3000 * ratio_pol) if "police" in job_raw.lower() else 0
            p_rct = int(2000 * ratio_rct) if "agent rct" in job_raw.lower() else 0
            p_staff = 4000 if "staff" in job_raw.lower() else 0
            p_averis = 2000 if "averis" in job_raw.lower() else 0
            p_sp = 1000 if "service public" in job_raw.lower() else 0
            
            # 3. Taxes Véhicules & Offre Trio
            mes_v = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
            count_rct = len(mes_v[mes_v["Assurance"].str.contains("RCT", na=False, case=False)])
            is_trio = count_rct >= 3
            taxe_v = 200 if is_trio else (len(mes_v) * 150)

            # 4. Total NET
            net_final = 15000 + p_pol + p_rct + p_staff + p_averis + p_sp - taxe_v

            # Affichage des lignes
            st.markdown(f"➕ **Base Civile** : `15,000$`")
            if p_staff > 0: st.markdown(f"⭐ **Prime Staff** : `{p_staff}$`")
            if p_averis > 0: st.markdown(f"🛡️ **Prime Averis** : `{p_averis}$` (via Moune2010)")
            if p_pol > 0: st.markdown(f"👮 **Prime Police** : `{p_pol}$` ({int(m_pol/60)}h/20h)")
            if p_rct > 0: st.markdown(f"👷 **Prime RCT** : `{p_rct}$` ({int(m_rct/60)}h/20h)")
            
            st.markdown(f"🚗 **Taxe Véhicules** : `-{taxe_v}$` " + ("(Offre Trio ✅)" if is_trio else f"({len(mes_v)} immat.)"))
            
            st.divider()
            st.markdown(f"### NET : {int(net_final):,}$")
# ---------------- COLONNE 3 : ARCHIVES DÉTAILLÉES ----------------
    with col3:
        st.markdown("### 📁 ARCHIVES")
        try:
            # Récupération des factures payées (Vérifie bien la majuscule "Factures")
            res_f = conn.table("Factures").select("*").eq("Cible", target).eq("Statut", "PAYÉ").execute()
            archives = pd.DataFrame(res_f.data).fillna("N/A")
            
            if not archives.empty:
                # On trie par ID pour avoir les dernières en haut
                archives = archives.sort_values(by="ID", ascending=False)
                
                st.write(f"Derniers paiements ({len(archives)}) :")
                
                for _, f in archives.head(8).iterrows(): # On passe à 8 pour plus de visibilité
                    # On définit une date propre si elle existe, sinon on met "Date inconnue"
                    date_f = f.get('created_at', '---')
                    if date_f != '---':
                        date_f = date_f.split('T')[0] # On garde juste AAAA-MM-JJ

                    st.markdown(f"""
                        <div style="border: 1px solid #e0e0e0; border-left: 5px solid #2e7d32; padding: 10px; border-radius: 5px; background: #ffffff; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #666; font-size: 0.75em; font-family: monospace;">#{f['ID']}</span>
                                <span style="background: #d4edda; color: #155724; font-size: 0.7em; padding: 2px 6px; border-radius: 10px; font-weight: bold;">PAYÉE</span>
                            </div>
                            <div style="margin-top: 5px;">
                                <b style="color: #1a1a1a; font-size: 0.9em;">{f['Motif']}</b>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 8px; border-top: 1px solid #f0f0f0; pt: 5px;">
                                <div style="color: #444; font-size: 0.85em;">
                                    👤 <small>Par: {f.get('Auteur', 'Inconnu')}</small>
                                </div>
                                <div style="color: #2e7d32; font-weight: bold; font-size: 1em;">
                                    {f['Montant']:,}$
                                </div>
                            </div>
                            <div style="text-align: right; color: #999; font-size: 0.7em; margin-top: 3px;">
                                📅 {date_f}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun historique de paiement trouvé.")
        except Exception as e:
            st.error(f"Erreur lors de la lecture des archives : {e}")
# ======================================================================================
# 7. LOGIQUE DES ONGLETS (CORRIGÉE)
# ======================================================================================

# ======================================================================================
# NOUVEAU : SYSTÈME DE PAIEMENT DES FACTURES (STYLE TICKET)
# ======================================================================================
# Version Supabase pour remplacer ta ligne Google Sheets
df_all_f = pd.DataFrame(conn.table("Factures").select("*").execute().data).fillna("")
mes_factures = df_all_f[(df_all_f["Cible"] == target) & (df_all_f["Statut"] == "EN ATTENTE")]

if not mes_factures.empty:
    st.error(f"⚠️ {len(mes_factures)} FACTURE(S) EN ATTENTE DE PAIEMENT")
    
for _, fac in mes_factures.iterrows():
        # 1. CALCUL DU TIMER (VERSION ROBUSTE)
        try:
            # pd.to_datetime est magique : il comprend le format tout seul (avec ou sans secondes)
            # errors='coerce' évite le crash si la case est vide
            date_limite = pd.to_datetime(fac['Date_Limite'], dayfirst=True, errors='coerce')
            
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
                    t_color = "#f39c12" # Orange
                else:
                    timer_info = "⚠️ DÉLAI DÉPASSÉ (IMPAYÉ)"
                    t_color = "#d32f2f" # Rouge
            else:
                # Si la case dans Sheets est vide ou texte invalide
                timer_info = "⌛ Date invalide"
                t_color = "#555"
                
        except Exception:
            # Sécurité ultime pour ne pas bloquer l'affichage de la page
            timer_info = f"⌛ Échéance : {fac['Date_Limite']}"
            t_color = "#555"

        # 2. Ton affichage Streamlit ici (ex: st.markdown avec t_color et timer_info)
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

# On récupère les véhicules depuis la table immatriculations
try:
    res_v = conn.table("Copie de Immatriculations").select("*").eq("Nom d'utilisateur ROBLOX", target).execute()
    v_data = pd.DataFrame(res_v.data)
except:
    v_data = pd.DataFrame()

if not v_data.empty:
    v_cols = st.columns(3)
    for i, (_, veh) in enumerate(v_data.iterrows()):
        with v_cols[i % 3]:
            # --- RÉCUPÉRATION DE LA DATE ---
            date_display = str(veh.get('Horodateur', 'Non spécifiée'))

            # --- LOGIQUE DE SÉCURITÉ (RCT / AVERIS) ---
            assu = str(veh.get('Assurance', '')).upper()
            role = st.session_state.user_auth
            
            color = "green"
            status_txt = "✅ VÉHICULE EN RÈGLE"
            
            # Application de tes règles de couleurs selon l'assurance
            if role == "RCT":
                if "RCT" in assu:
                    color = "green"
                    status_txt = "✅ ASSURÉ RCT"
                elif "AVERIS" in assu:
                    color = "#E67E22" # Orange
                    status_txt = "⚠️ ATTENTION : ASSURÉ AVERIS"
                else:
                    color = "#d32f2f" # Rouge
                    status_txt = "🚨 DANGER : NON-ASSURÉ"

            # --- DESIGN TITRE DE CIRCULATION ---
            st.markdown(f"""
            <div style="border: 2px solid black; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; line-height: 1.2; box-shadow: 4px 4px 0px #eee;">
                <center><b>TITRE DE CIRCULATION</b><br><small>RÉPUBLIQUE DE RENSSERLAER</small></center>
                <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                <div style="font-size: 0.85em;">
                    <b>DATE :</b> {date_display}<br>
                    <b>NOM  :</b> {target}<br>
                    <b>MODÈLE:</b> {veh.get('Marque du véhicule', '')}<br>
                    <b>PLAQUE:</b> <span style="border: 1px solid black; padding: 0 3px; background: #f0f0f0;">{veh.get('Numéro de la plaque', '')}</span><br>
                    <b>ASSURANCE :</b> {veh.get('Assurance', '')}
                </div>
                <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                <div style="text-align: center; color: {color}; font-weight: bold; font-size: 0.8em;">
                    {status_txt}<br>
                    <small>Par le Terminal National</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
                                        
            # --- OPTION DE RADIATION ---
            with st.expander("🗑️ Radier"):
                plaque = veh['Numéro de la plaque']
                r_cod_check = st.text_input("Code Secret", type="password", key=f"rad_in_{plaque}_{i}")
                
                if st.button("CONFIRMER LA RADIATION", key=f"btn_rad_{plaque}_{i}", use_container_width=True):
                    # Vérification : Code correct OU utilisateur est Staff
                    if str(r_cod_check) == str(veh.get('CODE', '')) or st.session_state.user_auth in ["Staff", "Admin"]:
                        try:
                            # DELETE CIBLÉ SUR SUPABASE
                            conn.table("Copie de Immatriculations").delete().eq("Numéro de la plaque", plaque).execute()
                            
                            st.success(f"Véhicule {plaque} radié !")
                            record_log(st.session_state.user_auth, f"Radiation véhicule : {plaque} ({target})")
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur lors de la radiation : {e}")
                    else:
                        st.error("Code incorrect ou accès refusé.")
else:
    st.info("Aucun véhicule trouvé.")
# ======================================================================================
# 7. LOGIQUE DES ONGLETS (CORRIGÉE & ALIGNÉE)
# ======================================================================================
tab_labels = ["🚗 IMMATRICULATION"]
if st.session_state.user_auth in ["RCT", "Staff", "Admin"]: tab_labels.append("👮 SERVICES AGENT")
if st.session_state.user_auth in ["Staff", "Admin"]: tab_labels.append("🛠️ ADMINISTRATION")

tabs = st.tabs(tab_labels)

# --- ONGLET 1 : IMMATRICULATION & RADIATION ---
with tabs[0]:
    col_f, col_t = st.columns([1.3, 1], gap="medium")
    
    with col_f:
        st.markdown("### 📝 Gestion des Titres")
        
        with st.container(border=True):
            f_owner = st.selectbox("Propriétaire du véhicule", ["---"] + df_b["Nom Roblox"].tolist(), key="k_owner_v7")
            f_model = st.text_input("Marque / Modèle", key="k_model_v7", placeholder="Ex: Sentinel")
            f_plate = st.text_input("Numéro de Plaque", key="k_plate_v7", placeholder="Ex: AB-123-CD").upper()
            f_assu = st.selectbox("Type d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"], key="k_assu_v7")
            f_code = st.text_input("Code de Radiation (Secret)", type="password", key="k_code_v7", help="Ce code sera demandé pour supprimer le véhicule.")

            # --- VÉRIFICATION BLACKLIST RCT ---
            is_banned = False
            if "RCT" in f_assu and f_owner != "---":
                try:
                    res_bl = conn.table("blacklist_rct").select("*").eq("Nom", f_owner).execute()
                    if res_bl.data:
                        is_banned = True
                        st.error(f"🚫 **ACTION INTERDITE** : {f_owner} est banni de la RCT.")
                        st.warning(f"⚠️ **Motif :** {res_bl.data[0].get('Raison', 'Non spécifié')}")
                except: pass

            # --- CALCUL TAXE JEUNE ---
            val_taxe_jeune = 0
            if f_owner != "---":
                try:
                    date_brute = df_b[df_b["Nom Roblox"] == f_owner]["Date d'arrivée"].values[0]
                    # Conversion robuste de la date
                    date_arr = pd.to_datetime(date_brute, dayfirst=True)
                    if (datetime.now() - date_arr).days < 30:
                        val_taxe_jeune = 50
                        st.warning(f"🔰 JEUNE CONDUCTEUR détecté (+{val_taxe_jeune}$)")
                except: pass

            # --- CALCUL DU TOTAL & OFFRE TRIO ---
            taxe_gouv = 175
            taxe_assu = 130 if "AVERIS" in f_assu else (150 if "RCT" in f_assu else 0)
            
            if "RCT" in f_assu and f_owner != "---" and not is_banned:
                # On compte les véhicules déjà possédés
                nb_vehicules = len(df_i[df_i["Nom d'utilisateur ROBLOX"] == f_owner])
                if nb_vehicules >= 2:
                    taxe_assu = 0
                    st.success(f"🎁 OFFRE TRIO ACTIVÉE (Assurance offerte)")

            total_bill = taxe_gouv + taxe_assu + val_taxe_jeune

            # --- VALIDATION ---
            if st.button(f"S'ACQUITTER DE {total_bill}$ ET ENREGISTRER", 
                         use_container_width=True, 
                         type="primary", 
                         disabled=is_banned):
                
                if f_owner == "---" or not f_model or not f_plate or not f_code:
                    st.error("⚠️ Formulaire incomplet !")
                else:
                    try:
                        with st.spinner("Paiement en cours..."):
                            # 1. Vérification Solde
                            res_s = conn.table("Banque").select("Solde").eq("Nom Roblox", f_owner).execute()
                            solde_actuel = float(res_s.data[0]["Solde"])
                            
                            if solde_actuel < total_bill:
                                st.error(f"❌ Solde insuffisant ! ({solde_actuel}$)")
                            else:
                                # 2. Retrait argent Citoyen
                                conn.table("Banque").update({"Solde": solde_actuel - total_bill}).eq("Nom Roblox", f_owner).execute()
                                
                                # 3. Redirection des fonds (Taxes)
                                # L'immat (175$) + Taxe Jeune va toujours à la RCT (une10000)
                                # L'assurance va au service concerné
                                dest_assu = "Moune2010" if "AVERIS" in f_assu else "une10000"
                                
                                # Versement à la RCT (Frais fixes + Taxe Jeune + Assurance si RCT)
                                part_rct = taxe_gouv + val_taxe_jeune + (taxe_assu if dest_assu == "une10000" else 0)
                                res_rct = conn.table("Banque").select("Solde").eq("Nom Roblox", "une10000").execute()
                                conn.table("Banque").update({"Solde": float(res_rct.data[0]["Solde"]) + part_rct}).eq("Nom Roblox", "une10000").execute()
                                
                                # Versement à Averis si nécessaire
                                if dest_assu == "Moune2010" and taxe_assu > 0:
                                    res_av = conn.table("Banque").select("Solde").eq("Nom Roblox", "Moune2010").execute()
                                    conn.table("Banque").update({"Solde": float(res_av.data[0]["Solde"]) + taxe_assu}).eq("Nom Roblox", "Moune2010").execute()

                                # 4. Enregistrement Véhicule
                                nouvelle_immat = {
                                    "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                    "Nom d'utilisateur ROBLOX": f_owner,
                                    "Marque du véhicule": f_model,
                                    "Numéro de la plaque": f_plate,
                                    "Assurance": f_assu.split(" (")[0],
                                    "CODE": f_code,
                                    "Points": 25 # Initialisation points véhicule si besoin
                                }
                                conn.table("Copie de Immatriculations").insert(nouvelle_immat).execute()
                                
                                st.balloons()
                                st.success("✅ Immatriculation terminée et enregistrée !")
                                st.cache_data.clear()
                                time.sleep(2)
                                st.rerun()
                    except Exception as e:
                        st.error(f"Erreur technique : {e}")

    with col_t:
        st.markdown("### 🖼️ Aperçu du Titre")
        
        # Préparation variables aperçu
        date_ticket = datetime.now().strftime("%d/%m/%Y %H:%M")
        nom_u = f_owner if f_owner != "---" else "................"
        marque_v = f_model if f_model else "................"
        plaque_v = f_plate if f_plate else "........"
        assu_v = f_assu.split(" (")[0] if f_assu != "Aucune" else "NON ASSURÉ"

        ticket_html = f"""
        <div style='border: 2px dashed #000; padding: 20px; background-color: #fff; color: #000; font-family: "Courier New", monospace; height: 440px; box-shadow: 8px 8px 0px #eee;'>
            <div style='text-align:center;'>
                <b style='font-size:1.2em;'>TITRE DE CIRCULATION</b><br>
                <small>RÉPUBLIQUE DE RENSSERLAER</small>
                <hr style='border-top: 1px dashed #000; margin: 10px 0;'>
            </div>
            <div style='font-size: 0.9em; line-height: 1.4;'>
                <b>DATE :</b> {date_ticket}<br>
                <b>NOM  :</b> {nom_u}<br>
                <b>MODÈLE:</b> {marque_v}<br>
                <b>PLAQUE:</b> <span style='border:1px solid #000; padding:0 5px; background:#f0f0f0;'>{plaque_v}</span><br>
                <b>ASSU  :</b> {assu_v}
            </div>
            <hr style='border-top: 1px dashed #000; margin: 10px 0;'>
            <div style='font-size: 0.8em;'>
                <div style='display:flex; justify-content:space-between;'><span>Frais Immat.</span><span>175$</span></div>
                <div style='display:flex; justify-content:space-between;'><span>Service Assu.</span><span>{taxe_assu}$</span></div>
                <div style='display:flex; justify-content:space-between;'><span>Taxe Jeune</span><span>{val_taxe_jeune}$</span></div>
            </div>
            <div style='border-top: 2px solid #000; margin-top: 10px; padding-top: 5px; text-align: right;'>
                <b style='font-size:1.2em;'>TOTAL : {total_bill}$</b>
            </div>
            <div style='text-align:center; margin-top: 25px; font-size: 0.7em; border: 1px solid #ccc; padding: 5px;'>
                CERTIFIÉ PAR LE TERMINAL NATIONAL<br>TRANSACTION SÉCURISÉE
            </div>
        </div>
        """
        st.components.v1.html(ticket_html, height=480)

st.write("---")
# --- ONGLET 2 : SERVICES AGENTS (RCT / AVERIS / POLICE) ---
if len(tabs) > 1:
    with tabs[1]:
        # Vérification des accès (Agents et Staff)
        roles_autorises = ["RCT", "Averis", "Police", "Staff", "Admin"]
        if any(r in st.session_state.user_auth for r in roles_autorises):
            st.markdown("## 🛡️ Administration & Blacklist")
            
            with st.container(border=True):
                col_add, col_list = st.columns([1, 1.5], gap="large")
                
                # --- PARTIE GAUCHE : AJOUTER ---
                with col_add:
                    st.markdown("#### 🚫 Bannir un client")
                    # On utilise la table banque pour avoir la liste des citoyens
                    b_nom = st.selectbox("Citoyen à bannir", ["---"] + df_b["Nom Roblox"].tolist(), key="rct_ban_nom")
                    b_raison = st.text_area("Raison du bannissement", placeholder="Ex: Impayés récurrents, comportement...", key="rct_ban_raison")
                    
                    if st.button("🔴 AJOUTER À LA LISTE", use_container_width=True, type="primary"):
                        if b_nom != "---" and b_raison:
                            try:
                                with st.spinner("Mise à jour de la base..."):
                                    # 1. Vérifier si déjà banni
                                    check = conn.table("blacklist_rct").select("*").eq("Nom", b_nom).execute()
                                    
                                    if check.data:
                                        st.error(f"⚠️ {b_nom} est déjà dans la liste noire.")
                                    else:
                                        # 2. Insertion Supabase
                                        new_ban = {
                                            "Nom": b_nom, 
                                            "Raison": b_raison,
                                            "Agent": st.session_state.user_auth,
                                            "Date": datetime.now().strftime("%d/%m/%Y")
                                        }
                                        conn.table("blacklist_rct").insert(new_ban).execute()
                                        
                                        # 3. Log de l'action
                                        record_log(st.session_state.user_auth, f"BLACKLIST : {b_nom} pour {b_raison}")
                                        
                                        st.success(f"✅ {b_nom} a été banni avec succès.")
                                        st.cache_data.clear()
                                        time.sleep(1)
                                        st.rerun()
                            except Exception as e:
                                st.error(f"Erreur technique : {e}")
                        else:
                            st.warning("Veuillez remplir tous les champs.")

                # --- PARTIE DROITE : LISTE & UNBAN ---
                with col_list:
                    st.markdown("#### 📜 Liste Noire Actuelle")
                    try:
                        # Récupération en temps réel
                        res_bl = conn.table("blacklist_rct").select("*").execute()
                        df_show_bl = pd.DataFrame(res_bl.data)
                        
                        if not df_show_bl.empty:
                            # On affiche une version propre
                            st.dataframe(
                                df_show_bl[["Nom", "Raison", "Date"]], 
                                use_container_width=True, 
                                hide_index=True, 
                                height=250
                            )
                            
                            st.divider()
                            st.markdown("#### 🔓 Débannissement")
                            unban_nom = st.selectbox("Sélectionner un citoyen", ["---"] + df_show_bl["Nom"].tolist(), key="unban_select")
                            
                            if st.button("🟢 RÉAUTORISER LE CLIENT", use_container_width=True):
                                if unban_nom != "---":
                                    # Suppression ciblée
                                    conn.table("blacklist_rct").delete().eq("Nom", unban_nom).execute()
                                    
                                    record_log(st.session_state.user_auth, f"UNBLACKLIST : {unban_nom}")
                                    st.success(f"✅ {unban_nom} est de nouveau autorisé.")
                                    st.cache_data.clear()
                                    time.sleep(1)
                                    st.rerun()
                        else:
                            st.info("ℹ️ La liste noire est actuellement vide.")
                    except Exception as e:
                        st.error(f"Erreur de lecture : {e}")
        else:
            st.error("Accès restreint aux Agents et au Staff.")
# --- 1. AUTHENTIFICATION & POINTAGE ---
with st.container(border=True):
    c_auth, c_stats = st.columns([1, 2.5])
    
    with c_auth:
        # Nettoyage du code saisi
        agent_code_saisi = st.text_input("🔑 Code Agent", type="password", key="main_agent_auth").strip()
    
    agent_identifie = None
    en_service = False
    
    if agent_code_saisi:
        # Recherche de l'agent dans df_b (chargé depuis Supabase)
        # On s'assure que la colonne Code est traitée comme du texte propre
        res_agent = df_b[df_b["Code"].astype(str).str.contains(agent_code_saisi, na=False)]
        
        if not res_agent.empty:
            agent_identifie = res_agent.iloc[0]["Nom Roblox"]
            agent_role = res_agent.iloc[0]["Role"] # On récupère le rôle pour les bonus
            
            # --- Lecture de la session active sur Supabase ---
            res_clock = conn.table("Clock").select("*").eq("nom", agent_identifie).eq("statut", "en cours").execute()
            session_active = res_clock.data
            en_service = len(session_active) > 0

            with c_stats:
                st.markdown(f"### 🎖️ Agent : {agent_identifie}")
                h_actuelle = datetime.now().strftime("%H:%M")
                m_actuelle, m_debut, m_fin = st.columns(3)
                m_actuelle.metric("Heure Actuelle", h_actuelle)
                
                if en_service:
                    h_deb_brute = session_active[0]['debut']
                    # Formatage pour l'affichage (HH:MM)
                    h_deb_clean = h_deb_brute.split(' ')[1][:5] if ' ' in h_deb_brute else h_deb_brute[:5]
                    m_debut.metric("Heure de Début", h_deb_clean)
                    
                    try:
                        # Calcul de la durée
                        diff = datetime.now() - datetime.strptime(h_deb_brute, "%d/%m/%Y %H:%M:%S")
                        duree_min = int(diff.total_seconds() / 60)
                        m_fin.metric("Temps de Service", f"{duree_min} min")
                    except:
                        m_fin.metric("Temps de Service", "Calcul...")
                else:
                    m_debut.metric("Heure de Début", "--:--")
                    m_fin.metric("Temps de Service", "0 min")

            st.divider()

            # --- LOGIQUE DE JOB & BONUS ---
            # Détermination du job auto selon le rôle
            job_auto = "RCT"
            if "Staff" in agent_role or "Admin" in agent_role: job_auto = "STAFF"
            elif "Averis" in agent_role: job_auto = "AVERIS"
            elif "Police" in agent_role: job_auto = "POLICE"
            
            if not en_service:
                st.info(f"💡 Prêt à prendre votre service en tant que **{job_auto}** ?")
                if st.button(f"▶️ DÉBUT DE SERVICE", use_container_width=True, type="primary"):
                    h_deb = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    new_clock = {
                        "nom": agent_identifie,
                        "action": "SERVICE",
                        "job": job_auto,
                        "debut": h_deb,
                        "statut": "en cours",
                        "role_at_time": agent_role # Pour historique des bonus
                    }
                    conn.table("Clock").insert(new_clock).execute()
                    st.toast("Service démarré !")
                    time.sleep(1)
                    st.rerun()
            else:
                # Calcul des primes si Staff (Exemple: bonus de présence)
                bonus_text = ""
                if job_auto == "STAFF":
                    bonus_text = " (+ Bonus Staff inclus)"
                
                st.warning(f"🚨 Session **{job_auto}** en cours{bonus_text}.")
                
                if st.button(f"⏹️ FIN DE SERVICE", use_container_width=True):
                    h_fin = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    # Mise à jour de la session dans Supabase
                    conn.table("Clock").update({
                        "fin": h_fin,
                        "statut": "à valider"
                    }).eq("id", session_active[0]['id']).execute()
                    
                    st.success(f"✅ Session {job_auto} terminée. En attente de validation.")
                    time.sleep(1)
                    st.rerun()
        else:
            st.error("❌ Code Agent Invalide ou introuvable.")
# --- 2. RECHERCHE & CONSULTATION DES FACTURES ---
st.markdown("### 📑 GESTION DES FACTURES")

try:
    # Lecture en temps réel via Supabase
    res_f = conn.table("Factures").select("*").execute()
    df_f_check = pd.DataFrame(res_f.data)
    
    if not df_f_check.empty:
        maintenant = datetime.now()
        # Conversion sécurisée des dates
        df_f_check['Date_Limite_DT'] = pd.to_datetime(df_f_check['Date_Limite'], dayfirst=True, errors='coerce')
        
        def determiner_statut(row):
            s_db = str(row["Statut"]).strip().upper()
            # On gère les variantes de saisie
            statuts_regles = ["PAYÉ", "PAYÉE", "REMBOURSÉ", "REMBOURSÉE", "ANNULÉ", "ANNULÉE"]
            if s_db in statuts_regles: 
                return s_db
            if pd.notnull(row['Date_Limite_DT']) and maintenant > row['Date_Limite_DT']:
                return "EN RETARD"
            return "EN ATTENTE"
        
        df_f_check["Statut_Reel"] = df_f_check.apply(determiner_statut, axis=1)
        
        # --- RADAR AUTOMATIQUE DES RETARDS ---
        df_retards_auto = df_f_check[df_f_check["Statut_Reel"] == "EN RETARD"]
        
        if not df_retards_auto.empty:
            with st.expander(f"🚨 ALERTES : {len(df_retards_auto)} RETARDS DÉTECTÉS", expanded=True):
                for _, row in df_retards_auto.sort_values(by="Date_Limite_DT").iterrows():
                    st.error(f"**[REF: {row['id']}]** {row['Cible']} — **{row['Montant']}$** (Limite était le : {row['Date_Limite']})")
        else:
            st.success("✅ Aucune facture en retard pour le moment.")
        
        # --- ZONE DE FILTRES ---
        with st.container(border=True):
            c_s1, c_s2 = st.columns([2, 1])
            search_f = c_s1.text_input("🔍 Rechercher un dossier", placeholder="Nom du citoyen, ID...", key="search_ui")
            filter_f = c_s2.selectbox("Filtrer par état", ["---", "En Attente", "En Retard", "Payé", "Remboursé", "Annulé"])
        
        # --- LOGIQUE DE FILTRAGE ---
        df_filtered = df_f_check.copy()
        
        if search_f:
            query = search_f.lower()
            df_filtered = df_filtered[
                (df_filtered["id"].astype(str).str.contains(query)) | 
                (df_filtered["Cible"].str.lower().str.contains(query)) |
                (df_filtered["Motif"].str.lower().str.contains(query))
            ]
            
        if filter_f != "---":
            f_val = filter_f.upper()
            if f_val == "PAYÉ": 
                df_filtered = df_filtered[df_filtered["Statut_Reel"].str.startswith("PAY")]
            elif f_val == "REMBOURSÉ": 
                df_filtered = df_filtered[df_filtered["Statut_Reel"].str.startswith("REMBOURS")]
            elif f_val == "ANNULÉ": 
                df_filtered = df_filtered[df_filtered["Statut_Reel"].str.startswith("ANNUL")]
            else: 
                df_filtered = df_filtered[df_filtered["Statut_Reel"] == f_val]

        # --- AFFICHAGE DES RÉSULTATS ---
        if not df_filtered.empty:
            st.write(f"🔍 {len(df_filtered)} dossier(s) trouvé(s) :")
            for _, row in df_filtered.iterrows():
                s = row["Statut_Reel"]
                
                # Code couleur dynamique
                color = "#27ae60" if "PAY" in s else "#3498db" if "REMBOURS" in s else "#95a5a6" if "ANNUL" in s else "#e74c3c" if s == "EN RETARD" else "#f39c12"
                
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"""
                            <div style="border-left: 5px solid {color}; padding-left: 15px;">
                                <b style="color:{color}; font-size: 1.1em;">{s} — RÉF : {row['id']}</b><br>
                                <span style="font-size: 1.2em; font-weight: bold;">{row['Cible']}</span><br>
                                <small>📅 Limite : {row['Date_Limite']} | Motif : {row['Motif']}</small>
                            </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<h2 style='text-align: center; color: #333;'>{row['Montant']}$</h2>", unsafe_allow_html=True)
                        # Optionnel : Bouton pour voir les détails si Staff
                        if st.session_state.user_auth in ["Staff", "Admin"]:
                            if st.button("Détails", key=f"det_{row['id']}"):
                                st.info(f"Émise par : {row.get('Emetteur', 'Inconnu')}")
        else:
            st.warning("🔎 Aucun dossier ne correspond à votre recherche.")
            
    else:
        st.info("📭 Aucune facture enregistrée dans la base de données.")

except Exception as e:
    st.error(f"⚠️ Erreur lors de la récupération des factures : {e}")
# --- 2. RECHERCHE & MANDATS ---
st.markdown("### 🔍 MANDATS & RECHERCHE")

with st.container(border=True):
    st.markdown("#### 📝 Lancer un Mandat d'Arrêt")
    c1, c2, c3 = st.columns([1.5, 2, 1])
    
    with c1:
        # Liste des citoyens via la table banque déjà chargée (df_b)
        liste_citoyens = sorted(df_b["Nom Roblox"].unique().tolist())
        cible_mandat = st.selectbox("Suspect", ["---"] + liste_citoyens, key="mandat_cible")
    
    with c2:
        motif_mandat = st.text_input("Motif de recherche", placeholder="Ex: Braquage, délit de fuite...", key="mandat_motif")
    
    with c3:
        st.write(" ")
        if st.button("🚨 LANCER L'ALERTE", use_container_width=True, type="primary"):
            if cible_mandat != "---" and motif_mandat:
                try:
                    # Mise à jour directe dans Supabase (Table Banque)
                    conn.table("Banque").update({
                        "Statut": "RECHERCHÉ",
                        "Motif Recherche": motif_mandat
                    }).eq("Nom Roblox", cible_mandat).execute()
                    
                    record_log(st.session_state.user_auth, f"MANDAT : Alerte lancée contre {cible_mandat}")
                    st.success(f"🚨 Mandat enregistré contre {cible_mandat} !")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")
            else:
                st.error("Champs requis !")

col_m1, col_m2 = st.columns([2, 1], gap="medium")

with col_m1:
    with st.container(border=True):
        st.markdown("#### 📢 Alertes Actives")
        # Filtrage en temps réel sur le DataFrame local mis à jour
        recherches = df_b[df_b["Statut"].str.upper().str.contains("RECHERCHÉ", na=False)]
        
        if not recherches.empty:
            for _, crim in recherches.iterrows():
                with st.container(border=True):
                    c1_r, c2_r = st.columns([3, 1])
                    c1_r.warning(f"🚨 **{crim['Nom Roblox']}**\n\n**Motif :** {crim.get('Motif Recherche', 'Non spécifié')}")
                    
                    if c2_r.button("Interpellé", key=f"rel_{crim['Nom Roblox']}", use_container_width=True):
                        # Levée du mandat
                        conn.table("Banque").update({
                            "Statut": "RAS",
                            "Motif Recherche": ""
                        }).eq("Nom Roblox", crim["Nom Roblox"]).execute()
                        
                        record_log(st.session_state.user_auth, f"INTERPELLATION : {crim['Nom Roblox']}")
                        st.success("Statut mis à jour.")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
        else: 
            st.success("✅ Aucun mandat actif sur le territoire.")

with col_m2:
    with st.container(border=True):
        st.markdown("#### 🔦 Scanner Plaque")
        p_search = st.text_input("Saisir plaque", key="plate_ui", placeholder="AB-123-CD").upper().strip()
        
        if p_search:
            # Recherche dans la table immatriculations (df_i)
            m = df_i[df_i["Numéro de la plaque"].astype(str).str.contains(p_search, na=False)]
            
            if not m.empty:
                nom_proprio = m.iloc[0]["Nom d'utilisateur ROBLOX"]
                vehicule = m.iloc[0]['Marque du véhicule']
                
                # Vérification croisée du statut du propriétaire
                info_proprio = df_b[df_b["Nom Roblox"] == nom_proprio]
                is_wanted = False
                if not info_proprio.empty:
                    is_wanted = "RECHERCHÉ" in str(info_proprio.iloc[0]["Statut"]).upper()

                if is_wanted:
                    st.error(f"⚠️ **ALERTE : PROPRIÉTAIRE RECHERCHÉ**")
                else:
                    st.success("✅ Véhicule en règle")
                
                st.markdown(f"""
                **👤 Proprio :** {nom_proprio}  
                **🚘 Modèle :** {vehicule}  
                **🛡️ Points :** {m.iloc[0].get('Points', 'N/A')}/25
                """)
            else: 
                st.error("❌ Plaque inconnue ou non enregistrée.")
# --- 3. INTERVENTION SUR CITOYEN (VERSION FINALE ET COMPLÈTE) ---
st.divider()

if target == "---":
    st.warning("⚠️ Sélectionnez un citoyen en haut de la page pour ouvrir le module d'intervention.")
else:
    # Sécurité : Vérification de l'identification de l'agent
    if not agent_identifie:
        st.info("🔒 Veuillez pointer votre code agent ci-dessus pour accéder à la facturation.")
    else:
        st.markdown(f"### ⚡ INTERVENTION : {target.upper()}")
        
        # --- Création des colonnes d'action ---
        col_form, col_facture, col_vehicules = st.columns([1.2, 1, 1], gap="medium")
        
        # --- COLONNE 1 : FORMULAIRE D'ACTION (LOGIQUE & ALERTES) ---
        with col_form:
            with st.container(border=True):
                # 1. Gestion de l'émetteur selon les droits d'accès
                if st.session_state.user_auth == "Staff":
                    f_emetteur = st.selectbox("Émetteur", ["POLSTA", "Averis", "RCT"], key="em_ui")
                elif "Averis" in st.session_state.user_auth:
                    f_emetteur = "Averis"
                    st.info(f"🏢 **Émetteur :** {f_emetteur}")
                else:
                    f_emetteur = "RCT"
                    st.info(f"🏢 **Émetteur :** {f_emetteur}")
                
                # 2. Paramètres de l'infraction
                f_val = st.number_input("Amende ($)", 0, 100000, 500, step=100)
                
                # Le retrait de points n'est actif que pour le Staff en mode POLSTA
                can_pull_points = (st.session_state.user_auth == "Staff" and f_emetteur == "POLSTA")
                f_pts = st.slider("Retrait de points", 0, 25, 0, disabled=not can_pull_points)
                
                f_motif = st.text_area("Motif détaillé", key="mot_ui", placeholder="Décrivez l'infraction (ex: Excès de vitesse, défaut d'assurance...)")
                
                # 3. Association au véhicule
                target_veh = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
                f_plate = st.selectbox("Véhicule lié", ["AUCUN"] + target_veh["Numéro de la plaque"].tolist())
                
                # 4. Bouton d'envoi et traitement de la donnée
                if st.button("🚨 ENVOYER FACTURE", use_container_width=True, type="primary"):
                    if f_motif:
                        with st.spinner("Transmission au central..."):
                            import random
                            # Chargement des factures
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
                            
                            # Logique de retrait de points (Table Points Permis)
                            if f_pts > 0 and can_pull_points:
                                try:
                                    df_p = cloud_conn.read(worksheet="Points Permis")
                                    idx_p = df_p[df_p["Nom Roblox"] == target].index[0]
                                    df_p.at[idx_p, "PTS"] = max(0, int(df_p.at[idx_p, "PTS"]) - f_pts)
                                    cloud_conn.update(worksheet="Points Permis", data=df_p)
                                except: pass
                            
                            # Enregistrement final
                            updated_f = pd.concat([df_all_f, pd.DataFrame([new_f])], ignore_index=True)
                            cloud_conn.update(worksheet="Factures", data=updated_f)
                            
                            st.success(f"✅ PV enregistré par {agent_identifie}")
                            time.sleep(1); st.rerun()
                    else:
                        st.error("❌ Le motif est obligatoire pour valider l'infraction.")

            # --- SECTION ALERTES VIGILANCE (SOUS LE FORMULAIRE) ---
            citoyen_info = df_b[df_b["Nom Roblox"] == target]
            is_wanted = "RECHERCHÉ" in str(citoyen_info.iloc[0].get("Statut", "")).upper() if not citoyen_info.empty else False
            motif_recherche = citoyen_info.iloc[0].get("Motif Recherche", "Non spécifié") if is_wanted else ""
            
            # Calcul dynamique de la dette impayée
            df_check_f = cloud_conn.read(worksheet="Factures").fillna("")
            impayes = df_check_f[(df_check_f["Cible"] == target) & (df_check_f["Statut"] == "EN ATTENTE")]
            total_dette = impayes["Montant"].astype(int).sum() if not impayes.empty else 0

            st.markdown("""
                <style>
                @keyframes pulse-red { 
                    0% { box-shadow: 0 0 0 0px rgba(211, 47, 47, 0.7); border-color:white; } 
                    50% { box-shadow: 0 0 0 15px rgba(211, 47, 47, 0); border-color:red; } 
                    100% { box-shadow: 0 0 0 0px rgba(211, 47, 47, 0); border-color:white; } 
                }
                .alert-mandat { background-color: #d32f2f; color: white; padding: 15px; border-radius: 10px; border: 2px solid white; animation: pulse-red 1s infinite; text-align: center; margin-top:10px; font-weight: bold;}
                .alert-dette { background-color: #e67e22; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-top:5px; border: 1px solid white; }
                </style>
            """, unsafe_allow_html=True)
            
            if is_wanted:
                st.markdown(f'<div class="alert-mandat">🚨 INDIVIDU RECHERCHÉ 🚨<br><small>{motif_recherche.upper()}</small></div>', unsafe_allow_html=True)
            if total_dette > 0:
                st.markdown(f'<div class="alert-dette">⚠️ DETTE TOTALE : {total_dette}$ (Factures en attente)</div>', unsafe_allow_html=True)

        # --- COLONNE 2 : APERÇU DE LA FACTURE (STYLE TICKET COURIER) ---
        with col_facture:
            st.markdown("#### 📄 Aperçu du Ticket")
            header_ticket = "FACTURE AVERIS" if f_emetteur == "Averis" else "FACTURE OFFICIELLE"
            
            st.markdown(f"""
            <div style="border: 2px solid black; padding: 20px; background: white; color: black; font-family: 'Courier New', monospace; line-height: 1.3; box-shadow: 5px 5px 0px #444;">
                <center>
                    <b style="font-size:1.2em;">{header_ticket}</b><br>
                    <small>RÉPUBLIQUE DE RENSSERLAER</small>
                </center>
                <hr style="border-top: 2px dashed black; margin: 15px 0;">
                <div style="font-size: 0.9em;">
                    <b>SIGNATAIRE :</b> {agent_identifie.upper()}<br>
                    <b>ÉMETTEUR   :</b> {f_emetteur.upper()}<br>
                    <b>DATE        :</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
                    <b>NOM         :</b> {target}<br>
                    <b>MOTIF       :</b> {f_motif.upper() if f_motif else 'EN ATTENTE...'}<br>
                    <b>PLAQUE      :</b> <span style="border: 1px solid black; padding: 0 4px; font-weight:bold;">{f_plate}</span><br>
                    <br>
                    <b style="font-size:1.1em;">MONTANT : {f_val}$</b>
                </div>
                <hr style="border-top: 2px dashed black; margin: 15px 0;">
                <div style="text-align: center;">
                    <b style="font-size:1.1em;">POINTS : -{f_pts if can_pull_points else 0}</b><br>
                    <small>Ce document fait foi de preuve officielle.<br>Paiement requis sous 24h.</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # --- COLONNE 3 : VÉHICULES DU CITOYEN (TITRES DE CIRCULATION) ---
        with col_vehicules:
            st.markdown("#### 🚗 État des Véhicules")
            if not target_veh.empty:
                for _, veh in target_veh.iterrows():
                    assu_v = str(veh['Assurance']).upper()
                    
                    # Logique de badges couleur pour l'assurance
                    if "RCT" in assu_v:
                        col_v, txt_v = "#27ae60", "✅ ASSURÉ RCT"
                    elif "AVERIS" in assu_v:
                        col_v, txt_v = "#E67E22", "⚠️ ASSURÉ AVERIS"
                    elif any(word in assu_v for word in ["OUI", "✅"]):
                        col_v, txt_v = "#27ae60", "✅ ASSURANCE OK"
                    else:
                        col_v, txt_v = "#d32f2f", "🚨 DÉFAUT D'ASSURANCE"

                    st.markdown(f"""
                    <div style="border: 2px solid black; padding: 12px; background: #f9f9f9; color: black; font-family: 'Courier New', monospace; margin-bottom: 12px; font-size: 0.85em; border-left: 5px solid {col_v};">
                        <center><b>TITRE DE CIRCULATION</b></center>
                        <hr style="border-top: 1px solid #ccc; margin: 8px 0;">
                        <b>MODÈLE :</b> {veh['Marque du véhicule']}<br>
                        <b>PLAQUE :</b> <span style="background: white; border: 1px solid black; padding: 0 3px; font-weight:bold;">{veh['Numéro de la plaque']}</span><br>
                        <hr style="border-top: 1px solid #ccc; margin: 8px 0;">
                        <div style="text-align: center; color: {col_v}; font-weight: bold; font-size:1em;">
                            {txt_v}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun véhicule enregistré pour ce citoyen.")
# ======================================================================================
# --- ONGLET 3 : ADMINISTRATION (STAFF UNIQUEMENT) ---
# ======================================================================================

if len(tabs) > 2:
    with tabs[2]:
        # Protection silencieuse : seuls les Staff voient le contenu
        if st.session_state.user_auth == "Staff":
            st.markdown("## 🛠️ ADMINISTRATION GÉNÉRALE")
            st.info("Espace réservé à la gestion nationale, validation des services et paies.")
            
            # --- A. MODULE DE VALIDATION DES HEURES (CLOCK) ---
            st.divider()
            st.subheader("🛡️ Validation des Services")
            
            try:
                df_admin_clock = cloud_conn.read(worksheet="Clock", ttl=0).fillna("")
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
                                time.sleep(0.5); st.rerun()
                                
                            if col_r.button("❌", key=f"refus_{i}"):
                                df_admin_clock.at[i, "statut"] = "Refusé"
                                cloud_conn.update(worksheet="Clock", data=df_admin_clock)
                                st.warning("Service refusé.")
                                time.sleep(0.5); st.rerun()
                else:
                    st.info("✅ Aucun service en attente de validation.")
            except Exception as e:
                st.error(f"Erreur Clock : {e}")

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

                if st.button("🆕 CRÉER LE DOSSIER", use_container_width=True, type="primary"):
                    if new_name:
                        # Règle : Date automatique
                        today_str = datetime.now().strftime("%d/%m/%Y")
                        
                        new_row_bank = pd.DataFrame([{
                            "Nom Roblox": new_name,
                            "Nom Discord": new_discord,
                            "Solde": 15000, # Règle : Solde de départ 15k
                            "Emploiement": " / ".join(new_jobs),
                            "Date d'arrivée": today_str,
                            "Statut": "RAS",
                            "Code": f"{new_name}123",
                            "Motif Recherche": ""
                        }])
                        
                        new_row_pts = pd.DataFrame([{"Nom Roblox": new_name, "PTS": new_pts, "Validité": "OUI"}])
                        
                        try:
                            df_b_updated = pd.concat([df_b, new_row_bank], ignore_index=True)
                            df_p_updated = pd.concat([df_p, new_row_pts], ignore_index=True)
                            cloud_conn.update(worksheet="Banque", data=df_b_updated)
                            cloud_conn.update(worksheet="Points Permis", data=df_p_updated)
                            st.success(f"✅ Dossier créé pour {new_name} (Solde : 15,000$)")
                            time.sleep(1); st.rerun()
                        except Exception as e:
                            st.error(f"Erreur : {e}")
                    else:
                        st.error("Veuillez saisir au moins le nom Roblox.")

            # --- C. GESTION DES PAIES & BONUS (STAFF) ---
            st.divider()
            st.subheader("💰 Gestion des Paies & Bonus")
            
            with st.expander("Ouvrir le calculateur de paie"):
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    target_paie = st.selectbox("Sélectionner le bénéficiaire", df_b["Nom Roblox"].tolist())
                    montant_base = st.number_input("Salaire de base ($)", 0, 50000, 2500)
                with c_p2:
                    bonus_staff = st.number_input("Bonus Staff / Primes ($)", 0, 10000, 0)
                    motif_paie = st.text_input("Motif de la paie", "Salaire Hebdomadaire")
                
                total_paie = montant_base + bonus_staff
                st.markdown(f"### Total à verser : **{total_paie}$**")
                
                if st.button("💸 VERSER LA PAIE", use_container_width=True):
                    try:
                        idx = df_b[df_b["Nom Roblox"] == target_paie].index[0]
                        df_b.at[idx, "Solde"] = int(df_b.at[idx, "Solde"]) + total_paie
                        cloud_conn.update(worksheet="Banque", data=df_b)
                        
                        st.success(f"✅ {total_paie}$ versés à {target_paie}")
                        
                        # Note spécifique Averis
                        if "Averis" in df_b.at[idx, "Emploiement"]:
                            st.info("ℹ️ Note : Transaction notifiée à la direction Averis (Moune2010).")
                            
                        time.sleep(1); st.rerun()
                    except Exception as e:
                        st.error(f"Erreur de virement : {e}")
# ======================================================================================
# --- SECTION C : SURVEILLANCE DU CUMUL DES HEURES ---
# ======================================================================================
st.divider()
st.markdown("### 📊 Surveillance du Cumul des Heures")
st.caption("Visualisation du temps de service accumulé par les agents (validé mais non payé).")

with st.container(border=True):
    # Récupération de la liste des agents ayant des logs
    list_agents = sorted(df_admin_clock["nom"].unique().tolist()) if not df_admin_clock.empty else []
    agent_view = st.selectbox("🔍 Sélectionner un agent pour vérification :", ["---"] + list_agents, key="cumul_view_select")

    if agent_view != "---":
        # Extraction des logs validés (on considère que 'validé' signifie en attente de paie)
        logs_view = df_admin_clock[(df_admin_clock["nom"] == agent_view) & (df_admin_clock["statut"] == "Validé")]
        
        v_min_rct, v_min_pol = 0, 0
        
        for _, r in logs_view.iterrows():
            try:
                t_deb = datetime.strptime(str(r["début"]), "%d/%m/%Y %H:%M:%S")
                t_fin = datetime.strptime(str(r["fin"]), "%d/%m/%Y %H:%M:%S")
                duree = (t_fin - t_deb).total_seconds() / 60
                
                if "RCT" in str(r["job"]).upper(): 
                    v_min_rct += duree
                elif "POL" in str(r["job"]).upper() or "POLICE" in str(r["job"]).upper(): 
                    v_min_pol += duree
            except: 
                continue

        # --- CALCUL DES GAINS (Exemple : Prime Max à 15h / 900 min) ---
        # RCT : Max 2000$ | Police : Max 3000$
        v_earn_rct = int(2000 * min(v_min_rct / 900, 1.0))
        v_earn_pol = int(3000 * min(v_min_pol / 900, 1.0))

        # Affichage des metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Minutes RCT", f"{int(v_min_rct)} min", f"+{v_earn_rct}$")
        m2.metric("Minutes Police", f"{int(v_min_pol)} min", f"+{v_earn_pol}$")
        
        total_primes = v_earn_rct + v_earn_pol
        m3.metric("Total Primes", f"{total_primes}$", f"{len(logs_view)} sessions", delta_color="normal")

        if not logs_view.empty:
            with st.expander("📄 Voir le détail des sessions validées"):
                # On affiche un tableau propre
                st.dataframe(logs_view[["job", "début", "fin"]], use_container_width=True)
                
                st.info("💡 Utilisez ces montants dans le 'Calculateur de paie' ci-dessus pour verser le salaire.")
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
        # 1. Récupération des données du profil
        user_data = df_b[df_b["Nom Roblox"] == target_paie].iloc[0]
        user_jobs = str(user_data.get("Emploiement", ""))
        
        try: 
            solde_actuel = float(str(user_data.get("Solde", 0)).replace('$', '').replace(',', '').strip())
        except: 
            solde_actuel = 0.0

        # 2. Calcul des primes basées sur les heures VALIDÉES (non payées)
        logs_paie = df_admin_clock[(df_admin_clock["nom"] == target_paie) & (df_admin_clock["statut"] == "Validé")]
        min_rct, min_pol = 0, 0
        
        for _, r in logs_paie.iterrows():
            try:
                d = (datetime.strptime(str(r["fin"]), "%d/%m/%Y %H:%M:%S") - 
                     datetime.strptime(str(r["début"]), "%d/%m/%Y %H:%M:%S")).total_seconds() / 60
                if "RCT" in str(r["job"]).upper(): min_rct += d
                elif "POL" in str(r["job"]).upper(): min_pol += d
            except: continue

        # 3. Barème financier (Base + Primes + Bonus Staff)
        base_sal = 15000
        p_rct = int(2000 * min(min_rct / 1200, 1.0)) # Prime max à 20h
        p_pol = int(3000 * min(min_pol / 1200, 1.0))
        
        b_staff = 4000 if "Staff" in user_jobs else 0
        b_averis = 2000 if "Averis" in user_jobs else 0
        b_sp = 1000 if "Service Public" in user_jobs else 0
        
        total_brut = base_sal + p_rct + p_pol + b_staff + b_averis + b_sp

        # 4. Déductions (Assurances)
        user_vehs = df_i[df_i["Nom d'utilisateur ROBLOX"] == target_paie]
        c_averis, c_std, count_rct_cars = 0, 0, 0
        
        for _, v in user_vehs.iterrows():
            assu = str(v.get("Assurance", "")).upper()
            if "RCT" in assu: count_rct_cars += 1
            elif "AVERIS" in assu: c_averis += 130
            else: c_std += 150
        
        c_rct_final = 300 if count_rct_cars >= 2 else count_rct_cars * 150
        total_deduc = c_rct_final + c_averis + c_std
        net_to_pay = total_brut - total_deduc

        # --- AFFICHAGE DE LA FICHE ---
        st.markdown(f"#### 📄 Fiche de Paie : {target_paie}")
        col_a, col_b, col_c, col_d = st.columns(4)
        
        col_a.metric("💸 BASE", f"{base_sal}$")
        col_b.metric("⏱️ PRIMES", f"{p_rct + p_pol}$", f"RCT+Pol")
        col_c.metric("🌟 BONUS", f"{b_staff + b_averis + b_sp}$", "Staff/Av/SP")
        col_d.metric("📉 TAXES", f"-{total_deduc}$", "Assurances", delta_color="inverse")

        st.divider()

        f1, f2 = st.columns([2, 1])
        f1.subheader(f"💰 NET À VERSER : {net_to_pay:,} $")
        
        if f2.button(f"🚀 VIRER LA PAIE", use_container_width=True, type="primary"):
            try:
                with st.spinner("Exécution du virement national..."):
                    # A. Mise à jour Solde
                    idx_c = df_b[df_b["Nom Roblox"] == target_paie].index[0]
                    df_b.at[idx_c, "Solde"] = solde_actuel + net_to_pay
                    
                    # B. Routage des Taxes (Averis -> Moune2010)
                    def route_money(patron, amount):
                        try:
                            ix = df_b[df_b["Nom Roblox"] == patron].index[0]
                            curr = float(str(df_b.at[ix, "Solde"]).replace('$','').replace(',',''))
                            df_b.at[ix, "Solde"] = curr + amount
                        except: pass

                    if c_rct_final > 0: route_money("une10000", c_rct_final)
                    if c_averis > 0: route_money("Moune2010", c_averis)
                    
                    # C. Bonus : Reset du Permis à 25 PTS
                    if target_paie in df_p["Nom Roblox"].values:
                        idx_p = df_p[df_p["Nom Roblox"] == target_paie].index[0]
                        df_p.at[idx_p, "PTS"] = 25
                    
                    # D. Marquage des heures comme PAYÉES
                    for idx_log in logs_paie.index:
                        df_admin_clock.at[idx_log, "statut"] = "Payé"

                    # E. Sauvegarde Cloud
                    cloud_conn.update(worksheet="Banque", data=df_b)
                    cloud_conn.update(worksheet="Points Permis", data=df_p)
                    cloud_conn.update(worksheet="Clock", data=df_admin_clock)
                    
                    st.balloons()
                    st.success(f"Transaction terminée ! {net_to_pay}$ versés.")
                    time.sleep(1.5); st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

# --- D. JOURNAUX D'AUDIT ---
st.divider()
st.markdown("### 📜 Journaux d'Audit (Session)")
if "audit_logs" in st.session_state and st.session_state.audit_logs:
    with st.container(height=150, border=True):
        for log in reversed(st.session_state.audit_logs):
            st.write(f"🔹 {log}")
else:
    st.info("Aucun log disponible pour cette session.")
# 8. PIED DE PAGE
# ======================================================================================
st.divider()
st.caption(f"Terminal Fédéral RCRP FR | Opérationnel | © 2026 République de Rensselaer")
