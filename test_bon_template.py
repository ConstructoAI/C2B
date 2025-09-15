#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test pour vérifier que le template moderne des bons de commande fonctionne
"""

import sys
import os
import io

# Configurer l'encodage pour Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test de l'import du module
print("🔍 Test d'import du module bon_commande_simple...")
try:
    import bon_commande_simple
    print("✅ Module bon_commande_simple importé avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)

# Test de l'import du template moderne
print("\n🔍 Test d'import du template moderne...")
try:
    from bon_commande_template_moderne import generate_modern_html
    print("✅ Template moderne importé avec succès")
except ImportError as e:
    print(f"⚠️ Template moderne non disponible: {e}")
    print("   Le module utilisera le template intégré comme fallback")

# Test de génération HTML
print("\n🔍 Test de génération HTML...")
test_data = {
    'numero': 'BC-2024-001',
    'date': '2024-01-15',
    'fournisseur': {
        'nom': 'Fournisseur Test Inc.',
        'contact': 'Jean Dupont',
        'telephone': '514-555-1234',
        'email': 'contact@fournisseur.ca'
    },
    'client': {
        'nom': 'Client Test Ltd.'
    },
    'projet': {
        'nom': 'Projet de Test',
        'adresse': '123 Rue Test, Montréal'
    },
    'items': [
        {
            'description': 'Article de test 1',
            'details': 'Détails supplémentaires pour l\'article 1',
            'quantite': 10,
            'unite': 'unité',
            'prix_unitaire': 25.50,
            'total': 255.00
        },
        {
            'description': 'Article de test 2',
            'quantite': 5,
            'unite': 'boîte',
            'prix_unitaire': 100.00,
            'total': 500.00
        }
    ],
    'totaux': {
        'sous_total': 755.00,
        'tps': 37.75,
        'tvq': 75.31,
        'total': 868.06
    }
}

try:
    html = bon_commande_simple.generate_html(test_data)

    # Vérifier que le HTML contient les éléments du template moderne
    checks = [
        ('Poppins', 'Police moderne'),
        ('linear-gradient', 'Gradients'),
        ('667eea', 'Couleur thème'),
        ('animation', 'Animations'),
        ('info-icon', 'Icônes d\'information'),
        ('backdrop-filter', 'Effets visuels')
    ]

    print("\n📊 Vérification du contenu HTML:")
    all_passed = True
    for keyword, description in checks:
        if keyword in html:
            print(f"  ✅ {description} trouvé")
        else:
            print(f"  ❌ {description} manquant")
            all_passed = False

    # Sauvegarder le HTML pour inspection visuelle
    output_file = 'test_bon_commande_output.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n💾 HTML sauvegardé dans: {output_file}")

    if all_passed:
        print("\n🎉 SUCCÈS: Le template moderne fonctionne correctement!")
    else:
        print("\n⚠️ ATTENTION: Certains éléments du template moderne sont manquants")
        print("   Le template de base pourrait être utilisé")

except Exception as e:
    print(f"❌ Erreur lors de la génération HTML: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test terminé")