#!/usr/bin/env python3
"""
Test de vérification des conflits de numérotation
Simule la création de soumissions dans les deux modules
"""

import sqlite3
import os
import sys
from datetime import datetime

# Ajouter le répertoire courant au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_test_environment():
    """Prépare l'environnement de test"""
    print("=== PREPARATION DE L'ENVIRONNEMENT DE TEST ===\n")

    # Créer le dossier data s'il n'existe pas
    os.makedirs('data', exist_ok=True)

    # Sauvegarder les bases existantes
    for db_file in ['soumissions_heritage.db', 'soumissions_multi.db']:
        db_path = f'data/{db_file}'
        backup_path = f'data/{db_file}.backup'
        if os.path.exists(db_path):
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"Sauvegarde créée: {backup_path}")

    return True

def test_numero_manager():
    """Test le module numero_manager"""
    print("\n=== TEST 1: Module numero_manager ===")

    try:
        from numero_manager import get_safe_unique_number

        # S'assurer que les tables existent
        conn = sqlite3.connect('data/soumissions_heritage.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS soumissions_heritage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE,
                client_nom TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

        numbers = []
        for i in range(3):
            num = get_safe_unique_number()
            numbers.append(num)
            print(f"  Numéro généré {i+1}: {num}")

            # IMPORTANT: Simuler l'insertion pour que le prochain appel trouve le numéro
            conn = sqlite3.connect('data/soumissions_heritage.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO soumissions_heritage (numero, client_nom)
                VALUES (?, ?)
            ''', (num, f'Test Manager {i+1}'))
            conn.commit()
            conn.close()

        # Vérifier l'unicité
        if len(numbers) == len(set(numbers)):
            print("  OK: Tous les numeros sont uniques via numero_manager")
            return True, numbers
        else:
            print("  ERREUR: DOUBLONS detectes via numero_manager!")
            print(f"    Numeros: {numbers}")
            print(f"    Uniques: {set(numbers)}")
            return False, numbers

    except ImportError:
        print("  ! Module numero_manager non disponible")
        return None, []

def test_app_fallback():
    """Test le fallback de app.py"""
    print("\n=== TEST 2: Fallback app.py ===")

    # Importer la fonction depuis app.py
    try:
        # Forcer l'utilisation du fallback en renommant temporairement numero_manager
        import_failed = False
        if os.path.exists('numero_manager.py'):
            os.rename('numero_manager.py', 'numero_manager.py.tmp')
            import_failed = True

        from app import get_next_submission_number

        numbers = []
        for i in range(3):
            num = get_next_submission_number()
            numbers.append(num)
            print(f"  Numéro généré {i+1}: {num}")

            # Simuler l'insertion dans la base
            conn = sqlite3.connect('data/soumissions_multi.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS soumissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_soumission TEXT UNIQUE NOT NULL,
                    nom_client TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            import uuid
            cursor.execute('''
                INSERT INTO soumissions (numero_soumission, nom_client, file_type, file_name, token)
                VALUES (?, ?, ?, ?, ?)
            ''', (num, f'Client Test App {i+1}', '.pdf', 'test.pdf', str(uuid.uuid4())))
            conn.commit()
            conn.close()

        # Restaurer numero_manager
        if import_failed:
            os.rename('numero_manager.py.tmp', 'numero_manager.py')

        # Vérifier l'unicité
        if len(numbers) == len(set(numbers)):
            print("  OK: Tous les numeros sont uniques via app.py fallback")
            return True, numbers
        else:
            print("  ERREUR: DOUBLONS detectes via app.py fallback!")
            return False, numbers

    except Exception as e:
        print(f"  Erreur: {e}")
        # Restaurer numero_manager si nécessaire
        if os.path.exists('numero_manager.py.tmp'):
            os.rename('numero_manager.py.tmp', 'numero_manager.py')
        return False, []

def test_heritage_fallback():
    """Test le fallback de soumission_heritage.py"""
    print("\n=== TEST 3: Fallback soumission_heritage.py ===")

    try:
        # Forcer l'utilisation du fallback
        import_failed = False
        if os.path.exists('numero_manager.py'):
            os.rename('numero_manager.py', 'numero_manager.py.tmp')
            import_failed = True

        from soumission_heritage import generate_numero_soumission

        numbers = []
        for i in range(3):
            num = generate_numero_soumission()
            numbers.append(num)
            print(f"  Numéro généré {i+1}: {num}")

            # Simuler l'insertion dans la base
            conn = sqlite3.connect('data/soumissions_heritage.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS soumissions_heritage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT UNIQUE,
                    client_nom TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                INSERT INTO soumissions_heritage (numero, client_nom)
                VALUES (?, ?)
            ''', (num, f'Client Test Heritage {i+1}'))
            conn.commit()
            conn.close()

        # Restaurer numero_manager
        if import_failed:
            os.rename('numero_manager.py.tmp', 'numero_manager.py')

        # Vérifier l'unicité
        if len(numbers) == len(set(numbers)):
            print("  OK: Tous les numeros sont uniques via heritage fallback")
            return True, numbers
        else:
            print("  ERREUR: DOUBLONS detectes via heritage fallback!")
            return False, numbers

    except Exception as e:
        print(f"  Erreur: {e}")
        # Restaurer numero_manager si nécessaire
        if os.path.exists('numero_manager.py.tmp'):
            os.rename('numero_manager.py.tmp', 'numero_manager.py')
        return False, []

def test_cross_module_conflict():
    """Test de conflit entre les modules"""
    print("\n=== TEST 4: Conflit entre modules ===")

    all_numbers = []

    # Collecter tous les numéros des bases
    try:
        # Heritage
        if os.path.exists('data/soumissions_heritage.db'):
            conn = sqlite3.connect('data/soumissions_heritage.db')
            cursor = conn.cursor()
            cursor.execute('SELECT numero FROM soumissions_heritage')
            for row in cursor.fetchall():
                all_numbers.append(('Heritage', row[0]))
            conn.close()

        # Multi
        if os.path.exists('data/soumissions_multi.db'):
            conn = sqlite3.connect('data/soumissions_multi.db')
            cursor = conn.cursor()
            cursor.execute('SELECT numero_soumission FROM soumissions')
            for row in cursor.fetchall():
                all_numbers.append(('Multi', row[0]))
            conn.close()

        # Vérifier les doublons
        numbers_only = [num for _, num in all_numbers]
        unique_numbers = set(numbers_only)

        print(f"  Total de numéros: {len(all_numbers)}")
        print(f"  Numéros uniques: {len(unique_numbers)}")

        if len(numbers_only) == len(unique_numbers):
            print("  OK: AUCUN CONFLIT - Tous les numeros sont uniques entre les modules!")
            return True
        else:
            print("  ERREUR: CONFLITS DETECTES!")
            # Trouver les doublons
            from collections import Counter
            counter = Counter(numbers_only)
            for num, count in counter.items():
                if count > 1:
                    sources = [source for source, n in all_numbers if n == num]
                    print(f"    - {num}: présent dans {sources}")
            return False

    except Exception as e:
        print(f"  Erreur: {e}")
        return False

def cleanup_test():
    """Nettoie après les tests"""
    print("\n=== NETTOYAGE ===")

    # Restaurer les bases depuis les sauvegardes
    for db_file in ['soumissions_heritage.db', 'soumissions_multi.db']:
        db_path = f'data/{db_file}'
        backup_path = f'data/{db_file}.backup'

        if os.path.exists(backup_path):
            import shutil
            shutil.copy2(backup_path, db_path)
            os.remove(backup_path)
            print(f"  Base restaurée: {db_file}")
        elif os.path.exists(db_path):
            # Si pas de backup, supprimer la base de test
            os.remove(db_path)
            print(f"  Base de test supprimée: {db_file}")

    # S'assurer que numero_manager.py est restauré
    if os.path.exists('numero_manager.py.tmp'):
        os.rename('numero_manager.py.tmp', 'numero_manager.py')
        print("  Module numero_manager.py restauré")

def main():
    print("=" * 60)
    print("TEST DE VERIFICATION DES CONFLITS DE NUMEROTATION")
    print("=" * 60)

    try:
        # Préparer l'environnement
        setup_test_environment()

        # Exécuter les tests
        results = []

        # Test 1: numero_manager
        success1, nums1 = test_numero_manager()
        if success1 is not None:
            results.append(('numero_manager', success1))

        # Test 2: app.py fallback
        success2, nums2 = test_app_fallback()
        results.append(('app.py fallback', success2))

        # Test 3: heritage fallback
        success3, nums3 = test_heritage_fallback()
        results.append(('heritage fallback', success3))

        # Test 4: Vérifier les conflits entre modules
        success4 = test_cross_module_conflict()
        results.append(('Conflits cross-module', success4))

        # Résumé
        print("\n" + "=" * 60)
        print("RESUME DES TESTS")
        print("=" * 60)

        all_success = True
        for test_name, success in results:
            status = "OK REUSSI" if success else "ERREUR ECHOUE"
            print(f"  {test_name}: {status}")
            if not success:
                all_success = False

        print("\n" + "=" * 60)
        if all_success:
            print(">>> TOUS LES TESTS SONT REUSSIS <<<")
            print("La numérotation est maintenant unifiée et sans conflit!")
        else:
            print("!!! CERTAINS TESTS ONT ECHOUE !!!")
            print("Il reste des problèmes de numérotation à corriger!")
        print("=" * 60)

    finally:
        # Nettoyer après les tests
        cleanup_test()

if __name__ == "__main__":
    main()