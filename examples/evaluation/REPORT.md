# Evaluation — mock workflow

9/9 behavioral cases passed. These are workflow results, not model accuracy.

| Case | Outcome |
|---|---|
| normal | PASS |
| missing | PASS |
| omission | PASS |
| injection | PASS |
| empty | PASS |
| invalid_response | PASS |
| fabricated_evidence | PASS |
| missing_job | PASS |
| synthetic_identity_pair | PASS |

Deliberate omission: {"correct_records": 4, "wrong_or_extra_records": 0, "missed_records": 1, "correct_empty_sections": 0, "precision": 1.0, "recall": 0.8}

- Fixture responses are prepared; this does not estimate real LLM accuracy.
- Gold labels are manually authored synthetic examples, not an independent representative benchmark.
- Record-level exact comparison is conservative and sensitive to paraphrase.
- Omission case intentionally has imperfect recall; passing means the gap was handled correctly.