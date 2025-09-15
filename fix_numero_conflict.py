#!/usr/bin/env python3
"""
Script pour corriger les conflits de numérotation entre les bases de données
Renumérote les soumissions pour garantir l'unicité
"""

import sqlite3
import os
from datetime import datetime
import json

def fix_numero_conflicts():
    """Corrige les conflits de numérotation entre les bases"""

    # Déterminer le répertoire de données
    DATA_DIR = os.getenv('DATA_DIR', 'data')

    print(f"Analyse des conflits de numérotation dans {DATA_DIR}...")

    current_year = datetime.now().year
    all_numbers = []

    # 1. Collecter tous les numéros existants
    print("\n1. Collecte des numéros existants...")

    # Heritage
    heritage_db = os.path.join(DATA_DIR, 'soumissions_heritage.db')
    if os.path.exists(heritage_db):
        conn = sqlite3.connect(heritage_db)
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, numero FROM soumissions_heritage WHERE numero LIKE '{current_year}-%' ORDER BY numero")
        heritage_records = cursor.fetchall()
        conn.close()
        print(f"   - Heritage: {len(heritage_records)} soumissions")
        for record in heritage_records:
            all_numbers.append(('heritage', record[0], record[1]))

    # Multi
    multi_db = os.path.join(DATA_DIR, 'soumissions_multi.db')
    if os.path.exists(multi_db):
        conn = sqlite3.connect(multi_db)
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, numero_soumission FROM soumissions WHERE numero_soumission LIKE '{current_year}-%' ORDER BY numero_soumission")
        multi_records = cursor.fetchall()
        conn.close()
        print(f"   - Multi: {len(multi_records)} soumissions")
        for record in multi_records:
            all_numbers.append(('multi', record[0], record[1]))

    # 2. Détecter les doublons
    print("\n2. Détection des doublons...")
    numbers_only = [num[2] for num in all_numbers]
    duplicates = set([x for x in numbers_only if numbers_only.count(x) > 1])

    if not duplicates:
        print("   ✅ Aucun doublon détecté!")
        return

    print(f"   ⚠️ {len(duplicates)} numéro(s) en double détecté(s): {duplicates}")

    # 3. Corriger les doublons
    print("\n3. Correction des doublons...")

    # Trouver le prochain numéro disponible
    max_num = 0
    for num in numbers_only:
        try:
            num_part = int(num.split('-')[1])
            max_num = max(max_num, num_part)
        except:
            pass

    next_available = max_num + 1

    # Renommer les doublons (garder le premier, renommer les suivants)
    seen = set()
    for db_type, record_id, numero in all_numbers:
        if numero in duplicates:
            if numero in seen:
                # C'est un doublon, le renommer
                new_numero = f"{current_year}-{next_available:03d}"
                print(f"   - Renommage {numero} -> {new_numero} dans {db_type} (ID: {record_id})")

                if db_type == 'heritage':
                    conn = sqlite3.connect(heritage_db)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE soumissions_heritage SET numero = ? WHERE id = ?", (new_numero, record_id))
                    conn.commit()
                    conn.close()
                elif db_type == 'multi':
                    conn = sqlite3.connect(multi_db)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE soumissions SET numero_soumission = ? WHERE id = ?", (new_numero, record_id))
                    conn.commit()
                    conn.close()

                next_available += 1
            else:
                seen.add(numero)

    print("\n✅ Correction terminée!")

    # 4. Vérification finale
    print("\n4. Vérification finale...")
    all_numbers_after = []

    if os.path.exists(heritage_db):
        conn = sqlite3.connect(heritage_db)
        cursor = conn.cursor()
        cursor.execute(f"SELECT numero FROM soumissions_heritage WHERE numero LIKE '{current_year}-%'")
        for row in cursor.fetchall():
            all_numbers_after.append(row[0])
        conn.close()

    if os.path.exists(multi_db):
        conn = sqlite3.connect(multi_db)
        cursor = conn.cursor()
        cursor.execute(f"SELECT numero_soumission FROM soumissions WHERE numero_soumission LIKE '{current_year}-%'")
        for row in cursor.fetchall():
            all_numbers_after.append(row[0])
        conn.close()

    duplicates_after = set([x for x in all_numbers_after if all_numbers_after.count(x) > 1])

    if duplicates_after:
        print(f"   ⚠️ Il reste des doublons: {duplicates_after}")
    else:
        print(f"   ✅ Tous les numéros sont maintenant uniques! Total: {len(all_numbers_after)} soumissions")

if __name__ == "__main__":
    fix_numero_conflicts()