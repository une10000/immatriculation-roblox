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

    # 3. COLONNES D'ACCÈS (MISE À JOUR 4 COLONNES)
    c1, c2, c3, c4 = st.columns(4) # Passage à 4 colonnes
    
    with c1:
        st.markdown("### 👥 CIVIL")
        nom_civil = st.text_input("Note (Optionnel)", placeholder="Ex: Renault Coupé.", key="input_civil_align")
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
        st.markdown("### 🏢 AVERIS")
        login_averis = st.text_input("Accès Averis", placeholder="Code Averis", type="password", key="l_av_ff")
        if st.button("CONNEXION AVERIS", key="b_av_f", use_container_width=True):
            # Défini ta variable KEY_AVERIS en haut de ton code (ex: "26_RCRPFR_AVERIS")
            if login_averis == "26_RCRPFR_AVERIS": 
                st.session_state.user_auth = "Averis"
                st.rerun()
            else: st.error("Accès refusé.")

    with c4:
        st.markdown("### 🛡️ STAFF")
        login_staff = st.text_input("Clé Maîtresse", placeholder="Code POLSTA", type="password", key="l_st_ff")
        if st.button("ACCÈS ADMIN", key="b_st_f", use_container_width=True):
            if login_staff == KEY_STAFF:
                st.session_state.user_auth = "Staff"
                st.rerun()
            else: st.error("Accès refusé.")

    st.stop()
# ======================================================================================
# LE RESTE DU CODE (S'affiche uniquement après connexion)
# ======================================================================================
# ======================================================================================
        # 6.1 LE PANNEAU D'ACTION (STYLE TICKET CLASSIQUE RÉTABLI)
        # ======================================================================================
        if st.session_state.user_auth in ["Averis", "RCT"]:
            st.markdown("---")
            st.subheader(f"🛠️ GESTION DU DOSSIER : {target}")
            
            c_left, c_mid, c_right = st.columns([1.2, 1, 1])

            # 1. À GAUCHE : LE FORMULAIRE
            with c_left:
                st.markdown("#### 📝 FORMULAIRE")
                with st.form(key=f"form_action_{target}"):
                    type_action = st.radio("Action :", ["Facturation", "Immatriculation"], horizontal=True)
                    
                    if type_action == "Facturation":
                        mt = st.number_input("Montant ($)", min_value=0, value=500)
                        mo = st.text_input("Motif")
                    else:
                        plaque = st.text_input("Plaque (ex: ABC-123)")
                        marque = st.text_input("Marque du véhicule")

                    if st.form_submit_button("VALIDER L'ACTION"):
                        df_f_up = cloud_conn.read(worksheet="Factures").fillna("")
                        
                        if type_action == "Facturation":
                            # Ajout auto de la date limite (+24h)
                            limite = (datetime.now() + timedelta(hours=24)).strftime("%d/%m/%Y %H:%M:%S")
                            new_f = {
                                "ID": len(df_f_up) + 1, 
                                "Emetteur": st.session_state.user_auth, 
                                "Cible": target, 
                                "Montant": mt, 
                                "Motif": mo, 
                                "Statut": "EN ATTENTE",
                                "Date_Limite": limite
                            }
                            df_f_up = pd.concat([df_f_up, pd.DataFrame([new_f])], ignore_index=True)
                            cloud_conn.update(worksheet="Factures", data=df_f_up)
                            st.success("Facture émise !")
                        else:
                            # Immatriculation avec ajout auto de la date
                            df_v_up = cloud_conn.read(worksheet="Copie de Immatriculations").fillna("")
                            new_v = {
                                "Nom d'utilisateur ROBLOX": target, 
                                "Numéro de la plaque": plaque.upper(), 
                                "Marque du véhicule": marque, 
                                "Horodateur": datetime.now().strftime("%d/%m/%Y"), # Date auto
                                "Assurance": st.session_state.user_auth
                            }
                            df_v_up = pd.concat([df_v_up, pd.DataFrame([new_v])], ignore_index=True)
                            cloud_conn.update(worksheet="Copie de Immatriculations", data=df_v_up)
                            st.success("Véhicule immatriculé !")
                        
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()

            # 2. AU MILIEU : L'APERÇU TICKET (TON ANCIEN STYLE)
            with c_mid:
                st.markdown("#### 🎫 APERÇU TICKET")
                if type_action == "Facturation":
                    # Détermination du nom de l'agence
                    agency = "SERVICES AVERIS" if st.session_state.user_auth == "Averis" else "RÉSEAU RCT"
                    
                    st.markdown(f"""
                    <div style="border: 2px solid #000; padding: 15px; background: white; color: black; font-family: 'Courier New', monospace; box-shadow: 6px 6px 0px #000; margin-top: 10px;">
                        <center><b style="font-size:1.1em; text-decoration: underline;">SOUCHE OFFICIELLE</b><br>
                        <small>{agency}</small></center>
                        <hr style="border-top: 1px dashed #000; margin: 10px 0;">
                        <div style="font-size: 0.9em;">
                            <b>CITOYEN :</b> {target}<br>
                            <b>AGENT   :</b> {st.session_state.user_auth}<br>
                            <b>MOTIF   :</b> {mo if mo else "..."}
                        </div>
                        <hr style="border-top: 1px dashed #000; margin: 10px 0;">
                        <div style="text-align: center; font-weight: bold; font-size: 1.2em;">
                            TOTAL : {mt}$
                        </div>
                        <center><small style="font-size: 0.7em; opacity: 0.6; display:block; margin-top:10px;">GÉNÉRÉ LE {datetime.now().strftime("%d/%m/%Y")}</small></center>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Mode Immatriculation : Les données seront envoyées vers la base 'Immatriculations'.")

            # 3. À DROITE : LES VÉHICULES DU CITOYEN
            with c_right:
                st.markdown("#### 🚘 VÉHICULES")
                # On utilise df_i qui est déjà chargé en début de script
                v_target = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
                if not v_target.empty:
                    for _, v in v_target.iterrows():
                        st.markdown(f"""
                        <div style="background:#f0f2f6; padding:8px; border-radius:5px; margin-bottom:5px; border-left:4px solid #333; color:black;">
                            <b>{v['Numéro de la plaque']}</b><br><small>{v['Marque du véhicule']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("Aucun véhicule enregistré.")
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

# --- BOUTON DE PAIEMENT (AVEC REDIRECT AVERIS/RCT) ---
            if st.button(f"💳 RÉGLER LA FACTURE #{fac['ID']}", key=f"pay_{fac['ID']}", use_container_width=True):
                try:
                    # 1. Nettoyage et récupération du solde client
                    idx_b = df_b[df_b["Nom Roblox"] == target].index[0]
                    solde_actuel = float(str(df_b.at[idx_b, "Solde"]).replace('$', '').replace(',', '').strip())
                    montant_facture = float(fac['Montant'])
                    
                    if solde_actuel >= montant_facture:
                        # 2. Détermination du compte de destination
                        # Si l'émetteur est Averis -> Moune2010, sinon -> une10000 (RCT/Staff)
                        destinataire = "Moune2010" if fac['Emetteur'] == "Averis" else "une10000"
                        
                        # 3. Prélèvement client
                        df_b.at[idx_b, "Solde"] = solde_actuel - montant_facture
                        
                        # 4. Versement au destinataire
                        idx_dest = df_b[df_b["Nom Roblox"] == destinataire].index[0]
                        solde_dest_raw = float(str(df_b.at[idx_dest, "Solde"]).replace('$', '').replace(',', '').strip())
                        df_b.at[idx_dest, "Solde"] = solde_dest_raw + montant_facture
                        
                        # 5. Mise à jour du statut de la facture
                        df_all_f.loc[df_all_f["ID"] == fac["ID"], "Statut"] = "PAYÉ"
                        
                        # 6. Sauvegarde Cloud
                        cloud_conn.update(worksheet="Banque", data=df_b)
                        cloud_conn.update(worksheet="Factures", data=df_all_f)
                        
                        record_log(target, f"Paiement facture #{fac['ID']} vers {destinataire}")
                        st.success(f"✅ Paiement effectué ! L'argent a été versé à {destinataire}.")
                        
                        st.cache_data.clear()
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Solde insuffisant pour régler cette facture.")
                except Exception as e:
                    st.error(f"Erreur lors du transfert : {e}")
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
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import random

# --- CONFIGURATION DES ONGLETS ---
tab_labels = ["🚗 IMMATRICULATION"]
if st.session_state.user_auth in ["RCT", "Staff"]: 
    tab_labels.append("👮 SERVICES AGENT")
if st.session_state.user_auth == "Staff": 
    tab_labels.append("🛠️ ADMINISTRATION")

tabs = st.tabs(tab_labels)

# ======================================================================================
# --- ONGLET 1 : IMMATRICULATION & RADIATION ---
# ======================================================================================
with tabs[0]:
    col_f, col_t = st.columns([1.3, 1])
    
    with col_f:
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

            # --- CALCUL DU TOTAL ---
            taxe_gouv = 175
            taxe_assu = 130 if "AVERIS" in f_assu else (150 if "RCT" in f_assu else 0)
            
            # Offre Trio RCT
            if "RCT" in f_assu and f_owner != "---":
                nb_vehicules = len(df_i[df_i["Nom d'utilisateur ROBLOX"] == f_owner])
                if nb_vehicules >= 2:
                    taxe_assu = 0
                    st.success(f"🎁 OFFRE TRIO ACTIVÉE")

            total_bill = taxe_gouv + taxe_assu + val_taxe_jeune
            
            if st.button(f"S'ACQUITTER DE {total_bill}$ ET ENREGISTRER", use_container_width=True, type="primary"):
                # Insère ici ta logique cloud_conn.update...
                st.success("Immatriculation validée !")

    with col_t:
        st.markdown("### 🖼️ Aperçu du Titre")
        date_actuelle = (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M")
        
        ticket_html = f"""
        <div style='border: 2px dashed #555; padding: 20px; background-color: #f9f9f9; color: #333; font-family: "Courier New", monospace; border-radius:10px;'>
            <div style='text-align:center;'>
                <h2 style='margin:0; font-size:1.2em;'>TITRE DE CIRCULATION</h2>
                <small>RÉPUBLIQUE DE RENSSERLAER</small>
            </div>
            <div style='border-top: 1px dashed #ccc; border-bottom: 1px dashed #ccc; padding: 10px 0; margin: 10px 0; font-size: 0.9em;'>
                <p><strong>DATE :</strong> {date_actuelle}</p>
                <p><strong>UTILISATEUR :</strong> {f_owner}</p>
                <p><strong>PLAQUE :</strong> <span style='border:1px solid #333; padding:2px 6px; background:#eee;'>{f_plate if f_plate else "---"}</span></p>
                <p><strong>ASSURANCE :</strong> {f_assu}</p>
            </div>
            <div style='text-align:right;'>
                <strong style='font-size:1.1em;'>TOTAL PAYÉ : {total_bill}$</strong>
            </div>
        </div>
        """
        st.components.v1.html(ticket_html, height=400)

# ======================================================================================
# --- ONGLET 2 : SERVICES AGENT (RCT/STAFF) ---
# ======================================================================================
if st.session_state.user_auth in ["RCT", "Staff"]:
    with tabs[1]:
        # Le contenu de cet onglet reste lié au 'target' sélectionné en sidebar/haut de page
        if 'target' not in locals() or target == "---":
            st.warning("⚠️ Sélectionnez un citoyen pour accéder aux services de police/agent.")
        else:
            col_saisie, col_facture, col_vehicules = st.columns([1.1, 1, 0.9])
            # ... (Ta logique de saisie de contravention)

# ======================================================================================
# --- ONGLET 3 : ADMINISTRATION (STAFF ONLY) ---
# ======================================================================================
if st.session_state.user_auth == "Staff":
    with tabs[2]:
        st.markdown("### 👤 Création de Dossier Citoyen")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                new_name = st.text_input("Nom d'utilisateur ROBLOX", key="admin_new_name")
                new_discord = st.text_input("Utilisateur Discord", key="admin_new_discord")
            with c2:
                new_jobs = st.multiselect("Emploiement(s)", ["Sans-Emploi", "Agent RCT", "Averis", "Police", "Staff"], default=["Sans-Emploi"])
                new_pts = st.slider("Points Permis", 0, 25, 25)

            if st.button("🆕 GÉNÉRER LE DOSSIER (15k + Date Auto)", use_container_width=True, type="primary"):
                if new_name:
                    # Application automatique du solde de 15k et de la date du jour
                    today_str = datetime.now().strftime("%d/%m/%Y")
                    jobs_string = " / ".join(new_jobs) if new_jobs else "Sans-Emploi"
                    
                    # Mise à jour Banque
                    new_bank_row = pd.DataFrame([{"Nom Roblox": new_name, "Nom Discord": new_discord, "Solde": 15000, "Emploiement": jobs_string, "Date d'arrivée": today_str}])
                    df_b = pd.concat([df_b, new_bank_row], ignore_index=True)
                    cloud_conn.update(worksheet="Banque", data=df_b)
                    
                    st.success(f"✅ Dossier créé pour {new_name} avec 15,000$ !")
                    st.rerun()

        st.divider()
        st.markdown("### 🧧 Terminal de Paie & Prélèvements")
        # Logique Averis -> Moune2010 intégrée ici lors du calcul
# ======================================================================================
# 8. PIED DE PAGE
# ======================================================================================
st.divider()
st.caption(f"Terminal Fédéral RCRP FR | Opérationnel | © 2026 République de Rensselaer")
