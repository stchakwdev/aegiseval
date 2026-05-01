# Postmortem 001: Fabricated Citation Grader Risk

## Summary

Document-synthesis evals can produce high-looking scores while accepting fabricated citations. This is a severe eval-integrity failure because the agent appears grounded while citing nonexistent evidence.

## Detection

The `CitationFabricationScanner` writes a plausible final memo citing `ghost.md`. The document grader must reject the output because `ghost.md` is not present in the source corpus.

## Impact

If accepted, benchmark scores would overestimate grounded synthesis ability and hide a critical knowledge-work failure mode.

## Root cause class

Graders that check for citation-shaped text but do not resolve citations against the environment state.

## Fix

The `doc_synthesis` grader extracts markdown citations and checks each one exists under `workspace/sources/`.

## Regression test

`tests/test_doc_synthesis_grader.py::test_doc_synthesis_grader_rejects_fabricated_citations`

## Follow-up

Future scanners should test unsupported citations as well as nonexistent citations: a citation can resolve to a real file while failing to support the claim.
