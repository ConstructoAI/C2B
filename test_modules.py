#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour tester l'importation des modules
"""

import sys

print("Test d'importation des modules...\n")

# Test 1: bon_commande_simple
try:
    from bon_commande_simple import show_bon_commande_interface
    print("[OK] Module bon_commande_simple importé")
    print("     -> Fonction show_bon_commande_interface disponible")
except ImportError as e:
    print(f"[ERREUR] Module bon_commande_simple: {e}")

# Test 2: fournisseurs_manager
try:
    from fournisseurs_manager import show_fournisseurs_interface
    print("[OK] Module fournisseurs_manager importé")
    print("     -> Fonction show_fournisseurs_interface disponible")
except ImportError as e:
    print(f"[ERREUR] Module fournisseurs_manager: {e}")

# Test 3: app
try:
    import app
    print("\n[OK] Module app importé")

    # Vérifier les flags
    print(f"     -> BON_COMMANDE_AVAILABLE: {app.BON_COMMANDE_AVAILABLE}")
    print(f"     -> BON_COMMANDE_SIMPLE_AVAILABLE: {app.BON_COMMANDE_SIMPLE_AVAILABLE}")
    print(f"     -> FOURNISSEURS_AVAILABLE: {app.FOURNISSEURS_AVAILABLE}")

except ImportError as e:
    print(f"[ERREUR] Module app: {e}")

print("\nTest terminé!")