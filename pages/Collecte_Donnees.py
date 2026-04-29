import streamlit as st
import sys
import os
import io
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Collecte Stratégique | AssurInsight",
    page_icon="📝",
    layout="wide"
)

# --- IMPORT DB_MANAGER ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from database.db_manager import save_entry, get_all_data, create_table
    create_table()
except ImportError:
    st.error("⚠️ Erreur de liaison avec le module database. Vérifiez le chemin du dossier.")

# --- GESTION DES NOTIFICATIONS POST-RERUN ---
if "success_msg" not in st.session_state:
    st.session_state.success_msg = None

# --- FONCTION EXPORT PDF (ReportLab) ---
def export_pdf(df):
    try:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        elements = []
        
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Rapport des Collectes - AssurInsight ({datetime.now().strftime('%d/%m/%Y')})", styles['Title']))
        
        data_list = [df.columns.to_list()] + df.values.tolist()
        
        t = Table(data_list)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(t)
        doc.build(elements)
        return buffer.getvalue()
    except Exception as e:
        return None

# --- CSS PREMIUM (CORRECTION CONTRASTE & DESIGN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    /* Fond de l'application */
    .stApp {
        background-color: #f8faff;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Correction critique du contraste des titres et labels */
    /* On force une couleur sombre (#002d5e) pour éviter le blanc sur blanc */
    .stMarkdown, .stSelectbox label, .stTextInput label, .stRadio label, .stSlider label, .stMultiSelect label, 
    .stHeader, p, span, label, .stSubheader, h1, h2, h3 {
        color: #002d5e !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    .header-container {
        text-align: center;
        padding: 30px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 30px;
        border: 1px solid #e2e8f0;
    }

    .main-title {
        background: linear-gradient(90deg, #002d5e, #007bff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
    }

    .section-card {
        background: white;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }

    /* Style du bouton envoyer */
    div.stButton > button {
        background: linear-gradient(135deg, #002d5e 0%, #007bff 100%) !important;
        color: white !important;
        border: none !important;
        height: 60px;
        border-radius: 15px !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        box-shadow: 0 10px 20px rgba(0, 123, 255, 0.2) !important;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: scale(1.01);
        box-shadow: 0 12px 25px rgba(0, 123, 255, 0.3) !important;
    }

    /* Bouton retour spécifique */
    .stButton > button[key="btn_home"] {
        background: white !important;
        color: #002d5e !important;
        border: 2px solid #e2e8f0 !important;
        height: 45px !important;
        font-size: 1rem !important;
        box-shadow: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- AFFICHAGE DU SUCCÈS (SI ACTIVÉ) ---
if st.session_state.success_msg:
    st.balloons()
    st.success(st.session_state.success_msg)
    st.session_state.success_msg = None  # Réinitialisation après affichage

# --- BOUTON RETOUR & NAVIGATION ---
col_back, _ = st.columns([1, 4])
with col_back:
    if st.button("⬅️ Menu Principal", key="btn_home"):
        st.switch_page("Accueil.py")

# --- HEADER ---
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">Collecte de Données Stratégiques</h1>
        <p style="color: #64748b; font-weight: 400;">Enrichissez l'intelligence du marché de l'assurance au Cameroun</p>
    </div>
""", unsafe_allow_html=True)

tab_form, tab_view = st.tabs(["🖋️ FORMULAIRE D'ENQUÊTE", "📊 BASE DE DONNÉES & EXPORTS"])

with tab_form:
    with st.form("survey_form", clear_on_submit=True):
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("👤 Profil & Localisation")
        c1, c2, c3 = st.columns(3)
        with c1:
            sexe = st.selectbox("Sexe", ["Masculin", "Féminin"])
            age = st.selectbox("Âge", ["18-25", "26-35", "36-45", "46-55", "56+"])
        with c2:
            region_val = st.selectbox("Région", ["Littoral", "Centre", "Ouest", "Sud", "Nord", "Est", "Adamaoua", "EN", "NW", "SW"])
            ville = st.text_input("Ville")
        with c3:
            secteur = st.selectbox("Secteur", ["Public", "Privé Formel", "Informel", "Étudiant", "Libéral"])
            revenu = st.selectbox("Revenu Mensuel", ["< 50k", "50k-150k", "150k-300k", "300k-600k", "> 300k"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🧠 Perception & Confiance")
        c4, c5 = st.columns(2)
        with c4:
            perception = st.radio("L'assurance est pour vous :", ["Nécessaire", "Une charge", "Une obligation"], horizontal=True)
            connaissance = st.select_slider("Niveau de connaissance", ["Nulle", "Faible", "Moyenne", "Bonne", "Expert"])
        with c5:
            confiance = st.slider("Confiance envers les assureurs (0-10)", 0, 10, 5)
            barriere = st.selectbox("Principale barrière", ["Coût élevé", "Méfiance (Remboursement)", "Lenteur administrative", "Manque d'infos", "Religieux/Culturel"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🛡️ Habitudes & Digitalisation")
        c6, c7 = st.columns(2)
        with c6:
            type_assur = st.multiselect("Assurances possédées", ["Auto", "Santé", "Vie/Décès", "Retraite", "Scolaire", "Habitation", "Aucune"])
            canal = st.selectbox("Canal préféré", ["Agent physique", "Courtier", "Banque", "Application Mobile", "Site Web"])
        with c7:
            experience = st.radio("Sinistre non remboursé ?", ["Non", "Oui", "Jamais eu de sinistre"], horizontal=True)
            insurtech = st.select_slider("Prêt pour l'assurance digitale ?", ["Pas du tout", "Peut-être", "Totalement prêt"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🚀 ENREGISTRER L'ENQUÊTE DANS LA BASE")
        
        if submit_btn:
            if not ville:
                st.warning("⚠️ Veuillez préciser la ville avant d'enregistrer.")
            else:
                data = {
                    "sexe": sexe,
                    "age_tranche": age,
                    "ville": ville,
                    "profession": region_val, 
                    "secteur_activite": secteur,
                    "revenu_mensuel": revenu,
                    "connaissance_assurance": connaissance,
                    "type_abonnement": ", ".join(type_assur) if type_assur else "Aucune",
                    "niveau_confiance": confiance,
                    "barriere_principale": barriere,
                    "critere_choix": canal,
                    "culture_cima": perception
                }
                
                try:
                    save_entry(data)
                    st.session_state.success_msg = f"✨ Félicitations ! L'enquête de la ville de {ville} a été enregistrée avec succès."
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'enregistrement : {e}")

with tab_view:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    df = get_all_data()
    
    if df is not None and not df.empty:
        st.markdown(f"### 🗂️ Aperçu de la Base de Données ({len(df)} enregistrements)")
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📥 Centre d'Exportation Professionnel")
        
        col_csv, col_xlsx, col_pdf = st.columns(3)
        
        csv_data = df.to_csv(index=False).encode('utf-8')
        col_csv.download_button(
            label="📂 Télécharger en CSV",
            data=csv_data,
            file_name=f"AssurInsight_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        output_xlsx = io.BytesIO()
        with pd.ExcelWriter(output_xlsx, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Donnees_Collectees')
        col_xlsx.download_button(
            label="📂 Télécharger en Excel",
            data=output_xlsx.getvalue(),
            file_name=f"AssurInsight_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        pdf_data = export_pdf(df)
        if pdf_data:
            col_pdf.download_button(
                label="📂 Télécharger en PDF",
                data=pdf_data,
                file_name=f"AssurInsight_Rapport_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            col_pdf.info("PDF : Installez 'reportlab'")
            
    else:
        st.info("💡 La base de données est actuellement vide. Remplissez le formulaire pour commencer la collecte.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
    <div style="text-align: center; padding-top: 20px; color: #94a3b8; font-size: 0.8rem;">
        © 2026 AssurInsight - Système de Collecte de Données Sécurisé | Développé avec Streamlit
    </div>
""", unsafe_allow_html=True)