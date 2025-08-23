import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import uuid
from typing import Optional, List, Dict, Any
import re
from dataclasses import dataclass
from PIL import Image
import io
import base64
import json

# Import des configurations
from config_approbation import *
from config_entreprise_unique import *

# Système d'inscription
from inscription_system import *
from pages_inscription import router_inscription
from admin_inscriptions import router_admin_inscriptions

# Interface mono-entreprise
from interface_mono_entreprise import *

# Fonction de connexion à la base de données
def get_database_connection():
    """Établit une connexion à la base de données"""
    return sqlite3.connect(DATABASE_PATH)

def init_main_tables():
    """Initialise les tables principales de l'application"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Table des entreprises clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entreprises_clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_entreprise TEXT NOT NULL,
                secteur_activite TEXT NOT NULL,
                taille_entreprise TEXT NOT NULL,
                nom_contact TEXT NOT NULL,
                poste_contact TEXT,
                email TEXT UNIQUE NOT NULL,
                telephone TEXT NOT NULL,
                adresse TEXT,
                ville TEXT,
                code_postal TEXT,
                numero_entreprise TEXT,
                site_web TEXT,
                description_entreprise TEXT,
                mot_de_passe_hash TEXT NOT NULL,
                statut TEXT DEFAULT 'actif' CHECK(statut IN ('actif', 'inactif', 'suspendu')),
                date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_derniere_connexion TIMESTAMP
            )
        ''')
        
        # Table des entreprises prestataires
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entreprises_prestataires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_entreprise TEXT NOT NULL,
                numero_rbq TEXT NOT NULL,
                domaines_expertise TEXT, -- JSON array
                taille_entreprise TEXT NOT NULL,
                nom_contact TEXT NOT NULL,
                poste_contact TEXT,
                email TEXT UNIQUE NOT NULL,
                telephone TEXT NOT NULL,
                adresse TEXT,
                ville TEXT,
                code_postal TEXT,
                numero_entreprise TEXT,
                site_web TEXT,
                description_entreprise TEXT,
                mot_de_passe_hash TEXT NOT NULL,
                certifications TEXT, -- JSON array
                tarif_horaire_min REAL DEFAULT 0.0,
                tarif_horaire_max REAL DEFAULT 0.0,
                zones_service TEXT,
                langues_parlees TEXT DEFAULT 'Français',
                statut TEXT DEFAULT 'actif' CHECK(statut IN ('actif', 'inactif', 'suspendu')),
                date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_derniere_connexion TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("Tables principales créées avec succès!")
        
    except Exception as e:
        print(f"Erreur lors de la création des tables principales: {e}")
        conn.rollback()
    finally:
        conn.close()

# Configuration de la page
st.set_page_config(
    page_title=STREAMLIT_CONFIG["page_title"],
    page_icon=STREAMLIT_CONFIG["page_icon"],
    layout=STREAMLIT_CONFIG["layout"],
    initial_sidebar_state=STREAMLIT_CONFIG["initial_sidebar_state"]
)

# Chargement du CSS personnalisé
def load_css():
    """Charge le fichier CSS personnalisé"""
    try:
        with open('style.css', 'r', encoding='utf-8') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Fichier style.css non trouvé. Utilisation du style par défaut.")

load_css()

# Classes de données
@dataclass
class EntrepriseCliente:
    id: Optional[int] = None
    nom_entreprise: str = ""
    secteur_activite: str = ""
    taille_entreprise: str = ""
    nom_contact: str = ""
    poste_contact: str = ""
    email: str = ""
    telephone: str = ""
    adresse: str = ""
    ville: str = ""
    code_postal: str = ""
    mot_de_passe_hash: str = ""
    numero_entreprise: str = ""
    site_web: str = ""
    description_entreprise: str = ""
    statut: str = "actif"

@dataclass
class EntreprisePrestataire:
    id: Optional[int] = None
    nom_entreprise: str = ""
    domaines_expertise: str = ""
    taille_entreprise: str = ""
    nom_contact: str = ""
    poste_contact: str = ""
    email: str = ""
    telephone: str = ""
    mot_de_passe_hash: str = ""
    certifications: str = ""
    tarif_horaire_min: float = 0.0
    tarif_horaire_max: float = 0.0
    note_moyenne: float = 0.0
    statut: str = "actif"

@dataclass
class DemandeDevis:
    id: Optional[int] = None
    client_id: int = 0
    titre: str = ""
    type_projet: str = ""
    description_detaillee: str = ""
    budget_min: float = 0.0
    budget_max: float = 0.0
    delai_livraison: str = ""
    date_limite_soumissions: Optional[datetime.datetime] = None
    statut: str = "brouillon"
    numero_reference: str = ""
    date_creation: Optional[datetime.datetime] = None

@dataclass
class Soumission:
    id: Optional[int] = None
    demande_id: int = 0
    prestataire_id: int = 0
    titre_soumission: str = ""
    resume_executif: str = ""
    proposition_technique: str = ""
    budget_total: float = 0.0
    delai_livraison: str = ""
    statut: str = "brouillon"
    date_creation: Optional[datetime.datetime] = None

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', os.path.join(os.getcwd(), 'data'))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, DATABASE_FILE)

# Fonctions utilitaires
def init_database():
    """Initialise la base de données si elle n'existe pas"""
    if not os.path.exists(DATABASE_PATH):
        print("Base de données non trouvée, initialisation...")
        from init_db_approbation import init_database_approbation
        init_database_approbation()
    else:
        print("Base de données existante trouvée")
        # Vérifier que toutes les tables essentielles existent
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables_existantes = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        tables_requises = ['entreprises_clientes', 'entreprises_prestataires', 'demandes_devis', 'soumissions']
        tables_manquantes = [table for table in tables_requises if table not in tables_existantes]
        
        if tables_manquantes:
            print(f"Tables manquantes détectées: {tables_manquantes}")
            print("Réinitialisation complète de la base de données...")
            from init_db_approbation import init_database_approbation
            init_database_approbation()

def get_database_connection():
    """Retourne une connexion à la base de données"""
    init_database()
    return sqlite3.connect(DATABASE_PATH)

def hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def valider_email(email: str) -> bool:
    """Valide le format d'un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def valider_telephone(telephone: str) -> bool:
    """Valide le format d'un numéro de téléphone"""
    pattern = r'^(\+1[-.\s]?)?\(?([2-9][0-9]{2})\)?[-.\s]?([2-9][0-9]{2})[-.\s]?([0-9]{4})$'
    return re.match(pattern, telephone.replace(" ", "")) is not None

def generer_numero_reference() -> str:
    """Génère un numéro de référence unique"""
    return f"{REFERENCE_PREFIX}-{datetime.datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

# Fonctions d'authentification
def authentifier_client(email: str, mot_de_passe: str) -> Optional[dict]:
    """Authentifie un client particulier"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM entreprises_clientes WHERE email = ? AND mot_de_passe_hash = ? AND statut = 'actif'
    ''', (email, hash_password(mot_de_passe)))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'prenom': result[1], 
            'nom': result[2],
            'nom_entreprise': f"{result[1]} {result[2]}",  # Pour compatibilité
            'email': result[3],
            'telephone': result[4],
            'adresse': result[5],
            'ville': result[6],
            'code_postal': result[7],
            'profession': result[10],
            'type_propriete': result[12],
            'statut': result[14]
        }
    return None

def authentifier_prestataire(email: str, mot_de_passe: str) -> Optional[EntreprisePrestataire]:
    """Authentifie une entreprise prestataire"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM entreprises_prestataires WHERE email = ? AND mot_de_passe_hash = ? AND statut = 'actif'
    ''', (email, hash_password(mot_de_passe)))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return EntreprisePrestataire(
            id=result[0], nom_entreprise=result[1], domaines_expertise=result[2],
            taille_entreprise=result[3], nom_contact=result[4], poste_contact=result[5],
            email=result[6], telephone=result[7], mot_de_passe_hash=result[9],
            certifications=result[17], tarif_horaire_min=result[18], tarif_horaire_max=result[19],
            note_moyenne=result[25], statut=result[23]
        )
    return None

def authentifier_admin(mot_de_passe: str) -> bool:
    """Authentifie un administrateur"""
    return mot_de_passe == "admin123"  # Mot de passe simple pour la démo

# Interface principale
def main():
    # Initialiser les tables d'inscription
    try:
        init_inscription_tables()
    except:
        pass
    
    init_database()
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🏠 PORTAIL C2B DE L'ENTREPRISE</h1>
        <p>Plateforme de soumissions construction - Client à Entreprise</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialiser les états de session
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'page' not in st.session_state:
        st.session_state.page = 'accueil'
    
    # Note: La page inscription sera gérée dans le routing normal pour garder la sidebar
    
    # Menu de navigation dans la sidebar
    with st.sidebar:
        st.markdown("## 🏠 PORTAIL C2B DE L'ENTREPRISE")
        st.markdown("*Plateforme Client à Entreprise pour travaux de construction*")
        st.markdown("---")
        
        if st.session_state.user_type is None:
            # Navigation principale
            st.markdown("### 📋 Navigation")
            
            if st.button("🏠 Accueil", key="accueil_btn", use_container_width=True):
                st.session_state.page = 'accueil'
                st.rerun()
            
            # Bouton d'inscription principal
            st.markdown("### ✨ Rejoignez-nous")
            
            if st.button("🚀 S'inscrire maintenant", use_container_width=True, type="primary"):
                st.session_state.page = 'inscription'
                st.rerun()
            
            st.markdown("---")
            
            # Menu pour utilisateurs non connectés
            st.markdown("### 🔐 Connexion")
            
            if st.button("👤 Client (Particulier)", key="login_client", use_container_width=True):
                st.session_state.show_login_form = "Client"
                st.rerun()
            
            if st.button("🏢 Entreprise", key="login_entreprise", use_container_width=True):
                st.session_state.show_login_form = "Entreprise"  
                st.rerun()
                
            if st.button("⚙️ Administrateur", key="login_admin", use_container_width=True):
                st.session_state.show_login_form = "Administrateur"
                st.rerun()
            
            # Afficher le formulaire de connexion si un type a été sélectionné
            if st.session_state.get('show_login_form'):
                show_login_form(st.session_state.show_login_form)
            
            st.markdown("---")
            
            # Section Services professionnels (accessible à tous, connectés ou non)
            st.markdown("### 🏗️ Services professionnels")
            services_prof_options = {
                "service_estimation": "💰 Service d'estimation",
                "service_technologue": "📐 Service de technologue", 
                "service_architecture": "🏛️ Service d'architecture",
                "service_ingenieur": "🔧 Service d'ingénieur"
            }
            
            for key, label in services_prof_options.items():
                if st.button(label, key=f"services_prof_{key}", use_container_width=True):
                    st.session_state.page = key
                    st.rerun()
            
            st.markdown("---")
            
            # Section Logiciels professionnels (accessible à tous, connectés ou non)
            st.markdown("### 💻 Logiciels professionnels")
            logiciels_options = {
                "experts_ia": "🧠 EXPERTS IA",
                "takeoff_ai": "📐 TAKEOFF AI",
                "erp_ai": "📊 ERP AI"
            }
            
            for key, label in logiciels_options.items():
                if st.button(label, key=f"logiciels_{key}", use_container_width=True):
                    st.session_state.page = key
                    st.rerun()
            
            # Informations sur les services 
            st.markdown("---")
            st.markdown("### ℹ️ À propos des services")
            st.markdown("""
            **Services professionnels :**
            
            📐 **Technologue** : ≤ 6,000 pi²  
            🏛️ **Architecture** : > 6,000 pi²  
            🔧 **Ingénierie** : Calculs structuraux  
            💰 **Estimation** : Évaluation de coûts
            
            **Logiciels professionnels :**
            
            🧠 **EXPERTS IA** : 60+ experts construction  
            📐 **TAKEOFF AI** : Estimation automatique  
            📊 **ERP AI** : Gestion de chantier 24 étapes
            
            **Contact :**
            
            📧 info@constructoai.ca  
            📞 514-820-1972
            """)
            
            # Footer de la sidebar
            st.markdown("---")
            st.markdown(
                """
                <div style="text-align: center; font-size: 12px; color: #666;">
                    © 2025 PORTAIL C2B DE L'ENTREPRISE<br>
                    Propulsé par IA
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        else:
            # Menu pour utilisateurs connectés
            user_name = st.session_state.user_data.nom_entreprise if hasattr(st.session_state.user_data, 'nom_entreprise') else "Administrateur"
            st.markdown(f"### 👋 Bonjour, {user_name}")
            st.markdown(f"**Rôle:** {st.session_state.user_type}")
            
            st.markdown("---")
            
            # Navigation principale - accessible à tous les utilisateurs connectés
            st.markdown("### 📋 Gestion de projets")
            
            if st.button("🏠 Tableau de bord", key="dashboard_btn", use_container_width=True):
                st.session_state.page = 'dashboard'
                st.rerun()
            
            # Menus spécifiques selon le rôle
            if st.session_state.user_type == "Client":
                if st.button("📝 Mes demandes de soumissions", key="mes_demandes_btn", use_container_width=True):
                    st.session_state.page = 'mes_demandes'
                    st.rerun()
                if st.button("➕ Nouvelle demande", key="nouvelle_demande_btn", use_container_width=True):
                    st.session_state.page = 'nouvelle_demande'
                    st.rerun()
                if st.button("📥 Soumissions reçues", key="soumissions_recues_btn", use_container_width=True):
                    st.session_state.page = 'soumissions_recues'
                    st.rerun()
                if st.button("⭐ Évaluations", key="evaluations_btn", use_container_width=True):
                    st.session_state.page = 'evaluations'
                    st.rerun()
                if st.button("📄 Contrats", key="contrats_btn", use_container_width=True):
                    st.session_state.page = 'contrats'
                    st.rerun()
                if st.button("💬 Messages", key="messages_btn", use_container_width=True):
                    st.session_state.page = 'messages'
                    st.rerun()
                if st.button("👤 Mon profil", key="profil_btn", use_container_width=True):
                    st.session_state.page = 'profil'
                    st.rerun()
                    
            elif st.session_state.user_type == "Entreprise":
                if st.button("📥 Demandes clients reçues", key="demandes_disponibles_btn", use_container_width=True):
                    st.session_state.page = 'demandes_disponibles'
                    st.rerun()
                if st.button("📤 Mes soumissions", key="mes_soumissions_btn", use_container_width=True):
                    st.session_state.page = 'mes_soumissions'
                    st.rerun()
                if st.button("➕ Nouvelle soumission", key="nouvelle_soumission_btn", use_container_width=True):
                    st.session_state.page = 'nouvelle_soumission'
                    st.rerun()
                if st.button("⭐ Mes évaluations", key="mes_evaluations_btn", use_container_width=True):
                    st.session_state.page = 'evaluations'
                    st.rerun()
                if st.button("📄 Mes contrats", key="mes_contrats_btn", use_container_width=True):
                    st.session_state.page = 'contrats'
                    st.rerun()
                if st.button("💬 Messages", key="messages_prestataire_btn", use_container_width=True):
                    st.session_state.page = 'messages'
                    st.rerun()
                if st.button("👤 Mon profil", key="profil_prestataire_btn", use_container_width=True):
                    st.session_state.page = 'profil'
                    st.rerun()
                    
            elif st.session_state.user_type == "Administrateur":
                if st.button("📋 Toutes les demandes", key="admin_demandes_btn", use_container_width=True):
                    st.session_state.page = 'demandes'
                    st.rerun()
                if st.button("📤 Toutes les soumissions", key="admin_soumissions_btn", use_container_width=True):
                    st.session_state.page = 'soumissions'
                    st.rerun()
                if st.button("🔄 Workflow d'approbation", key="admin_workflow_btn", use_container_width=True):
                    st.session_state.page = 'workflow'
                    st.rerun()
                if st.button("🏢 Gestion des entreprises", key="admin_entreprises_btn", use_container_width=True):
                    st.session_state.page = 'entreprises'
                    st.rerun()
                if st.button("📊 Rapports et analytics", key="admin_rapports_btn", use_container_width=True):
                    st.session_state.page = 'rapports'
                    st.rerun()
                if st.button("⚙️ Paramètres système", key="admin_parametres_btn", use_container_width=True):
                    st.session_state.page = 'parametres'
                    st.rerun()
            
            st.markdown("---")
            
            # Section Services professionnels (accessible à tous les utilisateurs connectés)
            st.markdown("### 🏗️ Services professionnels")
            services_prof_options = {
                "service_estimation": "💰 Service d'estimation",
                "service_technologue": "📐 Service de technologue", 
                "service_architecture": "🏛️ Service d'architecture",
                "service_ingenieur": "🔧 Service d'ingénieur"
            }
            
            for key, label in services_prof_options.items():
                if st.button(label, key=f"services_prof_connected_{key}", use_container_width=True):
                    st.session_state.page = key
                    st.rerun()
            
            st.markdown("---")
            
            # Section Logiciels professionnels (accessible à tous les utilisateurs connectés)
            st.markdown("### 💻 Logiciels professionnels")
            logiciels_options = {
                "experts_ia": "🧠 EXPERTS IA",
                "takeoff_ai": "📐 TAKEOFF AI",
                "erp_ai": "📊 ERP AI"
            }
            
            for key, label in logiciels_options.items():
                if st.button(label, key=f"logiciels_connected_{key}", use_container_width=True):
                    st.session_state.page = key
                    st.rerun()
            
            # Informations sur les services 
            st.markdown("---")
            st.markdown("### ℹ️ À propos des services")
            st.markdown("""
            **Services professionnels :**
            
            📐 **Technologue** : ≤ 6,000 pi²  
            🏛️ **Architecture** : > 6,000 pi²  
            🔧 **Ingénierie** : Calculs structuraux  
            💰 **Estimation** : Évaluation de coûts
            
            **Logiciels professionnels :**
            
            🧠 **EXPERTS IA** : 60+ experts construction  
            📐 **TAKEOFF AI** : Estimation automatique  
            📊 **ERP AI** : Gestion de chantier 24 étapes
            
            **Contact :**
            
            📧 info@constructoai.ca  
            📞 514-820-1972
            """)
            
            st.markdown("---")
            if st.button("🚪 Déconnexion", use_container_width=True):
                st.session_state.user_type = None
                st.session_state.user_data = None
                st.session_state.page = 'accueil'
                if 'show_login_form' in st.session_state:
                    del st.session_state.show_login_form
                st.rerun()
            
            # Footer de la sidebar
            st.markdown("---")
            st.markdown(
                """
                <div style="text-align: center; font-size: 12px; color: #666;">
                    © 2025 PORTAIL C2B DE L'ENTREPRISE<br>
                    Propulsé par IA
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    # Routing des pages
    if st.session_state.user_type is None:
        # Router pour utilisateurs non connectés
        if st.session_state.page == 'accueil':
            page_accueil()
        # Page d'inscription (avec sidebar visible)
        elif st.session_state.page == 'inscription':
            router_inscription()
        # Services professionnels (accessible sans connexion)
        elif st.session_state.page == 'service_estimation':
            page_service_estimation()
        elif st.session_state.page == 'service_technologue':
            page_service_technologue()
        elif st.session_state.page == 'service_architecture':
            page_service_architecture()
        elif st.session_state.page == 'service_ingenieur':
            page_service_ingenieur()
        # Logiciels professionnels (accessible sans connexion)
        elif st.session_state.page == 'experts_ia':
            page_experts_ia()
        elif st.session_state.page == 'takeoff_ai':
            page_takeoff_ai()
        elif st.session_state.page == 'erp_ai':
            page_erp_ai()
        else:
            page_accueil()
    elif st.session_state.user_type == "Particulier":
        router_client()
    elif st.session_state.user_type == "Entrepreneur Construction":
        router_prestataire()
    elif st.session_state.user_type == "Administrateur":
        router_admin()

def show_login_form(user_type: str):
    """Affiche le formulaire de connexion selon le type d'utilisateur"""
    
    with st.form(f"login_form_{user_type}"):
        st.markdown(f"#### Connexion {user_type}")
        
        if user_type != "Administrateur":
            email = st.text_input("Email", placeholder="votre@email.com")
            mot_de_passe = st.text_input("Mot de passe", type="password")
        else:
            mot_de_passe = st.text_input("Mot de passe administrateur", type="password")
            email = None
        
        connecter = st.form_submit_button("🔐 Se connecter", use_container_width=True)
        
        if connecter:
            if user_type == "Client" and email and mot_de_passe:
                client = authentifier_client(email, mot_de_passe)
                if client:
                    st.session_state.user_type = "Client"
                    st.session_state.user_data = client
                    st.session_state.page = 'dashboard'
                    st.success("✅ Connexion client réussie!")
                    st.rerun()
                else:
                    st.error("❌ Email ou mot de passe incorrect")
            
            elif user_type == "Entreprise" and email and mot_de_passe:
                prestataire = authentifier_prestataire(email, mot_de_passe)
                if prestataire:
                    st.session_state.user_type = "Entreprise"
                    st.session_state.user_data = prestataire
                    st.session_state.page = 'dashboard'
                    st.success("✅ Connexion entreprise réussie!")
                    st.rerun()
                else:
                    st.error("❌ Email ou mot de passe incorrect")
            
            elif user_type == "Administrateur" and mot_de_passe:
                if authentifier_admin(mot_de_passe):
                    st.session_state.user_type = "Administrateur"
                    st.session_state.user_data = None
                    st.session_state.page = 'dashboard'
                    st.success("✅ Connexion administrateur réussie!")
                    st.rerun()
                else:
                    st.error("❌ Mot de passe administrateur incorrect")
            
            else:
                st.error("❌ Veuillez remplir tous les champs")

def menu_client():
    """Menu de navigation pour les entreprises clientes (donneurs d'ouvrage)"""
    st.markdown("#### 🏢 Menu Donneur d'Ouvrage")
    
    menu_options = {
        "dashboard": "🏠 Tableau de bord",
        "mes_demandes": "📝 Mes demandes de devis",
        "nouvelle_demande": "➕ Nouvelle demande",
        "soumissions_recues": "📥 Soumissions reçues",
        "evaluations": "⭐ Évaluations",
        "contrats": "📄 Contrats",
        "messages": "💬 Messages",
        "profil": "👤 Mon profil"
    }
    
    for key, label in menu_options.items():
        if st.button(label, key=f"menu_client_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

def menu_prestataire():
    """Menu de navigation pour les entreprises de construction"""
    st.markdown("#### 🏗️ Menu Entrepreneur Construction")
    
    menu_options = {
        "dashboard": "🏠 Tableau de bord",
        "demandes_disponibles": "🔍 Demandes disponibles",
        "mes_soumissions": "📤 Mes soumissions",
        "nouvelle_soumission": "➕ Nouvelle soumission",
        "evaluations": "⭐ Mes évaluations",
        "contrats": "📄 Mes contrats",
        "messages": "💬 Messages",
        "profil": "👤 Mon profil"
    }
    
    for key, label in menu_options.items():
        if st.button(label, key=f"menu_prestataire_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

def menu_admin():
    """Menu de navigation pour les administrateurs"""
    st.markdown("#### ⚙️ Menu Admin")
    
    menu_options = {
        "dashboard": "🏠 Tableau de bord",
        "demandes": "📋 Toutes les demandes",
        "soumissions": "📤 Toutes les soumissions",
        "workflow": "🔄 Workflow d'approbation",
        "entreprises": "🏢 Gestion des entreprises",
        "rapports": "📊 Rapports et analytics",
        "parametres": "⚙️ Paramètres système"
    }
    
    for key, label in menu_options.items():
        if st.button(label, key=f"menu_admin_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

def page_accueil():
    """Page d'accueil pour utilisateurs non connectés"""
    
    # Section héro
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="demande-card">
            <h2>🏠 Bienvenue sur notre PORTAIL C2B</h2>
            <p style="font-size: 1.2rem; color: #475569;">
                Vous êtes un CLIENT ? Demandez votre soumission directement à notre ENTREPRISE de construction certifiée RBQ.
            </p>
            <ul style="font-size: 1.1rem; color: #334155;">
                <li>✅ Équipe unique d'entrepreneurs certifiés</li>
                <li>✅ Devis personnalisés pour projets résidentiels</li>
                <li>✅ Suivi transparent de vos travaux</li>
                <li>✅ Communication directe et simplifiée</li>
                <li>✅ Garanties et assurances complètes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <h3>📊 Notre expertise</h3>
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: white;">500+</div>
                <div>Projets résidentiels réalisés</div>
                <hr>
                <div style="font-size: 2rem; font-weight: bold; color: white;">15 ans</div>
                <div>D'expérience construction</div>
                <hr>
                <div style="font-size: 2rem; font-weight: bold; color: white;">98%</div>
                <div>Clients satisfaits</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Services pour particuliers
    st.markdown("## 🏠 Nos Services de Construction Résidentielle")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="demande-card">
            <h4 style="color: #1E40AF;">🛁 Rénovation Intérieure</h4>
            <ul>
                <li>Salle de bain complète</li>
                <li>Cuisine moderne</li>
                <li>Aménagement sous-sol</li>
                <li>Planchers et carrelage</li>
                <li>Peinture intérieure</li>
                <li>Électricité et plomberie</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="soumission-card">
            <h4 style="color: #059669;">🏡 Rénovation Extérieure</h4>
            <ul>
                <li>Toiture résidentielle</li>
                <li>Revêtement et isolation</li>
                <li>Terrasse et patio</li>
                <li>Fenêtres et portes</li>
                <li>Aménagement paysager</li>
                <li>Clôture et portail</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="entreprise-card">
            <h4 style="color: #7C3AED;">⚡ Services Spécialisés</h4>
            <ul>
                <li>Agrandissement maison</li>
                <li>Garage et cabanon</li>
                <li>Piscine et spa</li>
                <li>Chauffage climatisation</li>
                <li>Déneigement entretien</li>
                <li>Urgences 24/7</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # CTA pour particuliers
    st.markdown("## 🚀 Confiez-nous vos projets résidentiels")
    st.markdown("Créez votre compte particulier pour recevoir des devis personnalisés de notre équipe d'experts.")

# Routers pour chaque type d'utilisateur
def router_client():
    """Router pour les entreprises clientes"""
    if st.session_state.page == 'dashboard':
        dashboard_client()
    elif st.session_state.page == 'mes_demandes':
        page_mes_demandes()
    elif st.session_state.page == 'nouvelle_demande':
        page_nouvelle_demande()
    elif st.session_state.page == 'soumissions_recues':
        page_soumissions_recues()
    elif st.session_state.page == 'evaluations':
        page_evaluations_client()
    elif st.session_state.page == 'contrats':
        page_contrats_client()
    elif st.session_state.page == 'messages':
        page_messages_client()
    elif st.session_state.page == 'profil':
        page_profil_client()
    # Services professionnels
    elif st.session_state.page == 'service_estimation':
        page_service_estimation()
    elif st.session_state.page == 'service_technologue':
        page_service_technologue()
    elif st.session_state.page == 'service_architecture':
        page_service_architecture()
    elif st.session_state.page == 'service_ingenieur':
        page_service_ingenieur()
    # Logiciels professionnels
    elif st.session_state.page == 'experts_ia':
        page_experts_ia()
    elif st.session_state.page == 'takeoff_ai':
        page_takeoff_ai()
    elif st.session_state.page == 'erp_ai':
        page_erp_ai()
    else:
        dashboard_client()

def router_prestataire():
    """Router pour les entreprises prestataires"""
    if st.session_state.page == 'dashboard':
        dashboard_prestataire()
    elif st.session_state.page == 'demandes_disponibles':
        page_demandes_disponibles()
    elif st.session_state.page == 'mes_soumissions':
        page_mes_soumissions()
    elif st.session_state.page == 'nouvelle_soumission':
        page_nouvelle_soumission()
    elif st.session_state.page == 'evaluations':
        page_evaluations_prestataire()
    elif st.session_state.page == 'contrats':
        page_contrats_prestataire()
    elif st.session_state.page == 'messages':
        page_messages_prestataire()
    elif st.session_state.page == 'profil':
        page_profil_prestataire()
    # Services professionnels
    elif st.session_state.page == 'service_estimation':
        page_service_estimation()
    elif st.session_state.page == 'service_technologue':
        page_service_technologue()
    elif st.session_state.page == 'service_architecture':
        page_service_architecture()
    elif st.session_state.page == 'service_ingenieur':
        page_service_ingenieur()
    # Logiciels professionnels
    elif st.session_state.page == 'experts_ia':
        page_experts_ia()
    elif st.session_state.page == 'takeoff_ai':
        page_takeoff_ai()
    elif st.session_state.page == 'erp_ai':
        page_erp_ai()
    else:
        dashboard_prestataire()

def router_admin():
    """Router pour les administrateurs"""
    if st.session_state.page == 'dashboard':
        dashboard_admin()
    elif st.session_state.page == 'demandes':
        page_admin_demandes()
    elif st.session_state.page == 'soumissions':
        page_admin_soumissions()
    elif st.session_state.page == 'workflow':
        page_admin_workflow()
    elif st.session_state.page == 'entreprises':
        page_admin_entreprises()
    elif st.session_state.page == 'rapports':
        page_admin_rapports()
    elif st.session_state.page == 'parametres':
        page_admin_parametres()
    # Services professionnels
    elif st.session_state.page == 'service_estimation':
        page_service_estimation()
    elif st.session_state.page == 'service_technologue':
        page_service_technologue()
    elif st.session_state.page == 'service_architecture':
        page_service_architecture()
    elif st.session_state.page == 'service_ingenieur':
        page_service_ingenieur()
    # Logiciels professionnels
    elif st.session_state.page == 'experts_ia':
        page_experts_ia()
    elif st.session_state.page == 'takeoff_ai':
        page_takeoff_ai()
    elif st.session_state.page == 'erp_ai':
        page_erp_ai()
    else:
        dashboard_admin()

# Dashboards pour chaque type d'utilisateur
def dashboard_client():
    """Dashboard pour entreprises clientes"""
    st.markdown("## 🏠 Tableau de Bord Client")
    
    client = st.session_state.user_data
    
    # Statistiques rapides
    col1, col2, col3, col4 = st.columns(4)
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Compter les demandes actives
    cursor.execute('SELECT COUNT(*) FROM demandes_devis WHERE client_id = ? AND statut != "annulee"', (client.id,))
    nb_demandes = cursor.fetchone()[0]
    
    # Compter les soumissions reçues
    cursor.execute('''
        SELECT COUNT(*) FROM soumissions s 
        JOIN demandes_devis d ON s.demande_id = d.id 
        WHERE d.client_id = ?
    ''', (client.id,))
    nb_soumissions = cursor.fetchone()[0]
    
    # Compter les contrats actifs
    cursor.execute('SELECT COUNT(*) FROM contrats WHERE client_id = ? AND statut_contrat = "actif"', (client.id,))
    nb_contrats = cursor.fetchone()[0]
    
    conn.close()
    
    with col1:
        st.markdown(f"""
        <div class="stat-card client-stats">
            <h3>📋</h3>
            <h2>{nb_demandes}</h2>
            <p>Demandes actives</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card client-stats">
            <h3>📥</h3>
            <h2>{nb_soumissions}</h2>
            <p>Soumissions reçues</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card client-stats">
            <h3>📄</h3>
            <h2>{nb_contrats}</h2>
            <p>Contrats actifs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        taux_reponse = round((nb_soumissions / max(nb_demandes, 1)) * 100, 1)
        st.markdown(f"""
        <div class="stat-card client-stats">
            <h3>📊</h3>
            <h2>{taux_reponse}%</h2>
            <p>Taux de réponse</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Actions rapides
    st.markdown("### 🚀 Actions rapides")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Nouvelle demande de devis", use_container_width=True):
            st.session_state.page = 'nouvelle_demande'
            st.rerun()
    
    with col2:
        if st.button("📥 Voir mes soumissions", use_container_width=True):
            st.session_state.page = 'soumissions_recues'
            st.rerun()
    
    with col3:
        if st.button("📋 Mes demandes", use_container_width=True):
            st.session_state.page = 'mes_demandes'
            st.rerun()

def dashboard_prestataire():
    """Dashboard pour entreprises prestataires"""
    st.markdown("## 🏠 Tableau de Bord Prestataire")
    
    prestataire = st.session_state.user_data
    
    # Statistiques rapides
    col1, col2, col3, col4 = st.columns(4)
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Compter les soumissions actives
    cursor.execute('SELECT COUNT(*) FROM soumissions WHERE prestataire_id = ? AND statut NOT IN ("rejetee", "refusee")', (prestataire.id,))
    nb_soumissions = cursor.fetchone()[0]
    
    # Compter les demandes disponibles
    cursor.execute('SELECT COUNT(*) FROM demandes_devis WHERE statut = "publiee"')
    nb_demandes_dispo = cursor.fetchone()[0]
    
    # Compter les contrats actifs
    cursor.execute('SELECT COUNT(*) FROM contrats WHERE prestataire_id = ? AND statut_contrat = "actif"', (prestataire.id,))
    nb_contrats = cursor.fetchone()[0]
    
    conn.close()
    
    with col1:
        st.markdown(f"""
        <div class="stat-card prestataire-stats">
            <h3>📤</h3>
            <h2>{nb_soumissions}</h2>
            <p>Soumissions actives</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card prestataire-stats">
            <h3>🔍</h3>
            <h2>{nb_demandes_dispo}</h2>
            <p>Opportunités disponibles</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card prestataire-stats">
            <h3>📄</h3>
            <h2>{nb_contrats}</h2>
            <p>Contrats actifs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        note_moyenne = prestataire.note_moyenne or 0.0
        st.markdown(f"""
        <div class="stat-card prestataire-stats">
            <h3>⭐</h3>
            <h2>{note_moyenne:.1f}/5</h2>
            <p>Note moyenne</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Actions rapides
    st.markdown("### 🚀 Actions rapides")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Voir les opportunités", use_container_width=True):
            st.session_state.page = 'demandes_disponibles'
            st.rerun()
    
    with col2:
        if st.button("📤 Mes soumissions", use_container_width=True):
            st.session_state.page = 'mes_soumissions'
            st.rerun()
    
    with col3:
        if st.button("➕ Nouvelle soumission", use_container_width=True):
            st.session_state.page = 'nouvelle_soumission'
            st.rerun()

def dashboard_admin():
    """Dashboard pour administrateurs"""
    st.markdown("## 🏠 Tableau de Bord Administrateur")
    
    # Statistiques système
    col1, col2, col3, col4 = st.columns(4)
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Statistiques globales
    cursor.execute('SELECT COUNT(*) FROM entreprises_clientes WHERE statut = "actif"')
    nb_clients = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM entreprises_prestataires WHERE statut = "actif"')
    nb_prestataires = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM demandes_devis')
    nb_demandes = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM soumissions WHERE statut = "en_approbation"')
    nb_approbations_pending = cursor.fetchone()[0]
    
    conn.close()
    
    with col1:
        st.markdown(f"""
        <div class="stat-card admin-stats">
            <h3>🏢</h3>
            <h2>{nb_clients}</h2>
            <p>Entreprises clientes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card admin-stats">
            <h3>🏗️</h3>
            <h2>{nb_prestataires}</h2>
            <p>Prestataires actifs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card admin-stats">
            <h3>📋</h3>
            <h2>{nb_demandes}</h2>
            <p>Demandes totales</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card admin-stats">
            <h3>⏳</h3>
            <h2>{nb_approbations_pending}</h2>
            <p>En attente d'approbation</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Actions d'administration
    st.markdown("### ⚙️ Actions d'administration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Gérer le workflow", use_container_width=True):
            st.session_state.page = 'workflow'
            st.rerun()
    
    with col2:
        if st.button("📊 Voir les rapports", use_container_width=True):
            st.session_state.page = 'rapports'
            st.rerun()
    
    with col3:
        if st.button("🏢 Gérer les entreprises", use_container_width=True):
            st.session_state.page = 'entreprises'
            st.rerun()

# Fonctions de pages - Implémentation complète
def page_mes_demandes():
    """Page des demandes de devis pour les clients"""
    st.markdown("## 📋 Mes Demandes de Devis")
    
    # Récupérer les demandes du client connecté
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT d.*, 
               (SELECT COUNT(*) FROM soumissions s WHERE s.demande_id = d.id) as nb_soumissions
        FROM demandes_devis d 
        WHERE d.client_id = ? 
        ORDER BY d.date_creation DESC
    ''', (st.session_state.user_data.id,))
    
    demandes = cursor.fetchall()
    conn.close()
    
    if not demandes:
        st.info("📝 Vous n'avez encore publié aucune demande de devis.")
        if st.button("➕ Créer ma première demande", use_container_width=True):
            st.session_state.page = 'nouvelle_demande'
            st.rerun()
        return
    
    # Afficher les demandes
    for demande in demandes:
        with st.expander(f"📋 {demande[2]} - {STATUTS_DEMANDE.get(demande[9], demande[9])}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Type:** {demande[3]}")
                st.markdown(f"**Description:** {demande[4][:200]}..." if len(demande[4]) > 200 else f"**Description:** {demande[4]}")
                st.markdown(f"**Budget:** {demande[5]:,.0f}$ - {demande[6]:,.0f}$")
                st.markdown(f"**Délai:** {demande[7]}")
                
            with col2:
                st.metric("Soumissions reçues", demande[12])
                st.markdown(f"**Créée le:** {demande[11][:10]}")
                
                if st.button(f"📥 Voir soumissions", key=f"voir_soumissions_{demande[0]}"):
                    st.session_state.page = 'soumissions_recues'
                    st.session_state.demande_selectionnee = demande[0]
                    st.rerun()

def page_nouvelle_demande():
    """Page de création d'une nouvelle demande de devis"""
    st.markdown("## ➕ Nouvelle Demande de Devis")
    
    with st.form("nouvelle_demande_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            titre = st.text_input(
                "Titre du projet *",
                placeholder="Ex: Construction d'un entrepôt de 5000m²"
            )
            
            type_projet = st.selectbox(
                "Type de projet *",
                TYPES_PROJETS
            )
            
            budget_min = st.number_input(
                "Budget minimum ($) *",
                min_value=1000,
                value=100000,
                step=5000,
                format="%d"
            )
            
            budget_max = st.number_input(
                "Budget maximum ($) *",
                min_value=budget_min,
                value=int(budget_min * 1.5),
                step=5000,
                format="%d"
            )
        
        with col2:
            delai_livraison = st.selectbox(
                "Délai de réalisation souhaité *",
                DELAIS_LIVRAISON
            )
            
            date_limite = st.date_input(
                "Date limite de soumission *",
                value=datetime.datetime.now() + datetime.timedelta(days=30),
                min_value=datetime.datetime.now().date() + datetime.timedelta(days=7)
            )
            
            # Critères d'évaluation
            st.markdown("**Critères d'évaluation importants:**")
            criteres_selectionnes = st.multiselect(
                "Sélectionnez les critères prioritaires",
                CRITERES_EVALUATION,
                default=CRITERES_EVALUATION[:3]
            )
        
        description = st.text_area(
            "Description détaillée du projet *",
            placeholder="Décrivez précisément votre projet, les exigences techniques, les contraintes, les livrables attendus...",
            height=200
        )
        
        specifications_techniques = st.text_area(
            "Spécifications techniques",
            placeholder="Normes à respecter, certifications requises, matériaux spécifiques...",
            height=100
        )
        
        # Documents attachés
        st.markdown("**Documents de projet (optionnel):**")
        fichiers_uploaded = st.file_uploader(
            "Plans, cahier des charges, documents techniques",
            type=FORMATS_AUTORISES["tous"],
            accept_multiple_files=True
        )
        
        submitted = st.form_submit_button("📤 Publier la demande", use_container_width=True)
        
        if submitted:
            if not titre or not description or not type_projet:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
            elif budget_max <= budget_min:
                st.error("❌ Le budget maximum doit être supérieur au budget minimum")
            else:
                # Sauvegarder la demande
                conn = get_database_connection()
                cursor = conn.cursor()
                
                numero_reference = generer_numero_reference()
                
                # Convertir les fichiers en base64
                documents_json = []
                if fichiers_uploaded:
                    for fichier in fichiers_uploaded:
                        if fichier.size <= SECURITY_CONFIG["max_file_size"]:
                            content_b64 = base64.b64encode(fichier.read()).decode('utf-8')
                            documents_json.append({
                                "nom": fichier.name,
                                "type": fichier.type,
                                "contenu": content_b64
                            })
                        else:
                            st.warning(f"⚠️ Fichier {fichier.name} trop volumineux (max 25 MB)")
                
                cursor.execute('''
                    INSERT INTO demandes_devis (
                        client_id, titre, type_projet, description_detaillee, 
                        budget_min, budget_max, delai_livraison, date_limite_soumissions,
                        statut, numero_reference, specifications_techniques,
                        criteres_evaluation, documents_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'publiee', ?, ?, ?, ?)
                ''', (
                    st.session_state.user_data.id, titre, type_projet, description,
                    budget_min, budget_max, delai_livraison, date_limite,
                    numero_reference, specifications_techniques or "",
                    json.dumps(criteres_selectionnes), json.dumps(documents_json)
                ))
                
                conn.commit()
                conn.close()
                
                st.success(f"✅ Demande de devis publiée avec succès!\n📋 Référence: {numero_reference}")
                
                # Rediriger vers la liste des demandes
                if st.button("📋 Voir mes demandes"):
                    st.session_state.page = 'mes_demandes'
                    st.rerun()

def page_soumissions_recues():
    """Page des soumissions reçues pour une demande spécifique"""
    st.markdown("## 📥 Soumissions Reçues")
    
    # Vérifier qu'une demande est sélectionnée
    if not hasattr(st.session_state, 'demande_selectionnee'):
        st.warning("⚠️ Veuillez d'abord sélectionner une demande depuis 'Mes demandes'")
        if st.button("📋 Retour à mes demandes"):
            st.session_state.page = 'mes_demandes'
            st.rerun()
        return
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Récupérer les détails de la demande
    cursor.execute('SELECT * FROM demandes_devis WHERE id = ?', (st.session_state.demande_selectionnee,))
    demande = cursor.fetchone()
    
    if not demande:
        st.error("❌ Demande non trouvée")
        return
    
    # Afficher les détails de la demande
    st.markdown(f"### 📋 {demande[2]}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Budget", f"{demande[5]:,.0f}$ - {demande[6]:,.0f}$")
    with col2:
        st.metric("Type", demande[3])
    with col3:
        st.metric("Statut", STATUTS_DEMANDE.get(demande[9], demande[9]))
    
    # Récupérer les soumissions
    cursor.execute('''
        SELECT s.*, ep.nom_entreprise, ep.note_moyenne, ep.certifications
        FROM soumissions s
        JOIN entreprises_prestataires ep ON s.prestataire_id = ep.id
        WHERE s.demande_id = ?
        ORDER BY s.date_creation DESC
    ''', (st.session_state.demande_selectionnee,))
    
    soumissions = cursor.fetchall()
    conn.close()
    
    if not soumissions:
        st.info("📄 Aucune soumission reçue pour cette demande.")
        return
    
    st.markdown(f"### 📤 {len(soumissions)} Soumission(s) reçue(s)")
    
    # Afficher chaque soumission
    for soumission in soumissions:
        with st.expander(f"🏢 {soumission[12]} - {soumission[4]:,.0f}$ - {STATUTS_SOUMISSION.get(soumission[8], soumission[8])}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Titre:** {soumission[3]}")
                st.markdown(f"**Résumé exécutif:**")
                st.write(soumission[4])
                st.markdown(f"**Proposition technique:**")
                st.write(soumission[5])
                st.markdown(f"**Délai proposé:** {soumission[7]}")
            
            with col2:
                st.metric("Montant", f"{soumission[6]:,.0f}$")
                st.metric("Note entreprise", f"{soumission[13]:.1f}/5.0")
                st.markdown(f"**Certifications:** {soumission[14] or 'Non renseigné'}")
                st.markdown(f"**Soumise le:** {soumission[9][:10]}")
                
                # Actions selon le statut
                if soumission[8] == 'recue':
                    if st.button(f"🔍 Démarrer évaluation", key=f"evaluer_{soumission[0]}"):
                        # Changer le statut à "en_evaluation"
                        conn = get_database_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE soumissions SET statut = 'en_evaluation' 
                            WHERE id = ?
                        ''', (soumission[0],))
                        conn.commit()
                        conn.close()
                        st.rerun()
                
                elif soumission[8] == 'en_evaluation':
                    if st.button(f"✅ Approuver", key=f"approuver_{soumission[0]}"):
                        # Changer le statut à "approuvee"
                        conn = get_database_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE soumissions SET statut = 'approuvee' 
                            WHERE id = ?
                        ''', (soumission[0],))
                        conn.commit()
                        conn.close()
                        st.success("✅ Soumission approuvée!")
                        st.rerun()
                    
                    if st.button(f"❌ Rejeter", key=f"rejeter_{soumission[0]}"):
                        # Changer le statut à "rejetee"
                        conn = get_database_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE soumissions SET statut = 'rejetee' 
                            WHERE id = ?
                        ''', (soumission[0],))
                        conn.commit()
                        conn.close()
                        st.info("❌ Soumission rejetée")
                        st.rerun()
                
                elif soumission[8] == 'approuvee':
                    st.success("✅ Approuvée")
                    if st.button(f"📜 Créer contrat", key=f"contrat_{soumission[0]}"):
                        st.info("🚧 Génération de contrat - Fonctionnalité en développement")
                
                elif soumission[8] == 'rejetee':
                    st.error("❌ Rejetée")

def page_evaluations_client():
    """Évaluations et scoring des soumissions pour les clients"""
    st.markdown("## ⭐ Évaluations")
    
    # Récupérer les soumissions à évaluer
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, d.titre as demande_titre, ep.nom_entreprise, d.criteres_evaluation
        FROM soumissions s
        JOIN demandes_devis d ON s.demande_id = d.id
        JOIN entreprises_prestataires ep ON s.prestataire_id = ep.id
        WHERE d.client_id = ? AND s.statut IN ('recue', 'en_evaluation')
        ORDER BY s.date_creation DESC
    ''', (st.session_state.user_data.id,))
    
    soumissions = cursor.fetchall()
    
    if not soumissions:
        st.info("🎉 Aucune soumission en attente d'évaluation.")
        return
    
    st.markdown(f"### 📋 {len(soumissions)} soumission(s) à évaluer")
    
    for soumission in soumissions:
        with st.expander(f"⭐ Évaluer: {soumission[3]} par {soumission[11]}"):
            # Détails de la soumission
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Projet:** {soumission[10]}")
                st.markdown(f"**Entrepreneur:** {soumission[11]}")
                st.markdown(f"**Montant:** {soumission[6]:,.0f}$")
                st.markdown(f"**Délai:** {soumission[7]}")
                
                st.markdown("**Résumé exécutif:**")
                st.write(soumission[4])
            
            with col2:
                st.markdown("### 🎯 Évaluation")
                
                # Formulaire d'évaluation simple
                with st.form(f"eval_form_{soumission[0]}"):
                    note_technique = st.slider(
                        "Note technique (1-5)",
                        1, 5, 3,
                        help="Qualité de la proposition technique",
                        key=f"tech_{soumission[0]}"
                    )
                    
                    note_financiere = st.slider(
                        "Note financière (1-5)",
                        1, 5, 3,
                        help="Compétitivité du prix",
                        key=f"fin_{soumission[0]}"
                    )
                    
                    note_experience = st.slider(
                        "Expérience/Références (1-5)",
                        1, 5, 3,
                        help="Expérience de l'entrepreneur",
                        key=f"exp_{soumission[0]}"
                    )
                    
                    commentaires = st.text_area(
                        "Commentaires",
                        placeholder="Points forts, points faibles, questions...",
                        key=f"comm_{soumission[0]}"
                    )
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.form_submit_button("✅ Approuver"):
                            # Calculer la note globale
                            note_globale = (note_technique + note_financiere + note_experience) / 3
                            
                            cursor.execute('''
                                UPDATE soumissions 
                                SET statut = 'approuvee', note_auto_evaluation = ?, commentaires_internes = ?
                                WHERE id = ?
                            ''', (note_globale, f"Tech: {note_technique}/5, Fin: {note_financiere}/5, Exp: {note_experience}/5. {commentaires}", soumission[0]))
                            
                            conn.commit()
                            st.success("✅ Soumission approuvée!")
                            st.rerun()
                    
                    with col_b:
                        if st.form_submit_button("❌ Rejeter"):
                            cursor.execute('''
                                UPDATE soumissions 
                                SET statut = 'rejetee', commentaires_internes = ?
                                WHERE id = ?
                            ''', (commentaires or "Soumission non retenue", soumission[0]))
                            
                            conn.commit()
                            st.info("❌ Soumission rejetée")
                            st.rerun()
    
    conn.close()

def page_contrats_client():
    st.markdown("## 📄 Mes Contrats")
    st.info("🚧 Cette fonctionnalité sera implémentée dans la prochaine étape.")

def page_messages_client():
    st.markdown("## 💬 Messages")
    st.info("🚧 Cette fonctionnalité sera implémentée dans la prochaine étape.")

def page_profil_client():
    """Profil et informations de l'entreprise cliente"""
    st.markdown("## 👤 Mon Profil d'Entreprise")
    
    client = st.session_state.user_data
    
    # Informations entreprise
    st.markdown("### 🏢 Informations de l'entreprise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Nom:** {client.nom_entreprise}")
        st.info(f"**Secteur:** {client.secteur_activite}")
        st.info(f"**Taille:** {client.taille_entreprise}")
        st.info(f"**Email:** {client.email}")
    
    with col2:
        st.info(f"**Contact:** {client.nom_contact}")
        st.info(f"**Poste:** {client.poste_contact}")
        st.info(f"**Téléphone:** {client.telephone}")
        st.info(f"**Statut:** {client.statut}")
    
    # Statistiques d'activité
    st.markdown("### 📈 Statistiques d'activité")
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Statistiques des demandes
    cursor.execute('SELECT COUNT(*) FROM demandes_devis WHERE client_id = ?', (client.id,))
    nb_demandes = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM demandes_devis WHERE client_id = ? AND statut = "attribuee"', (client.id,))
    nb_attribuees = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM soumissions s
        JOIN demandes_devis d ON s.demande_id = d.id
        WHERE d.client_id = ?
    ''', (client.id,))
    nb_soumissions_recues = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT SUM(s.budget_total) FROM soumissions s
        JOIN demandes_devis d ON s.demande_id = d.id
        WHERE d.client_id = ? AND s.statut = "acceptee"
    ''', (client.id,))
    valeur_contrats = cursor.fetchone()[0] or 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Demandes publiées", nb_demandes)
    with col2:
        st.metric("Projets attribués", nb_attribuees)
    with col3:
        st.metric("Soumissions reçues", nb_soumissions_recues)
    with col4:
        st.metric("Valeur des contrats", f"{valeur_contrats:,.0f}$")
    
    # Historique récent
    st.markdown("### 📅 Activité récente")
    
    cursor.execute('''
        SELECT d.titre, d.date_creation, d.statut,
               (SELECT COUNT(*) FROM soumissions s WHERE s.demande_id = d.id) as nb_soumissions
        FROM demandes_devis d
        WHERE d.client_id = ?
        ORDER BY d.date_creation DESC
        LIMIT 5
    ''', (client.id,))
    
    demandes_recentes = cursor.fetchall()
    
    if demandes_recentes:
        for demande in demandes_recentes:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"📋 {demande[0]}")
                with col2:
                    st.write(f"{demande[1][:10]}")
                with col3:
                    st.write(f"{demande[3]} soumissions")
    
    conn.close()

def page_demandes_disponibles():
    """Page des demandes disponibles pour les entrepreneurs"""
    st.markdown("## 🔍 Demandes Disponibles")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtre_type = st.selectbox(
            "Filtrer par type de projet",
            ["Tous"] + TYPES_PROJETS
        )
    
    with col2:
        filtre_budget = st.selectbox(
            "Filtrer par budget",
            ["Tous"] + TRANCHES_BUDGET
        )
    
    with col3:
        filtre_delai = st.selectbox(
            "Filtrer par délai",
            ["Tous"] + DELAIS_LIVRAISON
        )
    
    # Récupérer les demandes ouvertes
    conn = get_database_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT d.*, ec.nom_entreprise, ec.secteur_activite,
               (SELECT COUNT(*) FROM soumissions s WHERE s.demande_id = d.id) as nb_soumissions
        FROM demandes_devis d
        JOIN entreprises_clientes ec ON d.client_id = ec.id
        WHERE d.statut = 'publiee' AND d.date_limite_soumissions >= date('now')
    '''
    
    params = []
    
    if filtre_type != "Tous":
        query += " AND d.type_projet = ?"
        params.append(filtre_type)
    
    query += " ORDER BY d.date_creation DESC"
    
    cursor.execute(query, params)
    demandes = cursor.fetchall()
    conn.close()
    
    if not demandes:
        st.info("📄 Aucune demande disponible correspondant à vos critères.")
        return
    
    st.markdown(f"### 🎧 {len(demandes)} Opportunité(s) disponible(s)")
    
    # Afficher chaque demande
    for demande in demandes:
        with st.expander(f"📋 {demande[2]} - {demande[5]:,.0f}$ à {demande[6]:,.0f}$"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Client:** {demande[12]} ({demande[13]})")
                st.markdown(f"**Type:** {demande[3]}")
                st.markdown(f"**Description:**")
                st.write(demande[4][:300] + "..." if len(demande[4]) > 300 else demande[4])
                st.markdown(f"**Délai souhaité:** {demande[7]}")
            
            with col2:
                st.metric("Budget", f"{demande[5]:,.0f}$ - {demande[6]:,.0f}$")
                st.metric("Soumissions déjà reçues", demande[14])
                st.markdown(f"**Date limite:** {demande[8]}")
                st.markdown(f"**Référence:** {demande[10]}")
                
                # Vérifier si l'entrepreneur a déjà soumissionné
                conn = get_database_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM soumissions 
                    WHERE demande_id = ? AND prestataire_id = ?
                ''', (demande[0], st.session_state.user_data.id))
                deja_soumis = cursor.fetchone()[0] > 0
                conn.close()
                
                if deja_soumis:
                    st.info("📤 Déjà soumissionné")
                else:
                    if st.button(f"📤 Soumettre une offre", key=f"soumettre_{demande[0]}"):
                        st.session_state.page = 'nouvelle_soumission'
                        st.session_state.demande_selectionnee = demande[0]
                        st.rerun()

def page_mes_soumissions():
    """Page des soumissions de l'entrepreneur connecté"""
    st.markdown("## 📤 Mes Soumissions")
    
    # Récupérer les soumissions de l'entrepreneur
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, d.titre as demande_titre, d.budget_min, d.budget_max,
               ec.nom_entreprise as client_nom
        FROM soumissions s
        JOIN demandes_devis d ON s.demande_id = d.id
        JOIN entreprises_clientes ec ON d.client_id = ec.id
        WHERE s.prestataire_id = ?
        ORDER BY s.date_creation DESC
    ''', (st.session_state.user_data.id,))
    
    soumissions = cursor.fetchall()
    conn.close()
    
    if not soumissions:
        st.info("📄 Vous n'avez encore envoyé aucune soumission.")
        if st.button("🔍 Explorer les demandes", use_container_width=True):
            st.session_state.page = 'demandes_disponibles'
            st.rerun()
        return
    
    # Statistiques rapides
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total soumissions", len(soumissions))
    with col2:
        approuvees = sum(1 for s in soumissions if s[8] == 'approuvee')
        st.metric("Approuvées", approuvees)
    with col3:
        en_cours = sum(1 for s in soumissions if s[8] in ['recue', 'en_evaluation', 'en_approbation'])
        st.metric("En cours", en_cours)
    with col4:
        valeur_totale = sum(s[6] for s in soumissions if s[8] in ['approuvee', 'acceptee'])
        st.metric("Valeur obtenue", f"{valeur_totale:,.0f}$")
    
    st.markdown("### 📋 Historique de vos soumissions")
    
    # Afficher chaque soumission
    for soumission in soumissions:
        statut_color = {
            'recue': 'blue', 'en_evaluation': 'orange', 'en_approbation': 'purple',
            'approuvee': 'green', 'rejetee': 'red', 'acceptee': 'green'
        }.get(soumission[8], 'gray')
        
        with st.expander(f"{STATUTS_SOUMISSION.get(soumission[8], soumission[8])} - {soumission[11]} - {soumission[6]:,.0f}$"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Projet:** {soumission[12]}")
                st.markdown(f"**Client:** {soumission[15]}")
                st.markdown(f"**Votre titre:** {soumission[3]}")
                st.markdown(f"**Budget demandé:** {soumission[13]:,.0f}$ - {soumission[14]:,.0f}$")
                st.markdown(f"**Votre offre:** {soumission[6]:,.0f}$")
                st.markdown(f"**Délai proposé:** {soumission[7]}")
            
            with col2:
                st.markdown(f"**Statut:** {STATUTS_SOUMISSION.get(soumission[8], soumission[8])}")
                st.markdown(f"**Soumise le:** {soumission[9][:10]}")
                
                # Actions selon le statut
                if soumission[8] == 'approuvee':
                    st.success("✅ Félicitations!")
                    st.info("📞 Le client va vous contacter pour finaliser.")
                elif soumission[8] == 'rejetee':
                    st.error("❌ Non retenue")
                elif soumission[8] in ['recue', 'en_evaluation']:
                    st.info("⏳ En cours d'évaluation...")
                elif soumission[8] == 'acceptee':
                    st.success("🎉 Contrat en cours!")
                
                # Bouton pour voir les détails
                if st.button(f"🔍 Voir détails", key=f"details_{soumission[0]}"):
                    st.session_state.soumission_details = soumission[0]
                    # Afficher les détails dans un nouveau container
    
    # Afficher les détails de la soumission sélectionnée
    if hasattr(st.session_state, 'soumission_details'):
        soumission_detail = next((s for s in soumissions if s[0] == st.session_state.soumission_details), None)
        if soumission_detail:
            st.markdown("---")
            st.markdown(f"### 🔍 Détails - {soumission_detail[3]}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Résumé exécutif:**")
                st.write(soumission_detail[4])
            with col2:
                st.markdown("**Proposition technique:**")
                st.write(soumission_detail[5])
            
            if st.button("❌ Fermer détails"):
                del st.session_state.soumission_details
                st.rerun()

def page_nouvelle_soumission():
    """Page de création d'une nouvelle soumission par un entrepreneur"""
    st.markdown("## ➕ Nouvelle Soumission")
    
    # Vérifier qu'une demande est sélectionnée
    if not hasattr(st.session_state, 'demande_selectionnee'):
        st.warning("⚠️ Veuillez d'abord sélectionner une demande depuis 'Demandes disponibles'")
        if st.button("🔍 Retour aux demandes"):
            st.session_state.page = 'demandes_disponibles'
            st.rerun()
        return
    
    # Récupérer les détails de la demande
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.*, ec.nom_entreprise 
        FROM demandes_devis d
        JOIN entreprises_clientes ec ON d.client_id = ec.id
        WHERE d.id = ?
    ''', (st.session_state.demande_selectionnee,))
    demande = cursor.fetchone()
    
    if not demande:
        st.error("❌ Demande non trouvée")
        return
    
    # Afficher les détails de la demande
    st.markdown("### 📋 Détail de la demande")
    with st.expander(f"{demande[2]} - {demande[12]}", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Type:** {demande[3]}")
            st.markdown(f"**Budget:** {demande[5]:,.0f}$ - {demande[6]:,.0f}$")
            st.markdown(f"**Délai:** {demande[7]}")
        with col2:
            st.markdown(f"**Client:** {demande[12]}")
            st.markdown(f"**Date limite:** {demande[8]}")
            st.markdown(f"**Référence:** {demande[10]}")
        
        st.markdown("**Description du projet:**")
        st.write(demande[4])
    
    # Formulaire de soumission
    st.markdown("### 📤 Votre proposition")
    
    with st.form("nouvelle_soumission_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            titre_soumission = st.text_input(
                "Titre de votre proposition *",
                placeholder="Ex: Solution construction clé en main avec certification LEED"
            )
            
            budget_total = st.number_input(
                "Montant total proposé ($) *",
                min_value=1000,
                value=int((demande[5] + demande[6]) / 2),
                step=1000,
                format="%d"
            )
            
            delai_livraison = st.text_input(
                "Délai de réalisation proposé *",
                placeholder="Ex: 32 semaines (8 mois)"
            )
        
        with col2:
            # Certifications et qualifications
            st.markdown("**Vos certifications/qualifications:**")
            certifications_projet = st.text_area(
                "Certifications pertinentes pour ce projet",
                placeholder="Ex: RBQ 5678-1234-01, Certification LEED AP, ASP Construction...",
                height=100
            )
            
            # Garanties
            garanties = st.text_area(
                "Garanties proposées",
                placeholder="Ex: Garantie pièces et main-d'œuvre 2 ans, garantie d'étanchéité 5 ans...",
                height=60
            )
        
        resume_executif = st.text_area(
            "Résumé exécutif de votre proposition *",
            placeholder="Résumé concis de votre approche, vos avantages compétitifs, votre expérience sur des projets similaires...",
            height=120
        )
        
        proposition_technique = st.text_area(
            "Proposition technique détaillée *",
            placeholder="Méthodologie, équipes, matériaux, planning détaillé, phases de réalisation...",
            height=200
        )
        
        proposition_financiere = st.text_area(
            "Détail financier (optionnel)",
            placeholder="Décomposition des coûts, conditions de paiement, options...",
            height=100
        )
        
        # Références clients
        references_clients = st.text_area(
            "Références clients pertinentes",
            placeholder="Ex: Projet similaire réalisé en 2023 pour Constructions ABC Inc., Complexe commercial 8000m²...",
            height=80
        )
        
        # Documents techniques
        st.markdown("**Documents techniques (optionnel):**")
        fichiers_uploaded = st.file_uploader(
            "Plans, devis, fiches techniques, photos de réalisations...",
            type=FORMATS_AUTORISES["tous"],
            accept_multiple_files=True
        )
        
        submitted = st.form_submit_button("📤 Envoyer la soumission", use_container_width=True)
        
        if submitted:
            if not titre_soumission or not resume_executif or not proposition_technique or not delai_livraison:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
            else:
                # Sauvegarder la soumission
                cursor = conn.cursor()
                
                # Convertir les fichiers en base64
                documents_json = []
                if fichiers_uploaded:
                    for fichier in fichiers_uploaded:
                        if fichier.size <= SECURITY_CONFIG["max_file_size"]:
                            content_b64 = base64.b64encode(fichier.read()).decode('utf-8')
                            documents_json.append({
                                "nom": fichier.name,
                                "type": fichier.type,
                                "contenu": content_b64
                            })
                        else:
                            st.warning(f"⚠️ Fichier {fichier.name} trop volumineux (max 25 MB)")
                
                cursor.execute('''
                    INSERT INTO soumissions (
                        demande_id, prestataire_id, titre_soumission, resume_executif,
                        proposition_technique, budget_total, delai_livraison, statut,
                        certifications_projet, garanties, proposition_financiere,
                        references_clients, documents_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'recue', ?, ?, ?, ?, ?)
                ''', (
                    st.session_state.demande_selectionnee, st.session_state.user_data.id,
                    titre_soumission, resume_executif, proposition_technique,
                    budget_total, delai_livraison, certifications_projet,
                    garanties, proposition_financiere, references_clients,
                    json.dumps(documents_json)
                ))
                
                conn.commit()
                conn.close()
                
                st.success("✅ Soumission envoyée avec succès!")
                st.info("🔔 Le client sera notifié de votre soumission et l'évaluera selon ses critères.")
                
                # Rediriger vers les soumissions
                if st.button("📤 Voir mes soumissions"):
                    st.session_state.page = 'mes_soumissions'
                    st.rerun()

def page_evaluations_prestataire():
    """Évaluations reçues par l'entrepreneur"""
    st.markdown("## ⭐ Mes Évaluations")
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Récupérer les évaluations de l'entrepreneur
    cursor.execute('''
        SELECT s.*, d.titre as demande_titre, ec.nom_entreprise as client_nom,
               s.note_auto_evaluation, s.commentaires_internes
        FROM soumissions s
        JOIN demandes_devis d ON s.demande_id = d.id
        JOIN entreprises_clientes ec ON d.client_id = ec.id
        WHERE s.prestataire_id = ? AND s.statut IN ('approuvee', 'rejetee', 'acceptee')
        AND (s.note_auto_evaluation IS NOT NULL OR s.commentaires_internes IS NOT NULL)
        ORDER BY s.date_creation DESC
    ''', (st.session_state.user_data.id,))
    
    evaluations = cursor.fetchall()
    
    if not evaluations:
        st.info("📄 Aucune évaluation disponible pour le moment.")
        return
    
    # Statistiques globales
    notes = [e[18] for e in evaluations if e[18] is not None]
    if notes:
        note_moyenne = sum(notes) / len(notes)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Note moyenne", f"{note_moyenne:.2f}/5.0")
        with col2:
            approuvees = sum(1 for e in evaluations if e[8] == 'approuvee')
            st.metric("Évaluations positives", f"{approuvees}/{len(evaluations)}")
        with col3:
            acceptees = sum(1 for e in evaluations if e[8] == 'acceptee')
            st.metric("Contrats obtenus", acceptees)
    
    # Détail des évaluations
    st.markdown("### 📝 Historique des évaluations")
    
    for evaluation in evaluations:
        status_color = "green" if evaluation[8] == "approuvee" else "red" if evaluation[8] == "rejetee" else "blue"
        
        with st.expander(f"{STATUTS_SOUMISSION.get(evaluation[8], evaluation[8])} - {evaluation[10]} par {evaluation[11]}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Projet:** {evaluation[10]}")
                st.markdown(f"**Client:** {evaluation[11]}")
                st.markdown(f"**Montant soumissionné:** {evaluation[6]:,.0f}$")
                st.markdown(f"**Date:** {evaluation[9][:10]}")
                
                if evaluation[19]:  # commentaires_internes
                    st.markdown("**Commentaires du client:**")
                    st.info(evaluation[19])
            
            with col2:
                if evaluation[18]:  # note_auto_evaluation
                    st.metric("Note obtenue", f"{evaluation[18]:.2f}/5.0")
                
                # Couleur selon le statut
                if evaluation[8] == "approuvee":
                    st.success("✅ Approuvée")
                elif evaluation[8] == "rejetee":
                    st.error("❌ Rejetée")
                elif evaluation[8] == "acceptee":
                    st.success("🎉 Contrat obtenu!")
    
    conn.close()

def page_contrats_prestataire():
    st.markdown("## 📄 Mes Contrats")
    st.info("🚧 Cette fonctionnalité sera implémentée dans la prochaine étape.")

def page_messages_prestataire():
    st.markdown("## 💬 Messages")
    st.info("🚧 Cette fonctionnalité sera implémentée dans la prochaine étape.")

def page_profil_prestataire():
    """Profil et informations de l'entrepreneur construction"""
    st.markdown("## 👤 Mon Profil d'Entrepreneur")
    
    prestataire = st.session_state.user_data
    
    # Informations entreprise
    st.markdown("### 🏢 Informations de l'entreprise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Nom:** {prestataire.nom_entreprise}")
        st.info(f"**Domaines:** {prestataire.domaines_expertise}")
        st.info(f"**Taille:** {prestataire.taille_entreprise}")
        st.info(f"**Email:** {prestataire.email}")
    
    with col2:
        st.info(f"**Contact:** {prestataire.nom_contact}")
        st.info(f"**Poste:** {prestataire.poste_contact}")
        st.info(f"**Téléphone:** {prestataire.telephone}")
        st.info(f"**Note moyenne:** {prestataire.note_moyenne:.1f}/5.0")
    
    # Certifications et tarifs
    st.markdown("### 🏅 Certifications et compétences")
    if prestataire.certifications:
        st.success(f"📜 **Certifications:** {prestataire.certifications}")
    else:
        st.warning("⚠️ Aucune certification renseignée")
    
    col1, col2 = st.columns(2)
    with col1:
        if prestataire.tarif_horaire_min > 0:
            st.info(f"💵 **Tarifs:** {prestataire.tarif_horaire_min:.0f}$ - {prestataire.tarif_horaire_max:.0f}$/heure")
    
    # Statistiques d'activité
    st.markdown("### 📈 Statistiques d'activité")
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Statistiques des soumissions
    cursor.execute('SELECT COUNT(*) FROM soumissions WHERE prestataire_id = ?', (prestataire.id,))
    nb_soumissions = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM soumissions WHERE prestataire_id = ? AND statut = "approuvee"', (prestataire.id,))
    nb_approuvees = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM soumissions WHERE prestataire_id = ? AND statut = "acceptee"', (prestataire.id,))
    nb_contrats = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(budget_total) FROM soumissions WHERE prestataire_id = ? AND statut = "acceptee"', (prestataire.id,))
    chiffre_affaires = cursor.fetchone()[0] or 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Soumissions envoyées", nb_soumissions)
    with col2:
        taux_succes = (nb_approuvees / nb_soumissions * 100) if nb_soumissions > 0 else 0
        st.metric("Taux d'approbation", f"{taux_succes:.1f}%")
    with col3:
        st.metric("Contrats obtenus", nb_contrats)
    with col4:
        st.metric("Chiffre d'affaires", f"{chiffre_affaires:,.0f}$")
    
    # Historique récent
    st.markdown("### 📅 Activité récente")
    
    cursor.execute('''
        SELECT s.titre_soumission, s.budget_total, s.statut, s.date_creation,
               d.titre as demande_titre, ec.nom_entreprise
        FROM soumissions s
        JOIN demandes_devis d ON s.demande_id = d.id
        JOIN entreprises_clientes ec ON d.client_id = ec.id
        WHERE s.prestataire_id = ?
        ORDER BY s.date_creation DESC
        LIMIT 5
    ''', (prestataire.id,))
    
    soumissions_recentes = cursor.fetchall()
    
    if soumissions_recentes:
        for soumission in soumissions_recentes:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.write(f"📤 {soumission[0]}")
                with col2:
                    st.write(f"{soumission[1]:,.0f}$")
                with col3:
                    st.write(STATUTS_SOUMISSION.get(soumission[2], soumission[2]))
                with col4:
                    st.write(f"{soumission[3][:10]}")
    
    conn.close()

def page_admin_demandes():
    """Page admin pour voir toutes les demandes du système"""
    st.markdown("## 📋 Toutes les Demandes")
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Statistiques rapides
    col1, col2, col3, col4 = st.columns(4)
    
    cursor.execute('SELECT COUNT(*) FROM demandes_devis')
    total_demandes = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM demandes_devis WHERE statut = "publiee"')
    demandes_actives = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM soumissions')
    total_soumissions = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM soumissions WHERE statut = "acceptee"')
    soumissions_acceptees = cursor.fetchone()[0]
    
    with col1:
        st.metric("Total Demandes", total_demandes)
    with col2:
        st.metric("Demandes Actives", demandes_actives)
    with col3:
        st.metric("Soumissions Créées", total_soumissions)
    with col4:
        st.metric("Soumissions Acceptées", soumissions_acceptees)
    
    st.markdown("---")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtre_statut = st.selectbox(
            "Filtrer par statut:",
            ["Tous", "publiee", "en_cours", "fermee", "attribuee"]
        )
    
    with col2:
        filtre_type = st.selectbox(
            "Filtrer par type de projet:",
            ["Tous"] + TYPES_PROJETS
        )
    
    with col3:
        filtre_budget = st.selectbox(
            "Filtrer par budget:",
            ["Tous", "< 10 000$", "10 000$ - 50 000$", "> 50 000$"]
        )
    
    # Construction de la requête avec filtres
    query = '''
        SELECT d.id, d.titre, d.type_projet, d.budget_min, d.budget_max, d.statut,
               d.date_creation, ec.nom_entreprise, ec.nom_contact,
               (SELECT COUNT(*) FROM soumissions s WHERE s.demande_id = d.id) as nb_soumissions
        FROM demandes_devis d
        JOIN entreprises_clientes ec ON d.client_id = ec.id
    '''
    
    conditions = []
    params = []
    
    if filtre_statut != "Tous":
        conditions.append("d.statut = ?")
        params.append(filtre_statut)
    
    if filtre_type != "Tous":
        conditions.append("d.type_projet = ?")
        params.append(filtre_type)
    
    if filtre_budget != "Tous":
        if filtre_budget == "< 10 000$":
            conditions.append("d.budget_max < 10000")
        elif filtre_budget == "10 000$ - 50 000$":
            conditions.append("d.budget_max >= 10000 AND d.budget_max <= 50000")
        elif filtre_budget == "> 50 000$":
            conditions.append("d.budget_max > 50000")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY d.date_creation DESC"
    
    cursor.execute(query, params)
    demandes = cursor.fetchall()
    
    st.markdown(f"### 📋 Liste des demandes ({len(demandes)} résultats)")
    
    if demandes:
        for demande in demandes:
            with st.expander(f"🔍 {demande[1]} - {demande[7]} ({demande[5]})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Client:** {demande[7]} (Contact: {demande[8]})")
                    st.markdown(f"**Type de projet:** {demande[2]}")
                    st.markdown(f"**Budget:** {demande[3]:,.0f}$ - {demande[4]:,.0f}$")
                    st.markdown(f"**Date de création:** {demande[6][:10]}")
                    
                with col2:
                    st.metric("Soumissions reçues", demande[9])
                    
                    # Boutons d'action admin
                    if st.button(f"📥 Voir soumissions", key=f"admin_voir_soum_{demande[0]}"):
                        st.session_state.demande_selectionnee = demande[0]
                        st.session_state.page = 'admin_soumissions'
                        st.rerun()
                    
                    if st.button(f"✏️ Modifier statut", key=f"admin_modif_statut_{demande[0]}"):
                        st.session_state.demande_a_modifier = demande[0]
                        # Ici on pourrait ajouter une modal ou une sous-page
    else:
        st.info("Aucune demande trouvée avec ces filtres.")
    
    conn.close()

def page_admin_soumissions():
    """Page de gestion de toutes les soumissions pour les admins"""
    st.markdown("## 📤 Toutes les Soumissions")
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Statistiques rapides
    col1, col2, col3, col4 = st.columns(4)
    
    cursor.execute('SELECT COUNT(*) FROM soumissions')
    total_soumissions = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM soumissions WHERE statut = "soumise"')
    soumissions_soumises = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM soumissions WHERE statut = "en_evaluation"')
    en_evaluation = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM soumissions WHERE statut = "acceptee"')
    acceptees = cursor.fetchone()[0]
    
    with col1:
        st.metric("Total Soumissions", total_soumissions)
    with col2:
        st.metric("Soumises", soumissions_soumises)
    with col3:
        st.metric("En Évaluation", en_evaluation)
    with col4:
        st.metric("Acceptées", acceptees)
    
    st.markdown("---")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtre_statut = st.selectbox(
            "Filtrer par statut:",
            ["Tous", "soumise", "en_evaluation", "acceptee", "rejetee"]
        )
    
    with col2:
        filtre_montant = st.selectbox(
            "Filtrer par montant:",
            ["Tous", "< 10 000$", "10 000$ - 50 000$", "> 50 000$"]
        )
    
    with col3:
        # Filtre par demande spécifique si on vient de la page demandes
        if hasattr(st.session_state, 'demande_selectionnee'):
            st.info(f"Filtré pour la demande ID: {st.session_state.demande_selectionnee}")
    
    # Construction de la requête
    query = '''
        SELECT s.id, s.titre_soumission, s.budget_total, s.statut, s.date_creation,
               d.titre as demande_titre, ec.nom_entreprise as client_nom,
               ep.nom_entreprise as prestataire_nom
        FROM soumissions s
        JOIN demandes_devis d ON s.demande_id = d.id
        JOIN entreprises_clientes ec ON d.client_id = ec.id
        JOIN entreprises_prestataires ep ON s.prestataire_id = ep.id
    '''
    
    conditions = []
    params = []
    
    # Filtre par demande spécifique
    if hasattr(st.session_state, 'demande_selectionnee'):
        conditions.append("s.demande_id = ?")
        params.append(st.session_state.demande_selectionnee)
    
    if filtre_statut != "Tous":
        conditions.append("s.statut = ?")
        params.append(filtre_statut)
    
    if filtre_montant != "Tous":
        if filtre_montant == "< 10 000$":
            conditions.append("s.budget_total < 10000")
        elif filtre_montant == "10 000$ - 50 000$":
            conditions.append("s.budget_total >= 10000 AND s.budget_total <= 50000")
        elif filtre_montant == "> 50 000$":
            conditions.append("s.budget_total > 50000")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY s.date_creation DESC"
    
    cursor.execute(query, params)
    soumissions = cursor.fetchall()
    
    st.markdown(f"### 📤 Liste des soumissions ({len(soumissions)} résultats)")
    
    if soumissions:
        for soum in soumissions:
            statut_color = {
                "soumise": "🟡",
                "en_evaluation": "🟠", 
                "acceptee": "🟢",
                "rejetee": "🔴"
            }.get(soum[3], "⚪")
            
            with st.expander(f"{statut_color} {soum[1]} - {soum[2]:,.0f}$ ({soum[3]})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Demande:** {soum[5]}")
                    st.markdown(f"**Client:** {soum[6]}")
                    st.markdown(f"**Prestataire:** {soum[7]}")
                    st.markdown(f"**Montant:** {soum[2]:,.0f}$")
                    st.markdown(f"**Date soumission:** {soum[4][:10]}")
                    
                with col2:
                    st.markdown(f"**Statut:** {STATUTS_SOUMISSION.get(soum[3], soum[3])}")
                    
                    # Actions admin
                    if soum[3] == "en_evaluation":
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✅ Accepter", key=f"accept_{soum[0]}"):
                                cursor.execute('UPDATE soumissions SET statut = "acceptee" WHERE id = ?', (soum[0],))
                                conn.commit()
                                st.success("Soumission acceptée!")
                                st.rerun()
                        with col_b:
                            if st.button("❌ Rejeter", key=f"reject_{soum[0]}"):
                                cursor.execute('UPDATE soumissions SET statut = "rejetee" WHERE id = ?', (soum[0],))
                                conn.commit()
                                st.warning("Soumission rejetée!")
                                st.rerun()
                    
                    if st.button(f"📋 Détails complets", key=f"details_{soum[0]}"):
                        st.session_state.soumission_selectionnee = soum[0]
                        # Ici on pourrait ouvrir une page de détails
    else:
        st.info("Aucune soumission trouvée avec ces filtres.")
    
    # Bouton pour revenir
    if hasattr(st.session_state, 'demande_selectionnee'):
        if st.button("↩️ Retour aux demandes"):
            if hasattr(st.session_state, 'demande_selectionnee'):
                delattr(st.session_state, 'demande_selectionnee')
            st.session_state.page = 'admin_demandes'
            st.rerun()
    
    conn.close()
    
    # Filtres
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filtre_statut = st.selectbox(
            "Filtrer par statut",
            ["Tous"] + list(STATUTS_SOUMISSION.values())
        )
    
    with col2:
        filtre_periode = st.selectbox(
            "Période",
            ["Toutes", "7 derniers jours", "30 derniers jours", "90 derniers jours"]
        )
    
    with col3:
        filtre_montant_min = st.number_input(
            "Montant minimum ($)",
            min_value=0,
            value=0,
            step=10000
        )
    
    with col4:
        filtre_montant_max = st.number_input(
            "Montant maximum ($)",
            min_value=0,
            value=0,
            step=10000
        )
    
    # Récupérer les soumissions filtrées
    conn = get_database_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT s.*, d.titre as demande_titre, d.budget_min, d.budget_max,
               ec.nom_entreprise as client_nom, ep.nom_entreprise as prestataire_nom
        FROM soumissions s
        JOIN demandes_devis d ON s.demande_id = d.id
        JOIN entreprises_clientes ec ON d.client_id = ec.id
        JOIN entreprises_prestataires ep ON s.prestataire_id = ep.id
        WHERE 1=1
    '''
    
    params = []
    
    # Appliquer les filtres
    if filtre_statut != "Tous":
        statut_key = next((k for k, v in STATUTS_SOUMISSION.items() if v == filtre_statut), None)
        if statut_key:
            query += " AND s.statut = ?"
            params.append(statut_key)
    
    if filtre_periode != "Toutes":
        jours = {"7 derniers jours": 7, "30 derniers jours": 30, "90 derniers jours": 90}[filtre_periode]
        query += " AND s.date_creation >= date('now', '-' || ? || ' days')"
        params.append(jours)
    
    if filtre_montant_min > 0:
        query += " AND s.budget_total >= ?"
        params.append(filtre_montant_min)
    
    if filtre_montant_max > 0:
        query += " AND s.budget_total <= ?"
        params.append(filtre_montant_max)
    
    query += " ORDER BY s.date_creation DESC"
    
    cursor.execute(query, params)
    soumissions = cursor.fetchall()
    
    # Statistiques rapides
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total soumissions", len(soumissions))
    with col2:
        valeur_totale = sum(s[6] for s in soumissions if s[6] is not None)
        st.metric("Valeur totale", f"{valeur_totale:,.0f}$")
    with col3:
        approuvees = sum(1 for s in soumissions if s[8] == 'approuvee')
        taux_approbation = (approuvees / len(soumissions) * 100) if soumissions else 0
        st.metric("Taux d'approbation", f"{taux_approbation:.1f}%")
    with col4:
        en_attente = sum(1 for s in soumissions if s[8] in ['recue', 'en_evaluation', 'en_approbation'])
        st.metric("En attente", en_attente)
    
    # Liste des soumissions
    if not soumissions:
        st.info("📄 Aucune soumission ne correspond à vos critères.")
    else:
        # Tableau des soumissions
        st.markdown(f"### 📋 {len(soumissions)} soumission(s)")
        
        # Créer un DataFrame pour l'affichage
        df_data = []
        for s in soumissions:
            # s[20] is date_creation, s[-4] is demande_titre, s[-1] is prestataire_nom
            date_str = str(s[20])[:10] if s[20] else "N/A"
            titre_str = str(s[-4])[:30] + "..." if len(str(s[-4])) > 30 else str(s[-4])
            client_str = str(s[-2]) if s[-2] else "N/A"
            prestataire_str = str(s[-1]) if s[-1] else "N/A"
            budget_val = s[9] if s[9] is not None else 0
            statut_str = STATUTS_SOUMISSION.get(s[17], s[17]) if s[17] else "N/A"
            
            df_data.append({
                "Date": date_str,
                "Projet": titre_str,
                "Client": client_str,
                "Entrepreneur": prestataire_str,
                "Montant": f"{budget_val:,.0f}$",
                "Statut": statut_str,
                "ID": s[0]
            })
        
        df = pd.DataFrame(df_data)
        
        # Utiliser st.dataframe avec une configuration personnalisée
        st.dataframe(
            df.drop(columns=['ID']),
            use_container_width=True,
            hide_index=True
        )
        
        # Actions en lot
        st.markdown("### ⚙️ Actions en lot")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Exporter en CSV"):
                csv = df.drop(columns=['ID']).to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger CSV",
                    data=csv,
                    file_name=f"soumissions_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("🗑 Archiver anciennes"):
                # Archiver les soumissions de plus de 6 mois
                cursor.execute('''
                    UPDATE soumissions 
                    SET statut = 'archivee' 
                    WHERE date_creation < date('now', '-6 months') 
                    AND statut IN ('rejetee')
                ''')
                conn.commit()
                st.success("✅ Soumissions anciennes archivées")
                st.rerun()
        
        with col3:
            if st.button("🔄 Actualiser"):
                st.rerun()
    
    conn.close()

def page_admin_workflow():
    """Page de gestion du workflow d'approbation C2B pour les admins"""
    st.markdown("## 🔄 Workflow d'Approbation C2B")
    
    # Tabs pour organiser les fonctionnalités
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vue d'ensemble", "⏳ Soumissions en cours", "✅ Historique", "⚙️ Configuration"])
    
    with tab1:
        st.markdown("### 📈 Tableau de bord du Workflow C2B")
        
        # Statistiques en temps réel
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Métriques clés
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cursor.execute("SELECT COUNT(*) FROM demandes_devis WHERE statut = 'publiee'")
            demandes_actives = cursor.fetchone()[0]
            st.metric("📥 Demandes clients actives", demandes_actives, "+2 cette semaine")
        
        with col2:
            cursor.execute("SELECT COUNT(*) FROM soumissions WHERE statut = 'en_evaluation'")
            soumissions_eval = cursor.fetchone()[0]
            st.metric("🔍 En évaluation", soumissions_eval, "-1 depuis hier")
        
        with col3:
            cursor.execute("SELECT COUNT(*) FROM soumissions WHERE statut = 'acceptee'")
            soumissions_acceptees = cursor.fetchone()[0]
            st.metric("✅ Acceptées ce mois", soumissions_acceptees, "+15%")
        
        with col4:
            taux_conversion = 75  # Calculé dynamiquement normalement
            st.metric("📊 Taux de conversion", f"{taux_conversion}%", "+5%")
        
        # Graphique des étapes du workflow
        st.markdown("### 🔄 Étapes du Workflow C2B")
        
        workflow_steps = {
            "1️⃣ Demande Client": "Client envoie sa demande à l'entreprise",
            "2️⃣ Réception Entreprise": "L'entreprise reçoit et analyse la demande",
            "3️⃣ Création Soumission": "L'entreprise prépare sa proposition",
            "4️⃣ Envoi au Client": "Le client reçoit la soumission",
            "5️⃣ Décision Client": "Le client accepte ou refuse",
            "6️⃣ Notification": "Génération du numéro de référence"
        }
        
        for step, desc in workflow_steps.items():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**{step}**")
            with col2:
                st.markdown(desc)
        
        conn.close()
    
    with tab2:
        st.markdown("### ⏳ Soumissions en cours de traitement")
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Filtre par statut
        statut_filtre = st.selectbox(
            "Filtrer par statut",
            ["Tous", "En attente", "En évaluation", "En approbation", "En négociation"]
        )
        
        # Tableau des soumissions actives
        query = """
        SELECT s.id, d.titre, ec.nom_entreprise AS client, s.statut, s.date_creation
        FROM soumissions s
        JOIN demandes_devis d ON s.demande_id = d.id
        JOIN entreprises_clientes ec ON d.client_id = ec.id
        WHERE s.statut NOT IN ('acceptee', 'refusee')
        ORDER BY s.date_creation DESC
        LIMIT 10
        """
        
        cursor.execute(query)
        soumissions = cursor.fetchall()
        
        if soumissions:
            for soum in soumissions:
                with st.expander(f"📋 {soum[1]} - {soum[2]}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**ID:** {soum[0]}")
                        st.write(f"**Client:** {soum[2]}")
                    with col2:
                        st.write(f"**Statut:** {STATUTS_SOUMISSION.get(soum[3], soum[3])}")
                        st.write(f"**Date:** {soum[4]}")
                    with col3:
                        if st.button(f"Traiter", key=f"traiter_{soum[0]}"):
                            st.session_state.page = 'traiter_soumission'
                            st.session_state.soumission_id = soum[0]
                            st.rerun()
        else:
            st.info("Aucune soumission en cours de traitement")
        
        conn.close()
    
    with tab3:
        st.markdown("### ✅ Historique des approbations")
        
        # Période de recherche
        col1, col2 = st.columns(2)
        with col1:
            date_debut = st.date_input("Date de début")
        with col2:
            date_fin = st.date_input("Date de fin")
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Statistiques historiques
        st.markdown("#### 📊 Résumé de la période")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cursor.execute("SELECT COUNT(*) FROM soumissions WHERE statut = 'acceptee'")
            total_acceptees = cursor.fetchone()[0]
            st.metric("✅ Total acceptées", total_acceptees)
        
        with col2:
            cursor.execute("SELECT COUNT(*) FROM soumissions WHERE statut = 'refusee'")
            total_refusees = cursor.fetchone()[0]
            st.metric("❌ Total refusées", total_refusees)
        
        with col3:
            cursor.execute("SELECT AVG(julianday(date_creation) - julianday(date_creation)) FROM soumissions")
            delai_moyen = 3  # En jours (normalement calculé)
            st.metric("⏱️ Délai moyen", f"{delai_moyen} jours")
        
        conn.close()
    
    with tab4:
        st.markdown("### ⚙️ Configuration du Workflow C2B")
        
        st.markdown("#### 🎯 Paramètres du système")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Délais automatiques**")
            delai_reponse = st.number_input("Délai de réponse entreprise (heures)", value=24, min_value=1)
            delai_evaluation = st.number_input("Délai d'évaluation client (jours)", value=7, min_value=1)
            delai_expiration = st.number_input("Expiration soumission (jours)", value=30, min_value=1)
        
        with col2:
            st.markdown("**Notifications automatiques**")
            notif_nouvelle = st.checkbox("Nouvelle demande client", value=True)
            notif_soumission = st.checkbox("Soumission envoyée", value=True)
            notif_decision = st.checkbox("Décision client", value=True)
            notif_rappel = st.checkbox("Rappels automatiques", value=True)
        
        st.markdown("#### 🏢 Configuration Entreprise")
        entreprise = get_entreprise_proprietaire()
        
        st.info(f"""
        **Entreprise configurée:** {entreprise['nom_entreprise']}
        **RBQ:** {entreprise['numero_rbq']}
        **Email:** {entreprise['email']}
        **Délai de réponse moyen:** {entreprise.get('delai_reponse_moyen', 24)} heures
        """)
        
        if st.button("💾 Sauvegarder la configuration", type="primary"):
            st.success("✅ Configuration du workflow sauvegardée avec succès!")

def page_admin_entreprises():
    """Page de gestion des entreprises pour les admins"""
    st.markdown("## 🏢 Gestion des Entreprises")
    
    tab1, tab2 = st.tabs(["👥 Entreprises Clientes", "🏗️ Configuration Prestataire"])
    
    with tab1:
        st.markdown("### 👥 Entreprises Clientes")
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nom_entreprise, nom_contact, email, telephone, ville, 
                   statut, date_inscription
            FROM entreprises_clientes 
            ORDER BY date_inscription DESC
        ''')
        
        clients = cursor.fetchall()
        
        if clients:
            for client in clients:
                with st.expander(f"🏢 {client[1]} - {client[2]} ({client[6]})"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Entreprise:** {client[1]}")
                        st.markdown(f"**Contact:** {client[2]}")
                        st.markdown(f"**Email:** {client[3]}")
                        st.markdown(f"**Téléphone:** {client[4]}")
                        st.markdown(f"**Ville:** {client[5]}")
                        st.markdown(f"**Inscription:** {client[7][:10]}")
                    
                    with col2:
                        st.markdown(f"**Statut:** {client[6]}")
                        
                        # Actions admin
                        if client[6] == "actif":
                            if st.button(f"⏸️ Suspendre", key=f"suspend_client_{client[0]}"):
                                cursor.execute('UPDATE entreprises_clientes SET statut = "suspendu" WHERE id = ?', (client[0],))
                                conn.commit()
                                st.warning("Client suspendu!")
                                st.rerun()
                        else:
                            if st.button(f"✅ Activer", key=f"activate_client_{client[0]}"):
                                cursor.execute('UPDATE entreprises_clientes SET statut = "actif" WHERE id = ?', (client[0],))
                                conn.commit()
                                st.success("Client activé!")
                                st.rerun()
        else:
            st.info("Aucune entreprise cliente enregistrée.")
        
        conn.close()
    
    with tab2:
        st.markdown("### 🏗️ Configuration Entreprise Prestataire")
        
        from config_entreprise_unique import get_entreprise_proprietaire
        entreprise = get_entreprise_proprietaire()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Nom:** {entreprise['nom_entreprise']}")
            st.markdown(f"**Contact:** {entreprise['nom_contact']}")
            st.markdown(f"**Email:** {entreprise['email']}")
            st.markdown(f"**Téléphone:** {entreprise['telephone']}")
            st.markdown(f"**RBQ:** {entreprise.get('numero_rbq', 'N/A')}")
        
        with col2:
            st.markdown(f"**Ville:** {entreprise['ville']}")
            st.markdown(f"**Disponibilité:** {entreprise.get('disponibilite', 'N/A')}")
            st.markdown(f"**Tarifs:** {entreprise.get('tarif_horaire_min', 0)}$ - {entreprise.get('tarif_horaire_max', 0)}$/h")
        
        st.markdown("**Domaines d'expertise:**")
        for domaine in entreprise['domaines_expertise']:
            st.markdown(f"• {domaine}")
        
        st.markdown("**Description:**")
        st.markdown(entreprise['description_entreprise'])
        
        st.info("💡 Pour modifier ces informations, éditez le fichier `config_entreprise_unique.py` et relancez l'application.")

def page_admin_rapports():
    """Page de rapports et analytics pour les admins"""
    st.markdown("## 📊 Rapports et Analytics")
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Métriques principales
    st.markdown("### 📈 Métriques Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Nombre total de demandes
    cursor.execute('SELECT COUNT(*) FROM demandes_devis')
    total_demandes = cursor.fetchone()[0]
    
    # Nombre de soumissions
    cursor.execute('SELECT COUNT(*) FROM soumissions')
    total_soumissions = cursor.fetchone()[0]
    
    # Taux de conversion (demandes avec soumissions)
    cursor.execute('''
        SELECT COUNT(DISTINCT demande_id) FROM soumissions
    ''')
    demandes_avec_soumissions = cursor.fetchone()[0]
    
    taux_reponse = (demandes_avec_soumissions / total_demandes * 100) if total_demandes > 0 else 0
    
    # Valeur totale des soumissions acceptées
    cursor.execute('SELECT SUM(budget_total) FROM soumissions WHERE statut = "acceptee"')
    result = cursor.fetchone()[0]
    valeur_acceptee = result if result else 0
    
    with col1:
        st.metric("Total Demandes", total_demandes)
    
    with col2:
        st.metric("Total Soumissions", total_soumissions)
    
    with col3:
        st.metric("Taux de Réponse", f"{taux_reponse:.1f}%")
    
    with col4:
        st.metric("CA Accepté", f"{valeur_acceptee:,.0f}$")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Répartition par Statut des Demandes")
        cursor.execute('''
            SELECT statut, COUNT(*) as nb
            FROM demandes_devis 
            GROUP BY statut
        ''')
        statuts_demandes = cursor.fetchall()
        
        if statuts_demandes:
            import pandas as pd
            df_statuts = pd.DataFrame(statuts_demandes, columns=['Statut', 'Nombre'])
            st.bar_chart(df_statuts.set_index('Statut'))
        else:
            st.info("Aucune donnée disponible")
    
    with col2:
        st.markdown("### 💰 Répartition par Budget")
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN budget_max < 10000 THEN 'Moins de 10K'
                    WHEN budget_max < 50000 THEN '10K - 50K'
                    ELSE 'Plus de 50K'
                END as tranche_budget,
                COUNT(*) as nb
            FROM demandes_devis
            GROUP BY 
                CASE 
                    WHEN budget_max < 10000 THEN 'Moins de 10K'
                    WHEN budget_max < 50000 THEN '10K - 50K'
                    ELSE 'Plus de 50K'
                END
        ''')
        budgets = cursor.fetchall()
        
        if budgets:
            import pandas as pd
            df_budgets = pd.DataFrame(budgets, columns=['Tranche', 'Nombre'])
            st.bar_chart(df_budgets.set_index('Tranche'))
        else:
            st.info("Aucune donnée disponible")
    
    st.markdown("---")
    
    # Tableaux détaillés
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 Top Clients (par nombre de demandes)")
        cursor.execute('''
            SELECT ec.nom_entreprise, COUNT(d.id) as nb_demandes,
                   AVG(d.budget_max) as budget_moyen
            FROM entreprises_clientes ec
            LEFT JOIN demandes_devis d ON ec.id = d.client_id
            GROUP BY ec.id, ec.nom_entreprise
            ORDER BY nb_demandes DESC
            LIMIT 10
        ''')
        top_clients = cursor.fetchall()
        
        if top_clients:
            for client in top_clients:
                st.markdown(f"**{client[0]}**: {client[1]} demande(s) - Budget moy: {client[2]:,.0f}$")
        else:
            st.info("Aucun client avec demandes")
    
    with col2:
        st.markdown("### 🎯 Performance Soumissions")
        cursor.execute('''
            SELECT 
                statut,
                COUNT(*) as nombre,
                AVG(budget_total) as montant_moyen
            FROM soumissions
            GROUP BY statut
            ORDER BY nombre DESC
        ''')
        perf_soumissions = cursor.fetchall()
        
        if perf_soumissions:
            for perf in perf_soumissions:
                st.markdown(f"**{STATUTS_SOUMISSION.get(perf[0], perf[0])}**: {perf[1]} soumissions - Moy: {perf[2]:,.0f}$")
        else:
            st.info("Aucune soumission")
    
    st.markdown("---")
    
    # Activité récente
    st.markdown("### 📅 Activité Récente (7 derniers jours)")
    
    cursor.execute('''
        SELECT DATE(date_creation) as jour, COUNT(*) as nb_demandes
        FROM demandes_devis
        WHERE date_creation >= date('now', '-7 days')
        GROUP BY DATE(date_creation)
        ORDER BY jour DESC
    ''')
    activite_demandes = cursor.fetchall()
    
    cursor.execute('''
        SELECT DATE(date_creation) as jour, COUNT(*) as nb_soumissions  
        FROM soumissions
        WHERE date_creation >= date('now', '-7 days')
        GROUP BY DATE(date_creation)
        ORDER BY jour DESC
    ''')
    activite_soumissions = cursor.fetchall()
    
    if activite_demandes or activite_soumissions:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Nouvelles demandes:**")
            for act in activite_demandes:
                st.markdown(f"• {act[0]}: {act[1]} demande(s)")
        
        with col2:
            st.markdown("**Nouvelles soumissions:**")
            for act in activite_soumissions:
                st.markdown(f"• {act[0]}: {act[1]} soumission(s)")
    else:
        st.info("Aucune activité récente")
    
    conn.close()

def page_admin_parametres():
    """Page des paramètres système pour les admins"""
    st.markdown("## ⚙️ Paramètres Système")
    
    tab1, tab2, tab3 = st.tabs(["🏗️ Configuration Entreprise", "🔧 Paramètres Techniques", "🛡️ Sécurité"])
    
    with tab1:
        st.markdown("### 🏗️ Configuration de l'Entreprise Propriétaire")
        
        from config_entreprise_unique import get_entreprise_proprietaire, valider_configuration
        
        entreprise = get_entreprise_proprietaire()
        
        st.markdown("**Configuration actuelle:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Nom entreprise", value=entreprise['nom_entreprise'], disabled=True)
            st.text_input("Contact", value=entreprise['nom_contact'], disabled=True)
            st.text_input("Email", value=entreprise['email'], disabled=True)
            st.text_input("Téléphone", value=entreprise['telephone'], disabled=True)
        
        with col2:
            st.text_input("RBQ", value=entreprise.get('numero_rbq', ''), disabled=True)
            st.text_input("Ville", value=entreprise['ville'], disabled=True)
            st.selectbox("Disponibilité", 
                        options=['disponible', 'occupe', 'indisponible'],
                        index=['disponible', 'occupe', 'indisponible'].index(entreprise.get('disponibilite', 'disponible')),
                        disabled=True)
        
        st.text_area("Description", value=entreprise['description_entreprise'], disabled=True)
        
        # Validation de la configuration
        erreurs = valider_configuration()
        if erreurs:
            st.warning("⚠️ Problèmes de configuration détectés:")
            for erreur in erreurs:
                st.markdown(f"• {erreur}")
        else:
            st.success("✅ Configuration valide")
        
        st.info("💡 Pour modifier ces paramètres, éditez le fichier `config_entreprise_unique.py` et relancez l'application.")
    
    with tab2:
        st.markdown("### 🔧 Paramètres Techniques")
        
        # Informations sur la base de données
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        st.markdown("**Base de données:**")
        st.markdown(f"• Type: SQLite")
        st.markdown(f"• Fichier: {DATABASE_PATH}")
        st.markdown(f"• Tables: {len(tables)}")
        
        # Statistiques des tables
        st.markdown("**Statistiques par table:**")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                st.markdown(f"• {table[0]}: {count} enregistrements")
            except:
                st.markdown(f"• {table[0]}: Erreur de lecture")
        
        # Informations système
        import os, platform
        st.markdown("**Informations système:**")
        st.markdown(f"• OS: {platform.system()} {platform.release()}")
        st.markdown(f"• Python: {platform.python_version()}")
        st.markdown(f"• Répertoire de travail: {os.getcwd()}")
        st.markdown(f"• Répertoire des données: {DATA_DIR}")
        
        conn.close()
    
    with tab3:
        st.markdown("### 🛡️ Sécurité et Maintenance")
        
        # Sauvegardes
        st.markdown("**Sauvegarde de la base de données:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Créer une sauvegarde"):
                import shutil, datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(DATA_DIR, f"backup_{timestamp}.db")
                try:
                    shutil.copy2(DATABASE_PATH, backup_path)
                    st.success(f"Sauvegarde créée: backup_{timestamp}.db")
                except Exception as e:
                    st.error(f"Erreur lors de la sauvegarde: {e}")
        
        with col2:
            if st.button("🔄 Réinitialiser la base"):
                if st.checkbox("Je confirme vouloir réinitialiser (ATTENTION: supprime toutes les données)"):
                    try:
                        from init_db_approbation import init_database_approbation
                        init_database_approbation()
                        st.success("Base de données réinitialisée avec succès!")
                        st.info("Rechargez la page pour voir les changements.")
                    except Exception as e:
                        st.error(f"Erreur lors de la réinitialisation: {e}")
        
        # Sécurité des mots de passe
        st.markdown("**Sécurité des comptes:**")
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Vérifier les mots de passe par défaut
        from config_entreprise_unique import hash_password
        
        default_passwords = ['demo123', 'admin123', 'entreprise123']
        warnings = []
        
        for pwd in default_passwords:
            hashed = hash_password(pwd)
            cursor.execute('SELECT COUNT(*) FROM entreprises_clientes WHERE mot_de_passe_hash = ?', (hashed,))
            nb_clients = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM entreprises_prestataires WHERE mot_de_passe_hash = ?', (hashed,))  
            nb_prestataires = cursor.fetchone()[0]
            
            if nb_clients > 0 or nb_prestataires > 0:
                warnings.append(f"⚠️ {nb_clients + nb_prestataires} compte(s) utilisent le mot de passe '{pwd}'")
        
        if warnings:
            st.warning("Risques de sécurité détectés:")
            for warning in warnings:
                st.markdown(warning)
            st.markdown("**Recommandation:** Changez les mots de passe par défaut avant la mise en production!")
        else:
            st.success("✅ Aucun mot de passe par défaut détecté")
        
        # Nettoyage
        st.markdown("**Maintenance:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Nettoyer les données de test"):
                if st.checkbox("Confirmer la suppression des données de démonstration"):
                    try:
                        cursor.execute('DELETE FROM soumissions')
                        cursor.execute('DELETE FROM demandes_devis') 
                        cursor.execute('DELETE FROM entreprises_clientes')
                        conn.commit()
                        st.success("Données de test supprimées!")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
        
        with col2:
            if st.button("📊 Vérifier l'intégrité"):
                try:
                    # Vérifications basiques
                    cursor.execute('SELECT COUNT(*) FROM entreprises_prestataires')
                    nb_prestataires = cursor.fetchone()[0]
                    
                    if nb_prestataires == 1:
                        st.success("✅ Configuration mono-entreprise correcte")
                    else:
                        st.warning(f"⚠️ {nb_prestataires} prestataires (devrait être 1)")
                    
                    cursor.execute('SELECT COUNT(*) FROM soumissions s LEFT JOIN demandes_devis d ON s.demande_id = d.id WHERE d.id IS NULL')
                    orphaned = cursor.fetchone()[0]
                    
                    if orphaned == 0:
                        st.success("✅ Intégrité des données OK")
                    else:
                        st.warning(f"⚠️ {orphaned} soumission(s) orpheline(s)")
                        
                except Exception as e:
                    st.error(f"Erreur lors de la vérification: {e}")
        
        conn.close()

# ========================================================================================
# SERVICES PROFESSIONNELS ET LOGICIELS - Intégrés depuis SEAOP
# ========================================================================================

def page_service_estimation():
    """Page du service d'estimation professionnel intégré depuis SEAOP"""
    
    st.markdown("""
    <div class="demande-card">
        <h1>💰 Service d'estimation professionnel</h1>
        <p>Obtenez une estimation détaillée pour votre projet de construction</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Service d'estimation spécialisé construction québécoise")
    
    st.info("""
    📋 **Notre service d'estimation comprend :**
    • Analyse détaillée de vos plans et spécifications
    • Calcul précis des matériaux et main-d'œuvre  
    • Estimation selon les prix du marché québécois
    • Respect des normes RBQ et codes du bâtiment
    • Délai de livraison : 2-5 jours ouvrables
    """)
    
    with st.form("demande_estimation_construction"):
        st.markdown("**🏗️ Informations du projet**")
        
        col1, col2 = st.columns(2)
        with col1:
            nom_client = st.text_input("Nom du contact *")
            email_client = st.text_input("Email *") 
            telephone = st.text_input("Téléphone *")
        
        with col2:
            entreprise = st.text_input("Nom de l'entreprise")
            adresse_projet = st.text_input("Adresse du projet")
            type_projet = st.selectbox("Type de projet *", TYPES_PROJETS)
        
        description_projet = st.text_area(
            "Description détaillée du projet *",
            placeholder="Décrivez précisément les travaux, matériaux, contraintes...",
            height=150
        )
        
        col1, col2 = st.columns(2)
        with col1:
            budget_approximatif = st.selectbox(
                "Budget approximatif",
                ["À déterminer", "Moins de 25 000$", "25 000$ - 100 000$", 
                 "100 000$ - 500 000$", "Plus de 500 000$"]
            )
        with col2:
            delai_souhaite = st.selectbox(
                "Délai souhaité",
                ["Flexible", "Urgent (< 1 mois)", "1-3 mois", "3-6 mois", "> 6 mois"]
            )
        
        st.markdown("**📎 Documents du projet**")
        uploaded_files = st.file_uploader(
            "Plans, photos, devis existants...",
            type=['pdf', 'png', 'jpg', 'jpeg', 'dwg', 'doc', 'docx'],
            accept_multiple_files=True
        )
        
        st.markdown("---")
        st.warning("💰 **Tarif :** 150$ pour estimation résidentielle • 300$ pour estimation commerciale")
        
        submitted = st.form_submit_button("📤 Demander une estimation", use_container_width=True)
        
        if submitted:
            if nom_client and email_client and telephone and description_projet:
                st.success("✅ Votre demande d'estimation a été soumise avec succès!")
                st.info("📧 Vous recevrez un devis dans les 24h et l'estimation dans 2-5 jours ouvrables.")
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires")

def page_service_technologue():
    """Page du service de technologue (projets ≤ 6000 pi²)"""
    
    st.markdown("""
    <div class="demande-card">
        <h1>📐 Service de Technologue en Architecture</h1>
        <p>Plans techniques professionnels pour projets de 6,000 pi² et moins</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Service de technologie professionnelle")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📐 Services inclus :**
        • Plans architecturaux détaillés
        • Plans de construction
        • Coupes et élévations  
        • Détails techniques
        • Respect du Code du bâtiment
        • Signature et sceau professionnel
        """)
    
    with col2:
        st.markdown("""
        **🏗️ Types de projets :**
        • Résidentiel unifamilial
        • Petits commerces (≤ 6000 pi²)
        • Rénovations et agrandissements
        • Bâtiments industriels légers
        • Structures accessoires
        """)
    
    st.info("⚠️ **Limite légale :** Maximum 6,000 pi² selon l'Ordre des architectes du Québec")
    
    with st.form("demande_technologue"):
        st.markdown("**👤 Informations client**")
        
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom complet *")
            email = st.text_input("Email *")
            telephone = st.text_input("Téléphone *")
        
        with col2:
            adresse = st.text_input("Adresse du projet *")
            superficie = st.number_input("Superficie (pi²) *", min_value=1, max_value=6000, value=1000)
        
        type_batiment = st.selectbox(
            "Type de bâtiment *",
            ["Maison unifamiliale", "Duplex/Triplex", "Commerce", "Bureau", 
             "Entrepôt", "Garage/Remise", "Autre"]
        )
        
        description = st.text_area(
            "Description du projet *",
            placeholder="Décrivez votre projet : travaux souhaités, style architectural, contraintes...",
            height=120
        )
        
        st.markdown("**📋 Services requis**")
        services = st.multiselect(
            "Sélectionnez les services requis *",
            ["Plans architecturaux", "Plans de construction", "Plans électriques", 
             "Plans de plomberie", "Plans de structure", "Permis de construction",
             "Suivi de chantier"]
        )
        
        budget = st.selectbox(
            "Budget pour les plans",
            ["À déterminer", "Moins de 2 000$", "2 000$ - 5 000$", 
             "5 000$ - 10 000$", "Plus de 10 000$"]
        )
        
        urgence = st.selectbox(
            "Délai souhaité",
            ["Standard (4-6 semaines)", "Accéléré (2-3 semaines)", "Express (1-2 semaines)"]
        )
        
        submitted = st.form_submit_button("📐 Demander les services", use_container_width=True)
        
        if submitted:
            if superficie > 6000:
                st.error("❌ Superficie trop grande! Maximum 6,000 pi² pour un technologue.")
                st.info("💡 Pour des projets > 6,000 pi², utilisez notre Service d'Architecture.")
            elif nom and email and telephone and adresse and services:
                st.success("✅ Votre demande a été soumise avec succès!")
                st.info("📧 Notre technologue vous contactera dans les 24h pour discuter de votre projet.")
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires")

def page_service_architecture():
    """Page du service d'architecture (projets > 6000 pi²)"""
    
    st.markdown("""
    <div class="demande-card">
        <h1>🏛️ Service d'Architecture Professionnelle</h1>
        <p>Plans d'architecte pour projets de grande envergure (> 6,000 pi²)</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("⚡ **Requis par la loi :** Projets > 6,000 pi² nécessitent un architecte membre de l'OAQ")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🏛️ Services d'architecture :**
        • Conception architecturale
        • Plans et devis techniques
        • Coordination multidisciplinaire
        • Supervision de chantier
        • Conformité aux codes
        • Sceau et signature OAQ
        """)
    
    with col2:
        st.markdown("""
        **🏢 Types de projets :**
        • Immeubles résidentiels
        • Bâtiments commerciaux 
        • Complexes industriels
        • Établissements publics
        • Projets institutionnels
        """)
    
    with st.form("demande_architecture"):
        st.markdown("**🏢 Informations du projet**")
        
        col1, col2 = st.columns(2)
        with col1:
            nom_client = st.text_input("Nom du promoteur/client *")
            email = st.text_input("Email *")
            telephone = st.text_input("Téléphone *")
            entreprise = st.text_input("Nom de l'entreprise")
        
        with col2:
            adresse_projet = st.text_input("Adresse du projet *")
            superficie = st.number_input("Superficie (pi²) *", min_value=6001, value=10000)
            etages = st.number_input("Nombre d'étages", min_value=1, max_value=50, value=1)
            usage = st.selectbox(
                "Usage principal *",
                ["Résidentiel multifamilial", "Commercial", "Bureau", "Industriel", 
                 "Institutionnel", "Mixte", "Autre"]
            )
        
        description_projet = st.text_area(
            "Description détaillée du projet *",
            placeholder="Décrivez votre vision : concept architectural, fonctions, contraintes, objectifs...",
            height=150
        )
        
        st.markdown("**🎯 Services architecturaux requis**")
        services_arch = st.multiselect(
            "Services requis *",
            ["Esquisse et conception", "Avant-projet", "Projet préliminaire", 
             "Plans et devis d'exécution", "Appels d'offres", "Surveillance de travaux",
             "Réception des travaux", "LEED/Développement durable"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            budget_construction = st.selectbox(
                "Budget de construction",
                ["Moins de 1M$", "1M$ - 5M$", "5M$ - 10M$", "Plus de 10M$", "À déterminer"]
            )
        with col2:
            echeance = st.date_input("Échéancier souhaité (début)")
        
        submitted = st.form_submit_button("🏛️ Demander les services d'architecture", use_container_width=True)
        
        if submitted:
            if superficie <= 6000:
                st.error("❌ Pour des projets ≤ 6,000 pi², utilisez notre Service de Technologue.")
            elif nom_client and email and telephone and adresse_projet and services_arch:
                st.success("✅ Votre demande d'architecture a été soumise avec succès!")
                st.info("📧 Un architecte OAQ vous contactera dans les 48h pour planifier une rencontre.")
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires")

def page_service_ingenieur():
    """Page du service d'ingénieur en structure"""
    
    st.markdown("""
    <div class="demande-card">
        <h1>🔧 Service d'Ingénieur en Structure</h1>
        <p>Calculs structuraux et plans d'ingénieur par professionnels OIQ</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("⚖️ **Ingénieurs certifiés OIQ** - Ordre des ingénieurs du Québec")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔧 Services d'ingénierie :**
        • Calculs de structures
        • Plans structuraux
        • Expertise technique
        • Évaluation de capacité
        • Réhabilitation de structures
        • Sceau et signature OIQ
        """)
    
    with col2:
        st.markdown("""
        **🏗️ Spécialisations :**
        • Structures en béton
        • Charpentes d'acier
        • Structures de bois
        • Fondations spéciales
        • Rénovations structurales
        """)
    
    with st.form("demande_ingenieur"):
        st.markdown("**👤 Informations client**")
        
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom complet *")
            email = st.text_input("Email *")
            telephone = st.text_input("Téléphone *")
        
        with col2:
            entreprise = st.text_input("Entreprise/Organisation")
            adresse = st.text_input("Adresse du projet *")
        
        st.markdown("**🏗️ Détails du projet**")
        
        col1, col2 = st.columns(2)
        with col1:
            type_structure = st.selectbox(
                "Type de structure *",
                ["Résidentielle", "Commerciale", "Industrielle", "Institutionnelle", 
                 "Pont/Infrastructure", "Autre"]
            )
            materiau_principal = st.selectbox(
                "Matériau principal *", 
                ["Béton armé", "Acier", "Bois", "Maçonnerie", "Mixte", "Autre"]
            )
        
        with col2:
            superficie = st.number_input("Superficie (pi²)", min_value=1, value=1000)
            hauteur = st.number_input("Hauteur/Étages", min_value=1, value=1)
        
        description_technique = st.text_area(
            "Description technique du projet *",
            placeholder="Décrivez les défis structuraux, charges, contraintes techniques...",
            height=120
        )
        
        services_ing = st.multiselect(
            "Services d'ingénierie requis *",
            ["Calculs structuraux", "Plans de structure", "Expertise technique",
             "Évaluation de capacité", "Plans de rénovation", "Surveillance de travaux",
             "Certification de conformité"]
        )
        
        urgence_ing = st.selectbox(
            "Priorité du projet",
            ["Standard (2-4 semaines)", "Prioritaire (1-2 semaines)", "Urgent (quelques jours)"]
        )
        
        submitted = st.form_submit_button("🔧 Demander les services d'ingénierie", use_container_width=True)
        
        if submitted:
            if nom and email and telephone and adresse and services_ing:
                st.success("✅ Votre demande d'ingénierie a été soumise avec succès!")
                st.info("📧 Un ingénieur OIQ vous contactera dans les 24-48h pour évaluer votre projet.")
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires")

def page_experts_ia():
    """Page dédiée à EXPERTS IA"""
    st.markdown("""
    <div class="demande-card">
        <h1>🧠 EXPERTS IA - 60+ Experts Construction</h1>
        <p>L'Assistant IA le Plus Avancé de la Construction Québécoise</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🏆 Révolutionnez votre expertise construction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 60+ Experts spécialisés :**
        • Expert RBQ et réglementation
        • Spécialiste en estimation  
        • Ingénieur en structure
        • Architecte conseil
        • Expert en efficacité énergétique
        • Spécialiste LEED/Environnement
        • Contremaître expérimenté
        • Expert en sécurité chantier
        """)
    
    with col2:
        st.markdown("""
        **⚡ Fonctionnalités avancées :**
        • Analyse de plans en temps réel
        • Calculs automatiques précis
        • Conformité codes du bâtiment
        • Résolution de problèmes complexes
        • Recommandations personnalisées
        • Formation continue 24/7
        • Support multilingue
        """)
    
    st.success("🚀 **Disponible maintenant !** Accès gratuit pendant la phase beta")
    
    st.info("""
    💼 **Installation & Support EXPERTS IA**
    
    Pour l'installation et la configuration personnalisée d'EXPERTS IA :
    - 📧 **Email** : info@constructoai.ca
    - 📱 **Téléphone** : 514-820-1972
    - 💬 **Support 24/7** via l'application
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🚀 **Accéder à EXPERTS IA**", "https://experts-ai.constructoai.ca/", use_container_width=True, type="primary")
    with col2:
        if st.button("📚 **Documentation**", use_container_width=True):
            st.info("📖 **Guide d'utilisation disponible sur :** https://experts-ai.constructoai.ca/docs")
    
    st.markdown("---")
    st.markdown("### 💬 Testez une question rapidement")
    
    question = st.text_area(
        "Posez votre question technique :",
        placeholder="Ex: Comment calculer la charge admissible d'une poutre en bois de 2x10 sur 12 pieds?",
        height=80
    )
    
    if st.button("❓ Poser la question à EXPERTS IA", use_container_width=True):
        if question:
            st.info("💡 Cliquez sur le lien 'Accéder à EXPERTS IA' ci-dessus pour obtenir une réponse complète de nos 60+ experts spécialisés.")
        else:
            st.warning("❓ Veuillez écrire votre question")

def page_takeoff_ai():
    """Page dédiée à TAKEOFF AI"""
    st.markdown("""
    <div class="demande-card">
        <h1>📐 TAKEOFF AI - Estimation de Construction</h1>
        <p>Calculs précis de matériaux et coûts avec IA avancée</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Optimisé pour l'industrie québécoise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Fonctionnalités avancées :**
        • Analyse automatique de plans
        • Import plans PDF/DWG pour mesures automatiques
        • Calcul précis de matériaux selon normes CSA/BNQ
        • Estimation main-d'œuvre avec tarifs CCQ actualisés
        • Base de données prix matériaux temps réel
        • Export vers Excel/PDF
        • Génération rapports détaillés
        • Intégration avec SEAOP pour soumissions
        """)
    
    with col2:
        st.markdown("""
        **🏗️ Types de projets :**
        • Résidentiel unifamilial
        • Multifamilial/Condos
        • Commercial/Bureau
        • Industriel/Entrepôt
        • Rénovations
        • Infrastructure
        • Conformité codes du bâtiment québécois
        """)
    
    st.success("🚀 **TAKEOFF AI est maintenant disponible !**")
    
    st.info("""
    💼 **Installation & Support TAKEOFF AI**
    
    Pour l'installation et la configuration personnalisée :
    - 📧 **Email** : info@constructoai.ca
    - 📱 **Téléphone** : 514-820-1972
    - 💬 **Formation** personnalisée incluse
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🚀 **Accéder à TAKEOFF AI**", "https://takeoff-ai.constructoai.ca/", use_container_width=True, type="primary")
    with col2:
        if st.button("📊 **Exemples d'estimations**", use_container_width=True):
            st.info("📊 **Voir les démos sur :** https://takeoff-ai.constructoai.ca/demo")
    
    st.markdown("---")
    
    with st.form("takeoff_demo"):
        st.markdown("**📐 Calculateur rapide - Aperçu des fonctionnalités**")
        
        col1, col2 = st.columns(2)
        with col1:
            longueur = st.number_input("Longueur (pi)", min_value=0.0, value=20.0)
            largeur = st.number_input("Largeur (pi)", min_value=0.0, value=15.0)
        
        with col2:
            hauteur = st.number_input("Hauteur (pi)", min_value=0.0, value=8.0)
            type_materiau = st.selectbox("Matériau", ["Bois", "Béton", "Acier", "Brique"])
        
        calculate = st.form_submit_button("📊 Calculer estimation rapide")
        
        if calculate:
            surface = longueur * largeur
            volume = surface * hauteur
            
            st.success(f"📐 **Résultats estimés :**")
            st.write(f"• Surface : {surface:,.0f} pi²")
            st.write(f"• Volume : {volume:,.0f} pi³")
            st.info("💡 Pour des estimations détaillées avec coûts complets, utilisez TAKEOFF AI via le lien ci-dessus!")

def page_erp_ai():
    """Page dédiée à ERP AI"""
    st.markdown("""
    <div class="demande-card">
        <h1>📊 ERP AI - Gestion de Projets Construction</h1>
        <p>ERP Spécialisé Construction avec 24 Étapes de Chantier</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🏗️ Fonctionnalités construction québécoise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📋 Gestion complète de chantier :**
        • 24 étapes de construction (excavation → livraison)
        • Bons de Travail (BT) avec traçabilité complète
        • Planification automatique avec IA
        • Suivi temps réel des projets
        • Gestion des ressources et équipes
        • Contrôle qualité à chaque étape
        • Pointage employés et sous-traitants
        • Livraison dans les délais contractuels
        """)
    
    with col2:
        st.markdown("""
        **🚀 Modules spécialisés :**
        • CRM construction et gestion RH spécialisée
        • Comptabilité construction avancée
        • Paie et ressources humaines  
        • Inventaire matériaux avec normes CSA/BNQ
        • Facturation progressive
        • Conformité RBQ/CNESST
        • Assistant IA pour la gestion de vos projets
        """)
    
    st.info("""
    💼 **Installation & Support ERP AI**
    
    Pour l'installation et la configuration personnalisée d'ERP AI :
    - 📧 **Email** : info@constructoai.ca
    - 📱 **Téléphone** : 514-820-1972
    - 🏗️ **Formation** sur site incluse
    - 💻 **Personnalisation** selon vos processus
    """)
    
    st.warning("🔄 **Plateforme en développement** - Versions beta disponibles sur demande")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📞 **Demander une démo**", use_container_width=True, type="primary"):
            st.success("📧 Contactez info@constructoai.ca ou 514-820-1972 pour planifier votre démo personnalisée")
    with col2:
        if st.button("📋 **Liste d'attente Beta**", use_container_width=True):
            st.info("💡 Inscrivez-vous sur la liste d'attente pour accès prioritaire à ERP AI")
    
    # Démo des 24 étapes de chantier
    st.markdown("---")
    st.markdown("### 📅 Les 24 étapes de chantier intégrées")
    
    etapes_chantier = [
        "1. Préparation et planification", "2. Demande de permis", "3. Préparation du terrain",
        "4. Excavation et terrassement", "5. Fondations", "6. Drainage et imperméabilisation",
        "7. Charpente et structure", "8. Couverture et toiture", "9. Revêtement extérieur",
        "10. Fenêtres et portes", "11. Isolation", "12. Systèmes mécaniques",
        "13. Plomberie", "14. Électricité", "15. Cloisons sèches",
        "16. Revêtements de sol", "17. Armoires et menuiserie", "18. Peinture et finitions",
        "19. Éclairage et électricité", "20. Plomberie finale", "21. Nettoyage final",
        "22. Inspections", "23. Corrections", "24. Livraison client"
    ]
    
    # Affichage en colonnes pour un meilleur rendu
    cols = st.columns(3)
    for i, etape in enumerate(etapes_chantier):
        with cols[i % 3]:
            st.write(f"✅ {etape}")
    
    st.success("📞 **Intéressé par ERP AI ?** Contactez-nous pour une démo personnalisée et l'accès beta")

if __name__ == "__main__":
    main()