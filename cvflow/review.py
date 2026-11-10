"""A review receipt preserves the original and re-evaluates corrected facts."""
import json
from datetime import datetime, timezone
from .contracts import REVIEW_SCHEMA, RESULT_SCHEMA, check
from .pipeline import digest, job_digest, run


def apply_review(original, review, text, job):
    check(original, RESULT_SCHEMA)
    check(review, REVIEW_SCHEMA)
    if review['candidate_id'] != original['candidate_id']:
        raise ValueError('Candidate ID does not match')
    if digest(text) != original['metadata']['source_sha256']:
        raise ValueError('Source changed; rerun extraction before review')
    if job_digest(job) != original['metadata']['job_sha256']:
        raise ValueError('Job criteria changed; rerun evaluation before review')
    corrected = review['corrected_facts']
    if original['processing_status'] == 'failed' and corrected is None:
        raise ValueError('Failed result needs corrected facts or a new extraction')
    updated = run(text, original['candidate_id'], original['source'], job, mode='human_corrected',
                  corrected=original['facts'] if corrected is None else corrected)
    if updated['processing_status'] != 'success':
        raise ValueError('Correction rejected: ' + '; '.join(updated['errors']))
    return {'original_sha256': digest(json.dumps(original,sort_keys=True,ensure_ascii=False)),
            'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),
            'review':review, 'result':updated,
            'notice':'Catatan review manusia; bukan keputusan hiring otomatis. Identitas reviewer belum diautentikasi pada prototype lokal.'}
