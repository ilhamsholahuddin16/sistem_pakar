"""
Script untuk setup database sistem pakar
Membuat tabel dan mengisi data awal
"""

import mysql.connector
from mysql.connector import Error

# Konfigurasi database
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'isganteng16'
}

def run_sql_file(cursor, filepath):
    """Menjalankan file SQL"""
    print(f"\nMenjalankan: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Remove comments
    lines = sql_content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip comment lines
        if line.strip().startswith('--'):
            continue
        cleaned_lines.append(line)

    sql_content = '\n'.join(cleaned_lines)

    # Split berdasarkan semicolon
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]

    executed = 0
    for statement in statements:
        # Skip empty dan CREATE DATABASE
        if not statement or statement.strip().upper().startswith('CREATE DATABASE') or statement.strip().upper().startswith('USE'):
            continue

        try:
            cursor.execute(statement)
            executed += 1
            if executed % 5 == 0:
                print(".", end="", flush=True)
        except Error as e:
            # Skip error untuk DROP TABLE
            if 'unknown table' not in str(e).lower() and 'doesn\'t exist' not in str(e).lower():
                print(f"\n[WARNING] {e}")

    print(f" [OK] ({executed} statements)")

def main():
    try:
        print("="*80)
        print("SETUP DATABASE SISTEM PAKAR PENYAKIT LAMBUNG")
        print("="*80)

        # Koneksi ke MySQL
        print("\n[1] Koneksi ke MySQL...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print("    [OK] Terhubung ke MySQL")

        # Buat database
        print("\n[2] Membuat database sistem_pakar_lambung...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS sistem_pakar_lambung")
        print("    [OK] Database dibuat")

        # Gunakan database
        cursor.execute("USE sistem_pakar_lambung")

        # Jalankan schema.sql
        print("\n[3] Membuat tabel dari schema.sql...")
        run_sql_file(cursor, 'database/schema.sql')
        connection.commit()
        print("    [OK] Tabel berhasil dibuat")

        # Jalankan seed_data.sql
        print("\n[4] Mengisi data dari seed_data.sql...")
        run_sql_file(cursor, 'database/seed_data.sql')
        connection.commit()
        print("    [OK] Data berhasil diisi")

        # Cek hasil
        print("\n[5] Verifikasi data...")
        cursor.execute("SELECT COUNT(*) as total FROM penyakit")
        result = cursor.fetchone()
        print(f"    - Jumlah penyakit: {result[0]}")

        cursor.execute("SELECT COUNT(*) as total FROM gejala")
        result = cursor.fetchone()
        print(f"    - Jumlah gejala: {result[0]}")

        cursor.execute("SELECT COUNT(*) as total FROM rule_patterns")
        result = cursor.fetchone()
        print(f"    - Jumlah rule patterns: {result[0]}")

        print("\n" + "="*80)
        print("[OK] SETUP DATABASE BERHASIL!")
        print("="*80)
        print("\nDatabase siap digunakan!")
        print("Jalankan: python test_rule_manager.py")

    except Error as e:
        print(f"\n[ERROR] {e}")
        return False

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nKoneksi database ditutup.")

    return True

if __name__ == '__main__':
    main()
