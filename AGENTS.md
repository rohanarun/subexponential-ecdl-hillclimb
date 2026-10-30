# Agent instructions

You are working in a research repository around a **conditional** paper. The
most important rule is: do not turn a conditional claim into an unconditional
one.

## Mission

Advance one claim in `CLAIMS.md` at a time. A claim advances only when its
verifier passes and its evidence column points at the committed artifact.

## Hard rules

1. **Never claim an unconditional ECDL break.** `C14` and `C15` are
   `conditional`. `C16` is `not-claimed`.
2. **Do not edit `AXIOMS.md`.** The only axiom is `A1` (Theorem D.1).
3. **Do not edit claim statuses.** Only a reviewed PR may change `CLAIMS.md`.
   Agents may add evidence paths in their task branch, but a curator merges the
   status change.
4. **Do not edit `eval/verify_claims.py` or a task's verifier** to make a task
   pass. If the verifier is wrong, open an issue.
5. **Do not use `sorry`** in a file that backs a `proved` claim.
6. **Preserve negative results.** A failed experiment, a counterexample, or a
   refutation is evidence. Do not delete it.
7. **No real cryptographic targets.** Toy curves only. Do not include private
   keys, live secrets, account data, or attack instructions against deployed
   systems.
8. **Do not fabricate measurements.** If you did not run it, say so. If it is a
   estimate, label it.

## Workflow

1. Pick an `open` task from `tasks/`.
2. Read its claim and inputs.
3. Implement the smallest change that makes the verifier meaningful.
4. Run:

   ```sh
   python3.12 -m pytest -q
   python3.12 eval/verify_claims.py
   python3.12 eval/run_task.py tasks/<your-task>.yaml
   ```

5. Commit the source, tests, and task result.
6. Open a PR that states:
   - the claim ID;
   - what changed;
   - the verifier output;
   - what is still not proved.

## Claim promotion

- `open -> tested`: add a test that fails before the change and passes after.
- `open/tested -> proved`: add a Lean theorem with no `sorry`.
- `conditional` stays conditional until every dependency is `proved`.
- `assumed` is only for `A1`.

## Style

- Keep the code small and literal. This is a semantics-first repository.
- Prefer exact arithmetic over floating point.
- Every nontrivial function gets a test with a concrete small case.
- If a construction is a baseline rather than the paper's, say so in the
  docstring and in `CLAIMS.md`.
