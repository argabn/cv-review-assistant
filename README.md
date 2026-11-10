# CV Review Assistant

Evidence-based CV review with structured extraction, explicit job criteria, and human oversight.

By **Arga Bona Simarmata**.

## Scope

A small Python workflow that reads a CV, extracts candidate facts, checks their source evidence, and suggests a review action. The final hiring decision always remains with a person.

Supports PDF, UTF-8 text, and bounded ZIP batches. A deterministic mock demo runs without an API or model; an optional Ollama adapter performs local LLM extraction.
