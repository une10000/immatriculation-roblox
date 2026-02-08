import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Système Intégral", layout="wide")

# --- 2. STYLE CSS COMPLET ---
st.markdown("""
    <style>
    .block-container { padding-top: 6rem !important; }
    [data-testid="stSidebar"] img { 
        border-radius: 12px; 
        width: 250px !important; 
        margin: 0 auto 20px auto;
        display: block;
    }
    .badge-assu {
        background-color: #ff4b4b;
        color: white;
        padding: 3px 12px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.85rem;
    }
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

# --- 3. CONNEXION ---
if "role" not in st.session_state:
    st.session_state.role = None

conn = st.connection("gsheets", type=GSheetsConnection)
TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?format=webp&quality=lossless&width=2732&height=1508"

def get_data(sheet_name):
    st.cache_data.clear()
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        return df.dropna(how='all').fillna("")
    except:
        return pd.DataFrame()

df_banque = get_data("Banque")
df_im = get_data("Copie de Immatriculations")
df_pts = get_data("Points Permis")

# ==========================================
# 🚪 PORTAIL
# ==========================================
if st.session_state.role is None:
    st.title("🏛️ Portail RCRP")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👤 Accès Public", use_container_width=True):
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
    st.image(LOGO_URL, use_container_width=True)
    st.markdown(f"🎭 **Session :** `{st.session_state.role}`")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()
    st.divider()
    st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

tabs = st.tabs(["🚗 Immatriculations", "🪪 Dossiers & Points", "💰 Banque"])

# --- ONGLET 1 : IMMATRICULATIONS ---
with tabs[0]:
    st.header("🚗 Registre des Véhicules")
    
    with st.expander("➕ Enregistrer un véhicule", expanded=True):
        # On place les widgets HORS du formulaire pour le calcul en direct
        u_sel = st.selectbox("Propriétaire", ["---"] + df_banque["Nom Roblox"].tolist())
        m_v = st.text_input("Marque / Modèle")
        p_v = st.text_input("Plaque")
        as_sel = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
        pw_v = st.text_input("🔑 Code Secret", type="password")
        
        # --- CALCUL LIVE ---
        c_v = 175
        c_a = 0
        if "AVERIS" in as_sel: c_a = 130
        elif "RCT" in as_sel: c_a = 150
        
        # Promo Trio
        r_count = len(df_im[(df_im["Nom d'utilisateur ROBLOX"] == u_sel) & (df_im["Assurance"].str.contains("RCT"))])
        if "RCT" in as_sel and r_count >= 2:
            c_a = 0
            st.info("🎁 Prime Trio : 3ème assurance gratuite !")

        # Taxe Jeune
        t_j = 0
        if u_sel != "---":
            u_info = df_banque[df_banque["Nom Roblox"] == u_sel]
            if not u_info.empty:
                try:
                    d_a = datetime.strptime(str(u_info.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                    if (datetime.now() - d_a).days < 30: t_j = 50
                except: pass
        
        tot = c_v + c_a + t_j
        
        st.markdown(f"""
        <div class="ticket-fix">
            <b>📄 FACTURE EN DIRECT</b><br>
            ----------------------------<br>
            Ville : 175$<br>
            Assurance : {c_a}$<br>
            Taxe Jeune : {t_j}$<br>
            ----------------------------<br>
            <b>TOTAL À PAYER : {tot}$</b>
        </div>
        """, unsafe_allow_html=True)

        if st.button("✅ Valider et Payer l'enregistrement"):
            if u_sel != "---" and p_v and pw_v:
                idx = df_banque[df_banque["Nom Roblox"] == u_sel].index[0]
                if float(df_banque.at[idx, "Solde"]) >= tot:
                    # Débit
                    df_banque.at[idx, "Solde"] = float(df_banque.at[idx, "Solde"]) - tot
                    
                    # Virement aux pros
                    dest = None
                    if "AVERIS" in as_sel: dest = TARGET_AVERIS
                    elif "RCT" in as_sel: dest = TARGET_RCT
                    
                    if dest and c_a > 0:
                        idx_d = df_banque[df_banque["Nom Roblox"] == dest].index[0]
                        df_banque.at[idx_d, "Solde"] = float(df_banque.at[idx_d, "Solde"]) + c_a
                    
                    # Save
                    new_i = pd.DataFrame([{
                        "Horodateur": datetime.now().strftime("%d/%m/%Y"),
                        "Nom d'utilisateur ROBLOX": u_sel,
                        "Marque du véhicule": m_v,
                        "Numéro de la plaque": p_v,
                        "Assurance": as_sel,
                        "CODE": str(pw_v)
                    }])
                    conn.update(worksheet="Banque", data=df_banque)
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_i], ignore_index=True))
                    st.success("Enregistrement réussi !"); time.sleep(1); st.rerun()
                else: st.error("Solde insuffisant.")
            else: st.warning("Champs incomplets.")

    # Liste
    st.divider()
    search = st.text_input("🔍 Recherche Plaque ou Nom").lower()
    if not df_im.empty:
        res = df_im[df_im.apply(lambda x: search in str(x).lower(), axis=1)]
        for i, r in res.iterrows():
            with st.container(border=True):
                st.markdown(f"<span class='badge-assu'>{r['Assurance']}</span>", unsafe_allow_html=True)
                st.write(f"🚗 **{r['Numéro de la plaque']}** | 👤 {r['Nom d\'utilisateur ROBLOX']} ({r['Marque du véhicule']})")
                with st.expander("⚙️ Gérer"):
                    if st.text_input("Code Secret", type="password", key=f"c_{i}") == str(r['CODE']) or st.session_state.role == "Staff":
                        if st.button("🗑️ Supprimer", key=f"b_{i}"):
                            conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                            st.rerun()

# --- ONGLET 2 : POINTS ---
with tabs[1]:
    st.header("🪪 Dossiers Citoyens")
    q = st.text_input("🔍 Rechercher un Nom").lower()
    if q:
        res_p = df_pts[df_pts["Nom Roblox"].str.lower().str.contains(q, na=False)]
        if not res_p.empty:
            for _, r in res_p.iterrows():
                st.metric(f"Points de {r['Nom Roblox']}", f"{r['PTS']} / 25")
    
    if st.session_state.role == "Staff":
        st.divider()
        with st.expander("👤 Nouveau Profil"):
            with st.form("new_p"):
                nr, nd = st.text_input("Roblox"), st.text_input("Discord")
                if st.form_submit_button("🚀 Créer"):
                    dc = datetime.now().strftime("%d/%m/%Y")
                    nb = pd.DataFrame([{"Solde": 15000, "Nom Discord": nd, "Nom Roblox": nr, "Date d'arrivée": dc}])
                    np = pd.DataFrame([{"Nom Roblox": nr, "PTS": 25}])
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, nb], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, np], ignore_index=True))
                    st.success("Profil créé !"); st.rerun()

# --- ONGLET 3 : BANQUE ---
with tabs[2]:
    st.header("💰 État de la Banque")
    if q:
        res_b = df_banque[df_banque["Nom Roblox"].str.lower().str.contains(q, na=False)]
        res_p2 = df_pts[df_pts["Nom Roblox"].str.lower().str.contains(q, na=False)]
        if not res_b.empty:
            c1, c2 = st.columns(2)
            c1.metric(f"Solde de {res_b.iloc[0]['Nom Roblox']}", f"{float(res_b.iloc[0]['Solde']):,.0f} $")
            if not res_p2.empty: c2.metric("Points Permis", f"{res_p2.iloc[0]['PTS']} / 25")
            st.write(f"📅 Arrivée : {res_bq.iloc[0]['Date d\'arrivée']}")

st.markdown("---")
st.markdown("<center><small>RCRP Système v13.0 | 2026</small></center>", unsafe_allow_html=True)
