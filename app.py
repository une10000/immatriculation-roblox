import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE ET INTERFACE
# ==============================================================================
st.set_page_config(
    page_title="RCRP - Système Intégral Professionnel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. STYLE CSS PERSONNALISÉ (PRÉSERVÉ À 100%)
# ==============================================================================
st.markdown("""
    <style>
    .block-container { 
        padding-top: 6rem !important; 
    }
    
    [data-testid="stSidebar"] img { 
        border-radius: 15px; 
        width: 250px !important; 
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 25px;
        display: block;
        border: 1px solid #333;
    }

    .badge-assu {
        background-color: #ff4b4b;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }

    .ticket-fix { 
        background-color: #0d0d0d !important; 
        color: #00ff00 !important; 
        padding: 25px; 
        border: 2px dashed #ff4b4b; 
        border-radius: 12px; 
        font-family: 'Courier New', monospace;
        line-height: 1.5;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. VARIABLES DE SÉCURITÉ ET CONSTANTES
# ==============================================================================
if "role" not in st.session_state:
    st.session_state.role = None

conn = st.connection("gsheets", type=GSheetsConnection)

# Cibles de virement
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"

# Codes d'accès
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"

# Logo officiel
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

# ==============================================================================
# 4. FONCTIONS DE CHARGEMENT (GSHEETS)
# ==============================================================================
def get_data(sheet_name):
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except Exception as e:
        st.error(f"Erreur lors du chargement de {sheet_name}")
        return pd.DataFrame()

# Chargement initial
df_banque = get_data("Banque")
df_im = get_data("Copie de Immatriculations")
df_pts = get_data("Points Permis")

# ==============================================================================
# 5. SYSTÈME D'AUTHENTIFICATION (PORTAIL)
# ==============================================================================
if st.session_state.role is None:
    st.title("🏛️ Système de Gestion RCRP - Accès")
    
    col_civ, col_pro, col_staff = st.columns(3)
    
    with col_civ:
        with st.container(border=True):
            st.subheader("👤 Secteur Civil")
            if st.button("Accès Portail Public", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()
                
    with col_pro:
        with st.container(border=True):
            st.subheader("🛠️ Professionnel")
            in_pro = st.text_input("Saisir Code RCT", type="password")
            if st.button("Authentification RCT", use_container_width=True):
                if in_pro == CODE_PRO:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("Code erroné.")
                    
    with col_staff:
        with st.container(border=True):
            st.subheader("👮 Gouvernement")
            in_staff = st.text_input("Saisir Code Staff", type="password")
            if st.button("Authentification Staff", use_container_width=True):
                if in_staff == CODE_ADMIN:
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    st.error("Code erroné.")
    st.stop()

# ==============================================================================
# 6. NAVIGATION LATÉRALE (SIDEBAR) AVEC HEURE
# ==============================================================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    
    # --- C'EST ICI QUE L'HEURE EST AJOUTÉE ---
    st.markdown("---")
    maintenant = datetime.now()
    st.markdown(f"📅 **Date :** {maintenant.strftime('%d/%m/%Y')}")
    st.markdown(f"⏰ **Heure :** {maintenant.strftime('%H:%M:%S')}") # <--- L'HEURE EST LÀ
    
    if st.button("🔄 Actualiser l'heure"): # Petit bouton pour mettre à jour sans bug
        st.rerun()
    st.markdown("---")
    # ----------------------------------------

    st.info(f"Rôle : **{st.session_state.role}**")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()

# ==============================================================================
# 7. GESTION DES ONGLETS PRINCIPAUX
# ==============================================================================
tab_immat, tab_dossier, tab_banque = st.tabs([
    "🚗 Registre National", 
    "🪪 Dossiers Citoyens", 
    "💰 Gestion Bancaire"
])

# ------------------------------------------------------------------------------
# ONGLET 1 : IMMATRICULATIONS
# ------------------------------------------------------------------------------
with tab_immat:
    st.header("🚗 Registre des Véhicules")
    
    # Formulaire Civil
    if st.session_state.role not in ["RCT", "Staff"]:
        with st.expander("➕ Enregistrer un nouveau véhicule", expanded=True):
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                proprio = st.selectbox("Sélectionner le Propriétaire", ["---"] + df_banque["Nom Roblox"].tolist())
                marque = st.text_input("Marque et Modèle du véhicule")
                plaque_in = st.text_input("Numéro de la Plaque")
                
            with col_f2:
                assurance = st.selectbox("Type d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
                code_sec = st.text_input("Définir un Code Secret", type="password")
            
            # Calcul des frais détaillés
            f_fixe = 175
            f_assu = 0
            f_jeune = 0
            
            if "AVERIS" in assurance:
                f_assu = 130
            elif "RCT" in assurance:
                f_assu = 150
                
            # Logique Offre Trio RCT (2 payantes, la 3ème gratuite)
            rct_count = len(df_im[(df_im["Nom d'utilisateur ROBLOX"] == proprio) & (df_im["Assurance"].str.contains("RCT"))])
            if "RCT" in assurance and rct_count >= 2:
                f_assu = 0
                
            # Logique Taxe Jeune Conducteur
            if proprio != "---":
                u_d = df_banque[df_banque["Nom Roblox"] == proprio]
                try:
                    d_arr = datetime.strptime(str(u_d.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                    if (datetime.now() - d_arr).days < 30:
                        f_jeune = 50
                except:
                    pass
            
            total_t = f_fixe + f_assu + f_jeune
            
            # Affichage du reçu avant validation
            st.markdown(f"""
            <div class="ticket-fix">
                🧾 <b>PRÉ-VISUALISATION FACTURE</b><br>
                Propriétaire: {proprio}<br>
                Frais Dossier: 175$<br>
                Assurance: {f_assu}$<br>
                Taxe Jeune: {f_jeune}$<br>
                -------------------------<br>
                <b>MONTANT À DÉBITER: {total_t}$</b>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✅ Valider l'enregistrement et le paiement"):
                if proprio != "---" and plaque_in and code_sec:
                    idx_b = df_banque[df_banque["Nom Roblox"] == proprio].index[0]
                    if float(df_banque.at[idx_b, "Solde"]) >= total_t:
                        # Débit citoyen
                        df_banque.at[idx_b, "Solde"] -= total_t
                        
                        # Virement entreprise
                        if f_assu > 0:
                            cible = TARGET_AVERIS if "AVERIS" in assurance else TARGET_RCT
                            idx_target = df_banque[df_banque["Nom Roblox"] == cible].index[0]
                            df_banque.at[idx_target, "Solde"] = float(df_banque.at[idx_target, "Solde"]) + f_assu
                        
                        # Ajout au registre
                        new_v = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y"), 
                            "Nom d'utilisateur ROBLOX": proprio, 
                            "Marque du véhicule": marque, 
                            "Numéro de la plaque": plaque_in, 
                            "Assurance": assurance, 
                            "CODE": str(code_sec)
                        }])
                        
                        conn.update(worksheet="Banque", data=df_banque)
                        conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_v], ignore_index=True))
                        st.success("Opération terminée avec succès !"); time.sleep(1); st.rerun()
                    else:
                        st.error("Solde insuffisant pour cette opération.")
    else:
        st.info("⚠️ Le registre est en mode consultation pour les autorités.")

    # Affichage des plaques enregistrées
    st.divider()
    search_p = st.text_input("🔍 Rechercher une Plaque ou un Propriétaire").lower()
    
    for i, r in df_im.iterrows():
        if search_p in str(r['Numéro de la plaque']).lower() or search_p in str(r['Nom d\'utilisateur ROBLOX']).lower():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2,2,1])
                c1.write(f"🆔 **PLAQUE : {r['Numéro de la plaque']}**")
                c2.write(f"👤 Propriétaire : {r['Nom d\'utilisateur ROBLOX']}")
                c3.markdown(f"<span class='badge-assu'>{r['Assurance']}</span>", unsafe_allow_html=True)
                
                with st.expander("🗑️ Radier le véhicule"):
                    input_code = st.text_input("Saisir Code Secret", type="password", key=f"del_{i}")
                    if input_code == str(r['CODE']) or st.session_state.role == "Staff":
                        if st.button("Confirmer la suppression", key=f"btn_{i}"):
                            conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                            st.success("Véhicule radié."); time.sleep(1); st.rerun()

# ------------------------------------------------------------------------------
# ONGLET 2 : DOSSIERS & PAYE
# ------------------------------------------------------------------------------
with tab_dossier:
    st.header("🪪 Gestion des Dossiers Citoyens")
    
    if st.session_state.role == "Staff":
        with st.container(border=True):
            st.subheader("🏦 Script de Paye Mensuelle & Prélèvements")
            st.write("Distribution : **15,000$** (Civils) | **17,000$** (RCT)")
            
            if st.button("🧧 EXÉCUTER LA PAYE GLOBALE", use_container_width=True):
                with st.status("Traitement en cours..."):
                    # 1. Traitement des salaires via colonne Emploiement
                    for idx, row in df_banque.iterrows():
                        montant = 15000
                        if "RCT" in str(row["Emploiement"]).upper():
                            montant = 17000
                            st.write(f"💸 {row['Nom Roblox']} (Employé) : +17k")
                        else:
                            st.write(f"👤 {row['Nom Roblox']} (Civil) : +15k")
                        df_banque.at[idx, "Solde"] = float(row["Solde"]) + montant
                    
                    # 2. Prélèvement des assurances (vers une10000 / Moune2010)
                    track_rct = {}
                    for _, v in df_im.iterrows():
                        own = v["Nom d'utilisateur ROBLOX"]
                        if own in df_banque["Nom Roblox"].values:
                            idx_b = df_banque[df_banque["Nom Roblox"] == own].index[0]
                            if "RCT" in v["Assurance"]:
                                track_rct[own] = track_rct.get(own, 0) + 1
                                if track_rct[own] <= 2:
                                    df_banque.at[idx_b, "Solde"] -= 150
                                    df_banque.loc[df_banque["Nom Roblox"] == TARGET_RCT, "Solde"] += 150
                            elif "AVERIS" in v["Assurance"]:
                                df_banque.at[idx_b, "Solde"] -= 130
                                df_banque.loc[df_banque["Nom Roblox"] == TARGET_AVERIS, "Solde"] += 130
                                
                    conn.update(worksheet="Banque", data=df_banque)
                    st.success("Distribution et facturation terminées !"); time.sleep(1); st.rerun()

    # Barre de recherche de dossier
    search_d = st.text_input("🔍 Rechercher un Dossier Citoyen").lower()
    if search_d:
        res = df_banque[df_banque["Nom Roblox"].str.lower().str.contains(search_d, na=False)]
        for _, c in res.iterrows():
            with st.container(border=True):
                st.subheader(f"Citoyen : {c['Nom Roblox']}")
                st.write(f"🛡️ Poste : {c['Emploiement']}")
                p_row = df_pts[df_pts["Nom Roblox"] == c["Nom Roblox"]]
                if not p_row.empty:
                    st.metric("Points Permis", f"{p_row.iloc[0]['PTS']} / 25")

    # Création de profil (Staff uniquement)
    if st.session_state.role == "Staff":
        with st.expander("👤 Créer un nouveau profil citoyen"):
            with st.form("new_cit_form"):
                nr = st.text_input("Nom Roblox")
                nd = st.text_input("Pseudo Discord")
                if st.form_submit_button("Enregistrer le citoyen"):
                    dt_now = datetime.now().strftime("%d/%m/%Y")
                    # Ajout banque (avec date auto)
                    new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": nd, "Nom Roblox": nr, "Date d'arrivée": dt_now, "Emploiement": "Civil"}])
                    # Ajout points
                    new_p = pd.DataFrame([{"Nom Roblox": nr, "PTS": 25}])
                    
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, new_b], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, new_p], ignore_index=True))
                    st.success("Profil créé !"); time.sleep(1); st.rerun()

# ------------------------------------------------------------------------------
# ONGLET 3 : BANQUE CENTRALE
# ------------------------------------------------------------------------------
with tab_banque:
    st.header("💰 Gestion Bancaire Centrale")
    
    search_b = st.text_input("🔍 Rechercher un compte (Nom Roblox)").lower()
    if search_b:
        res_b = df_banque[df_banque["Nom Roblox"].str.lower().str.contains(search_b, na=False)]
        for idx, row in res_b.iterrows():
            with st.container(border=True):
                st.subheader(f"Compte : {row['Nom Roblox']}")
                st.metric("Solde actuel", f"{float(row['Solde']):,.0f} $")
                
                if st.session_state.role in ["RCT", "Staff"]:
                    with st.expander("⚙️ Effectuer une opération financière"):
                        m_val = st.number_input("Montant de la transaction ($)", min_value=1, key=f"m_{idx}")
                        r_val = st.text_input("Motif de l'opération", key=f"r_{idx}")
                        p_val = st.text_input("Numéro de plaque (Si amende)", key=f"p_{idx}")
                        
                        if st.button("Valider la transaction", key=f"btn_op_{idx}"):
                            # Débit
                            df_banque.at[idx, "Solde"] -= m_val
                            
                            action_txt = "Fonds retirés du circuit"
                            if st.session_state.role == "RCT":
                                # Virement vers RCT
                                df_banque.loc[df_banque["Nom Roblox"] == TARGET_RCT, "Solde"] += m_val
                                action_txt = f"Virement vers compte {TARGET_RCT}"
                            
                            conn.update(worksheet="Banque", data=df_banque)
                            
                            # GÉNÉRATION DU REÇU NOIR
                            st.markdown(f"""
                            <div class="ticket-fix">
                                🧾 <b>REÇU DE TRANSACTION OFFICIEL</b><br>
                                Porteur: {row['Nom Roblox']}<br>
                                Montant: {m_val}$<br>
                                Motif: {r_val}<br>
                                Plaque: {p_val}<br>
                                Statut: {action_txt}<br>
                                Date: {datetime.now().strftime('%H:%M:%S')}
                            </div>
                            """, unsafe_allow_html=True)
                            time.sleep(1); st.rerun()

# Pied de page
st.markdown("---")
st.markdown("<center><small>RCRP Management System v14.9 | Technologie GSheets Intégrée</small></center>", unsafe_allow_html=True)
