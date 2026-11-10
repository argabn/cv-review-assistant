import json
import unittest
from unittest.mock import MagicMock, patch
from cvflow.extraction import _extract, grounded_quote
from cvflow.documents import text_from_bytes

class ModelTests(unittest.TestCase):
    def response(self,payload):
        response=MagicMock();response.__enter__.return_value.read.return_value=json.dumps(payload).encode();return response
    def test_truncation_is_explicit(self):
        with patch('cvflow.extraction.urlopen',return_value=self.response({'done_reason':'length','message':{'content':'{'}})):
            with self.assertRaisesRegex(ValueError,'token limit'):
                _extract('Python','ollama',model='test')
    def test_source_lines_resolve_original_whitespace(self):
        output={'skills':[{'name':'Python','source_lines':[2]}],'education':[],'experience':[],'projects':[]}
        with patch('cvflow.extraction.urlopen',return_value=self.response({'done_reason':'stop','message':{'content':json.dumps(output)}})):
            facts=_extract('CV\n\nSkills: Python.\n','ollama',model='test')
        self.assertEqual(facts['skills'][0]['quote'],'Skills: Python.')
    def test_context_budget_rejects_before_request(self):
        with patch('cvflow.extraction.urlopen') as request:
            with self.assertRaisesRegex(ValueError,'context budget'):
                _extract('x'*3001,'ollama',model='test')
            request.assert_not_called()
    def test_literal_identity_cannot_be_invented(self):
        with self.assertRaises(ValueError):
            grounded_quote({'role':'CEO','quote':'Developer'},'Developer')
    def test_corrupt_pdf_fails(self):
        with self.assertRaises(Exception):
            text_from_bytes('broken.pdf',b'not a pdf')

if __name__=='__main__':unittest.main()
