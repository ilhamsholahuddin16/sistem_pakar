-- Database Schema untuk Sistem Pakar Penyakit Lambung
-- Forward Chaining dengan Rule Pattern Matching (IF-THEN)

CREATE DATABASE IF NOT EXISTS sistem_pakar_lambung;
USE sistem_pakar_lambung;

-- Tabel Penyakit Lambung
CREATE TABLE IF NOT EXISTS penyakit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_penyakit VARCHAR(10) UNIQUE NOT NULL,
    nama_penyakit VARCHAR(100) NOT NULL,
    deskripsi TEXT,
    solusi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel Gejala
CREATE TABLE IF NOT EXISTS gejala (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_gejala VARCHAR(10) UNIQUE NOT NULL,
    nama_gejala VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel Rule Patterns (Basis Pengetahuan)
-- Format: IF (Gejala1 + Gejala2 + ...) THEN Penyakit
CREATE TABLE IF NOT EXISTS rule_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_rule VARCHAR(20) UNIQUE NOT NULL,
    penyakit_id INT NOT NULL,
    nama_rule VARCHAR(200),
    referensi TEXT,  -- Sumber jurnal/buku/penelitian
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (penyakit_id) REFERENCES penyakit(id) ON DELETE CASCADE
);

-- Tabel Detail Rule (Gejala-gejala dalam satu rule)
-- Kombinasi gejala yang membentuk satu rule
-- Menggunakan kode langsung agar lebih mudah dipahami
CREATE TABLE IF NOT EXISTS rule_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_rule VARCHAR(20) NOT NULL,
    kode_gejala VARCHAR(10) NOT NULL,
    FOREIGN KEY (kode_rule) REFERENCES rule_patterns(kode_rule) ON DELETE CASCADE,
    FOREIGN KEY (kode_gejala) REFERENCES gejala(kode_gejala) ON DELETE CASCADE,
    UNIQUE KEY unique_rule_gejala (kode_rule, kode_gejala)
);

-- Tabel Riwayat Konsultasi
CREATE TABLE IF NOT EXISTS riwayat_konsultasi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_user VARCHAR(100) NOT NULL,
    tanggal_konsultasi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    penyakit_id INT,
    rule_matched VARCHAR(20),  -- Kode rule yang cocok
    match_percentage DECIMAL(5,2), -- Persentase kecocokan (0.00 - 100.00)
    jumlah_gejala INT,         -- Jumlah gejala yang dipilih user
    FOREIGN KEY (penyakit_id) REFERENCES penyakit(id) ON DELETE SET NULL
);

-- Tabel Detail Riwayat (gejala yang dipilih pada konsultasi)
CREATE TABLE IF NOT EXISTS detail_riwayat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    riwayat_id INT NOT NULL,
    gejala_id INT NOT NULL,
    FOREIGN KEY (riwayat_id) REFERENCES riwayat_konsultasi(id) ON DELETE CASCADE,
    FOREIGN KEY (gejala_id) REFERENCES gejala(id) ON DELETE CASCADE
);

-- Index untuk optimasi query
CREATE INDEX idx_rule_patterns_penyakit ON rule_patterns(penyakit_id);
CREATE INDEX idx_rule_details_rule ON rule_details(kode_rule);
CREATE INDEX idx_rule_details_gejala ON rule_details(kode_gejala);
CREATE INDEX idx_riwayat_tanggal ON riwayat_konsultasi(tanggal_konsultasi);
