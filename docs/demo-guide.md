# Demo dan penjelasan singkat

1. Buka samples/job.json: tunjukkan tiga kebutuhan wajib dan satu tambahan. Semua merupakan posisi sintetis.
2. Buka samples/cv.txt: skill, pendidikan, pengalaman dan proyek yang disebutkan secara eksplisit.
3. Jalankan `python -m cvflow demo`. Buka output/demo/report.html.
4. Jelaskan fakta dan bukti, alasan rekomendasi, serta caveat bahwa CV bukan verifikasi kemampuan.
5. Buka output/review-before/report.html: SQL sengaja terlewat dalam fixture; hasil meminta klarifikasi.
6. Perlihatkan samples/review.json dan output/review-after/report.html: koreksi reviewer menambah fakta yang memang ada dalam sumber; rekomendasi dihitung ulang. Review tidak mengubah dokumen asli.
7. Buka output/evaluation/REPORT.md: sembilan kasus perilaku, metrik omission kurang dari sempurna, dan batas interpretasi mock.

Poin reasoning: saya memilih workflow kecil dengan batas yang jelas; valid JSON belum tentu benar; tidak ditemukan bukan berarti tidak mampu; penilaian hanya berdasarkan kriteria eksplisit; koreksi manusia tercatat; setiap kegagalan memiliki jalur aman.

Jika ditanya pengembangan selanjutnya: uji lebih banyak CV sintetis dengan layout beragam dan label independen, perbaiki context coverage, tambahkan OCR jika kebutuhan nyata menuntut, dan audit fairness sebelum penggunaan hiring nyata. Tambahan fitur dilakukan berdasarkan hasil evaluasi, bukan sekadar kompleksitas.
