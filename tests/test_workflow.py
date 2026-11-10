import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from cvflow.pipeline import run
from cvflow.evaluation import load, SAMPLES, compare
from cvflow.review import apply_review
from cvflow.documents import documents
from cvflow.contracts import RESULT_SCHEMA, check
from cvflow.report import render

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.job=load('job.json');self.text=(SAMPLES/'cv.txt').read_text()
    def result(self,fixture='response.json',**kwargs):
        return run(self.text,'C-0001','cv.txt',self.job,fixture=SAMPLES/fixture,**kwargs)
    def test_complete_contract(self):
        r=self.result();check(r,RESULT_SCHEMA)
        self.assertEqual(r['recommendation']['status'],'ready_for_review')
        self.assertIsNone(r['final_decision'])
    def test_missing_is_clarification(self):
        self.assertEqual(self.result('response_omission.json')['recommendation']['status'],'needs_clarification')
    def test_fabrication_is_failure(self):
        r=self.result('response_fabricated.json')
        self.assertEqual(r['processing_status'],'failed');self.assertFalse(r['facts']['skills'])
    def test_provider_failure_has_valid_envelope(self):
        with patch('cvflow.pipeline.extract',side_effect=TimeoutError('timeout')):
            r=self.result()
        check(r,RESULT_SCHEMA);self.assertEqual(r['recommendation']['status'],'unable_to_assess')
    def test_review_recalculates_without_mutating_original(self):
        before=self.result('response_omission.json');snapshot=copy.deepcopy(before)
        receipt=apply_review(before,load('review.json'),self.text,self.job)
        self.assertEqual(receipt['result']['recommendation']['status'],'ready_for_review')
        self.assertEqual(before,snapshot)
    def test_review_rejects_changed_source(self):
        with self.assertRaises(ValueError):
            apply_review(self.result(),load('review.json'),self.text+'altered',self.job)
    def test_review_rejects_changed_job(self):
        changed=copy.deepcopy(self.job);changed['version']='2'
        with self.assertRaises(ValueError):
            apply_review(self.result(),load('review.json'),self.text,changed)
    def test_review_rejects_fabricated_correction(self):
        receipt=load('review.json');receipt['corrected_facts']['skills'][0]['name']='Kubernetes'
        with self.assertRaises(ValueError):
            apply_review(self.result(),receipt,self.text,self.job)
    def test_exact_word_matching(self):
        from cvflow.pipeline import contains
        self.assertFalse(contains('JavaScript','Java'))
        self.assertTrue(contains('Python, SQL.','sql'))
    def test_metrics_detect_omission(self):
        metrics=compare(load('response_omission.json'),load('gold.json'))
        self.assertEqual(metrics['missed_records'],1);self.assertLess(metrics['recall'],1)
    def test_zip_limit_and_no_path_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            archive=Path(folder)/'sample.zip'
            with zipfile.ZipFile(archive,'w') as z:
                z.writestr('../one.txt','CV one');z.writestr('two.txt','CV two')
            self.assertEqual(len(list(documents(archive,limit=1))),1)
            self.assertFalse((Path(folder)/'one.txt').exists())
    def test_html_escapes_untrusted_source(self):
        r=self.result();r['source']='<img src=x onerror=alert(1)>'
        page=render({'job':self.job,'results':[r]})
        self.assertNotIn('<img src=x',page);self.assertIn('&lt;img',page)
    def test_input_error_is_not_missing_skill(self):
        r=self.result(input_error='Unreadable PDF')
        self.assertEqual(r['assessment'],[]);self.assertEqual(r['processing_status'],'failed')
    def test_no_job_never_uses_defaults(self):
        r=run(self.text,'C1','cv.txt',None,fixture=SAMPLES/'response.json')
        self.assertEqual(r['recommendation']['status'],'unable_to_assess')

if __name__=='__main__':unittest.main()

class ReportTests(unittest.TestCase):
    def result(self):
        return run((SAMPLES/'cv.txt').read_text(),'C-0001','cv.txt',load('job.json'),fixture=SAMPLES/'response.json')
    def test_no_assignment_branding_and_mock_is_visible(self):
        page=render({'job':load('job.json'),'results':[self.result()]})
        self.assertNotIn('MINI ASSIGNMENT',page)
        self.assertNotIn('SK Batch',page)
        self.assertIn('Simulasi',page)
        self.assertIn('Arga Bona Simarmata',page)
    def test_correction_supports_add_remove(self):
        page=render({'job':load('job.json'),'results':[self.result()]})
        self.assertIn('data-new',page)
        self.assertIn('data-remove',page)
        self.assertIn('data-key="quote"',page)
    def test_review_history_is_displayed_and_escaped(self):
        page=render({'job':load('job.json'),'results':[self.result()],
                     'review':{'reviewer':'Reviewer','action':'reviewed','notes':'<script>unsafe</script>'}})
        self.assertIn('Review terakhir',page)
        self.assertIn('&lt;script&gt;unsafe&lt;/script&gt;',page)
        self.assertNotIn('<script>unsafe</script>',page)
