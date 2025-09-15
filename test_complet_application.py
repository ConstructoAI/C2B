#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests complets de l'application C2B avec bons de commande
"""

import os
import sys
import sqlite3
import json
import time
from datetime import datetime
import traceback

# Configuration de l'environnement
os.environ['DATA_DIR'] = os.path.join(os.getcwd(), 'data')
os.environ['FILES_DIR'] = os.path.join(os.getcwd(), 'files')

def print_test_header(title):
    """Affiche un en-tête de test"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_result(test_name, success, details=""):
    """Affiche le résultat d'un test"""
    status = "[SUCCES]" if success else "[ECHEC]"
    color = "\033[92m" if success else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status:10}{reset} {test_name}")
    if details:
        print(f"           -> {details}")

class TestsApplication:
    def __init__(self):
        self.results = []
        self.data_dir = os.getenv('DATA_DIR', 'data')

    def test_import_modules(self):
        """Test 1: Importation de tous les modules"""
        print_test_header("TEST 1: IMPORTATION DES MODULES")

        modules = {
            'app': 'Application principale',
            'bon_commande_simple': 'Module bons de commande',
            'fournisseurs_manager': 'Module fournisseurs',
            'entreprise_config': 'Configuration entreprise',
            'soumission_heritage': 'Soumissions Heritage',
            'backup_manager': 'Gestionnaire de sauvegardes',
            'numero_manager': 'Gestionnaire de numéros',
            'token_manager': 'Gestionnaire de tokens'
        }

        all_success = True
        for module_name, description in modules.items():
            try:
                __import__(module_name)
                print_result(description, True, f"Module {module_name} importé")
            except ImportError as e:
                print_result(description, False, str(e))
                all_success = False

        self.results.append(('Import modules', all_success))
        return all_success

    def test_database_creation(self):
        """Test 2: Création et accès aux bases de données"""
        print_test_header("TEST 2: BASES DE DONNEES")

        databases = {
            'entreprise_config.db': ('entreprise_config', 'Configuration entreprise'),
            'soumissions_heritage.db': ('soumissions_heritage', 'Soumissions Heritage'),
            'soumissions_multi.db': ('soumissions', 'Documents uploadés'),
            'bons_commande_simple.db': ('bons_commande', 'Bons de commande'),
            'fournisseurs.db': ('fournisseurs', 'Fournisseurs')
        }

        all_success = True
        for db_file, (table_name, description) in databases.items():
            db_path = os.path.join(self.data_dir, db_file)

            try:
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()

                    # Vérifier que la table principale existe
                    cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                    table_exists = cursor.fetchone()[0] > 0

                    if table_exists:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        print_result(description, True, f"{count} enregistrement(s)")
                    else:
                        print_result(description, False, f"Table {table_name} non trouvée")
                        all_success = False

                    conn.close()
                else:
                    print_result(description, False, "Base de données non créée")
                    # Essayer de créer la base
                    if 'fournisseurs' in db_file:
                        from fournisseurs_manager import init_fournisseurs_db
                        init_fournisseurs_db()
                        print_result(f"  -> Création {description}", True)
                    elif 'bons_commande_simple' in db_file:
                        from bon_commande_simple import init_bon_commande_db
                        init_bon_commande_db()
                        print_result(f"  -> Création {description}", True)

            except Exception as e:
                print_result(description, False, str(e))
                all_success = False

        self.results.append(('Bases de données', all_success))
        return all_success

    def test_bon_commande_functions(self):
        """Test 3: Fonctionnalités des bons de commande"""
        print_test_header("TEST 3: FONCTIONNALITES BONS DE COMMANDE")

        try:
            from bon_commande_simple import (
                init_bon_commande_db,
                generate_numero_bon,
                save_bon_commande,
                generate_html,
                get_company_info
            )

            all_success = True

            # Test 1: Initialisation
            try:
                init_bon_commande_db()
                print_result("Initialisation base de données", True)
            except Exception as e:
                print_result("Initialisation base de données", False, str(e))
                all_success = False

            # Test 2: Génération de numéro
            try:
                numero = generate_numero_bon()
                is_valid = numero and numero.startswith('BC-')
                print_result("Génération numéro", is_valid, numero)
                if not is_valid:
                    all_success = False
            except Exception as e:
                print_result("Génération numéro", False, str(e))
                all_success = False

            # Test 3: Information entreprise
            try:
                company = get_company_info()
                has_info = company and 'name' in company
                print_result("Récupération info entreprise", has_info,
                           company.get('name', 'Non disponible'))
                if not has_info:
                    all_success = False
            except Exception as e:
                print_result("Récupération info entreprise", False, str(e))
                all_success = False

            # Test 4: Création d'un bon de commande test
            try:
                test_data = {
                    'numero': generate_numero_bon(),
                    'fournisseur': {
                        'nom': 'Fournisseur Test',
                        'contact': 'Contact Test',
                        'telephone': '514-555-0000',
                        'email': 'test@test.com'
                    },
                    'client': {
                        'nom': 'Client Test'
                    },
                    'projet': {
                        'nom': 'Projet Test'
                    },
                    'items': [
                        {
                            'description': 'Article test 1',
                            'details': 'Détails test',
                            'quantite': 2,
                            'unite': 'unité',
                            'prix_unitaire': 100.00,
                            'total': 200.00
                        }
                    ],
                    'totaux': {
                        'sous_total': 200.00,
                        'tps': 10.00,
                        'tvq': 19.95,
                        'total': 229.95
                    }
                }

                bon_id, token, lien, filename = save_bon_commande(test_data)
                print_result("Sauvegarde bon de commande", True,
                           f"ID: {bon_id}, Token: {token[:8]}...")

                # Test génération HTML
                html = generate_html(test_data)
                has_html = html and len(html) > 100
                print_result("Génération HTML", has_html,
                           f"{len(html)} caractères générés")
                if not has_html:
                    all_success = False

            except Exception as e:
                print_result("Création bon de commande test", False, str(e))
                all_success = False

            self.results.append(('Bons de commande', all_success))
            return all_success

        except ImportError as e:
            print_result("Import module bon_commande_simple", False, str(e))
            self.results.append(('Bons de commande', False))
            return False

    def test_fournisseurs_functions(self):
        """Test 4: Fonctionnalités des fournisseurs"""
        print_test_header("TEST 4: FONCTIONNALITES FOURNISSEURS")

        try:
            from fournisseurs_manager import (
                init_fournisseurs_db,
                get_fournisseurs_list,
                get_fournisseur_by_nom,
                save_fournisseur,
                delete_fournisseur
            )

            all_success = True

            # Test 1: Initialisation
            try:
                init_fournisseurs_db()
                print_result("Initialisation base fournisseurs", True)
            except Exception as e:
                print_result("Initialisation base fournisseurs", False, str(e))
                all_success = False

            # Test 2: Liste des fournisseurs
            try:
                fournisseurs = get_fournisseurs_list()
                print_result("Liste fournisseurs", True,
                           f"{len(fournisseurs)} fournisseur(s)")
            except Exception as e:
                print_result("Liste fournisseurs", False, str(e))
                all_success = False

            # Test 3: Ajout d'un fournisseur test
            try:
                test_fournisseur = {
                    'nom': f'Test Fournisseur {datetime.now().strftime("%H%M%S")}',
                    'type': 'Fournisseur',
                    'contact_principal': 'Test Contact',
                    'telephone': '514-555-TEST',
                    'email': 'test@fournisseur.com',
                    'ville': 'Montréal',
                    'specialites': 'Test, Démonstration'
                }

                success = save_fournisseur(test_fournisseur)
                print_result("Ajout fournisseur", success, test_fournisseur['nom'])
                if not success:
                    all_success = False

                # Test récupération
                fournisseur = get_fournisseur_by_nom(test_fournisseur['nom'])
                found = fournisseur is not None
                print_result("Récupération fournisseur", found)
                if not found:
                    all_success = False

            except Exception as e:
                print_result("Gestion fournisseur test", False, str(e))
                all_success = False

            self.results.append(('Fournisseurs', all_success))
            return all_success

        except ImportError as e:
            print_result("Import module fournisseurs_manager", False, str(e))
            self.results.append(('Fournisseurs', False))
            return False

    def test_statistics_function(self):
        """Test 5: Fonction statistiques"""
        print_test_header("TEST 5: STATISTIQUES GLOBALES")

        try:
            import app

            # Vérifier que la fonction existe
            has_function = hasattr(app, 'show_statistics_section')
            print_result("Fonction show_statistics_section", has_function)

            if has_function:
                # Tester la collecte de statistiques
                try:
                    # Compter les enregistrements dans chaque base
                    stats = {}

                    # Soumissions Heritage
                    db_path = os.path.join(self.data_dir, 'soumissions_heritage.db')
                    if os.path.exists(db_path):
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM soumissions_heritage")
                        stats['heritage'] = cursor.fetchone()[0]
                        conn.close()
                    else:
                        stats['heritage'] = 0

                    # Bons de commande
                    db_path = os.path.join(self.data_dir, 'bons_commande_simple.db')
                    if os.path.exists(db_path):
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM bons_commande")
                        stats['bons'] = cursor.fetchone()[0]
                        conn.close()
                    else:
                        stats['bons'] = 0

                    # Fournisseurs
                    db_path = os.path.join(self.data_dir, 'fournisseurs.db')
                    if os.path.exists(db_path):
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM fournisseurs WHERE actif = 1")
                        stats['fournisseurs'] = cursor.fetchone()[0]
                        conn.close()
                    else:
                        stats['fournisseurs'] = 0

                    print_result("Collecte statistiques", True,
                               f"Heritage: {stats['heritage']}, Bons: {stats['bons']}, Fournisseurs: {stats['fournisseurs']}")

                    self.results.append(('Statistiques', True))
                    return True

                except Exception as e:
                    print_result("Collecte statistiques", False, str(e))
                    self.results.append(('Statistiques', False))
                    return False
            else:
                self.results.append(('Statistiques', False))
                return False

        except ImportError as e:
            print_result("Import module app", False, str(e))
            self.results.append(('Statistiques', False))
            return False

    def test_interface_integration(self):
        """Test 6: Intégration dans l'interface"""
        print_test_header("TEST 6: INTEGRATION INTERFACE")

        try:
            import app

            all_success = True

            # Test des flags d'activation
            tests = [
                ('BON_COMMANDE_AVAILABLE', 'Bons de commande activés'),
                ('BON_COMMANDE_SIMPLE_AVAILABLE', 'Module bon_commande_simple'),
                ('FOURNISSEURS_AVAILABLE', 'Module fournisseurs')
            ]

            for flag_name, description in tests:
                if hasattr(app, flag_name):
                    is_active = getattr(app, flag_name)
                    print_result(description, is_active,
                               "Activé" if is_active else "Désactivé")
                    if not is_active:
                        all_success = False
                else:
                    print_result(description, False, "Flag non trouvé")
                    all_success = False

            # Test des fonctions d'interface
            functions = [
                ('show_statistics_section', 'Section statistiques'),
                ('show_dashboard_content', 'Tableau de bord'),
                ('show_upload_section', 'Section upload')
            ]

            for func_name, description in functions:
                has_func = hasattr(app, func_name)
                print_result(description, has_func)
                if not has_func:
                    all_success = False

            self.results.append(('Interface', all_success))
            return all_success

        except Exception as e:
            print_result("Test interface", False, str(e))
            self.results.append(('Interface', False))
            return False

    def run_all_tests(self):
        """Exécute tous les tests"""
        print("\n" + "="*70)
        print("  TESTS COMPLETS - APPLICATION C2B AVEC BONS DE COMMANDE")
        print("="*70)

        # Exécuter tous les tests
        self.test_import_modules()
        self.test_database_creation()
        self.test_bon_commande_functions()
        self.test_fournisseurs_functions()
        self.test_statistics_function()
        self.test_interface_integration()

        # Résumé
        print_test_header("RESUME DES TESTS")

        success_count = sum(1 for _, result in self.results if result)
        total_count = len(self.results)

        for test_name, success in self.results:
            print_result(test_name, success)

        print(f"\n{success_count}/{total_count} catégories de tests réussies")

        if success_count == total_count:
            print("\n" + "="*70)
            print("  SUCCES TOTAL ! L'application est prête à être utilisée.")
            print("  Lancez: streamlit run app.py")
            print("="*70)
        else:
            print("\n" + "="*70)
            print("  ATTENTION: Certains tests ont échoué.")
            print("  Vérifiez les erreurs ci-dessus.")
            print("="*70)

        return success_count == total_count

def main():
    """Fonction principale"""
    # Changer vers le répertoire de l'application
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Créer les répertoires nécessaires
    os.makedirs('data', exist_ok=True)
    os.makedirs('files', exist_ok=True)
    os.makedirs('data/backups', exist_ok=True)

    # Exécuter les tests
    tester = TestsApplication()
    success = tester.run_all_tests()

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())