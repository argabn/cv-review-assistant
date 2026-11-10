# Verification record

- Python 3.11.9; 22 automated tests passed.
- Synthetic workflow evaluation: 9/9 behavioral cases passed.
- CLI demo, CLI review, and genuine Ollama smoke test completed.
- Model: qwen2.5:1.5b; one short synthetic CV, sequential local request.
- No user CV is included in this package.

## Real-model smoke test

Processing succeeded; schema and literal evidence checks passed. Four criteria have source support; final_decision remains null. This verifies connectivity and the workflow on one synthetic example, not production readiness.

Exact-record comparison against the manual reference:

```json
{
  "correct_records": 2,
  "wrong_or_extra_records": 3,
  "missed_records": 3,
  "correct_empty_sections": 0,
  "precision": 0.4,
  "recall": 0.4
}
```

The model merges the degree and field into the degree value, adds a description where the reference stores null, and includes technology wording in the project name. Exact-record metrics count these differences conservatively. Passing the workflow does not mean perfect extraction. Quotes can be broader than needed. The reviewer should check these fields; the correction flow exists for this reason.

Mock evaluation and real-model evaluation are deliberately reported separately. Samples used during development are not an independent holdout set.

UI revision: candidate profile and criterion evidence matrix; structured correction form with add/remove entries; review history shown; assignment branding removed. JavaScript syntax checked. Automated HTML checks cover escaping, mode labels, corrections and review history. No comprehensive visual or accessibility audit claimed.

Dependency-free JavaScript behavior test passed: structured correction add/remove, unmodified export, and required reviewer validation. All generated reports passed anchor/ID checks and output-schema validation.

## Limited dataset validation

A subsequent, local validation used three purposefully selected IT resume examples from an archive the user identified as [Snehaan Bhawal's Resume Dataset on Kaggle](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset). The publisher describes examples collected from LiveCareer. Kaggle metadata marks the dataset public with a CC0 license; it does not establish that all documents are synthetic or fully anonymized. The local archive was not exhaustively matched against the published version.

One document completed extraction; one was blocked because the model generated unsupported employment dates; another was blocked by the input-context budget after an unrecognized section heading. This is operational success on 1/3 selected documents, not a population accuracy estimate. The sample was small, not random, and included a document used during earlier debugging.

The external dataset documents, extracted text, model responses, and document identifiers from that test are excluded from this repository. The included demo and evaluation fixtures are independently authored synthetic examples. No hidden change or successful-only selection was applied to these results. The date extraction and context/heading handling remain known limitations.
