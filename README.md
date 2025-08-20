# 🏗️ PORTAIL C2B DE L'ENTREPRISE

Un portail web Client à Entreprise (C2B) permettant à une entreprise de construction de recevoir et gérer les demandes de soumissions de ses clients, développé avec Streamlit.

## 📋 Description

Ce portail de soumissions est une solution **mono-entreprise** conçue pour les entrepreneurs en construction qui souhaitent offrir à leurs clients un portail web professionnel pour demander des soumissions. Contrairement aux marketplaces multi-prestataires, ce système est dédié à **UNE SEULE entreprise propriétaire** qui reçoit toutes les demandes et gère ses soumissions de manière centralisée.

**Modèle d'affaires :** Créez des portails individuels dédiés pour chaque entreprise de construction (entrepreneurs généraux, prestataires spécialisés, etc.)

## ✨ Fonctionnalités principales

### 👥 Interface Clients (C2B)
- **Demandes de soumissions personnalisées** avec description détaillée du projet
- **Soumission de documents** et spécifications techniques
- **Suivi en temps réel** du statut de leur demande
- **Évaluation et acceptation** des soumissions reçues
- **Historique complet** de leurs projets
- **Communication directe** avec l'entreprise

### 🏗️ Dashboard Entreprise Propriétaire
- **Réception automatique** de toutes les demandes clients
- **Création et envoi** de soumissions personnalisées
- **Notifications d'acceptation** avec numéro de référence
- **Suivi de tous les projets** et leur statut
- **Gestion des contrats** et planning des travaux
- **Statistiques et métriques** de performance

### ⚙️ Configuration Entreprise
- **Profil entreprise personnalisable** (nom, RBQ, certifications)
- **Domaines d'expertise** et zones de service
- **Tarification** et disponibilité
- **Informations de contact** et coordonnées
- **Authentification sécurisée** pour l'entreprise propriétaire

## 🔄 Workflow C2B Simplifié

### Processus direct Client → Entreprise (C2B)
1. 📝 **Demande client** : Le client soumet sa demande de soumission via le portail
2. 📥 **Réception automatique** : L'entreprise propriétaire reçoit instantanément la demande
3. 📋 **Création soumission** : L'entreprise prépare et envoie sa soumission personnalisée  
4. 👀 **Évaluation client** : Le client examine la soumission reçue
5. ✅ **Acceptation/Refus** : Le client accepte ou refuse la proposition
6. 🔔 **Notification** : L'entreprise reçoit la notification avec le numéro de référence
7. 📞 **Suivi projet** : Contact direct pour finalisation et début des travaux

### Statuts de suivi
- 📝 **Brouillon** : Demande en cours de rédaction par le client
- 📤 **Soumise** : Demande envoyée à l'entreprise
- 📋 **Soumission créée** : L'entreprise a préparé sa proposition
- 👀 **En évaluation** : Le client examine la soumission
- ✅ **Acceptée** : Soumission approuvée par le client
- ❌ **Refusée** : Soumission rejetée par le client
- 🚧 **En cours** : Travaux commencés
- 🏁 **Terminée** : Projet complété

## 🚀 Installation et démarrage

### Prérequis
- Python 3.8 ou plus récent
- pip (gestionnaire de paquets Python)

### ⚡ Installation nouvelle entreprise (recommandée)
1. **Télécharger et extraire le projet**
```bash
# Extraire dans le dossier de votre choix
cd PortailSoumissions
```

2. **Configurer pour votre entreprise**
```bash
# Windows - Assistant automatique
config_nouvelle_entreprise.bat
```

3. **Lancer le portail**
```bash
# Windows  
run.bat
```

### Installation manuelle
1. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

2. **Initialiser la base de données**
```bash
python init_db_approbation.py
```

3. **Lancer l'application**
```bash
streamlit run app.py
```

4. **Accéder à l'application**
- URL : `http://localhost:8501`

## 🔐 Comptes de démonstration

### 🏗️ Entreprise Propriétaire (Configuration C2B par défaut)
- **Email**: alex@constructionexcellence.ca
- **Mot de passe**: `entreprise123` ⚠️ **À changer en production**
- **Entreprise**: Construction Excellence Québec Inc.
- **RBQ**: 5678-1234-01

### 👥 Clients de Démonstration (mot de passe: `demo123`)
- **marie.dubois@technosolutions.ca** - TechnoSolutions Inc.
- **jean.tremblay@commerceplus.ca** - Commerce Plus Ltée  
- **sophie.lavoie@financeconseil.ca** - FinanceConseil Pro

### ⚙️ Administrateur
- **Mot de passe** : `admin123`

> **Note**: Ces comptes sont pour la démonstration. En production, modifiez tous les mots de passe dans `config_entreprise_unique.py`

## ⚙️ Configuration Personnalisée

### 🎨 Personnalisation pour votre entreprise

Chaque installation est **entièrement personnalisable** dans `config_entreprise_unique.py` :

```python
ENTREPRISE_PROPRIETAIRE = {
    "nom_entreprise": "Votre Entreprise Construction Inc.",
    "numero_rbq": "XXXX-XXXX-XX",  # Votre numéro RBQ
    "nom_contact": "Votre Nom",
    "email": "votre.email@entreprise.ca",
    "telephone": "514-XXX-XXXX",
    "domaines_expertise": ["Vos spécialités"],
    "description_entreprise": "Description de votre entreprise...",
    "mot_de_passe": "VotreMotDePasse123", # À personnaliser !
}
```

### 🏗️ Adaptable à tous secteurs construction
- **Entrepreneurs généraux** (construction complète)
- **Spécialistes RBQ** (électricité, plomberie, etc.)
- **Rénovation** (cuisine, salle de bain, sous-sol)
- **Construction commerciale** (bureaux, magasins)
- **Services spécialisés** (toiture, isolation, etc.)

## 📊 Données de démonstration

L'application inclut des données réalistes :
- ✅ **3 clients entreprises** avec comptes de test 
- ✅ **1 entreprise construction** (Configuration Excellence Québec Inc.)
- ✅ **3 demandes projets construction** (salle bain, cuisine, sous-sol)
- ✅ **2 soumissions détaillées** avec prix et délais
- ✅ **Workflow acceptation/refus** fonctionnel
- ✅ **Notifications avec numéros référence** (SE-XXXXXXX)

## 🛠️ Architecture technique

### Stack technologique
- **Frontend/Backend** : Streamlit 1.28+
- **Base de données** : SQLite avec stockage persistant optimisé
- **Gestion des fichiers** : Encodage Base64 avec support multi-formats
- **Sécurité** : Hashage SHA-256 et gestion des sessions
- **Workflow** : Système d'états avancé avec notifications
- **Déploiement** : Compatible Render, Heroku, et cloud platforms

### Tables du système C2B
- **entreprises_clientes** : Profils des clients qui demandent des devis
- **entreprises_prestataires** : Profils des entreprises qui soumissionnent
- **demandes_devis** : Demandes avec cahier des charges et critères
- **soumissions** : Propositions avec workflow d'approbation
- **processus_approbation** : Gestion des étapes de validation
- **evaluations** : Système de notation multi-critères
- **contrats** : Gestion complète des contrats signés
- **messages** : Communication entre entreprises
- **notifications** : Alertes et notifications en temps réel
- **logs_audit** : Traçabilité complète des actions

## 🌐 Déploiement sur Render

### Configuration recommandée
- **Instance** : Standard (2 GB RAM, 1 CPU) - 25$/mois
- **Stockage persistant** : 20 GB configuré pour documents B2B
- **Variables d'environnement** :
  - `DATA_DIR` : `/opt/render/project/data`
  - `ADMIN_PASSWORD` : Mot de passe admin sécurisé

### Étapes de déploiement
1. **Connecter le repository** GitHub à Render
2. **Configurer les variables** d'environnement
3. **Ajouter le disque persistant** (20 GB recommandé)
4. **Déployer** automatiquement avec build command : `pip install -r requirements.txt`
5. **Start command** : `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## 🔧 Configuration avancée

### Stockage persistant
- **Local** : Utilise le répertoire `./data/`
- **Production** : Utilise `DATA_DIR` variable d'environnement
- **Backup automatique** : Lors des migrations de base de données

### Personnalisation
- **Workflow d'approbation** : Configurable dans `config_approbation.py`
- **Critères d'évaluation** : Personnalisables par demande
- **Types de projets** : Extensibles selon les besoins B2B
- **Notifications** : Templates modifiables par type d'événement

### Sécurité B2B
- **Authentification** : Séparée par type d'entreprise
- **Autorisations** : Contrôle d'accès granulaire
- **Audit trail** : Logging complet de toutes les actions
- **Données sensibles** : Chiffrement des documents confidentiels

## 📈 Fonctionnalités avancées C2B

### Intelligence artificielle
- **Scoring automatique** des soumissions selon les critères
- **Recommandations** de prestataires pertinents
- **Détection d'anomalies** dans les propositions
- **Analytics prédictives** pour les délais et budgets

### Workflow intelligent
- **Étapes personnalisables** selon le type de projet
- **Notifications automatiques** à chaque changement de statut
- **Escalade automatique** en cas de dépassement de délais
- **Intégration calendrier** pour les deadlines importantes

### Reporting et analytics
- **Dashboards entreprises** : Performance et statistiques
- **Métriques prestataires** : Taux de réussite et évaluations
- **Analytics administrateur** : Vue globale du système
- **Rapports exportables** : PDF, Excel, CSV

## 🚨 Nouveautés Version 1.0

### ✅ Fonctionnalités principales
- 🏢 **Architecture C2B complète** avec rôles séparés
- 🔄 **Workflow d'approbation** en 5 étapes personnalisables
- ⭐ **Système d'évaluation** multi-critères avancé
- 🔔 **Notifications intelligentes** avec priorités
- 📊 **Dashboards spécialisés** pour chaque type d'utilisateur
- 🔍 **Filtres et recherche** avancés pour les opportunités
- 📎 **Gestion de documents** C2B avec support multi-formats
- 🎯 **Matching intelligent** entreprises-opportunités

## 🐛 Dépannage

### Problèmes courants

**L'application ne démarre pas**
```bash
# Vérifier Python
py --version

# Installer les dépendances
py -m pip install -r requirements.txt

# Utiliser le script de démarrage
run.bat
```

**Erreur de base de données**
```bash
# Réinitialiser la base
py init_db_approbation.py
```

**Port déjà utilisé**
```bash
# Utiliser un autre port
py -m streamlit run app.py --server.port 8502
```

### Messages d'erreur fréquents
- **"Table not found"** → Exécuter `py init_db_approbation.py`
- **"Import error"** → Vérifier l'installation des dépendances
- **"Permission denied"** → Vérifier les droits d'écriture dans le répertoire

## 🎯 Roadmap

### Version 1.1 (développement en cours)
- [ ] **API REST** pour intégrations tierces
- [ ] **Webhooks** pour notifications externes
- [ ] **Intégration signatures électroniques** 
- [ ] **Export avancé** des rapports

### Version 1.2 (futur)
- [ ] **Application mobile** (React Native)
- [ ] **Intelligence artificielle** pour matching automatique
- [ ] **Intégration ERP** (SAP, Oracle)
- [ ] **Multi-langues** (français/anglais/espagnol)

### Version 2.0 (vision)
- [ ] **Blockchain** pour la certification des contrats
- [ ] **IoT integration** pour suivi de projets
- [ ] **IA prédictive** pour estimation des délais et coûts
- [ ] **Marketplace** intégré avec paiements

## 📞 Support et documentation

### Démarrage rapide
- **README.md** : Ce fichier  
- **DEMARRAGE.md** : Guide d'installation détaillé
- **Configuration** : `config_entreprise_unique.py`
- **Base de données** : `init_db_approbation.py`

### Scripts utiles
- **`run.bat`** : Démarrage automatique Windows optimisé
- **`config_nouvelle_entreprise.bat`** : Assistant configuration entreprise
- **`init_db_approbation.py`** : Initialisation mono-entreprise
- **`app.py`** : Application Streamlit principale

## 🤝 Contribution

1. Fork le projet SoumissionsEntreprises
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements avec des messages clairs
4. Tester localement avec `py -m streamlit run app.py`
5. Ouvrir une Pull Request détaillée

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 🏆 **PORTAIL C2B DE L'ENTREPRISE v2.0**

**Solution Client à Entreprise pour entrepreneurs en construction - Créez des portails dédiés pour vos clients**

### Statistiques du projet
- **7,200+ lignes de code** Python optimisé construction
- **Architecture mono-entreprise** personnalisable
- **Configuration en 3 clics** via assistant Windows
- **100% fonctionnel** avec workflow client → entreprise → notification
- **Production-ready** pour Render, Heroku ou serveur privé

### 🎯 **Votre modèle d'affaires**
Développez et déployez des portails individuels pour chaque entreprise de construction :
- **Portail A** : Construction ABC Inc. (ses clients → ses soumissions)  
- **Portail B** : Électricien XYZ Ltée (ses clients → ses soumissions)
- **Portail C** : Rénovations 123 (ses clients → ses soumissions)

### Technologies utilisées
- ⚡ **Streamlit** - Interface web moderne et responsive
- 💾 **SQLite** - Base de données robuste et performante  
- 🔐 **SHA-256** - Sécurité des mots de passe entreprise
- 📱 **Responsive design** - Compatible tous appareils
- 🎨 **CSS personnalisé** - Design corporate professionnel
- 🔔 **Notifications temps réel** - Communication instantanée
- 🔄 **Workflow intelligent** - Processus d'approbation automatisé
- 📊 **Analytics avancées** - Business Intelligence intégrée