#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de débogage pour vérifier pourquoi le template moderne n'est pas utilisé
"""

import sys
import os
import io

# Configurer l'encodage pour Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("DÉBOGAGE DU TEMPLATE MODERNE")
print("=" * 60)

# 1. Vérifier la présence des fichiers
print("\n1. VÉRIFICATION DES FICHIERS:")
files_to_check = [
    'bon_commande_simple.py',
    'bon_commande_template_moderne.py',
    'app.py'
]

for file in files_to_check:
    exists = os.path.exists(file)
    status = "✅" if exists else "❌"
    print(f"  {status} {file}: {'Existe' if exists else 'MANQUANT'}")

# 2. Vérifier l'import du template moderne
print("\n2. TEST D'IMPORT DU TEMPLATE:")
try:
    from bon_commande_template_moderne import generate_modern_html
    print("  ✅ Import direct réussi")

    # Vérifier que la fonction existe
    if callable(generate_modern_html):
        print("  ✅ Fonction generate_modern_html est appelable")
except ImportError as e:
    print(f"  ❌ Erreur d'import: {e}")

# 3. Vérifier le contenu de bon_commande_simple.py
print("\n3. VÉRIFICATION DE BON_COMMANDE_SIMPLE.PY:")
if os.path.exists('bon_commande_simple.py'):
    with open('bon_commande_simple.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Chercher les éléments clés
    checks = [
        ('from bon_commande_template_moderne import', 'Import du template'),
        ('USE_MODERN_TEMPLATE', 'Variable de contrôle'),
        ('generate_modern_html_embedded', 'Fonction intégrée de fallback'),
        ('if USE_MODERN_TEMPLATE:', 'Condition d\'utilisation')
    ]

    for pattern, description in checks:
        if pattern in content:
            print(f"  ✅ {description} trouvé")
        else:
            print(f"  ❌ {description} MANQUANT")

# 4. Tester l'import de bon_commande_simple
print("\n4. TEST D'IMPORT DE BON_COMMANDE_SIMPLE:")
try:
    import bon_commande_simple
    print("  ✅ Module importé")

    # Vérifier les attributs
    if hasattr(bon_commande_simple, 'USE_MODERN_TEMPLATE'):
        value = bon_commande_simple.USE_MODERN_TEMPLATE
        print(f"  {'✅' if value else '❌'} USE_MODERN_TEMPLATE = {value}")
    else:
        print("  ❌ USE_MODERN_TEMPLATE non trouvé")

    if hasattr(bon_commande_simple, 'generate_html'):
        print("  ✅ Fonction generate_html existe")
    else:
        print("  ❌ Fonction generate_html MANQUANTE")

    if hasattr(bon_commande_simple, 'generate_modern_html_embedded'):
        print("  ✅ Fonction de fallback existe")
    else:
        print("  ❌ Fonction de fallback MANQUANTE")

except Exception as e:
    print(f"  ❌ Erreur: {e}")

# 5. Test rapide de génération
print("\n5. TEST DE GÉNÉRATION HTML:")
try:
    import bon_commande_simple

    # Données minimales de test
    test_data = {
        'numero': 'TEST-001',
        'date': '2024-01-01',
        'fournisseur': {'nom': 'Test'},
        'client': {'nom': 'Client'},
        'projet': {'nom': 'Projet'},
        'items': [],
        'totaux': {
            'sous_total': 0,
            'tps': 0,
            'tvq': 0,
            'total': 0
        }
    }

    html = bon_commande_simple.generate_html(test_data)

    # Vérifier le contenu
    if 'Poppins' in html:
        print("  ✅ Police Poppins détectée")
    else:
        print("  ❌ Police Poppins NON détectée")

    if 'linear-gradient' in html:
        print("  ✅ Gradients détectés")
    else:
        print("  ❌ Gradients NON détectés")

    if '#667eea' in html:
        print("  ✅ Couleur thème détectée")
    else:
        print("  ❌ Couleur thème NON détectée")

except Exception as e:
    print(f"  ❌ Erreur lors du test: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("FIN DU DÉBOGAGE")
print("=" * 60)