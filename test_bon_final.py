#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test final du bon de commande avec le template style soumission
"""

import sys
import os
import io

# Configurer l'encodage pour Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("TEST FINAL DU BON DE COMMANDE")
print("=" * 60)

# Test de l'import du module
print("\n1. Import du module bon_commande_simple...")
try:
    import bon_commande_simple
    print("   ✓ Module importé avec succès")
except ImportError as e:
    print(f"   ✗ Erreur d'import: {e}")
    sys.exit(1)

# Test de la fonction get_company_info
print("\n2. Test de get_company_info()...")
try:
    company = bon_commande_simple.get_company_info()
    required_fields = ['name', 'address', 'city', 'province', 'postal_code', 'phone', 'email', 'rbq', 'neq', 'tps', 'tvq']

    all_present = True
    for field in required_fields:
        if field in company:
            print(f"   ✓ {field}: {company[field]}")
        else:
            print(f"   ✗ {field}: MANQUANT")
            all_present = False

    if not all_present:
        print("   ⚠ Certains champs manquent!")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()

# Test de génération HTML
print("\n3. Génération du bon de commande HTML...")
test_data = {
    'numero': 'BC-2024-TEST',
    'date': '15/01/2024',
    'fournisseur': {
        'nom': 'Fournisseur Test Inc.',
        'contact': 'Jean Dupont',
        'telephone': '514-555-1234',
        'email': 'contact@fournisseur.ca',
        'adresse': '123 Rue Industrielle, Montréal'
    },
    'client': {
        'nom': 'Client Excellence Plus'
    },
    'projet': {
        'nom': 'Projet de Construction',
        'adresse': '456 Boulevard Principal, Laval',
        'ref_soumission': 'SOUM-2024-001'
    },
    'items': [
        {
            'description': 'Matériaux de construction',
            'details': 'Béton, acier, bois de charpente',
            'quantite': 100,
            'unite': 'unité',
            'prix_unitaire': 50.00,
            'total': 5000.00
        },
        {
            'description': 'Main d\'oeuvre spécialisée',
            'quantite': 40,
            'unite': 'heures',
            'prix_unitaire': 85.00,
            'total': 3400.00
        }
    ],
    'totaux': {
        'sous_total': 8400.00,
        'tps': 420.00,
        'tvq': 838.95,
        'total': 9658.95
    },
    'conditions_paiement': 'Net 30 jours',
    'date_livraison': '25/01/2024',
    'lieu_livraison': 'Sur le chantier',
    'notes': 'Livraison par camion. Prévoir accès pour véhicules lourds.'
}

try:
    html = bon_commande_simple.generate_html(test_data)

    # Vérifier que le HTML contient les éléments du template soumission
    checks = [
        ('linear-gradient(135deg, var(--primary-dark)', 'Gradient bleu'),
        ('#3b82f6', 'Couleur bleue'),
        ('#374151', 'Couleur grise'),
        ('font-family: -apple-system', 'Police système'),
        ('info-box', 'Boîtes d\'information'),
        ('table-header', 'En-tête de tableau stylé'),
        ('Construction Excellence Plus', 'Nom de l\'entreprise'),
        ('Montréal', 'Ville'),
        ('Québec', 'Province')
    ]

    print("\n   Vérification du contenu HTML:")
    all_passed = True
    for keyword, description in checks:
        if keyword in html:
            print(f"   ✓ {description} trouvé")
        else:
            print(f"   ✗ {description} MANQUANT")
            all_passed = False

    # Sauvegarder le HTML pour inspection visuelle
    output_file = 'test_bon_final.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n   💾 HTML sauvegardé dans: {output_file}")

    if all_passed:
        print("\n✅ SUCCÈS: Le bon de commande est généré correctement!")
    else:
        print("\n⚠ ATTENTION: Certains éléments sont manquants")

except Exception as e:
    print(f"   ✗ Erreur lors de la génération HTML: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("FIN DU TEST")
print("=" * 60)