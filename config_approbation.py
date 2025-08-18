# Configuration - Système de Soumissions Construction P2B Québec

# Version du système
VERSION = "2.0.0"
NOM_SYSTEME = "ConstructionP2BQuébec"
DESCRIPTION = "Plateforme de Soumissions Construction pour Particuliers au Québec"

# Configuration de la base de données
DATABASE_FILE = "soumissions_entreprises.db"
BACKUP_PREFIX = "soumissions_backup"

# Codes de référence
REFERENCE_PREFIX = "SE"

# Configuration Streamlit
STREAMLIT_CONFIG = {
    "page_title": "Construction Québec P2B - Plateforme pour Particuliers",
    "page_icon": "🏠",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Types de projets construction résidentielle P2B
TYPES_PROJETS = [
    "Rénovation salle de bain",
    "Rénovation cuisine",
    "Agrandissement maison",
    "Rénovation sous-sol",
    "Toiture résidentielle",
    "Revêtement extérieur",
    "Isolation et étanchéité",
    "Plomberie résidentielle", 
    "Électricité résidentielle",
    "Chauffage et climatisation",
    "Fenêtres et portes",
    "Planchers et carrelage",
    "Peinture intérieure/extérieure",
    "Aménagement paysager",
    "Terrasse et patio",
    "Clôture et portail",
    "Garage et cabanon",
    "Piscine et spa",
    "Déneigement et entretien",
    "Autre projet résidentiel"
]

# Secteurs d'activité des entreprises clientes - Construction Québec
SECTEURS_ACTIVITE = [
    "Développement immobilier résidentiel",
    "Développement immobilier commercial",
    "Développement immobilier industriel",
    "Copropriétés et condos",
    "Logement social et coopératif",
    "Centres commerciaux et retail",
    "Bureaux et tours à bureaux",
    "Hôtels et hébergement",
    "Établissements de santé",
    "Établissements d'enseignement",
    "Infrastructures municipales",
    "Infrastructures de transport",
    "Installations sportives et récréatives",
    "Centres de distribution et entrepôts",
    "Usines et installations industrielles",
    "Centres de données et télécommunications",
    "Installations énergétiques",
    "Projets miniers et ressources naturelles",
    "Rénovation et restauration patrimoniale",
    "Projets gouvernementaux",
    "Organismes sans but lucratif",
    "Coopératives d'habitation",
    "Autre secteur construction"
]

# Tranches budgétaires construction résidentielle P2B
TRANCHES_BUDGET = [
    "Moins de 1 000$",
    "1 000$ - 5 000$",
    "5 000$ - 15 000$",
    "15 000$ - 50 000$",
    "50 000$ - 100 000$",
    "100 000$ - 200 000$",
    "Plus de 200 000$",
    "À déterminer selon projet"
]

# Délais de réalisation construction
DELAIS_LIVRAISON = [
    "Urgent (moins de 1 mois)",
    "Court terme (1-3 mois)",
    "Moyen terme (3-6 mois)", 
    "Long terme (6-12 mois)",
    "Très long terme (1-2 ans)",
    "Projet pluriannuel (2+ ans)",
    "Selon disponibilité"
]

# Tailles d'entreprises
TAILLES_ENTREPRISE = [
    "TPE (1-9 employés)",
    "PME (10-249 employés)",
    "ETI (250-4999 employés)",
    "Grande entreprise (5000+ employés)"
]

# Statuts des demandes de devis
STATUTS_DEMANDE = {
    "brouillon": "📝 Brouillon",
    "publiee": "📢 Publiée",
    "en_cours": "📋 En cours d'évaluation",
    "fermee": "🔒 Fermée aux soumissions",
    "attribuee": "✅ Attribuée",
    "annulee": "❌ Annulée"
}

# Statuts des soumissions avec workflow d'approbation
STATUTS_SOUMISSION = {
    "brouillon": "📝 Brouillon",
    "soumise": "📤 Soumise",
    "recue": "📥 Reçue",
    "en_evaluation": "🔍 En évaluation",
    "en_approbation": "⏳ En approbation",
    "approuvee": "✅ Approuvée",
    "rejetee": "❌ Rejetée",
    "en_negociation": "💬 En négociation",
    "acceptee": "🎉 Acceptée",
    "refusee": "🚫 Refusée"
}

# Critères d'évaluation des soumissions
CRITERES_EVALUATION = [
    "Prix et rapport qualité-prix",
    "Expérience et références",
    "Qualité de la proposition technique",
    "Délais de livraison proposés",
    "Méthodologie de travail",
    "Équipe proposée",
    "Certifications et qualifications",
    "Innovation et créativité",
    "Support post-livraison",
    "Flexibilité et adaptabilité"
]

# Rôles utilisateurs P2B
ROLES_UTILISATEUR = {
    "client": "Particulier",
    "prestataire": "Entreprise de Construction", 
    "admin": "Administrateur"
}

# Étapes du processus d'approbation
ETAPES_APPROBATION = [
    {
        "etape": 1,
        "nom": "Réception",
        "description": "Soumission reçue et enregistrée"
    },
    {
        "etape": 2, 
        "nom": "Évaluation technique",
        "description": "Analyse de la proposition technique"
    },
    {
        "etape": 3,
        "nom": "Évaluation financière", 
        "description": "Analyse du budget et des coûts"
    },
    {
        "etape": 4,
        "nom": "Évaluation globale",
        "description": "Synthèse et notation finale"
    },
    {
        "etape": 5,
        "nom": "Décision finale",
        "description": "Approbation ou rejet"
    }
]

# Paramètres de sécurité
SECURITY_CONFIG = {
    "password_min_length": 8,
    "session_timeout": 7200,  # 2 heures en secondes
    "max_file_size": 25 * 1024 * 1024,  # 25 MB pour les documents B2B
    "max_files_per_upload": 10
}

# Formats de fichiers autorisés B2B
FORMATS_AUTORISES = {
    "documents": ["pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx"],
    "images": ["png", "jpg", "jpeg", "gif", "bmp", "svg"],
    "techniques": ["zip", "rar", "txt", "csv", "json", "xml"],
    "tous": ["pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "png", "jpg", "jpeg", "gif", "bmp", "svg", "zip", "rar", "txt", "csv"]
}

# Configuration email
EMAIL_CONFIG = {
    "smtp_server": "localhost",
    "smtp_port": 587,
    "use_tls": True,
    "from_email": "noreply@soumissions-entreprises.ca",
    "admin_email": "admin@soumissions-entreprises.ca"
}

# Messages système
MESSAGES = {
    "welcome_client": "Bienvenue sur la plateforme de soumissions B2B",
    "welcome_prestataire": "Trouvez de nouveaux clients avec notre plateforme",
    "demande_publiee": "Votre demande de devis a été publiée avec succès",
    "soumission_envoyee": "Votre soumission a été envoyée et sera évaluée",
    "soumission_approuvee": "Félicitations ! Votre soumission a été approuvée",
    "acces_refuse": "Accès refusé - Vérifiez vos identifiants"
}

# Configuration des notifications
NOTIFICATIONS_CONFIG = {
    "nouvelle_demande": "Nouvelle demande de devis disponible",
    "soumission_recue": "Nouvelle soumission reçue pour votre demande",
    "changement_statut": "Le statut de votre soumission a changé",
    "deadline_approche": "Date limite de soumission dans 48h",
    "approbation_requise": "Une soumission nécessite votre approbation",
    "decision_prise": "Une décision a été prise sur votre soumission"
}

# Informations organisation
ORGANISATION_INFO = {
    "nom": "Construction Québec P2B - Services pour Particuliers",
    "adresse": "1234 Boulevard René-Lévesque, Montréal, QC, H3A 1A1",
    "telephone": "(514) 555-0123",
    "email": "info@constructionquebec.ca",
    "site_web": "https://www.constructionquebec.ca"
}

# Configuration des rapports et analytics
RAPPORTS_CONFIG = {
    "formats_export": ["PDF", "Excel", "CSV"],
    "metriques_cles": [
        "Nombre de demandes publiées",
        "Taux de réponse aux demandes",
        "Temps moyen d'approbation",
        "Satisfaction clients",
        "Valeur totale des contrats"
    ],
    "frequence_rapports": "hebdomadaire",
    "retention_donnees": 730  # 2 ans en jours
}

# Configuration du système de notation
SYSTEME_NOTATION = {
    "note_min": 1,
    "note_max": 5,
    "criteres_poids": {
        "prix": 0.3,
        "qualite": 0.25, 
        "experience": 0.2,
        "delais": 0.15,
        "innovation": 0.1
    }
}