"""Explicit contracts for job configuration, extraction, and final results."""
from copy import deepcopy
from jsonschema import Draft202012Validator
from .extraction import SCHEMA, object_schema

TEXT = {'type': 'string', 'minLength': 1}
STRINGS = {'type': 'array', 'items': TEXT}
FACT_FIELDS = ('skills', 'education', 'experience', 'projects')
CRITERION = object_schema({
    'id': TEXT, 'label': TEXT, 'field': {'enum': list(FACT_FIELDS)},
    'any_of': {'type': 'array', 'items': TEXT, 'minItems': 1},
    'required': {'type': 'boolean'},
})
JOB_SCHEMA = object_schema({'title': TEXT, 'version': TEXT, 'criteria': {'type': 'array', 'items': CRITERION, 'minItems': 1}})
RECOMMENDATION = object_schema({
    'status': {'enum': ['ready_for_review', 'needs_clarification', 'unable_to_assess']},
    'summary': TEXT, 'rationale': TEXT, 'caveats': STRINGS, 'follow_up_questions': STRINGS,
})
RESULT_SCHEMA = object_schema({
    'schema_version': {'const': '1.0'}, 'candidate_id': TEXT, 'source': TEXT,
    'processing_status': {'enum': ['success', 'failed']},
    'facts': deepcopy(SCHEMA),
    'assessment': {'type': 'array', 'items': object_schema({
        'criterion_id': TEXT, 'label': TEXT, 'required': {'type': 'boolean'},
        'status': {'enum': ['supported', 'not_evidenced']},
        'evidence': STRINGS, 'explanation': TEXT,
    })},
    'recommendation': RECOMMENDATION,
    'human_review_required': {'const': True}, 'final_decision': {'type': 'null'},
    'errors': STRINGS,
    'metadata': object_schema({'author': TEXT, 'mode': {'enum': ['mock', 'ollama', 'human_corrected']},
        'model': {'type': ['string','null']}, 'job_title': {'type': ['string','null']},
        'job_version': {'type': ['string','null']}, 'source_sha256': TEXT,
        'job_sha256': TEXT, 'elapsed_seconds': {'type': 'number', 'minimum': 0}}),
})
REVIEW_SCHEMA = object_schema({
    'reviewer': TEXT, 'candidate_id': TEXT,
    'action': {'enum': ['reviewed', 'request_clarification']},
    'notes': TEXT, 'corrected_facts': {'anyOf': [deepcopy(SCHEMA), {'type':'null'}]},
})


def check(data, schema):
    Draft202012Validator(schema).validate(data)
    return data


def check_job(job):
    check(job, JOB_SCHEMA)
    ids = [item['id'] for item in job['criteria']]
    if len(ids) != len(set(ids)):
        raise ValueError('Criterion IDs must be unique')
    if any(not word.strip() for c in job['criteria'] for word in c['any_of']):
        raise ValueError('Criterion terms must not be blank')
    return job
