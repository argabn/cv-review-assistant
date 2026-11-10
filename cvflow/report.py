"""Accessible, self-contained candidate review report. No external assets."""
import html
import json
from pathlib import Path

ASSETS = Path(__file__).parent / 'assets'
STATUS = {
    'ready_for_review': ('Siap ditinjau', 'ready'),
    'needs_clarification': ('Perlu klarifikasi', 'clarify'),
    'unable_to_assess': ('Belum dapat dinilai', 'failed'),
}
FIELD_LABELS = {'name':'Nama', 'degree':'Gelar', 'field':'Bidang', 'institution':'Institusi',
                'role':'Jabatan', 'organization':'Organisasi', 'period_raw':'Periode',
                'description':'Deskripsi', 'quote':'Kutipan sumber'}


def esc(value):
    return html.escape(str(value if value is not None else 'Tidak disebutkan'), quote=True)


def evidence(quote):
    return '<details class="evidence"><summary>Bukti sumber</summary><blockquote>'+esc(quote)+'</blockquote></details>'


def fact_section(field, label, records):
    entries=[]
    for record in records:
        primary=record.get('role') or record.get('name') or record.get('degree') or 'Informasi belum lengkap'
        secondary=' · '.join(str(record[k]) for k in ('organization','period_raw','institution','field') if record.get(k))
        entries.append('<li><strong>'+esc(primary)+'</strong>'
                       + ('<p class="muted">'+esc(secondary)+'</p>' if secondary else '')
                       + ('<p>'+esc(record['description'])+'</p>' if record.get('description') else '')
                       + evidence(record['quote'])+'</li>')
    return '<section class="fact-section"><h3>'+label+' <span class="count">'+str(len(records))+'</span></h3><ul class="records">'+''.join(entries)+'</ul>'+('' if entries else '<p class="empty">Belum ada informasi teridentifikasi.</p>')+'</section>'


def correction_editor(facts):
    # Keep editing structured; JSON is only an optional data export.
    groups=[]
    for field,label in [('skills','Keahlian'),('education','Pendidikan'),('experience','Pengalaman'),('projects','Proyek')]:
        records=[]
        for record in facts[field]:
            controls=''.join('<label>'+FIELD_LABELS.get(k,k)+'<textarea data-key="'+esc(k)+'" rows="'+('3' if k=='quote' else '1')+'">'+esc(v if v is not None else '')+'</textarea></label>' for k,v in record.items())
            records.append('<fieldset data-record><legend>'+label+'</legend>'+controls+'<label class="check"><input type="checkbox" data-remove> Hapus entri ini</label></fieldset>')
        # A blank optional record allows adding an omitted fact, not merely editing existing ones.
        keys={'skills':['name','quote'],'education':['degree','field','institution','quote'],
              'experience':['role','organization','period_raw','description','quote'],
              'projects':['name','description','quote']}[field]
        blank=''.join('<label>'+FIELD_LABELS[k]+'<textarea data-key="'+k+'" rows="'+('3' if k=='quote' else '1')+'"></textarea></label>' for k in keys)
        groups.append('<details data-field="'+field+'"><summary>'+label+'</summary>'+''.join(records)+'<fieldset data-record data-new><legend>Tambah entri</legend>'+blank+'</fieldset></details>')
    return '<div class="corrections" hidden>'+''.join(groups)+'</div>'


def review_panel(result, index):
    receipt=(result.get('_review') or {})
    history=''
    if receipt:
        history='<section class="review-history"><h3>Review terakhir</h3><p><strong>'+esc(receipt.get('reviewer',''))+'</strong></p><p>'+esc(receipt.get('notes',''))+'</p><span class="tag">'+('Klarifikasi diminta' if receipt.get('action')=='request_clarification' else 'Sudah ditinjau')+'</span></section>'
    return '<aside class="review-panel">'+history+'<h3>Catatan reviewer</h3><p class="muted">Periksa bukti sebelum menentukan tindak lanjut.</p><form data-candidate="'+esc(result['candidate_id'])+'"><label>Reviewer<input name="reviewer" autocomplete="name" required></label><label>Tindak lanjut<select name="action"><option value="reviewed">Sudah ditinjau</option><option value="request_clarification">Minta klarifikasi</option></select></label><label>Catatan<textarea name="notes" rows="4" placeholder="Temuan, hal yang perlu diverifikasi, atau pertanyaan lanjutan" required></textarea></label><label class="check"><input type="checkbox" name="correct"> Koreksi informasi kandidat</label>'+correction_editor(result['facts'])+'<button type="submit" class="primary">Ekspor review</button><p class="helper">Koreksi diterapkan setelah file review divalidasi oleh aplikasi.</p><p class="feedback" role="status" aria-live="polite"></p></form></aside>'


def candidate_card(result,index):
    rec=result['recommendation'];status,tone=STATUS[rec['status']]
    mode=result['metadata']['mode']
    mode_label={'mock':'Simulasi','ollama':'Ekstraksi AI','human_corrected':'Hasil review'}[mode]
    rows=[]
    for item in result['assessment']:
        support=item['status']=='supported'
        proof=''.join(evidence(q) for q in item['evidence']) if support else '<span class="muted">Klarifikasi diperlukan.</span>'
        rows.append('<tr><th scope="row">'+esc(item['label'])+'<small>'+('Wajib' if item['required'] else 'Tambahan')+'</small></th><td><span class="signal '+('positive' if support else 'pending')+'">'+('Ada bukti' if support else 'Belum ada bukti')+'</span></td><td>'+proof+'</td></tr>')
    facts=''.join(fact_section(k,label,result['facts'][k]) for k,label in [('experience','Pengalaman'),('projects','Proyek'),('education','Pendidikan'),('skills','Keahlian')])
    supported=sum(x['status']=='supported' for x in result['assessment'])
    metric=f'{supported}/{len(result["assessment"])} kriteria berbukti' if result['assessment'] else 'Penilaian tertahan'
    caveats=''.join('<li>'+esc(x)+'</li>' for x in rec['caveats'])
    questions=''.join('<li>'+esc(x)+'</li>' for x in rec['follow_up_questions'])
    errors='<div class="error" role="alert">'+'<br>'.join(esc(x) for x in result['errors'])+'</div>' if result['errors'] else ''
    return _candidate_body(result,index,mode_label,status,tone,rows,facts,metric,caveats,questions,errors)


def _candidate_body(result,index,mode_label,status,tone,rows,facts,metric,caveats,questions,errors):
    rec=result['recommendation']
    matrix='<div class="table-wrap"><table><caption class="sr-only">Bukti terhadap kriteria posisi</caption><thead><tr><th>Kriteria</th><th>Status</th><th>Sumber</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>' if rows else '<p class="empty">Kriteria belum dapat dievaluasi.</p>'
    return ('<article id="candidate-'+str(index)+'"><div class="candidate-header"><div class="identity"><div class="avatar">'+esc(result['candidate_id'][-2:])+'</div><div><h2>'+esc(result['candidate_id'])+'</h2><p class="muted filename">'+esc(result['source'])+'</p></div></div><div class="tags"><span class="tag">'+mode_label+'</span><span class="status '+tone+'">'+status+'</span></div></div>'
        +'<div class="candidate-layout"><div class="candidate-main">'+errors
        +'<section class="recommendation"><div class="section-title"><h3>Rekomendasi penelaahan</h3><span class="muted">'+metric+'</span></div><p>'+esc(rec['rationale'])+'</p><p class="helper">Bukti CV belum memverifikasi kompetensi. Keputusan tetap pada reviewer.</p></section>'
        +'<section class="scorecard"><h3>Kriteria posisi</h3>'+matrix+'</section><div class="profile-grid">'+facts+'</div>'
        +'<section class="follow-up"><h3>Pertanyaan lanjutan</h3><ul>'+questions+'</ul></section>'
        +'<details class="limits"><summary>Ketidakpastian dan batas penilaian</summary><ul>'+caveats+'</ul></details></div>'
        +review_panel(result,index)+'</div></article>')


def render(bundle):
    results=bundle['results'];job=bundle.get('job') or {}
    nav=''.join('<a href="#candidate-'+str(i)+'"><span>'+esc(r['candidate_id'])+'</span><small>'+STATUS[r['recommendation']['status']][0]+'</small></a>' for i,r in enumerate(results))
    styles=(ASSETS/'report.css').read_text();script=(ASSETS/'report.js').read_text()
    cards=''.join(candidate_card({**r, '_review': bundle.get('review')},i) for i,r in enumerate(results))
    return '<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Candidate Review</title><style>'+styles+'</style></head><body><a class="skip" href="#main">Ke isi utama</a><header class="appbar"><span class="brand"><span class="brand-mark">C</span>Candidate Review</span><span class="appbar-meta">Penelaahan kandidat</span></header><div class="workspace"><nav class="sidebar" aria-label="Daftar kandidat"><p class="eyebrow">KANDIDAT <span>'+str(len(results))+'</span></p>'+nav+'</nav><main id="main"><div class="page-heading"><div><p class="breadcrumb">Kandidat / Penelaahan</p><h1>'+esc(job.get('title','Posisi belum ditentukan'))+'</h1><p class="muted">Kriteria versi '+esc(job.get('version','—'))+'</p></div><a class="button" href="results.json" download>Unduh hasil</a></div>'+cards+'<details class="technical"><summary>Data terstruktur</summary><pre>'+esc(json.dumps(bundle,ensure_ascii=False,indent=2))+'</pre></details><footer>Arga Bona Simarmata</footer></main></div><script>'+script+'</script></body></html>'
