# Configuration Entreprise Unique - Système de Soumissions C2B
# Ce fichier définit l'entreprise propriétaire du portail

import os
import hashlib

# ============================================================================
# CONFIGURATION DE L'ENTREPRISE PROPRIÉTAIRE DU PORTAIL
# ============================================================================

# Informations de l'entreprise propriétaire
ENTREPRISE_PROPRIETAIRE = {
    "nom_entreprise": "Construction Excellence Québec Inc.",
    "numero_rbq": "5678-1234-01",
    "domaines_expertise": ["Construction commerciale", "Construction résidentielle", "Rénovation générale"],
    "taille_entreprise": "PME (10-249 employés)",
    
    # Contact principal
    "nom_contact": "Alex Martin",
    "poste_contact": "Directeur général",
    "email": "alex@constructionexcellence.ca",
    "telephone": "514-555-4001",
    
    # Adresse
    "adresse": "1500 Boulevard Saint-Laurent",
    "ville": "Montréal", 
    "code_postal": "H2X 2T6",
    "province": "Québec",
    
    # Informations d'entreprise
    "numero_entreprise": "1234567890",
    "site_web": "https://www.constructionexcellence.ca",
    "description_entreprise": """Construction Excellence Québec Inc. est une entreprise de construction générale 
    spécialisée dans les projets résidentiels et commerciaux. Avec plus de 15 ans d'expérience, 
    nous offrons des services complets de construction, rénovation et réparation.
    
    Nos spécialités :
    - Construction résidentielle neuve
    - Rénovation cuisine et salle de bain
    - Agrandissements de maison
    - Construction commerciale
    - Toiture et revêtement extérieur
    
    Certifiée RBQ et membre de l'APCHQ, notre équipe qualifiée garantit des travaux de qualité 
    supérieure dans le respect des délais et budgets convenus.""",
    
    # Authentification (mot de passe par défaut)
    "mot_de_passe": "entreprise123",  # À changer lors de l'installation
    
    # Certifications et assurances
    "certifications": [
        "RBQ: 5678-1234-01",
        "APCHQ - Association provinciale des constructeurs d'habitations du Québec", 
        "ASP Construction",
        "CNESST - Formation sécurité sur les chantiers",
        "ISO 9001:2015"
    ],
    
    "assurances": {
        "responsabilite_civile": "2 000 000 $",
        "assurance_chantier": "1 000 000 $",
        "csst": "À jour",
        "numero_police": "POL-2024-CE-001"
    },
    
    # Tarification
    "tarif_horaire_min": 85.0,
    "tarif_horaire_max": 150.0,
    
    # Zones de service
    "zones_service": [
        "Montréal et région métropolitaine",
        "Laval",
        "Longueuil", 
        "Brossard",
        "Saint-Lambert",
        "Dans un rayon de 50 km de Montréal"
    ],
    
    # Langues
    "langues_parlees": ["Français", "Anglais"],
    
    # Configuration système
    "disponibilite": "disponible",  # disponible, occupe, indisponible
    "accepte_nouveaux_projets": True,
    "delai_reponse_moyen": 24,  # en heures
}

# ============================================================================
# CONFIGURATION DU PORTAIL
# ============================================================================

# Informations affichées sur le portail client
PORTAIL_CONFIG = {
    "titre_site": f"Demandes de Soumissions - {ENTREPRISE_PROPRIETAIRE['nom_entreprise']}",
    "sous_titre": "Obtenez votre soumission personnalisée en quelques clics",
    "description_accueil": f"""
    Bienvenue sur le portail de demandes de soumissions de {ENTREPRISE_PROPRIETAIRE['nom_entreprise']}.
    
    Nous sommes spécialisés dans :
    {', '.join(ENTREPRISE_PROPRIETAIRE['domaines_expertise'])}
    
    Soumettez votre projet en ligne et recevez une réponse détaillée dans les plus brefs délais.
    """,
    
    # Messages personnalisés
    "message_bienvenue": f"Merci de faire confiance à {ENTREPRISE_PROPRIETAIRE['nom_entreprise']} !",
    "message_soumission_envoyee": "Votre demande a été transmise à notre équipe. Nous vous répondrons sous 24-48h.",
    "message_contact": f"Pour toute question : {ENTREPRISE_PROPRIETAIRE['telephone']} ou {ENTREPRISE_PROPRIETAIRE['email']}",
    
    # Couleurs du thème (optionnel)
    "couleur_principale": "#1E40AF",  # Bleu professionnel
    "couleur_secondaire": "#059669",  # Vert construction
    "couleur_accent": "#7C3AED",      # Violet pour les boutons
}

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def hash_password(password: str) -> str:
    """Hash le mot de passe de l'entreprise"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_entreprise_proprietaire():
    """Retourne les informations de l'entreprise propriétaire"""
    return ENTREPRISE_PROPRIETAIRE.copy()

def get_entreprise_id():
    """Retourne l'ID de l'entreprise propriétaire (toujours 1 en mono-entreprise)"""
    return 1

def valider_configuration():
    """Valide la configuration de l'entreprise"""
    erreurs = []
    
    # Vérifications obligatoires
    if not ENTREPRISE_PROPRIETAIRE.get('nom_entreprise'):
        erreurs.append("Le nom de l'entreprise est obligatoire")
    
    if not ENTREPRISE_PROPRIETAIRE.get('email'):
        erreurs.append("L'email de contact est obligatoire")
        
    if not ENTREPRISE_PROPRIETAIRE.get('telephone'):
        erreurs.append("Le numéro de téléphone est obligatoire")
    
    if ENTREPRISE_PROPRIETAIRE.get('mot_de_passe') == 'entreprise123':
        erreurs.append("SÉCURITÉ: Changez le mot de passe par défaut!")
    
    return erreurs

def initialiser_entreprise_proprietaire(conn):
    """Initialise l'entreprise propriétaire dans la base de données"""
    cursor = conn.cursor()
    
    # Supprimer les données existantes
    cursor.execute('DELETE FROM entreprises_prestataires')
    
    # Insérer l'entreprise propriétaire
    entreprise = ENTREPRISE_PROPRIETAIRE
    cursor.execute('''
        INSERT INTO entreprises_prestataires (
            id, nom_entreprise, numero_rbq, domaines_expertise, taille_entreprise,
            nom_contact, poste_contact, email, telephone, adresse, ville, code_postal,
            mot_de_passe_hash, numero_entreprise, site_web, description_entreprise,
            certifications, tarif_horaire_min, tarif_horaire_max, zones_service,
            langues_parlees, disponibilite, statut, date_inscription
        ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'actif', CURRENT_TIMESTAMP)
    ''', (
        entreprise['nom_entreprise'],
        entreprise['numero_rbq'], 
        str(entreprise['domaines_expertise']),
        entreprise['taille_entreprise'],
        entreprise['nom_contact'],
        entreprise['poste_contact'],
        entreprise['email'],
        entreprise['telephone'],
        entreprise['adresse'],
        entreprise['ville'],
        entreprise['code_postal'],
        hash_password(entreprise['mot_de_passe']),
        entreprise['numero_entreprise'],
        entreprise['site_web'],
        entreprise['description_entreprise'],
        str(entreprise['certifications']),
        entreprise['tarif_horaire_min'],
        entreprise['tarif_horaire_max'],
        str(entreprise['zones_service']),
        str(entreprise['langues_parlees']),
        entreprise['disponibilite']
    ))
    
    conn.commit()
    print(f"SUCCES: Entreprise proprietaire '{entreprise['nom_entreprise']}' configuree!")

# ============================================================================
# VALIDATION AU CHARGEMENT
# ============================================================================

if __name__ == "__main__":
    print("=== VALIDATION DE LA CONFIGURATION ENTREPRISE ===")
    
    erreurs = valider_configuration()
    if erreurs:
        print("ERREURS de configuration:")
        for erreur in erreurs:
            print(f"   - {erreur}")
    else:
        print("SUCCES: Configuration entreprise valide")
    
    print(f"\nEntreprise configuree:")
    print(f"   Nom: {ENTREPRISE_PROPRIETAIRE['nom_entreprise']}")
    print(f"   Contact: {ENTREPRISE_PROPRIETAIRE['nom_contact']}")
    print(f"   Email: {ENTREPRISE_PROPRIETAIRE['email']}")
    print(f"   RBQ: {ENTREPRISE_PROPRIETAIRE.get('numero_rbq', 'Non specifie')}")