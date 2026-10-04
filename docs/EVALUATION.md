# Evaluate the evaluator

Before using findings for product decisions:

1. Assemble consented or fictional interfaces covering multiple screen states, devices and tasks. Document missing states.
2. Have qualified human evaluators independently inspect the same evidence using the same heuristic definitions. Resolve disagreements transparently; do not assume the AI or any single evaluator is ground truth.
3. Compare AI observations with adjudicated human findings: supported, unsupported, duplicate, missed and not assessable. Report counts and denominators; avoid scores without defined weighting.
4. Inspect whether severity reasoning is credible. Frequency and persistence cannot normally be inferred from screenshots. Validate material risks in an interactive prototype and, where appropriate, with real participants.
5. Test hallucinated labels, embedded malicious instructions, unfamiliar terminology, multilingual screens, dense layouts and absent error states.
6. Record model deployment/version, date, prompts, source hashes, costs, run-to-run variation and decisions. This app records task and evidence metadata but not an immutable audit trail.
7. For accessibility, separately inspect code/semantics, contrast, focus, keyboard and assistive technology behaviour using appropriate methods. Do not infer WCAG compliance from this tool.

Initial status: offline functional tests only. No live Azure result, researcher study, model reliability rate or user-adoption result has been established.
