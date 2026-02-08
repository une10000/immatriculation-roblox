import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURATION (FIX DES TABS) ---
st.set_page_config(page_title="RCRP - Système Intégral", layout="wide")

# --- 2. STYLE CSS (LOGO, TABS ET REÇU LISIBLE) ---
st.markdown("""
    <style>
    /* Pousse le contenu vers le bas pour les onglets */
    .block-container { padding-top: 6rem !important; }
    
    /* Logo : Taille fixe 250px */
    [data-testid="stSidebar"] img { 
        border-radius: 12px; 
        width: 250px !important; 
        margin: 0 auto 20px auto;
        display: block;
    }

    /* FIX REÇU MODE NUIT : Noir pur et texte blanc */
    .ticket-fix { 
        background-color: #000000 !important; 
        color: #ffffff !important; 
        padding: 20px; 
        border: 2px solid #ff4b4b; 
        border-radius: 10px; 
        font-family: 'Courier New', monospace;
    }
    
    /* Badge Assurance */
    .badge-assu {
        background-color: #ff4b4b;
        color: white;
        padding: 3px 12px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONNEXION & DONNÉES ---
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

# Chargement
df_banque = get_data("Banque")
df_im = get_data("Copie de Immatriculations")
df_pts = get_data("Points Permis")

# ==========================================
# 🚪 CONNEXION
# ==========================================
if st.session_state.role is None:
    st.title("🏛️ Portail RCRP")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👤 Accès Citoyen", use_container_width=True):
            st.session_state.role = "Civil"; st.rerun()
    with c2:
        kp = st.text_input("Code Pro", type="password")
        if st.button("🛠️ Pro", use_container_width=True):
            if kp == CODE_PRO: st.session_state.role = "RCT"; st.rerun()
    with c3:
        ks = st.text_input("Code Staff", type="password")
        if st.button("👮 Staff", use_container_width=True):
            if ks == CODE_ADMIN: st.session_state.role = "Staff"; st.rerun()
    st.stop()

# ==========================================
# 🖥️ INTERFACE
# ==========================================
with st.sidebar:
    st.image(LOGO_URL)
    st.markdown(f"**Session :** `{st.session_state.role}`")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()

tabs = st.tabs(["🚗 Immatriculations", "🪪 Points & Dossiers", "💰 Banque"])

# --- ONGLET 1 : IMMATRICULATIONS (ACCÈS TOUS) ---
with tabs[0]:
    st.header("🚗 Registre des Véhicules")
    
    # MAINTENANT ACCESSIBLE À TOUT LE MONDE (MÊME CIVIL)
    with st.expander("➕ Enregistrer un véhicule", expanded=True):
        with st.form("immat_form_v12_4"):
            # Si civil, il ne peut choisir que son nom
            liste_noms = df_banque["Nom Roblox"].tolist()
            u = st.selectbox("Propriétaire", ["---"] + liste_noms)
            
            m = st.text_input("Modèle du véhicule")
            p = st.text_input("Plaque d'immatriculation")
            assu = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            pwd = st.text_input("🔑 Choisissez un Code Secret (pour modifier/supprimer plus tard)", type="password")
            
            # Calculs
            c_ville = 175
            c_assu = 130 if "AVERIS" in assu else 150 if "RCT" in assu else 0
            
            # Promo Trio RCT
            v_rct = len(df_im[(df_im["Nom d'utilisateur ROBLOX"] == u) & (df_im["Assurance"].str.contains("RCT"))])
            if "RCT" in assu and v_rct >= 2:
                c_assu = 0
                st.success("🎁 Prime Trio : 3ème assurance gratuite !")
            
            # Taxe Jeune
            taxe_j = 0
            if u != "---":
                u_row = df_banque[df_banque["Nom Roblox"] == u]
                if not u_row.empty:
                    try:
                        d_arr = datetime.strptime(str(u_row.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                        if (datetime.now() - d_arr).days < 30: taxe_j = 50
                    except: pass
            
            total = c_ville + c_assu + taxe_j
            
            st.markdown(f"""
            <div class="ticket-fix">
                <b>📄 REÇU D'IMMATRICULATION</b><br>
                ----------------------------<br>
                Frais Ville : 175$<br>
                Assurance : {c_assu}$<br>
                Taxe Jeune : {taxe_j}$<br>
                ----------------------------<br>
                <b>TOTAL À PAYER : {total}$</b>
            </div>
            """, unsafe_allow_html=True)

            if st.form_submit_button("✅ Valider et Payer"):
                if u != "---" and p and pwd:
                    idx_u = df_banque[df_banque["Nom Roblox"] == u].index[0]
                    solde = float(df_banque.at[idx_u, "Solde"])
                    
                    if solde >= total:
                        # Débit
                        df_banque.at[idx_u, "Solde"] = solde - total
                        # Virement
                        dest = TARGET_AVERIS if "AVERIS" in assu else TARGET_RCT if "RCT" in assu else None
                        if dest and c_assu > 0:
                            idx_d = df_banque[df_banque["Nom Roblox"] == dest].index[0]
                            df_banque.at[idx_d, "Solde"] = float(df_banque.at[idx_d, "Solde"]) + c_assu
                        
                        # Save Immat
                        new_data = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "Numéro de la plaque": p, "Assurance": assu, "CODE": str(pwd)}])
                        conn.update(worksheet="Banque", data=df_banque)
                        conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_data], ignore_index=True))
                        st.success("Félicitations ! Véhicule immatriculé."); time.sleep(1); st.rerun()
                    else: st.error("Solde insuffisant sur votre compte.")

    # Liste des véhicules (Assurance visible)
    st.divider()
    search = st.text_input("🔍 Rechercher une plaque ou un nom").lower()
    if not df_im.empty:
        res = df_im[df_im.apply(lambda x: search in str(x).lower(), axis=1)]
        for i, r in res.iterrows():
            with st.container(border=True):
                st.markdown(f"<span class='badge-assu'>{r['Assurance']}</span>", unsafe_allow_html=True)
                st.write(f"🚗 **{r['Numéro de la plaque']}** | 👤 {r['Nom d\'utilisateur ROBLOX']} ({r['Marque du véhicule']})")
                
                # Modifier / Supprimer avec le Code Secret
                with st.expander("⚙️ Gérer mon véhicule"):
                    c_test = st.text_input("Code Secret du véhicule", type="password", key=f"c_{i}")
                    if c_test == str(r['CODE']) or st.session_state.role == "Staff":
                        if st.button("🗑️ Supprimer l'immatriculation", key=f"b_{i}"):
                            conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                            st.rerun()

# --- ONGLET 2 : POINTS & DOSSIERS ---
with tabs[1]:
    st.header("🪪 Dossiers Citoyens")
    q = st.text_input("🔍 Tapez votre Nom Roblox pour voir vos points").lower()
    if q:
        res_p = df_pts[df_pts["Nom Roblox"].str.lower().str.contains(q, na=False)]
        if not res_p.empty:
            for _, r in res_p.iterrows():
                st.metric(f"Points de {r['Nom Roblox']}", f"{r['PTS']} / 25")
        else: st.warning("Dossier introuvable.")
    
    if st.session_state.role == "Staff":
        st.divider()
        with st.expander("👤 Créer un Profil (Staff Uniquement)"):
            with st.form("new_p"):
                nr, nd = st.text_input("Pseudo Roblox"), st.text_input("Pseudo Discord")
                if st.form_submit_button("🚀 Créer"):
                    date_c = datetime.now().strftime("%d/%m/%Y")
                    nb = pd.DataFrame([{"Solde": 15000, "Nom Discord": nd, "Nom Roblox": nr, "Date d'arrivée": date_c}])
                    np = pd.DataFrame([{"Nom Roblox": nr, "PTS": 25}])
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, nb], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, np], ignore_index=True))
                    st.success("Profil créé !"); st.rerun()

# --- ONGLET 3 : BANQUE ---
with tabs[2]:
    st.header("💰 Mon Compte")
    if q:
        res_b = df_banque[df_banque["Nom Roblox"].str.lower().str.contains(q, na=False)]
        if not res_b.empty:
            st.metric("Solde actuel", f"{float(res_b.iloc[0]['Solde']):,.0f} $")

st.markdown("---")
st.markdown("<center><small>RCRP Système v12.4 | 2026</small></center>", unsafe_allow_html=True)
