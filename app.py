import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURATION PAGE ---
st.set_page_config(
    page_title="RCRP - Système Intégral",
    layout="wide"
)

# --- 2. STYLE CSS COMPLET (DÉPLOYÉ LIGNE PAR LIGNE) ---
st.markdown("""
    <style>
    /* Correction de l'affichage des onglets */
    .block-container { 
        padding-top: 6rem !important; 
    }
    
    /* Logo Sidebar Haute Définition */
    [data-testid="stSidebar"] img { 
        border-radius: 12px; 
        width: 250px !important; 
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 20px;
        display: block;
    }

    /* Badge pour l'état de l'assurance */
    .badge-assu {
        background-color: #ff4b4b;
        color: white;
        padding: 3px 12px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.85rem;
    }

    /* Style du reçu noir (Mode Nuit) */
    .ticket-fix { 
        background-color: #000000 !important; 
        color: #ffffff !important; 
        padding: 20px; 
        border: 2px solid #ff4b4b; 
        border-radius: 10px; 
        font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INITIALISATION & CONNEXION ---
if "role" not in st.session_state:
    st.session_state.role = None

conn = st.connection("gsheets", type=GSheetsConnection)

# Paramètres de redirection financière
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"

# Codes de sécurité
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"

# Lien Image Logo
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

# Fonction de récupération des données avec gestion d'erreurs
def get_data(sheet_name):
    st.cache_data.clear()
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        return df.dropna(how='all').fillna("")
    except Exception as e:
        st.error(f"Erreur de chargement de la feuille {sheet_name} : {e}")
        return pd.DataFrame()

# Chargement des bases de données
df_banque = get_data("Banque")
df_im = get_data("Copie de Immatriculations")
df_pts = get_data("Points Permis")

# ==========================================
# 🚪 PORTAIL DE CONNEXION
# ==========================================
if st.session_state.role is None:
    st.title("🏛️ Portail RCRP")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.subheader("👤 Citoyen")
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()
                
    with col2:
        with st.container(border=True):
            st.subheader("🛠️ Employés RCT")
            kp = st.text_input("Code d'accès Pro", type="password", key="p_login")
            if st.button("Connexion Pro", use_container_width=True):
                if kp == CODE_PRO:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("Code erroné")
                    
    with col3:
        with st.container(border=True):
            st.subheader("👮 Gouvernement")
            ks = st.text_input("Code d'accès Staff", type="password", key="s_login")
            if st.button("Connexion Staff", use_container_width=True):
                if ks == CODE_ADMIN:
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    st.error("Code erroné")
    st.stop()

# ==========================================
# 🖥️ INTERFACE CONNECTÉE
# ==========================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown(f"🎭 **Session :** `{st.session_state.role}`")
    
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None
        st.rerun()
        
    st.divider()
    st.write(f"📅 Date : {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"⏰ Heure : {datetime.now().strftime('%H:%M')}")

# Navigation par Onglets
tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers & Points", "💰 Banque"])

# --- ONGLET 1 : IMMATRICULATIONS ---
with tabs[0]:
    st.header("🚗 Registre des Véhicules")
    
    with st.expander("➕ Enregistrer un véhicule", expanded=True):
        user_select = st.selectbox("Sélectionner le Propriétaire", ["---"] + df_banque["Nom Roblox"].tolist())
        marque_v = st.text_input("Marque / Modèle du véhicule")
        plaque_v = st.text_input("Numéro de la plaque (ex: ABC-123)")
        assu_select = st.selectbox("Type d'Assurance souhaitée", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
        code_v = st.text_input("🔑 Code Secret du véhicule (OBLIGATOIRE)", type="password")
        
        # --- LOGIQUE DE CALCUL DÉTAILLÉE (PAS DE COMPRESSION) ---
        cost_ville = 175
        cost_assu = 0
        
        if "AVERIS" in assu_select:
            cost_assu = 130
        
        if "RCT" in assu_select:
            cost_assu = 150
            
        # Promo Trio RCT (le 3ème véhicule assuré chez RCT est gratuit)
        # On compte combien de véhicules le citoyen a déjà chez RCT
        rct_count = len(df_im[(df_im["Nom d'utilisateur ROBLOX"] == user_select) & (df_im["Assurance"].str.contains("RCT"))])
        
        if "RCT" in assu_select:
            if rct_count >= 2:
                cost_assu = 0
                st.success("🎁 Offre Trio : 3ème assurance gratuite chez RCT !")

        # Taxe Jeune Conducteur (Moins de 30 jours en ville)
        cost_jeune = 0
        if user_select != "---":
            u_row = df_banque[df_banque["Nom Roblox"] == user_select]
            if not u_row.empty:
                try:
                    date_string = str(u_row.iloc[0]["Date d'arrivée"])
                    date_arr = datetime.strptime(date_string, "%d/%m/%Y")
                    delta_jours = (datetime.now() - date_arr).days
                    if delta_jours < 30:
                        cost_jeune = 50
                except Exception:
                    pass
        
        total_facture = cost_ville + cost_assu + cost_jeune
        
        # Affichage du reçu détaillé
        st.markdown(f"""
        <div class="ticket-fix">
            <b>📄 REÇU DE PAIEMENT - RCRP</b><br>
            --------------------------------<br>
            Frais d'Immatriculation : 175$<br>
            Service Assurance : {cost_assu}$<br>
            Taxe Jeune Conducteur : {cost_jeune}$<br>
            --------------------------------<br>
            <b>TOTAL À PRÉLEVER : {total_facture}$</b>
        </div>
        """, unsafe_allow_html=True)

        # Bouton de validation
        if st.button("✅ Valider l'enregistrement et Payer"):
            if user_select != "---" and plaque_v and code_v:
                # Recherche de l'index du client
                idx_user = df_banque[df_banque["Nom Roblox"] == user_select].index[0]
                current_solde = float(df_banque.at[idx_user, "Solde"])
                
                if current_solde >= total_facture:
                    # Débit du compte citoyen
                    df_banque.at[idx_user, "Solde"] = current_solde - total_facture
                    
                    # Virement aux comptes entreprises (RCT ou Averis)
                    dest_account = None
                    if "AVERIS" in assu_select:
                        dest_account = TARGET_AVERIS
                    
                    if "RCT" in assu_select:
                        dest_account = TARGET_RCT
                    
                    if dest_account is not None:
                        if cost_assu > 0:
                            idx_dest = df_banque[df_banque["Nom Roblox"] == dest_account].index[0]
                            old_dest_solde = float(df_banque.at[idx_dest, "Solde"])
                            df_banque.at[idx_dest, "Solde"] = old_dest_solde + cost_assu
                    
                    # Création de la ligne d'immatriculation
                    new_immat = pd.DataFrame([{
                        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                        "Nom d'utilisateur ROBLOX": user_select,
                        "Marque du véhicule": marque_v,
                        "Numéro de la plaque": plaque_v,
                        "Assurance": assu_select,
                        "CODE": str(code_v)
                    }])
                    
                    # Sauvegarde générale
                    conn.update(worksheet="Banque", data=df_banque)
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_immat], ignore_index=True))
                    
                    st.success("Opération réussie ! Le véhicule est enregistré.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Solde bancaire insuffisant pour cette opération.")
            else:
                st.warning("Veuillez remplir toutes les informations (Propriétaire, Plaque, Code Secret).")

    # Affichage de la base existante
    st.divider()
    search_q = st.text_input("🔍 Rechercher une plaque ou un propriétaire dans la base").lower()
    
    if not df_im.empty:
        filtered_im = df_im[df_im.apply(lambda x: search_q in str(x).lower(), axis=1)]
        
        for i, row in filtered_im.iterrows():
            with st.container(border=True):
                st.markdown(f"<span class='badge-assu'>{row['Assurance']}</span>", unsafe_allow_html=True)
                st.write(f"🚗 **Plaque : {row['Numéro de la plaque']}**")
                st.write(f"👤 Propriétaire : {row['Nom d\'utilisateur ROBLOX']} | Modèle : {row['Marque du véhicule']}")
                
                with st.expander("⚙️ Options de gestion du véhicule"):
                    check_code = st.text_input("Entrer le Code Secret pour gérer", type="password", key=f"manage_{i}")
                    if check_code == str(row['CODE']) or st.session_state.role == "Staff":
                        if st.button("🗑️ Supprimer le véhicule de la base", key=f"del_{i}"):
                            new_df_im = df_im.drop(i)
                            conn.update(worksheet="Copie de Immatriculations", data=new_df_im)
                            st.success("Véhicule supprimé avec succès.")
                            st.rerun()

# --- ONGLET 2 : POINTS (ROBLOX / DISCORD) ---
with tabs[1]:
    st.header("🪪 Dossiers Citoyens")
    
    query_pts = st.text_input("🔍 Rechercher un citoyen (Nom Roblox ou Pseudo Discord)").lower()
    
    if query_pts:
        # Recherche croisée dans la base banque
        matches = df_banque[
            (df_banque["Nom Roblox"].str.lower().str.contains(query_pts, na=False)) | 
            (df_banque["Nom Discord"].str.lower().str.contains(query_pts, na=False))
        ]
        
        if not matches.empty:
            for _, citoyen in matches.iterrows():
                # On récupère ses points dans la table Points
                pts_data = df_pts[df_pts["Nom Roblox"] == citoyen["Nom Roblox"]]
                if not pts_data.empty:
                    st.metric(
                        label=f"Points de {citoyen['Nom Roblox']} (@{citoyen['Nom Discord']})", 
                        value=f"{pts_data.iloc[0]['PTS']} / 25"
                    )
        else:
            st.warning("Aucun dossier trouvé pour cette recherche.")
    
    # Création de profil (Staff uniquement)
    if st.session_state.role == "Staff":
        st.divider()
        with st.expander("👤 Créer un nouveau profil citoyen"):
            with st.form("creation_profil_form"):
                new_rob = st.text_input("Nom d'utilisateur Roblox du citoyen")
                new_disc = st.text_input("Pseudo Discord du citoyen")
                
                if st.form_submit_button("🚀 Créer le dossier complet"):
                    # Date d'arrivée automatique comme demandé
                    current_date = datetime.now().strftime("%d/%m/%Y")
                    
                    # Création des lignes de données
                    new_bank_row = pd.DataFrame([{
                        "Solde": 15000, 
                        "Nom Discord": new_disc, 
                        "Nom Roblox": new_rob, 
                        "Date d'arrivée": current_date
                    }])
                    
                    new_pts_row = pd.DataFrame([{
                        "Nom Roblox": new_rob, 
                        "PTS": 25
                    }])
                    
                    # Mise à jour des bases
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, new_bank_row], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_pts_row], ignore_index=True))
                    
                    st.success(f"Profil créé pour {new_rob} à la date du {current_date} !")
                    time.sleep(1)
                    st.rerun()

# --- ONGLET 3 : BANQUE (RCT VS STAFF) ---
with tabs[2]:
    st.header("💰 État de la Banque")
    
    query_bank = st.text_input("🔍 Rechercher un compte (Roblox ou Discord)").lower()
    
    if query_bank:
        # Recherche croisée Roblox ou Discord dans la base banque
        res_bank = df_banque[
            (df_banque["Nom Roblox"].str.lower().str.contains(query_bank, na=False)) | 
            (df_banque["Nom Discord"].str.lower().str.contains(query_bank, na=False))
        ]
        
        if not res_bank.empty:
            for _, row_b in res_bank.iterrows():
                with st.container(border=True):
                    st.subheader(f"👤 {row_b['Nom Roblox']} (@{row_b['Nom Discord']})")
                    
                    col_solde, col_pts_bank = st.columns(2)
                    
                    with col_solde:
                        st.metric(label="Solde Bancaire Actuel", value=f"{float(row_b['Solde']):,.0f} $")
                        
                    with col_pts_bank:
                        pts_info = df_pts[df_pts["Nom Roblox"] == row_b["Nom Roblox"]]
                        if not pts_info.empty:
                            st.metric(label="Points de Permis", value=f"{pts_info.iloc[0]['PTS']} / 25")
                    
                    st.write(f"📅 Date d'arrivée enregistrée : {row_b['Date d\'arrivée']}")
                    
                    # --- SECTION ACTIONS SPÉCIALES (PRO ET STAFF) ---
                    if st.session_state.role in ["RCT", "Staff"]:
                        st.divider()
                        
                        # Titre dynamique selon le rôle
                        if st.session_state.role == "RCT":
                            st.markdown("### 🛠️ Facturation Professionnelle (RCT)")
                        else:
                            st.markdown("### 👮 Gestion Administrative (Staff)")
                            
                        with st.expander(f"Effectuer un retrait d'argent sur le compte de {row_b['Nom Roblox']}"):
                            facture_amount = st.number_input("Montant à retirer ($)", min_value=1, value=100, key=f"amt_{row_b['Nom Roblox']}")
                            raison = st.text_input("Motif du retrait", placeholder="Raison de la facture ou amende...", key=f"rs_{row_b['Nom Roblox']}")
                            
                            if st.button(f"Confirmer le retrait pour {row_b['Nom Roblox']}", key=f"btn_{row_b['Nom Roblox']}"):
                                if float(row_b['Solde']) >= facture_amount:
                                    # Index du citoyen cible
                                    idx_client = df_banque[df_banque["Nom Roblox"] == row_b["Nom Roblox"]].index[0]
                                    
                                    # On retire l'argent au client quoi qu'il arrive
                                    df_banque.at[idx_client, "Solde"] = float(df_banque.at[idx_client, "Solde"]) - facture_amount
                                    
                                    # LOGIQUE DE REDIRECTION (RCT VS STAFF)
                                    msg_info = ""
                                    
                                    if st.session_state.role == "RCT":
                                        # Si c'est un employé RCT, l'argent va sur le compte "une10000"
                                        idx_rct = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                        old_rct_solde = float(df_banque.at[idx_rct, "Solde"])
                                        df_banque.at[idx_rct, "Solde"] = old_rct_solde + facture_amount
                                        msg_info = f"Argent transféré avec succès vers le compte {TARGET_RCT}."
                                    else:
                                        # Si c'est un Staff, l'argent est juste supprimé (pas de transfert vers ton compte)
                                        msg_info = "Argent retiré du compte (Amende / Ajustement Staff)."
                                    
                                    # Mise à jour finale
                                    conn.update(worksheet="Banque", data=df_banque)
                                    
                                    # Affichage du reçu de transaction
                                    st.markdown(f"""
                                    <div class="ticket-fix">
                                        <b>🧾 REÇU DE TRANSACTION - {st.session_state.role}</b><br>
                                        --------------------------------<br>
                                        Compte débité : {row_b['Nom Roblox']}<br>
                                        Montant retiré : {facture_amount}$<br>
                                        Motif : {raison}<br>
                                        --------------------------------<br>
                                        <i>{msg_info}</i>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error("Le citoyen n'a pas les fonds nécessaires pour ce retrait.")
        else:
            st.warning("Aucun compte bancaire trouvé pour cette recherche.")
    else:
        st.info("Veuillez entrer un nom (Roblox ou Discord) pour consulter un compte.")

# --- FOOTER ---
st.markdown("---")
st.markdown("<center><small>RCRP Système de Gestion Intégral v13.6 | 2026</small></center>", unsafe_allow_html=True)
