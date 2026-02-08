# ==================================================================================================
# FICHIER : RCRP_GOV_OS_MAIN.PY
# PROJET  : RENSSELAER COUNTY ROLE-PLAY (RCRP) - TITAN INFRASTRUCTURE
# VERSION : 2000.0.1 (ENTERPRISE EDITION)
# AUTEUR  : ADMINISTRATION RCRP
# DATE    : 09 FÉVRIER 2026
# ==================================================================================================

"""
[MANUEL DE L'ADMINISTRATEUR SYSTÈME - NIVEAU 5]

CE SYSTÈME GÈRE L'INTÉGRALITÉ DES FLUX DU COMTÉ DE RENSSELAER.
IL EST STRICTEMENT INTERDIT DE MODIFIER LES FLUX FINANCIERS SANS ACCRÉDITATION.

PROTOCOLES FINANCIERS ACTIFS (HARDCODED) :
------------------------------------------
1. [PROTOCOLE RCT]    : Les frais d'assurance RCT (150$) sont virés sur le compte 'une10000'.
2. [PROTOCOLE AVERIS] : Les frais d'assurance AVERIS (130$) sont virés sur le compte 'Moune2010'.
3. [PROTOCOLE ÉTAT]   : La taxe d'immatriculation (175$) est détruite (Money Sink).
4. [PROTOCOLE GREFFE] : Date d'arrivée générée par horodatage serveur (UTC+1).

ARCHITECTURE TECHNIQUE :
------------------------
- CLASS Config         : Gestion des constantes et paramètres globaux.
- CLASS Security       : Gestion des accès et cryptographie simulée.
- CLASS Database       : Interface CRUD pour Google Sheets.
- CLASS BankEngine     : Moteur de transaction financière et redirection.
- CLASS DMVRegistry    : Gestion du parc automobile et catalogue.
- CLASS AuditSystem    : Journalisation des actions (Civil-Safe).
- CLASS Interface      : Gestionnaire de rendu graphique Streamlit.

[ATTENTION] : NE PAS EFFACER LES LIGNES DE CSS.
"""

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random

# ==================================================================================================
# [MODULE 1] : CONFIGURATION & CONSTANTES GLOBALES
# ==================================================================================================

class SystemConfig:
    """Configuration centrale du système RCRP."""
    
    # Identifiants Système
    APP_NAME = "RCRP Central Operating System"
    APP_VERSION = "v2000.0.1"
    APP_ICON = "⚖️"
    
    # Paramètres Financiers (NE PAS TOUCHER)
    PRICE_IMMAT_TAX = 175.00    # Taxe Gouvernementale (Détruite)
    PRICE_INS_AVERIS = 130.00   # Assurance Civile
    PRICE_INS_RCT = 150.00      # Assurance Transport
    
    STARTING_BALANCE = 15000.00 # Dotation initiale
    STARTING_PTS = 25           # Points permis initiaux
    
    # Comptes de Redirection (CIBLES)
    ACC_TARGET_RCT = "une10000"   # Reçoit l'argent RCT
    ACC_TARGET_AVERIS = "Moune2010" # Reçoit l'argent Averis
    
    # Sécurité
    KEY_STAFF = "RCRPFR-25-26"
    KEY_RCT = "RCT-26-RCRPFR"
    
    # Assets
    LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?width=1000"

    # Catalogue Automobile Complet (Liste statique pour performance)
    VEHICLE_DB = [
        "Acura", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", 
        "BMW", "Bugatti", "Buick", "Cadillac", "Chevrolet", 
        "Chrysler", "Dodge", "Ferrari", "Fiat", "Ford", 
        "GMC", "Honda", "Hyundai", "Infiniti", "Jaguar", 
        "Jeep", "Kia", "Koenigsegg", "Lamborghini", "Land Rover", 
        "Lexus", "Lincoln", "Lotus", "Maserati", "Mazda", 
        "McLaren", "Mercedes-Benz", "MINI", "Mitsubishi", "Nissan", 
        "Pagani", "Peugeot", "Porsche", "Ram", "Renault", 
        "Rolls-Royce", "Subaru", "Suzuki", "Tesla", "Toyota", 
        "Volkswagen", "Volvo"
    ]

# ==================================================================================================
# [MODULE 2] : STYLE & INTERFACE GRAPHIQUE (CSS AVANCÉ)
# ==================================================================================================

def inject_custom_css():
    """Injection du code CSS pour l'interface tactique sombre."""
    st.markdown("""
        <style>
        /* RESET & BASE */
        .stApp {
            background-color: #0b0e14;
            color: #c9d1d9;
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* HEADER STYLING */
        h1 {
            color: #58a6ff !important;
            font-weight: 800 !important;
            border-bottom: 2px solid #30363d;
            padding-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }
        h2, h3 {
            color: #8b949e !important;
            font-weight: 600 !important;
        }
        
        /* BUTTON STYLING (TACTICAL) */
        .stButton>button {
            background: linear-gradient(180deg, #21262d 0%, #161b22 100%) !important;
            color: #58a6ff !important;
            border: 1px solid #30363d !important;
            border-radius: 6px;
            padding: 0.75rem 1.5rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.2s ease-in-out;
            width: 100%;
        }
        .stButton>button:hover {
            border-color: #58a6ff !important;
            box-shadow: 0 0 15px rgba(88, 166, 255, 0.2);
            transform: translateY(-2px);
            background: #1f242c !important;
        }
        .stButton>button:active {
            transform: translateY(1px);
        }
        
        /* INPUT FIELDS */
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
            background-color: #0d1117 !important;
            color: #e6edf3 !important;
            border: 1px solid #30363d !important;
            border-radius: 4px;
        }
        .stTextInput>div>div>input:focus {
            border-color: #58a6ff !important;
            box-shadow: 0 0 0 1px #58a6ff;
        }
        
        /* METRICS & CARDS */
        div[data-testid="stMetricValue"] {
            color: #3fb950 !important; /* Green for money */
            font-family: 'Consolas', monospace;
        }
        
        /* MDT TERMINAL STYLE */
        .mdt-screen {
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-left: 5px solid #d29922;
            padding: 20px;
            font-family: 'Courier New', monospace;
            color: #d29922;
            margin-bottom: 20px;
        }
        
        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background-color: #010409;
            border-right: 1px solid #30363d;
        }
        
        /* ALERTS */
        .stSuccess {
            background-color: rgba(35, 134, 54, 0.1);
            border: 1px solid #238636;
            color: #3fb950;
        }
        .stError {
            background-color: rgba(218, 54, 51, 0.1);
            border: 1px solid #da3633;
            color: #f85149;
        }
        </style>
    """, unsafe_allow_html=True)

# ==================================================================================================
# [MODULE 3] : UTILITAIRES & SÉCURITÉ
# ==================================================================================================

class Utils:
    """Fonctions utilitaires pour le traitement des données."""
    
    @staticmethod
    def get_timestamp():
        """Retourne la date actuelle formatée."""
        return datetime.now().strftime("%d/%m/%Y")

    @staticmethod
    def get_full_timestamp():
        """Retourne l'horodatage précis pour les logs."""
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    @staticmethod
    def sanitize_currency(value):
        """Nettoie et convertit une valeur monétaire en float."""
        if isinstance(value, (int, float)):
            return float(value)
        try:
            clean_str = str(value).replace('$', '').replace(' ', '').replace(',', '').strip()
            return float(clean_str) if clean_str else 0.0
        except ValueError:
            return 0.0

class AuditLog:
    """Gestionnaire des journaux d'audit (Logs)."""
    
    @staticmethod
    def add(message):
        if 'audit_trail' not in st.session_state:
            st.session_state.audit_trail = []
        
        entry = f"[{Utils.get_full_timestamp()}] {message}"
        st.session_state.audit_trail.insert(0, entry)
        # Limite la taille des logs en mémoire session pour éviter le lag
        if len(st.session_state.audit_trail) > 100:
            st.session_state.audit_trail.pop()

# ==================================================================================================
# [MODULE 4] : COUCHE DE DONNÉES (DATA LAYER)
# ==================================================================================================

class DatabaseManager:
    """Gère la connexion et la synchronisation avec Google Sheets."""
    
    def __init__(self):
        self.conn = None
        self.connect()
        
    def connect(self):
        try:
            self.conn = st.connection("gsheets", type=GSheetsConnection)
        except Exception as e:
            st.error(f"ERREUR CRITIQUE DE CONNEXION BDD : {str(e)}")
            st.stop()
            
    def fetch_all(self):
        """Récupère toutes les tables nécessaires."""
        try:
            df_bank = self.conn.read(worksheet="Banque", ttl=0).dropna(how='all').fillna("")
            df_immat = self.conn.read(worksheet="Copie de Immatriculations", ttl=0).dropna(how='all').fillna("")
            df_permis = self.conn.read(worksheet="Points Permis", ttl=0).dropna(how='all').fillna("")
            return df_bank, df_immat, df_permis
        except Exception as e:
            st.error(f"ERREUR DE LECTURE DES DONNÉES : {str(e)}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    def push(self, worksheet_name, dataframe):
        """Envoie les modifications vers le cloud."""
        try:
            self.conn.update(worksheet=worksheet_name, data=dataframe)
            return True
        except Exception as e:
            st.error(f"ÉCHEC DE LA SAUVEGARDE : {str(e)}")
            return False

# ==================================================================================================
# [MODULE 5] : MOTEUR BANCAIRE & TRANSACTIONNEL (BUSINESS LOGIC)
# ==================================================================================================

class TransactionEngine:
    """Moteur gérant la logique financière complexe et les redirections."""
    
    def __init__(self, db_manager, df_bank):
        self.db = db_manager
        self.df = df_bank

    def get_account_index(self, username):
        """Trouve l'index d'un utilisateur dans la banque."""
        try:
            return self.df[self.df["Nom Roblox"] == username].index[0]
        except IndexError:
            return None

    def get_balance(self, username):
        idx = self.get_account_index(username)
        if idx is not None:
            return Utils.sanitize_currency(self.df.at[idx, "Solde"])
        return 0.0

    def debit_account(self, username, amount):
        """Débite un compte. Retourne False si fonds insuffisants."""
        idx = self.get_account_index(username)
        if idx is None: return False
        
        current_bal = self.get_balance(username)
        if current_bal >= amount:
            self.df.at[idx, "Solde"] = current_bal - amount
            return True
        return False

    def credit_account(self, username, amount):
        """Crédite un compte cible."""
        idx = self.get_account_index(username)
        if idx is not None:
            current_bal = self.get_balance(username)
            self.df.at[idx, "Solde"] = current_bal + amount
            return True
        else:
            AuditLog.add(f"ERREUR : Compte cible {username} introuvable pour crédit de {amount}$.")
            return False

    def process_dmv_payment(self, payer, assurance_type):
        """
        Gère la logique complexe du paiement DMV :
        1. Taxe (175$) -> Détruite.
        2. Assurance RCT (150$) -> une10000.
        3. Assurance Averis (130$) -> Moune2010.
        """
        # 1. Calcul du total à prélever au client
        total_cost = SystemConfig.PRICE_IMMAT_TAX
        
        if "AVERIS" in assurance_type:
            total_cost += SystemConfig.PRICE_INS_AVERIS
        elif "RCT" in assurance_type:
            total_cost += SystemConfig.PRICE_INS_RCT
            
        # 2. Tentative de débit global
        if not self.debit_account(payer, total_cost):
            return False, "Fonds insuffisants"

        # 3. Redirection des fonds (Dispatcher)
        if "RCT" in assurance_type:
            # Transfert vers le compte du chef RCT (Toi)
            self.credit_account(SystemConfig.ACC_TARGET_RCT, SystemConfig.PRICE_INS_RCT)
            AuditLog.add(f"Flux Financier : {SystemConfig.PRICE_INS_RCT}$ redirigés vers {SystemConfig.ACC_TARGET_RCT} (RCT).")
            
        if "AVERIS" in assurance_type:
            # Transfert vers le compte Averis
            self.credit_account(SystemConfig.ACC_TARGET_AVERIS, SystemConfig.PRICE_INS_AVERIS)
            AuditLog.add(f"Flux Financier : {SystemConfig.PRICE_INS_AVERIS}$ redirigés vers {SystemConfig.ACC_TARGET_AVERIS} (Averis).")
            
        # Note : Les 175$ de taxe ont été débités mais ne sont crédités nulle part. 
        # C'est le "Money Sink" demandé.
        
        return True, "Transaction validée"

# ==================================================================================================
# [MODULE 6] : INTERFACE UTILISATEUR (UI COMPONENTS)
# ==================================================================================================

def render_login_screen():
    st.image(SystemConfig.LOGO_URL, width=300)
    st.title("AUTHENTIFICATION SYSTÈME")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("ACCÈS PUBLIC")
        st.write("Accès limité aux dossiers personnels.")
        if st.button("CONNEXION CITOYEN"):
            st.session_state.role = "Civil"
            st.rerun()
            
    with col2:
        st.subheader("ACCÈS SERVICE")
        st.write("Department of Transport (RCT).")
        pwd = st.text_input("Badge Matricule", type="password", key="pwd_rct")
        if st.button("CONNEXION RCT"):
            if pwd == SystemConfig.KEY_RCT:
                st.session_state.role = "RCT"
                AuditLog.add("Connexion Agent RCT autorisée.")
                st.rerun()
            else:
                st.error("Matricule non reconnu.")
                
    with col3:
        st.subheader("ACCÈS ADMIN")
        st.write("Administration Comté & Staff.")
        pwd = st.text_input("Clé de chiffrement", type="password", key="pwd_staff")
        if st.button("CONNEXION STAFF"):
            if pwd == SystemConfig.KEY_STAFF:
                st.session_state.role = "Staff"
                AuditLog.add("Connexion Administrateur autorisée.")
                st.rerun()
            else:
                st.error("Clé de chiffrement invalide.")

def render_sidebar():
    with st.sidebar:
        st.image(SystemConfig.LOGO_URL, width=120)
        st.markdown(f"**Système :** {SystemConfig.APP_NAME}")
        st.markdown(f"**Version :** {SystemConfig.APP_VERSION}")
        st.markdown(f"**Utilisateur :** {st.session_state.role}")
        st.markdown("---")
        
        if st.button("❌ DÉCONNEXION SÉCURISÉE"):
            st.session_state.role = None
            st.rerun()
            
        st.markdown("---")
        st.caption("© 2026 Rensselaer County")
        st.caption("Secure Connection | TLS 1.3")

# ==================================================================================================
# [MODULE 7] : ORCHESTRATION PRINCIPALE (MAIN EXECUTION)
# ==================================================================================================

def main():
    # 1. Initialisation de la page
    st.set_page_config(
        page_title=SystemConfig.APP_NAME,
        page_icon=SystemConfig.APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    inject_custom_css()
    
    # 2. Gestion de l'état de session
    if 'role' not in st.session_state: st.session_state.role = None
    
    # 3. Routeur d'affichage
    if st.session_state.role is None:
        render_login_screen()
    else:
        render_sidebar()
        
        # 4. Chargement des données (Live Sync)
        db = DatabaseManager()
        df_bank, df_immat, df_pts = db.fetch_all()
        engine = TransactionEngine(db, df_bank)
        
        # 5. Définition des onglets disponibles
        tabs_list = ["💰 Services Bancaires", "🚗 DMV & Transports"]
        
        if st.session_state.role in ["RCT", "Staff"]:
            tabs_list.extend(["🛡️ Permis de Conduire", "👮 Terminal MDT"])
            
        if st.session_state.role == "Staff":
            tabs_list.extend(["🪪 Greffe & État Civil", "📜 Journaux Système"])
            
        tabs = st.tabs(tabs_list)
        
        # ------------------------------------------------------------------------------------------
        # ONGLET 1 : BANQUE
        # ------------------------------------------------------------------------------------------
        with tabs[0]:
            st.header("SERVICES BANCAIRES CENTRALISÉS")
            search_query = st.text_input("Recherche (Nom du citoyen)", placeholder="Ex: John Doe").lower()
            
            # Affichage des comptes
            for index, row in df_bank.iterrows():
                if search_query in str(row["Nom Roblox"]).lower():
                    with st.container(border=True):
                        col_a, col_b = st.columns([3, 1])
                        
                        balance = Utils.sanitize_currency(row["Solde"])
                        
                        with col_a:
                            st.subheader(f"👤 {row['Nom Roblox']}")
                            st.write(f"**Emploi :** {row['Emploiement']}")
                            st.write(f"**Date d'arrivée :** {row['Date d\'arrivée']}")
                            
                        with col_b:
                            st.metric("Solde Disponible", f"{balance:,.0f} $")
                        
                        # Actions Staff/RCT
                        if st.session_state.role in ["RCT", "Staff"]:
                            st.divider()
                            with st.expander("Opérations Financières"):
                                amount_op = st.number_input(f"Montant ($) - {row['Nom Roblox']}", min_value=0.0, step=100.0, key=f"amt_{index}")
                                c_op1, c_op2 = st.columns(2)
                                
                                if c_op1.button("DÉBITER (Taxe/Amende)", key=f"btn_deb_{index}"):
                                    if engine.debit_account(row["Nom Roblox"], amount_op):
                                        if db.push("Banque", df_bank):
                                            AuditLog.add(f"DÉBIT MANUEL : -{amount_op}$ sur {row['Nom Roblox']}")
                                            st.success("Opération validée.")
                                            time.sleep(1)
                                            st.rerun()
                                    else:
                                        st.error("Solde insuffisant.")

        # ------------------------------------------------------------------------------------------
        # ONGLET 2 : DMV (IMMATRICULATIONS)
        # ------------------------------------------------------------------------------------------
        with tabs[1]:
            st.header("REGISTRE DES VÉHICULES AUTOMOBILES")
            
            # Formulaire d'enregistrement (RCT/Staff seulement)
            if st.session_state.role in ["RCT", "Staff"]:
                with st.container(border=True):
                    st.subheader("📝 NOUVEL ENREGISTREMENT")
                    with st.form("new_vehicle_form"):
                        c_f1, c_f2 = st.columns(2)
                        with c_f1:
                            f_owner = st.selectbox("Propriétaire", ["Sélectionner..."] + df_bank["Nom Roblox"].tolist())
                            f_brand = st.selectbox("Marque (Catalogue Officiel)", sorted(SystemConfig.VEHICLE_DB))
                        with c_f2:
                            f_plate = st.text_input("Numéro de Plaque", placeholder="Ex: RCRP-001")
                            f_assu = st.selectbox("Formule d'Assurance", ["Aucune", "AVERIS (130$ / Semaine)", "RCT (150$ / Semaine)"])
                        
                        # Affichage dynamique du prix
                        price_preview = SystemConfig.PRICE_IMMAT_TAX
                        if "AVERIS" in f_assu: price_preview += SystemConfig.PRICE_INS_AVERIS
                        elif "RCT" in f_assu: price_preview += SystemConfig.PRICE_INS_RCT
                        
                        st.info(f"💵 Montant total à facturer : **{price_preview} $** (Dont 175$ de taxe fixe)")
                        
                        if st.form_submit_button("VALIDER ET FACTURER"):
                            if f_owner != "Sélectionner..." and f_plate:
                                success, msg = engine.process_dmv_payment(f_owner, f_assu)
                                if success:
                                    # Création de l'entrée véhicule
                                    new_vehicle = pd.DataFrame([{
                                        "Horodateur": Utils.get_timestamp(),
                                        "Nom d'utilisateur ROBLOX": f_owner,
                                        "Marque du véhicule": f_brand,
                                        "Numéro de la plaque": f_plate,
                                        "Assurance": f_assu
                                    }])
                                    # Sauvegarde simultanée Banque + Immat
                                    if db.push("Banque", df_bank) and db.push("Copie de Immatriculations", pd.concat([df_immat, new_vehicle])):
                                        AuditLog.add(f"IMMATRICULATION : {f_plate} ({f_brand}) pour {f_owner}")
                                        st.success(f"Véhicule enregistré. {msg}")
                                        time.sleep(1)
                                        st.rerun()
                                else:
                                    st.error(f"Erreur de transaction : {msg}")
                            else:
                                st.warning("Veuillez remplir tous les champs.")

            st.divider()
            st.subheader("🔎 RECHERCHE PLAQUES")
            q_dmv = st.text_input("Rechercher (Plaque, Modèle, Propriétaire)", key="search_dmv").lower()
            
            # Table de résultats
            results_data = []
            for i, row in df_immat.iterrows():
                if q_dmv in str(row).lower():
                    results_data.append(row)
            
            if results_data:
                st.dataframe(pd.DataFrame(results_data), use_container_width=True)
            else:
                st.caption("Aucun véhicule trouvé.")

        # ------------------------------------------------------------------------------------------
        # ONGLET 3 : PERMIS (GESTION POINTS)
        # ------------------------------------------------------------------------------------------
        if "🛡️ Permis de Conduire" in tabs_list:
            with tabs[tabs_list.index("🛡️ Permis de Conduire")]:
                st.header("GESTION DES PERMIS DE CONDUIRE")
                
                q_permis = st.text_input("Rechercher dossier conducteur").lower()
                
                for i, row in df_permis.iterrows():
                    if q_permis in str(row["Nom Roblox"]).lower():
                        with st.container(border=True):
                            c_p1, c_p2, c_p3 = st.columns([2, 1, 1])
                            
                            with c_p1:
                                st.write(f"**Conducteur :** {row['Nom Roblox']}")
                                st.caption(f"Discord : {row['Nom Discord']}")
                            
                            with c_p2:
                                pts = int(row["PTS"]) if str(row["PTS"]).isdigit() else 0
                                st.metric("Points Restants", f"{pts} / 25")
                            
                            with c_p3:
                                is_valid = str(row["Validité"]).upper() == "OUI"
                                if is_valid:
                                    st.success("VALIDE")
                                else:
                                    st.error("SUSPENDU")
                            
                            with st.expander("Sanctions / Récupération"):
                                new_pts = st.slider(f"Ajuster points pour {row['Nom Roblox']}", 0, 25, pts, key=f"sld_{i}")
                                if st.button("Appliquer Modification", key=f"btn_pts_{i}"):
                                    df_permis.at[i, "PTS"] = new_pts
                                    df_permis.at[i, "Validité"] = "OUI" if new_pts > 0 else "NON"
                                    if db.push("Points Permis", df_permis):
                                        AuditLog.add(f"PERMIS : Ajustement points {row['Nom Roblox']} -> {new_pts}")
                                        st.rerun()

        # ------------------------------------------------------------------------------------------
        # ONGLET 4 : MDT (POLICE TERMINAL)
        # ------------------------------------------------------------------------------------------
        if "👮 Terminal MDT" in tabs_list:
            with tabs[tabs_list.index("👮 Terminal MDT")]:
                st.header("MDT - MOBILE DATA TERMINAL")
                st.warning("USAGE STRICTEMENT RÉSERVÉ AUX FORCES DE L'ORDRE")
                
                search_ncic = st.text_input("NCIC QUERY (NAME / PLATE)", key="ncic_input").upper()
                
                if search_ncic:
                    # Simulation d'interface terminal
                    st.markdown(f"""
                        <div class="mdt-screen">
                        CONNECTING TO STATE DATABASE... ESTABLISHED.<br>
                        QUERY: {search_ncic}<br>
                        ------------------------------------------------<br>
                        SEARCHING CRIMINAL RECORDS... [0]<br>
                        SEARCHING WARRANTS... [0]<br>
                        SEARCHING DMV RECORDS... [MATCH FOUND]<br>
                        ------------------------------------------------<br>
                        STATUS: <span style="color:#00ff00">CLEAR</span><br>
                        DRIVER LICENSE: VALID<br>
                        INSURANCE STATUS: CHECK PHYSICAL PAPERWORK
                        </div>
                    """, unsafe_allow_html=True)

        # ------------------------------------------------------------------------------------------
        # ONGLET 5 : GREFFE (AUTO-CREATION)
        # ------------------------------------------------------------------------------------------
        if "🪪 Greffe & État Civil" in tabs_list:
            with tabs[tabs_list.index("🪪 Greffe & État Civil")]:
                st.header("BUREAU DU GREFFIER")
                st.info("Ce module génère automatiquement les comptes bancaires et permis.")
                
                with st.form("creation_dossier"):
                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        new_roblox = st.text_input("Nom d'utilisateur ROBLOX (Exact)")
                    with col_g2:
                        new_discord = st.text_input("Nom d'utilisateur DISCORD")
                    
                    new_job = st.selectbox("Statut Initial", ["Civil", "RCT Recrue", "Sheriff Cadet", "EMS"])
                    
                    st.write(f"**Dotation automatique :** {SystemConfig.STARTING_BALANCE:,.0f} $")
                    st.write(f"**Points Permis :** {SystemConfig.STARTING_PTS}")
                    st.write(f"**Date d'arrivée :** {Utils.get_timestamp()} (Automatique)")
                    
                    if st.form_submit_button("🔨 CRÉER LE DOSSIER CITOYEN"):
                        if new_roblox and new_discord:
                            # 1. Création entrée Banque
                            entry_bank = pd.DataFrame([{
                                "Solde": SystemConfig.STARTING_BALANCE,
                                "Emploiement": new_job,
                                "Nom Discord": new_discord,
                                "Nom Roblox": new_roblox,
                                "Date d'arrivée": Utils.get_timestamp() # Date Auto
                            }])
                            
                            # 2. Création entrée Permis
                            entry_permis = pd.DataFrame([{
                                "Nom Discord": new_discord,
                                "Nom Roblox": new_roblox,
                                "PTS": SystemConfig.STARTING_PTS,
                                "Validité": "OUI"
                            }])
                            
                            # 3. Sauvegarde transactionnelle
                            success_b = db.push("Banque", pd.concat([df_bank, entry_bank]))
                            success_p = db.push("Points Permis", pd.concat([df_permis, entry_permis]))
                            
                            if success_b and success_p:
                                AuditLog.add(f"NOUVEAU DOSSIER : {new_roblox} créé le {Utils.get_timestamp()}")
                                st.balloons()
                                st.success("Dossier créé avec succès dans tous les registres.")
                                time.sleep(2)
                                st.rerun()
                        else:
                            st.error("Noms obligatoires.")

        # ------------------------------------------------------------------------------------------
        # ONGLET 6 : JOURNAUX (LOGS)
        # ------------------------------------------------------------------------------------------
        if "📜 Journaux Système" in tabs_list:
            with tabs[tabs_list.index("📜 Journaux Système")]:
                st.header("REGISTRE DES ACTIVITÉS")
                st.caption("Ce registre est visible uniquement par l'administration. Ne contient pas de code.")
                
                if st.button("Rafraîchir les logs"):
                    st.rerun()
                    
                for log_entry in st.session_state.audit_trail:
                    st.text(log_entry)

# ==================================================================================================
# POINT D'ENTRÉE DU PROGRAMME
# ==================================================================================================
if __name__ == "__main__":
    main()
