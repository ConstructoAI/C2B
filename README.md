---
title: Construction Excellence Plus - Gestion de Soumissions
emoji: 🏗️
colorFrom: blue
colorTo: gray
sdk: streamlit
sdk_version: 1.29.0
app_file: app.py
pinned: false
license: mit
---

# 🏗️ Construction Excellence Plus - Système de Gestion de Soumissions

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://huggingface.co/spaces/YOUR_USERNAME/construction-excellence-plus)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Description

Application professionnelle de gestion de soumissions pour entreprises de construction, développée avec Streamlit. Cette solution complète permet de créer, gérer et suivre des soumissions détaillées avec un module Heritage intégré pour des estimations précises selon les standards de l'industrie québécoise.

### 🎯 Démonstration en ligne

Cette application est déployée sur Hugging Face Spaces. **Accès direct sans authentification** pour la démonstration.

## ✨ Fonctionnalités Principales

### 🏢 **Configuration d'Entreprise**
- Personnalisation complète des informations de l'entreprise
- Gestion du logo et des couleurs
- Configuration des taux (administration, profit, contingences)
- Paramètres fiscaux (TPS/TVQ)

### 📊 **Tableau de Bord**
- Vue d'ensemble des soumissions actives
- Statistiques en temps réel
- Filtres et recherche avancée
- Export des données

### ➕ **Module Heritage - Création de Soumissions**
- **140+ items prédéfinis** organisés en 8 catégories
- Calculs automatiques avec marges configurables
- Génération de documents HTML professionnels
- Système d'approbation client en ligne

### 📤 **Upload Multi-Format**
- Support complet : PDF, Word, Excel, Images
- Extraction automatique des informations
- Stockage sécurisé en base de données
- Aperçu intégré des documents

### 💾 **Sauvegardes**
- Backup automatique des données
- Export/Import de configurations
- Restauration simple

## 🛠️ Architecture Technique

### Stack Technologique
- **Frontend**: Streamlit 1.29.0
- **Backend**: Python 3.8+
- **Base de données**: SQLite
- **Déploiement**: Docker, Hugging Face Spaces

### Modules Principaux
```
├── app.py                    # Application principale (sans authentification)
├── soumission_heritage.py    # Module de soumissions détaillées
├── entreprise_config.py      # Configuration d'entreprise
├── categories_complete.py    # 140+ items de construction
├── backup_manager.py         # Gestion des sauvegardes
├── numero_manager.py         # Génération de numéros uniques
└── token_manager.py          # Protection des tokens
```

## 🚀 Installation et Déploiement

### Installation Locale

```bash
# Cloner le repository
git clone https://github.com/YOUR_USERNAME/construction-excellence-plus.git
cd construction-excellence-plus

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
```

### Déploiement sur Hugging Face Spaces

1. **Fork ce repository** sur GitHub
2. **Créer un nouveau Space** sur Hugging Face
3. **Sélectionner Streamlit** comme SDK
4. **Connecter votre repository** GitHub
5. L'application se déploiera automatiquement

### Variables d'Environnement (Optionnel)

```env
# Pour personnaliser (dans les Settings du Space)
DATA_DIR=/data
FILES_DIR=/files
```

## 📁 Structure des Données

### Bases de Données SQLite
- `entreprise_config.db` - Configuration de l'entreprise
- `soumissions_heritage.db` - Soumissions Heritage
- `soumissions_multi.db` - Documents uploadés

### Catégories de Construction

1. **0.0** - Travaux Préparatoires et Démolition
2. **1.0** - Fondation, Infrastructure et Services  
3. **2.0** - Structure et Charpente
4. **3.0** - Enveloppe Extérieure
5. **4.0** - Systèmes Mécaniques et Électriques
6. **5.0** - Isolation et Étanchéité
7. **6.0** - Finitions Intérieures
8. **7.0** - Aménagement Extérieur et Garage

## 🔒 Sécurité

- ✅ Pas d'authentification requise (version démo)
- ✅ Tokens UUID pour liens sécurisés
- ✅ Données stockées localement
- ✅ Backup automatique des configurations

## 📊 Formats Supportés

### Documents
- PDF, Word (.doc, .docx)
- Excel (.xls, .xlsx)
- PowerPoint (.ppt, .pptx)

### Images
- JPG, PNG, GIF, SVG

### Web
- HTML, HTM

## 🎨 Personnalisation

L'application utilise les informations de **Construction Excellence Plus** (entreprise fictive de démonstration). Pour personnaliser :

1. Accéder à l'onglet **🏢 ENTREPRISE**
2. Modifier les informations selon vos besoins
3. Sauvegarder la configuration
4. Les changements s'appliquent immédiatement

## 💡 Cas d'Usage

- **Entrepreneurs en construction** : Création rapide de soumissions professionnelles
- **Gestionnaires de projets** : Suivi centralisé des propositions
- **Équipes commerciales** : Gestion des approbations clients
- **Administration** : Tableaux de bord et rapports

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à :
- 🐛 Reporter des bugs
- 💡 Suggérer des améliorations
- 🔧 Proposer des pull requests

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- Développé pour l'industrie de la construction québécoise
- Basé sur les standards RBQ et normes GCR
- Interface optimisée pour une utilisation professionnelle

## 📧 Contact

Pour questions ou support :
- 🌐 [Hugging Face Space](https://huggingface.co/spaces/YOUR_USERNAME/construction-excellence-plus)
- 📧 Email : info@constructionexcellence.ca (fictif)
- 🏢 Construction Excellence Plus (Entreprise de démonstration)

---

**Note**: Cette application est fournie à titre de démonstration avec des données d'entreprise fictives. Adaptez selon vos besoins réels.

[![Déployé sur Hugging Face Spaces](https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-on-spaces-lg.svg)](https://huggingface.co/spaces)