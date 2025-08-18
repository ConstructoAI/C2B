# Initialisation complète de la base de données
# Combine les tables principales + tables d'inscription

import sqlite3
import datetime
import hashlib
import random
import os
from config_approbation import *

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', os.path.join(os.getcwd(), 'data'))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, DATABASE_FILE)

def hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_complete_database():
    """Initialise la base de données complète (principale + inscription)"""
    
    # Créer une nouvelle base de données
    if os.path.exists(DATABASE_PATH):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_db_path = os.path.join(DATA_DIR, f'soumissions_entreprises_new_{timestamp}.db')
        DATABASE_PATH_NEW = new_db_path
        print(f"Creation d'une nouvelle base: {new_db_path}")
    else:
        DATABASE_PATH_NEW = DATABASE_PATH
    
    conn = sqlite3.connect(DATABASE_PATH_NEW)
    cursor = conn.cursor()
    
    # ============= TABLES PRINCIPALES =============
    
    # Table des entreprises clientes (qui demandent des devis)
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
    
    # Table des entreprises prestataires
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entreprises_prestataires (
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
    
    # Table des demandes de devis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS demandes_devis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            titre TEXT NOT NULL,
            type_projet TEXT NOT NULL,
            secteur_activite TEXT,
            description_detaillee TEXT NOT NULL,
            objectifs TEXT,
            contraintes TEXT,
            budget_min REAL,
            budget_max REAL,
            budget_flexible BOOLEAN DEFAULT 0,
            date_debut_souhaitee DATE,
            date_fin_souhaitee DATE,
            delai_livraison TEXT NOT NULL,
            date_limite_soumissions DATETIME NOT NULL,
            criteres_evaluation TEXT,
            competences_requises TEXT,
            niveau_experience_requis TEXT,
            localisation_projet TEXT,
            mode_travail TEXT,
            documents TEXT,
            cahier_charges TEXT,
            nombre_soumissions_max INTEGER DEFAULT 10,
            statut TEXT DEFAULT 'brouillon',
            numero_reference TEXT UNIQUE,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_publication TIMESTAMP,
            date_fermeture TIMESTAMP,
            vue_par_prestataires INTEGER DEFAULT 0,
            nombre_soumissions_recues INTEGER DEFAULT 0,
            tags TEXT,
            priorite TEXT DEFAULT 'normale',
            confidentiel BOOLEAN DEFAULT 0,
            accord_nda_requis BOOLEAN DEFAULT 0,
            FOREIGN KEY (client_id) REFERENCES entreprises_clientes (id)
        )
    ''')
    
    # Table des soumissions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS soumissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demande_id INTEGER NOT NULL,
            prestataire_id INTEGER NOT NULL,
            titre_soumission TEXT NOT NULL,
            resume_executif TEXT NOT NULL,
            proposition_technique TEXT NOT NULL,
            methodologie TEXT,
            planning_detaille TEXT,
            equipe_proposee TEXT,
            budget_total REAL NOT NULL,
            detail_budget TEXT,
            delai_livraison TEXT NOT NULL,
            date_debut_proposee DATE,
            date_fin_proposee DATE,
            conditions_generales TEXT,
            garanties TEXT,
            maintenance_support TEXT,
            inclusions TEXT,
            exclusions TEXT,
            options_supplementaires TEXT,
            documents_joints TEXT,
            portfolio_pertinent TEXT,
            validite_offre INTEGER DEFAULT 30,
            statut TEXT DEFAULT 'brouillon',
            note_auto_evaluation REAL,
            commentaires_internes TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_soumission TIMESTAMP,
            date_derniere_modification TIMESTAMP,
            vue_par_client BOOLEAN DEFAULT 0,
            date_vue_client TIMESTAMP,
            temps_preparation INTEGER,
            version INTEGER DEFAULT 1,
            soumission_parent_id INTEGER,
            FOREIGN KEY (demande_id) REFERENCES demandes_devis (id),
            FOREIGN KEY (prestataire_id) REFERENCES entreprises_prestataires (id),
            FOREIGN KEY (soumission_parent_id) REFERENCES soumissions (id),
            UNIQUE(demande_id, prestataire_id, version)
        )
    ''')
    
    # ============= TABLES D'INSCRIPTION =============
    
    # Table des demandes d'inscription
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS demandes_inscription (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_entreprise TEXT NOT NULL CHECK(type_entreprise IN ('client', 'prestataire')),
            nom_entreprise TEXT NOT NULL,
            secteur_activite TEXT,
            domaines_expertise TEXT,
            taille_entreprise TEXT NOT NULL,
            nom_contact TEXT NOT NULL,
            poste_contact TEXT,
            email TEXT UNIQUE NOT NULL,
            telephone TEXT NOT NULL,
            adresse TEXT,
            ville TEXT,
            code_postal TEXT,
            province TEXT DEFAULT 'Québec',
            numero_entreprise TEXT,
            numero_rbq TEXT,
            site_web TEXT,
            description_entreprise TEXT,
            mot_de_passe_hash TEXT NOT NULL,
            documents_joints TEXT,
            statut TEXT DEFAULT 'en_attente' CHECK(statut IN ('en_attente', 'en_verification', 'approuvee', 'rejetee', 'incomplete')),
            certifications TEXT,
            assurances TEXT,
            tarif_horaire_min REAL DEFAULT 0.0,
            tarif_horaire_max REAL DEFAULT 0.0,
            zones_service TEXT,
            langues_parlees TEXT DEFAULT 'Français',
            date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_verification TIMESTAMP,
            date_decision TIMESTAMP,
            evaluateur_admin_id INTEGER,
            commentaires_admin TEXT,
            raison_rejet TEXT,
            email_verifie BOOLEAN DEFAULT 0,
            token_verification TEXT,
            documents_valides BOOLEAN DEFAULT 0,
            ip_address TEXT,
            user_agent TEXT,
            source_inscription TEXT DEFAULT 'web'
        )
    ''')
    
    # Table des documents requis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents_requis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_entreprise TEXT NOT NULL,
            nom_document TEXT NOT NULL,
            obligatoire BOOLEAN DEFAULT 1,
            description TEXT,
            formats_acceptes TEXT,
            taille_max_mb INTEGER DEFAULT 5,
            ordre_affichage INTEGER DEFAULT 0
        )
    ''')
    
    # Table historique des inscriptions
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
    
    # ============= AUTRES TABLES NÉCESSAIRES =============
    
    # Table des processus d'approbation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processus_approbation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soumission_id INTEGER NOT NULL,
            etape_actuelle INTEGER DEFAULT 1,
            etape_nom TEXT,
            statut_etape TEXT DEFAULT 'en_cours',
            evaluateur_id INTEGER,
            evaluateur_type TEXT,
            date_debut_etape TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_fin_etape TIMESTAMP,
            commentaires_etape TEXT,
            documents_etape TEXT,
            score_etape REAL,
            criteres_evaluation TEXT,
            decision TEXT,
            raison_decision TEXT,
            prochaine_etape INTEGER,
            delai_etape_jours INTEGER,
            notification_envoyee BOOLEAN DEFAULT 0,
            FOREIGN KEY (soumission_id) REFERENCES soumissions (id)
        )
    ''')
    
    # Table des évaluations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soumission_id INTEGER NOT NULL,
            evaluateur_id INTEGER NOT NULL,
            evaluateur_type TEXT NOT NULL,
            type_evaluation TEXT NOT NULL,
            critere_nom TEXT NOT NULL,
            note INTEGER NOT NULL CHECK(note >= 1 AND note <= 5),
            poids REAL DEFAULT 1.0,
            commentaire TEXT,
            justification TEXT,
            recommandations TEXT,
            date_evaluation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modifiable BOOLEAN DEFAULT 1,
            version INTEGER DEFAULT 1,
            FOREIGN KEY (soumission_id) REFERENCES soumissions (id)
        )
    ''')
    
    # Table des messages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demande_id INTEGER,
            soumission_id INTEGER,
            expediteur_id INTEGER NOT NULL,
            expediteur_type TEXT NOT NULL,
            destinataire_id INTEGER NOT NULL,
            destinataire_type TEXT NOT NULL,
            type_message TEXT DEFAULT 'general',
            sujet TEXT,
            contenu TEXT NOT NULL,
            pieces_jointes TEXT,
            priorite TEXT DEFAULT 'normale',
            confidentiel BOOLEAN DEFAULT 0,
            date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_lecture TIMESTAMP,
            lu BOOLEAN DEFAULT 0,
            archive BOOLEAN DEFAULT 0,
            reponse_a_message_id INTEGER,
            FOREIGN KEY (demande_id) REFERENCES demandes_devis (id),
            FOREIGN KEY (soumission_id) REFERENCES soumissions (id),
            FOREIGN KEY (reponse_a_message_id) REFERENCES messages (id)
        )
    ''')
    
    # Table des notifications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            utilisateur_type TEXT NOT NULL,
            type_notification TEXT NOT NULL,
            titre TEXT NOT NULL,
            message TEXT NOT NULL,
            lien_interne TEXT,
            donnees_contexte TEXT,
            priorite TEXT DEFAULT 'normale',
            lu BOOLEAN DEFAULT 0,
            archive BOOLEAN DEFAULT 0,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_lecture TIMESTAMP,
            date_expiration TIMESTAMP,
            canal_notification TEXT DEFAULT 'app'
        )
    ''')
    
    # Table des contrats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contrats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demande_id INTEGER NOT NULL,
            soumission_id INTEGER NOT NULL,
            client_id INTEGER NOT NULL,
            prestataire_id INTEGER NOT NULL,
            numero_contrat TEXT UNIQUE,
            titre_contrat TEXT NOT NULL,
            valeur_contrat REAL NOT NULL,
            date_signature TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_debut_prevue DATE NOT NULL,
            date_fin_prevue DATE NOT NULL,
            conditions_particulieres TEXT,
            modalites_paiement TEXT,
            livrables TEXT,
            jalons TEXT,
            statut_contrat TEXT DEFAULT 'actif',
            avancement_pourcentage REAL DEFAULT 0.0,
            montant_paye REAL DEFAULT 0.0,
            documents_contractuels TEXT,
            date_derniere_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes_suivi TEXT,
            FOREIGN KEY (demande_id) REFERENCES demandes_devis (id),
            FOREIGN KEY (soumission_id) REFERENCES soumissions (id),
            FOREIGN KEY (client_id) REFERENCES entreprises_clientes (id),
            FOREIGN KEY (prestataire_id) REFERENCES entreprises_prestataires (id)
        )
    ''')
    
    # Table des logs d'audit
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER,
            utilisateur_type TEXT,
            action TEXT NOT NULL,
            table_affectee TEXT,
            enregistrement_id INTEGER,
            donnees_avant TEXT,
            donnees_apres TEXT,
            adresse_ip TEXT,
            user_agent TEXT,
            date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details_supplementaires TEXT
        )
    ''')
    
    # ============= INDEX =============
    
    # Index pour améliorer les performances
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_demandes_statut ON demandes_devis(statut)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_demandes_client ON demandes_devis(client_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_demandes_type ON demandes_devis(type_projet)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_soumissions_demande ON soumissions(demande_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_soumissions_prestataire ON soumissions(prestataire_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_soumissions_statut ON soumissions(statut)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_demande ON messages(demande_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_soumission ON messages(soumission_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_utilisateur ON notifications(utilisateur_id, utilisateur_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_approbation_soumission ON processus_approbation(soumission_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inscription_statut ON demandes_inscription(statut)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inscription_email ON demandes_inscription(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inscription_type ON demandes_inscription(type_entreprise)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inscription_date ON demandes_inscription(date_demande)')
    
    # ============= DONNÉES DE DEMO =============
    
    # Entreprises clientes
    clients_demo = [
        {
            'nom_entreprise': 'Développements Immobiliers Québec Inc.',
            'secteur_activite': 'Développement immobilier commercial',
            'taille_entreprise': 'ETI (250-4999 employés)',
            'nom_contact': 'Marie Dubois',
            'poste_contact': 'Directrice des projets',
            'email': 'marie.dubois@devimmo-qc.ca',
            'telephone': '514-555-1001',
            'adresse': '1234 Rue Saint-Laurent',
            'ville': 'Montréal',
            'code_postal': 'H2X 1A1',
            'mot_de_passe': 'demo123',
            'numero_entreprise': '1234567890',
            'site_web': 'https://www.devimmo-qc.ca',
            'description_entreprise': 'Développeur immobilier spécialisé en projets commerciaux et résidentiels au Québec'
        },
        {
            'nom_entreprise': 'Industries Manufacturières du Québec',
            'secteur_activite': 'Usines et installations industrielles',
            'taille_entreprise': 'Grande entreprise (5000+ employés)',
            'nom_contact': 'Jean Tremblay',
            'poste_contact': 'Directeur des infrastructures',
            'email': 'jean.tremblay@imq.ca',
            'telephone': '418-555-2002',
            'adresse': '567 Boulevard Charest Est',
            'ville': 'Québec',
            'code_postal': 'G1K 1A1',
            'mot_de_passe': 'demo123',
            'numero_entreprise': '2345678901',
            'site_web': 'https://www.imq.ca',
            'description_entreprise': 'Leader manufacturier québécois spécialisé dans la transformation métallurgique'
        },
        {
            'nom_entreprise': 'Hôpitaux Régionaux Santé Québec',
            'secteur_activite': 'Établissements de santé',
            'taille_entreprise': 'Grande entreprise (5000+ employés)',
            'nom_contact': 'Sophie Lavoie',
            'poste_contact': 'Gestionnaire des infrastructures',
            'email': 'sophie.lavoie@hrsq.ca',
            'telephone': '450-555-3003',
            'adresse': '890 Boulevard de la Santé',
            'ville': 'Laval',
            'code_postal': 'H7T 1A1',
            'mot_de_passe': 'demo123',
            'numero_entreprise': '3456789012',
            'site_web': 'https://www.hrsq.ca',
            'description_entreprise': 'Réseau hospitalier régional gérant les infrastructures médicales du Québec'
        }
    ]
    
    # Insérer les clients
    for client in clients_demo:
        cursor.execute('''
            INSERT INTO entreprises_clientes (
                nom_entreprise, secteur_activite, taille_entreprise, nom_contact,
                poste_contact, email, telephone, adresse, ville, code_postal,
                mot_de_passe_hash, numero_entreprise, site_web, description_entreprise
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            client['nom_entreprise'], client['secteur_activite'], client['taille_entreprise'],
            client['nom_contact'], client['poste_contact'], client['email'], client['telephone'],
            client['adresse'], client['ville'], client['code_postal'], hash_password(client['mot_de_passe']),
            client['numero_entreprise'], client['site_web'], client['description_entreprise']
        ))
    
    # Entreprises prestataires
    prestataires_demo = [
        {
            'nom_entreprise': 'Construction Excellence Québec Inc.',
            'domaines_expertise': '["Construction commerciale", "Construction industrielle", "Rénovation de bâtiments commerciaux"]',
            'taille_entreprise': 'PME (10-249 employés)',
            'nom_contact': 'Alex Martin',
            'poste_contact': 'Directeur général',
            'email': 'alex@constructionexcellence.ca',
            'telephone': '514-555-4001',
            'mot_de_passe': 'demo123',
            'certifications': '["RBQ: 5678-1234-01", "APCHQ", "ASP Construction", "ISO 9001:2015"]',
            'tarif_horaire_min': 85.0,
            'tarif_horaire_max': 150.0
        },
        {
            'nom_entreprise': 'Électricité Industrielle Québec',
            'domaines_expertise': '["Électricité industrielle", "Systèmes mécaniques (CVC)", "Automation"]',
            'taille_entreprise': 'PME (10-249 employés)',
            'nom_contact': 'Isabelle Roy',
            'poste_contact': 'Présidente',
            'email': 'isabelle@eiqc.ca',
            'telephone': '418-555-5002',
            'mot_de_passe': 'demo123',
            'certifications': '["RBQ: 9876-5432-01", "CEIQ", "Maître électricien", "Formation sécurité CCQ"]',
            'tarif_horaire_min': 95.0,
            'tarif_horaire_max': 180.0
        },
        {
            'nom_entreprise': 'Structures Métalliques Bergeron',
            'domaines_expertise': '["Structures d\'acier", "Béton et fondations", "Soudage certifié"]',
            'taille_entreprise': 'TPE (1-9 employés)',
            'nom_contact': 'Michel Bergeron',
            'poste_contact': 'Propriétaire et soudeur certifié',
            'email': 'michel@structures-bergeron.ca',
            'telephone': '450-555-6003',
            'mot_de_passe': 'demo123',
            'certifications': '["RBQ: 1357-2468-01", "Soudeur certifié CSA W47.1", "Formation grue mobile", "SIMDUT 2015"]',
            'tarif_horaire_min': 110.0,
            'tarif_horaire_max': 175.0
        }
    ]
    
    # Insérer les prestataires
    for prestataire in prestataires_demo:
        cursor.execute('''
            INSERT INTO entreprises_prestataires (
                nom_entreprise, domaines_expertise, taille_entreprise, nom_contact,
                poste_contact, email, telephone, mot_de_passe_hash, certifications,
                tarif_horaire_min, tarif_horaire_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prestataire['nom_entreprise'], prestataire['domaines_expertise'], prestataire['taille_entreprise'],
            prestataire['nom_contact'], prestataire['poste_contact'], prestataire['email'],
            prestataire['telephone'], hash_password(prestataire['mot_de_passe']),
            prestataire['certifications'], prestataire['tarif_horaire_min'], prestataire['tarif_horaire_max']
        ))
    
    # Documents requis pour inscription
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
    
    cursor.executemany('''
        INSERT INTO documents_requis 
        (type_entreprise, nom_document, obligatoire, description, formats_acceptes, taille_max_mb, ordre_affichage)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', documents_client + documents_prestataire)
    
    conn.commit()
    conn.close()
    
    print("Base de donnees complete initialisee avec succes!")
    print("- Tables principales: entreprises, demandes, soumissions, etc.")
    print("- Tables d'inscription: demandes_inscription, documents_requis, historique")
    print("- Donnees de demo: 3 clients + 3 prestataires")
    print("- Comptes admin: admin123")

if __name__ == "__main__":
    init_complete_database()