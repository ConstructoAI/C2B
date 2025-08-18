# Interface administrateur pour gérer les inscriptions
# Approbation, rejet et suivi des demandes

import streamlit as st
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from inscription_system import *
from config_approbation import *

def get_database_connection():
    """Retourne une connexion à la base de données"""
    DATA_DIR = os.getenv('DATA_DIR', os.path.join(os.getcwd(), 'data'))
    DATABASE_PATH = os.path.join(DATA_DIR, DATABASE_FILE)
    return sqlite3.connect(DATABASE_PATH)

def obtenir_statistiques_inscriptions() -> Dict[str, int]:
    """Obtient les statistiques des inscriptions"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Total des demandes
    cursor.execute('SELECT COUNT(*) FROM demandes_inscription')
    stats['total'] = cursor.fetchone()[0]
    
    # Par statut
    for statut in ['en_attente', 'en_verification', 'approuvee', 'rejetee']:
        cursor.execute('SELECT COUNT(*) FROM demandes_inscription WHERE statut = ?', (statut,))
        stats[statut] = cursor.fetchone()[0]
    
    # Par type
    for type_ent in ['client', 'prestataire']:
        cursor.execute('SELECT COUNT(*) FROM demandes_inscription WHERE type_entreprise = ?', (type_ent,))
        stats[f'type_{type_ent}'] = cursor.fetchone()[0]
    
    # Dernières 24h
    hier = datetime.now() - timedelta(days=1)
    cursor.execute('SELECT COUNT(*) FROM demandes_inscription WHERE date_demande > ?', (hier,))
    stats['dernieres_24h'] = cursor.fetchone()[0]
    
    conn.close()
    return stats

def obtenir_demandes_inscription(statut: str = None, type_entreprise: str = None) -> List[Dict]:
    """Obtient la liste des demandes d'inscription avec filtres optionnels"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT id, type_entreprise, nom_entreprise, nom_contact, email, telephone,
               numero_rbq, statut, date_demande, date_verification, date_decision,
               evaluateur_admin_id, commentaires_admin
        FROM demandes_inscription
        WHERE 1=1
    '''
    params = []
    
    if statut:
        query += ' AND statut = ?'
        params.append(statut)
    
    if type_entreprise:
        query += ' AND type_entreprise = ?'
        params.append(type_entreprise)
    
    query += ' ORDER BY date_demande DESC'
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    demandes = []
    for row in results:
        demandes.append({
            'id': row[0],
            'type_entreprise': row[1],
            'nom_entreprise': row[2],
            'nom_contact': row[3],
            'email': row[4],
            'telephone': row[5],
            'numero_rbq': row[6],
            'statut': row[7],
            'date_demande': row[8],
            'date_verification': row[9],
            'date_decision': row[10],
            'evaluateur_admin_id': row[11],
            'commentaires_admin': row[12]
        })
    
    conn.close()
    return demandes

def obtenir_detail_demande(demande_id: int) -> Dict[str, Any]:
    """Obtient les détails complets d'une demande d'inscription"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM demandes_inscription WHERE id = ?', (demande_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    # Obtenir les colonnes
    columns = [desc[0] for desc in cursor.description]
    demande = dict(zip(columns, row))
    
    # Obtenir l'historique
    cursor.execute('''
        SELECT ancien_statut, nouveau_statut, commentaire, date_changement, utilisateur_type
        FROM historique_inscription 
        WHERE demande_inscription_id = ? 
        ORDER BY date_changement DESC
    ''', (demande_id,))
    
    historique = []
    for hist_row in cursor.fetchall():
        historique.append({
            'ancien_statut': hist_row[0],
            'nouveau_statut': hist_row[1],
            'commentaire': hist_row[2],
            'date_changement': hist_row[3],
            'utilisateur_type': hist_row[4]
        })
    
    demande['historique'] = historique
    
    conn.close()
    return demande

def mettre_a_jour_statut_demande(demande_id: int, nouveau_statut: str, commentaires: str = "", utilisateur_id: int = None):
    """Met à jour le statut d'une demande d'inscription"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Obtenir le statut actuel
    cursor.execute('SELECT statut FROM demandes_inscription WHERE id = ?', (demande_id,))
    ancien_statut = cursor.fetchone()[0]
    
    # Mettre à jour la demande
    if nouveau_statut in ['approuvee', 'rejetee']:
        cursor.execute('''
            UPDATE demandes_inscription 
            SET statut = ?, date_decision = ?, evaluateur_admin_id = ?, commentaires_admin = ?
            WHERE id = ?
        ''', (nouveau_statut, datetime.now(), utilisateur_id, commentaires, demande_id))
    else:
        cursor.execute('''
            UPDATE demandes_inscription 
            SET statut = ?, date_verification = ?, evaluateur_admin_id = ?, commentaires_admin = ?
            WHERE id = ?
        ''', (nouveau_statut, datetime.now(), utilisateur_id, commentaires, demande_id))
    
    # Ajouter à l'historique
    cursor.execute('''
        INSERT INTO historique_inscription 
        (demande_inscription_id, ancien_statut, nouveau_statut, commentaire, utilisateur_type)
        VALUES (?, ?, ?, ?, 'admin')
    ''', (demande_id, ancien_statut, nouveau_statut, commentaires))
    
    conn.commit()
    conn.close()

def approuver_demande_inscription(demande_id: int, commentaires: str = ""):
    """Approuve une demande d'inscription et crée le compte entreprise"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Obtenir les détails de la demande
    demande = obtenir_detail_demande(demande_id)
    
    if not demande or demande['statut'] == 'approuvee':
        conn.close()
        return False, "Demande introuvable ou déjà approuvée"
    
    try:
        # Créer le compte entreprise selon le type
        if demande['type_entreprise'] == 'client':
            cursor.execute('''
                INSERT INTO entreprises_clientes (
                    nom_entreprise, secteur_activite, taille_entreprise, nom_contact,
                    poste_contact, email, telephone, adresse, ville, code_postal,
                    mot_de_passe_hash, numero_entreprise, site_web, description_entreprise,
                    statut, date_inscription
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'actif', ?)
            ''', (
                demande['nom_entreprise'], demande['secteur_activite'], demande['taille_entreprise'],
                demande['nom_contact'], demande['poste_contact'], demande['email'],
                demande['telephone'], demande['adresse'], demande['ville'], demande['code_postal'],
                demande['mot_de_passe_hash'], demande['numero_entreprise'], demande['site_web'],
                demande['description_entreprise'], datetime.now()
            ))
        
        else:  # prestataire
            cursor.execute('''
                INSERT INTO entreprises_prestataires (
                    nom_entreprise, domaines_expertise, taille_entreprise, nom_contact,
                    poste_contact, email, telephone, adresse, ville, code_postal,
                    mot_de_passe_hash, numero_entreprise, site_web, description_entreprise,
                    certifications, tarif_horaire_min, tarif_horaire_max, zones_service,
                    langues_parlees, statut, date_inscription
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'actif', ?)
            ''', (
                demande['nom_entreprise'], demande['domaines_expertise'], demande['taille_entreprise'],
                demande['nom_contact'], demande['poste_contact'], demande['email'],
                demande['telephone'], demande['adresse'], demande['ville'], demande['code_postal'],
                demande['mot_de_passe_hash'], demande['numero_entreprise'], demande['site_web'],
                demande['description_entreprise'], demande['certifications'],
                demande['tarif_horaire_min'], demande['tarif_horaire_max'],
                demande['zones_service'], demande['langues_parlees'], datetime.now()
            ))
        
        # Mettre à jour le statut de la demande
        mettre_a_jour_statut_demande(demande_id, 'approuvee', commentaires)
        
        conn.commit()
        conn.close()
        
        return True, "Demande approuvée et compte créé avec succès"
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erreur lors de l'approbation : {str(e)}"

def page_admin_inscriptions():
    """Page principale de gestion des inscriptions pour l'admin"""
    st.markdown("""
    <div class="main-header">
        <h1>👥 Gestion des Inscriptions</h1>
        <p>Approuver et gérer les demandes d'inscription des entreprises</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistiques
    stats = obtenir_statistiques_inscriptions()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total demandes", 
            stats['total'],
            delta=f"+{stats['dernieres_24h']} (24h)"
        )
    
    with col2:
        st.metric(
            "En attente", 
            stats['en_attente'],
            delta="À traiter"
        )
    
    with col3:
        st.metric(
            "Approuvées", 
            stats['approuvee']
        )
    
    with col4:
        st.metric(
            "Rejetées", 
            stats['rejetee']
        )
    
    st.markdown("---")
    
    # Filtres
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        filtre_statut = st.selectbox(
            "Filtrer par statut",
            options=["Tous", "en_attente", "en_verification", "approuvee", "rejetee"],
            index=1  # Par défaut "en_attente"
        )
    
    with col2:
        filtre_type = st.selectbox(
            "Filtrer par type",
            options=["Tous", "client", "prestataire"]
        )
    
    with col3:
        if st.button("🔄 Actualiser", use_container_width=True):
            st.rerun()
    
    # Obtenir les demandes avec filtres
    statut_filtre = None if filtre_statut == "Tous" else filtre_statut
    type_filtre = None if filtre_type == "Tous" else filtre_type
    
    demandes = obtenir_demandes_inscription(statut_filtre, type_filtre)
    
    if not demandes:
        st.info("📭 Aucune demande d'inscription trouvée avec ces critères")
        return
    
    # Liste des demandes
    st.markdown("### 📋 Liste des demandes")
    
    for demande in demandes:
        with st.expander(
            f"{'🏢' if demande['type_entreprise'] == 'client' else '🔨'} "
            f"{demande['nom_entreprise']} - {demande['nom_contact']} "
            f"({demande['statut'].replace('_', ' ').title()})",
            expanded=(demande['statut'] == 'en_attente')
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Email :** {demande['email']}")
                st.markdown(f"**Téléphone :** {demande['telephone']}")
                st.markdown(f"**Type :** {'Entreprise Cliente' if demande['type_entreprise'] == 'client' else 'Entrepreneur Prestataire'}")
                if demande['numero_rbq']:
                    st.markdown(f"**Licence RBQ :** {demande['numero_rbq']}")
                st.markdown(f"**Date de demande :** {demande['date_demande']}")
                
                if demande['commentaires_admin']:
                    st.markdown(f"**Commentaires admin :** {demande['commentaires_admin']}")
            
            with col2:
                # Badge de statut
                if demande['statut'] == 'en_attente':
                    st.markdown("🟡 **En attente**")
                elif demande['statut'] == 'en_verification':
                    st.markdown("🔵 **En vérification**")
                elif demande['statut'] == 'approuvee':
                    st.markdown("🟢 **Approuvée**")
                elif demande['statut'] == 'rejetee':
                    st.markdown("🔴 **Rejetée**")
                
                # Actions
                if demande['statut'] in ['en_attente', 'en_verification']:
                    if st.button(
                        "📋 Examiner", 
                        key=f"examiner_{demande['id']}",
                        use_container_width=True
                    ):
                        st.session_state.demande_selectionnee = demande['id']
                        st.session_state.page_admin = 'detail_inscription'
                        st.rerun()

def page_detail_inscription():
    """Page de détail d'une demande d'inscription"""
    if 'demande_selectionnee' not in st.session_state:
        st.error("Aucune demande sélectionnée")
        return
    
    demande_id = st.session_state.demande_selectionnee
    demande = obtenir_detail_demande(demande_id)
    
    if not demande:
        st.error("Demande introuvable")
        return
    
    # Header avec retour
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Retour à la liste"):
            st.session_state.page_admin = 'inscriptions'
            if 'demande_selectionnee' in st.session_state:
                del st.session_state.demande_selectionnee
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div class="main-header">
            <h2>{'🏢' if demande['type_entreprise'] == 'client' else '🔨'} {demande['nom_entreprise']}</h2>
            <p>Demande d'inscription #{demande['id']} - {demande['statut'].replace('_', ' ').title()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Informations détaillées
    tab1, tab2, tab3 = st.tabs(["📝 Détails", "📎 Documents", "📊 Historique"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏢 Informations entreprise")
            st.markdown(f"**Nom :** {demande['nom_entreprise']}")
            st.markdown(f"**Type :** {'Entreprise Cliente' if demande['type_entreprise'] == 'client' else 'Entrepreneur Prestataire'}")
            st.markdown(f"**Taille :** {demande['taille_entreprise']}")
            
            if demande['secteur_activite']:
                st.markdown(f"**Secteur :** {demande['secteur_activite']}")
            
            if demande['domaines_expertise']:
                try:
                    domaines = json.loads(demande['domaines_expertise'])
                    st.markdown(f"**Domaines d'expertise :** {', '.join(domaines)}")
                except:
                    st.markdown(f"**Domaines d'expertise :** {demande['domaines_expertise']}")
            
            if demande['numero_entreprise']:
                st.markdown(f"**NEQ :** {demande['numero_entreprise']}")
            
            if demande['numero_rbq']:
                st.markdown(f"**Licence RBQ :** {demande['numero_rbq']}")
            
            if demande['site_web']:
                st.markdown(f"**Site web :** {demande['site_web']}")
            
            if demande['description_entreprise']:
                st.markdown("**Description :**")
                st.markdown(demande['description_entreprise'])
        
        with col2:
            st.markdown("### 👤 Contact")
            st.markdown(f"**Nom :** {demande['nom_contact']}")
            if demande['poste_contact']:
                st.markdown(f"**Poste :** {demande['poste_contact']}")
            st.markdown(f"**Email :** {demande['email']}")
            st.markdown(f"**Téléphone :** {demande['telephone']}")
            
            if any([demande['adresse'], demande['ville'], demande['code_postal']]):
                st.markdown("### 📍 Adresse")
                if demande['adresse']:
                    st.markdown(f"**Adresse :** {demande['adresse']}")
                if demande['ville']:
                    st.markdown(f"**Ville :** {demande['ville']}")
                if demande['code_postal']:
                    st.markdown(f"**Code postal :** {demande['code_postal']}")
            
            if demande['type_entreprise'] == 'prestataire':
                st.markdown("### 💰 Tarification")
                if demande['tarif_horaire_min'] or demande['tarif_horaire_max']:
                    st.markdown(f"**Tarifs :** {demande['tarif_horaire_min']}$ - {demande['tarif_horaire_max']}$ / heure")
                
                if demande['zones_service']:
                    st.markdown(f"**Zones de service :** {demande['zones_service']}")
                
                if demande['langues_parlees']:
                    st.markdown(f"**Langues :** {demande['langues_parlees']}")
                
                if demande['certifications']:
                    try:
                        certs = json.loads(demande['certifications'])
                        if certs:
                            st.markdown("**Certifications :**")
                            for cert in certs:
                                st.markdown(f"• {cert}")
                    except:
                        st.markdown(f"**Certifications :** {demande['certifications']}")
    
    with tab2:
        st.markdown("### 📎 Documents requis")
        
        docs_requis = obtenir_documents_requis(demande['type_entreprise'])
        
        if docs_requis:
            for doc in docs_requis:
                required_text = "**OBLIGATOIRE**" if doc['obligatoire'] else "Optionnel"
                st.markdown(f"**{doc['nom']}** ({required_text})")
                st.markdown(f"• {doc['description']}")
                
                # Ici on pourrait ajouter la gestion des documents uploadés
                # Pour l'instant, on indique que c'est en développement
                st.info("📄 Système de validation des documents en cours de développement")
                st.markdown("---")
        else:
            st.info("Aucun document spécifique requis")
    
    with tab3:
        st.markdown("### 📊 Historique des changements")
        
        if demande['historique']:
            for hist in demande['historique']:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if hist['ancien_statut']:
                            st.markdown(f"**{hist['ancien_statut']}** → **{hist['nouveau_statut']}**")
                        else:
                            st.markdown(f"**{hist['nouveau_statut']}**")
                        
                        if hist['commentaire']:
                            st.markdown(f"*{hist['commentaire']}*")
                    
                    with col2:
                        st.markdown(f"📅 {hist['date_changement']}")
                        st.markdown(f"👤 {hist['utilisateur_type']}")
                    
                    st.markdown("---")
        else:
            st.info("Aucun historique disponible")
    
    # Actions d'approbation/rejet
    if demande['statut'] in ['en_attente', 'en_verification']:
        st.markdown("---")
        st.markdown("### ⚡ Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Approuver", use_container_width=True, type="primary"):
                st.session_state.action_demande = 'approuver'
        
        with col2:
            if st.button("❌ Rejeter", use_container_width=True):
                st.session_state.action_demande = 'rejeter'
        
        with col3:
            if st.button("🔍 Mettre en vérification", use_container_width=True):
                st.session_state.action_demande = 'verification'
        
        # Formulaire d'action
        if 'action_demande' in st.session_state:
            action = st.session_state.action_demande
            
            with st.form(f"form_action_{action}"):
                if action == 'approuver':
                    st.success("✅ Approuver cette demande d'inscription")
                    st.markdown("Un compte sera automatiquement créé pour cette entreprise.")
                elif action == 'rejeter':
                    st.error("❌ Rejeter cette demande d'inscription")
                elif action == 'verification':
                    st.info("🔍 Mettre en vérification")
                
                commentaires = st.text_area(
                    "Commentaires (optionnel)",
                    placeholder="Ajoutez des commentaires sur votre décision..."
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Confirmer", use_container_width=True):
                        if action == 'approuver':
                            success, message = approuver_demande_inscription(demande_id, commentaires)
                            if success:
                                st.success(f"✅ {message}")
                                st.balloons()
                                # Retour à la liste après approbation
                                st.session_state.page_admin = 'inscriptions'
                                if 'demande_selectionnee' in st.session_state:
                                    del st.session_state.demande_selectionnee
                                if 'action_demande' in st.session_state:
                                    del st.session_state.action_demande
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        
                        elif action == 'rejeter':
                            mettre_a_jour_statut_demande(demande_id, 'rejetee', commentaires)
                            st.success("✅ Demande rejetée")
                            st.session_state.page_admin = 'inscriptions'
                            if 'demande_selectionnee' in st.session_state:
                                del st.session_state.demande_selectionnee
                            if 'action_demande' in st.session_state:
                                del st.session_state.action_demande
                            st.rerun()
                        
                        elif action == 'verification':
                            mettre_a_jour_statut_demande(demande_id, 'en_verification', commentaires)
                            st.success("✅ Demande mise en vérification")
                            if 'action_demande' in st.session_state:
                                del st.session_state.action_demande
                            st.rerun()
                
                with col2:
                    if st.form_submit_button("Annuler", use_container_width=True):
                        if 'action_demande' in st.session_state:
                            del st.session_state.action_demande
                        st.rerun()

def router_admin_inscriptions():
    """Router pour les pages d'administration des inscriptions"""
    # Initialiser la page admin si nécessaire
    if 'page_admin' not in st.session_state:
        st.session_state.page_admin = 'inscriptions'
    
    # Router vers la bonne page
    if st.session_state.page_admin == 'inscriptions':
        page_admin_inscriptions()
    elif st.session_state.page_admin == 'detail_inscription':
        page_detail_inscription()
    else:
        st.error("Page admin inconnue")
        st.session_state.page_admin = 'inscriptions'
        st.rerun()