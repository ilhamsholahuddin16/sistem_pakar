"""
History Manager - Mengelola penyimpanan dan pengambilan riwayat konsultasi
"""

from datetime import datetime
from app.database import Database

class HistoryManager:
    def __init__(self):
        self.db = Database()

    def save_consultation(self, nama_user, gejala_terpilih, diagnosis_result):
        """
        Menyimpan hasil konsultasi ke database

        Args:
            nama_user: nama user yang melakukan konsultasi
            gejala_terpilih: list of dict gejala yang dipilih
            diagnosis_result: dict hasil diagnosis (dari pattern matching)

        Returns:
            int: ID riwayat konsultasi yang baru disimpan
        """
        if not diagnosis_result:
            return None
        
        try:
            self.db.connect()
            # Insert ke tabel riwayat_konsultasi
            insert_riwayat = """
                INSERT INTO riwayat_konsultasi
                (nama_user, penyakit_id, rule_matched, match_percentage, jumlah_gejala)
                VALUES (%s, %s, %s, %s, %s)
            """

            riwayat_id = self.db.execute_query(insert_riwayat, (
                nama_user,
                diagnosis_result['penyakit_id'],
                diagnosis_result['kode_rule'],
                diagnosis_result['persentase_match'],
                len(gejala_terpilih)
            ))

            if not riwayat_id:
                raise Exception("Gagal menyimpan riwayat konsultasi.")

            # Insert detail gejala yang dipilih
            for gejala in gejala_terpilih:
                insert_detail = """
                    INSERT INTO detail_riwayat (riwayat_id, gejala_id)
                    VALUES (%s, %s)
                """
                detail_id = self.db.execute_query(insert_detail, (riwayat_id, gejala['id']))
                if not detail_id:
                    raise Exception("Gagal menyimpan detail riwayat.")

            self.db.commit()
            return riwayat_id

        except Exception as e:
            print(f"Error saving consultation: {e}")
            self.db.rollback()
            return None
        finally:
            self.db.close()

    def get_user_history(self, nama_user, limit=10):
        """
        Mengambil riwayat konsultasi user

        Args:
            nama_user: nama user
            limit: jumlah maksimal riwayat yang diambil

        Returns:
            list of dict riwayat konsultasi
        """
        try:
            self.db.connect()
            query = """
                SELECT
                    rk.id,
                    rk.tanggal_konsultasi,
                    rk.rule_matched,
                    rk.match_percentage,
                    rk.jumlah_gejala,
                    p.kode_penyakit,
                    p.nama_penyakit,
                    p.deskripsi,
                    p.solusi
                FROM riwayat_konsultasi rk
                LEFT JOIN penyakit p ON rk.penyakit_id = p.id
                WHERE rk.nama_user = %s
                ORDER BY rk.tanggal_konsultasi DESC
                LIMIT %s
            """
            history = self.db.fetch_all(query, (nama_user, limit))
            return history
        except Exception as e:
            print(f"Error getting user history: {e}")
            return []
        finally:
            self.db.close()

    def get_consultation_detail(self, riwayat_id):
        """
        Mengambil detail lengkap dari satu konsultasi

        Args:
            riwayat_id: ID riwayat konsultasi

        Returns:
            dict dengan info lengkap konsultasi
        """
        try:
            self.db.connect()
            # Ambil info utama
            query_main = """
                SELECT
                    rk.*,
                    p.kode_penyakit,
                    p.nama_penyakit,
                    p.deskripsi,
                    p.solusi
                FROM riwayat_konsultasi rk
                LEFT JOIN penyakit p ON rk.penyakit_id = p.id
                WHERE rk.id = %s
            """
            consultation = self.db.fetch_one(query_main, (riwayat_id,))

            if not consultation:
                return None

            # Ambil gejala yang dipilih
            query_gejala = """
                SELECT
                    g.id,
                    g.kode_gejala,
                    g.nama_gejala
                FROM detail_riwayat dr
                JOIN gejala g ON dr.gejala_id = g.id
                WHERE dr.riwayat_id = %s
                ORDER BY g.kode_gejala
            """
            gejala_list = self.db.fetch_all(query_gejala, (riwayat_id,))

            return {
                'consultation': consultation,
                'gejala_terpilih': gejala_list
            }
        except Exception as e:
            print(f"Error getting consultation detail: {e}")
            return None
        finally:
            self.db.close()
    def get_all_history(self, limit=50):
        """
        Mengambil semua riwayat konsultasi (untuk admin/statistik)

        Args:
            limit: jumlah maksimal riwayat

        Returns:
            list of dict riwayat konsultasi
        """
        try:
            self.db.connect()
            query = """
                SELECT
                    rk.id,
                    rk.nama_user,
                    rk.tanggal_konsultasi,
                    rk.rule_matched,
                    rk.match_percentage,
                    rk.jumlah_gejala,
                    p.kode_penyakit,
                    p.nama_penyakit
                FROM riwayat_konsultasi rk
                LEFT JOIN penyakit p ON rk.penyakit_id = p.id
                ORDER BY rk.tanggal_konsultasi DESC
                LIMIT %s
            """
            history = self.db.fetch_all(query, (limit,))
            return history
        except Exception as e:
            print(f"Error getting all history: {e}")
            return []
        finally:
            self.db.close()


    def get_statistics(self):
        """
        Mendapatkan statistik konsultasi

        Returns:
            dict dengan berbagai statistik
        """
        try:
            self.db.connect()
            # Total konsultasi
            total = self.db.fetch_one("SELECT COUNT(*) as total FROM riwayat_konsultasi")

            # Rata-rata match percentage
            avg_match = self.db.fetch_one("SELECT AVG(match_percentage) as rata_rata FROM riwayat_konsultasi")

            # Penyakit paling sering didiagnosis
            most_common = self.db.fetch_all("""
                SELECT
                    p.nama_penyakit,
                    COUNT(*) as jumlah
                FROM riwayat_konsultasi rk
                JOIN penyakit p ON rk.penyakit_id = p.id
                GROUP BY p.id
                ORDER BY jumlah DESC
                LIMIT 5
            """)

            # Rule paling sering match
            most_matched_rules = self.db.fetch_all("""
                SELECT
                    rule_matched,
                    COUNT(*) as jumlah
                FROM riwayat_konsultasi
                WHERE rule_matched IS NOT NULL
                GROUP BY rule_matched
                ORDER BY jumlah DESC
                LIMIT 5
            """)

            return {
                'total_konsultasi': total['total'] if total else 0,
                'rata_rata_match': round(avg_match['rata_rata'], 2) if avg_match and avg_match['rata_rata'] else 0,
                'penyakit_tersering': most_common,
                'rule_tersering': most_matched_rules
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
        finally:
            self.db.close()
            
    def delete_consultation(self, riwayat_id):
        """
        Menghapus riwayat konsultasi (cascade akan hapus detail_riwayat juga)

        Args:
            riwayat_id: ID riwayat yang akan dihapus

        Returns:
            bool: True jika berhasil
        """
        try:
            self.db.connect()
            query = "DELETE FROM riwayat_konsultasi WHERE id = %s"
            result = self.db.execute_query(query, (riwayat_id,))
            if result is not None:
                self.db.commit()
                return True
            else:
                self.db.rollback()
                return False
        except Exception as e:
            print(f"Error deleting consultation: {e}")
            self.db.rollback()
            return False
        finally:
            self.db.close()

    def close(self):
        """Tutup koneksi database"""
        self.db.close()
