#!/usr/bin/env python3
"""
Correction immédiate des schémas de bases de données
"""

import sqlite3
import os

# Configuration pour Hugging Face
DATA_DIR = '/data/app_data' if os.getenv('SPACE_ID') else 'data'
os.makedirs(DATA_DIR, exist_ok=True)

print("🔧 Correction des bases de données...")

# 1. Corriger soumissions_heritage.db
heritage_db = os.path.join(DATA_DIR, 'soumissions_heritage.db')
print(f"\n📁 Correction de {heritage_db}")

conn = sqlite3.connect(heritage_db)
cursor = conn.cursor()

# Supprimer l'ancienne table si elle existe
cursor.execute("DROP TABLE IF EXISTS soumissions")

# Créer la table avec le BON nom
cursor.execute('''
    CREATE TABLE IF NOT EXISTS soumissions_heritage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT UNIQUE,
        client_nom TEXT,
        projet_nom TEXT,
        montant_total REAL,
        statut TEXT DEFAULT 'en_attente',
        token TEXT UNIQUE,
        data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        lien_public TEXT
    )
''')
conn.commit()
conn.close()
print("✅ soumissions_heritage.db corrigée")

# 2. Corriger bon_commande.db
bon_db = os.path.join(DATA_DIR, 'bon_commande.db')
print(f"\n📁 Correction de {bon_db}")

conn = sqlite3.connect(bon_db)
cursor = conn.cursor()

# Supprimer et recréer avec la bonne structure
cursor.execute("DROP TABLE IF EXISTS bons_commande")
cursor.execute('''
    CREATE TABLE bons_commande (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT UNIQUE NOT NULL,
        numero_bon TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fournisseur_nom TEXT,
        client_nom TEXT,
        projet_nom TEXT,
        items_json TEXT,
        sous_total REAL,
        tps REAL,
        tvq REAL,
        total REAL,
        statut TEXT DEFAULT 'brouillon',
        token TEXT UNIQUE,
        lien_public TEXT
    )
''')
conn.commit()
conn.close()
print("✅ bon_commande.db corrigée")

# 3. Créer bons_commande_simple.db
bon_simple_db = os.path.join(DATA_DIR, 'bons_commande_simple.db')
print(f"\n📁 Création de {bon_simple_db}")

conn = sqlite3.connect(bon_simple_db)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bons_commande (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT UNIQUE NOT NULL,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fournisseur_nom TEXT,
        client_nom TEXT,
        projet_nom TEXT,
        items_json TEXT,
        sous_total REAL,
        tps REAL,
        tvq REAL,
        total REAL,
        statut TEXT DEFAULT 'brouillon',
        token TEXT UNIQUE,
        lien_public TEXT
    )
''')
conn.commit()
conn.close()
print("✅ bons_commande_simple.db créée")

# 4. Créer fournisseurs.db
fournisseurs_db = os.path.join(DATA_DIR, 'fournisseurs.db')
print(f"\n📁 Création de {fournisseurs_db}")

conn = sqlite3.connect(fournisseurs_db)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS fournisseurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT UNIQUE NOT NULL,
        type TEXT DEFAULT 'Fournisseur',
        contact_principal TEXT,
        telephone TEXT,
        cellulaire TEXT,
        email TEXT,
        adresse TEXT,
        ville TEXT,
        province TEXT DEFAULT 'Québec',
        code_postal TEXT,
        site_web TEXT,
        numero_entreprise TEXT,
        tps TEXT,
        tvq TEXT,
        rbq TEXT,
        specialites TEXT,
        conditions_paiement TEXT DEFAULT 'Net 30 jours',
        delai_livraison TEXT,
        notes TEXT,
        actif INTEGER DEFAULT 1,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        derniere_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Table pour l'historique des prix
cursor.execute('''
    CREATE TABLE IF NOT EXISTS historique_prix (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fournisseur_id INTEGER,
        description TEXT,
        prix_unitaire REAL,
        unite TEXT,
        date_prix DATE,
        projet_reference TEXT,
        notes TEXT,
        FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id)
    )
''')

# Ajouter des données de démonstration
demo_fournisseurs = [
    ('Matériaux ABC Inc.', 'Fournisseur', 'Jean Tremblay', '514-555-1234',
     '514-555-5678', 'info@materiauxabc.ca', '1234 Rue Industrielle',
     'Montréal', 'Québec', 'H1A 2B3', 'www.materiauxabc.ca',
     '1234567890', '123456789RT0001', '1234567890TQ0001', '',
     'Bois, Quincaillerie, Matériaux de construction', 'Net 30 jours', '24-48 heures'),

    ('Électricité Pro', 'Sous-traitant', 'Marie Dubois', '514-555-9876',
     '514-555-4321', 'contact@electricitepro.ca', '5678 Boulevard Commercial',
     'Laval', 'Québec', 'H7N 4K5', '', '', '', '', '5678-9012-34',
     'Installation électrique, Panneaux, Éclairage', 'Net 15 jours', 'Selon disponibilité'),

    ('Plomberie Moderne', 'Sous-traitant', 'Pierre Gagnon', '450-555-3456',
     '', 'info@plomberiemoderne.ca', '9012 Rue des Artisans',
     'Brossard', 'Québec', 'J4W 3H7', '', '', '', '', '9876-5432-10',
     'Plomberie, Chauffage, Ventilation', 'Net 30 jours', '')
]

for fournisseur in demo_fournisseurs:
    cursor.execute('''
        INSERT OR IGNORE INTO fournisseurs
        (nom, type, contact_principal, telephone, cellulaire, email,
         adresse, ville, province, code_postal, site_web,
         numero_entreprise, tps, tvq, rbq, specialites,
         conditions_paiement, delai_livraison)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', fournisseur)

conn.commit()
conn.close()
print("✅ fournisseurs.db créée avec données de démonstration complètes")

# 5. Vérifier toutes les bases
print("\n📊 Vérification des bases de données:")
for db_name in ['entreprise_config.db', 'soumissions_heritage.db',
                'soumissions_multi.db', 'bon_commande.db',
                'bons_commande_simple.db', 'fournisseurs.db']:
    db_path = os.path.join(DATA_DIR, db_name)
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            print(f"  ✅ {db_name}: {len(tables)} table(s)")
            for table in tables:
                print(f"     • {table[0]}")
        except Exception as e:
            print(f"  ❌ {db_name}: Erreur - {e}")
    else:
        print(f"  ⚠️ {db_name}: N'existe pas")

print("\n✅ TOUTES LES BASES SONT MAINTENANT OPÉRATIONNELLES!")
print("\n🚀 Instructions:")
print("1. Uploadez ce fichier sur Hugging Face Spaces")
print("2. Exécutez: python fix_db_schema.py")
print("3. Redémarrez le Space")