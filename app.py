import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# ======================================================================================
# 1. CONFIGURATION DE L'INTERFACE ET DE LA PAGE
# ======================================================================================
st.set_page_config(
    page_title="RCRP - Système de Gestion Intégral Professionnel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================================================
# 2. DESIGN ET STYLE CSS PERSONNALISÉ
# ======================================================================================
st.markdown("""
    <style>
    /* Ajustement de la zone de contenu principale */
    .main .block-container {
        padding-top: 5rem !important;
        padding-bottom: 5rem !important;
    }

    /* Style du Logo dans la barre latérale */
    [data-testid="stSidebar"] img {
        border-radius: 20px;
        width: 100% !important;
        margin-bottom: 20px;
        border: 2px solid #333;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }

    /* Style des Badges d'Assurance */
    .badge-assu {
        background-color: #ff4b4b;
        color: white;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
    }

    /* Style du Reçu Noir (Ticket de caisse) */
    .ticket-fix {
        background-color: #000000 !important;
        color: #00FF00 !important;
        padding: 30px;
        border: 2px dashed #ff4b4b;
        border-radius: 15px;
        font-family: 'Courier New', Courier, monospace;
        line-height: 1.6;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Boutons personnalisés */
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s;
        font-weight: bold;
    }
    
    /* Input style */
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# ======================================================================================
# 3. INITIALISATION DES SYSTÈMES ET VARIABLES DE SESSION
# ======================================================================================

if "role" not in st.session_state:
    st.session_state.role = None

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de connexion au serveur de données : {e}")

# Configuration des comptes (Averis -> Moune2010)
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"

CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"

LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

# ======================================================================================
# 4. FONCTIONS DE CHARGEMENT DES DONNÉES
# ======================================================================================

def fetch_bank_data():
    data = conn.read(worksheet="Banque", ttl=0)
    df = data.dropna(how='all').fillna("")
    return df

def fetch_immat_data():
    data = conn.read(worksheet="Copie de Immatriculations", ttl=0)
    df = data.dropna(how='all').fillna("")
    return df

def fetch_points_data():
    data = conn.read(worksheet="Points Permis", ttl=0)
    df = data.dropna(how='all').fillna("")
    return df

df_banque = fetch_bank_data()
df_im = fetch_immat_data()
df_pts = fetch_points_data()

# ======================================================================================
# 5. PORTAIL D'ACCÈS (AUTHENTIFICATION)
# ======================================================================================

if st.session_state.role is None:
    st.title("🏛️ Système de Gestion Centralisé - RCRP")
    st.subheader("Bienvenue sur l'interface officielle du Gouvernement et de la RCT.")
    st.write("---")
    
    col_access_1, col_access_2, col_access_3 = st.columns(3)
    
    with col_access_1:
        with st.container(border=True):
            st.header("👤 Civil")
            st.write("Accès citoyen standard.")
            if st.button("Accéder au Portail Public", use_container_width=True):
                st.session_state.role = "Civil"
                st.rerun()
                
    with col_access_2:
        with st.container(border=True):
            st.header("🛠️ Agent RCT")
            st.write("Espace réservé aux agents en service.")
            input_code_rct = st.text_input("Code d'accès Agent", type="password", key="auth_rct")
            if st.button("Connexion Agent RCT", use_container_width=True):
                if input_code_rct == CODE_PRO:
                    st.session_state.role = "RCT"
                    st.rerun()
                else:
                    st.error("Code RCT non valide.")
                    
    with col_access_3:
        with st.container(border=True):
            st.header("👮 Gouvernement")
            st.write("Haute sécurité (Staff).")
            input_code_staff = st.text_input("Code Administrateur", type="password", key="auth_staff")
            if st.button("Connexion Administrateur", use_container_width=True):
                if input_code_staff == CODE_ADMIN:
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    st.error("Code Staff non valide.")
    st.stop()

# ======================================================================================
# 6. BARRE LATÉRALE
# ======================================================================================

with st.sidebar:
    st.image(LOGO_URL)
    st.markdown("---")
    now = datetime.now()
    st.write(f"📅 **Date du jour :**")
    st.info(now.strftime('%d / %m / %Y'))
    st.write(f"⏰ **Heure du serveur :**")
    st.info(now.strftime('%H : %M : %S'))
    
    if st.button("🔄 Actualiser les données", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    st.write("👤 **Utilisateur :**")
    st.success(f"Mode {st.session_state.role} actif")
    
    if st.button("🚪 Déconnexion du système", use_container_width=True):
        st.session_state.role = None
        st.rerun()
    
    st.divider()
    st.caption("RCRP Management System v16.7 | 2026")

# ======================================================================================
# 7. INTERFACE PRINCIPALE - GESTION DES ONGLETS
# ======================================================================================

tab_reg, tab_dos, tab_ban = st.tabs([
    "🚗 REGISTRE VÉHICULES", 
    "🪪 DOSSIERS CITOYENS", 
    "💰 BANQUE CENTRALE"
])

# --------------------------------------------------------------------------------------
# ONGLET 1 : REGISTRE DES VÉHICULES
# --------------------------------------------------------------------------------------

with tab_reg:
    st.header("🚗 Registre National des Immatriculations")
    
    if st.session_state.role not in ["RCT", "Staff"]:
        with st.expander("➕ Enregistrer un nouveau véhicule", expanded=True):
            c_left, c_right = st.columns(2)
            with c_left:
                sel_proprio = st.selectbox("Titulaire (Nom Roblox)", ["---"] + df_banque["Nom Roblox"].tolist())
                in_marque = st.text_input("Marque et Modèle", placeholder="Ex: Mercedes-Benz AMG")
                in_plaque = st.text_input("Numéro de Plaque", placeholder="Ex: RC-123-RP")
            
            with c_right:
                sel_assu = st.selectbox("Formule d'Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
                in_code = st.text_input("Code Secret", type="password")

            frais_base = 175
            frais_assurance = 0
            taxe_jeune = 0
            
            if "AVERIS" in sel_assu: frais_assurance = 130
            elif "RCT" in sel_assu: frais_assurance = 150
            
            veh_rct_check = df_im[(df_im["Nom d'utilisateur ROBLOX"] == sel_proprio) & (df_im["Assurance"].str.contains("RCT"))]
            if "RCT" in sel_assu and len(veh_rct_check) >= 2:
                frais_assurance = 0
                st.info("💡 **PROMOTION :** Offre Trio RCT appliquée !")

            if sel_proprio != "---":
                user_record = df_banque[df_banque["Nom Roblox"] == sel_proprio]
                try:
                    date_arr_dt = datetime.strptime(str(user_record.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                    if (datetime.now() - date_arr_dt).days < 30:
                        taxe_jeune = 50
                        st.warning("⚠️ **TAXE :** Nouveau citoyen détecté (+50$)")
                except: pass

            total_facture = frais_base + frais_assurance + taxe_jeune
            
            st.markdown(f"""<div class="ticket-fix">🧾 <b>PRÉ-VISUALISATION FACTURE</b><br>--------------------<br>Titulaire : {sel_proprio}<br>Plaque : {in_plaque}<br>--------------------<br>Base : 175$<br>Assurance : {frais_assurance}$<br>Taxe Jeune : {taxe_jeune}$<br>--------------------<br><b>TOTAL : {total_facture}$</b></div>""", unsafe_allow_html=True)
            
            if st.button("💳 Procéder au Paiement", use_container_width=True):
                if sel_proprio == "---" or not in_plaque or not in_code:
                    st.error("Veuillez remplir tous les champs.")
                else:
                    idx_b = df_banque[df_banque["Nom Roblox"] == sel_proprio].index[0]
                    try:
                        val_brute = str(df_banque.at[idx_b, "Solde"]).replace('$', '').replace(' ', '').replace(',', '')
                        solde_actuel = float(val_brute) if val_brute != "" else 0.0
                    except:
                        st.error("Erreur format solde.")
                        st.stop()
                    
                    if solde_actuel >= total_facture:
                        df_banque.at[idx_b, "Solde"] = solde_actuel - total_facture
                        if frais_assurance > 0:
                            target_compte = TARGET_AVERIS if "AVERIS" in sel_assu else TARGET_RCT
                            idx_target = df_banque[df_banque["Nom Roblox"] == target_compte].index[0]
                            val_cible = str(df_banque.at[idx_target, "Solde"]).replace('$', '').replace(' ', '').replace(',', '')
                            df_banque.at[idx_target, "Solde"] = (float(val_cible) if val_cible != "" else 0.0) + frais_assurance
                        
                        new_vehicule_entry = pd.DataFrame([{
                            "Horodateur": now.strftime("%d/%m/%Y"),
                            "Nom d'utilisateur ROBLOX": sel_proprio,
                            "Marque du véhicule": in_marque,
                            "Numéro de la plaque": in_plaque,
                            "Assurance": sel_assu,
                            "CODE": str(in_code)
                        }])
                        
                        conn.update(worksheet="Banque", data=df_banque)
                        conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_vehicule_entry], ignore_index=True))
                        st.success("Enregistrement réussi !")
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("Solde insuffisant.")

    st.divider()
    st.subheader("🔍 Consultation du Registre Public")
    search_query = st.text_input("Rechercher par Plaque ou Nom", key="search_reg_main").lower()

    for i, row in df_im.iterrows():
        nom_db = str(row['Nom d\'utilisateur ROBLOX']).lower()
        plaque_db = str(row['Numéro de la plaque']).lower()
        
        if not search_query or search_query in nom_db or search_query in plaque_db:
            with st.container(border=True):
                col_i1, col_i2, col_i3 = st.columns([2, 2, 1])
                with col_i1:
                    st.write(f"🆔 **PLAQUE : {row['Numéro de la plaque']}**")
                    st.write(f"🚗 {row['Marque du véhicule']}")
                with col_i2:
                    st.write(f"👤 Propriétaire : **{row['Nom d\'utilisateur ROBLOX']}**")
                    st.write(f"📅 Le : {row['Horodateur']}")
                with col_i3:
                    st.markdown(f"<span class='badge-assu'>{row['Assurance']}</span>", unsafe_allow_html=True)
                
                with st.expander("⚙️ Radiation"):
                    check_code_sec = st.text_input("Code Secret", type="password", key=f"del_key_{i}")
                    if st.button("🚫 Confirmer la Radiation", key=f"del_btn_{i}", use_container_width=True):
                        if check_code_sec == str(row['CODE']) or st.session_state.role == "Staff":
                            conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                            st.success("Véhicule radié.")
                            time.sleep(1)
                            st.rerun()

# --------------------------------------------------------------------------------------
# ONGLET 2 : DOSSIERS CITOYENS
# --------------------------------------------------------------------------------------

with tab_dos:
    st.header("🪪 Dossiers Administratifs")
    
    if st.session_state.role == "Staff":
        with st.container(border=True):
            st.subheader("🏦 Console de Paye")
            if st.button("🧧 EXECUTER LA PAYE TOTALE", use_container_width=True):
                with st.status("Traitement..."):
                    for idx, citoyen in df_banque.iterrows():
                        poste = str(citoyen["Emploiement"]).upper()
                        salaire = 17000 if "RCT" in poste else 15000
                        v_s = str(citoyen["Solde"]).replace('$', '').replace(' ', '').replace(',', '')
                        df_banque.at[idx, "Solde"] = (float(v_s) if v_s != "" else 0.0) + salaire
                    
                    compteur_rct_paye = {}
                    for _, veh in df_im.iterrows():
                        proprio = veh["Nom d'utilisateur ROBLOX"]
                        if proprio in df_banque["Nom Roblox"].values:
                            idx_b = df_banque[df_banque["Nom Roblox"] == proprio].index[0]
                            if "RCT" in veh["Assurance"]:
                                compteur_rct_paye[proprio] = compteur_rct_paye.get(proprio, 0) + 1
                                if compteur_rct_paye[proprio] <= 2:
                                    df_banque.at[idx_b, "Solde"] -= 150
                                    df_banque.loc[df_banque["Nom Roblox"] == TARGET_RCT, "Solde"] += 150
                            elif "AVERIS" in veh["Assurance"]:
                                df_banque.at[idx_b, "Solde"] -= 130
                                df_banque.loc[df_banque["Nom Roblox"] == TARGET_AVERIS, "Solde"] += 130
                    
                    conn.update(worksheet="Banque", data=df_banque)
                    st.success("Paye effectuée !")
                    st.rerun()

    st.divider()
    search_dos = st.text_input("Rechercher un citoyen (Roblox/Discord)", key="s_dos").lower()
    if search_dos:
        mask = (df_banque["Nom Roblox"].str.lower().str.contains(search_dos, na=False)) | (df_banque["Nom Discord"].str.lower().str.contains(search_dos, na=False))
        for idx, r in df_banque[mask].iterrows():
            with st.container(border=True):
                st.subheader(f"Citoyen : {r['Nom Roblox']}")
                c1, c2 = st.columns(2)
                with c1: st.write(f"🆔 Discord : {r['Nom Discord']}\n📌 Emploi : {r['Emploiement']}")
                with c2: st.write(f"📅 Arrivée : {r['Date d\'arrivée']}")

    if st.session_state.role == "Staff":
        with st.expander("👤 Ajouter un Nouveau Citoyen"):
            with st.form("form_new_c"):
                f_nom = st.text_input("Nom Roblox")
                f_disc = st.text_input("Discord")
                f_empl = st.selectbox("Emploi", ["Civil", "Agent RCT", "Staff"])
                if st.form_submit_button("Créer Profil"):
                    date_now = datetime.now().strftime("%d/%m/%Y")
                    new_line = pd.DataFrame([{"Solde": 15000, "Nom Discord": f_disc, "Nom Roblox": f_nom, "Date d'arrivée": date_now, "Emploiement": f_empl}])
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, new_line], ignore_index=True))
                    st.success(f"Profil créé le {date_now}")
                    st.rerun()

# --------------------------------------------------------------------------------------
# ONGLET 3 : BANQUE CENTRALE
# --------------------------------------------------------------------------------------

with tab_ban:
    st.header("💰 Gestion Bancaire")
    search_b = st.text_input("🔍 Rechercher un compte", key="sb_main").lower()
    if search_b:
        mask_b = df_banque["Nom Roblox"].str.lower().str.contains(search_b, na=False)
        for idx, rb in df_banque[mask_b].iterrows():
            with st.container(border=True):
                st.subheader(f"Compte : {rb['Nom Roblox']}")
                v_solde = str(rb['Solde']).replace('$', '').replace(' ', '').replace(',', '')
                st.metric("Solde Actuel", f"{float(v_solde):,.0f} $")
                
                if st.session_state.role in ["RCT", "Staff"]:
                    with st.expander("⚙️ Opération de Débit"):
                        m_deb = st.number_input("Montant", min_value=1, key=f"deb_{idx}")
                        if st.button("Confirmer le débit", key=f"btn_deb_{idx}"):
                            curr_s = float(v_solde)
                            df_banque.at[idx, "Solde"] = curr_s - m_deb
                            if st.session_state.role == "RCT":
                                idx_rct = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                df_banque.at[idx_rct, "Solde"] = float(str(df_banque.at[idx_rct, "Solde"]).replace('$', '').replace(' ', '').replace(',', '')) + m_deb
                            conn.update(worksheet="Banque", data=df_banque)
                            st.success("Opération réussie.")
                            st.rerun()

st.markdown("---")
st.markdown("<center><small>RCRP System 2026 | Propriété de Moune2010 & une10000</small></center>", unsafe_allow_html=True)
