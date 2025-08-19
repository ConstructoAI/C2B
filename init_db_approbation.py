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

def init_database_approbation():
    """Initialise la base de données du système d'approbation de soumissions"""
    
    # FORCE: Supprimer l'ancienne base pour recréer avec la bonne structure
    if os.path.exists(DATABASE_PATH):
        try:
            os.remove(DATABASE_PATH)
            print("Ancienne base de données supprimée pour recréation")
        except OSError as e:
            print(f"Impossible de supprimer l'ancienne base: {e}")
            # Essayer de la vider au moins
            try:
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                for table in tables:
                    cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
                conn.commit()
                conn.close()
                print("Tables existantes supprimées")
            except:
                pass
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
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
            numero_entreprise TEXT,
            site_web TEXT,
            description_entreprise TEXT,
            mot_de_passe_hash TEXT NOT NULL,
            statut TEXT DEFAULT 'actif' CHECK(statut IN ('actif', 'inactif', 'suspendu')),
            date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_derniere_connexion TIMESTAMP
        )
    ''')
    
    # Table des entreprises prestataires (qui répondent aux demandes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entreprises_prestataires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_entreprise TEXT NOT NULL,
            numero_rbq TEXT NOT NULL,  -- Numéro de licence RBQ
            domaines_expertise TEXT NOT NULL,  -- JSON array
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
            certifications TEXT,  -- JSON array des certifications
            portfolio TEXT,  -- JSON array des projets réalisés
            tarif_horaire_min REAL DEFAULT 0.0,
            tarif_horaire_max REAL DEFAULT 0.0,
            disponibilite TEXT DEFAULT 'disponible',  -- disponible, occupe, indisponible
            langues_parlees TEXT DEFAULT 'Français',
            zones_service TEXT,  -- Zones géographiques desservies
            date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            statut TEXT DEFAULT 'actif',
            derniere_connexion TIMESTAMP,
            preferences_notification TEXT,
            note_moyenne REAL DEFAULT 0.0,
            nombre_evaluations INTEGER DEFAULT 0,
            nombre_projets_realises INTEGER DEFAULT 0,
            taux_reponse REAL DEFAULT 0.0,
            delai_reponse_moyen INTEGER DEFAULT 0  -- en heures
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
            criteres_evaluation TEXT,  -- JSON des critères et pondérations
            competences_requises TEXT,  -- JSON array
            niveau_experience_requis TEXT,  -- junior, intermediaire, senior, expert
            localisation_projet TEXT,
            mode_travail TEXT,  -- sur_site, remote, hybride
            documents TEXT,  -- Base64 des documents joints
            cahier_charges TEXT,  -- Cahier des charges détaillé
            nombre_soumissions_max INTEGER DEFAULT 10,
            statut TEXT DEFAULT 'brouillon',
            numero_reference TEXT UNIQUE,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_publication TIMESTAMP,
            date_fermeture TIMESTAMP,
            vue_par_prestataires INTEGER DEFAULT 0,
            nombre_soumissions_recues INTEGER DEFAULT 0,
            tags TEXT,  -- JSON array pour faciliter la recherche
            priorite TEXT DEFAULT 'normale',  -- faible, normale, elevee, urgente
            confidentiel BOOLEAN DEFAULT 0,
            accord_nda_requis BOOLEAN DEFAULT 0,
            FOREIGN KEY (client_id) REFERENCES entreprises_clientes (id)
        )
    ''')
    
    # Table des soumissions avec workflow d'approbation
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
            equipe_proposee TEXT,  -- JSON des membres de l'équipe
            budget_total REAL NOT NULL,
            detail_budget TEXT,  -- JSON détaillé du budget
            delai_livraison TEXT NOT NULL,
            date_debut_proposee DATE,
            date_fin_proposee DATE,
            conditions_generales TEXT,
            garanties TEXT,
            maintenance_support TEXT,
            inclusions TEXT,
            exclusions TEXT,
            options_supplementaires TEXT,  -- JSON des options
            documents_joints TEXT,  -- Base64 des documents
            portfolio_pertinent TEXT,  -- Références pertinentes
            validite_offre INTEGER DEFAULT 30,  -- en jours
            statut TEXT DEFAULT 'brouillon',
            note_auto_evaluation REAL,  -- Note basée sur les critères
            commentaires_internes TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_soumission TIMESTAMP,
            date_derniere_modification TIMESTAMP,
            vue_par_client BOOLEAN DEFAULT 0,
            date_vue_client TIMESTAMP,
            temps_preparation INTEGER,  -- temps passé en heures
            version INTEGER DEFAULT 1,
            soumission_parent_id INTEGER,  -- Pour les révisions
            FOREIGN KEY (demande_id) REFERENCES demandes_devis (id),
            FOREIGN KEY (prestataire_id) REFERENCES entreprises_prestataires (id),
            FOREIGN KEY (soumission_parent_id) REFERENCES soumissions (id),
            UNIQUE(demande_id, prestataire_id, version)
        )
    ''')
    
    # Table du processus d'approbation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processus_approbation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soumission_id INTEGER NOT NULL,
            etape_actuelle INTEGER DEFAULT 1,
            etape_nom TEXT,
            statut_etape TEXT DEFAULT 'en_cours',  -- en_cours, completee, bloquee
            evaluateur_id INTEGER,
            evaluateur_type TEXT,  -- client, admin, externe
            date_debut_etape TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_fin_etape TIMESTAMP,
            commentaires_etape TEXT,
            documents_etape TEXT,  -- Documents ajoutés à cette étape
            score_etape REAL,
            criteres_evaluation TEXT,  -- JSON des critères évalués
            decision TEXT,  -- approuve, rejete, en_attente, modif_requise
            raison_decision TEXT,
            prochaine_etape INTEGER,
            delai_etape_jours INTEGER,
            notification_envoyee BOOLEAN DEFAULT 0,
            FOREIGN KEY (soumission_id) REFERENCES soumissions (id)
        )
    ''')
    
    # Table des évaluations détaillées
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soumission_id INTEGER NOT NULL,
            evaluateur_id INTEGER NOT NULL,
            evaluateur_type TEXT NOT NULL,  -- client, prestataire, admin
            type_evaluation TEXT NOT NULL,  -- technique, financiere, globale
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
    
    # Table des messages et communications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demande_id INTEGER,
            soumission_id INTEGER,
            expediteur_id INTEGER NOT NULL,
            expediteur_type TEXT NOT NULL,  -- client, prestataire, admin
            destinataire_id INTEGER NOT NULL,
            destinataire_type TEXT NOT NULL,
            type_message TEXT DEFAULT 'general',  -- general, question, clarification, negociation
            sujet TEXT,
            contenu TEXT NOT NULL,
            pieces_jointes TEXT,  -- Base64 des pièces jointes
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
            utilisateur_type TEXT NOT NULL,  -- client, prestataire, admin
            type_notification TEXT NOT NULL,
            titre TEXT NOT NULL,
            message TEXT NOT NULL,
            lien_interne TEXT,  -- Lien vers la page concernée
            donnees_contexte TEXT,  -- JSON avec données contextuelles
            priorite TEXT DEFAULT 'normale',  -- faible, normale, elevee, urgente
            lu BOOLEAN DEFAULT 0,
            archive BOOLEAN DEFAULT 0,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_lecture TIMESTAMP,
            date_expiration TIMESTAMP,
            canal_notification TEXT DEFAULT 'app'  -- app, email, sms
        )
    ''')
    
    # Table des contrats et attributions
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
            livrables TEXT,  -- JSON des livrables attendus
            jalons TEXT,  -- JSON des jalons de paiement
            statut_contrat TEXT DEFAULT 'actif',  -- actif, suspendu, termine, resilie
            avancement_pourcentage REAL DEFAULT 0.0,
            montant_paye REAL DEFAULT 0.0,
            documents_contractuels TEXT,  -- Base64 des documents signés
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
            donnees_avant TEXT,  -- JSON des données avant modification
            donnees_apres TEXT,  -- JSON des données après modification
            adresse_ip TEXT,
            user_agent TEXT,
            date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details_supplementaires TEXT
        )
    ''')
    
    # Créer des index pour améliorer les performances
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
    
    # Insérer des données de démonstration
    
    # Clients particuliers de démonstration
    clients_demo = [
        {
            'nom_entreprise': 'TechnoSolutions Inc.',
            'secteur_activite': 'Développement immobilier résidentiel',
            'taille_entreprise': 'PME (10-249 employés)',
            'nom_contact': 'Marie Dubois',
            'poste_contact': 'Directrice des projets',
            'email': 'marie.dubois@technosolutions.ca',
            'telephone': '514-555-1001',
            'adresse': '1234 Rue Saint-Laurent',
            'ville': 'Montréal',
            'code_postal': 'H2X 1A1',
            'mot_de_passe': 'demo123',
            'numero_entreprise': '1234567890',
            'site_web': 'https://www.technosolutions.ca',
            'description_entreprise': 'Entreprise spécialisée dans les projets résidentiels et rénovations'
        },
        {
            'nom_entreprise': 'Commerce Plus Ltée',
            'secteur_activite': 'Centres commerciaux et retail',
            'taille_entreprise': 'ETI (250-4999 employés)',
            'nom_contact': 'Jean Tremblay',
            'poste_contact': 'Directeur des infrastructures',
            'email': 'jean.tremblay@commerceplus.ca',
            'telephone': '418-555-2002',
            'adresse': '567 Boulevard Charest Est',
            'ville': 'Québec',
            'code_postal': 'G1K 1A1',
            'mot_de_passe': 'demo123',
            'numero_entreprise': '2345678901',
            'site_web': 'https://www.commerceplus.ca',
            'description_entreprise': 'Développeur de centres commerciaux et espaces retail'
        },
        {
            'nom_entreprise': 'FinanceConseil Pro',
            'secteur_activite': 'Bureaux et tours à bureaux',
            'taille_entreprise': 'TPE (1-9 employés)',
            'nom_contact': 'Sophie Lavoie',
            'poste_contact': 'Gestionnaire des installations',
            'email': 'sophie.lavoie@financeconseil.ca',
            'telephone': '450-555-3003',
            'adresse': '890 Rue de la Paix',
            'ville': 'Laval',
            'code_postal': 'H7T 1A1',
            'mot_de_passe': 'demo123',
            'numero_entreprise': '3456789012',
            'site_web': 'https://www.financeconseil.ca',
            'description_entreprise': 'Cabinet de conseil financier avec bureaux modernes'
        }
    ]
    
    # Insérer les entreprises clientes
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
    
    # Entreprises de construction de démonstration
    prestataires_demo = [
        {
            'nom_entreprise': 'Construction Excellence Québec Inc.',
            'numero_rbq': '5678-1234-01',
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
            'numero_rbq': '9876-5432-01',
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
            'numero_rbq': '1357-2468-01',
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
                nom_entreprise, numero_rbq, domaines_expertise, taille_entreprise, nom_contact,
                poste_contact, email, telephone, mot_de_passe_hash, certifications,
                tarif_horaire_min, tarif_horaire_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prestataire['nom_entreprise'], prestataire['numero_rbq'], prestataire['domaines_expertise'], prestataire['taille_entreprise'],
            prestataire['nom_contact'], prestataire['poste_contact'], prestataire['email'],
            prestataire['telephone'], hash_password(prestataire['mot_de_passe']),
            prestataire['certifications'], prestataire['tarif_horaire_min'], prestataire['tarif_horaire_max']
        ))
    
    # Demandes de travaux résidentiels de démonstration
    demandes_demo = [
        {
            'client_id': 1,  # Marie Dubois
            'titre': 'Rénovation complète de salle de bain',
            'type_projet': 'Rénovation salle de bain',
            'description_detaillee': '''Nous souhaitons rénover entièrement notre salle de bain principale.
            
            SITUATION ACTUELLE:
            - Salle de bain de 8x10 pieds
            - Céramique des années 80 
            - Plomberie et électricité à refaire
            - Ventilation insuffisante
            
            TRAVAUX SOUHAITÉS:
            - Démolition complète
            - Nouvelle céramique moderne
            - Installation douche en verre
            - Nouveau vanité double
            - Plomberie et électricité aux normes
            - Éclairage LED et ventilateur
            
            CONTRAINTES:
            - Nous avons une seule salle de bain
            - Besoin de finir avant les vacances d'été
            - Budget serré mais qualité importante
            
            FOURNITURES:
            - Nous achetons la céramique et accessoires
            - Entrepreneur fournit matériel plomberie/électricité''',
            'budget_min': 8000.0,
            'budget_max': 15000.0,
            'delai_livraison': 'Court terme (1-3 mois)',
            'date_limite_soumissions': '2024-04-15 23:59:59',
            'competences_requises': '["Plomberie", "Électricité", "Céramique", "Rénovation"]',
            'niveau_experience_requis': 'intermediaire',
            'numero_reference': 'SE-20240301-001'
        },
        {
            'client_id': 2,  # Jean Tremblay
            'titre': 'Agrandissement cuisine avec îlot',
            'type_projet': 'Rénovation cuisine',
            'description_detaillee': '''Projet d'agrandissement et rénovation de cuisine dans un condo.
            
            CONTEXTE:
            - Condo de 900 pi² au 12e étage
            - Cuisine actuelle trop petite
            - Veut ouvrir sur le salon
            - Ajout d'un îlot central
            
            TRAVAUX REQUIS:
            - Démolition mur non-porteur
            - Nouvelle cuisine avec îlot
            - Électricité pour îlot et éclairage
            - Plomberie pour évier d'îlot
            - Plancher uniforme salon-cuisine
            
            MATÉRIAUX PRÉFÉRÉS:
            - Armoires de cuisine moderne
            - Comptoir quartz
            - Électroménagers stainless
            - Plancher bois franc
            
            DÉLAIS:
            - Flexible sur les dates
            - Peut séjourner ailleurs si nécessaire''',
            'budget_min': 25000.0,
            'budget_max': 45000.0,
            'delai_livraison': 'Moyen terme (3-6 mois)',
            'date_limite_soumissions': '2024-04-20 23:59:59',
            'competences_requises': '["Cuisine", "Démolition", "Plomberie", "Électricité", "Plancher"]',
            'niveau_experience_requis': 'senior',
            'numero_reference': 'SE-20240302-002'
        },
        {
            'client_id': 3,  # Sophie Lavoie
            'titre': 'Aménagement sous-sol familial',
            'type_projet': 'Rénovation sous-sol',
            'description_detaillee': '''Aménagement du sous-sol pour créer un espace familial.
            
            ESPACE DISPONIBLE:
            - Sous-sol de 600 pi² non-aménagé
            - Hauteur de 7 pieds
            - Humidité sous contrôle
            - Accès par escalier intérieur
            
            AMÉNAGEMENT SOUHAITÉ:
            - Salon familial avec TV
            - Salle de jeu pour enfants
            - Bureau à domicile
            - Salle de lavage améliorée
            - Demi-salle de bain
            
            BESOINS TECHNIQUES:
            - Isolation et finition murs
            - Plafond suspendu
            - Éclairage encastré
            - Prises électriques multiples
            - Plancher stratifié
            
            BUDGET ET TIMING:
            - Budget flexible selon options
            - Projet pour l'automne''',
            'budget_min': 15000.0,
            'budget_max': 30000.0,
            'delai_livraison': 'Moyen terme (3-6 mois)',
            'date_limite_soumissions': '2024-04-10 23:59:59',
            'competences_requises': '["Sous-sol", "Isolation", "Électricité", "Plomberie", "Plancher"]',
            'niveau_experience_requis': 'intermediaire',
            'numero_reference': 'SE-20240303-003'
        }
    ]
    
    # Insérer les demandes
    for demande in demandes_demo:
        cursor.execute('''
            INSERT INTO demandes_devis (
                client_id, titre, type_projet, description_detaillee, budget_min, budget_max,
                delai_livraison, date_limite_soumissions, competences_requises,
                niveau_experience_requis, numero_reference, statut
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'publiee')
        ''', (
            demande['client_id'], demande['titre'], demande['type_projet'],
            demande['description_detaillee'], demande['budget_min'], demande['budget_max'],
            demande['delai_livraison'], demande['date_limite_soumissions'],
            demande['competences_requises'], demande['niveau_experience_requis'],
            demande['numero_reference']
        ))
    
    # Soumissions de démonstration
    soumissions_demo = [
        {
            'demande_id': 1,
            'prestataire_id': 1,  # WebDev Experts
            'titre_soumission': 'Plateforme e-commerce moderne avec React & Node.js',
            'resume_executif': '''Nous proposons le développement d'une plateforme e-commerce complète utilisant les dernières technologies web.''',
            'proposition_technique': '''ARCHITECTURE TECHNIQUE:
            
            Frontend:
            - React 18 avec TypeScript
            - Redux Toolkit pour la gestion d'état
            - Material-UI pour l'interface utilisateur
            - Progressive Web App (PWA)
            
            Backend:
            - Node.js avec Express.js
            - Architecture REST API
            - Authentification JWT
            - Validation des données avec Joi
            
            Base de données:
            - PostgreSQL avec Prisma ORM
            - Redis pour le cache
            - Structure optimisée pour l'e-commerce
            
            Intégrations:
            - Stripe pour les paiements
            - SendGrid pour les emails
            - AWS S3 pour les images
            - Google Analytics''',
            'budget_total': 22000.0,
            'delai_livraison': '10 semaines',
            'statut': 'soumise'
        },
        {
            'demande_id': 2,
            'prestataire_id': 2,  # Marketing Digital Pro
            'titre_soumission': 'Stratégie marketing 360° pour le lancement produit',
            'resume_executif': '''Campagne marketing multi-canaux avec approche data-driven pour maximiser le ROI.''',
            'proposition_technique': '''STRATÉGIE PROPOSÉE:
            
            Phase 1: Analyse et préparation (4 semaines)
            - Audit concurrentiel approfondi
            - Personas détaillés et customer journey
            - Stratégie de contenu et calendrier éditorial
            - Configuration des outils de tracking
            
            Phase 2: Lancement et acquisition (8 semaines)
            - Campagnes Google Ads optimisées
            - Social media marketing (Facebook, Instagram, LinkedIn)
            - Content marketing (blog, vidéos, infographies)
            - Email marketing automation
            
            Phase 3: Optimisation et scaling (4 semaines)
            - A/B testing des campagnes
            - Optimisation du taux de conversion
            - Influencer partnerships
            - Reporting détaillé et recommandations''',
            'budget_total': 42000.0,
            'delai_livraison': '16 semaines',
            'statut': 'en_evaluation'
        }
    ]
    
    # Insérer les soumissions
    for soumission in soumissions_demo:
        cursor.execute('''
            INSERT INTO soumissions (
                demande_id, prestataire_id, titre_soumission, resume_executif,
                proposition_technique, budget_total, delai_livraison, statut
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            soumission['demande_id'], soumission['prestataire_id'],
            soumission['titre_soumission'], soumission['resume_executif'],
            soumission['proposition_technique'], soumission['budget_total'],
            soumission['delai_livraison'], soumission['statut']
        ))
    
    conn.commit()
    conn.close()
    
    print("Base de données P2B Construction initialisée avec succès!")
    print("\nDonnées créées:")
    print("   - 3 clients particuliers avec comptes demo")
    print("   - 3 entreprises de construction avec comptes demo")
    print("   - 3 demandes de travaux résidentiels détaillées")
    print("   - 2 soumissions de démonstration")
    print("\nComptes de test:")
    print("   - Admin: mot de passe 'admin123'")
    print("   - Particuliers: emails ci-dessus + mot de passe 'demo123'")
    print("   - Entrepreneurs: emails ci-dessus + mot de passe 'demo123'")
    print("\nFonctionnalités du système P2B:")
    print("   - Demandes de travaux résidentiels")
    print("   - Soumissions simplifiées")
    print("   - Évaluations adaptées aux particuliers")
    print("   - Communication directe")
    print("   - Suivi des projets résidentiels")
    print("   - Gestion simplifiée des contrats")

if __name__ == "__main__":
    init_database_approbation()