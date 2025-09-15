#!/usr/bin/env python3
"""
Script de correction des numéros de soumission en doublon
Corrige les conflits entre Heritage et Multi-format
"""

import sqlite3
import os
from datetime import datetime
import sys

def find_duplicates():
    """Trouve tous les numéros en doublon entre les bases"""
    all_numbers = {}
    duplicates = []

    # 1. Collecter depuis Heritage
    if os.path.exists('data/soumissions_heritage.db'):
        try:
            conn = sqlite3.connect('data/soumissions_heritage.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, numero, client_nom, created_at FROM soumissions_heritage ORDER BY created_at')
            for row in cursor.fetchall():
                if row[1]:  # Si le numéro existe
                    if row[1] in all_numbers:
                        duplicates.append({
                            'numero': row[1],
                            'source1': all_numbers[row[1]],
                            'source2': {'type': 'heritage', 'id': row[0], 'client': row[2], 'date': row[3]}
                        })
                    else:
                        all_numbers[row[1]] = {'type': 'heritage', 'id': row[0], 'client': row[2], 'date': row[3]}
            conn.close()
        except Exception as e:
            print(f"Erreur lecture Heritage: {e}")

    # 2. Collecter depuis Multi
    if os.path.exists('data/soumissions_multi.db'):
        try:
            conn = sqlite3.connect('data/soumissions_multi.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, numero_soumission, nom_client, date_creation FROM soumissions ORDER BY date_creation')
            for row in cursor.fetchall():
                if row[1]:  # Si le numéro existe
                    if row[1] in all_numbers:
                        duplicates.append({
                            'numero': row[1],
                            'source1': all_numbers[row[1]],
                            'source2': {'type': 'multi', 'id': row[0], 'client': row[2], 'date': row[3]}
                        })
                    else:
                        all_numbers[row[1]] = {'type': 'multi', 'id': row[0], 'client': row[2], 'date': row[3]}
            conn.close()
        except Exception as e:
            print(f"Erreur lecture Multi: {e}")

    return duplicates, all_numbers

def get_next_available_number(all_numbers, year):
    """Trouve le prochain numéro disponible pour une année"""
    max_num = 0
    for numero in all_numbers.keys():
        if numero.startswith(f"{year}-"):
            try:
                num = int(numero.split('-')[1])
                max_num = max(max_num, num)
            except:
                pass
    return f"{year}-{max_num + 1:03d}"

def fix_duplicates(duplicates, all_numbers, auto_fix=False):
    """Corrige les numéros en doublon"""
    fixed_count = 0

    for dup in duplicates:
        print(f"\nDoublon detecte: {dup['numero']}")
        print(f"   1. {dup['source1']['type'].upper()}: ID={dup['source1']['id']}, Client={dup['source1']['client']}, Date={dup['source1']['date']}")
        print(f"   2. {dup['source2']['type'].upper()}: ID={dup['source2']['id']}, Client={dup['source2']['client']}, Date={dup['source2']['date']}")

        # Déterminer lequel garder (le plus ancien par défaut)
        if dup['source1']['date'] and dup['source2']['date']:
            if dup['source1']['date'] <= dup['source2']['date']:
                keep = dup['source1']
                change = dup['source2']
            else:
                keep = dup['source2']
                change = dup['source1']
        else:
            # Si pas de date, garder Heritage par défaut
            if dup['source1']['type'] == 'heritage':
                keep = dup['source1']
                change = dup['source2']
            else:
                keep = dup['source2']
                change = dup['source1']

        print(f"   -> Garder: {keep['type'].upper()} (ID={keep['id']})")
        print(f"   -> Changer: {change['type'].upper()} (ID={change['id']})")

        if not auto_fix:
            response = input("   Corriger? (o/n/q pour quitter): ").lower()
            if response == 'q':
                break
            if response != 'o':
                continue

        # Générer un nouveau numéro
        year = datetime.now().year
        new_numero = get_next_available_number(all_numbers, year)
        all_numbers[new_numero] = change  # Ajouter le nouveau numéro à la liste

        # Appliquer la correction
        try:
            if change['type'] == 'heritage':
                conn = sqlite3.connect('data/soumissions_heritage.db')
                cursor = conn.cursor()
                cursor.execute('UPDATE soumissions_heritage SET numero = ? WHERE id = ?', (new_numero, change['id']))
                conn.commit()
                conn.close()
            else:  # multi
                conn = sqlite3.connect('data/soumissions_multi.db')
                cursor = conn.cursor()
                cursor.execute('UPDATE soumissions SET numero_soumission = ? WHERE id = ?', (new_numero, change['id']))
                conn.commit()
                conn.close()

            print(f"   OK Corrige: {dup['numero']} -> {new_numero}")
            fixed_count += 1
        except Exception as e:
            print(f"   ERREUR: {e}")

    return fixed_count

def verify_uniqueness():
    """Vérifie qu'il n'y a plus de doublons"""
    duplicates, _ = find_duplicates()
    if not duplicates:
        print("OK: Aucun doublon detecte - Tous les numeros sont uniques!")
        return True
    else:
        print(f"ATTENTION: {len(duplicates)} doublon(s) encore present(s)")
        return False

def main():
    print("=" * 60)
    print("CORRECTION DES NUMEROS DE SOUMISSION EN DOUBLON")
    print("=" * 60)

    # Vérifier si numero_manager existe
    if os.path.exists('numero_manager.py'):
        print("OK: Module numero_manager.py detecte")
        print("   Les futures soumissions utiliseront la numérotation unifiée")
    else:
        print("ATTENTION: Module numero_manager.py non trouve")
        print("   Risque de nouveaux doublons!")

    print("\nAnalyse des bases de donnees...")

    # Trouver les doublons
    duplicates, all_numbers = find_duplicates()

    print(f"\nStatistiques:")
    print(f"   Total de numéros: {len(all_numbers)}")
    print(f"   Doublons trouvés: {len(duplicates)}")

    if not duplicates:
        print("\nOK: Aucun doublon detecte!")
        return

    print("\nATTENTION: Des doublons ont ete detectes!")

    # Demander le mode de correction
    print("\nOptions:")
    print("1. Correction interactive (recommandé)")
    print("2. Correction automatique (garde le plus ancien)")
    print("3. Afficher seulement (ne rien changer)")
    print("4. Quitter")

    choice = input("\nVotre choix (1-4): ")

    if choice == '1':
        fixed = fix_duplicates(duplicates, all_numbers, auto_fix=False)
        print(f"\nOK: {fixed} numero(s) corrige(s)")
    elif choice == '2':
        print("\nCorrection automatique en cours...")
        fixed = fix_duplicates(duplicates, all_numbers, auto_fix=True)
        print(f"\nOK: {fixed} numero(s) corrige(s) automatiquement")
    elif choice == '3':
        for dup in duplicates:
            print(f"\nDoublon: {dup['numero']}")
            print(f"  - {dup['source1']['type']}: {dup['source1']['client']}")
            print(f"  - {dup['source2']['type']}: {dup['source2']['client']}")
    else:
        print("Annulé.")
        return

    # Vérification finale
    if choice in ['1', '2']:
        print("\nVerification finale...")
        verify_uniqueness()

if __name__ == "__main__":
    main()