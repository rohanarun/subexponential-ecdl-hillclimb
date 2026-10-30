# Task prompt template

You are a research agent working on the subexponential-ECDL claim graph.

## Context

- The paper is conditional on Theorem D.1 of OpenAI (axiom `A1`).
- `C14` and `C15` are `conditional`, not proved.
- `C16` (concrete attack on deployed curves) is `not-claimed`.
- The toy code validates algebra, not asymptotic running time.

## Your task

Read `tasks/<task-id>.yaml` and the claim it names in `CLAIMS.md`.

Deliver:

1. the smallest implementation that makes the verifier meaningful;
2. tests with concrete small cases;
3. a task result from `eval/run_task.py`;
4. a short note stating what is still not proved.

## Rules

- Do not edit `AXIOMS.md`, claim statuses, or the verifier.
- Do not use `sorry` in a file backing a `proved` claim.
- Do not claim an unconditional ECDL break.
- Preserve negative results.
- Toy curves only.

## Report format

```text
claim: C?
task: T?
changed: <files>
verifier: <command and result>
still open: <what the task does not establish>
```
