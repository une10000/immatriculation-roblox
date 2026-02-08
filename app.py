import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Système Intégral", layout="wide")

# --- 2. STYLE CSS (LOGO PLUS GRAND, TABS DESCENDUS, REÇU LISIBLE) ---
st.markdown("""
    <style>
    /* Décale le contenu pour ne plus couper les onglets */
    .stApp { margin-top: 6rem !important; }
    
    /* Logo plus grand et centré dans la sidebar */
    [data-testid="stSidebar"] img { 
        border-radius: 10px; 
        width: 250px !important; 
        margin-left: auto;
        margin-right: auto;
        display: block;
    }

    /* Badge Assurance bien visible */
    .assu-tag {
        background-color: #ff4b4b;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* Reçu Lisible Mode Nuit */
    .ticket-nuit { 
        background-color: #000000 !important; 
        color: #ffffff !important; 
        padding: 20px; 
        border: 2px solid #ff4b4b; 
        border-radius: 10px;
        font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONNEXION ---
if "role" not in st.session_state:
    st.session_state.role = None

conn = st.connection("gsheets", type=GSheetsConnection)
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

def get_data(sheet_name):
    st.cache_data.clear()
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        return df.dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

# Chargement des bases
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
        if st.button("👤 Accès Citoyen", use_container_width=True):
            st.session_state.role = "Civil"; st.rerun()
    with col2:
        kp = st.text_input("Code Pro", type="password")
        if st.button("🛠️ Connexion Pro", use_container_width=True):
            if kp == CODE_PRO: st.session_state.role = "RCT"; st.rerun()
    with col3:
        ks = st.text_input("Code Staff", type="password")
        if st.button("👮 Connexion Staff", use_container_width=True):
            if ks == CODE_ADMIN: st.session_state.role = "Staff"; st.rerun()
    st.stop()

# ==========================================
# 🖥️ INTERFACE PRINCIPALE
# ==========================================
with st.sidebar:
    st.image(LOGO_URL)
    st.markdown(f"**Session :** `{st.session_state.role}`")
    if st.button("🚪 Déconnexion"):
        st.session_state.role = None; st.rerun()

# Navigation
tabs = st.tabs(["🚗 Immat", "🪪 Points & Dossiers", "💰 Banque"])

# --- ONGLET 1 : IMMATRICULATIONS (RE-FIXÉ) ---
with tabs[0]:
    st.header("🚗 Registre Immatriculation")
    
    if st.session_state.role != "Civil":
        with st.expander("➕ Enregistrer un véhicule"):
            with st.form("form_v12"):
                user = st.selectbox("Citoyen", ["---"] + df_banque["Nom Roblox"].tolist())
                marque = st.text_input("Modèle")
                plaque = st.text_input("Plaque")
                assu_choix = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
                code_car = st.text_input("🔑 Code Secret", type="password")
                
                # Calculs prix
                p_ville = 175
                p_assu = 130 if "AVERIS" in assu_choix else 150 if "RCT" in assu_choix else 0
                
                # Bonus Trio RCT
                v_deja_rct = len(df_im[(df_im["Nom d'utilisateur ROBLOX"] == user) & (df_im["Assurance"].str.contains("RCT"))])
                if "RCT" in assu_choix and v_deja_rct >= 2:
                    p_assu = 0
                    st.success("🎁 Prime TRIO : 3ème véhicule gratuit !")

                # Taxe Jeune
                taxe_j = 0
                if user != "---":
                    u_info = df_banque[df_banque["Nom Roblox"] == user]
                    if not u_info.empty:
                        try:
                            d_arr = datetime.strptime(str(u_info.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                            if (datetime.now() - d_arr).days < 30: taxe_j = 50
                        except: pass
                
                total = p_ville + p_assu + taxe_j
                
                st.markdown(f"""<div class="ticket-nuit">
                <b>FACTURE RCRP</b><br>---<br>
                Immat : 175$<br>Assurance : {p_assu}$<br>Taxe Jeune : {taxe_j}$<br>
                ---<br><b>TOTAL : {total}$</b>
                </div>""", unsafe_allow_html=True)

                if st.form_submit_button("✅ Enregistrer"):
                    if user != "---" and plaque and code_car:
                        idx_u = df_banque[df_banque["Nom Roblox"] == user].index[0]
                        solde = float(df_banque.at[idx_u, "Solde"])
                        if solde >= total:
                            # Débit
                            df_banque.at[idx_u, "Solde"] = solde - total
                            # Virement
                            vire_a = TARGET_AVERIS if "AVERIS" in assu_choix else TARGET_RCT if "RCT" in assu_choix else None
                            if vire_a and p_assu > 0:
                                idx_t = df_banque[df_banque["Nom Roblox"] == vire_a].index[0]
                                df_banque.at[idx_t, "Solde"] = float(df_banque.at[idx_t, "Solde"]) + p_assu
                            
                            # Save
                            new_row = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y"), "Nom d'utilisateur ROBLOX": user, "Marque du véhicule": marque, "Numéro de la plaque": plaque, "Assurance": assu_choix, "CODE": str(code_car)}])
                            conn.update(worksheet="Banque", data=df_banque)
                            conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_row], ignore_index=True))
                            st.success("Immatriculation validée !"); time.sleep(1); st.rerun()
                        else: st.error("Le citoyen n'a pas assez d'argent.")

    # Liste des immatriculations avec Assurance visible
    st.divider()
    search = st.text_input("🔍 Recherche Plaque ou Nom").lower()
    res = df_im[df_im.apply(lambda x: search in str(x).lower(), axis=1)]
    for i, r in res.iterrows():
        with st.container(border=True):
            st.markdown(f"<span class='assu-tag'>{r['Assurance']}</span>", unsafe_allow_html=True)
            st.write(f"🚗 **{r['Numéro de la plaque']}** | 👤 {r['Nom d\'utilisateur ROBLOX']} ({r['Marque du véhicule']})")
            if st.session_state.role == "Staff" or st.session_state.role == "RCT":
                if st.button("🗑️ Supprimer", key=f"del_{i}"):
                    conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                    st.rerun()

# --- ONGLET 2 : POINTS (VISIBLE POUR TOUS) ---
with tabs[1]:
    st.header("🪪 Dossiers & Points Permis")
    
    # Barre de recherche pour les points
    q_pts = st.text_input("🔍 Entrez votre Nom Roblox pour voir vos points").lower()
    if q_pts:
        res_p = df_pts[df_pts["Nom Roblox"].str.lower().contains(q_pts)]
        if not res_p.empty:
            for i, r in res_p.iterrows():
                st.metric(f"Points de {r['Nom Roblox']}", f"{r['PTS']} / 25")
        else:
            st.warning("Aucun dossier trouvé à ce nom.")

    if st.session_state.role == "Staff":
        st.divider()
        st.subheader("🛠️ Administration des Dossiers")
        with st.expander("👤 Créer un nouveau profil Citoyen"):
            with st.form("new_cit"):
                n_r = st.text_input("Pseudo Roblox")
                n_d = st.text_input("Pseudo Discord")
                if st.form_submit_button("🚀 Créer Profil"):
                    date_c = datetime.now().strftime("%d/%m/%Y")
                    # Ajout Banque
                    row_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": n_d, "Nom Roblox": n_r, "Date d'arrivée": date_c}])
                    # Ajout Points
                    row_p = pd.DataFrame([{"Nom Roblox": n_r, "PTS": 25}])
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, row_b], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, row_p], ignore_index=True))
                    st.success("Profil créé !"); st.rerun()

# --- ONGLET 3 : BANQUE ---
with tabs[2]:
    st.header("💰 État des Comptes")
    # Affichage simplifié du solde
    if q_pts: # Réutilise la recherche du dessus
        res_b = df_banque[df_banque["Nom Roblox"].str.lower().contains(q_pts)]
        if not res_b.empty:
            st.metric("Solde Bancaire", f"{float(res_b.iloc[0]['Solde']):,.0f} $")

st.markdown("---")
st.markdown("<center><small>RCRP Système v12.2 | 2026</small></center>", unsafe_allow_html=True)
