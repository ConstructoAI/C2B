# Interface Mono-Entreprise - Adaptations pour un portail dédié
# Modifications pour transformer l'app en portail mono-entreprise

import streamlit as st
from config_entreprise_unique import *

def afficher_page_accueil_mono():
    """Page d'accueil adaptée au modèle mono-entreprise"""
    
    entreprise = get_entreprise_proprietaire()
    
    # Header personnalisé avec les informations de l'entreprise
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1E40AF 0%, #059669 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem; color: white;">
        <h1 style="margin: 0; text-align: center;">{entreprise['nom_entreprise']}</h1>
        <p style="text-align: center; font-size: 1.2em; margin: 0.5rem 0;">
            {PORTAIL_CONFIG['sous_titre']}
        </p>
        <div style="text-align: center; margin-top: 1rem;">
            <strong>📍 {entreprise['ville']}, {entreprise['province']}</strong> • 
            <strong>📞 {entreprise['telephone']}</strong> • 
            <strong>📧 {entreprise['email']}</strong>
        </div>
        {f"<div style='text-align: center; margin-top: 0.5rem;'><strong>🏗️ RBQ: {entreprise['numero_rbq']}</strong></div>" if entreprise.get('numero_rbq') else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # Description des services
    st.markdown("## 🏗️ Nos Spécialités")
    
    col1, col2, col3 = st.columns(3)
    domaines = entreprise['domaines_expertise']
    
    for i, domaine in enumerate(domaines):
        with [col1, col2, col3][i % 3]:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                <h4 style="color: #1E40AF; margin: 0;">{domaine}</h4>
            </div>
            """, unsafe_allow_html=True)
    
    # Description de l'entreprise
    st.markdown("## 📋 À Propos")
    st.markdown(entreprise['description_entreprise'])
    
    # Zones de service
    if entreprise.get('zones_service'):
        st.markdown("## 📍 Zones de Service")
        zones_col1, zones_col2 = st.columns(2)
        zones = entreprise['zones_service']
        
        for i, zone in enumerate(zones):
            with zones_col1 if i % 2 == 0 else zones_col2:
                st.markdown(f"• {zone}")
    
    # Bouton d'action principal
    st.markdown("---")
    st.markdown("## 🚀 Demander une Soumission")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Faire une Demande de Soumission", use_container_width=True, type="primary"):
            if 'user_type' not in st.session_state:
                st.session_state.page = 'auth_client'
            else:
                st.session_state.page = 'nouvelle_demande'
            st.rerun()
    
    # Informations de contact
    st.markdown("---")
    st.markdown("## 📞 Nous Contacter")
    
    contact_col1, contact_col2 = st.columns(2)
    
    with contact_col1:
        st.markdown(f"""
        **📍 Adresse:**  
        {entreprise['adresse']}  
        {entreprise['ville']}, {entreprise['code_postal']}
        
        **📞 Téléphone:**  
        {entreprise['telephone']}
        
        **📧 Email:**  
        {entreprise['email']}
        """)
    
    with contact_col2:
        if entreprise.get('site_web'):
            st.markdown(f"**🌐 Site Web:**  \n{entreprise['site_web']}")
        
        if entreprise.get('certifications'):
            st.markdown("**🏆 Certifications:**")
            for cert in entreprise['certifications'][:3]:  # Afficher les 3 premières
                st.markdown(f"• {cert}")
        
        st.markdown(f"""
        **⏱️ Délai de réponse moyen:**  
        {entreprise.get('delai_reponse_moyen', 24)} heures
        
        **🎯 Disponibilité:**  
        {entreprise.get('disponibilite', 'Disponible').title()}
        """)

def afficher_notification_soumission_acceptee(numero_reference):
    """Affiche une notification quand une soumission est acceptée"""
    
    st.success(f"""
    🎉 **SOUMISSION ACCEPTÉE !**
    
    **Numéro de soumission:** {numero_reference}
    
    Le client a accepté votre soumission. Vous pouvez maintenant:
    - Contacter le client pour finaliser les détails
    - Préparer le contrat
    - Planifier le début des travaux
    """)
    
    # Boutons d'action
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📞 Contacter le Client", key="contact_client"):
            st.session_state.page = 'contact_client'
            st.rerun()
    
    with col2:
        if st.button("📄 Générer le Contrat", key="generer_contrat"):
            st.session_state.page = 'generer_contrat'
            st.rerun()
    
    with col3:
        if st.button("📅 Planifier les Travaux", key="planifier_travaux"):
            st.session_state.page = 'planifier_travaux'
            st.rerun()

def sidebar_entreprise():
    """Sidebar adaptée pour l'entreprise propriétaire"""
    
    entreprise = get_entreprise_proprietaire()
    
    st.sidebar.markdown(f"""
    ### 🏗️ {entreprise['nom_entreprise']}
    
    **👤 {entreprise['nom_contact']}**  
    *{entreprise['poste_contact']}*
    
    ---
    
    📞 {entreprise['telephone']}  
    📧 {entreprise['email']}  
    🏗️ RBQ: {entreprise.get('numero_rbq', 'N/A')}
    
    ---
    """)
    
    # Statut de l'entreprise
    disponibilite = entreprise.get('disponibilite', 'disponible')
    couleur = {'disponible': '🟢', 'occupe': '🟡', 'indisponible': '🔴'}
    
    st.sidebar.markdown(f"""
    **Statut:** {couleur.get(disponibilite, '⚪')} {disponibilite.title()}
    
    **Tarification:** {entreprise.get('tarif_horaire_min', 0)}$ - {entreprise.get('tarif_horaire_max', 0)}$/h
    """)

def dashboard_entreprise_proprietaire():
    """Dashboard simplifié pour l'entreprise propriétaire"""
    
    st.markdown("## 🏠 Tableau de Bord - Mes Projets")
    
    entreprise = get_entreprise_proprietaire()
    
    # Statistiques rapides
    col1, col2, col3, col4 = st.columns(4)
    
    from app import get_database_connection
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Demandes reçues
    cursor.execute('SELECT COUNT(*) FROM demandes_devis WHERE statut = "publiee"')
    nb_demandes_recues = cursor.fetchone()[0]
    
    # Mes soumissions
    cursor.execute('SELECT COUNT(*) FROM soumissions WHERE prestataire_id = 1')
    nb_mes_soumissions = cursor.fetchone()[0]
    
    # Soumissions acceptées
    cursor.execute('SELECT COUNT(*) FROM soumissions WHERE prestataire_id = 1 AND statut = "acceptee"')
    nb_acceptees = cursor.fetchone()[0]
    
    # Projets en cours
    cursor.execute('SELECT COUNT(*) FROM contrats WHERE prestataire_id = 1 AND statut_contrat = "actif"')
    nb_projets_cours = cursor.fetchone()[0]
    
    conn.close()
    
    with col1:
        st.metric("📥 Demandes Reçues", nb_demandes_recues)
    
    with col2:
        st.metric("📤 Mes Soumissions", nb_mes_soumissions)
    
    with col3:
        st.metric("✅ Acceptées", nb_acceptees)
    
    with col4:
        st.metric("🚧 Projets en Cours", nb_projets_cours)
    
    # Actions rapides pour l'entreprise
    st.markdown("### 🚀 Actions Rapides")
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("📥 Voir Nouvelles Demandes", use_container_width=True):
            st.session_state.page = 'demandes_disponibles'
            st.rerun()
    
    with action_col2:
        if st.button("📊 Mes Soumissions", use_container_width=True):
            st.session_state.page = 'mes_soumissions'
            st.rerun()
    
    with action_col3:
        if st.button("🏗️ Projets en Cours", use_container_width=True):
            st.session_state.page = 'projets_cours'
            st.rerun()
    
    # Dernières activités
    st.markdown("### 📋 Activité Récente")
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Récentes demandes
    cursor.execute('''
        SELECT d.titre, d.type_projet, d.budget_max, d.date_creation, ec.nom_entreprise
        FROM demandes_devis d
        JOIN entreprises_clientes ec ON d.client_id = ec.id
        WHERE d.statut = "publiee"
        ORDER BY d.date_creation DESC
        LIMIT 5
    ''')
    
    demandes_recentes = cursor.fetchall()
    
    if demandes_recentes:
        st.markdown("**Nouvelles demandes de clients :**")
        for demande in demandes_recentes:
            with st.expander(f"{demande[0]} - {demande[4]} ({demande[2]:,.0f}$)", expanded=False):
                st.markdown(f"**Type:** {demande[1]}")
                st.markdown(f"**Budget:** {demande[2]:,.0f}$")
                st.markdown(f"**Reçue le:** {demande[3][:10]}")
                
                if st.button(f"Soumissionner", key=f"soum_{demande[0]}"):
                    st.session_state.demande_selectionnee = demande[0]
                    st.session_state.page = 'nouvelle_soumission'
                    st.rerun()
    else:
        st.info("Aucune nouvelle demande pour le moment.")
    
    conn.close()