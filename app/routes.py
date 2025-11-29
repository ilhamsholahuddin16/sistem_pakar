from flask import render_template, request, jsonify, session, flash, redirect, url_for
from app import app
from app.inference_engine import ForwardChaining
from app.history_manager import HistoryManager
from app.database import Database


@app.route('/')
def index():
    """Halaman utama"""
    return render_template('index.html')


@app.route('/manage-rules', methods=['GET', 'POST'])
def manage_rules():
    """Halaman untuk mengelola aturan (rules)"""
    db = Database()
    fc = ForwardChaining()
    try:
        db.connect()
        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'add':
                kode_rule = request.form.get('kode_rule')
                nama_rule = request.form.get('nama_rule')
                penyakit_id = request.form.get('id_penyakit')
                gejala_ids = request.form.getlist('gejala_ids')
                referensi = request.form.get('referensi')

                if not all([kode_rule, nama_rule, penyakit_id, gejala_ids]):
                    flash('Semua field harus diisi, dan minimal satu gejala harus dipilih.', 'warning')
                else:
                    # Menggunakan metode dari ForwardChaining yang sudah ada
                    rule_id = fc.add_rule(kode_rule, penyakit_id, nama_rule, gejala_ids, referensi if referensi else None)
                    if rule_id:
                        flash(f'Rule pattern "{kode_rule}" berhasil ditambahkan.', 'success')
                    else:
                        flash(f'Gagal menambahkan rule. Kode "{kode_rule}" mungkin sudah ada.', 'danger')

            elif action == 'delete':
                rule_id = request.form.get('rule_id')
                if rule_id:
                    if db.delete_rule(rule_id):
                        flash('Gejala berhasil dihapus dari aturan.', 'success')
                    else:
                        flash('Gagal menghapus gejala dari aturan.', 'danger')

            return redirect(url_for('manage_rules'))

        # Untuk metode GET
        all_rules = db.get_all_rules()
        all_penyakit = fc.get_all_penyakit()
        all_gejala = fc.get_all_gejala()

        # Dapatkan kode rule terakhir untuk menyarankan kode berikutnya
        last_rule_query = "SELECT kode_rule FROM rule_patterns ORDER BY CAST(SUBSTRING(kode_rule, 2) AS UNSIGNED) DESC LIMIT 1"
        last_rule = db.fetch_one(last_rule_query)
        next_rule_number = 1
        if last_rule:
            try:
                next_rule_number = int(last_rule['kode_rule'][1:]) + 1
            except (ValueError, IndexError):
                pass # Biarkan default jika format tidak terduga
        suggested_kode_rule = f"R{next_rule_number:03d}"


        return render_template('manage_rules.html',
                               all_rules=all_rules,
                               all_penyakit=all_penyakit,
                               all_gejala=all_gejala,
                               suggested_kode_rule=suggested_kode_rule)
    finally:
        if db.connection and db.connection.is_connected():
            db.close()


@app.route('/diagnosis')
def diagnosis():
    """Halaman diagnosis - menampilkan form pilihan gejala"""
    fc = ForwardChaining()
    gejala_list = fc.get_all_gejala()

    return render_template('diagnosis.html', gejala_list=gejala_list)


@app.route('/process-diagnosis', methods=['POST'])
def process_diagnosis():
    """
    Memproses diagnosis berdasarkan pattern matching
    """
    try:
        # Ambil data dari form
        nama_user = request.form.get('nama_user', 'Anonymous')
        gejala_ids = request.form.getlist('gejala[]')

        if not gejala_ids:
            return jsonify({
                'success': False,
                'message': 'Silakan pilih minimal satu gejala'
            }), 400

        # Convert ke format yang sesuai
        gejala_terpilih = [{'id': int(gid)} for gid in gejala_ids]

        # Jalankan forward chaining dengan pattern matching
        fc = ForwardChaining()
        diagnosis_result = fc.diagnose(gejala_terpilih)

        if not diagnosis_result:
            return jsonify({
                'success': False,
                'message': 'Tidak ada rule yang cocok dengan gejala yang dipilih. Silakan pilih kombinasi gejala lain atau konsultasi dengan dokter.'
            }), 404

        # Simpan ke riwayat konsultasi
        hm = HistoryManager()
        riwayat_id = hm.save_consultation(
            nama_user=nama_user,
            gejala_terpilih=gejala_terpilih,
            diagnosis_result=diagnosis_result
        )

        # Simpan riwayat_id, gejala_cocok, dan detail akurasi ke session
        session['last_riwayat_id'] = riwayat_id
        session['gejala_cocok'] = diagnosis_result.get('gejala_cocok', [])
        session['completeness'] = diagnosis_result.get('completeness', 0)
        session['relevance'] = diagnosis_result.get('relevance', 0)

        # Return hasil diagnosis
        return jsonify({
            'success': True,
            'riwayat_id': riwayat_id,
            'diagnosis': diagnosis_result
        })

    except Exception as e:
        print(f"Error in process_diagnosis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500


@app.route('/hasil-diagnosis/<int:riwayat_id>')
def hasil_diagnosis(riwayat_id):
    """Halaman hasil diagnosis"""
    hm = HistoryManager()
    detail = hm.get_consultation_detail(riwayat_id)

    if not detail:
        return "Riwayat konsultasi tidak ditemukan", 404

    # Ambil gejala cocok dan detail akurasi dari session
    gejala_cocok = session.get('gejala_cocok', [])
    completeness = session.get('completeness', 0)
    relevance = session.get('relevance', 0)

    # Tambahkan completeness dan relevance ke consultation object
    consultation_data = dict(detail['consultation'])
    consultation_data['completeness'] = completeness
    consultation_data['relevance'] = relevance

    return render_template('hasil_diagnosis.html',
                           consultation=consultation_data,
                           gejala_terpilih=detail['gejala_terpilih'],
                           gejala_cocok=gejala_cocok)


@app.route('/riwayat')
def riwayat():
    """Halaman riwayat konsultasi"""
    nama_user = request.args.get('nama', None)

    hm = HistoryManager()

    if nama_user:
        history_list = hm.get_user_history(nama_user=nama_user, limit=20)
    else:
        history_list = hm.get_all_history(limit=50)

    statistics = hm.get_statistics()

    return render_template('riwayat.html',
                           history_list=history_list,
                           statistics=statistics,
                           nama_filter=nama_user)


@app.route('/riwayat/<int:riwayat_id>')
def riwayat_detail(riwayat_id):
    """Detail riwayat konsultasi tertentu"""
    hm = HistoryManager()
    detail = hm.get_consultation_detail(riwayat_id)

    if not detail:
        return "Riwayat tidak ditemukan", 404

    return render_template('riwayat_detail.html',
                           consultation=detail['consultation'],
                           gejala_terpilih=detail['gejala_terpilih'])


@app.route('/api/gejala')
def api_gejala():
    """API endpoint untuk mendapatkan daftar gejala"""
    fc = ForwardChaining()
    gejala_list = fc.get_all_gejala()

    return jsonify({
        'success': True,
        'data': gejala_list
    })


@app.route('/api/statistics')
def api_statistics():
    """API endpoint untuk statistik konsultasi"""
    hm = HistoryManager()
    stats = hm.get_statistics()

    return jsonify({
        'success': True,
        'data': stats
    })


@app.route('/tentang')
def tentang():
    """Halaman tentang sistem"""
    return render_template('tentang.html')


@app.errorhandler(404)
def not_found(error):
    """Handler untuk 404"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handler untuk 500"""
    return render_template('500.html'), 500
