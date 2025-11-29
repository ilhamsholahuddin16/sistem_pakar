# Sistem Pakar Penyakit Lambung

Sistem pakar untuk diagnosis penyakit lambung menggunakan metode **Forward Chaining** dengan **Certainty Factor** berbasis riwayat konsultasi.

## Fitur Utama

- ✅ **Forward Chaining** - Metode inferensi dari fakta ke kesimpulan
- ✅ **Riwayat Konsultasi** - Tracking dan analisis konsultasi
- ✅ **Responsive UI** - Antarmuka modern dengan Bootstrap 5

## Penyakit yang Dapat Didiagnosis

1. Gastritis (Maag)
2. GERD (Gastroesophageal Reflux Disease)
3. Tukak Lambung (Ulkus Peptikum)
4. Dispepsia Fungsional
5. Gastroenteritis
6. Gastritis Erosif

## Teknologi yang Digunakan

**Backend:**
- Python
- Flask Web Framework
- MySQL Database
- mysql-connector-python

**Frontend:**
- HTML5, CSS3
- Bootstrap 5
- jQuery
- Font Awesome

## Cara Instalasi

### 1. Prerequisites

Pastikan Anda sudah menginstall:
- Python 3.7 atau lebih tinggi
- MySQL Server
- pip (Python package manager)

### 2. Clone/Download Project

```bash
git remote add origin https://github.com/ilhamsholahuddin16/sistem_pakar.git
```

### 3. Buat Virtual Environment (Opsional tapi Direkomendasikan)

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Konfigurasi Database

Buka file `config.py` dan sesuaikan konfigurasi database Anda:

```python
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'sistem_pakar_lambung'
```

### 6. Setup Database

Pastikan MySQL Server sudah berjalan, kemudian jalankan:

```bash
python setup_database.py
```

Script ini akan:
- Membuat database `sistem_pakar_lambung`
- Membuat semua tabel yang diperlukan
- Mengisi data awal (penyakit, gejala, dan rules)

### 7. Jalankan Aplikasi

```bash
python run.py
```

Aplikasi akan berjalan di: `http://localhost:5001`

## Struktur Project

```
sistem_pakar/
├── app/
│   ├── __init__.py              # Inisialisasi Flask app
│   ├── routes.py                # Routes/Controllers
│   ├── database.py              # Database connection handler
│   ├── inference_engine.py      # Forward chaining engine
│   ├── pattern_matcher.py       # Pattern matching algoritma
│   ├── history_manager.py       # Riwayat konsultasi manager
│   └── templates/               # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── diagnosis.html
│       ├── hasil_diagnosis.html
│       ├── riwayat.html
│       ├── riwayat_detail.html
│       ├── tentang.html
│       ├── 404.html
│       └── 500.html
├── database/
│   ├── schema.sql              # Database schema
│   └── seed_data.sql           # Data awal (penyakit, gejala, rules)
├── config.py                   # Konfigurasi aplikasi
├── run.py                      # Entry point aplikasi
├── setup_database.py           # Script setup database
├── requirements.txt            # Python dependencies
└── README.md                   # Dokumentasi ini
```

## Cara Penggunaan

### 1. Diagnosis Penyakit

1. Buka aplikasi di browser
2. Klik menu **"Diagnosis"**
3. Masukkan nama
4. Pilih gejala-gejala yang Anda alami
5. Klik **"Proses Diagnosis"**
6. Lihat hasil diagnosis dengan tingkat keyakinan

### 2. Melihat Riwayat

1. Klik menu **"Riwayat"**
2. Lihat semua konsultasi yang pernah dilakukan
3. Klik **"Detail"** untuk melihat informasi lengkap konsultasi
4. Gunakan fitur filter untuk mencari berdasarkan nama

## Metode yang Digunakan

### Forward Chaining

Metode inferensi yang bekerja dari fakta (gejala) menuju kesimpulan (penyakit). Sistem mencocokkan gejala yang dipilih dengan basis pengetahuan (rules) untuk menentukan penyakit.

## API Endpoints

- `GET /` - Halaman utama
- `GET /diagnosis` - Form diagnosis
- `POST /process-diagnosis` - Proses diagnosis (AJAX)
- `GET /hasil-diagnosis/<id>` - Hasil diagnosis
- `GET /riwayat` - Daftar riwayat
- `GET /riwayat/<id>` - Detail riwayat
- `GET /tentang` - Tentang sistem
- `GET /api/gejala` - API daftar gejala (JSON)
- `GET /api/statistics` - API statistik (JSON)
- `GET /api/pattern-stats` - API statistik pattern (JSON)

## Troubleshooting

### Database Connection Error

Pastikan:
- MySQL Server di Laragon sudah berjalan
- Konfigurasi di `config.py` sudah benar
- Database sudah dibuat dengan `setup_database.py`

### Module Not Found Error

Jalankan:
```bash
pip install -r requirements.txt
```

### Port Already in Use

Ubah port di `run.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5002)
```

## Disclaimer

⚠️ Sistem ini dikembangkan untuk tujuan edukasi dan sebagai alat bantu diagnosis awal. Hasil diagnosis **BUKAN merupakan diagnosis medis resmi** dan tidak dapat menggantikan konsultasi dengan dokter profesional.

## Lisensi

Project ini dibuat untuk keperluan edukasi dan pembelajaran.
