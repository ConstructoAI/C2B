#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour vérifier les doublons d'ID dans la base de données fournisseurs
"""

import sqlite3
import os
import sys
import io

# Configurer l'encodage pour Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Déterminer le chemin de la base de données
if os.getenv('SPACE_ID'):  # Hugging Face
    db_path = '/data/app_data/fournisseurs.db'
else:
    db_path = 'data/fournisseurs.db'

print(f"Vérification de la base de données: {db_path}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Vérifier les doublons d'ID
    cursor.execute("""
        SELECT id, COUNT(*) as count
        FROM fournisseurs
        GROUP BY id
        HAVING COUNT(*) > 1
    """)

    duplicates = cursor.fetchall()

    if duplicates:
        print("\n⚠️ DOUBLONS D'ID TROUVÉS:")
        for id_val, count in duplicates:
            print(f"  ID {id_val}: {count} occurrences")

            # Afficher les détails
            cursor.execute("SELECT id, nom FROM fournisseurs WHERE id = ?", (id_val,))
            details = cursor.fetchall()
            for detail in details:
                print(f"    - {detail}")
    else:
        print("\n✅ Aucun doublon d'ID trouvé")

    # Afficher tous les fournisseurs avec leurs IDs
    print("\n📋 Liste de tous les fournisseurs:")
    cursor.execute("SELECT id, nom FROM fournisseurs ORDER BY id")
    all_fournisseurs = cursor.fetchall()

    for id_val, nom in all_fournisseurs:
        print(f"  ID {id_val}: {nom}")

    conn.close()
else:
    print(f"❌ Base de données non trouvée: {db_path}")