"""
Script pour mettre à jour les informations de l'entreprise dans la base de données
Remplace Construction Héritage par Construction Excellence Plus
"""

import sqlite3
import json
import os

# Nouvelles informations de l'entreprise
NEW_CONFIG = {
    'nom': 'Construction Excellence Plus',
    'adresse': '2500 Boulevard Innovation',
    'ville': 'Montréal',
    'province': 'Québec',
    'code_postal': 'H3K 2A9',
    'telephone_bureau': '514-555-8900',
    'telephone_cellulaire': '514-555-8901',
    'email': 'info@constructionexcellence.ca',
    'site_web': 'www.constructionexcellence.ca',
    'rbq': '1234-5678-01',
    'neq': '1234567890',
    'tps': '123456789RT0001',
    'tvq': '1234567890TQ0001',
    'contact_principal_nom': '',
    'contact_principal_titre': '',
    'contact_principal_telephone': '',
    'contact_principal_email': '',
    'logo_path': '',
    'logo_base64': '',
    'couleur_primaire': '#374151',
    'couleur_secondaire': '#4b5563',
    'couleur_accent': '#3b82f6',
    'slogan': '',
    'conditions_paiement': '30% à la signature, 35% début des travaux, paiements progressifs selon avancement, 35% retenue finale',
    'garanties': '1 an main-d\'œuvre, 5 ans toiture, 10 ans structure, selon normes GCR',
    'delai_validite_soumission': '30',
    'taux_administration': 3.0,
    'taux_contingences': 12.0,
    'taux_profit': 15.0
}

def update_entreprise_config():
    """Met à jour la configuration de l'entreprise dans la base de données"""
    db_path = 'data/entreprise_config.db'
    
    # Vérifier si la base existe
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        print("Création de la base avec les nouvelles informations...")
        os.makedirs('data', exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Créer la table si elle n'existe pas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entreprise_config (
                id INTEGER PRIMARY KEY,
                config_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Vérifier si une configuration existe
        cursor.execute('SELECT id FROM entreprise_config')
        existing = cursor.fetchone()
        
        config_json = json.dumps(NEW_CONFIG, ensure_ascii=False)
        
        if existing:
            # Mettre à jour la configuration existante
            cursor.execute('''
                UPDATE entreprise_config 
                SET config_data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (config_json, existing[0]))
            print(f"✅ Configuration mise à jour (ID: {existing[0]})")
        else:
            # Insérer une nouvelle configuration
            cursor.execute('''
                INSERT INTO entreprise_config (config_data)
                VALUES (?)
            ''', (config_json,))
            print("✅ Nouvelle configuration insérée")
        
        conn.commit()
        conn.close()
        
        print("\n📊 Nouvelles informations de l'entreprise:")
        print(f"   Nom: {NEW_CONFIG['nom']}")
        print(f"   Adresse: {NEW_CONFIG['adresse']}")
        print(f"   Ville: {NEW_CONFIG['ville']}, {NEW_CONFIG['province']} {NEW_CONFIG['code_postal']}")
        print(f"   Téléphone: {NEW_CONFIG['telephone_bureau']}")
        print(f"   Email: {NEW_CONFIG['email']}")
        print(f"   RBQ: {NEW_CONFIG['rbq']}")
        print(f"   NEQ: {NEW_CONFIG['neq']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
        return False

def update_heritage_submissions():
    """Met à jour les soumissions Heritage existantes avec le nouveau nom"""
    db_path = 'data/soumissions_heritage.db'
    
    if not os.path.exists(db_path):
        print(f"ℹ️ Base Heritage non trouvée: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer toutes les soumissions
        cursor.execute('SELECT id, data FROM soumissions_heritage WHERE data IS NOT NULL')
        submissions = cursor.fetchall()
        
        updated_count = 0
        for sub_id, data_json in submissions:
            try:
                data = json.loads(data_json)
                
                # Mettre à jour les informations de l'entreprise dans les données
                if 'entreprise' in data:
                    data['entreprise'] = {
                        'nom': NEW_CONFIG['nom'],
                        'adresse': NEW_CONFIG['adresse'],
                        'ville': f"{NEW_CONFIG['ville']} ({NEW_CONFIG['province']}) {NEW_CONFIG['code_postal']}",
                        'telephone': NEW_CONFIG['telephone_bureau'],
                        'cellulaire': NEW_CONFIG['telephone_cellulaire'],
                        'email': NEW_CONFIG['email'],
                        'rbq': NEW_CONFIG['rbq'],
                        'neq': NEW_CONFIG['neq'],
                        'tps': NEW_CONFIG['tps'],
                        'tvq': NEW_CONFIG['tvq']
                    }
                    
                    # Sauvegarder les modifications
                    cursor.execute('''
                        UPDATE soumissions_heritage 
                        SET data = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (json.dumps(data, ensure_ascii=False), sub_id))
                    updated_count += 1
                    
            except json.JSONDecodeError:
                continue
        
        conn.commit()
        conn.close()
        
        if updated_count > 0:
            print(f"✅ {updated_count} soumissions Heritage mises à jour")
        
    except Exception as e:
        print(f"⚠️ Erreur mise à jour Heritage: {e}")

def main():
    """Fonction principale"""
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("MISE A JOUR DES INFORMATIONS DE L'ENTREPRISE")
    print("=" * 60)
    print()
    
    # Mise à jour de la configuration principale
    success = update_entreprise_config()
    
    if success:
        print("\nMise a jour des soumissions existantes...")
        update_heritage_submissions()
        
        print("\n" + "=" * 60)
        print("MISE A JOUR TERMINEE AVEC SUCCES")
        print("=" * 60)
        print("\nIMPORTANT: Redemarrez l'application pour voir les changements")
        print("   Utilisez: streamlit run app.py")
    else:
        print("\nLa mise a jour a echoue")

if __name__ == "__main__":
    main()