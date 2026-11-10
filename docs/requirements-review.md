# Requirements review

## Hasil pemeriksaan

Paket menyediakan keluaran teknis yang diminta dalam SK_Batch2_AI_Engineer.pdf: architecture note, prototype yang berjalan, schema, rekomendasi bercaveat, sample input/output, serta evaluasi sederhana. Brief mengizinkan mock dan tidak mewajibkan aplikasi ATS lengkap, UI unggah, deployment, multi-agent, atau OCR. Implementasi adalah prototype lokal untuk demonstrasi alur, bukan produk produksi yang sudah tersertifikasi. Contoh yang disertakan bersifat sintetis; asal dataset eksternal untuk pengujian tambahan dijelaskan di bawah.

| Kebutuhan brief | Artefak/bukti | Status |
|---|---|---|
| Menerima CV dan menggunakan flow LLM | cvflow/documents.py, extraction.py, __main__.py; jalur mock dan Ollama | Tersedia |
| Informasi kandidat terstruktur | schemas/extraction.schema.json; skills, education, experience, projects dengan quote | Tersedia |
| Schema output utama | schemas/result.schema.json; kontrak sukses/gagal yang sama | Tersedia |
| Recommendation dengan caveat | pipeline.py, recommendation.status/rationale/caveats/follow_up_questions | Tersedia |
| Tidak membuat keputusan otomatis | human_review_required=true; final_decision=null | Diuji |
| Prototype/pseudocode/mock bekerja | python -m cvflow demo; output/demo | Diuji |
| Sample input/output | [Input](../samples/cv.txt), [output](../examples/demo/results.json) | Tersedia, sintetis |
| Evaluasi sederhana | [Laporan](../examples/evaluation/REPORT.md), [metrik](../examples/evaluation/metrics.json), tests | Diuji; mock dibedakan dari LLM |
| Architecture note | architecture.md | Tersedia |
| Catatan AI/tools | [AI dan tools](ai-usage.md) | Tersedia |
| Tidak membeli API/tool | Demo tanpa model/API; Ollama opsional dan lokal | Dipenuhi dalam pengerjaan |
| Tidak menggunakan data pribadi/confidential nyata | Contoh dalam paket sintetis; pengujian tambahan menggunakan dataset contoh CV publik Kaggle | Tidak ada dokumen dataset eksternal dalam paket; status seluruh dataset sebagai sintetis belum terverifikasi |
| Nama file sesuai format | Arga_Bona_Simarmata_AIEngineer_SKBatch2.zip | Nama paket pengumpulan; kode sumber juga tersedia di repo |
| Repo/notebook/Docs | [Repository](https://github.com/argabn/cv-review-assistant) berisi kode dan Markdown | Sudah dipublikasikan |
| Anyone with link can view, link bisa diakses | Repository GitHub publik | Visibilitas publik diverifikasi pada 10 November 2026 |
| Identitas, email, deadline, submit form | Catatan privat di luar paket | Tindakan pengumpulan masih pada pemilik |

## Sumber data pengujian

Arsip untuk pengujian tambahan diidentifikasi oleh pengguna sebagai
[Resume Dataset oleh Snehaan Bhawal di Kaggle](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset).
Deskripsi penerbit menyebut kumpulan contoh CV yang diambil dari LiveCareer;
metadata Kaggle menandai dataset sebagai publik dengan lisensi CC0. Deskripsi
tersebut tidak menyatakan seluruh dokumen sintetis atau menjamin anonimisasi
lengkap. Karena itu, dataset disebut contoh CV publik, bukan CV privat pengguna
atau dataset sintetis yang sudah terverifikasi. Metadata sumber diperiksa pada
10 November 2026; kecocokan seluruh arsip lokal dengan versi Kaggle tidak diaudit.

Paket publik hanya menyediakan input, fixture, dan output sintetis. Dokumen
Kaggle, teks ekstraksi, dan respons model dari pengujian dataset eksternal tidak
disertakan. Ringkasan agregat pengujian tambahan tetap dijelaskan
di [verification.md](verification.md). Demonstrasi dan evaluasi yang dapat
direproduksi untuk pengumpulan menggunakan data sintetis. Tidak ada pengujian
ulang dataset eksternal dalam audit pengumpulan ini. Sumber publik saja tidak
cukup untuk memastikan ketiadaan informasi pribadi di setiap dokumen.

## Antarmuka dan pola industri

Tidak ada standar tunggal yang mewajibkan bentuk visual tertentu. Paper yang disediakan memberi bukti tentang alur dan risiko review, bukan spesifikasi desain produk yang wajib disalin. Tampilan memakai pola review kandidat yang juga terdokumentasi pada ATS: konteks posisi, identitas kandidat, evaluasi per kriteria, profil terstruktur, akses bukti, serta feedback reviewer.

Sumber pembanding produk (diakses 10 November 2026):

- [Greenhouse — Application review stage](https://support.greenhouse.io/hc/en-us/articles/4401963991707-Application-review-stage): candidate details, documents, feedback, dan application review.
- [Greenhouse — Scorecard overview](https://support.greenhouse.io/hc/en-us/articles/4414777492891-Scorecard-overview): kriteria yang ditetapkan sebelumnya, key takeaways, serta recommendation.

Keputusan desain:

- Hilangkan banner tugas, slogan, dan identitas program dari UI. Nama pembuat menjadi watermark kecil.
- Tampilkan posisi dan status penelaahan terlebih dahulu. ID kandidat dipakai karena data contoh tidak memerlukan identitas pribadi.
- Tabel kriteria menyediakan bukti langsung; jangan hanya memberi persentase kecocokan yang seolah terkalibrasi.
- Pengalaman/proyek/pendidikan/skill berada dalam profil yang mudah dipindai.
- Sumber dan keterbatasan tersedia melalui progressive disclosure; caveat utama tetap terlihat.
- Label Simulasi tetap terlihat untuk membedakan respons mock dari inferensi nyata. Menghapus label ini akan menyesatkan.
- Koreksi menggunakan formulir field, bukan editor JSON sebagai interaksi utama. Pengguna dapat mengubah, menghapus, dan menambah entri.
- Ekspor review tidak mengklaim telah menyimpan keputusan. Backend CLI memvalidasi dan menghitung ulang, lalu laporan baru menunjukkan catatan review terakhir.
- UI mendukung keyboard focus, label form, status feedback, viewport kecil, serta print stylesheet. Evaluasi pengguna dan audit aksesibilitas menyeluruh belum dilakukan.

Batas analogi ATS: sistem ini tidak memiliki autentikasi, pipeline organisasi, dokumen tersimpan dalam server, komunikasi kandidat, audit log tahan manipulasi, atau keputusan advance/reject. Tidak ada klaim parity dengan Greenhouse atau sertifikasi standar industri.

## Hubungan dengan referensi lokal

- Kupfer et al. (2023), bagian 2.4 dan Figure 3: ringkasan harus dapat ditelusuri ke informasi lebih rinci untuk verifikasi. Diadaptasi melalui bukti per fakta dan per kriteria; tidak menyalin ranking otomatis atau penilaian kepribadian.
- Lo et al. (2025), bagian 4 dan 5.4: extraction, evaluation, summarization dan formatting dipisahkan; feedback terkait kebutuhan posisi. Diadaptasi menjadi modul kecil dengan alasan spesifik kriteria.
- Thomas & Vince (2026), bagian evaluasi: miss, error/hallucination dan correct absence dibedakan. Laporan mock sengaja memperlihatkan kasus omission dengan recall 0,8.
- Geng et al. (2025) dan Ferguson et al. (2026): format terstruktur tidak sama dengan isi benar. Schema dan pemeriksaan sumber tidak diklaim sebagai verifikasi kompetensi.

## Batas kualitas yang harus tetap jujur

Uji model nyata pada satu CV sintetis berhasil secara operasional, tetapi exact-record comparison hanya 0,4 precision/recall karena perbedaan pemisahan dan pengisian field. Angka tersebut tercatat di verification.md; tidak diganti dengan angka test passing. Mode mock dipilih sebagai demo utama yang reproducible sesuai izin brief. Untuk penggunaan rekrutmen nyata diperlukan dataset berlabel yang lebih representatif, perbaikan ekstraksi, evaluasi fairness, dan kontrol akses.
