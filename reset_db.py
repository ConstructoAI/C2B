#!/usr/bin/env python3
"""
Script utilitaire pour réinitialiser la base de données
Usage: python reset_db.py
"""

import os
import shutil
from config_approbation import *
from init_db_approbation import init_database_approbation

# Configuration du stockage
DATA_DIR = os.getenv('DATA_DIR', os.path.join(os.getcwd(), 'data'))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, DATABASE_FILE)

def reset_database():
    """Supprime et recrée complètement la base de données"""
    
    print("REINITIALISATION DE LA BASE DE DONNEES")
    print("=" * 50)
    
    # Supprimer l'ancienne base de données
    if os.path.exists(DATABASE_PATH):
        try:
            os.remove(DATABASE_PATH)
            print(f"Ancienne base supprimee: {DATABASE_PATH}")
        except OSError as e:
            print(f"Erreur lors de la suppression: {e}")
            return False
    
    # Supprimer les anciens backups (optionnel)
    backup_files = [f for f in os.listdir(DATA_DIR) if f.startswith(BACKUP_PREFIX)]
    if backup_files:
        print(f"\nNettoyage de {len(backup_files)} fichiers de backup...")
        for backup_file in backup_files:
            try:
                os.remove(os.path.join(DATA_DIR, backup_file))
                print(f"   Supprime: {backup_file}")
            except OSError as e:
                print(f"   Erreur: {backup_file} - {e}")
    
    # Recréer la base de données
    print("\nCreation d'une nouvelle base de donnees...")
    try:
        init_database_approbation()
        print("\nBase de donnees reinitialisee avec succes!")
        return True
    except Exception as e:
        print(f"\nErreur lors de la creation: {e}")
        return False

def backup_current_database():
    """Crée un backup manuel de la base actuelle"""
    if not os.path.exists(DATABASE_PATH):
        print("Aucune base de donnees a sauvegarder")
        return False
    
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = os.path.join(DATA_DIR, f"manual_backup_{timestamp}.db")
    
    try:
        shutil.copy2(DATABASE_PATH, backup_name)
        print(f"Backup cree: {backup_name}")
        return True
    except Exception as e:
        print(f"Erreur backup: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    print("SoumissionsEntreprises - Utilitaire de Base de Donnees")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--backup-only":
        # Mode backup seulement
        backup_current_database()
    else:
        # Mode reset complet
        response = input("\nVoulez-vous vraiment reinitialiser la base de donnees? (y/N): ")
        if response.lower() in ['y', 'yes', 'oui', 'o']:
            
            # Proposer un backup avant reset
            backup_response = input("Creer un backup avant reinitialisation? (Y/n): ")
            if backup_response.lower() not in ['n', 'no', 'non']:
                backup_current_database()
            
            # Procéder au reset
            if reset_database():
                print("\nVous pouvez maintenant relancer l'application!")
                print("   Commande: python -m streamlit run app.py")
            else:
                print("\nEchec de la reinitialisation")
                sys.exit(1)
        else:
            print("Reinitialisation annulee")