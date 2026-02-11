import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
# AJOUT DE L'IMPORT MANQUANT ICI :
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
# 7. LOGIQUE DES ONGLETS (CORRIGÉE)
# ======================================================================================
# ======================================================================================
# NOUVEAU : SYSTÈME DE PAIEMENT DES FACTURES (STYLE TICKET)
# ======================================================================================
# --- RÉCUPÉRATION DES DONNÉES (À ajouter avant le if) ---
df_all_f = cloud_conn.read(worksheet="Factures").fillna("")
# On filtre pour ne voir que les factures du citoyen sélectionné (target)
mes_factures = df_all_f[(df_all_f["Cible"] == target) & (df_all_f["Statut"] == "EN ATTENTE")]

# --- NOUVEAU : SYSTÈME DE PAIEMENT DES FACTURES (STYLE TICKET) ---
# --- SYSTÈME DE PAIEMENT DES FACTURES (STYLE TICKET) ---
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
            timer_info = "⌛ Délai : 24 heures"
            t_color = "#555"

# 2. AFFICHAGE DU TICKET HTML
        prefix_name = "POLICE NATIONALE" if fac['Emetteur'] == "Staff" else "RÉSEAU RCT"
        if fac['Emetteur'] == "Averis": prefix_name = "SERVICES AVERIS"

        st.markdown(f"""
        <div style="border: 2px solid #000; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; margin-bottom: 5px; box-shadow: 6px 6px 0px #000;">
            <center><b style="font-size:1.1em; text-decoration: underline;">FACTURE OFFICIELLE</b><br>
            <small>{prefix_name}</small></center>
            <hr style="border-top: 1px dashed #000; margin: 10px 0;">
            <div style="font-size: 0.9em; line-height: 1.2;">
                <b>RÉFÉRENCE :</b> #{fac['ID']}<br>
                <b>ÉMETTEUR   :</b> {fac['Emetteur']}<br>
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

        # 3. BOUTON DE PAIEMENT (BIEN INDENTÉ)
        # On ajoute 8 espaces (ou 2 tabulations) devant pour qu'il soit DANS la boucle
        if st.button(f"💳 RÉGLER LA FACTURE #{fac['ID']}", key=f"pay_{fac['ID']}", use_container_width=True):
            try:
                # 1. Récupération des données du payeur (le civil)
                idx_b = df_b[df_b["Nom Roblox"] == target].index[0]
                solde_raw = str(df_b.at[idx_b, "Solde"]).replace('$', '').replace(',', '')
                solde_actuel = float(solde_raw)
                montant_facture = float(fac['Montant'])
                
                if solde_actuel >= montant_facture:
                    # DÉBIT du civil
                    df_b.at[idx_b, "Solde"] = solde_actuel - montant_facture
                    
                    # 2. LOGIQUE DE REDIRECTION (CASH-FLOW)
                    emetteur = str(fac['Emetteur'])
                    
                    if emetteur == "RCT":
                        # Argent vers une10000
                        rct_idx = df_b[df_b["Nom Roblox"] == "une10000"].index[0]
                        solde_rct = float(str(df_b.at[rct_idx, "Solde"]).replace('$', '').replace(',', ''))
                        df_b.at[rct_idx, "Solde"] = solde_rct + montant_facture
                        
                    elif emetteur == "Averis":
                        # Argent vers Moune2010
                        ave_idx = df_b[df_b["Nom Roblox"] == "Moune2010"].index[0]
                        solde_ave = float(str(df_b.at[ave_idx, "Solde"]).replace('$', '').replace(',', ''))
                        df_b.at[ave_idx, "Solde"] = solde_ave + montant_facture
                    
                    # 3. Mise à jour du statut et Sauvegarde
                    df_all_f.loc[df_all_f["ID"] == fac["ID"], "Statut"] = "PAYÉ"
                    
                    cloud_conn.update(worksheet="Banque", data=df_b)
                    cloud_conn.update(worksheet="Factures", data=df_all_f)
                    
                    st.success(f"✅ Payé à {emetteur} !")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Solde insuffisant.")
            except Exception as e:
                st.error(f"Erreur : {e}")

        # BOUTON ANNULER (Seulement pour Staff/Admin)
        if st.session_state.user_auth in ["Staff", "Admin"]:
            if st.button(f"🗑️ ANNULER LA FACTURE #{fac['ID']}", key=f"admin_del_{fac['ID']}", use_container_width=True):
                try:
                    df_f_sync = cloud_conn.read(worksheet="Factures")
                    row_up = df_f_sync[df_f_sync["ID"] == fac["ID"]].index[0] + 2
                    cloud_conn.update(worksheet="Factures", range=f"E{row_up}", data=[["ANNULÉ"]])
                    st.warning("Facture annulée.")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur d'annulation : {e}")
        
        st.write("---") # Séparateur entre les tickets s'il y en a plusieurs
# --- SECTION VÉHICULES CORRIGÉE ---
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
                                
                                # 3. Création de la ligne (CORRIGÉE POUR CORRESPONDRE AU SHEETS)
nouvelle_immat = {
    "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    "Nom d'utilisateur ROBLOX": f_owner,
    "Marque du véhicule": f_model,    # Corrigé
    "Numéro de la plaque": f_plate,  # Corrigé
    "Assurance": f_assu.split(" (")[0],
    "CODE": f_code,                  # Mis en majuscules comme sur ton image
    "Points": 25
}

# Ajout au tableau local
new_df_i = pd.concat([df_i, pd.DataFrame([nouvelle_immat])], ignore_index=True)
                                }
                                
                                # Ajout au tableau local
                                new_df_i = pd.concat([df_i, pd.DataFrame([nouvelle_immat])], ignore_index=True)
                                
                                # 4. Envoi au Google Sheets (INDISPENSABLE)
                                cloud_conn.update(worksheet="Banque", data=df_b)
                                cloud_conn.update(worksheet="Copie de Immatriculations", data=new_df_i)
                                
                                # 5. Effet de fête et Confirmation
                                st.balloons() # Les ballons ! 🎈
                                
                                # Message de confirmation stylé
                                st.success(f"""
                                ### ✅ IMMATRICULATION RÉUSSIE !
                                ---
                                * **Propriétaire :** {f_owner}
                                * **Véhicule :** {f_model}
                                * **Plaque :** {f_plate}
                                * **Montant débité :** {total_bill}$
                                
                                *Le titre de circulation a été enregistré dans la base nationale.*
                                """)
                                
                                # Petite pause pour laisser voir les ballons avant le refresh
                                import time
                                time.sleep(3)
                                
                                # Rafraîchissement pour vider le formulaire
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
# --- ONGLET 2 : SERVICES AGENT (FACTURES / POINTS / CONSULTATION) ---
if st.session_state.user_auth in ["RCT", "Staff"]:
    with tabs[1]:
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
        
        st.divider()

        # 2. SYSTÈME DE SAISIE ET CONSULTATION
        if target == "---":
            st.warning("⚠️ Sélectionnez un citoyen en haut de la page.")
        else:
            # ALIGNEMENT : Saisie (Gauche) | Facture (Milieu) | Titres (Droite)
            col_saisie, col_facture, col_vehicules = st.columns([1.1, 1, 0.9])

            with col_saisie:
                with st.container(border=True):
                    st.markdown("#### 📝 Saisie")
                    
                    # 1. Choix de l'émetteur
                    if st.session_state.user_auth == "Staff":
                        f_emetteur = st.selectbox("Émetteur", ["POLSTA", "Averis"], key="v_emetteur_final")
                    else:
                        f_emetteur = "RCT"
                        st.info("Émetteur : RCT")

                    # --- CONFIGURATION DES CHAMPS ---
                    
                    # Montant : Toujours modifiable pour tout le monde
                    f_val = st.number_input("Montant ($)", min_value=0, step=50, key="v_val_final")
                    
                    # Points : Uniquement pour POLSTA (Staff). Bloqué pour Averis et RCT.
                    can_pull_points = (st.session_state.user_auth == "Staff" and f_emetteur == "POLSTA")
                    f_pts = st.number_input("Points à retirer", 0, 12, 0, key="v_pts_final", disabled=not can_pull_points)
                    
                    # Motif : Toujours modifiable pour tout le monde
                    f_motif = st.text_input("Motif", key="v_mot_final")
                    
                    # Véhicule : Toujours modifiable
                    target_veh = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
                    v_list = ["AUCUN / PIÉTON"] + target_veh["Numéro de la plaque"].tolist()
                    f_plate = st.selectbox("Véhicule concerné", v_list, key="v_plate_final")
                    
                    st.write("")
                    label = "🚨 ENVOYER FACTURE"
                    
                    if st.button(label, use_container_width=True, type="primary"):
                        if not f_motif:
                            st.error("Motif obligatoire.")
                        else:
                            # 1. Logique Points (Seulement si POLSTA)
                            if f_pts > 0 and can_pull_points:
                                try:
                                    idx_p = df_p[df_p["Nom Roblox"] == target].index[0]
                                    df_p.at[idx_p, "PTS"] = max(0, int(df_p.at[idx_p, "PTS"]) - f_pts)
                                    cloud_conn.update(worksheet="Points Permis", data=df_p)
                                except: pass

                            # 2. Enregistrement de la facture
                            import random
                            new_row = {
                                "ID": random.randint(1000, 9999), 
                                "Cible": target,
                                "Emetteur": f_emetteur,
                                "Montant": f_val,
                                "Motif": f"{f_motif} [{f_plate}]", 
                                "Statut": "EN ATTENTE",
                                "Date_Limite": (datetime.now() + timedelta(hours=24)).strftime("%d/%m/%Y %H:%M:%S")
                            }
                            
                            df_f_updated = pd.concat([df_all_f, pd.DataFrame([new_row])], ignore_index=True)
                            cloud_conn.update(worksheet="Factures", data=df_f_updated)
                            
                            st.success(f"✅ Facture {f_emetteur} envoyée !")
                            st.cache_data.clear()
                            st.rerun()

            with col_facture:
                st.markdown("#### 📄 Aperçu")
                # Design dynamique selon l'émetteur
                header_ticket = "FACTURE AVERIS" if f_emetteur == "Averis" else "FACTURE OFFICIELLE"
                st.markdown(f"""
                <div style="border: 2px solid black; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; line-height: 1.2;">
                    <center><b>{header_ticket}</b><br><small>RÉPUBLIQUE DE RENSSERLAER</small></center>
                    <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                    <b>ÉMETTEUR :</b> {f_emetteur.upper()}<br>
                    <b>DATE    :</b> {datetime.now().strftime('%d/%m/%Y')}<br>
                    <b>NOM     :</b> {target}<br>
                    <b>MOTIF   :</b> {f_motif.upper() if f_motif else '...'}<br>
                    <b>PLAQUE  :</b> <span style="border: 1px solid black; padding: 0 3px;">{f_plate}</span><br>
                    <b>MONTANT :</b> {f_val}$
                    <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                    <div style="text-align: center; color: black; font-weight: bold; font-size: 0.8em;">
                        POINTS : -{f_pts if can_pull_points else 0}<br>
                        <small>Document généré par terminal</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_vehicules:
                st.markdown("#### 🚗 Véhicules")
                if not target_veh.empty:
                    for _, veh in target_veh.iterrows():
                        assu_v = str(veh['Assurance']).upper()
                        
                        # 1. LOGIQUE DES COULEURS (Miroir)
                        if st.session_state.user_auth == "RCT":
                            if "RCT" in assu_v:
                                col_v, txt_v = "green", "✅ ASSURÉ RCT"
                            elif "AVERIS" in assu_v:
                                col_v, txt_v = "#E67E22", "⚠️ ASSURÉ AVERIS"
                            else:
                                col_v, txt_v = "#d32f2f", "🚨 DANGER : NON-ASSURÉ"
                        else:
                            col_v, txt_v = "green", "✅ VÉHICULE EN RÈGLE"

                        # 2. AFFICHAGE (Sorti du 'else' pour être visible par tout le monde)
                        st.markdown(f"""
                        <div style="border: 2px solid black; padding: 10px; background: white; color: black; font-family: 'Courier New', monospace; margin-bottom: 10px; font-size: 0.8em;">
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
                job_list = ["Sans-Emploi", "Agent RCT", "Averis", "Police", "Staff", "Entreprise Privée", "Service Public"]
                new_jobs = st.multiselect("Emploiement(s)", job_list, default=["Sans-Emploi"], key="admin_new_jobs")
                new_pts = st.slider("Points Permis (Départ)", 0, 25, 25, key="admin_new_pts")

            if st.button("🆕 GÉNÉRER LE DOSSIER (15k + Date Auto)", use_container_width=True, type="primary"):
                if new_name and new_name not in df_b["Nom Roblox"].values:
                    with st.spinner("Initialisation..."):
                        today_str = datetime.now().strftime("%d/%m/%Y")
                        jobs_string = " / ".join(new_jobs) if new_jobs else "Sans-Emploi"
                        
                        # Banque (Solde 15k auto)
                        new_bank_row = pd.DataFrame([{"Nom Roblox": new_name, "Nom Discord": new_discord, "Solde": 15000, "Emploiement": jobs_string, "Date d'arrivée": today_str}])
                        df_b = pd.concat([df_b, new_bank_row], ignore_index=True)
                        cloud_conn.update(worksheet="Banque", data=df_b)

                        # Permis
                        new_pts_row = pd.DataFrame([{"Nom Roblox": new_name, "PTS": new_pts, "Validité": "OUI" if new_pts > 0 else "NON"}])
                        df_p = pd.concat([df_p, new_pts_row], ignore_index=True)
                        cloud_conn.update(worksheet="Points Permis", data=df_p)

                        record_log(st.session_state.user_auth, f"Profil créé : {new_name}")
                        st.success(f"✅ Dossier créé pour {new_name}")
                        st.cache_data.clear()
                        import time
                        time.sleep(1)
                        st.rerun()
# --- SECTION 2 : SYSTÈME DE PAIE & ASSURANCES AUTOMATIQUES ---

if st.session_state.get("user_auth") == "Staff":
    st.divider()
    st.markdown("### 🧧 Terminal de Paie Nationale")
    
    with st.container(border=True):
        options_paie = sorted(df_b["Nom Roblox"].unique().tolist()) if not df_b.empty else []
        target_paie = st.selectbox("Sélectionner le bénéficiaire :", options_paie, key="paie_auto_target")
        
        if target_paie:
            # 1. Analyse du dossier
            user_data = df_b[df_b["Nom Roblox"] == target_paie]
            user_jobs_raw = user_data["Emploiement"].values[0]
            user_jobs_list = [j.strip() for j in str(user_jobs_raw).split("/")]
            solde_actuel = float(str(user_data["Solde"].values[0]).replace('$', '').replace(',', ''))
            
            # 2. Salaire et Primes
            primes_detail_list = []
            calcul_primes = 0
            if 'PRIME_JOB' in locals():
                for job in user_jobs_list:
                    m_prime = PRIME_JOB.get(job, 0)
                    if m_prime > 0:
                        primes_detail_list.append(f"• **{job}** : +{m_prime}$")
                        calcul_primes += m_prime
            total_brut = 15000 + calcul_primes
            
            # 3. Calcul précis des Assurances (SCAN PAR VÉHICULE + OFFRE TRIO)
            mes_vehicules = df_i[df_i["Nom d'utilisateur ROBLOX"] == target_paie]
            nb_vehicules = len(mes_vehicules)
            
            count_rct = 0
            argent_pour_averis = 0
            argent_standard = 0
            
            for index, vhc in mes_vehicules.iterrows():
                choix = str(vhc["Assurance"]).upper()
                if "RCT" in choix:
                    count_rct += 1
                elif "AVERIS" in choix:
                    argent_pour_averis += 130
                else:
                    argent_standard += 150
            
            # Application de l'Offre Trio RCT (Max 2 payants)
            if count_rct >= 3:
                argent_pour_rct = 300
                label_rct_display = "Part RCT (Offre Trio 🎁)"
            else:
                argent_pour_rct = count_rct * 150
                label_rct_display = "Part RCT"

            total_assurance = argent_pour_rct + argent_pour_averis + argent_standard
            
            # 4. Taxes Jeune Conducteur
            try:
                date_arrivee_str = str(user_data["Date d'arrivée"].values[0])
                date_arrivee = pd.to_datetime(date_arrivee_str, dayfirst=True)
                anciennete_jours = (datetime.now() - date_arrivee).days
            except:
                anciennete_jours = 0
            
            est_jeune_conducteur = anciennete_jours < 30
            taxe_jc_total = (nb_vehicules * 50) if est_jeune_conducteur else 0
            
            total_prelevement = total_assurance + taxe_jc_total
            total_net = total_brut - total_prelevement
            solde_final = solde_actuel + total_net
            
            # --- AFFICHAGE ---
            st.markdown(f"#### 📊 Fiche de Paie : {target_paie}")
            col_rev1, col_rev2 = st.columns(2)
            
            with col_rev1:
                with st.container(border=True):
                    st.write("**💰 REVENUS**")
                    st.write(f"• Salaire de Base : 15,000$")
                    if primes_detail_list:
                        for p in primes_detail_list: st.write(p)
                    else: st.write("• Aucune prime métier")
            
            with col_rev2:
                with st.container(border=True):
                    st.write("**📉 PRÉLÈVEMENTS**")
                    if argent_pour_rct > 0: st.write(f"• {label_rct_display} : -{argent_pour_rct}$")
                    if argent_pour_averis > 0: st.write(f"• Part Averis : -{argent_pour_averis}$")
                    if argent_standard > 0: st.write(f"• Part Standard : -{argent_standard}$")
                    
                    if est_jeune_conducteur:
                        st.write(f"• Taxes JC ({anciennete_jours}j) : -{taxe_jc_total}$")
                    else:
                        st.write(f"• Taxes JC : **EXONÉRÉ** ✅")

            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Solde Actuel", f"{solde_actuel}$")
            
            points_actuels = mes_vehicules["Points"].values[0] if not mes_vehicules.empty and "Points" in df_i.columns else 25
            diff_points = 25 - points_actuels
            c2.metric("Points Permis", "25/25", delta=f"+{diff_points}" if diff_points > 0 else None)
            
            c3.metric("Net à Verser", f"+{total_net}$", delta=f"-{total_prelevement}$ Taxes", delta_color="inverse")
            c4.metric("Solde Final", f"{solde_final}$", delta=f"+{total_net}$")

# --- BOUTON DE VALIDATION (PARFAITEMENT ALIGNÉ) ---
if st.button(f"🧧 CONFIRMER LE VERSEMENT ET LES TRANSFERTS", use_container_width=True, type="primary"):
    try:
        with st.spinner("Mise à jour des comptes..."):
            # A. Transferts Patrons
            if "Agent RCT" in user_jobs_list:
                idx_rct = df_b[df_b["Nom Roblox"] == "une10000"].index[0]
                df_b.at[idx_rct, "Solde"] = float(df_b.at[idx_rct, "Solde"]) - 2000 + argent_pour_rct
            elif argent_pour_rct > 0:
                idx_rct = df_b[df_b["Nom Roblox"] == "une10000"].index[0]
                df_b.at[idx_rct, "Solde"] = float(df_b.at[idx_rct, "Solde"]) + argent_pour_rct

            if "Averis" in user_jobs_list:
                idx_av = df_b[df_b["Nom Roblox"] == "Moune2010"].index[0]
                df_b.at[idx_av, "Solde"] = float(df_b.at[idx_av, "Solde"]) - 2000 + argent_pour_averis
            elif argent_pour_averis > 0:
                idx_av = df_b[df_b["Nom Roblox"] == "Moune2010"].index[0]
                df_b.at[idx_av, "Solde"] = float(df_b.at[idx_av, "Solde"]) + argent_pour_averis

            # B. Crédit Citoyen
            idx_ben = df_b[df_b["Nom Roblox"] == target_paie].index[0]
            df_b.at[idx_ben, "Solde"] = solde_final 
            
            # C. Reset Immatriculations (MAINTIENT LE TYPE D'ASSURANCE)
            mask_user = df_i["Nom d'utilisateur ROBLOX"] == target_paie

            def format_assurance(x):
                # On nettoie pour éviter "✅ ✅ RCT"
                propre = str(x).replace("✅", "").strip().upper()
                if "RCT" in propre:
                    return "✅ RCT"
                elif "AVERIS" in propre:
                    return "✅ AVERIS"
                else:
                    return "✅ Standard"

            df_i.loc[mask_user, "Assurance"] = df_i.loc[mask_user, "Assurance"].apply(format_assurance)

            if "Points" in df_i.columns:
                df_i.loc[mask_user, "Points"] = 25
            
            # Enregistrement Cloud
            cloud_conn.update(worksheet="Banque", data=df_b)
            cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i)
            
            record_log("Staff", f"PAIE : {target_paie} | Net: {total_net}$")
            st.success(f"✅ Terminé ! Statuts mis à jour et points réinitialisés.")
            st.cache_data.clear()
            st.rerun()
    except Exception as e:
        st.error(f"⚠️ Erreur lors de la validation : {e}")
# <-- Plus rien ici, le terminal est fini et protégé.
        # --- SECTION 3 : LOGS ET STATISTIQUES ---
        st.divider()
        col_admin_left, col_admin_right = st.columns(2)
        
        with col_admin_left:
            st.markdown("### 📜 Journaux d'Audit")
            with st.container(border=True):
                if "audit_logs" in st.session_state and st.session_state.audit_logs:
                    log_text = "\n".join(list(reversed(st.session_state.audit_logs)))
                    st.code(log_text, language="bash")
                    if st.button("🗑️ EFFACER LES LOGS", use_container_width=True):
                        st.session_state.audit_logs = []
                        st.rerun()
                else:
                    st.info("Aucune activité enregistrée.")

        with col_admin_right:
            st.markdown("### 📊 État du Système")
            with st.container(border=True):
                st.success(f"👥 Citoyens enregistrés : {len(df_b)}")
                st.info(f"🚗 Véhicules en base : {len(df_i)}")
                st.warning(f"🪪 Permis actifs : {len(df_p)}")
                st.divider()
                if st.button("♻️ FORCER LA SYNCHRO", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()

# --- FIN DE L'ONGLET ADMINISTRATION ---
# ======================================================================================
# 8. PIED DE PAGE
# ======================================================================================
st.divider()
st.caption(f"Terminal Fédéral RCRP FR | Opérationnel | © 2026 République de Rensselaer")
