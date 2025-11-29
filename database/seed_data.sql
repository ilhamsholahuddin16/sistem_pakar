-- Seed Data untuk Sistem Pakar Penyakit Lambung
-- Rule Pattern Matching dengan IF-THEN
USE sistem_pakar_lambung;

-- ============================================
-- INSERT DATA PENYAKIT
-- ============================================
INSERT INTO penyakit (kode_penyakit, nama_penyakit, deskripsi, solusi) VALUES
('P001', 'Gastritis (Maag)',
    'Peradangan pada lapisan lambung yang dapat menyebabkan rasa tidak nyaman dan nyeri pada perut bagian atas.',
    'Hindari makanan pedas, asam, dan berlemak. Makan secara teratur dengan porsi kecil tapi sering. Konsumsi obat antasida sesuai anjuran dokter. Kurangi stress dan hindari alkohol serta rokok.'),

('P002', 'GERD (Gastroesophageal Reflux Disease)',
    'Kondisi di mana asam lambung naik kembali ke kerongkongan, menyebabkan iritasi dan rasa terbakar di dada.',
    'Hindari makanan pemicu seperti cokelat, kopi, makanan berlemak dan pedas. Jangan langsung berbaring setelah makan. Tinggikan kepala saat tidur. Turunkan berat badan jika obesitas.'),

('P003', 'Tukak Lambung (Ulkus Peptikum)',
    'Luka terbuka pada lapisan dalam lambung akibat erosi oleh asam lambung.',
    'Konsultasi ke dokter untuk pemeriksaan H. pylori dan pengobatan antibiotik jika perlu. Hindari NSAID. Hindari alkohol dan rokok. Makan teratur dan hindari stress.'),

('P004', 'Dispepsia Fungsional',
    'Gangguan pencernaan yang menyebabkan rasa tidak nyaman di perut atas tanpa penyebab organik yang jelas.',
    'Makan dalam porsi kecil tapi sering. Hindari makanan berlemak, pedas, dan asam. Kelola stress dengan baik. Olahraga teratur. Hindari kafein dan alkohol.'),

('P005', 'Gastroenteritis',
    'Peradangan pada saluran pencernaan yang melibatkan lambung dan usus, biasanya disebabkan oleh infeksi.',
    'Perbanyak minum air untuk mencegah dehidrasi. Konsumsi makanan lunak dan mudah dicerna. Istirahat cukup. Jika disertai demam tinggi atau diare berdarah, segera ke dokter.'),

('P006', 'Gastritis Erosif',
    'Bentuk gastritis yang lebih parah dengan erosi atau pengikisan pada lapisan lambung.',
    'Segera konsultasi ke dokter untuk penanganan intensif. Hindari NSAID, alkohol, dan rokok. Konsumsi obat pelindung lambung. Makan makanan lunak. Istirahat cukup.');

-- ============================================
-- INSERT DATA GEJALA
-- ============================================
INSERT INTO gejala (kode_gejala, nama_gejala) VALUES
('G001', 'Nyeri atau perih di ulu hati'),
('G002', 'Mual'),
('G003', 'Muntah'),
('G004', 'Perut kembung'),
('G005', 'Sering bersendawa'),
('G006', 'Rasa terbakar di dada (heartburn)'),
('G007', 'Asam lambung naik ke tenggorokan'),
('G008', 'Nyeri bertambah saat perut kosong'),
('G009', 'Nyeri berkurang setelah makan'),
('G010', 'Kehilangan nafsu makan'),
('G011', 'Cepat merasa kenyang'),
('G012', 'Muntah darah atau muntah berwarna hitam'),
('G013', 'BAB berdarah atau berwarna hitam'),
('G014', 'Nyeri perut setelah makan'),
('G015', 'Berat badan menurun'),
('G016', 'Diare'),
('G017', 'Demam'),
('G018', 'Lemas dan lelah'),
('G019', 'Nyeri yang menjalar ke punggung'),
('G020', 'Mulut terasa asam atau pahit'),
('G021', 'Sulit menelan'),
('G022', 'Batuk kronis terutama malam hari'),
('G023', 'Suara serak'),
('G024', 'Sakit perut hilang timbul');

-- ============================================
-- INSERT RULE PATTERNS
-- Format: IF (Gejala1 + Gejala2 + ...) THEN Penyakit
-- ============================================

-- RULE UNTUK GASTRITIS (P001)
INSERT INTO rule_patterns (kode_rule, penyakit_id, nama_rule, referensi) VALUES
('R001', 1, 'Gastritis Akut Klasik', 'Pola gejala gastritis akut umum'),
('R002', 1, 'Gastritis dengan Dispepsia', 'Gastritis disertai gangguan pencernaan'),
('R003', 1, 'Gastritis Kronis', 'Pola gastritis yang berkelanjutan');

-- Detail Rule R001: IF (Nyeri ulu hati + Mual + Muntah) THEN Gastritis
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R001', 'G001'),  -- Nyeri ulu hati
('R001', 'G002'),  -- Mual
('R001', 'G003');  -- Muntah

-- Detail Rule R002: IF (Nyeri ulu hati + Perut kembung + Cepat kenyang) THEN Gastritis
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R002', 'G001'),  -- Nyeri ulu hati
('R002', 'G004'),  -- Perut kembung
('R002', 'G011');  -- Cepat kenyang

-- Detail Rule R003: IF (Nyeri ulu hati + Sakit hilang timbul + Kehilangan nafsu makan) THEN Gastritis
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R003', 'G001'),  -- Nyeri ulu hati
('R003', 'G024'),  -- Sakit hilang timbul
('R003', 'G010');  -- Kehilangan nafsu makan

-- RULE UNTUK GERD (P002)
INSERT INTO rule_patterns (kode_rule, penyakit_id, nama_rule, referensi) VALUES
('R004', 2, 'GERD Klasik', 'Pola GERD dengan heartburn dominan'),
('R005', 2, 'GERD dengan Refluks', 'GERD dengan asam naik ke tenggorokan'),
('R006', 2, 'GERD Komplikasi Esofagus', 'GERD dengan gangguan esofagus');

-- Detail Rule R004: IF (Heartburn + Asam naik + Mulut asam) THEN GERD
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R004', 'G006'),  -- Heartburn
('R004', 'G007'),  -- Asam naik
('R004', 'G020');  -- Mulut asam

-- Detail Rule R005: IF (Heartburn + Sering bersendawa + Mual) THEN GERD
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R005', 'G006'),  -- Heartburn
('R005', 'G005'),  -- Bersendawa
('R005', 'G002');  -- Mual

-- Detail Rule R006: IF (Heartburn + Sulit menelan + Batuk kronis) THEN GERD
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R006', 'G006'),  -- Heartburn
('R006', 'G021'),  -- Sulit menelan
('R006', 'G022');  -- Batuk kronis

-- RULE UNTUK TUKAK LAMBUNG (P003)
INSERT INTO rule_patterns (kode_rule, penyakit_id, nama_rule, referensi) VALUES
('R007', 3, 'Tukak Lambung Khas', 'Pola nyeri khas tukak lambung'),
('R008', 3, 'Tukak dengan Perdarahan', 'Tukak lambung dengan komplikasi'),
('R009', 3, 'Tukak Kronis', 'Tukak lambung berkelanjutan');

-- Detail Rule R007: IF (Nyeri saat kosong + Nyeri hilang setelah makan) THEN Tukak Lambung
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R007', 'G008'),  -- Nyeri saat perut kosong
('R007', 'G009');  -- Nyeri hilang setelah makan

-- Detail Rule R008: IF (Nyeri ulu hati + Muntah darah + BAB berdarah) THEN Tukak Lambung
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R008', 'G001'),  -- Nyeri ulu hati
('R008', 'G012'),  -- Muntah darah
('R008', 'G013');  -- BAB berdarah

-- Detail Rule R009: IF (Nyeri saat kosong + Nyeri ke punggung + Berat badan turun) THEN Tukak Lambung
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R009', 'G008'),  -- Nyeri saat kosong
('R009', 'G019'),  -- Nyeri ke punggung
('R009', 'G015');  -- Berat badan turun

-- RULE UNTUK DISPEPSIA FUNGSIONAL (P004)
INSERT INTO rule_patterns (kode_rule, penyakit_id, nama_rule, referensi) VALUES
('R010', 4, 'Dispepsia Fungsional Tipikal', 'Pola dispepsia tanpa penyebab organik'),
('R011', 4, 'Dispepsia dengan Kembung', 'Dispepsia dengan dominan kembung');

-- Detail Rule R010: IF (Cepat kenyang + Perut kembung + Mual) THEN Dispepsia
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R010', 'G011'),  -- Cepat kenyang
('R010', 'G004'),  -- Kembung
('R010', 'G002');  -- Mual

-- Detail Rule R011: IF (Perut kembung + Bersendawa + Nyeri setelah makan) THEN Dispepsia
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R011', 'G004'),  -- Kembung
('R011', 'G005'),  -- Bersendawa
('R011', 'G014');  -- Nyeri setelah makan

-- RULE UNTUK GASTROENTERITIS (P005)
INSERT INTO rule_patterns (kode_rule, penyakit_id, nama_rule, referensi) VALUES
('R012', 5, 'Gastroenteritis Akut', 'Pola infeksi saluran cerna akut'),
('R013', 5, 'Gastroenteritis dengan Dehidrasi', 'GE dengan risiko dehidrasi');

-- Detail Rule R012: IF (Diare + Muntah + Mual) THEN Gastroenteritis
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R012', 'G016'),  -- Diare
('R012', 'G003'),  -- Muntah
('R012', 'G002');  -- Mual

-- Detail Rule R013: IF (Diare + Demam + Lemas) THEN Gastroenteritis
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R013', 'G016'),  -- Diare
('R013', 'G017'),  -- Demam
('R013', 'G018');  -- Lemas

-- RULE UNTUK GASTRITIS EROSIF (P006)
INSERT INTO rule_patterns (kode_rule, penyakit_id, nama_rule, referensi) VALUES
('R014', 6, 'Gastritis Erosif dengan Perdarahan', 'Gastritis erosif berat'),
('R015', 6, 'Gastritis Erosif Akut', 'Gastritis erosif onset cepat');

-- Detail Rule R014: IF (Muntah darah + Nyeri ulu hati + Lemas) THEN Gastritis Erosif
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R014', 'G012'),  -- Muntah darah
('R014', 'G001'),  -- Nyeri ulu hati
('R014', 'G018');  -- Lemas

-- Detail Rule R015: IF (Nyeri ulu hati + Muntah + Kehilangan nafsu makan) THEN Gastritis Erosif
INSERT INTO rule_details (kode_rule, kode_gejala) VALUES
('R015', 'G001'),  -- Nyeri ulu hati
('R015', 'G003'),  -- Muntah
('R015', 'G010');  -- Kehilangan nafsu makan
