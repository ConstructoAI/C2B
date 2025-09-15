#!/usr/bin/env python3
"""
Script d'initialisation du stockage persistant pour Hugging Face Spaces
Gère la création des répertoires et la migration des données
"""

import os
import shutil
import sqlite3
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_persistent_storage():
    """Initialise le stockage persistant sur Hugging Face"""

    # Détection de l'environnement Hugging Face
    is_huggingface = os.getenv('SPACE_ID') is not None

    if is_huggingface:
        # Vérifier si /data est accessible (stockage persistant activé)
        if os.path.exists('/data') and os.access('/data', os.W_OK):
            # Stockage persistant disponible
            PERSISTENT_DIR = '/data'
            logger.info("Using persistent storage at /data")
        else:
            # Fallback sur le home directory si /data n'est pas disponible
            PERSISTENT_DIR = os.path.expanduser('~/app_data')
            logger.warning("/data not accessible. Using fallback directory: ~/app_data")
            logger.warning("⚠️ IMPORTANT: Activez le stockage persistant dans Settings → Persistent Storage pour conserver vos données!")

        DATA_DIR = os.path.join(PERSISTENT_DIR, 'app_data')
        FILES_DIR = os.path.join(PERSISTENT_DIR, 'app_files')
        BACKUP_DIR = os.path.join(PERSISTENT_DIR, 'backups')
        INIT_MARKER = os.path.join(PERSISTENT_DIR, '.initialized')
    else:
        # Configuration locale (Windows ou Linux)
        PERSISTENT_DIR = os.getcwd()
        DATA_DIR = os.path.join(PERSISTENT_DIR, 'data')
        FILES_DIR = os.path.join(PERSISTENT_DIR, 'files')
        BACKUP_DIR = os.path.join(PERSISTENT_DIR, 'data', 'backups')
        INIT_MARKER = os.path.join(DATA_DIR, '.initialized')

    logger.info(f"Environment: {'Hugging Face' if is_huggingface else 'Local'}")
    logger.info(f"Persistent directory: {PERSISTENT_DIR}")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info(f"Files directory: {FILES_DIR}")
    logger.info(f"Backup directory: {BACKUP_DIR}")

    # Créer les répertoires s'ils n'existent pas
    for directory in [DATA_DIR, FILES_DIR, BACKUP_DIR]:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            else:
                logger.info(f"Directory exists: {directory}")
        except PermissionError as e:
            logger.error(f"Permission denied creating {directory}: {e}")
            # Essayer un répertoire alternatif dans le home
            alt_dir = os.path.expanduser(f"~/{os.path.basename(directory)}")
            try:
                os.makedirs(alt_dir, exist_ok=True)
                logger.info(f"Created alternative directory: {alt_dir}")
                # Mettre à jour le chemin
                if 'app_data' in directory:
                    DATA_DIR = alt_dir
                elif 'app_files' in directory:
                    FILES_DIR = alt_dir
                elif 'backups' in directory:
                    BACKUP_DIR = alt_dir
            except Exception as e2:
                logger.error(f"Failed to create alternative directory: {e2}")

    # Vérifier si c'est la première initialisation
    first_init = not os.path.exists(INIT_MARKER)

    if first_init and is_huggingface:
        logger.info("First initialization on Hugging Face - migrating data...")

        # Migration des bases de données existantes si présentes
        local_data_dir = os.path.join(os.getcwd(), 'data')
        if os.path.exists(local_data_dir):
            databases = [
                'entreprise_config.db',
                'soumissions_heritage.db',
                'soumissions_multi.db',
                'bon_commande.db'
            ]

            for db_file in databases:
                src_path = os.path.join(local_data_dir, db_file)
                dst_path = os.path.join(DATA_DIR, db_file)

                if os.path.exists(src_path) and not os.path.exists(dst_path):
                    try:
                        shutil.copy2(src_path, dst_path)
                        logger.info(f"Migrated database: {db_file}")
                    except Exception as e:
                        logger.error(f"Failed to migrate {db_file}: {e}")

        # Migration des fichiers uploadés si présents
        local_files_dir = os.path.join(os.getcwd(), 'files')
        if os.path.exists(local_files_dir):
            try:
                for file_name in os.listdir(local_files_dir):
                    src_file = os.path.join(local_files_dir, file_name)
                    dst_file = os.path.join(FILES_DIR, file_name)
                    if os.path.isfile(src_file) and not os.path.exists(dst_file):
                        shutil.copy2(src_file, dst_file)
                        logger.info(f"Migrated file: {file_name}")
            except Exception as e:
                logger.error(f"Failed to migrate files: {e}")

        # Créer le marqueur d'initialisation
        with open(INIT_MARKER, 'w') as f:
            f.write(f"Initialized on: {os.environ.get('SPACE_ID', 'local')}\n")
        logger.info("Initialization complete!")

    # Initialiser les bases de données si elles n'existent pas
    databases_config = {
        'entreprise_config.db': '''
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'soumissions_heritage.db': '''
            CREATE TABLE IF NOT EXISTS soumissions_heritage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE,
                client_nom TEXT,
                client_email TEXT,
                client_telephone TEXT,
                projet_nom TEXT,
                projet_adresse TEXT,
                statut TEXT DEFAULT 'en_attente',
                montant_total REAL,
                token TEXT UNIQUE,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                lien_public TEXT,
                date_decision TIMESTAMP,
                commentaire_client TEXT
            )
        ''',
        'soumissions_multi.db': '''
            CREATE TABLE IF NOT EXISTS soumissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_soumission TEXT UNIQUE NOT NULL,
                nom_client TEXT NOT NULL,
                email_client TEXT,
                telephone_client TEXT,
                nom_projet TEXT,
                montant_total REAL,
                file_type TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT,
                file_size INTEGER,
                file_data BLOB,
                html_preview TEXT,
                token TEXT UNIQUE NOT NULL,
                statut TEXT DEFAULT 'en_attente',
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_envoi TIMESTAMP,
                date_decision TIMESTAMP,
                commentaire_client TEXT,
                ip_client TEXT,
                lien_public TEXT,
                metadata TEXT
            )
        ''',
        'bon_commande.db': '''
            CREATE TABLE IF NOT EXISTS bons_commande (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE NOT NULL,
                fournisseur_nom TEXT NOT NULL,
                fournisseur_adresse TEXT,
                fournisseur_contact TEXT,
                fournisseur_telephone TEXT,
                fournisseur_email TEXT,
                projet_reference TEXT,
                date_emission DATE NOT NULL,
                date_livraison DATE,
                lieu_livraison TEXT,
                conditions_paiement TEXT,
                validite_jours INTEGER DEFAULT 30,
                items TEXT NOT NULL,
                sous_total REAL NOT NULL,
                tps REAL,
                tvq REAL,
                total REAL NOT NULL,
                notes TEXT,
                statut TEXT DEFAULT 'brouillon',
                token TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approuve_par TEXT,
                date_approbation TIMESTAMP,
                signature_acheteur TEXT,
                signature_fournisseur TEXT,
                metadata TEXT
            )
        '''
    }

    for db_name, create_sql in databases_config.items():
        db_path = os.path.join(DATA_DIR, db_name)
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(create_sql)

            # Créer les index pour améliorer les performances
            if 'soumissions_heritage' in db_name:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_token ON soumissions_heritage(token)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_statut ON soumissions_heritage(statut)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_numero ON soumissions_heritage(numero)')
            elif 'soumissions_multi' in db_name:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_token ON soumissions(token)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_statut ON soumissions(statut)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_numero ON soumissions(numero_soumission)')
            elif 'bon_commande' in db_name:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_numero ON bons_commande(numero)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_token ON bons_commande(token)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_statut ON bons_commande(statut)')

            conn.commit()
            conn.close()
            logger.info(f"Database initialized: {db_name}")
        except Exception as e:
            logger.error(f"Failed to initialize {db_name}: {e}")

    # Définir les variables d'environnement pour l'application
    os.environ['DATA_DIR'] = DATA_DIR
    os.environ['FILES_DIR'] = FILES_DIR
    os.environ['BACKUP_DIR'] = BACKUP_DIR

    logger.info("Persistent storage initialization complete!")
    return {
        'data_dir': DATA_DIR,
        'files_dir': FILES_DIR,
        'backup_dir': BACKUP_DIR,
        'is_huggingface': is_huggingface,
        'first_init': first_init
    }

if __name__ == "__main__":
    result = init_persistent_storage()
    print("\nPersistent Storage Configuration:")
    for key, value in result.items():
        print(f"  {key}: {value}")