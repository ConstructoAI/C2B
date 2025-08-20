# Pages d'inscription pour les nouvelles entreprises
# Interface utilisateur complète avec validation

import streamlit as st
import json
import base64
from typing import Dict, Any, List
from inscription_system import *
from config_approbation import *

def page_selection_inscription():
    """Page de sélection du type d'inscription"""
    st.markdown("""
    <div class="demande-card">
        <h1>🏗️ Inscription CLIENT - PORTAIL C2B</h1>
        <p>Créez votre compte client pour demander des soumissions à notre entreprise</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 👤 Inscription pour CLIENTS uniquement")
    
    st.info("""
    **Note importante:** Ce portail C2B est dédié à UNE SEULE entreprise de construction.
    
    Si vous êtes un **CLIENT** (particulier ou entreprise ayant besoin de travaux), vous pouvez vous inscrire ici.
    
    Si vous êtes un **ENTREPRENEUR** cherchant des opportunités, ce portail n'est pas pour vous.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("👤 Je suis un CLIENT - Créer mon compte", key="btn_client_inscription", use_container_width=True, type="primary"):
            st.session_state.type_inscription = "client"
            st.session_state.page_inscription = "formulaire"
            st.rerun()
        
        st.markdown("""
        **En tant que CLIENT, vous pourrez:**
        - ✅ Demander des soumissions pour vos projets
        - ✅ Recevoir des propositions personnalisées
        - ✅ Communiquer directement avec notre entreprise
        - ✅ Suivre l'avancement de vos demandes
        - ✅ Accepter ou refuser les soumissions
        - ✅ Gérer vos contrats et évaluations
        """)
    
    with col2:
        st.warning("""
        **⚠️ Entreprise unique**
        
        Notre entreprise:
        **Construction Excellence Québec Inc.**
        
        RBQ: 5678-1234-01
        
        Toutes vos demandes seront traitées exclusivement par notre équipe.
        """)
    
    st.markdown("---")
    st.info("💡 **Déjà inscrit ?** Utilisez le bouton de connexion en haut de page")

def formulaire_inscription_client():
    """Formulaire d'inscription pour les clients (particuliers ou entreprises)"""
    st.markdown("""
    <div class="demande-card">
        <h2>📝 Inscription CLIENT</h2>
        <p>Créez votre compte pour demander des soumissions à Construction Excellence Québec Inc.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialiser les données du formulaire
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    with st.form("inscription_client_form"):
        st.markdown("### 🏢 Informations sur l'entreprise")
        
        col1, col2 = st.columns(2)
        with col1:
            nom_entreprise = st.text_input(
                "Nom de l'entreprise *", 
                value=st.session_state.form_data.get('nom_entreprise', ''),
                help="Raison sociale complète de votre entreprise"
            )
            secteur_activite = st.selectbox(
                "Secteur d'activité *", 
                options=SECTEURS_ACTIVITE,
                index=SECTEURS_ACTIVITE.index(st.session_state.form_data.get('secteur_activite', SECTEURS_ACTIVITE[0]))
            )
            taille_entreprise = st.selectbox(
                "Taille de l'entreprise *", 
                options=TAILLES_ENTREPRISE,
                index=TAILLES_ENTREPRISE.index(st.session_state.form_data.get('taille_entreprise', TAILLES_ENTREPRISE[0]))
            )
        
        with col2:
            numero_entreprise = st.text_input(
                "Numéro d'entreprise du Québec (NEQ)", 
                value=st.session_state.form_data.get('numero_entreprise', ''),
                help="Numéro d'identification officiel (optionnel)"
            )
            site_web = st.text_input(
                "Site web", 
                value=st.session_state.form_data.get('site_web', ''),
                placeholder="https://www.votreentreprise.com"
            )
        
        description_entreprise = st.text_area(
            "Description de l'entreprise",
            value=st.session_state.form_data.get('description_entreprise', ''),
            help="Décrivez brièvement votre entreprise et vos activités",
            height=100
        )
        
        st.markdown("### 👤 Contact principal")
        
        col1, col2 = st.columns(2)
        with col1:
            nom_contact = st.text_input(
                "Nom du contact *", 
                value=st.session_state.form_data.get('nom_contact', '')
            )
            email = st.text_input(
                "Adresse email *", 
                value=st.session_state.form_data.get('email', ''),
                help="Cette adresse servira pour la connexion"
            )
        
        with col2:
            poste_contact = st.text_input(
                "Poste/Fonction", 
                value=st.session_state.form_data.get('poste_contact', '')
            )
            telephone = st.text_input(
                "Téléphone *", 
                value=st.session_state.form_data.get('telephone', ''),
                placeholder="514-555-1234"
            )
        
        st.markdown("### 📍 Adresse de l'entreprise")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            adresse = st.text_input(
                "Adresse", 
                value=st.session_state.form_data.get('adresse', '')
            )
        with col2:
            ville = st.text_input(
                "Ville", 
                value=st.session_state.form_data.get('ville', '')
            )
        with col3:
            code_postal = st.text_input(
                "Code postal", 
                value=st.session_state.form_data.get('code_postal', ''),
                placeholder="H1A 1A1"
            )
        
        st.markdown("### 🔐 Sécurité du compte")
        
        col1, col2 = st.columns(2)
        with col1:
            mot_de_passe = st.text_input(
                "Mot de passe *", 
                type="password",
                help="Minimum 8 caractères"
            )
        with col2:
            confirmation_mot_de_passe = st.text_input(
                "Confirmer le mot de passe *", 
                type="password"
            )
        
        st.markdown("### 📎 Documents (optionnel)")
        st.info("💡 Vous pourrez ajouter les documents requis après validation de votre email")
        
        # Afficher les documents qui seront demandés
        docs_requis = obtenir_documents_requis('client')
        if docs_requis:
            st.markdown("**Documents qui vous seront demandés :**")
            for doc in docs_requis:
                required_text = "**Obligatoire**" if doc['obligatoire'] else "Optionnel"
                st.markdown(f"- {doc['nom']} ({required_text}) - {doc['description']}")
        
        st.markdown("---")
        
        # Conditions d'utilisation
        conditions_acceptees = st.checkbox(
            "J'accepte les conditions d'utilisation et la politique de confidentialité *",
            help="Vous devez accepter nos conditions pour créer un compte"
        )
        
        # Bouton de soumission
        submitted = st.form_submit_button(
            "📤 Soumettre ma demande d'inscription",
            use_container_width=True
        )
        
        if submitted:
            # Préparer les données
            data = {
                'nom_entreprise': nom_entreprise,
                'secteur_activite': secteur_activite,
                'taille_entreprise': taille_entreprise,
                'nom_contact': nom_contact,
                'poste_contact': poste_contact,
                'email': email,
                'telephone': telephone,
                'adresse': adresse,
                'ville': ville,
                'code_postal': code_postal,
                'numero_entreprise': numero_entreprise,
                'site_web': site_web,
                'description_entreprise': description_entreprise,
                'mot_de_passe': mot_de_passe,
                'confirmation_mot_de_passe': confirmation_mot_de_passe
            }
            
            # Sauvegarder pour conserver les données en cas d'erreur
            st.session_state.form_data = data
            
            # Validation
            if not conditions_acceptees:
                st.error("❌ Vous devez accepter les conditions d'utilisation")
                return
            
            erreurs = valider_donnees_inscription(data, 'client')
            
            if erreurs:
                st.error("❌ Veuillez corriger les erreurs suivantes :")
                for champ, erreur in erreurs.items():
                    st.error(f"• {erreur}")
                return
            
            try:
                # Sauvegarder la demande
                demande_id = sauvegarder_demande_inscription(data, 'client')
                
                # Succès - marquer pour affichage en dehors du formulaire
                st.session_state.inscription_success = True
                st.session_state.inscription_type = 'client'
                
                # Nettoyer les données du formulaire
                if 'form_data' in st.session_state:
                    del st.session_state.form_data
                
                st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de l'inscription : {str(e)}")
    
    # Afficher le succès en dehors du formulaire
    if st.session_state.get('inscription_success') and st.session_state.get('inscription_type') == 'client':
        st.success("✅ Votre demande d'inscription a été soumise avec succès !")
        st.balloons()
        
        st.info("""
        📧 **Prochaines étapes :**
        1. Vérifiez votre boîte email pour confirmer votre adresse
        2. Un administrateur vérifiera votre demande sous 48h
        3. Vous recevrez une notification par email une fois approuvée
        4. Vous pourrez alors vous connecter et commencer à publier vos projets
        """)
        
        # Bouton retour maintenant en dehors du formulaire
        if st.button("🏠 Retour à l'accueil", key="client_success_home"):
            # Nettoyer les variables de session
            if 'inscription_success' in st.session_state:
                del st.session_state.inscription_success
            if 'inscription_type' in st.session_state:
                del st.session_state.inscription_type
            if 'type_inscription' in st.session_state:
                del st.session_state.type_inscription
            if 'page_inscription' in st.session_state:
                del st.session_state.page_inscription
            st.rerun()

def formulaire_inscription_prestataire():
    """Formulaire d'inscription pour les entreprises prestataires"""
    st.markdown("""
    <div class="demande-card">
        <h2>🔨 Inscription Entreprise Prestataire</h2>
        <p>Rejoignez notre réseau d'entrepreneurs certifiés RBQ</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialiser les données du formulaire
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    with st.form("inscription_prestataire_form"):
        st.markdown("### 🏗️ Informations sur l'entreprise")
        
        col1, col2 = st.columns(2)
        with col1:
            nom_entreprise = st.text_input(
                "Nom de l'entreprise *", 
                value=st.session_state.form_data.get('nom_entreprise', ''),
                help="Raison sociale complète de votre entreprise"
            )
            numero_rbq = st.text_input(
                "Numéro de licence RBQ *", 
                value=st.session_state.form_data.get('numero_rbq', ''),
                placeholder="5678-1234-01",
                help="Numéro de licence valide de la Régie du bâtiment du Québec"
            )
            taille_entreprise = st.selectbox(
                "Taille de l'entreprise *", 
                options=TAILLES_ENTREPRISE,
                index=TAILLES_ENTREPRISE.index(st.session_state.form_data.get('taille_entreprise', TAILLES_ENTREPRISE[0]))
            )
        
        with col2:
            numero_entreprise = st.text_input(
                "Numéro d'entreprise du Québec (NEQ)", 
                value=st.session_state.form_data.get('numero_entreprise', ''),
                help="Numéro d'identification officiel"
            )
            site_web = st.text_input(
                "Site web", 
                value=st.session_state.form_data.get('site_web', ''),
                placeholder="https://www.votreentreprise.com"
            )
        
        # Domaines d'expertise
        st.markdown("### 🎯 Domaines d'expertise")
        domaines_expertise = st.multiselect(
            "Sélectionnez vos domaines d'expertise *",
            options=TYPES_PROJETS,
            default=st.session_state.form_data.get('domaines_expertise', []),
            help="Choisissez tous les types de projets que vous pouvez réaliser"
        )
        
        description_entreprise = st.text_area(
            "Description de l'entreprise et spécialisations",
            value=st.session_state.form_data.get('description_entreprise', ''),
            help="Décrivez votre entreprise, vos spécialisations et votre expérience",
            height=120
        )
        
        st.markdown("### 👤 Contact principal")
        
        col1, col2 = st.columns(2)
        with col1:
            nom_contact = st.text_input(
                "Nom du contact *", 
                value=st.session_state.form_data.get('nom_contact', '')
            )
            email = st.text_input(
                "Adresse email *", 
                value=st.session_state.form_data.get('email', ''),
                help="Cette adresse servira pour la connexion"
            )
        
        with col2:
            poste_contact = st.text_input(
                "Poste/Fonction", 
                value=st.session_state.form_data.get('poste_contact', ''),
                placeholder="Ex: Directeur général, Contremaître"
            )
            telephone = st.text_input(
                "Téléphone *", 
                value=st.session_state.form_data.get('telephone', ''),
                placeholder="514-555-1234"
            )
        
        st.markdown("### 📍 Adresse de l'entreprise")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            adresse = st.text_input(
                "Adresse", 
                value=st.session_state.form_data.get('adresse', '')
            )
        with col2:
            ville = st.text_input(
                "Ville", 
                value=st.session_state.form_data.get('ville', '')
            )
        with col3:
            code_postal = st.text_input(
                "Code postal", 
                value=st.session_state.form_data.get('code_postal', ''),
                placeholder="H1A 1A1"
            )
        
        st.markdown("### 💰 Tarification et zones de service")
        
        col1, col2 = st.columns(2)
        with col1:
            tarif_min = st.number_input(
                "Tarif horaire minimum ($)", 
                min_value=0.0, 
                value=st.session_state.form_data.get('tarif_horaire_min', 50.0),
                step=5.0
            )
            zones_service = st.text_input(
                "Zones de service",
                value=st.session_state.form_data.get('zones_service', ''),
                placeholder="Ex: Montréal, Laval, Rive-Sud",
                help="Zones géographiques que vous desservez"
            )
        
        with col2:
            tarif_max = st.number_input(
                "Tarif horaire maximum ($)", 
                min_value=0.0, 
                value=st.session_state.form_data.get('tarif_horaire_max', 150.0),
                step=5.0
            )
            langues = st.multiselect(
                "Langues parlées",
                options=["Français", "Anglais", "Espagnol", "Italien", "Portugais", "Arabe"],
                default=st.session_state.form_data.get('langues_parlees', ["Français"])
            )
        
        st.markdown("### 🏆 Certifications et qualifications")
        
        certifications_text = st.text_area(
            "Certifications professionnelles",
            value=st.session_state.form_data.get('certifications_text', ''),
            placeholder="Ex: LEED AP, Maître électricien, Soudeur certifié CSA W47.1, Formation CNESST...",
            help="Listez vos certifications, formations et qualifications",
            height=100
        )
        
        st.markdown("### 🔐 Sécurité du compte")
        
        col1, col2 = st.columns(2)
        with col1:
            mot_de_passe = st.text_input(
                "Mot de passe *", 
                type="password",
                help="Minimum 8 caractères"
            )
        with col2:
            confirmation_mot_de_passe = st.text_input(
                "Confirmer le mot de passe *", 
                type="password"
            )
        
        st.markdown("### 📎 Documents requis")
        st.warning("⚠️ **Important :** Les documents suivants seront requis pour valider votre inscription")
        
        # Afficher les documents requis
        docs_requis = obtenir_documents_requis('prestataire')
        if docs_requis:
            for doc in docs_requis:
                required_text = "**OBLIGATOIRE**" if doc['obligatoire'] else "Optionnel"
                formats_text = ", ".join(doc['formats']).upper()
                st.markdown(f"• **{doc['nom']}** ({required_text})")
                st.markdown(f"  - {doc['description']}")
                st.markdown(f"  - Formats acceptés: {formats_text} (max {doc['taille_max']}MB)")
                st.markdown("")
        
        st.info("💡 Vous pourrez télécharger ces documents après validation de votre email")
        
        st.markdown("---")
        
        # Conditions d'utilisation
        conditions_acceptees = st.checkbox(
            "J'accepte les conditions d'utilisation et la politique de confidentialité *",
            help="Vous devez accepter nos conditions pour créer un compte"
        )
        
        certification_rbq = st.checkbox(
            "Je certifie que ma licence RBQ est valide et à jour *",
            help="Votre licence RBQ sera vérifiée lors de l'approbation"
        )
        
        # Bouton de soumission
        submitted = st.form_submit_button(
            "📤 Soumettre ma demande d'inscription",
            use_container_width=True
        )
        
        if submitted:
            # Préparer les données
            data = {
                'nom_entreprise': nom_entreprise,
                'numero_rbq': numero_rbq,
                'taille_entreprise': taille_entreprise,
                'domaines_expertise': json.dumps(domaines_expertise),
                'nom_contact': nom_contact,
                'poste_contact': poste_contact,
                'email': email,
                'telephone': telephone,
                'adresse': adresse,
                'ville': ville,
                'code_postal': code_postal,
                'numero_entreprise': numero_entreprise,
                'site_web': site_web,
                'description_entreprise': description_entreprise,
                'tarif_horaire_min': tarif_min,
                'tarif_horaire_max': tarif_max,
                'zones_service': zones_service,
                'langues_parlees': ', '.join(langues),
                'certifications': json.dumps([cert.strip() for cert in certifications_text.split('\n') if cert.strip()]),
                'mot_de_passe': mot_de_passe,
                'confirmation_mot_de_passe': confirmation_mot_de_passe
            }
            
            # Sauvegarder pour conserver les données en cas d'erreur
            st.session_state.form_data = data
            
            # Validation
            if not conditions_acceptees:
                st.error("❌ Vous devez accepter les conditions d'utilisation")
                return
            
            if not certification_rbq:
                st.error("❌ Vous devez certifier que votre licence RBQ est valide")
                return
            
            erreurs = valider_donnees_inscription(data, 'prestataire')
            
            if erreurs:
                st.error("❌ Veuillez corriger les erreurs suivantes :")
                for champ, erreur in erreurs.items():
                    st.error(f"• {erreur}")
                return
            
            try:
                # Sauvegarder la demande
                demande_id = sauvegarder_demande_inscription(data, 'prestataire')
                
                # Succès - marquer pour affichage en dehors du formulaire
                st.session_state.inscription_success = True
                st.session_state.inscription_type = 'prestataire'
                
                # Nettoyer les données du formulaire
                if 'form_data' in st.session_state:
                    del st.session_state.form_data
                
                st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de l'inscription : {str(e)}")
    
    # Afficher le succès en dehors du formulaire pour prestataire
    if st.session_state.get('inscription_success') and st.session_state.get('inscription_type') == 'prestataire':
        st.success("✅ Votre demande d'inscription a été soumise avec succès !")
        st.balloons()
        
        st.info("""
        📧 **Prochaines étapes :**
        1. Vérifiez votre boîte email pour confirmer votre adresse
        2. Préparez vos documents (licence RBQ, assurances, etc.)
        3. Un administrateur vérifiera votre demande et documents sous 48h
        4. Votre licence RBQ sera validée auprès de la Régie du bâtiment
        5. Vous recevrez une notification par email une fois approuvé
        6. Vous pourrez alors vous connecter et commencer à soumissionner
        """)
        
        # Bouton retour maintenant en dehors du formulaire
        if st.button("🏠 Retour à l'accueil", key="prestataire_success_home"):
            # Nettoyer les variables de session
            if 'inscription_success' in st.session_state:
                del st.session_state.inscription_success
            if 'inscription_type' in st.session_state:
                del st.session_state.inscription_type
            if 'type_inscription' in st.session_state:
                del st.session_state.type_inscription
            if 'page_inscription' in st.session_state:
                del st.session_state.page_inscription
            st.rerun()

def router_inscription():
    """Router principal pour les pages d'inscription"""
    # Initialiser les variables de session si nécessaire
    if 'type_inscription' not in st.session_state:
        st.session_state.type_inscription = None
    
    if 'page_inscription' not in st.session_state:
        st.session_state.page_inscription = "selection"
    
    # Bouton retour en haut
    if st.session_state.get('type_inscription') or st.session_state.get('page_inscription') != "selection":
        if st.button("← Retour", key="btn_retour_inscription"):
            if st.session_state.page_inscription == "formulaire":
                st.session_state.page_inscription = "selection"
                st.session_state.type_inscription = None
            else:
                # Retour complet à l'accueil
                for key in ['type_inscription', 'page_inscription', 'form_data']:
                    if key in st.session_state:
                        del st.session_state[key]
            st.rerun()
    
    # Afficher la page appropriée
    if st.session_state.page_inscription == "selection":
        page_selection_inscription()
    elif st.session_state.page_inscription == "formulaire":
        if st.session_state.type_inscription == "client":
            formulaire_inscription_client()
        elif st.session_state.type_inscription == "prestataire":
            formulaire_inscription_prestataire()
        else:
            st.error("Type d'inscription non reconnu")
            st.session_state.page_inscription = "selection"
            st.rerun()