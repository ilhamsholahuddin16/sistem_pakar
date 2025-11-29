import mysql.connector
from mysql.connector import Error
from config import Config

class Database:
    def __init__(self):
        self.host = Config.DB_HOST
        self.user = Config.DB_USER
        self.password = Config.DB_PASSWORD
        self.database = Config.DB_NAME
        self.connection = None

    def connect(self):
        """Membuat koneksi ke database MySQL"""
        if self.connection and self.connection.is_connected():
            return self.connection
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.connection.autocommit = False # Important for transactions
            if self.connection.is_connected():
                return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def execute_query(self, query, params=None):
        """Eksekusi query INSERT, UPDATE, DELETE tanpa auto-commit"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            # self.connection.commit() # Dihapus untuk kontrol transaksi manual
            return cursor.lastrowid
        except Error as e:
            print(f"Error executing query: {e}")
            self.rollback() # Rollback jika ada error
            return None

    def commit(self):
        """Commit transaksi saat ini"""
        if self.connection and self.connection.is_connected():
            self.connection.commit()

    def rollback(self):
        """Rollback transaksi saat ini"""
        if self.connection and self.connection.is_connected():
            self.connection.rollback()
            
    def fetch_all(self, query, params=None):
        """Fetch multiple rows"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching data: {e}")
            return []

    def fetch_one(self, query, params=None):
        """Fetch single row"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching data: {e}")
            return None

    def close(self):
        """Tutup koneksi database"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def get_all_rules(self):
        """Mengambil semua detail aturan dengan informasi penyakit dan gejala"""
        query = """
            SELECT
                rd.id,
                rp.kode_rule,
                rp.nama_rule,
                rp.referensi,
                p.kode_penyakit,
                p.nama_penyakit,
                g.kode_gejala,
                g.nama_gejala
            FROM rule_details rd
            JOIN rule_patterns rp ON rd.kode_rule = rp.kode_rule
            JOIN gejala g ON rd.kode_gejala = g.kode_gejala
            JOIN penyakit p ON rp.penyakit_id = p.id
            ORDER BY rp.kode_rule, g.kode_gejala
        """
        return self.fetch_all(query)

    def add_rule(self, id_penyakit, id_gejala):
        """Fungsi ini dinonaktifkan karena skema aturan yang kompleks."""
        # TODO: Implementasi logika untuk menambah aturan pada skema rule_patterns
        return False

    def delete_rule(self, rule_detail_id):
        """Menghapus satu gejala dari sebuah aturan (rule_details) berdasarkan ID-nya"""
        query = "DELETE FROM rule_details WHERE id = %s"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (rule_detail_id,))
            self.commit()
            return cursor.rowcount > 0 # Return True jika ada baris yang terhapus
        except Error as e:
            print(f"Error deleting rule detail: {e}")
            self.rollback()
            return False
