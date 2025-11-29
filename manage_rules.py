"""
Rule Manager - File khusus untuk mengelola Rule Patterns
Gunakan file ini untuk menambah, melihat, dan menghapus rule patterns
"""

from app.database import Database
from app.inference_engine import ForwardChaining
from tabulate import tabulate

class RuleManager:
    def __init__(self):
        self.db = Database()
        self.fc = ForwardChaining()

    def lihat_semua_penyakit(self):
        """Menampilkan daftar semua penyakit yang tersedia"""
        self.db.connect()
        query = "SELECT * FROM penyakit ORDER BY kode_penyakit"
        penyakit_list = self.db.fetch_all(query)
        self.db.close()
        
        print("\n" + "="*80)
        print("DAFTAR PENYAKIT YANG TERSEDIA")
        print("="*80)

        table_data = []
        for p in penyakit_list:
            table_data.append([
                p['id'],
                p['kode_penyakit'],
                p['nama_penyakit']
            ])

        print(tabulate(table_data, headers=['ID', 'Kode', 'Nama Penyakit'], tablefmt='grid'))
        return penyakit_list

    def lihat_semua_gejala(self):
        """Menampilkan daftar semua gejala yang tersedia"""
        gejala_list = self.fc.get_all_gejala()

        print("\n" + "="*80)
        print("DAFTAR GEJALA YANG TERSEDIA")
        print("="*80)

        table_data = []
        for g in gejala_list:
            table_data.append([
                g['id'],
                g['kode_gejala'],
                g['nama_gejala']
            ])

        print(tabulate(table_data, headers=['ID', 'Kode', 'Nama Gejala'], tablefmt='grid'))
        return gejala_list

    def lihat_semua_rule(self):
        """Menampilkan semua rule patterns yang ada"""
        rules_list = self.fc.get_all_rules()

        print("\n" + "="*80)
        print("DAFTAR SEMUA RULE PATTERNS")
        print("="*80)
        print(f"Total Rule: {len(rules_list)}\n")

        for rule in rules_list:
            print(f"+-- {rule['kode_rule']}: {rule['nama_rule']}")
            print(f"|   Penyakit: {rule['kode_penyakit']} - {rule['nama_penyakit']}")
            print(f"|   IF User memiliki gejala:")

            gejala_codes = rule['gejala_codes'].split(', ')
            gejala_names = rule['gejala_names'].split(' + ')

            for i in range(len(gejala_codes)):
                print(f"|      - {gejala_codes[i]}: {gejala_names[i]}")

            if rule['referensi']:
                print(f"|   Referensi: {rule['referensi']}")
            print(f"+-- THEN: Diagnosis -> {rule['nama_penyakit']}")
            print()

        return rules_list

    def tambah_rule(self, kode_rule, penyakit_id, nama_rule, gejala_ids, referensi=None):
        """
        Menambah rule pattern baru

        Args:
            kode_rule (str): Kode unik rule (misal: R016)
            penyakit_id (int): ID penyakit
            nama_rule (str): Nama/deskripsi rule
            gejala_ids (list): List ID gejala [1, 2, 3]
            referensi (str): Referensi jurnal (opsional)

        Returns:
            int: ID rule yang baru dibuat atau None jika gagal
        """
        # Validasi
        if not kode_rule or not penyakit_id or not nama_rule or not gejala_ids:
            print("[ERROR] Semua parameter wajib harus diisi!")
            return None

        if len(gejala_ids) < 2:
            print("[ERROR] Minimal 2 gejala harus dipilih!")
            return None
        
        self.db.connect()
        # Cek apakah kode rule sudah ada
        check = self.db.fetch_one("SELECT id FROM rule_patterns WHERE kode_rule = %s", (kode_rule,))
        if check:
            print(f"[ERROR] Kode rule '{kode_rule}' sudah digunakan!")
            self.db.close()
            return None
        self.db.close()
        # Tambah rule
        rule_id = self.fc.add_rule(
            kode_rule=kode_rule,
            penyakit_id=penyakit_id,
            nama_rule=nama_rule,
            gejala_ids=gejala_ids,
            referensi=referensi
        )

        if rule_id:
            print(f"[OK] Rule {kode_rule} berhasil ditambahkan! (ID: {rule_id})")
            print(f"     IF User memiliki gejala: {gejala_ids}")
            print(f"     THEN Diagnosis: Penyakit ID {penyakit_id}")
            return rule_id
        else:
            print("[ERROR] Gagal menambahkan rule!")
            return None

    def hapus_rule(self, rule_id):
        """
        Menghapus rule berdasarkan ID

        Args:
            rule_id (int): ID rule yang akan dihapus

        Returns:
            bool: True jika berhasil
        """
        self.db.connect()
        # Ambil info rule dulu
        rule_info = self.db.fetch_one("SELECT kode_rule, nama_rule FROM rule_patterns WHERE id = %s", (rule_id,))

        if not rule_info:
            print(f"[ERROR] Rule dengan ID {rule_id} tidak ditemukan!")
            self.db.close()
            return False
        
        self.db.close()
        # Hapus
        success = self.fc.delete_rule(rule_id)

        if success:
            print(f"[OK] Rule {rule_info['kode_rule']} berhasil dihapus!")
            print(f"     Nama: {rule_info['nama_rule']}")
            return True
        else:
            print("[ERROR] Gagal menghapus rule!")
            return False

    def cari_rule_by_kode(self, kode_rule):
        """Mencari rule berdasarkan kode"""
        self.db.connect()
        rule = self.db.fetch_one("""
            SELECT
                rp.*,
                p.kode_penyakit,
                p.nama_penyakit
            FROM rule_patterns rp
            JOIN penyakit p ON rp.penyakit_id = p.id
            WHERE rp.kode_rule = %s
        """, (kode_rule,))

        if not rule:
            print(f"[ERROR] Rule dengan kode '{kode_rule}' tidak ditemukan!")
            self.db.close()
            return None

        # Ambil gejala
        gejala = self.db.fetch_all("""
            SELECT g.kode_gejala, g.nama_gejala
            FROM rule_details rd
            JOIN gejala g ON rd.kode_gejala = g.kode_gejala
            WHERE rd.kode_rule = %s
        """, (rule['kode_rule'],))
        
        self.db.close()
        print(f"\n+-- {rule['kode_rule']}: {rule['nama_rule']}")
        print(f"|   ID: {rule['id']}")
        print(f"|   Penyakit: {rule['kode_penyakit']} - {rule['nama_penyakit']}")
        print(f"|   Gejala:")
        for g in gejala:
            print(f"|      - {g['kode_gejala']}: {g['nama_gejala']}")
        if rule['referensi']:
            print(f"|   Referensi: {rule['referensi']}")
        print(f"+-- THEN: Diagnosis -> {rule['nama_penyakit']}\n")

        return rule

    def close(self):
        """Tutup koneksi database"""
        self.fc.close()
        self.db.close()


def menu_interaktif():
    """Menu interaktif untuk mengelola rule"""
    rm = RuleManager()

    while True:
        print("\n" + "="*80)
        print("RULE MANAGER - SISTEM PAKAR PENYAKIT LAMBUNG")
        print("="*80)
        print("1. Lihat Semua Rule")
        print("2. Lihat Daftar Penyakit")
        print("3. Lihat Daftar Gejala")
        print("4. Tambah Rule Baru")
        print("5. Hapus Rule")
        print("6. Cari Rule by Kode")
        print("0. Keluar")
        print("="*80)

        pilihan = input("Pilih menu (0-6): ").strip()

        if pilihan == '1':
            rm.lihat_semua_rule()
            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '2':
            rm.lihat_semua_penyakit()
            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '3':
            rm.lihat_semua_gejala()
            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '4':
            print("\n" + "="*80)
            print("TAMBAH RULE BARU")
            print("="*80)

            # Input kode rule
            kode_rule = input("Kode Rule (misal: R016): ").strip().upper()

            # Lihat penyakit
            penyakit_list = rm.lihat_semua_penyakit()
            penyakit_input = input("\nMasukkan ID atau Kode Penyakit (misal: 1 atau P001): ").strip().upper()

            # Cek apakah input adalah kode (P001) atau ID (1)
            penyakit_id = None
            if penyakit_input.startswith('P'):
                # Cari berdasarkan kode
                for p in penyakit_list:
                    if p['kode_penyakit'] == penyakit_input:
                        penyakit_id = p['id']
                        break
                if not penyakit_id:
                    print(f"[ERROR] Kode penyakit '{penyakit_input}' tidak ditemukan!")
                    input("\nTekan Enter untuk lanjut...")
                    continue
            else:
                # Input adalah ID
                try:
                    penyakit_id = int(penyakit_input)
                except ValueError:
                    print(f"[ERROR] Input '{penyakit_input}' tidak valid! Masukkan ID angka atau kode (P001)")
                    input("\nTekan Enter untuk lanjut...")
                    continue

            # Input nama rule
            nama_rule = input("Nama/Deskripsi Rule: ").strip()

            # Lihat gejala
            rm.lihat_semua_gejala()
            gejala_input = input("\nMasukkan ID Gejala (pisahkan dengan koma, misal: 1,2,5): ").strip()
            gejala_ids = [int(g.strip()) for g in gejala_input.split(',')]

            # Referensi (opsional)
            referensi = input("Referensi Jurnal (opsional, Enter untuk skip): ").strip()

            # Konfirmasi
            print("\n--- KONFIRMASI ---")
            print(f"Kode Rule: {kode_rule}")
            print(f"Penyakit ID: {penyakit_id}")
            print(f"Nama Rule: {nama_rule}")
            print(f"Gejala IDs: {gejala_ids}")
            print(f"Referensi: {referensi if referensi else '-'}")

            konfirm = input("\nTambahkan rule ini? (y/n): ").strip().lower()
            if konfirm == 'y':
                rm.tambah_rule(
                    kode_rule=kode_rule,
                    penyakit_id=penyakit_id,  # Already converted to int above
                    nama_rule=nama_rule,
                    gejala_ids=gejala_ids,
                    referensi=referensi if referensi else None
                )
            else:
                print("[BATAL] Tidak jadi menambahkan rule.")

            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '5':
            print("\n" + "="*80)
            print("HAPUS RULE")
            print("="*80)

            # Lihat semua rule dulu
            rm.lihat_semua_rule()

            rule_id = input("Masukkan ID Rule yang akan dihapus: ").strip()

            konfirm = input(f"Hapus rule ID {rule_id}? (y/n): ").strip().lower()
            if konfirm == 'y':
                rm.hapus_rule(int(rule_id))
            else:
                print("[BATAL] Tidak jadi menghapus rule.")

            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '6':
            print("\n" + "="*80)
            print("CARI RULE")
            print("="*80)

            kode_rule = input("Masukkan Kode Rule (misal: R001): ").strip().upper()
            rm.cari_rule_by_kode(kode_rule)

            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '0':
            print("\nTerima kasih! Keluar dari Rule Manager.")
            rm.close()
            break

        else:
            print("[ERROR] Pilihan tidak valid!")
            input("\nTekan Enter untuk lanjut...")


# ============================================
# CONTOH PENGGUNAAN LANGSUNG DI KODE
# ============================================

def contoh_tambah_rule():
    """Contoh menambah rule langsung via kode"""
    rm = RuleManager()

    # Tambah rule R016: Gastritis Kronis Berat
    rm.tambah_rule(
        kode_rule='R016',
        penyakit_id=1,  # Gastritis
        nama_rule='Gastritis Kronis Berat',
        gejala_ids=[1, 2, 10, 18],  # G001, G002, G010, G018
        referensi='Contoh Jurnal ABC (2024)'
    )

    # Tambah rule R017: GERD dengan Batuk Kronis
    rm.tambah_rule(
        kode_rule='R017',
        penyakit_id=2,  # GERD
        nama_rule='GERD dengan Batuk Kronis dan Suara Serak',
        gejala_ids=[6, 22, 23],  # G006, G022, G023
        referensi='Gastroenterology Journal (2024)'
    )

    rm.close()


if __name__ == '__main__':
    # Jalankan menu interaktif
    menu_interaktif()
