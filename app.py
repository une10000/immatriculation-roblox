import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="RCRP - Portail Officiel", layout="wide")

# --- INITIALISATION SESSION ---
if "role" not in st.session_state:
    st.session_state.role = None

# --- PARAMÈTRES ET CODES ---
conn = st.connection("gsheets", type=GSheetsConnection)
CODE_ADMIN_GENERAL = "RCRPFR-25-26" 
CODE_ENTREPRISE = "RCT-26-RCRPFR" 
MON_PSEUDO_ROBLOX = "une10000"
LOGO_URL = "https://cdn.discordapp.com/attachments/1441508709024006315/1467106550656270484/Capture_decran_2025-12-01_a_21.03.31.png"

def get_data(sheet_name):
    st.cache_data.clear()
    try:
        data = conn.read(worksheet=sheet_name, ttl=0)
        return data.dropna(how='all').fillna("")
    except: return pd.DataFrame()

# ==========================================
# 🚪 PAGE DE CONNEXION
# ==========================================
if st.session_state.role is None:
    st.divider()
    center_co1, center_co2, center_co3 = st.columns([1, 2, 1])
    with center_co2:
        st.image(LOGO_URL, width=300)
        st.title("🏛️ Portail des Services RCRP")
        st.subheader("Choisissez votre mode d'accès")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.write("### 👤 Citoyen")
            st.write("Consulter les registres publics.")
            if st.button("Accès Public", use_container_width=True):
                st.session_state.role = "Civil"; st.rerun()
    with col2:
        with st.container(border=True):
            st.write("### 🛠️ Entreprise (RCT)")
            st.write("Interface de facturation business.")
            c_rct = st.text_input("Code RCT", type="password")
            if st.button("Connexion Pro", use_container_width=True):
                if c_rct == CODE_ENTREPRISE:
                    st.session_state.role = "RCT"; st.rerun()
                else: st.error("Code invalide.")
    with col3:
        with st.container(border=True):
            st.write("### 👮 Autorités / Staff")
            st.write("Gestion complète du fichier central.")
            c_pol = st.text_input("Code Autorisation", type="password")
            if st.button("Connexion Sécurisée", use_container_width=True):
                if c_pol == CODE_ADMIN_GENERAL:
                    st.session_state.role = "Staff"; st.rerun()
                else: st.error("Code invalide.")
    st.stop()

# ==========================================
# 🖥️ INTERFACE CONNECTÉE
# ==========================================

# HEADER REPRÉSENTATIF (LOGO TOUJOURS PRÉSENT)
header_1, header_2 = st.columns([1, 6])
with header_1:
    st.image(LOGO_URL, width=100)
with header_2:
    st.title(f"🏛️ Espace {st.session_state.role}")
    if st.button("🚪 Déconnexion"):
        st.session_state.role = None; st.rerun()

# --- DÉFINITION DES ONGLETS SELON LE RÔLE ---
if st.session_state.role == "Staff":
    tabs = st.tabs(["🚗 Immatriculations", "🪪 Permis de conduire", "💰 Banque Centrale", "📜 Archives Logs"])
elif st.session_state.role == "RCT":
    tabs = st.tabs(["🚗 Immatriculations", "💰 Facturation RCT Business"])
else:
    tabs = st.tabs(["🚗 Registre Véhicules", "💰 Consulter mon Solde"])

# --- LISTES ---
liste_etats = sorted(["Alberta", "Beautiful British Columbia", "California", "Colorado", "Connecticut", "Delaware", "Washington", "Florida", "Indiana", "Kansas", "Maine", "Manitoba", "Maryland", "Massachusetts", "Michigan", "Mississippi", "Montana", "New Brunswick", "New Hampshire", "New Jersey", "New York", "Newfoundland Labrador", "Nova Scotia", "Nuvanut", "Ohio", "Oklahoma", "Ontario", "Pennsylvania", "Prince Edward Island", "Quebec", "Rhode Island", "Saskatchewan", "South Carolina", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Wisconsin", "Yukon"])
liste_marques = sorted(["Altstadt", "Bremen", "Comrader", "Delton", "Envy", "Eva", "Gam", "Gemini", "Hamotsu", "Katzmann", "Koritsu", "Land treker", "Lexima", "Linco", "Lyon", "Marshall", "Mita", "Mizuhara", "Nesumi", "Neptune", "Revasser", "Revolt", "Roamer", "Senseon", "Shatoku", "Sternauster", "Turismo", "Yosurai"])
liste_assurances = ["Non assuré", "RCT", "Averis"]

# ==========================================
# 🚗 IMMATRICULATIONS (TOUS)
# ==========================================
with tabs[0]:
    df_im = get_data("Copie de Immatriculations")
    st.metric("🚗 Véhicules enregistrés", len(df_im))
    
    with st.expander("➕ Enregistrer un nouveau véhicule"):
        with st.form("add_v96"):
            c1, c2 = st.columns(2)
            u = c1.text_input("👤 Pseudo Roblox"); m = c1.selectbox("🚘 Marque", liste_marques)
            e = c2.selectbox("📍 État", liste_etats); p = c2.text_input("🔢 Plaque")
            a = c1.selectbox("🛡️ Assurance", liste_assurances); c = c2.text_input("🔑 Code secret véhicule", type="password")
            if st.form_submit_button("✅ Valider l'immatriculation"):
                if u and p and c:
                    new_r = pd.DataFrame([{"Horodateur": (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"), "Nom d'utilisateur ROBLOX": u, "Marque du véhicule": m, "L'état de la plaque": e, "Numéro de la plaque": p, "Assurance": a, "CODE": str(c)}])
                    conn.update(worksheet="Copie de Immatriculations", data=pd.concat([df_im, new_r], ignore_index=True))
                    st.success("🎉 Enregistré avec succès !"); time.sleep(1); st.rerun()

    st.divider()
    sq = st.text_input("🔍 Rechercher une plaque ou un propriétaire").strip().upper()
    if not df_im.empty:
        mask = df_im.apply(lambda r: sq in str(r).upper(), axis=1) if sq else [True]*len(df_im)
        for idx, row in df_im[mask].iterrows():
            with st.container(border=True):
                co1, co2 = st.columns([3, 1])
                co1.markdown(f"### 🚗 {row['Numéro de la plaque']} — {row['Marque du véhicule']}")
                co1.write(f"👤 **{row['Nom d\'utilisateur ROBLOX']}** | 📍 {row['L\'état de la plaque']} | 🛡️ **Assurance : {row['Assurance']}**")
                
                # Gestion réservée Staff/RCT ou propriétaire avec code
                if co2.button(f"⚙️ Gérer", key=f"g_{idx}"): st.session_state[f"op_{idx}"] = not st.session_state.get(f"op_{idx}", False)
                
                if st.session_state.get(f"op_{idx}"):
                    with st.form(f"fo_{idx}"):
                        np = st.text_input("🔢 Nouvelle Plaque", value=row['Numéro de la plaque'])
                        na = st.selectbox("🛡️ Nouvelle Assurance", liste_assurances, index=liste_assurances.index(row['Assurance']))
                        vc = st.text_input("🔑 Code secret véhicule", type="password")
                        c_s, c_d = st.columns(2)
                        if c_s.form_submit_button("💾 Sauver"):
                            if vc == str(row['CODE']) or st.session_state.role == "Staff":
                                df_im.at[idx, 'Numéro de la plaque'] = np
                                df_im.at[idx, 'Assurance'] = na
                                conn.update(worksheet="Copie de Immatriculations", data=df_im)
                                st.success("✨ Mis à jour !"); time.sleep(1); st.rerun()
                            else: st.error("❌ Code secret incorrect.")
                        if c_d.form_submit_button("🗑️ Supprimer"):
                            if vc == str(row['CODE']) or st.session_state.role == "Staff":
                                updated = df_im[df_im['Numéro de la plaque'] != row['Numéro de la plaque']]
                                conn.update(worksheet="Copie de Immatriculations", data=updated)
                                st.success("🗑️ Retiré."); time.sleep(1); st.rerun()

# ==========================================
# 💰 BANQUE (ADAPTÉE AU RÔLE)
# ==========================================
with tabs[1]:
    df_b = get_data("Banque")
    if st.session_state.role == "Civil":
        st.write("### 🏦 Votre compte personnel")
        nom = st.text_input("Entrez votre Pseudo Roblox pour voir votre solde").strip().lower()
        if nom:
            res = df_b[df_b['Nom Roblox'].str.lower() == nom]
            if not res.empty:
                st.metric(f"Solde de {nom}", f"{float(res.iloc[0]['Solde']):,.0f} $")
            else: st.error("❌ Compte introuvable.")
    else:
        st.write(f"### 💰 Interface de Gestion Bancaire ({st.session_state.role})")
        sb = st.text_input("🔍 Rechercher un compte citoyen").strip().lower()
        if not df_b.empty and sb:
            res_b = df_b[df_b.apply(lambda r: sb in str(r).lower(), axis=1)]
            for idx, row in res_b.iterrows():
                solde = float(row.get('Solde', 0))
                with st.container(border=True):
                    st.metric(f"👤 {row['Nom Roblox']}", f"{solde:,.0f} $")
                    with st.form(f"fb_{idx}"):
                        mt = st.number_input("💵 Montant", min_value=0.0, step=100.0)
                        c_ret, c_aj = st.columns(2)
                        if c_ret.form_submit_button("📉 RETIRER / FACTURER"):
                            if st.session_state.role == "RCT":
                                if solde >= mt:
                                    df_b.at[idx, "Solde"] = solde - mt
                                    mask = df_b['Nom Roblox'].str.lower() == MON_PSEUDO_ROBLOX.lower()
                                    if mask.any():
                                        df_b.at[df_b[mask].index[0], "Solde"] = float(df_b.at[df_b[mask].index[0], "Solde"]) + mt
                                        conn.update(worksheet="Banque", data=df_b)
                                        st.success("💸 Facturation RCT payée !"); time.sleep(1); st.rerun()
                                    else: st.error("❌ Erreur: Compte 'une10000' introuvable.")
                                else: st.error("❌ Solde client insuffisant.")
                            else: # Staff
                                df_b.at[idx, "Solde"] = solde - mt
                                conn.update(worksheet="Banque", data=df_b)
                                st.success("📉 Retrait effectué."); time.sleep(1); st.rerun()
                        if c_aj.form_submit_button("📈 AJOUTER (Staff Only)"):
                            if st.session_state.role == "Staff":
                                df_b.at[idx, "Solde"] = solde + mt
                                conn.update(worksheet="Banque", data=df_b)
                                st.success("📈 Ajout effectué."); time.sleep(1); st.rerun()
                            else: st.error("❌ Action réservée au Staff.")

# L'onglet Permis et Logs sont inclus dans la vue Staff.
if st.session_state.role == "Staff":
    with tabs[2]:
        st.write("### 🪪 Gestion des Permis de Conduire")
        # Code Permis identique aux versions précédentes...
    with tabs[3]:
        st.write("### 📜 Archives Logs")
        st.dataframe(get_data("Logs").iloc[::-1], use_container_width=True)

st.markdown("---")
st.markdown("<center><small>République de Californie RP | Système v9.6</small></center>", unsafe_allow_html=True)
# ==========================================
# 💰 ONGLET 3 : BANQUE & RCT
# ==========================================
with tabs[2]:
    df_bank = get_data("Banque")
    # Calcul de la richesse totale
    total_bank = sum([float(x) for x in df_bank['Solde'] if str(x).replace('.','').isdigit()])
    
    b1, b2, b3 = st.columns(3)
    b1.metric("🏦 Masse Monétaire", f"{total_bank:,.0f} $")
    b2.metric("👥 Comptes Actifs", len(df_bank))
    b3.success("💡 RCT Business : Utilisez le code entreprise pour vos facturations.")

    sb = st.text_input("🔍 Rechercher un compte bancaire").strip().lower()
    if not df_bank.empty and sb:
        res_b = df_bank[df_bank.apply(lambda r: sb in str(r).lower(), axis=1)]
        for idx, row in res_b.iterrows():
            solde = float(row.get('Solde', 0))
            with st.container(border=True):
                c_info, c_op = st.columns([2, 2])
                c_info.metric(f"👤 {row['Nom Roblox']}", f"{solde:,.0f} $")
                with c_op:
                    with st.form(f"fb_v93_{idx}"):
                        cd = st.text_input("🔑 Code", type="password")
                        mt = st.number_input("💵 Somme", min_value=0.0, step=500.0)
                        r, a = st.columns(2)
                        if r.form_submit_button("📉 RETIRER"):
                            if cd == CODE_ENTREPRISE:
                                if solde >= mt:
                                    df_bank.at[idx, "Solde"] = solde - mt
                                    mask = df_bank['Nom Roblox'].str.lower() == MON_PSEUDO_ROBLOX.lower()
                                    if mask.any():
                                        im = df_bank[mask].index[0]
                                        df_bank.at[im, "Solde"] = float(df_bank.at[im, "Solde"]) + mt
                                        conn.update(worksheet="Banque", data=df_bank)
                                        st.success("💸 Virement RCT OK !"); time.sleep(1); st.rerun()
                                    else: st.error("Compte destinataire 'une10000' absent.")
                                else: st.error("Solde insuffisant.")
                            elif cd == CODE_ADMIN_GENERAL:
                                df_bank.at[idx, "Solde"] = solde - mt
                                conn.update(worksheet="Banque", data=df_bank)
                                st.success("📉 Retrait effectué."); time.sleep(1); st.rerun()
                            else: st.error("Code incorrect.")
                        if a.form_submit_button("📈 AJOUTER"):
                            if cd == CODE_ADMIN_GENERAL:
                                df_bank.at[idx, "Solde"] = solde + mt
                                conn.update(worksheet="Banque", data=df_bank)
                                st.success("📈 Ajouté."); time.sleep(1); st.rerun()
                            else: st.error("Accès Admin requis.")

# ==========================================
# 📜 ONGLET 4 : ARCHIVES LOGS
# ==========================================
with tabs[3]:
    st.info("🔐 Accès restreint au haut commandement.")
    pwd_log = st.text_input("🔑 Entrez le Code d'Accès Archives", type="password")
    if pwd_log == CODE_ADMIN_GENERAL:
        st.dataframe(get_data("Logs").iloc[::-1], use_container_width=True)
    elif pwd_log:
        st.error("❌ Accès refusé.")

st.markdown("---")
st.markdown("<center><small>RCRP FR - Système de Gestion Centralisé v9.3 | Développé pour le RP</small></center>", unsafe_allow_html=True)
