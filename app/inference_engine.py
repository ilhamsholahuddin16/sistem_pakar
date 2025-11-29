from app.database import Database

class ForwardChaining:
    def __init__(self):
        self.db = Database()

    def diagnose(self, gejala_terpilih):
        """
        Melakukan diagnosis berdasarkan pattern matching dengan persentase

        Args:
            gejala_terpilih: list of dict [{'id': int}, ...]

        Returns:
            dict hasil diagnosis dengan persentase atau None
        """
        if not gejala_terpilih:
            return None

        self.db.connect()
        # Ambil semua gejala ID yang dipilih user
        user_gejala_ids = set([g['id'] for g in gejala_terpilih])

        # Ambil semua rule patterns dari database
        query_rules = """
            SELECT
                rp.id as rule_id,
                rp.kode_rule,
                rp.nama_rule,
                rp.referensi,
                rp.penyakit_id,
                p.kode_penyakit,
                p.nama_penyakit,
                p.deskripsi,
                p.solusi
            FROM rule_patterns rp
            JOIN penyakit p ON rp.penyakit_id = p.id
            ORDER BY rp.id
        """
        all_rules = self.db.fetch_all(query_rules)

        matched_rules = []

        # Cek setiap rule dan hitung persentase match
        for rule in all_rules:
            rule_id = rule['rule_id']

            # Ambil gejala-gejala dalam rule ini
            kode_rule = rule['kode_rule']
            query_details = """
                SELECT g.id as gejala_id
                FROM rule_details rd
                JOIN gejala g ON rd.kode_gejala = g.kode_gejala
                WHERE rd.kode_rule = %s
            """
            rule_gejala = self.db.fetch_all(query_details, (kode_rule,))
            rule_gejala_ids = set([rg['gejala_id'] for rg in rule_gejala])

            # Hitung berapa banyak gejala rule yang cocok dengan gejala user
            matched_gejala_ids = rule_gejala_ids.intersection(user_gejala_ids)
            jumlah_match = len(matched_gejala_ids)
            jumlah_gejala_rule = len(rule_gejala_ids)
            jumlah_gejala_user = len(user_gejala_ids)

            # PERHITUNGAN AKURASI HYBRID (2 METRIK):
            # 1. Completeness: Seberapa lengkap gejala rule terpenuhi
            if jumlah_gejala_rule > 0:
                completeness = (jumlah_match / jumlah_gejala_rule) * 100
            else:
                completeness = 0

            # 2. Relevance: Seberapa banyak gejala user yang dijelaskan oleh rule
            if jumlah_gejala_user > 0:
                relevance = (jumlah_match / jumlah_gejala_user) * 100
            else:
                relevance = 0

            # 3. Confidence Score (rata-rata weighted):
            # Bobot: 60% completeness + 40% relevance
            # Completeness lebih penting karena mengikuti pattern rule dari jurnal
            confidence_score = (0.6 * completeness) + (0.4 * relevance)

            # KRITERIA MATCHING (HYBRID):
            # 1. Minimal 2 gejala harus cocok (untuk rule dengan banyak gejala)
            # 2. ATAU minimal 40% confidence score
            # Ini lebih fleksibel untuk rule dengan 5-7 gejala dari jurnal
            min_gejala_cocok = 2
            min_confidence = 40

            cocok = (jumlah_match >= min_gejala_cocok) or (confidence_score >= min_confidence)

            if cocok:
                matched_rules.append({
                    'rule_id': rule_id,
                    'kode_rule': rule['kode_rule'],
                    'nama_rule': rule['nama_rule'],
                    'referensi': rule['referensi'],
                    'penyakit_id': rule['penyakit_id'],
                    'kode_penyakit': rule['kode_penyakit'],
                    'nama_penyakit': rule['nama_penyakit'],
                    'deskripsi': rule['deskripsi'],
                    'solusi': rule['solusi'],
                    'persentase_match': round(confidence_score, 1),  # Gunakan confidence score
                    'completeness': round(completeness, 1),
                    'relevance': round(relevance, 1),
                    'jumlah_gejala_rule': jumlah_gejala_rule,
                    'jumlah_gejala_match': jumlah_match,
                    'jumlah_gejala_user': jumlah_gejala_user,
                    'matched_gejala_ids': list(matched_gejala_ids) # Convert set to list
                })

        if not matched_rules:
            self.db.close()
            return None

        # STRATEGI PENGURUTAN UNTUK DIAGNOSIS MEDIS:
        # 1. Prioritas PERTAMA: Confidence score (akurasi hybrid)
        # 2. Prioritas KEDUA: Jumlah gejala yang cocok (lebih banyak = lebih baik)
        # Ini lebih masuk akal untuk rule dengan banyak gejala (5-7 gejala)
        matched_rules.sort(key=lambda x: (x['persentase_match'], x['jumlah_gejala_match']), reverse=True)

        best_match = matched_rules[0]

        # Ambil detail gejala yang cocok
        if best_match['matched_gejala_ids']:
            ids = tuple(best_match['matched_gejala_ids'])
            # Menggunakan format string untuk query IN
            query_gejala_cocok = f"SELECT * FROM gejala WHERE id IN ({','.join(['%s'] * len(ids))})"
            gejala_cocok = self.db.fetch_all(query_gejala_cocok, ids)
            best_match['gejala_cocok'] = gejala_cocok
        else:
            best_match['gejala_cocok'] = []
            
        self.db.close()
        # Return rule dengan persentase tertinggi
        return best_match

    def get_all_gejala(self):
        """Mengambil semua gejala yang tersedia"""
        self.db.connect()
        query = "SELECT * FROM gejala ORDER BY kode_gejala"
        gejala = self.db.fetch_all(query)
        self.db.close()
        return gejala

    def get_all_penyakit(self):
        """Mengambil semua penyakit yang tersedia"""
        self.db.connect()
        query = "SELECT * FROM penyakit ORDER BY kode_penyakit"
        penyakit = self.db.fetch_all(query)
        self.db.close()
        return penyakit


    def get_all_rules(self):
        """Mengambil semua rule patterns dengan detailnya"""
        self.db.connect()
        query = """
            SELECT
                rp.id,
                rp.kode_rule,
                rp.nama_rule,
                rp.referensi,
                p.kode_penyakit,
                p.nama_penyakit,
                GROUP_CONCAT(rd.kode_gejala ORDER BY rd.kode_gejala SEPARATOR ', ') as gejala_codes,
                GROUP_CONCAT(g.nama_gejala ORDER BY rd.kode_gejala SEPARATOR ' + ') as gejala_names
            FROM rule_patterns rp
            JOIN penyakit p ON rp.penyakit_id = p.id
            JOIN rule_details rd ON rp.kode_rule = rd.kode_rule
            JOIN gejala g ON rd.kode_gejala = g.kode_gejala
            GROUP BY rp.id
            ORDER BY p.kode_penyakit, rp.kode_rule
        """
        rules = self.db.fetch_all(query)
        self.db.close()
        return rules

    def get_penyakit_by_id(self, penyakit_id):
        """Mengambil detail penyakit berdasarkan ID"""
        self.db.connect()
        query = "SELECT * FROM penyakit WHERE id = %s"
        penyakit = self.db.fetch_one(query, (penyakit_id,))
        self.db.close()
        return penyakit

    def add_rule(self, kode_rule, penyakit_id, nama_rule, gejala_ids, referensi=None):
        """
        Menambah rule pattern baru dengan transaksi

        Args:
            kode_rule: Kode unik rule (misal: R016)
            penyakit_id: ID penyakit
            nama_rule: Nama/deskripsi rule
            gejala_ids: List ID gejala yang membentuk rule
            referensi: Sumber jurnal/referensi (opsional)

        Returns:
            int: ID rule yang baru dibuat atau None jika gagal
        """
        try:
            self.db.connect()
            
            # Insert rule pattern
            query_rule = """
                INSERT INTO rule_patterns (kode_rule, penyakit_id, nama_rule, referensi)
                VALUES (%s, %s, %s, %s)
            """
            rule_id = self.db.execute_query(query_rule, (kode_rule, penyakit_id, nama_rule, referensi))

            if not rule_id:
                raise Exception("Gagal memasukkan rule pattern baru.")

            # Insert detail gejala menggunakan kode
            for gejala_id in gejala_ids:
                # Ambil kode gejala dari ID
                query_get_kode = "SELECT kode_gejala FROM gejala WHERE id = %s"
                gejala_row = self.db.fetch_one(query_get_kode, (gejala_id,))
                
                if not gejala_row:
                    raise Exception(f"Gejala dengan ID {gejala_id} tidak ditemukan.")
                
                query_detail = """
                    INSERT INTO rule_details (kode_rule, kode_gejala)
                    VALUES (%s, %s)
                """
                detail_id = self.db.execute_query(query_detail, (kode_rule, gejala_row['kode_gejala']))
                if not detail_id:
                    raise Exception("Gagal memasukkan detail rule.")

            self.db.commit()
            return rule_id
        except Exception as e:
            print(f"Error adding rule: {e}")
            self.db.rollback()
            return None
        finally:
            self.db.close()

    def delete_rule(self, rule_id):
        """
        Menghapus rule pattern (cascade akan hapus detail juga)

        Args:
            rule_id: ID rule yang akan dihapus

        Returns:
            bool: True jika berhasil
        """
        try:
            self.db.connect()
            query = "DELETE FROM rule_patterns WHERE id = %s"
            result = self.db.execute_query(query, (rule_id,))
            if result is not None:
                self.db.commit()
                return True
            else:
                self.db.rollback()
                return False
        except Exception as e:
            print(f"Error deleting rule: {e}")
            self.db.rollback()
            return False
        finally:
            self.db.close()

    def close(self):
        """Tutup koneksi database"""
        self.db.close()
