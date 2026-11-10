"""Reproducible synthetic workflow evaluation; never presented as real LLM accuracy."""
import json
from pathlib import Path
from .pipeline import run, AUTHOR
from .contracts import FACT_FIELDS
from .review import apply_review

ROOT=Path(__file__).resolve().parents[1]
SAMPLES=ROOT/'samples'


def load(name):
    return json.loads((SAMPLES/name).read_text())


def facts_as_set(facts):
    return {(field,json.dumps({k:v for k,v in record.items() if k!='quote'},sort_keys=True))
            for field in FACT_FIELDS for record in facts[field]}


def compare(predicted,gold):
    actual,expected=facts_as_set(predicted),facts_as_set(gold)
    correct=len(actual&expected);false=len(actual-expected);miss=len(expected-actual)
    return {'correct_records':correct,'wrong_or_extra_records':false,'missed_records':miss,
            'correct_empty_sections':sum(not gold[k] and not predicted[k] for k in FACT_FIELDS),
            'precision':correct/len(actual) if actual else None,'recall':correct/len(expected) if expected else None}


def evaluate():
    job=load('job.json')
    cases=[
      ('normal','cv.txt','response.json','ready_for_review','success','gold.json',job),
      ('missing','cv_missing.txt','response_missing.json','needs_clarification','success','response_missing.json',job),
      ('omission','cv.txt','response_omission.json','needs_clarification','success','gold.json',job),
      ('injection','cv_attack.txt','response.json','unable_to_assess','failed',None,job),
      ('empty','cv_empty.txt','response.json','unable_to_assess','failed',None,job),
      ('invalid_response','cv.txt','response_invalid.json','unable_to_assess','failed',None,job),
      ('fabricated_evidence','cv.txt','response_fabricated.json','unable_to_assess','failed',None,job),
      ('missing_job','cv.txt','response.json','unable_to_assess','failed',None,None),
    ]
    rows=[]
    for name,cv,response,status,processing,gold,criteria in cases:
        result=run((SAMPLES/cv).read_text(),name,cv,criteria,fixture=SAMPLES/response)
        passed=result['recommendation']['status']==status and result['processing_status']==processing
        rows.append({'case':name,'passed':passed,'expected_status':status,'actual_status':result['recommendation']['status'],
                     'extraction_metrics':compare(result['facts'],load(gold)) if gold else None})
    original=(SAMPLES/'cv.txt').read_text()
    a=run(original,'PAIR-A','pair-a.txt',job,fixture=SAMPLES/'response.json')
    b=run(original.replace('DEMO-001','DEMO-OTHER'),'PAIR-B','pair-b.txt',job,fixture=SAMPLES/'response.json')
    rows.append({'case':'synthetic_identity_pair','passed':a['facts']==b['facts'] and a['assessment']==b['assessment'],
                 'scope':'Mock invariance only; not a fairness audit of a model'})
    output=ROOT/'output/evaluation';output.mkdir(parents=True,exist_ok=True)
    payload={'mode':'mock','case_count':len(rows),'passed':sum(r['passed'] for r in rows),'cases':rows,
             'limitations':['Fixture responses are prepared; this does not estimate real LLM accuracy.',
             'Gold labels are manually authored synthetic examples, not an independent representative benchmark.',
             'Record-level exact comparison is conservative and sensitive to paraphrase.',
             'Omission case intentionally has imperfect recall; passing means the gap was handled correctly.']}
    (output/'metrics.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False))
    table='\n'.join('| '+r['case']+' | '+('PASS' if r['passed'] else 'FAIL')+' |' for r in rows)
    omission=next(r['extraction_metrics'] for r in rows if r['case']=='omission')
    (output/'REPORT.md').write_text('# Evaluation — mock workflow\n\n'+f"{payload['passed']}/{len(rows)} behavioral cases passed. These are workflow results, not model accuracy.\n\n| Case | Outcome |\n|---|---|\n"+table+'\n\nDeliberate omission: '+json.dumps(omission)+'\n\n'+ '\n'.join('- '+x for x in payload['limitations']))
    print(f"Evaluation: {payload['passed']}/{len(rows)} cases. {output}")
    if not all(row['passed'] for row in rows):
        raise ValueError('Evaluation failed')
    return payload


def demo():
    from .__main__ import save
    job=load('job.json');text=(SAMPLES/'cv.txt').read_text()
    normal=run(text,'C-0001','cv.txt',job,fixture=SAMPLES/'response.json')
    save({'author':AUTHOR,'job':job,'results':[normal]},ROOT/'output/demo')
    before=run(text,'C-0001','cv.txt',job,fixture=SAMPLES/'response_omission.json')
    save({'author':AUTHOR,'job':job,'results':[before]},ROOT/'output/review-before')
    reviewed=apply_review(before,load('review.json'),text,job)
    save({'author':AUTHOR,'job':job,'results':[reviewed['result']], 'review':reviewed['review']},ROOT/'output/review-after')
    (ROOT/'output/review-after/review_receipt.json').write_text(json.dumps(reviewed,ensure_ascii=False,indent=2))
    evaluate()
    print(f'Demo: {ROOT / "output/demo/report.html"}')
