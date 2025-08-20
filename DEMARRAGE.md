# 🚀 Démarrage Rapide - PORTAIL C2B DE L'ENTREPRISE

## 📋 Installation pour une nouvelle entreprise

### Option 1: Configuration automatique (recommandée)
```bash
# Double-cliquez sur le fichier
config_nouvelle_entreprise.bat
```

### Option 2: Configuration manuelle
1. **Modifier la configuration**
   ```bash
   # Editez le fichier de configuration
   notepad config_entreprise_unique.py
   ```

2. **Informations à personnaliser**
   - `nom_entreprise`: Nom de votre entreprise
   - `numero_rbq`: Votre numéro RBQ (si applicable)
   - `nom_contact` et `email`: Contact principal de connexion
   - `telephone`, `adresse`: Coordonnées
   - `mot_de_passe`: **IMPORTANT** - Changez "entreprise123"
   - `domaines_expertise`: Vos spécialités
   - `description_entreprise`: Description complète

3. **Lancer le portail**
   ```bash
   # Double-cliquez sur le fichier
   run.bat
   ```

## 🔐 Comptes par défaut

### Entreprise (Propriétaire du portail)
- **Email**: alex@constructionexcellence.ca
- **Mot de passe**: entreprise123
- **Rôle**: Reçoit toutes les demandes et crée les soumissions

### Clients de démonstration  
- **Emails**: marie.dubois@technosolutions.ca, jean.tremblay@commerceplus.ca, sophie.lavoie@financeconseil.ca
- **Mot de passe**: demo123
- **Rôle**: Peuvent créer des demandes de soumissions

### Administrateur
- **Mot de passe**: admin123
- **Rôle**: Gestion générale du système

## 🌐 Accès au portail

Une fois lancé, le portail est accessible sur:
**http://localhost:8501**

## 📊 Workflow C2B (Client à Entreprise)

### Pour l'entreprise propriétaire:
1. Se connecter avec les identifiants entreprise
2. Voir les demandes reçues des clients
3. Créer et envoyer des soumissions
4. Recevoir les notifications d'acceptation avec numéro de référence

### Pour les clients:
1. Se connecter ou créer un compte client
2. Créer une demande de soumission détaillée
3. Recevoir et évaluer les soumissions
4. Accepter/refuser les propositions

## 🔧 Scripts utilitaires

- `run.bat`: Démarrage complet du portail
- `config_nouvelle_entreprise.bat`: Assistant de configuration
- `reset_db.py`: Réinitialisation de la base de données
- `verify_tables.py`: Vérification de l'intégrité

## ⚠️ Sécurité

**IMPORTANT**: Avant la mise en production:
1. Changez le mot de passe par défaut dans `config_entreprise_unique.py`
2. Modifiez les mots de passe des comptes de démonstration
3. Configurez HTTPS pour le déploiement web

## 🆘 Dépannage

### Erreur "Table not found"
```bash
py init_db_approbation.py
```

### Erreur de dépendances
```bash
py -m pip install -r requirements.txt
```

### Port déjà utilisé
```bash
# Tuez les processus Streamlit ou changez le port
py -m streamlit run app.py --server.port 8502
```

## 📞 Support

Pour toute question technique, vérifiez les logs dans la console ou contactez le développeur avec les détails de l'erreur.