# Test simple pour vérifier que l'application fonctionne

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config_approbation import *
    print("Configuration importee avec succes")
    
    from inscription_system import *
    print("Systeme d'inscription importe avec succes")
    
    from pages_inscription import *
    print("Pages d'inscription importees avec succes")
    
    from admin_inscriptions import *
    print("Admin inscriptions importe avec succes")
    
    # Test de connexion base de données
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print("Base de donnees accessible")
    print(f"   Tables disponibles: {len(tables)}")
    
    # Vérifier tables critiques
    required_tables = ['entreprises_clientes', 'entreprises_prestataires', 'demandes_inscription']
    missing_tables = [table for table in required_tables if table not in tables]
    
    if missing_tables:
        print(f"Tables manquantes: {missing_tables}")
    else:
        print("Toutes les tables critiques presentes")
    
    # Test validation donnees
    test_data = {
        'email': 'test@example.com',
        'telephone': '514-555-1234',
        'mot_de_passe': 'test12345',
        'confirmation_mot_de_passe': 'test12345',
        'nom_entreprise': 'Test Corp',
        'nom_contact': 'John Doe'
    }
    
    erreurs = valider_donnees_inscription(test_data, 'client')
    if erreurs:
        print(f"Validation test: {erreurs}")
    else:
        print("Validation des donnees fonctionne")
    
    print("\nApplication prete a fonctionner!")
    
except Exception as e:
    print(f"Erreur lors du test: {str(e)}")
    import traceback
    traceback.print_exc()