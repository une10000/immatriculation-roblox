# ======================================================================================
# PROJECT       : RCRP FR OS - ULTIMATE INTEGRAL
# VERSION       : 31.0.0 (FULL FEATURES)
# BUILD DATE    : 09/02/2026
# ======================================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# ======================================================================================
# 1. STYLE & DESIGN (BORDURES NOIRES & DARK HEADER)
# ======================================================================================

st.set_page_config(page_title="RCRP FR OS", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stTextInput>div>div>input, .stNumberInput>div>div>input, 
    .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
        border: 2px solid #000000 !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        background-color: #ffffff !important;
    }
    .header-box {
        background-color: #1a1a1a;
        color: #ffffff;
        padding: 25px;
        border-radius: 10px;
        border-left: 10px solid #d32f2f;
        margin-bottom: 20px;
    }
    .receipt-container {
        background-color: #ffffff;
        padding: 25px;
        border: 3px solid #000000;
        font-family: 'Courier New', Courier, monospace;
        color: #000;
        box-shadow: 8px 8px 0px #000;
    }
    .stButton>button {
        border: 2px solid #000 !important;
        font-weight: 900 !important;
        height: 3.5em;
    }
    </style>
""", unsafe_allow_html=True)

# ======================================================================================
# 2. DATA CORE (CONNEXION & CACHE)
# ======================================================================================

cloud_conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def load_all_data():
    df_bank = cloud_conn.read(worksheet="Banque").dropna(how='all').fillna("")
    df_immat = cloud_conn.read(worksheet="Copie de Immatriculations").dropna(how='all').fillna("")
    df_pts = cloud_conn.read(worksheet="Points Permis").dropna(how='all').fillna("")
    return df_bank, df_immat, df_pts

df_b, df_i, df_p = load_all_data()

# Sessions
if "user_auth" not in st.session_state: st.session_state.user_auth = None
if "active_receipt" not in st.session_state: st.session_state.active_receipt = None

# Constantes
ACC_RCT = "une10000"
ACC_AVERIS = "Moune2010"
KEY_RCT = "RCT-26-RCRPFR"
KEY_STAFF = "RCRPFR-25-26"

# ======================================================================================
# 3. SIDEBAR (LOGO, DATE, HEURE)
# ======================================================================================

with st.sidebar:
    st.image("https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=698a61b3&is=69891033&hm=8210184eaca7e5b311b5e00c11ba2e30e86bd67228f54e1f148577592ecfb090&=&format=webp&quality=lossless&width=2732&height=1508", use_container_width=True)
    st.divider()
    
    # Horloge temps réel (statique au refresh)
    st.markdown(f"## 📅 {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown(f"## ⏰ {datetime.now().strftime('%H:%M:%S')}")
    st.divider()
    
    st.write(f"Accréditation : **{st.session_state.user_auth}**")
    if st.button("🔄 RECHARGER LES DONNÉES"): st.cache_data.clear(); st.rerun()
    if st.button("🚪 DÉCONNEXION"): st.session_state.user_auth = None; st.rerun()

# ======================================================================================
# 4. ÉCRAN D'ACCÈS
# ======================================================================================

if st.session_state.user_auth is None:
    st.markdown('<div class="header-box"><h1>🏛️ RCRPFR OS - TERMINAL FÉDÉRAL</h1></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("👥 ACCÈS CIVIL", use_container_width=True): st.session_state.user_auth = "Civil"; st.rerun()
    with c2:
        k_r = st.text_input("Code RCT", type="password")
        if st.button("LOGIN AGENT", use_container_width=True):
            if k_r == KEY_RCT: st.session_state.user_auth = "RCT"; st.rerun()
    with c3:
        k_s = st.text_input("Code Staff", type="password")
        if st.button("LOGIN ADMIN", use_container_width=True):
            if k_s == KEY_STAFF: st.session_state.user_auth = "Staff"; st.rerun()
    st.stop()

# ======================================================================================
# 5. DOSSIER CITOYEN UNIFIÉ (CENTRALE D'INFOS)
# ======================================================================================

st.markdown('<div class="header-box"><h2>📂 DOSSIER CITOYEN</h2></div>', unsafe_allow_html=True)

target = st.selectbox("Sélectionner un profil à consulter :", ["---"] + df_b["Nom Roblox"].tolist())

if target != "---":
    m1, m2, m3 = st.columns(3)
    with m1:
        p_dat = df_p[df_p["Nom Roblox"] == target]
        pts = p_dat.iloc[0]['PTS'] if not p_dat.empty else '?'
        st.metric("POINTS PERMIS", f"{pts}/25")
        status = "VALIDE" if int(pts) > 0 else "SUSPENDU"
        st.write(f"Statut : **{status}**")
    with m2:
        b_dat = df_b[df_b["Nom Roblox"] == target]
        st.metric("SOLDE COMPTE", f"{b_dat.iloc[0]['Solde'] if not b_dat.empty else '0'}$")
        st.caption(f"Arrivée : {b_dat.iloc[0]['Date d\'arrivée'] if not b_dat.empty else 'N/A'}")
    with m3:
        v_dat = df_i[df_i["Nom d'utilisateur ROBLOX"] == target]
        st.write(f"🚗 {len(v_dat)} Véhicule(s) enregistré(s)")
        for _, v in v_dat.iterrows():
            st.caption(f"• {v['Numéro de la plaque']} | {v['Marque du véhicule']}")

st.divider()

# ======================================================================================
# 6. ONGLETS DYNAMIQUES (DROITS D'ACCÈS)
# ======================================================================================

# Filtrage intelligent des onglets
labels = ["🚗 IMMATRICULATION"]
if st.session_state.user_auth in ["RCT", "Staff"]: labels.append("⚙️ SERVICES AGENT")
if st.session_state.user_auth == "Staff": labels.append("🛡️ ADMINISTRATION")

tabs = st.tabs(labels)

# --- ONGLET 1 : IMMATRICULATION (ACCÈS CIVIL +) ---
with tabs[0]:
    f1, f2 = st.columns([1.5, 1])
    
    with f1:
        with st.form("new_v_form"):
            st.subheader("📝 Enregistrement de Véhicule")
            f_o = st.selectbox("Propriétaire", ["---"] + df_b["Nom Roblox"].tolist())
            f_m = st.text_input("Marque et Modèle")
            f_p = st.text_input("Numéro de Plaque (Ex: AB-123-CD)").upper()
            f_a = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
            f_s = st.text_input("Code Secret de Radiation (Gardez-le bien)", type="password")
            
            # Prix & Bonus RCT
            p_tot = 175 + (130 if "AVERIS" in f_a else (150 if "RCT" in f_a else 0))
            if "RCT" in f_a and len(df_i[df_i["Nom d'utilisateur ROBLOX"] == f_o]) >= 2:
                p_tot -= 150 # Trio RCT
                st.info("🎁 Bonus Trio RCT : Assurance offerte !")

            if st.form_submit_button("VALIDER ET PAYER", use_container_width=True):
                # Sécurité anti-doublon plaque
                if f_p in df_i["Numéro de la plaque"].values:
                    st.error("Cette plaque est déjà enregistrée.")
                elif f_o != "---" and f_p and f_s:
                    u_idx = df_b[df_b["Nom Roblox"] == f_o].index[0]
                    solde = float(str(df_b.at[u_idx, "Solde"]).replace('$', ''))
                    
                    if solde >= p_tot:
                        # Transaction
                        df_b.at[u_idx, "Solde"] = solde - p_tot
                        if p_tot > 175: # Si assurance payée
                            dest = ACC_AVERIS if "AVERIS" in f_a else ACC_RCT
                            d_idx = df_b[df_b["Nom Roblox"] == dest].index[0]
                            df_b.at[d_idx, "Solde"] = float(str(df_b.at[d_idx, "Solde"]).replace('$', '')) + (p_tot - 175)
                        
                        # Enregistrement
                        new_veh = pd.DataFrame([{
                            "Horodateur": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Nom d'utilisateur ROBLOX": f_o,
                            "Marque du véhicule": f_m,
                            "Numéro de la plaque": f_p,
                            "Assurance": f_a,
                            "CODE": f_s
                        }])
                        cloud_conn.update(worksheet="Banque", data=df_b)
                        cloud_conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_i, new_veh]))
                        st.session_state.active_receipt = {"nom": f_o, "plq": f_p, "mod": f_m, "prix": p_tot}
                        st.cache_data.clear(); st.rerun()
                    else: st.error("Solde insuffisant.")

    with f2:
        if st.session_state.active_receipt:
            r = st.session_state.active_receipt
            st.markdown(f"""
                <div class="receipt-container">
                    <center><b>📜 TITRE DE CIRCULATION</b></center><hr>
                    <b>TITULAIRE :</b> {r["nom"]}<br>
                    <b>VÉHICULE   :</b> {r["mod"]}<br>
                    <b>PLAQUE    :</b> {r["plq"]}<br>
                    <b>TOTAL PAYÉ:</b> {r["prix"]}$<br>
                    <hr><b>CERTIFIÉ PAR RCRP FR OS</b>
                </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("🗑️ Radiation")
        rp = st.text_input("Plaque", key="rp_del").upper()
        rc = st.text_input("Code Secret", type="password", key="rc_del")
        if st.button("RADIER", use_container_width=True):
            match = df_i[df_i["Numéro de la plaque"].astype(str).str.upper() == rp]
            if not match.empty and (str(rc) == str(match.iloc[0]["CODE"]) or st.session_state.user_auth == "Staff"):
                cloud_conn.update(worksheet="Copie de Immatriculations", data=df_i.drop(match.index[0]))
                st.cache_data.clear(); st.success("Véhicule supprimé."); st.rerun()

# --- ONGLET 2 : SERVICES RCT (AMENDES & POINTS) ---
if st.session_state.user_auth in ["RCT", "Staff"]:
    with tabs[1]:
        st.subheader("👮 Gestion de la Circulation")
        if target != "---":
            st.info(f"Cible : {target}")
            a1, a2 = st.columns(2)
            # Amende
            amt = a1.number_input("Montant Amende", min_value=0)
            if a1.button("PRÉLEVER L'AMENDE", use_container_width=True):
                idx_b = df_b[df_b["Nom Roblox"] == target].index[0]
                df_b.at[idx_b, "Solde"] = float(str(df_b.at[idx_b, "Solde"]).replace('$', '')) - amt
                # Gain RCT
                rct_idx = df_b[df_b["Nom Roblox"] == ACC_RCT].index[0]
                df_b.at[rct_idx, "Solde"] = float(str(df_b.at[rct_idx, "Solde"]).replace('$', '')) + amt
                cloud_conn.update(worksheet="Banque", data=df_b)
                st.cache_data.clear(); st.success("Amende transférée."); st.rerun()
            # Points
            pts_r = a2.number_input("Points à retirer", min_value=0, max_value=25)
            if a2.button("RETIRER POINTS", use_container_width=True):
                idx_p = df_p[df_p["Nom Roblox"] == target].index[0]
                df_p.at[idx_p, "PTS"] = max(0, int(df_p.at[idx_p, "PTS"]) - pts_r)
                cloud_conn.update(worksheet="Points Permis", data=df_p)
                st.cache_data.clear(); st.success("Points mis à jour."); st.rerun()

# --- ONGLET 3 : ADMINISTRATION (STAFF ONLY) ---
if st.session_state.user_auth == "Staff":
    with tabs[2]:
        s1, s2 = st.columns(2)
        with s1:
            with st.form("new_citizen_full"):
                st.subheader("🔨 Inscription Fédérale")
                st.caption("Pack 15,000$ + 25 Points Automatique")
                nr = st.text_input("Nom Roblox")
                nd = st.text_input("Discord")
                nj = st.selectbox("Fonction", ["Civil", "RCT", "Gouverneur", "Justice"])
                if st.form_submit_button("CRÉER LE DOSSIER"):
                    if nr in df_b["Nom Roblox"].values:
                        st.error("Ce citoyen existe déjà.")
                    else:
                        d_auto = datetime.now().strftime("%d/%m/%Y")
                        new_b = pd.DataFrame([{"Solde": 15000, "Nom Discord": nd, "Nom Roblox": nr, "Date d'arrivée": d_auto, "Emploiement": nj}])
                        new_p = pd.DataFrame([{"Nom Discord": nd, "Nom Roblox": nr, "PTS": 25, "Validité": "OUI"}])
                        cloud_conn.update(worksheet="Banque", data=pd.concat([df_b, new_b]))
                        cloud_conn.update(worksheet="Points Permis", data=pd.concat([df_p, new_p]))
                        st.cache_data.clear(); st.success("Bienvenue à Rensselaer !"); st.rerun()
        with s2:
            st.subheader("⚙️ Maintenance")
            if st.button("RAZ DU CACHE SYSTÈME"):
                st.cache_data.clear(); st.rerun()
            # Possibilité de voir la DB brute pour le Staff
            if st.checkbox("Voir la base brute (Banque)"):
                st.dataframe(df_b)
