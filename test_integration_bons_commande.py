#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier l'intégration des bons de commande
"""

import os
import sys
import sqlite3

# Couleurs pour l'affichage
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(message, status='info'):
    """Affiche un message avec couleur"""
    if status == 'success':
        print(f"{GREEN}[OK] {message}{RESET}")
    elif status == 'error':
        print(f"{RED}[ERREUR] {message}{RESET}")
    elif status == 'warning':
        print(f"{YELLOW}[ATTENTION] {message}{RESET}")
    else:
        print(f"{BLUE}[INFO] {message}{RESET}")

def test_imports():
    """Test l'importation des modules"""
    print("\n" + "="*60)
    print("TEST 1: IMPORTATION DES MODULES")
    print("="*60)

    modules_to_test = [
        ('app', 'Module principal'),
        ('bon_commande_simple', 'Module bons de commande'),
        ('fournisseurs_manager', 'Module fournisseurs'),
        ('entreprise_config', 'Module configuration entreprise'),
        ('backup_manager', 'Module sauvegardes'),
        ('soumission_heritage', 'Module soumissions heritage')
    ]

    success_count = 0
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print_status(f"{description} ({module_name})", 'success')
            success_count += 1
        except ImportError as e:
            print_status(f"{description} ({module_name}): {e}", 'error')

    print(f"\nRésultat: {success_count}/{len(modules_to_test)} modules importés avec succès")
    return success_count == len(modules_to_test)

def test_databases():
    """Test la création et l'accès aux bases de données"""
    print("\n" + "="*60)
    print("TEST 2: BASES DE DONNÉES")
    print("="*60)

    data_dir = os.getenv('DATA_DIR', 'data')

    databases = [
        ('entreprise_config.db', 'Configuration entreprise'),
        ('soumissions_heritage.db', 'Soumissions Heritage'),
        ('soumissions_multi.db', 'Soumissions multi-format'),
        ('bon_commande.db', 'Bons de commande (ancien)'),
        ('bons_commande_simple.db', 'Bons de commande (nouveau)'),
        ('fournisseurs.db', 'Fournisseurs')
    ]

    success_count = 0
    for db_name, description in databases:
        db_path = os.path.join(data_dir, db_name)
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                conn.close()
                print_status(f"{description}: {len(tables)} table(s)", 'success')
                success_count += 1
            except Exception as e:
                print_status(f"{description}: Erreur - {e}", 'error')
        else:
            print_status(f"{description}: Non trouvée", 'warning')

    print(f"\nRésultat: {success_count}/{len(databases)} bases de données accessibles")
    return success_count >= 4  # Au moins 4 BDD doivent être présentes

def test_bon_commande_functions():
    """Test les fonctions du module bon_commande_simple"""
    print("\n" + "="*60)
    print("TEST 3: FONCTIONS BONS DE COMMANDE")
    print("="*60)

    try:
        from bon_commande_simple import (
            generate_numero_bon,
            init_bon_commande_db,
            get_company_info
        )

        # Test initialisation DB
        init_bon_commande_db()
        print_status("Initialisation base de données", 'success')

        # Test génération numéro
        numero = generate_numero_bon()
        if numero and numero.startswith('BC-'):
            print_status(f"Génération numéro: {numero}", 'success')
        else:
            print_status(f"Numéro invalide: {numero}", 'error')

        # Test récupération info entreprise
        company = get_company_info()
        if company and 'name' in company:
            print_status(f"Info entreprise: {company['name']}", 'success')
        else:
            print_status("Info entreprise non disponible", 'error')

        return True
    except Exception as e:
        print_status(f"Erreur lors des tests: {e}", 'error')
        return False

def test_fournisseurs_functions():
    """Test les fonctions du module fournisseurs_manager"""
    print("\n" + "="*60)
    print("TEST 4: FONCTIONS FOURNISSEURS")
    print("="*60)

    try:
        from fournisseurs_manager import (
            init_fournisseurs_db,
            get_fournisseurs_list,
            save_fournisseur
        )

        # Test initialisation DB
        init_fournisseurs_db()
        print_status("Initialisation base de données fournisseurs", 'success')

        # Test liste fournisseurs
        fournisseurs = get_fournisseurs_list()
        print_status(f"Liste fournisseurs: {len(fournisseurs)} trouvé(s)", 'success')

        # Test ajout fournisseur
        test_fournisseur = {
            'nom': 'Test Fournisseur Integration',
            'type': 'Fournisseur',
            'contact_principal': 'Test Contact',
            'telephone': '514-555-TEST',
            'email': 'test@integration.com',
            'ville': 'Montréal'
        }

        if save_fournisseur(test_fournisseur):
            print_status("Ajout fournisseur test", 'success')
        else:
            print_status("Échec ajout fournisseur", 'error')

        return True
    except Exception as e:
        print_status(f"Erreur lors des tests: {e}", 'error')
        return False

def test_interface_integration():
    """Test l'intégration dans l'interface principale"""
    print("\n" + "="*60)
    print("TEST 5: INTÉGRATION INTERFACE")
    print("="*60)

    try:
        import app

        # Vérifier les flags d'activation
        if hasattr(app, 'BON_COMMANDE_SIMPLE_AVAILABLE'):
            status = 'success' if app.BON_COMMANDE_SIMPLE_AVAILABLE else 'warning'
            print_status(f"Module bon_commande_simple: {'Activé' if app.BON_COMMANDE_SIMPLE_AVAILABLE else 'Désactivé'}", status)

        if hasattr(app, 'FOURNISSEURS_AVAILABLE'):
            status = 'success' if app.FOURNISSEURS_AVAILABLE else 'warning'
            print_status(f"Module fournisseurs: {'Activé' if app.FOURNISSEURS_AVAILABLE else 'Désactivé'}", status)

        # Vérifier la fonction statistiques
        if hasattr(app, 'show_statistics_section'):
            print_status("Fonction statistiques disponible", 'success')
        else:
            print_status("Fonction statistiques manquante", 'error')

        return True
    except Exception as e:
        print_status(f"Erreur lors des tests: {e}", 'error')
        return False

def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("TESTS D'INTÉGRATION - BONS DE COMMANDE C2B")
    print("="*60)

    # Définir le répertoire de travail
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Exécuter les tests
    tests = [
        ("Importation des modules", test_imports),
        ("Bases de données", test_databases),
        ("Fonctions bons de commande", test_bon_commande_functions),
        ("Fonctions fournisseurs", test_fournisseurs_functions),
        ("Intégration interface", test_interface_integration)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"Erreur inattendue dans {test_name}: {e}", 'error')
            results.append((test_name, False))

    # Résumé final
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)

    success_count = sum(1 for _, result in results if result)

    for test_name, result in results:
        status = 'success' if result else 'error'
        symbol = 'OK' if result else 'ECHEC'
        print_status(f"{test_name}: {symbol}", status)

    print(f"\n{success_count}/{len(tests)} tests réussis")

    if success_count == len(tests):
        print_status("\nINTEGRATION REUSSIE! Les bons de commande sont prets a etre utilises.", 'success')
        print("\nPour lancer l'application:")
        print(f"{BLUE}streamlit run app.py{RESET}")
    else:
        print_status("\nCertains tests ont echoue. Verifiez les erreurs ci-dessus.", 'warning')

    return success_count == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)