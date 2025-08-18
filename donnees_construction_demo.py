# Données de démonstration spécifiques à la construction B2B Québec

# Demandes de devis construction de démonstration
demandes_construction_demo = [
    {
        'client_id': 1,  # Développements Immobiliers Québec
        'titre': 'Construction d\'un complexe commercial de 15 000 pi²',
        'type_projet': 'Construction commerciale',
        'description_detaillee': '''Nous recherchons un entrepreneur général pour la construction d'un nouveau complexe commercial.
        
        CONTEXTE:
        Notre entreprise développe un nouveau centre commercial dans la région de Montréal Est.
        
        SPÉCIFICATIONS DU PROJET:
        - Surface totale: 15 000 pi² répartis en 8 unités commerciales
        - Structure: Charpente d'acier avec murs de béton préfabriqué
        - Toiture: Membrane TPO avec isolation R-30
        - Finitions extérieures: Brique et panneau composite
        - Stationnement: 60 places avec éclairage LED
        - Système électrique: 600 ampères, 347/600V
        - Système de chauffage: Unités de toit à gaz naturel
        
        EXIGENCES PARTICULIÈRES:
        - Conformité aux normes accessibilité universelle
        - Certification LEED Silver souhaitée
        - Respect du calendrier municipal (ouverture prévue automne 2024)
        - Coordination avec les services publics existants
        
        LIVRABLES ATTENDUS:
        - Plans et devis détaillés
        - Calendrier de construction détaillé
        - Gestion complète du projet incluant sous-traitants
        - Rapports de progression hebdomadaires
        - Garanties sur matériaux et main-d'œuvre''',
        'budget_min': 2500000.0,
        'budget_max': 3200000.0,
        'delai_livraison': 'Long terme (6-12 mois)',
        'date_limite_soumissions': '2024-04-15 23:59:59',
        'competences_requises': '["Construction commerciale", "Charpente acier", "Gestion de projet", "LEED"]',
        'niveau_experience_requis': 'senior',
        'numero_reference': 'CB-20240301-001'
    },
    {
        'client_id': 2,  # Industries Manufacturières du Québec
        'titre': 'Agrandissement d\'usine avec installation de pont roulant',
        'type_projet': 'Construction industrielle',
        'description_detaillee': '''Projet d'agrandissement de notre usine principale avec installation d'équipements lourds.
        
        OBJECTIFS:
        - Augmenter la capacité de production de 40%
        - Installer un nouveau pont roulant de 25 tonnes
        - Moderniser les systèmes électriques et mécaniques
        
        DESCRIPTION TECHNIQUE:
        - Agrandissement: 8 000 pi² en continuité avec bâtiment existant
        - Hauteur libre: 28 pieds minimum pour pont roulant
        - Fondations: Supports pour équipements lourds (vibrations)
        - Structure: Charpente d'acier soudée sur place
        - Toiture: Système de ventilation naturelle intégré
        - Plancher industriel: Béton haute résistance avec durcisseur
        
        SYSTÈMES REQUIS:
        - Électricité industrielle 480V/3ph pour équipements
        - Système de ventilation et extraction des fumées
        - Éclairage haute performance (LED, 50 fc minimum)
        - Système de sprinkleurs conforme NFPA
        - Installation complète du pont roulant
        
        CONTRAINTES:
        - Maintien de la production pendant les travaux
        - Accès limité aux équipements existants
        - Coordination avec arrêts de production planifiés
        - Respect strict des normes CNESST''',
        'budget_min': 1800000.0,
        'budget_max': 2400000.0,
        'delai_livraison': 'Moyen terme (3-6 mois)',
        'date_limite_soumissions': '2024-04-20 23:59:59',
        'competences_requises': '["Construction industrielle", "Charpente acier", "Électricité industrielle", "Équipements lourds"]',
        'niveau_experience_requis': 'expert',
        'numero_reference': 'CB-20240302-002'
    },
    {
        'client_id': 3,  # Hôpitaux Régionaux Santé Québec
        'titre': 'Rénovation de bloc opératoire avec salles blanches',
        'type_projet': 'Rénovation de bâtiments commerciaux',
        'description_detaillee': '''Rénovation complète d'un bloc opératoire de 3 500 pi² avec mise aux normes.
        
        SITUATION ACTUELLE:
        - Bloc opératoire de 1995 nécessitant modernisation complète
        - 4 salles d'opération + salles de réveil et préparation
        - Systèmes de ventilation et filtration défaillants
        - Non-conformité aux nouvelles normes CSA Z317.2
        
        TRAVAUX REQUIS:
        - Démolition sélective (maintien structure)
        - Installation de nouveaux systèmes CVC avec filtration HEPA
        - Revêtements muraux et plafonds conformes salles blanches
        - Planchers conducteurs antidérapants
        - Éclairage chirurgical spécialisé
        - Système électrique d'urgence dédié
        - Installation gaz médicaux (O2, N2O, air comprimé)
        
        EXIGENCES SPÉCIALISÉES:
        - Pression positive maintenue en tout temps
        - Niveau sonore < 45 dB(A)
        - Température ±1°C, humidité ±5%
        - Étanchéité parfaite (test fumée obligatoire)
        - Conformité réglementaire stricte (Santé Canada)
        
        CONTRAINTES MAJEURES:
        - Travaux par phases (maintien 2 salles opérationnelles)
        - Protocoles de décontamination quotidiens
        - Accès restreint et contrôlé (badgeage)
        - Livraisons matériaux en horaires spécifiques''',
        'budget_min': 850000.0,
        'budget_max': 1200000.0,
        'delai_livraison': 'Long terme (6-12 mois)',
        'date_limite_soumissions': '2024-04-10 23:59:59',
        'competences_requises': '["Salles blanches", "Systèmes CVC spécialisés", "Électricité médicale", "Gaz médicaux"]',
        'niveau_experience_requis': 'expert',
        'numero_reference': 'CB-20240303-003'
    }
]

# Soumissions construction de démonstration
soumissions_construction_demo = [
    {
        'demande_id': 1,
        'prestataire_id': 1,  # Construction Excellence Québec
        'titre_soumission': 'Complexe commercial clé en main avec certification LEED',
        'resume_executif': '''Construction Excellence Québec propose une solution complète pour votre complexe commercial de 15 000 pi² avec notre expertise de plus de 25 ans en construction commerciale et notre certification LEED AP.''',
        'proposition_technique': '''APPROCHE DE CONSTRUCTION PROPOSÉE:
        
        PHASE 1: PRÉPARATION ET FONDATIONS (4 semaines)
        - Arpentage et implantation par arpenteur agréé
        - Excavation et terrassement selon plans géotechniques
        - Coulée de fondations avec béton haute performance (35 MPa)
        - Installation des services souterrains (aqueduc, égouts, électricité)
        
        PHASE 2: STRUCTURE PRINCIPALE (8 semaines)
        - Érection de charpente d'acier certifiée CSA G40.21-350W
        - Installation de poutrelles et tablier métallique
        - Montage des murs préfabriqués avec isolation intégrée
        - Installation de la toiture structurale
        
        PHASE 3: ENVELOPPE ET ÉTANCHÉITÉ (6 semaines)
        - Installation membrane TPO soudée avec isolation R-30
        - Pose de revêtement extérieur (brique et panneaux composites)
        - Installation fenestration avec vitrage performant
        - Système d'étanchéité à l'air (test Blower Door)
        
        PHASE 4: SYSTÈMES MÉCANIQUES/ÉLECTRIQUES (10 semaines)
        - Installation système électrique 600A avec panneaux dédiés
        - Système CVC avec unités de toit à haut rendement (>90% AFUE)
        - Installation système de sprinkleurs conforme NFPA 13
        - Câblage données et télécommunications
        
        PHASE 5: FINITIONS ET AMÉNAGEMENT (8 semaines)
        - Cloisons intérieures et finitions selon plan locataires
        - Installation revêtements de sol et plafonds suspendus
        - Peinture intérieure avec produits faibles COV
        - Installation éclairage LED haute efficacité
        
        CERTIFICATION LEED SILVER:
        - Gestion des matériaux recyclés (75% minimum)
        - Utilisation de matériaux régionaux (rayon 800 km)
        - Systèmes à haute efficacité énergétique
        - Gestion des eaux pluviales sur site
        - Aménagement paysager avec espèces indigènes''',
        'budget_total': 2950000.0,
        'delai_livraison': '36 semaines (9 mois)',
        'statut': 'soumise'
    },
    {
        'demande_id': 2,
        'prestataire_id': 2,  # Électricité Industrielle Québec
        'titre_soumission': 'Agrandissement industriel avec systèmes électriques spécialisés',
        'resume_executif': '''Électricité Industrielle Québec, avec plus de 15 ans d'expérience en projets industriels lourds, propose une solution intégrée incluant structure, systèmes électriques 480V et installation complète du pont roulant 25 tonnes.''',
        'proposition_technique': '''SOLUTION TECHNIQUE INTÉGRÉE:
        
        PHASE 1: ÉTUDES ET PRÉPARATION (3 semaines)
        - Analyse structurale détaillée du bâtiment existant
        - Calculs de charges pour pont roulant 25 tonnes
        - Plans d'exécution par ingénieur structurel P.Eng.
        - Coordination avec Hydro-Québec pour augmentation de service
        
        PHASE 2: TRAVAUX STRUCTURAUX (12 semaines)
        - Excavation et coulée de fondations renforcées
        - Érection charpente d'acier avec poutres de roulement
        - Installation de colonnes de support pont roulant
        - Connexions soudées certifiées CSA W47.1
        - Plancher industriel béton 6" avec durcisseur Hardener
        
        PHASE 3: SYSTÈMES ÉLECTRIQUES INDUSTRIELS (8 semaines)
        - Installation tableau principal 480V/3ph/600A
        - Câblage force motrice pour équipements de production
        - Système d'éclairage LED industriel 50 fc (500 lux)
        - Installation barres de distribution aérienne
        - Mise à la terre selon norme CSA C22.1
        
        PHASE 4: PONT ROULANT ET AUTOMATISATION (4 semaines)
        - Installation pont roulant Demag 25 tonnes
        - Programmation automate Siemens S7-1500
        - Système de contrôle sans fil pour opération
        - Formation opérateurs et procédures de sécurité
        - Tests de charge et certification CNESST
        
        PHASE 5: SYSTÈMES AUXILIAIRES (6 semaines)
        - Ventilation industrielle avec extracteurs de fumées
        - Système de sprinkleurs haute pression
        - Éclairage d'urgence avec générateur de secours
        - Installation équipements de manutention
        
        GESTION DE PROJET:
        - Coordination avec production existante
        - Arrêts planifiés minimaux (3 fins de semaine maximum)
        - Équipes de nuit pour travaux critiques
        - Supervision continue par contremaître certifié''',
        'budget_total': 2150000.0,
        'delai_livraison': '33 semaines (8 mois)',
        'statut': 'en_evaluation'
    }
]

# Messages de démonstration construction
messages_construction_demo = [
    {
        'demande_id': 1,
        'prestataire_id': 1,
        'expediteur_type': 'prestataire',
        'expediteur_id': 1,
        'destinataire_id': 1,
        'message': 'Bonjour Mme Dubois, merci pour ce projet stimulant. Notre équipe d\'ingénieurs a préparé une proposition détaillée incluant la certification LEED Silver. Nous avons une question concernant les spécifications de stationnement - souhaitez-vous des bornes de recharge électrique?'
    },
    {
        'demande_id': 1,
        'prestataire_id': 1,
        'expediteur_type': 'client',
        'expediteur_id': 1,
        'destinataire_id': 1,
        'message': 'Merci pour votre soumission très détaillée. Excellente idée pour les bornes électriques - prévoyez 8 bornes niveau 2. Pouvez-vous aussi confirmer si le délai inclut les retards possibles dus aux conditions météo hivernales?'
    },
    {
        'demande_id': 2,
        'prestataire_id': 2,
        'expediteur_type': 'prestataire',
        'expediteur_id': 2,
        'destinataire_id': 2,
        'message': 'M. Tremblay, notre équipe a visité le site hier. Nous confirmons la faisabilité d\'installer le pont roulant sans arrêt de production majeur. Notre calendrier prévoit les travaux électriques pendant vos arrêts planifiés de maintenance. Acceptez-vous un début des travaux la première semaine de mai?'
    }
]