# Intégration du système d'inscription dans l'application principale
# Ce fichier contient les modifications nécessaires pour app.py

"""
INSTRUCTIONS D'INTÉGRATION :

1. Ajouter ces imports au début de app.py (après les imports existants) :
"""

# Nouveaux imports à ajouter dans app.py
additional_imports = """
# Système d'inscription
from inscription_system import *
from pages_inscription import router_inscription
from admin_inscriptions import router_admin_inscriptions
"""

"""
2. Modifier la fonction main() pour ajouter le bouton d'inscription :
"""

def main_modified():
    """Version modifiée de la fonction main() avec système d'inscription"""
    
    # Initialiser les tables d'inscription
    try:
        init_inscription_tables()
    except:
        pass  # Tables déjà créées
    
    init_database()
    
    # Header principal avec bouton inscription
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <div class="main-header">
            <h1>🏗️ Le B2B de la Construction au Québec</h1>
            <p>Plateforme d'approbation de soumissions construction avec workflow intelligent</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Bouton d'inscription visible seulement si pas connecté
        if st.session_state.get('user_type') is None:
            if st.button("✨ S'inscrire", use_container_width=True, type="primary"):
                st.session_state.page = 'inscription'
                st.rerun()
    
    # Initialiser les états de session
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'page' not in st.session_state:
        st.session_state.page = 'accueil'
    
    # Router principal de l'application
    if st.session_state.page == 'inscription':
        router_inscription()
        return
    
    # Menu de navigation dans la sidebar (reste identique)
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1E40AF/FFFFFF?text=B2B+Construction+Quebec", width=200)
        
        if st.session_state.user_type is None:
            # Menu pour utilisateurs non connectés
            st.markdown("### 🔐 Connexion")
            
            # Lien vers inscription
            if st.button("📝 Créer un compte", use_container_width=True):
                st.session_state.page = 'inscription'
                st.rerun()
            
            st.markdown("---")
            
            user_type_choice = st.selectbox(
                "Type de compte",
                ["", "Entreprise Cliente", "Entreprise Prestataire", "Administrateur"],
                key="user_type_selector"
            )
            
            if user_type_choice:
                show_login_form(user_type_choice)
        
        else:
            # Menu pour utilisateurs connectés
            user_name = st.session_state.user_data.nom_entreprise if hasattr(st.session_state.user_data, 'nom_entreprise') else "Administrateur"
            st.markdown(f"### 👋 Bonjour, {user_name}")
            st.markdown(f"**Rôle:** {st.session_state.user_type}")
            
            # Menu de navigation selon le rôle
            if st.session_state.user_type == "Entreprise Cliente":
                menu_client()
            elif st.session_state.user_type == "Entreprise Prestataire":
                menu_prestataire()
            elif st.session_state.user_type == "Administrateur":
                menu_admin()
            
            # Bouton de déconnexion
            st.markdown("---")
            if st.button("🚪 Se déconnecter", use_container_width=True):
                for key in ['user_type', 'user_data', 'page']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    # Contenu principal selon la page
    if st.session_state.user_type is None:
        page_accueil()
    else:
        if st.session_state.user_type == "Entreprise Cliente":
            router_client()
        elif st.session_state.user_type == "Entreprise Prestataire":
            router_prestataire()
        elif st.session_state.user_type == "Administrateur":
            router_admin()

"""
3. Modifier la fonction menu_admin() pour ajouter la gestion des inscriptions :
"""

def menu_admin_modified():
    """Version modifiée du menu admin avec gestion des inscriptions"""
    st.markdown("### ⚙️ Administration")
    
    # Obtenir le nombre de demandes en attente
    try:
        stats = obtenir_statistiques_inscriptions()
        demandes_attente = stats.get('en_attente', 0)
        badge_text = f" ({demandes_attente})" if demandes_attente > 0 else ""
    except:
        badge_text = ""
    
    if st.button(f"👥 Gestion des inscriptions{badge_text}", use_container_width=True):
        st.session_state.page = 'admin_inscriptions'
        st.rerun()
    
    if st.button("📋 Gestion des demandes", use_container_width=True):
        st.session_state.page = 'admin_demandes'
        st.rerun()
    
    if st.button("📄 Gestion des soumissions", use_container_width=True):
        st.session_state.page = 'admin_soumissions'
        st.rerun()
    
    if st.button("🔄 Gestion du workflow", use_container_width=True):
        st.session_state.page = 'admin_workflow'
        st.rerun()
    
    if st.button("🏢 Gestion des entreprises", use_container_width=True):
        st.session_state.page = 'admin_entreprises'
        st.rerun()
    
    if st.button("📊 Rapports et analytics", use_container_width=True):
        st.session_state.page = 'admin_rapports'
        st.rerun()
    
    if st.button("⚙️ Paramètres système", use_container_width=True):
        st.session_state.page = 'admin_parametres'
        st.rerun()

"""
4. Modifier la fonction router_admin() pour inclure la gestion des inscriptions :
"""

def router_admin_modified():
    """Version modifiée du router admin avec gestion des inscriptions"""
    page = st.session_state.get('page', 'admin_demandes')
    
    if page == 'admin_inscriptions':
        router_admin_inscriptions()
    elif page == 'admin_demandes':
        page_admin_demandes()
    elif page == 'admin_soumissions':
        page_admin_soumissions()
    elif page == 'admin_workflow':
        page_admin_workflow()
    elif page == 'admin_entreprises':
        page_admin_entreprises()
    elif page == 'admin_rapports':
        page_admin_rapports()
    elif page == 'admin_parametres':
        page_admin_parametres()
    else:
        st.error(f"Page admin inconnue: {page}")
        st.session_state.page = 'admin_demandes'
        st.rerun()

"""
5. Ajouter ces nouvelles configurations dans config_approbation.py :
"""

config_inscription = """
# Ajout dans config_approbation.py

# Statuts des demandes d'inscription
STATUTS_INSCRIPTION = {
    "en_attente": "⏳ En attente",
    "en_verification": "🔍 En vérification", 
    "approuvee": "✅ Approuvée",
    "rejetee": "❌ Rejetée",
    "incomplete": "⚠️ Incomplète"
}

# Messages système pour inscription
MESSAGES_INSCRIPTION = {
    "demande_soumise": "Votre demande d'inscription a été soumise avec succès",
    "email_verification": "Veuillez vérifier votre email pour confirmer votre adresse",
    "en_attente_approbation": "Votre demande est en cours d'examen par nos équipes",
    "approuvee": "Félicitations ! Votre inscription a été approuvée",
    "rejetee": "Désolé, votre demande d'inscription a été rejetée",
    "documents_requis": "Des documents supplémentaires sont requis"
}

# Configuration des notifications d'inscription
NOTIFICATIONS_INSCRIPTION = {
    "nouvelle_demande_admin": "Nouvelle demande d'inscription à examiner",
    "demande_approuvee_user": "Votre inscription a été approuvée",
    "demande_rejetee_user": "Votre inscription a été rejetée",
    "documents_manquants": "Documents manquants pour votre inscription"
}
"""

"""
6. Instructions d'installation :

Étape 1: Sauvegarder votre app.py actuel
Étape 2: Ajouter les imports au début de app.py
Étape 3: Remplacer la fonction main() par main_modified()
Étape 4: Remplacer menu_admin() par menu_admin_modified()
Étape 5: Remplacer router_admin() par router_admin_modified()
Étape 6: Ajouter les configurations dans config_approbation.py

Étape 7: Initialiser les nouvelles tables
python inscription_system.py

Étape 8: Tester l'application
streamlit run app.py
"""

# Code complet d'intégration prêt à copier
integration_complete = """
# INTÉGRATION COMPLÈTE POUR APP.PY

# 1. Ajouter ces imports après les imports existants
from inscription_system import *
from pages_inscription import router_inscription
from admin_inscriptions import router_admin_inscriptions

# 2. Remplacer la fonction main() existante par celle-ci :
def main():
    # Initialiser les tables d'inscription
    try:
        init_inscription_tables()
    except:
        pass
    
    init_database()
    
    # Header principal avec bouton inscription
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('''
        <div class="main-header">
            <h1>🏗️ Le B2B de la Construction au Québec</h1>
            <p>Plateforme d'approbation de soumissions construction avec workflow intelligent</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.get('user_type') is None:
            if st.button("✨ S'inscrire", use_container_width=True, type="primary"):
                st.session_state.page = 'inscription'
                st.rerun()
    
    # Initialiser les états de session
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'page' not in st.session_state:
        st.session_state.page = 'accueil'
    
    # Router principal
    if st.session_state.page == 'inscription':
        router_inscription()
        return
    
    # Menu de navigation dans la sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1E40AF/FFFFFF?text=B2B+Construction+Quebec", width=200)
        
        if st.session_state.user_type is None:
            st.markdown("### 🔐 Connexion")
            
            if st.button("📝 Créer un compte", use_container_width=True):
                st.session_state.page = 'inscription'
                st.rerun()
            
            st.markdown("---")
            
            user_type_choice = st.selectbox(
                "Type de compte",
                ["", "Entreprise Cliente", "Entreprise Prestataire", "Administrateur"],
                key="user_type_selector"
            )
            
            if user_type_choice:
                show_login_form(user_type_choice)
        
        else:
            user_name = st.session_state.user_data.nom_entreprise if hasattr(st.session_state.user_data, 'nom_entreprise') else "Administrateur"
            st.markdown(f"### 👋 Bonjour, {user_name}")
            st.markdown(f"**Rôle:** {st.session_state.user_type}")
            
            if st.session_state.user_type == "Entreprise Cliente":
                menu_client()
            elif st.session_state.user_type == "Entreprise Prestataire":
                menu_prestataire()
            elif st.session_state.user_type == "Administrateur":
                menu_admin()
            
            st.markdown("---")
            if st.button("🚪 Se déconnecter", use_container_width=True):
                for key in ['user_type', 'user_data', 'page']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    # Contenu principal
    if st.session_state.user_type is None:
        page_accueil()
    else:
        if st.session_state.user_type == "Entreprise Cliente":
            router_client()
        elif st.session_state.user_type == "Entreprise Prestataire":
            router_prestataire()
        elif st.session_state.user_type == "Administrateur":
            router_admin()

# 3. Modifier menu_admin() pour ajouter :
def menu_admin():
    st.markdown("### ⚙️ Administration")
    
    try:
        stats = obtenir_statistiques_inscriptions()
        demandes_attente = stats.get('en_attente', 0)
        badge_text = f" ({demandes_attente})" if demandes_attente > 0 else ""
    except:
        badge_text = ""
    
    if st.button(f"👥 Gestion des inscriptions{badge_text}", use_container_width=True):
        st.session_state.page = 'admin_inscriptions'
        st.rerun()
    
    # ... reste du menu existant

# 4. Modifier router_admin() pour ajouter :
def router_admin():
    page = st.session_state.get('page', 'admin_demandes')
    
    if page == 'admin_inscriptions':
        router_admin_inscriptions()
    elif page == 'admin_demandes':
        page_admin_demandes()
    # ... reste du router existant
"""

if __name__ == "__main__":
    print("📋 Instructions d'intégration du système d'inscription")
    print("="*60)
    print("\n1. Sauvegarder votre app.py actuel")
    print("2. Ajouter les imports nécessaires")
    print("3. Modifier les fonctions main(), menu_admin(), router_admin()")
    print("4. Ajouter les configurations dans config_approbation.py") 
    print("5. Initialiser les tables: python inscription_system.py")
    print("6. Tester: streamlit run app.py")
    print("\n✅ Tous les fichiers nécessaires ont été créés !")
    print("   - inscription_system.py")
    print("   - pages_inscription.py") 
    print("   - admin_inscriptions.py")
    print("   - app_inscription_integration.py")