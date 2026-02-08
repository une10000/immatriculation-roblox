import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# ==========================================
# 1. CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(
    page_title="RCRP - Système Intégral Professionnel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. STYLE CSS DÉTAILLÉ (RÉTABLI À 100%)
# ==========================================
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
    
    .stAlert {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VARIABLES ET CONSTANTES (PRÉSERVÉES)
# ==========================================
if "role" not in st.session_state:
    st.session_state.role = None

conn = st.connection("gsheets", type=GSheetsConnection)

TARGET_RCT = "une10000"
TARGET_AVERIS = "Moune2010"
CODE_ADMIN = "RCRPFR-25-26" 
CODE_PRO = "RCT-26-RCRPFR"
LOGO_URL = "https://media.discordapp.net/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png?ex=6989b8f3&is=69886773&hm=29c056c7c305026ba05077deb91af1f7a838c8e409cbbaba0d94b41076cefa62&=&format=webp&quality=lossless&width=2732&height=1508"

# ==========================================
# 4. FONCTIONS DE GESTION (PRÉSERVÉES)
# ==========================================
def get_data(sheet_name):
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        df_clean = data.dropna(how='all')
        df_final = df_clean.fillna("")
        return df_final
    except Exception as e:
        st.error(f"Erreur technique : {e}")
        return pd.DataFrame()

df_banque = get_data("Banque")
df_im = get_data("Copie de Immatriculations")
df_pts = get_data("Points Permis")

# ==========================================
# 5. PORTAIL DE CONNEXION (COMPLET)
# ==========================================
if st.session_state.role is None:
    st.title("🏛️ Système de Gestion RCRP - Portail d'Accès")
    col_civ, col_pro, col_staff = st.columns(3)
    
    with col_civ:
        with st.container(border=True):
            st.subheader("👤 Secteur Civil")
            if st.button("Accéder au Portail Public", use_container_width=True):
                st.session_state.role = "Civil"; st.rerun()
                
    with col_pro:
        with st.container(border=True):
            st.subheader("🛠️ Secteur Professionnel")
            input_pro = st.text_input("Code Employé", type="password", key="login_p")
            if st.button("Authentification Pro", use_container_width=True):
                if input_pro == CODE_PRO:
                    st.session_state.role = "RCT"; st.rerun()
                else: st.error("Code RCT invalide.")
                    
    with col_staff:
        with st.container(border=True):
            st.subheader("👮 Gouvernement")
            input_staff = st.text_input("Code Gouvernement", type="password", key="login_s")
            if st.button("Authentification Staff", use_container_width=True):
                if input_staff == CODE_ADMIN:
                    st.session_state.role = "Staff"; st.rerun()
                else: st.error("Code Administration invalide.")
    st.stop()

# ==========================================
# 6. SIDEBAR (COMPLÈTE)
# ==========================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.divider()
    st.markdown(f"### 🔑 Session active")
    st.info(f"Rôle actuel : **{st.session_state.role}**")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.role = None; st.rerun()
    st.divider()
    now = datetime.now()
    st.write(f"📅 **Date :** {now.strftime('%d/%m/%Y')}")
    st.write(f"⏰ **Heure :** {now.strftime('%H:%M:%S')}")
    st.caption("RCRP Management System v14.2")

# ==========================================
# 7. INTERFACE PRINCIPALE
# ==========================================
tab_immat, tab_dossier, tab_banque = st.tabs([
    "🚗 Registre Immatriculations", 
    "🪪 Dossiers Citoyens", 
    "💰 Gestion Bancaire Centrale"
])

# --- ONGLET 1 : IMMATRICULATIONS (VERROUILLÉ POUR STAFF/RCT) ---
with tab_immat:
    st.header("🚗 Registre National des Véhicules")
    
    # LA POSSIBILITÉ D'IMMATRICULER EST ENLEVÉE POUR RCT ET STAFF (COMME DEMANDÉ)
    if st.session_state.role not in ["RCT", "Staff"]:
        with st.expander("➕ Enregistrer un nouveau véhicule (Paiement automatique)", expanded=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                proprio = st.selectbox("Propriétaire", ["---"] + df_banque["Nom Roblox"].tolist())
                marque = st.text_input("Marque et Modèle")
                plaque = st.text_input("Plaque")
            with col_f2:
                assurance = st.selectbox("Assurance", ["Aucune", "AVERIS (130$)", "RCT (150$)"])
                code_secret = st.text_input("🔑 Code Secret", type="password")
            
            # CALCULS (RÉTABLIS)
            f_fixe, f_assu, f_jeune = 175, 0, 0
            if "AVERIS" in assurance: f_assu = 130
            elif "RCT" in assurance: f_assu = 150
            
            rct_c = len(df_im[(df_im["Nom d'utilisateur ROBLOX"] == proprio) & (df_im["Assurance"].str.contains("RCT"))])
            if "RCT" in assurance and rct_c >= 2: f_assu = 0

            if proprio != "---":
                u_d = df_banque[df_banque["Nom Roblox"] == proprio]
                if not u_d.empty:
                    try:
                        d_arr = datetime.strptime(str(u_d.iloc[0]["Date d'arrivée"]), "%d/%m/%Y")
                        if (datetime.now() - d_arr).days < 30: f_jeune = 50
                    except: pass
            
            total_t = f_fixe + f_assu + f_jeune
            st.markdown(f'<div class="ticket-fix"><b>🧾 FACTURE IMMAT</b><br>Dossier: 175$<br>Assu: {f_assu}$<br>Taxe: {f_jeune}$<br><b>TOTAL: {total_t}$</b></div>', unsafe_allow_html=True)

            if st.button("✅ Confirmer l'achat"):
                if proprio != "---" and plaque and code_secret:
                    idx_c = df_banque[df_banque["Nom Roblox"] == proprio].index[0]
                    if float(df_banque.at[idx_c, "Solde"]) >= total_t:
                        df_banque.at[idx_c, "Solde"] = float(df_banque.at[idx_c, "Solde"]) - total_t
                        if f_assu > 0:
                            cible = TARGET_AVERIS if "AVERIS" in assurance else TARGET_RCT
                            idx_d = df_banque[df_banque["Nom Roblox"] == cible].index[0]
                            df_banque.at[idx_d, "Solde"] = float(df_banque.at[idx_d, "Solde"]) + f_assu
                        new_v = pd.DataFrame([{"Horodateur": datetime.now().strftime("%d/%m/%Y"), "Nom d'utilisateur ROBLOX": proprio, "Marque du véhicule": marque, "Numéro de la plaque": plaque, "Assurance": assurance, "CODE": str(code_secret)}])
                        conn.update(worksheet="Banque", data=df_banque)
                        conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_v], ignore_index=True))
                        st.success("Payé et enregistré !"); time.sleep(1); st.rerun()
    else:
        st.info("⚠️ Enregistrement désactivé pour votre grade. Seuls les citoyens via le portail public peuvent immatriculer.")

    # LISTE DES VÉHICULES (GARDÉE)
    st.divider()
    search_v = st.text_input("🔍 Rechercher une plaque").lower()
    if not df_im.empty:
        mask = df_im.apply(lambda x: search_v in str(x).lower(), axis=1)
        for i, r in df_im[mask].iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"🚗 **{r['Numéro de la plaque']}** ({r['Nom d\'utilisateur ROBLOX']})")
                c2.markdown(f"<span class='badge-assu'>{r['Assurance']}</span>", unsafe_allow_html=True)
                with st.expander("🗑️ Supprimer"):
                    if st.text_input("Code Secret", type="password", key=f"d_{i}") == str(r['CODE']) or st.session_state.role == "Staff":
                        if st.button("Confirmer", key=f"b_{i}"):
                            conn.update(worksheet="Copie de Immatriculations", data=df_im.drop(i))
                            st.success("Supprimé"); st.rerun()

# --- ONGLET 2 : DOSSIERS & PAYE ---
with tab_dossier:
    st.header("🪪 Dossiers Citoyens")
    if st.session_state.role == "Staff":
        with st.container(border=True):
            st.subheader("🏦 Script de Gestion Mensuelle")
            if st.button("🧧 EXECUTER LA PAYE (15k) & PRÉLÈVEMENTS"):
                with st.status("Exécution..."):
                    df_banque["Solde"] = df_banque["Solde"].apply(lambda x: float(x) + 15000)
                    tr = {}
                    for _, v in df_im.iterrows():
                        owner = v["Nom d'utilisateur ROBLOX"]
                        if owner in df_banque["Nom Roblox"].values:
                            idx_o = df_banque[df_banque["Nom Roblox"] == owner].index[0]
                            if "RCT" in v["Assurance"]:
                                tr[owner] = tr.get(owner, 0) + 1
                                if tr[owner] <= 2:
                                    df_banque.at[idx_o, "Solde"] -= 150
                                    idx_r = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                    df_banque.at[idx_r, "Solde"] += 150
                            elif "AVERIS" in v["Assurance"]:
                                df_banque.at[idx_o, "Solde"] -= 130
                                idx_a = df_banque[df_banque["Nom Roblox"] == TARGET_AVERIS].index[0]
                                df_banque.at[idx_a, "Solde"] += 130
                    conn.update(worksheet="Banque", data=df_banque); st.success("Terminé !"); st.rerun()

    search_d = st.text_input("🔍 Rechercher un dossier").lower()
    if search_d:
        res_d = df_banque[(df_banque["Nom Roblox"].str.lower().str.contains(search_d, na=False)) | (df_banque["Nom Discord"].str.lower().str.contains(search_d, na=False))]
        for _, c in res_d.iterrows():
            with st.container(border=True):
                st.subheader(f"Dossier de {c['Nom Roblox']}")
                p = df_pts[df_pts["Nom Roblox"] == c["Nom Roblox"]]
                if not p.empty: st.metric("Points", f"{p.iloc[0]['PTS']} / 25")

    if st.session_state.role == "Staff":
        with st.expander("👤 Nouveau profil"):
            with st.form("f_n"):
                nr, nd = st.text_input("Roblox"), st.text_input("Discord")
                if st.form_submit_button("Créer"):
                    dt = datetime.now().strftime("%d/%m/%Y")
                    conn.update(worksheet="Banque", data=pd.concat([df_banque, pd.DataFrame([{"Solde": 15000, "Nom Discord": nd, "Nom Roblox": nr, "Date d'arrivée": dt}])], ignore_index=True))
                    conn.update(worksheet="Points Permis", data=pd.concat([df_pts, pd.DataFrame([{"Nom Roblox": nr, "PTS": 25}])], ignore_index=True))
                    st.success("Créé !"); st.rerun()

# --- ONGLET 3 : BANQUE ---
with tab_banque:
    st.header("💰 Gestion Bancaire Centrale")
    search_b = st.text_input("🔍 Rechercher un compte").lower()
    if search_b:
        res_b = df_banque[(df_banque["Nom Roblox"].str.lower().str.contains(search_b, na=False)) | (df_banque["Nom Discord"].str.lower().str.contains(search_b, na=False))]
        for idx, row in res_b.iterrows():
            with st.container(border=True):
                st.subheader(f"Compte : {row['Nom Roblox']}")
                st.metric("Solde", f"{float(row['Solde']):,.0f} $")
                if st.session_state.role in ["RCT", "Staff"]:
                    with st.expander("⚙️ Opération"):
                        m, r = st.number_input("Montant", key=f"m_{idx}"), st.text_input("Motif", key=f"r_{idx}")
                        if st.button("Confirmer le retrait", key=f"btn_{idx}"):
                            idx_c = df_banque[df_banque["Nom Roblox"] == row['Nom Roblox']].index[0]
                            df_banque.at[idx_c, "Solde"] -= m
                            txt = "Fonds détruits"
                            if st.session_state.role == "RCT":
                                idx_r = df_banque[df_banque["Nom Roblox"] == TARGET_RCT].index[0]
                                df_banque.at[idx_r, "Solde"] += m
                                txt = f"Virement vers {TARGET_RCT}"
                            conn.update(worksheet="Banque", data=df_banque)
                            st.markdown(f'<div class="ticket-fix"><b>🧾 REÇU</b><br>Montant: {m}$<br>Motif: {r}<br>Nature: {txt}</div>', unsafe_allow_html=True)
                            time.sleep(1); st.rerun()

st.markdown("---")
st.markdown("<center><small>RCRP Système v14.2 | 2026</small></center>", unsafe_allow_html=True)
