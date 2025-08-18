import sqlite3
import os
from config_approbation import *

# Test database connection and tables
conn = sqlite3.connect(os.path.join(os.getenv('DATA_DIR', os.path.join(os.getcwd(), 'data')), DATABASE_FILE))
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print(f"All tables: {sorted(tables)}")

required_tables = ['entreprises_clientes', 'entreprises_prestataires', 'demandes_devis', 'soumissions']
missing = [t for t in required_tables if t not in tables]

print(f"Required tables present: {len(missing) == 0}")
if missing:
    print(f"Missing: {missing}")

# Test specific query that was failing
try:
    cursor.execute('SELECT COUNT(*) FROM demandes_devis')
    count = cursor.fetchone()[0]
    print(f"demandes_devis table working: {count} rows")
except Exception as e:
    print(f"Error with demandes_devis: {e}")

conn.close()
print("Database verification complete!")