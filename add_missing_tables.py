# Script pour ajouter les tables manquantes sans supprimer l'existant

import sqlite3
import datetime
import hashlib
import os
from config_approbation import *

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', os.path.join(os.getcwd(), 'data'))
DATABASE_PATH = os.path.join(DATA_DIR, DATABASE_FILE)

def hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def add_missing_tables():
    """Ajoute les tables manquantes à la base existante"""
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("Ajout des tables manquantes...")
    
    # Vérifier quelles tables existent
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables existantes: {existing_tables}")
    
    # Table des entreprises clientes (si manquante)
    if 'entreprises_clientes' not in existing_tables:
        print("Création table entreprises_clientes...")
        cursor.execute('''
            CREATE TABLE entreprises_clientes (
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
                province TEXT DEFAULT 'Québec',
                mot_de_passe_hash TEXT NOT NULL,
                numero_entreprise TEXT,
                site_web TEXT,
                description_entreprise TEXT,
                logo TEXT,
                date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                statut TEXT DEFAULT 'actif',
                derniere_connexion TIMESTAMP,
                preferences_notification TEXT,
                limite_budget_mensuel REAL DEFAULT 0.0,
                budget_utilise_mois REAL DEFAULT 0.0
            )
        ''')
        
        # Ajouter données de demo clients
        clients_demo = [
            ('Développements Immobiliers Québec Inc.', 'Développement immobilier commercial', 'ETI (250-4999 employés)', 
             'Marie Dubois', 'Directrice des projets', 'marie.dubois@devimmo-qc.ca', '514-555-1001',
             '1234 Rue Saint-Laurent', 'Montréal', 'H2X 1A1', hash_password('demo123'),
             '1234567890', 'https://www.devimmo-qc.ca', 'Développeur immobilier spécialisé en projets commerciaux'),
            
            ('Industries Manufacturières du Québec', 'Usines et installations industrielles', 'Grande entreprise (5000+ employés)',
             'Jean Tremblay', 'Directeur des infrastructures', 'jean.tremblay@imq.ca', '418-555-2002',
             '567 Boulevard Charest Est', 'Québec', 'G1K 1A1', hash_password('demo123'),
             '2345678901', 'https://www.imq.ca', 'Leader manufacturier québécois spécialisé dans la transformation métallurgique'),
             
            ('Hôpitaux Régionaux Santé Québec', 'Établissements de santé', 'Grande entreprise (5000+ employés)',
             'Sophie Lavoie', 'Gestionnaire des infrastructures', 'sophie.lavoie@hrsq.ca', '450-555-3003',
             '890 Boulevard de la Santé', 'Laval', 'H7T 1A1', hash_password('demo123'),
             '3456789012', 'https://www.hrsq.ca', 'Réseau hospitalier régional gérant les infrastructures médicales')
        ]
        
        cursor.executemany('''
            INSERT INTO entreprises_clientes (
                nom_entreprise, secteur_activite, taille_entreprise, nom_contact,
                poste_contact, email, telephone, adresse, ville, code_postal,
                mot_de_passe_hash, numero_entreprise, site_web, description_entreprise
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', clients_demo)
        
        print("Table entreprises_clientes créée avec données de demo")
    
    # Table des entreprises prestataires (si manquante)
    if 'entreprises_prestataires' not in existing_tables:
        print("Création table entreprises_prestataires...")
        cursor.execute('''
            CREATE TABLE entreprises_prestataires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_entreprise TEXT NOT NULL,
                domaines_expertise TEXT NOT NULL,
                taille_entreprise TEXT NOT NULL,
                nom_contact TEXT NOT NULL,
                poste_contact TEXT,
                email TEXT UNIQUE NOT NULL,
                telephone TEXT NOT NULL,
                adresse TEXT,
                ville TEXT,
                code_postal TEXT,
                province TEXT DEFAULT 'Québec',
                mot_de_passe_hash TEXT NOT NULL,
                numero_entreprise TEXT,
                site_web TEXT,
                description_entreprise TEXT,
                logo TEXT,
                certifications TEXT,
                portfolio TEXT,
                tarif_horaire_min REAL DEFAULT 0.0,
                tarif_horaire_max REAL DEFAULT 0.0,
                disponibilite TEXT DEFAULT 'disponible',
                langues_parlees TEXT DEFAULT 'Français',
                zones_service TEXT,
                date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                statut TEXT DEFAULT 'actif',
                derniere_connexion TIMESTAMP,
                preferences_notification TEXT,
                note_moyenne REAL DEFAULT 0.0,
                nombre_evaluations INTEGER DEFAULT 0,
                nombre_projets_realises INTEGER DEFAULT 0,
                taux_reponse REAL DEFAULT 0.0,
                delai_reponse_moyen INTEGER DEFAULT 0
            )
        ''')
        
        # Ajouter données de demo prestataires
        prestataires_demo = [
            ('Construction Excellence Québec Inc.', '["Construction commerciale", "Construction industrielle", "Rénovation de bâtiments commerciaux"]', 
             'PME (10-249 employés)', 'Alex Martin', 'Directeur général', 'alex@constructionexcellence.ca', '514-555-4001',
             '', '', '', hash_password('demo123'), '', '', '', '["RBQ: 5678-1234-01", "APCHQ", "ASP Construction", "ISO 9001:2015"]',
             '', 85.0, 150.0),
            
            ('Électricité Industrielle Québec', '["Électricité industrielle", "Systèmes mécaniques (CVC)", "Automation"]',
             'PME (10-249 employés)', 'Isabelle Roy', 'Présidente', 'isabelle@eiqc.ca', '418-555-5002',
             '', '', '', hash_password('demo123'), '', '', '', '["RBQ: 9876-5432-01", "CEIQ", "Maître électricien", "Formation sécurité CCQ"]',
             '', 95.0, 180.0),
             
            ('Structures Métalliques Bergeron', '["Structures d\'acier", "Béton et fondations", "Soudage certifié"]',
             'TPE (1-9 employés)', 'Michel Bergeron', 'Propriétaire et soudeur certifié', 'michel@structures-bergeron.ca', '450-555-6003',
             '', '', '', hash_password('demo123'), '', '', '', '["RBQ: 1357-2468-01", "Soudeur certifié CSA W47.1", "Formation grue mobile", "SIMDUT 2015"]',
             '', 110.0, 175.0)
        ]
        
        cursor.executemany('''
            INSERT INTO entreprises_prestataires (
                nom_entreprise, domaines_expertise, taille_entreprise, nom_contact,
                poste_contact, email, telephone, adresse, ville, code_postal,
                mot_de_passe_hash, numero_entreprise, site_web, description_entreprise, certifications,
                portfolio, tarif_horaire_min, tarif_horaire_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', prestataires_demo)
        
        print("Table entreprises_prestataires créée avec données de demo")
    
    # Autres tables importantes si manquantes
    tables_a_creer = [
        ('demandes_devis', '''
            CREATE TABLE demandes_devis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                titre TEXT NOT NULL,
                type_projet TEXT NOT NULL,
                secteur_activite TEXT,
                description_detaillee TEXT NOT NULL,
                budget_min REAL,
                budget_max REAL,
                delai_livraison TEXT NOT NULL,
                date_limite_soumissions DATETIME NOT NULL,
                statut TEXT DEFAULT 'brouillon',
                numero_reference TEXT UNIQUE,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES entreprises_clientes (id)
            )
        '''),
        ('soumissions', '''
            CREATE TABLE soumissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                demande_id INTEGER NOT NULL,
                prestataire_id INTEGER NOT NULL,
                titre_soumission TEXT NOT NULL,
                resume_executif TEXT NOT NULL,
                proposition_technique TEXT NOT NULL,
                budget_total REAL NOT NULL,
                delai_livraison TEXT NOT NULL,
                statut TEXT DEFAULT 'brouillon',
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (demande_id) REFERENCES demandes_devis (id),
                FOREIGN KEY (prestataire_id) REFERENCES entreprises_prestataires (id)
            )
        '''),
        ('processus_approbation', '''
            CREATE TABLE processus_approbation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                soumission_id INTEGER NOT NULL,
                etape_actuelle INTEGER DEFAULT 1,
                statut_etape TEXT DEFAULT 'en_cours',
                date_debut_etape TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (soumission_id) REFERENCES soumissions (id)
            )
        '''),
        ('evaluations', '''
            CREATE TABLE evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                soumission_id INTEGER NOT NULL,
                evaluateur_id INTEGER NOT NULL,
                evaluateur_type TEXT NOT NULL,
                critere_nom TEXT NOT NULL,
                note INTEGER NOT NULL CHECK(note >= 1 AND note <= 5),
                commentaire TEXT,
                date_evaluation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (soumission_id) REFERENCES soumissions (id)
            )
        '''),
        ('messages', '''
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                demande_id INTEGER,
                soumission_id INTEGER,
                expediteur_id INTEGER NOT NULL,
                expediteur_type TEXT NOT NULL,
                destinataire_id INTEGER NOT NULL,
                destinataire_type TEXT NOT NULL,
                contenu TEXT NOT NULL,
                date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                lu BOOLEAN DEFAULT 0,
                FOREIGN KEY (demande_id) REFERENCES demandes_devis (id),
                FOREIGN KEY (soumission_id) REFERENCES soumissions (id)
            )
        '''),
        ('notifications', '''
            CREATE TABLE notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilisateur_id INTEGER NOT NULL,
                utilisateur_type TEXT NOT NULL,
                type_notification TEXT NOT NULL,
                titre TEXT NOT NULL,
                message TEXT NOT NULL,
                lu BOOLEAN DEFAULT 0,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''),
        ('contrats', '''
            CREATE TABLE contrats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                demande_id INTEGER NOT NULL,
                soumission_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                prestataire_id INTEGER NOT NULL,
                titre_contrat TEXT NOT NULL,
                valeur_contrat REAL NOT NULL,
                date_signature TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                statut_contrat TEXT DEFAULT 'actif',
                FOREIGN KEY (demande_id) REFERENCES demandes_devis (id),
                FOREIGN KEY (soumission_id) REFERENCES soumissions (id),
                FOREIGN KEY (client_id) REFERENCES entreprises_clientes (id),
                FOREIGN KEY (prestataire_id) REFERENCES entreprises_prestataires (id)
            )
        '''),
        ('logs_audit', '''
            CREATE TABLE logs_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilisateur_id INTEGER,
                utilisateur_type TEXT,
                action TEXT NOT NULL,
                table_affectee TEXT,
                date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    ]
    
    for table_name, create_sql in tables_a_creer:
        if table_name not in existing_tables:
            print(f"Création table {table_name}...")
            cursor.execute(create_sql)
    
    # Vérifier/Ajouter documents requis si table existe mais vide
    if 'documents_requis' in existing_tables:
        cursor.execute('SELECT COUNT(*) FROM documents_requis')
        if cursor.fetchone()[0] == 0:
            print("Ajout des documents requis...")
            documents = [
                ('client', 'Certificat d\'incorporation', True, 'Document officiel d\'incorporation de l\'entreprise', '["pdf"]', 5, 1),
                ('client', 'Preuve d\'adresse', True, 'Facture ou document officiel récent', '["pdf", "jpg", "png"]', 3, 2),
                ('prestataire', 'Licence RBQ', True, 'Licence valide de la Régie du bâtiment du Québec', '["pdf"]', 5, 1),
                ('prestataire', 'Assurance responsabilité', True, 'Certificat d\'assurance responsabilité civile', '["pdf"]', 5, 2),
                ('prestataire', 'Certificat d\'incorporation', True, 'Document officiel d\'incorporation', '["pdf"]', 5, 3)
            ]
            
            cursor.executemany('''
                INSERT INTO documents_requis 
                (type_entreprise, nom_document, obligatoire, description, formats_acceptes, taille_max_mb, ordre_affichage)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', documents)
    
    conn.commit()
    conn.close()
    
    print("Tables manquantes ajoutées avec succès!")
    print("Vous pouvez maintenant utiliser le système d'inscription.")

if __name__ == "__main__":
    add_missing_tables()