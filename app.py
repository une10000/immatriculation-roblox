import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta, timezone
from streamlit_gsheets import GSheetsConnection

# 1. INTERFACE & DESIGN (DOIT ÊTRE LA PREMIÈRE COMMANDE STREAMLIT)
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
# CONFIGURATION ET FONCTIONS TECHNIQUES
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

# --- CONFIGURATION DES COMPTES DESTINATAIRES ---
ACC_RCT = "une10000"
ACC_AVERIS = "Moune2010"

def traiter_paiement_prime(target_name, metier, montant, df_b, cloud_conn):
    """Gère le prélèvement sur l'employeur et l'ajout sur l'employé"""
    source_compte = None
    if "Averis" in metier:
        source_compte = ACC_AVERIS
    elif "Agent RCT" in metier:
        source_compte = ACC_RCT
    
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
        return False, "⚠️ Aucun employeur configuré."

# Codes de Service
KEY_RCT = "RCT-26-RCRPFR"
KEY_AVERIS = "AVE-26-RCRPFR" # La clé pour ton login Averis
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
            iframe { 
                border: none !important; 
                box-shadow: none !important; 
                background: transparent !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # 1. CALCUL DU MOMENT (UTC+1)
    # Import local pour être sûr que c'est reconnu si les imports du haut ont sauté
    from datetime import datetime, timedelta, timezone
    import streamlit.components.v1 as components 

    t_now_lock = datetime.now(timezone.utc) + timedelta(hours=1)
    h_lock = t_now_lock.hour

    if 5 <= h_lock < 18:
        salut_complet = "Bonjour☀️"
        p_style = "background-color: #87CEEB; background-image: conic-gradient(from 200deg at 85% 10%, transparent 0deg, rgba(255,255,255,0.4) 15deg, transparent 30deg, rgba(255,223,137,0.5) 45deg, transparent 60deg, rgba(255,255,255,0.4) 75deg, transparent 90deg), radial-gradient(circle at 85% 10%, #FFF9E3 0%, #FFD700 15%, rgba(255,215,0,0.4) 30%, transparent 60%);"
        t_color = "#1E1E1E"
        glow = "0 0 30px rgba(255, 255, 255, 1), 0 0 60px rgba(255, 200, 0, 0.6)"
    else:
        salut_complet = "Bonsoir🌕"
        p_style = "background-color: #05070a; background-image: radial-gradient(1px 1px at 25% 35%, white, transparent), radial-gradient(1px 1px at 50% 10%, white, transparent); background-size: 150px 150px, 200px 200px;"
        t_color = "#FFFFFF"
        glow = "0 0 40px rgba(255,255,255,0.9), 0 0 80px rgba(255,255,255,0.4)"

    # --- LE BLOC MONOLITHIQUE ---
    components.html(f"""
        <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; width: 100%; border-radius: 25px; overflow: hidden; border: none;">
            <div style="text-align: center; padding: 70px 20px; color: {t_color}; {p_style} height: 350px; box-sizing: border-box;">
                <h1 style="font-size: 5.5em; margin: 0; font-weight: 900; letter-spacing: -3px; text-shadow: {glow}; line-height: 1.1;">{salut_complet}</h1>
                <p style="font-size: 1.1em; opacity: 0.8; letter-spacing: 5px; font-weight: bold; text-transform: uppercase; margin: 25px 0;">Unité Fédérale de Rensselaer</p>
                <div id="clock_lock" style="font-size: 3.8em; letter-spacing: 3px; font-weight: bold; border-top: 2px solid {t_color}33; display: inline-block; padding-top: 10px;">00:00:00</div>
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
                document.getElementById('clock_lock').textContent = h + ":" + m + ":" + s;
            }}
            setInterval(update, 1000); update();
        </script>
    """, height=650)

    st.write("")
    st.warning("⚠️ **AVERTISSEMENT :** Toute action effectuée sur ce terminal est enregistrée.")
    st.write("---")

    # --- COLONNES D'ACCÈS ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("### 👥 CIVIL")
        st.text_input("Commentaire", placeholder="Ex: Liberté...", key="input_civ")
        if st.button("ACCÉDER", key="btn_civ", use_container_width=True):
            st.session_state.user_auth = "Civil"
            st.rerun()
    with c2:
        st.markdown("### 👨‍🔧 AGENT RCT")
        l_rct = st.text_input("Identifiant", type="password", key="in_rct")
        if st.button("AUTH RCT", key="btn_rct", use_container_width=True):
            if l_rct == KEY_RCT:
                st.session_state.user_auth = "RCT"
                st.rerun()
            else: st.error("Invalide")
    with c3:
        st.markdown("### 🏢 AVERIS")
        l_ave = st.text_input("Code Entreprise", type="password", key="in_ave")
        if st.button("ACCÈS AVERIS", key="btn_ave", use_container_width=True):
            if l_ave == KEY_AVERIS:
                st.session_state.user_auth = "Averis"
                st.rerun()
            else: st.error("Invalide")
    with c4:
        st.markdown("### 🛡️ STAFF")
        l_st = st.text_input("Clé Maîtresse", type="password", key="in_st")
        if st.button("ACCÈS ADMIN", key="btn_st", use_container_width=True):
            if l_st == KEY_STAFF:
                st.session_state.user_auth = "Staff"
                st.rerun()
            else: st.error("Refusé")

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
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Aucun permis trouvé.")

        # --- COLONNE 2 : BANQUE ---
        with col2:
            b_data = df_b[df_b["Nom Roblox"] == target]
            if not b_data.empty:
                c_info, c_v, c_m = st.columns([3, 0.5, 2])
                
                with c_info:
                    # 1. Solde
                    st.metric("SOLDE BANCAIRE", f"{b_data.iloc[0]['Solde']}$")
                    
                    # 2. Métier
                    current_jobs_raw = str(b_data.iloc[0]['Emploiement'])
                    st.write(f"🏢 Métier : **{current_jobs_raw}**")
                    
                    # 3. Modification Staff
                    if st.session_state.user_auth == "Staff":
                        if st.button("✏️ Modifier le métier", key=f"edit_job_{target}", use_container_width=True):
                            st.session_state[f"show_editor_{target}"] = not st.session_state.get(f"show_editor_{target}", False)
                        
                        if st.session_state.get(f"show_editor_{target}", False):
                            with st.container(border=True):
                                liste_metiers = ["Sans-Emploi", "Agent RCT", "Averis", "Police", "Staff", "Service Public", "Entreprise Privée"]
                                current_jobs_list = [j.strip() for j in current_jobs_raw.split("/") if j.strip()]
                                valid_defaults = [j for j in current_jobs_list if j in liste_metiers]
                                
                                new_jobs = st.multiselect("Sélection :", options=liste_metiers, default=valid_defaults)
                                
                                cs1, cs2 = st.columns(2)
                                with cs1:
                                    if st.button("💾 Sauver", key=f"save_j_{target}", use_container_width=True, type="primary"):
                                        new_str = " / ".join(new_jobs) if new_jobs else "Sans-Emploi"
                                        idx_b = df_b[df_b["Nom Roblox"] == target].index[0]
                                        df_b.at[idx_b, "Emploiement"] = new_str
                                        cloud_conn.update(worksheet="Banque", data=df_b)
                                        st.session_state[f"show_editor_{target}"] = False
                                        st.cache_data.clear()
                                        st.rerun()
                                with cs2:
                                    if st.button("Annuler", key=f"cancel_j_{target}", use_container_width=True):
                                        st.session_state[f"show_editor_{target}"] = False
                                        st.rerun()

                    st.caption(f"📅 Arrivée : {b_data.iloc[0]['Date d\'arrivée']}")
                
                with c_m:
                    st.markdown("""
                        <div style="text-align: right; line-height: 1; padding-top: 5px;">
                            <div style="opacity: 0.15; font-size: 40px; margin-bottom: -10px;">🏛️</div>
                            <div style="opacity: 0.1; font-size: 50px; margin-bottom: -10px;">💳</div>
                            <div style="height: 4px; width: 60px; background: linear-gradient(90deg, transparent, #000); display: inline-block; opacity: 0.2; border-radius: 2px;"></div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Aucun compte trouvé.")

        # --- COLONNE 3 : ARCHIVES ---
        with col3:
            st.markdown("### 📁 ARCHIVES")
            try:
                df_f_history = cloud_conn.read(worksheet="Factures").fillna("")
                historique = df_f_history[(df_f_history["Cible"] == target) & (df_f_history["Statut"] == "PAYÉ")]

                if not historique.empty:
                    for _, f in historique.iterrows():
                        if st.session_state.user_auth in ["Staff", "Admin"]:
                            if st.button(f"🔄 Rembourser #{f['ID']}", key=f"refund_{f['ID']}", use_container_width=True):
                                st.info("Traitement...")
                                # Ta logique de remboursement ici
                        
                        st.markdown(f"""
                        <div style="border: 1px solid #000; padding: 10px; background: #f9f9f9; color: black; margin-bottom: 8px; border-left: 5px solid green;">
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
            except Exception as e:
                st.error(f"Erreur Archives : {e}")
# ======================================================================================
# 7. LOGIQUE DE RÉCUPÉRATION & PAIEMENT (FACTURES CITOYEN)
# ======================================================================================
df_all_f = cloud_conn.read(worksheet="Factures").fillna("")
mes_factures = df_all_f[(df_all_f["Cible"] == target) & (df_all_f["Statut"] == "EN ATTENTE")]

if not mes_factures.empty and target != "---":
    st.error(f"⚠️ {len(mes_factures)} FACTURE(S) EN ATTENTE POUR {target}")
    for _, fac in mes_factures.iterrows():
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
                timer_info = "⚠️ DÉLAI DÉPASSÉ (IMPAYÉ)"; t_color = "#d32f2f"
        except: timer_info = "⌛ Délai : 24 heures"; t_color = "#555"

        # --- DESIGN DU TICKET ---
        prefix_name = "POLICE NATIONALE" if fac['Emetteur'] == "Staff" else f"SERVICES {fac['Emetteur']}"
        st.markdown(f"""
        <div style="border: 2px solid #000; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; margin-bottom: 5px; box-shadow: 6px 6px 0px #000;">
            <center><b style="font-size:1.1em; text-decoration: underline;">FACTURE OFFICIELLE</b><br><small>{prefix_name}</small></center>
            <hr style="border-top: 1px dashed #000; margin: 10px 0;">
            <div style="font-size: 0.9em; line-height: 1.2;">
                <b>RÉFÉRENCE :</b> #{fac['ID']}<br>
                <b>AGENT     :</b> {fac['Emetteur']}<br>
                <b>MOTIF     :</b> {fac['Motif']}<br>
                <b style="color: {t_color};">{timer_info}</b>
            </div>
            <hr style="border-top: 1px dashed #000; margin: 10px 0;">
            <div style="text-align: center; color: #d32f2f; font-weight: bold; font-size: 1.3em;">MONTANT : {fac['Montant']}$</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"💳 RÉGLER LA FACTURE #{fac['ID']}", key=f"pay_{fac['ID']}", use_container_width=True):
            try:
                idx_b = df_b[df_b["Nom Roblox"] == target].index[0]
                solde_actuel = float(str(df_b.at[idx_b, "Solde"]).replace('$', '').replace(',', ''))
                montant_f = float(fac['Montant'])
                
                if solde_actuel >= montant_f:
                    df_b.at[idx_b, "Solde"] = solde_actuel - montant_f
                    # Redirection selon émetteur
                    if fac['Emetteur'] == "RCT":
                        idx_dest = df_b[df_b["Nom Roblox"] == "une10000"].index[0]
                        df_b.at[idx_dest, "Solde"] += montant_f
                    elif fac['Emetteur'] == "Averis":
                        idx_dest = df_b[df_b["Nom Roblox"] == "Moune2010"].index[0]
                        df_b.at[idx_dest, "Solde"] += montant_f
                    
                    df_all_f.loc[df_all_f["ID"] == fac["ID"], "Statut"] = "PAYÉ"
                    cloud_conn.update(worksheet="Banque", data=df_b)
                    cloud_conn.update(worksheet="Factures", data=df_all_f)
                    st.success("✅ Facture payée !")
                    st.cache_data.clear()
                    st.rerun()
                else: st.error("Solde insuffisant.")
            except Exception as e: st.error(f"Erreur : {e}")

# ======================================================================================
# 8. SYSTÈME DES ONGLETS
# ======================================================================================
tab_labels = ["🚗 IMMATRICULATION"]
if st.session_state.user_auth in ["RCT", "Staff", "Averis"]: tab_labels.append("👮 SERVICES AGENT")
if st.session_state.user_auth == "Staff": tab_labels.append("🛠️ ADMINISTRATION")

tabs = st.tabs(tab_labels)

# --- ONGLET 1 : IMMATRICULATION & TITRES ---
with tabs[0]:
    col_f, col_t = st.columns([1.3, 1])
    with col_f:
        st.markdown("### 📝 Gestion des Titres")
        with st.container(border=True):
            f_owner = st.selectbox("Propriétaire", ["---"] + df_b["Nom Roblox"].tolist(), key="k_own")
            f_model = st.text_input("Marque", key="k_mod")
            f_plate = st.text_input("Numéro de Plaque", key="k_pla").upper()
            f_assu = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"], key="k_ass")
            f_code = st.text_input("Code Secret Radiation", type="password", key="k_cod")
            
            taxe_gouv = 175
            taxe_assu = 130 if "AVERIS" in f_assu else (150 if "RCT" in f_assu else 0)
            total_bill = taxe_gouv + taxe_assu
            
            if st.button(f"S'ACQUITTER DE {total_bill}$ ET ENREGISTRER", use_container_width=True, type="primary"):
                if f_owner != "---" and f_model and f_plate and f_code:
                    idx_b = df_b[df_b["Nom Roblox"] == f_owner].index[0]
                    solde = float(str(df_b.at[idx_b, "Solde"]).replace('$',''))
                    if solde >= total_bill:
                        df_b.at[idx_b, "Solde"] = solde - total_bill
                        # Crédit RCT Trésorerie (une10000)
                        idx_rct = df_b[df_b["Nom Roblox"] == "une10000"].index[0]
                        df_b.at[idx_rct, "Solde"] += total_bill
                        
                        new_row = {"Nom d'utilisateur ROBLOX": f_owner, "Marque du véhicule": f_model, "Numéro de la plaque": f_plate, "Assurance": f_assu, "Code": f_code, "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M")}
                        df_i = pd.concat([df_i, pd.DataFrame([new_row])], ignore_index=True)
                        cloud_conn.update(worksheet="Banque", data=df_b)
                        cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i)
                        st.success("✅ Véhicule enregistré !")
                        st.cache_data.clear()
                        st.rerun()
                    else: st.error("Solde insuffisant.")
                else: st.error("Champs manquants.")

    with col_t:
        st.markdown("### 🖼️ Aperçu")
        if f_owner != "---":
            st.markdown(f"""
            <div style="border: 2px solid black; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace;">
                <center><b>TITRE DE CIRCULATION</b><br><small>RÉPUBLIQUE DE RENSSERLAER</small></center>
                <hr>
                <b>NOM :</b> {f_owner}<br>
                <b>MODÈLE :</b> {f_model}<br>
                <b>PLAQUE :</b> <span style="border: 1px solid black; padding: 0 3px;">{f_plate}</span><br>
                <b>ASSURANCE :</b> {f_assu}
            </div>
            """, unsafe_allow_html=True)

# --- ONGLET 2 : SERVICES AGENT (AVERIS / RCT / STAFF) ---
if "👮 SERVICES AGENT" in tab_labels:
    with tabs[1]:
        col_s, col_v = st.columns([1.5, 1])
        with col_s:
            st.markdown("#### 📝 Émission de Facture")
            with st.container(border=True):
                f_val = st.number_input("Montant ($)", min_value=0, step=50)
                f_mot = st.text_input("Motif")
                if st.button("🚨 ENVOYER LA FACTURE", use_container_width=True, type="primary"):
                    new_f = {"ID": random.randint(1000, 9999), "Cible": target, "Emetteur": st.session_state.user_auth, "Montant": f_val, "Motif": f_mot, "Statut": "EN ATTENTE", "Date_Limite": (datetime.now() + timedelta(hours=24)).strftime("%d/%m/%Y %H:%M:%S")}
                    df_all_f = pd.concat([df_all_f, pd.DataFrame([new_f])], ignore_index=True)
                    cloud_conn.update(worksheet="Factures", data=df_all_f)
                    st.success("Facture envoyée !")
                    st.rerun()
        with col_v:
            st.markdown("#### 🚗 Véhicules du Citoyen")
            v_citoyen = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
            for _, v in v_citoyen.iterrows():
                st.caption(f"🚘 {v['Marque du véhicule']} [{v['Numéro de la plaque']}]")

# --- ONGLET 3 : ADMINISTRATION ---
if "🛠️ ADMINISTRATION" in tab_labels:
    with tabs[-1]:
        # SECTION CRÉATION
        st.markdown("### 👤 Création de Dossier")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                n_name = st.text_input("Pseudo Roblox", key="adm_n")
                n_disc = st.text_input("Discord", key="adm_d")
            with c2:
                n_jobs = st.multiselect("Emplois", ["Sans-Emploi", "Agent RCT", "Averis", "Staff"], default=["Sans-Emploi"])
            
            if st.button("🆕 GÉNÉRER LE PROFIL (15k + DATE AUTO)", use_container_width=True):
                today = datetime.now().strftime("%d/%m/%Y")
                new_b = pd.DataFrame([{"Nom Roblox": n_name, "Nom Discord": n_disc, "Solde": 15000, "Emploiement": " / ".join(n_jobs), "Date d'arrivée": today}])
                df_b = pd.concat([df_b, new_b], ignore_index=True)
                cloud_conn.update(worksheet="Banque", data=df_b)
                st.success(f"Profil {n_name} créé avec 15,000$ !")
                st.rerun()
        
        st.divider()
        # SECTION RESET
        st.markdown("### ♻️ Recyclage & Paie")
        if st.button("🧧 VERSER LES PAIES ET VIDER TOUTES LES PLAQUES", use_container_width=True, type="primary"):
            # Logique de paie simplifiée ici (Verser 15k + primes à tout le monde si besoin)
            # Puis Reset Immat :
            df_i_empty = pd.DataFrame(columns=df_i.columns)
            cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i_empty)
            st.warning("⚠️ SYSTÈME RECYCLÉ : Toutes les plaques ont été supprimées.")
            st.cache_data.clear()
            st.rerun()
# ======================================================================================
# 9. PIED DE PAGE
# ======================================================================================
st.divider()
st.caption(f"Terminal Fédéral RCRP FR | Opérationnel | © 2026 République de Rensselaer")
