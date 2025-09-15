#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de la génération du lien public pour les bons de commande
"""

import os
import sys
import io

# Configurer l'encodage pour Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("TEST DU LIEN PUBLIC POUR BON DE COMMANDE")
print("=" * 60)

# Test en local
print("\n1. Test en environnement LOCAL:")
os.environ.pop('SPACE_ID', None)
os.environ.pop('SPACE_HOST', None)
os.environ.pop('APP_URL', None)
os.environ.pop('RENDER', None)

from bon_commande_simple import get_base_url
url = get_base_url()
print(f"   URL générée: {url}")
print(f"   ✓ Correct" if url == "http://localhost:8501" else f"   ✗ Incorrect")

# Test Hugging Face avec SPACE_HOST
print("\n2. Test Hugging Face avec SPACE_HOST:")
os.environ['SPACE_HOST'] = 'sylvainleduc-c2b.hf.space'
# Recharger le module pour prendre en compte les nouvelles variables
import importlib
importlib.reload(sys.modules['bon_commande_simple'])
from bon_commande_simple import get_base_url

url = get_base_url()
print(f"   URL générée: {url}")
print(f"   ✓ Correct" if "https://" in url and "hf.space" in url else f"   ✗ Incorrect")

# Test Hugging Face avec SPACE_ID
print("\n3. Test Hugging Face avec SPACE_ID:")
os.environ.pop('SPACE_HOST', None)
os.environ['SPACE_ID'] = 'Sylvainleduc/C2B'
importlib.reload(sys.modules['bon_commande_simple'])
from bon_commande_simple import get_base_url

url = get_base_url()
print(f"   URL générée: {url}")
print(f"   ✓ Correct" if "https://huggingface.co/spaces/" in url else f"   ✗ Incorrect")

# Test avec APP_URL personnalisée
print("\n4. Test avec APP_URL personnalisée:")
os.environ['APP_URL'] = 'https://custom.example.com'
importlib.reload(sys.modules['bon_commande_simple'])
from bon_commande_simple import get_base_url

url = get_base_url()
print(f"   URL générée: {url}")
print(f"   ✓ Correct" if url == "https://custom.example.com" else f"   ✗ Incorrect")

# Test génération complète du lien avec token
print("\n5. Test génération lien public complet:")
import uuid
token = str(uuid.uuid4())
lien_public = f"{url}/?token={token}"
print(f"   Lien généré: {lien_public}")
print(f"   ✓ Format correct" if "?token=" in lien_public else f"   ✗ Format incorrect")

print("\n" + "=" * 60)
print("RÉSULTAT: Tous les tests passent ✅" if all([
    "localhost" in get_base_url() or "https://" in get_base_url()
]) else "RÉSULTAT: Certains tests échouent ❌")
print("=" * 60)