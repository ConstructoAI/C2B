# Système d'inscription pour les nouvelles entreprises
# Module complet avec workflow d'approbation

import sqlite3
import datetime
import hashlib
import uuid
import os
from typing import Optional, Dict, Any
import streamlit as st
import re
from config_approbation import *

def init_inscription_tables():
    """Initialise les tables pour le système d'inscription"""
    DATA_DIR = os.getenv('DATA_DIR', os.path.join(os.getcwd(), 'data'))
    DATABASE_PATH = os.path.join(DATA_DIR, DATABASE_FILE)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Table des demandes d'inscription en attente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS demandes_inscription (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_entreprise TEXT NOT NULL CHECK(type_entreprise IN ('client', 'prestataire')),
            
            -- Informations générales
            nom_entreprise TEXT NOT NULL,
            secteur_activite TEXT,
            domaines_expertise TEXT,  -- JSON pour prestataires
            taille_entreprise TEXT NOT NULL,
            
            -- Contact principal
            nom_contact TEXT NOT NULL,
            poste_contact TEXT,
            email TEXT UNIQUE NOT NULL,
            telephone TEXT NOT NULL,
            
            -- Adresse
            adresse TEXT,
            ville TEXT,
            code_postal TEXT,
            province TEXT DEFAULT 'Québec',
            
            -- Informations entreprise
            numero_entreprise TEXT,  -- NEQ
            numero_rbq TEXT,  -- Pour prestataires construction
            site_web TEXT,
            description_entreprise TEXT,
            
            -- Sécurité
            mot_de_passe_hash TEXT NOT NULL,
            
            -- Documents joints (Base64)
            documents_joints TEXT,  -- JSON avec {type: content_base64}
            
            -- Statut de la demande
            statut TEXT DEFAULT 'en_attente' CHECK(statut IN ('en_attente', 'en_verification', 'approuvee', 'rejetee', 'incomplete')),
            
            -- Informations spécifiques prestataires
            certifications TEXT,  -- JSON array
            assurances TEXT,  -- JSON avec détails assurances
            tarif_horaire_min REAL DEFAULT 0.0,
            tarif_horaire_max REAL DEFAULT 0.0,
            zones_service TEXT,  -- Zones géographiques
            langues_parlees TEXT DEFAULT 'Français',
            
            -- Suivi de la demande
            date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_verification TIMESTAMP,
            date_decision TIMESTAMP,
            evaluateur_admin_id INTEGER,
            commentaires_admin TEXT,
            raison_rejet TEXT,
            
            -- Validation
            email_verifie BOOLEAN DEFAULT 0,
            token_verification TEXT,
            documents_valides BOOLEAN DEFAULT 0,
            
            -- Métadonnées
            ip_address TEXT,
            user_agent TEXT,
            source_inscription TEXT DEFAULT 'web'
        )
    ''')
    
    # Table pour les documents requis par type d'entreprise
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents_requis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_entreprise TEXT NOT NULL,
            nom_document TEXT NOT NULL,
            obligatoire BOOLEAN DEFAULT 1,
            description TEXT,
            formats_acceptes TEXT,  -- JSON array
            taille_max_mb INTEGER DEFAULT 5,
            ordre_affichage INTEGER DEFAULT 0
        )
    ''')
    
    # Table pour l'historique des changements de statut
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historique_inscription (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demande_inscription_id INTEGER NOT NULL,
            ancien_statut TEXT,
            nouveau_statut TEXT,
            utilisateur_id INTEGER,
            utilisateur_type TEXT,
            commentaire TEXT,
            date_changement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (demande_inscription_id) REFERENCES demandes_inscription (id)
        )
    ''')
    
    # Index pour améliorer les performances
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inscription_statut ON demandes_inscription(statut)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inscription_email ON demandes_inscription(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inscription_type ON demandes_inscription(type_entreprise)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inscription_date ON demandes_inscription(date_demande)')
    
    # Insérer les documents requis par défaut
    documents_client = [
        ('client', 'Certificat d\'incorporation', True, 'Document officiel d\'incorporation de l\'entreprise', '["pdf"]', 5, 1),
        ('client', 'Preuve d\'adresse', True, 'Facture ou document officiel récent', '["pdf", "jpg", "png"]', 3, 2),
        ('client', 'Attestation fiscale', False, 'Attestation de conformité fiscale', '["pdf"]', 5, 3)
    ]
    
    documents_prestataire = [
        ('prestataire', 'Licence RBQ', True, 'Licence valide de la Régie du bâtiment du Québec', '["pdf"]', 5, 1),
        ('prestataire', 'Assurance responsabilité', True, 'Certificat d\'assurance responsabilité civile', '["pdf"]', 5, 2),
        ('prestataire', 'Certificat d\'incorporation', True, 'Document officiel d\'incorporation', '["pdf"]', 5, 3),
        ('prestataire', 'Portfolio de projets', False, 'Exemples de projets réalisés', '["pdf", "jpg", "png"]', 10, 4),
        ('prestataire', 'Certifications additionnelles', False, 'Certifications professionnelles (LEED, etc.)', '["pdf"]', 5, 5)
    ]
    
    # Insérer seulement si la table est vide
    cursor.execute('SELECT COUNT(*) FROM documents_requis')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO documents_requis 
            (type_entreprise, nom_document, obligatoire, description, formats_acceptes, taille_max_mb, ordre_affichage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', documents_client + documents_prestataire)
    
    conn.commit()
    conn.close()
    
    print("Tables d'inscription initialisees avec succes!")

def hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def valider_donnees_inscription(data: Dict[str, Any], type_entreprise: str) -> Dict[str, str]:
    """Valide les données d'inscription et retourne les erreurs"""
    erreurs = {}
    
    # Validation email
    if not data.get('email'):
        erreurs['email'] = "Email requis"
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
        erreurs['email'] = "Format d'email invalide"
    elif email_existe_deja(data['email']):
        erreurs['email'] = "Cette adresse email est déjà utilisée"
    
    # Validation téléphone
    if not data.get('telephone'):
        erreurs['telephone'] = "Numéro de téléphone requis"
    elif not re.match(r'^(\+1[-.\s]?)?\(?([2-9][0-9]{2})\)?[-.\s]?([2-9][0-9]{2})[-.\s]?([0-9]{4})$', 
                      data['telephone'].replace(" ", "")):
        erreurs['telephone'] = "Format de téléphone invalide (ex: 514-555-1234)"
    
    # Validation mot de passe
    if not data.get('mot_de_passe'):
        erreurs['mot_de_passe'] = "Mot de passe requis"
    elif len(data['mot_de_passe']) < 8:
        erreurs['mot_de_passe'] = "Le mot de passe doit contenir au moins 8 caractères"
    
    # Validation confirmation mot de passe
    if data.get('mot_de_passe') != data.get('confirmation_mot_de_passe'):
        erreurs['confirmation_mot_de_passe'] = "Les mots de passe ne correspondent pas"
    
    # Validation nom entreprise
    if not data.get('nom_entreprise') or len(data['nom_entreprise'].strip()) < 2:
        erreurs['nom_entreprise'] = "Nom d'entreprise requis (minimum 2 caractères)"
    
    # Validation nom contact
    if not data.get('nom_contact') or len(data['nom_contact'].strip()) < 2:
        erreurs['nom_contact'] = "Nom du contact requis (minimum 2 caractères)"
    
    # Validations spécifiques aux prestataires
    if type_entreprise == 'prestataire':
        if not data.get('numero_rbq'):
            erreurs['numero_rbq'] = "Numéro RBQ requis pour les entrepreneurs"
        elif not re.match(r'^\d{4}-\d{4}-\d{2}$', data['numero_rbq']):
            erreurs['numero_rbq'] = "Format RBQ invalide (ex: 5678-1234-01)"
        
        if not data.get('domaines_expertise'):
            erreurs['domaines_expertise'] = "Au moins un domaine d'expertise requis"
    
    return erreurs

def email_existe_deja(email: str) -> bool:
    """Vérifie si l'email existe déjà dans le système"""
    DATA_DIR = os.getenv('DATA_DIR', os.path.join(os.getcwd(), 'data'))
    DATABASE_PATH = os.path.join(DATA_DIR, DATABASE_FILE)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Vérifier dans les entreprises existantes
        cursor.execute('SELECT COUNT(*) FROM entreprises_clientes WHERE email = ?', (email,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return True
        
        cursor.execute('SELECT COUNT(*) FROM entreprises_prestataires WHERE email = ?', (email,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return True
    except sqlite3.OperationalError:
        # Les tables principales n'existent pas encore, continuer avec les inscriptions
        pass
    
    try:
        # Vérifier dans les demandes d'inscription en attente
        cursor.execute('SELECT COUNT(*) FROM demandes_inscription WHERE email = ? AND statut != "rejetee"', (email,))
        existe = cursor.fetchone()[0] > 0
    except sqlite3.OperationalError:
        # Table d'inscription pas encore créée
        existe = False
    
    conn.close()
    return existe

def sauvegarder_demande_inscription(data: Dict[str, Any], type_entreprise: str) -> int:
    """Sauvegarde une demande d'inscription et retourne l'ID"""
    DATA_DIR = os.getenv('DATA_DIR', os.path.join(os.getcwd(), 'data'))
    DATABASE_PATH = os.path.join(DATA_DIR, DATABASE_FILE)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Générer un token de vérification
    token_verification = str(uuid.uuid4())
    
    # Préparer les données selon le type
    if type_entreprise == 'prestataire':
        cursor.execute('''
            INSERT INTO demandes_inscription (
                type_entreprise, nom_entreprise, domaines_expertise, taille_entreprise,
                nom_contact, poste_contact, email, telephone, adresse, ville, code_postal,
                numero_entreprise, numero_rbq, site_web, description_entreprise,
                mot_de_passe_hash, certifications, tarif_horaire_min, tarif_horaire_max,
                zones_service, langues_parlees, token_verification
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            type_entreprise, data['nom_entreprise'], data.get('domaines_expertise', '[]'),
            data['taille_entreprise'], data['nom_contact'], data.get('poste_contact', ''),
            data['email'], data['telephone'], data.get('adresse', ''), data.get('ville', ''),
            data.get('code_postal', ''), data.get('numero_entreprise', ''), data.get('numero_rbq', ''),
            data.get('site_web', ''), data.get('description_entreprise', ''),
            hash_password(data['mot_de_passe']), data.get('certifications', '[]'),
            data.get('tarif_horaire_min', 0.0), data.get('tarif_horaire_max', 0.0),
            data.get('zones_service', ''), data.get('langues_parlees', 'Français'),
            token_verification
        ))
    else:  # client
        cursor.execute('''
            INSERT INTO demandes_inscription (
                type_entreprise, nom_entreprise, secteur_activite, taille_entreprise,
                nom_contact, poste_contact, email, telephone, adresse, ville, code_postal,
                numero_entreprise, site_web, description_entreprise, mot_de_passe_hash,
                token_verification
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            type_entreprise, data['nom_entreprise'], data.get('secteur_activite', ''),
            data['taille_entreprise'], data['nom_contact'], data.get('poste_contact', ''),
            data['email'], data['telephone'], data.get('adresse', ''), data.get('ville', ''),
            data.get('code_postal', ''), data.get('numero_entreprise', ''),
            data.get('site_web', ''), data.get('description_entreprise', ''),
            hash_password(data['mot_de_passe']), token_verification
        ))
    
    demande_id = cursor.lastrowid
    
    # Ajouter l'historique
    cursor.execute('''
        INSERT INTO historique_inscription (
            demande_inscription_id, ancien_statut, nouveau_statut, commentaire
        ) VALUES (?, NULL, 'en_attente', 'Demande d''inscription soumise')
    ''', (demande_id,))
    
    conn.commit()
    conn.close()
    
    return demande_id

def obtenir_documents_requis(type_entreprise: str) -> list:
    """Récupère la liste des documents requis pour un type d'entreprise"""
    DATA_DIR = os.getenv('DATA_DIR', os.path.join(os.getcwd(), 'data'))
    DATABASE_PATH = os.path.join(DATA_DIR, DATABASE_FILE)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT nom_document, obligatoire, description, formats_acceptes, taille_max_mb
        FROM documents_requis 
        WHERE type_entreprise = ? 
        ORDER BY ordre_affichage
    ''', (type_entreprise,))
    
    documents = cursor.fetchall()
    conn.close()
    
    return [
        {
            'nom': doc[0],
            'obligatoire': bool(doc[1]),
            'description': doc[2],
            'formats': eval(doc[3]) if doc[3] else ['pdf'],
            'taille_max': doc[4]
        }
        for doc in documents
    ]

if __name__ == "__main__":
    init_inscription_tables()