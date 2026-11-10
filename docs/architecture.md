# Architecture note

## Masalah dan hasil yang dituju

Reviewer memerlukan fakta kandidat yang dapat diperiksa, dibandingkan dengan kebutuhan posisi, serta disertai ketidakpastian. CV merupakan input tidak tepercaya dan klaim kandidat, bukan instruksi atau ground truth kompetensi.

Implementasi memisahkan ingestion (`documents.py`), ekstraksi (`extraction.py`), kontrak (`contracts.py`), penilaian (`pipeline.py`), presentasi (`report.py`), dan review (`review.py`). CLI menyatukan alurnya. Pemisahan ini cukup untuk prototype; tidak dibutuhkan agent framework, database, RAG, atau deployment.

## Kontrak

Input: PDF/TXT/ZIP dan job JSON dengan title, version, serta criteria. Setiap kriteria memiliki ID, label, field fakta, daftar istilah/alias, dan penanda required. Tidak ada kriteria default tersembunyi.

Fakta: skills, education, experience, projects. Field tidak diketahui bernilai null; koleksi tanpa entri berupa []. Setiap record punya kutipan. Schema final menambahkan assessment, recommendation, errors, metadata, human_review_required=true, final_decision=null. Semua hasil, termasuk kegagalan, divalidasi dengan kontrak yang sama.

Mode mock membaca respons yang disiapkan. Mode Ollama meminta structured generation dengan JSON Schema. Agar model kecil tidak mengulang teks panjang, ia mengembalikan nomor baris; aplikasi merekonstruksi kutipan. Output terpotong tidak diterima. Nilai literal seperti jabatan/tanggal harus ditemukan pada sumber setelah normalisasi kapitalisasi dan whitespace. Pipeline memeriksa kembali bahwa nilai ada dalam kutipannya. Deskripsi tetap memerlukan review semantik.

## Context budget dan kelengkapan

Dokumen dibatasi 10 halaman/10 MB dan 12.000 karakter. Setiap permintaan ekstraksi dibatasi konservatif 3.000 karakter, dengan konteks 4096 token. Ini heuristik, bukan penghitungan token tokenizer. Model dapat menolak/terpotong dan menghasilkan kegagalan terkontrol. Jika heading Education dan Experience dikenal, bagian diproses berurutan; jika tidak, seluruh teks diproses dalam batas per-permintaan. Tidak ada silent truncation oleh aplikasi. CV panjang yang tidak muat perlu penanganan manual atau pengembangan chunking berikutnya.

## Penilaian dan rekomendasi

Kriteria dicocokkan pada field yang dikonfigurasi, bukan seluruh CV tanpa konteks. Istilah harus muncul pada fakta dan bukti. Kriteria wajib yang belum didukung menghasilkan needs_clarification. Seluruh kriteria wajib didukung menghasilkan ready_for_review. Input/config/ekstraksi gagal menghasilkan unable_to_assess dengan fakta kosong; output parsial tidak diteruskan.

Ringkasan menghitung informasi yang tersedia dan kriteria berbukti. Rationale mengacu pada posisi serta gap yang konkret. Tidak ada penilaian kepribadian, gender, usia, agama, atau ranking kandidat. Skill personal yang memang ditulis dalam CV merupakan klaim, bukan asesmen objektif.

## Human oversight

Laporan menampilkan bukti, caveat, pertanyaan, dan form koreksi. Reviewer mengunduh receipt; CLI memvalidasi koreksi dan menghitung ulang assessment. Source hash dan job hash mencegah review diterapkan pada data yang sudah berubah. Hasil awal dipertahankan, hasil koreksi dan receipt disimpan terpisah. Identitas reviewer belum diautentikasi; ini simulasi audit trail lokal, bukan sistem produksi.

## Safety dan kegagalan

- Tidak ada tools/action yang dapat dipanggil dari isi CV. Tidak membuka URL dalam CV.
- Deteksi instruksi memakai heuristik terbatas; bukan proteksi prompt injection lengkap.
- ZIP tidak diekstrak ke filesystem; pembacaan dibatasi dan per-file error dilaporkan.
- HTML meng-escape data CV; data tidak dimasukkan menjadi JavaScript executable.
- Tidak ada keputusan diterima/ditolak, komunikasi kandidat, atau perubahan ATS.
- CV asli, identitas kontak kandidat, serta arsip dataset pengguna tidak disertakan dalam paket submission.
- Hidden text PDF, relasi field yang keliru, proxy bias, dan klaim palsu tetap memerlukan pemeriksaan manusia.

## Evaluasi dan trade-off

Demo dan evaluasi memakai data sintetis. Ada kasus normal, missing information, deliberate omission, injection, empty input, invalid schema, fabricated evidence, missing job, serta pasangan identitas sintetis. Label fakta disimpan terpisah. Program mengukur correct records, missed records, wrong/extra records, correct empty sections, precision, dan recall. Exact record matching konservatif; perbedaan parafrasa dapat dianggap salah. Tidak mengklaim akurasi produksi dari fixture, test passing, atau satu smoke test model.

Aturan deterministik dipilih agar rekomendasi mudah diaudit dan biaya rendah. Konsekuensinya: sinonim di luar any_of, pengalaman implisit, dan hubungan semantik kompleks bisa terlewat. Hal itu dinyatakan sebagai kebutuhan klarifikasi, bukan kekurangan kompetensi yang pasti.

## Hubungan dengan referensi

- Lo et al. (2025), *AI Hiring with LLMs: A Context-Aware and Explainable Multi-Agent Framework for Resume Screening*, bagian 4: pemisahan extractor, evaluator, summarizer, formatter. Diadaptasi sebagai fungsi, tanpa mengadopsi scoring, RAG, atau agent tambahan.
- Sainz et al. (2024), *GoLLIE*: pentingnya definisi dan panduan ekstraksi. Digunakan sebagai dasar prompt/kontrak; model tidak dilatih ulang.
- Geng et al. (2025), *JSONSchemaBench*: kepatuhan struktur dan kualitas isi adalah dimensi berbeda. Keduanya dipisahkan dalam pemeriksaan.
- Thomas & Vince (2026), *What 1,114 Documents Reveal About Schema-Driven Extraction*: membedakan extraction errors dan correct absence; evaluasi mock tidak digeneralisasi menjadi kualitas dokumen riil.
- Kupfer et al. (2023), *Check the box! How to deal with automation bias in AI-based personnel selection*: pentingnya verifikasi dan informasi potensi kesalahan, diimplementasikan melalui bukti dan koreksi reviewer.
- Augey et al. (2026), *RAPIDS*: heuristik bukan jaminan deteksi seluruh manipulasi; batas keamanan dinyatakan eksplisit.

Referensi dibaca dari PDF yang disediakan untuk persiapan. Tidak disertakan ulang sebagai salinan paper dalam paket.
