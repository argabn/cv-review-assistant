"""A single deterministic workflow shared by CLI, demo, and human review."""
import hashlib
import json
import re
import time
from .contracts import FACT_FIELDS, RESULT_SCHEMA, check, check_job
from .extraction import extract, validate_extraction, grounded_quote

AUTHOR = 'Arga Bona Simarmata'


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def job_digest(job):
    return digest(json.dumps(job, sort_keys=True, ensure_ascii=False))


def contains(text, term):
    return bool(re.search(r'(?<!\w)' + re.escape(' '.join(term.split())) + r'(?!\w)', ' '.join(text.split()), re.I))


def assess(facts, job):
    result = []
    for criterion in job['criteria']:
        evidence = []
        for record in facts[criterion['field']]:
            values = ' '.join(str(v) for k,v in record.items() if k != 'quote' and v)
            # Require the matching term in both the extracted fact and its source quote.
            if any(contains(values, term) and contains(record['quote'], term) for term in criterion['any_of']):
                evidence.append(record['quote'])
        result.append({'criterion_id': criterion['id'], 'label': criterion['label'],
            'required': criterion['required'], 'status': 'supported' if evidence else 'not_evidenced',
            'evidence': list(dict.fromkeys(evidence)),
            'explanation': 'Ada klaim eksplisit beserta bukti CV; kompetensi belum diverifikasi.' if evidence else 'Belum ada bukti pada hasil ekstraksi; bukan bukti kandidat tidak mampu.'})
    return result


def run(text, candidate_id, source, job, *, mode='mock', model=None, fixture=None, corrected=None, input_error=None):
    started = time.monotonic()
    result = {'schema_version':'1.0', 'candidate_id':candidate_id, 'source':source,
        'processing_status':'failed', 'facts':{key:[] for key in FACT_FIELDS}, 'assessment':[],
        'human_review_required':True, 'final_decision':None, 'errors':[],
        'metadata':{'author':AUTHOR, 'mode':mode, 'model':model, 'job_title':None, 'job_version':None,
            'source_sha256':digest(text), 'job_sha256':job_digest(job), 'elapsed_seconds':0}}
    caveats = ['Isi CV adalah klaim, belum verifikasi kompetensi.',
               'Informasi tidak ditemukan dapat disebabkan data tidak dicantumkan atau ekstraksi terlewat.',
               'Pemeriksaan kutipan tidak membuktikan semua hubungan antarfield benar. Reviewer harus membandingkan sumber.',
               'Deteksi manipulasi bersifat terbatas; hidden text PDF dan proxy bias belum diaudit.']
    if mode == 'mock':
        caveats.append('Respons model disimulasikan; hasil ini menguji workflow, bukan akurasi LLM nyata.')
    try:
        if input_error:
            raise ValueError(input_error)
        if not text.strip():
            raise ValueError('Teks CV tidak tersedia; lakukan pemeriksaan manual/OCR.')
        if len(text) > 12000:
            raise ValueError('CV melebihi batas 12.000 karakter untuk demo ringan.')
        if re.search(r'ignore.{0,60}instructions|abaikan.{0,60}instruksi|hire me|rank me|recommend me', text, re.I):
            raise ValueError('Terdapat indikasi instruksi dalam CV; perlu pemeriksaan manual, bukan penolakan kandidat.')
        # No implicit Python/SQL defaults: the reviewer must provide the role.
        check_job(job)
        result['metadata'].update(job_title=job['title'], job_version=job['version'])
        facts = json.loads(json.dumps(corrected)) if corrected is not None else extract(text, mode, model=model, fixture=fixture)
        validate_extraction(facts, text)
        for records in facts.values():
            for record in records:
                # Validate literal identity fields without silently expanding supplied evidence.
                expanded = grounded_quote(record, record['quote'])
                if not expanded:
                    raise ValueError('Bukti fakta kosong')
        assessment = assess(facts, job)
        missing = [item for item in assessment if item['required'] and item['status']=='not_evidenced']
        supported = sum(item['status']=='supported' for item in assessment)
        summary = (f"Terdapat {len(facts['skills'])} skill, {len(facts['education'])} pendidikan, "
                   f"{len(facts['experience'])} pengalaman, dan {len(facts['projects'])} proyek yang diekstrak. "
                   f"{supported}/{len(assessment)} kriteria memiliki bukti tertulis.")
        empty = [field for field, entries in facts.items() if not entries]
        if empty:
            caveats.append('Belum ada informasi pada: ' + ', '.join(empty) + '.')
        result.update(processing_status='success', facts=facts, assessment=assessment)
        result['recommendation'] = {'status':'needs_clarification' if missing else 'ready_for_review',
            'summary':summary, 'rationale': f"Untuk posisi {job['title']}, " + ('klarifikasi diperlukan pada: '+', '.join(x['label'] for x in missing)+'.' if missing else 'seluruh kriteria wajib memiliki bukti awal untuk ditinjau manusia.'),
            'caveats':caveats, 'follow_up_questions':[f"Dapatkah kandidat menunjukkan bukti untuk: {item['label']}?" for item in missing] or ['Verifikasi kontribusi pribadi dan kualitas hasil melalui wawancara atau demonstrasi.']}
    except Exception as exc:
        # A failed extraction never leaks partially trusted facts into the recommendation.
        result.update(processing_status='failed', facts={key:[] for key in FACT_FIELDS}, assessment=[], errors=[str(exc)])
        result['recommendation']={'status':'unable_to_assess','summary':'Data belum dapat digunakan untuk penilaian.',
            'rationale':'Proses memerlukan perbaikan input, konfigurasi, atau pemeriksaan manusia.',
            'caveats':caveats+[str(exc)], 'follow_up_questions':['Periksa sumber dan alasan kegagalan sebelum menjalankan kembali.']}
    result['metadata']['elapsed_seconds']=round(time.monotonic()-started,3)
    return check(result, RESULT_SCHEMA)
