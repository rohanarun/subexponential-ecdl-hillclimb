# Auto-research instructions

This is the entry point for research agents. Read this file before touching the
repository. It tells you which track to pick, how to run the verifier, and how to
record a result — including a negative one.

The repository studies a **conditional** paper. `C14` and `C15` are
`conditional`, `C16` is `not-claimed`, and the only axiom is `A1` (Theorem D.1 of
OpenAI). Do not turn any of that into an unconditional ECDL claim.

## The Core Hillclimbing Objective: Breaking and Tightening the Bounds

The overarching mission of this repository is to **hillclimb the mathematical and
operational bounds** of the ECDL reduction:

1. **The $2^{217}$ Feasibility Bound (Track D)**: Theorem D.1 of `[Ope26]` has an astronomical
   cutoff where $\lfloor s / 2^{217} \rfloor = 0$, rendering the algorithm completely inactive
   for any deployable curve size ($s < 2^{217} \approx 2.11 \times 10^{65}$). Hillclimbers
   investigate whether the partition and tree-decomposition parameters can be tightened to
   a realistic finite scale ($s \le 10^5$).
2. **The Encoding Degree Bound $\Delta$ (Track A)**: Theorem 3 achieves degree $O(d^{3/4})$
   via a 2-stage Fourier transform split ($L = L_1 L_2$). Hillclimbers construct multi-stage
   splits ($k \ge 3$) to improve the degree bound toward $O(d^{2/3})$ and $O(d^{1/2})$.
3. **Concrete Constant Compression (Track A)**: The paper upper-bounds edge count by $< 1,100(d+1)$
   and degree by $< 136(d+1)^{3/4}$. Hillclimbers optimize limb packing and carry propagation
   to drive these constants to their minimal mathematical limits.

## The one rule

> A result is evidence only if another person can rerun the command and get the
> same outcome.

Everything else follows from that: exact commands, exact environment, committed
artifacts, and no self-reported success without a verifier.

## What counts as a contribution

All of these are welcome and belong in `auto-research/`:

| Outcome | Meaning |
|---|---|
| `positive` | The task verifier passed and the claim's evidence is stronger. |
| `negative` | A concrete attempt failed. No claim changes. This is useful. |
| `inconclusive` | You ran the check, but it cannot distinguish the hypotheses. |
| `reproduced` | You reproduced an existing result, including an existing failure. |
| `refuted` | You have a minimal counterexample to a specific claim. |

A negative result is **not** a refutation. "My construction failed" is
`negative`; "here is a counterexample to Lemma 10 at the stated parameters" is
`refuted`. Keep the distinction.

Negative results are never deleted. They are the record of what did not work.

## Pick a track

Choose one track. Do not mix tracks in one result folder.

| Track | Folder | Tasks | Claims | Difficulty | Start here |
|---|---|---|---|---|---|
| A. Low-degree encodings | `auto-research/encodings/` | T06, T07, T08 | C5, C6, C11 | high | `docs/paper-notes.md#theorem-3`, `#lemma-8`, `#lemma-11` |
| B. Factor-base coverage | `auto-research/coverage/` | T09 | C9, C10 | medium | `docs/paper-notes.md#lemma-10` |
| C. Lean 4 formalization | `auto-research/lean/` | T10 | C14 | high | `lean/README.md`, `AXIOMS.md` |
| D. Theorem D.1 audit | `auto-research/d1-audit/` | T11 | C17 | high, independent | `AXIOMS.md#a1` |
| E. Reproduction and negative results | `auto-research/reproduction/` | T01-T05 | C1, B1-B4 | low to medium | `README.md`, `tasks/` |
| F. New claim or task | `auto-research/other/` | new | new | any | open an issue first |

Track A is the critical path for the paper's reduction: the table encodings in
`src/btn/encodings/` are only semantic oracles. Track D is the critical path for
the external dependency: a refutation there is a valid and important outcome.

If you are unsure, start with Track E. Reproduce the toy demo and one test, then
write a `reproduced` result. That teaches you the workflow without a large
implementation.

## Before you start

1. Read `CLAIMS.md`, `AXIOMS.md`, and `docs/non-claims.md`.
2. Read the task YAML for your chosen task in `tasks/`.
3. Set up the environment:

   ```sh
   python3.12 -m pip install -r requirements.txt
   python3.12 -m pytest -q
   python3.12 eval/verify_claims.py
   ```

4. Run the task verifier once before changing anything. If it already passes,
   the task may be done; pick another task or write a `reproduced` result.

## Workflow

1. Pick a track and an `open` task from `tasks/`.
2. Create a branch: `git checkout -b auto-research/<track>-<task>-<slug>`.
3. Make the smallest change that makes the verifier meaningful.
4. Run the task verifier:

   ```sh
   python3.12 eval/run_task.py tasks/<task>.yaml
   ```

5. Run the full checks:

   ```sh
   python3.12 -m pytest -q
   python3.12 eval/verify_claims.py
   python3.12 eval/verify_results.py
   ```

6. Write the result under `auto-research/<track>/<YYYY-MM-DD>-<task>-<slug>/`.
   Use `auto-research/_template/` as the starting point.
7. Add a row to the index in `auto-research/README.md`.
8. Commit the source, tests, task result, and research result. Open a PR.

## Result folder format

```text
auto-research/<track>/<YYYY-MM-DD>-<task>-<slug>/
├── README.md          human-readable write-up
├── result.json        machine-readable metadata
└── artifacts/         optional small logs, patches, or measurements
```

Rules:

- The folder name is the `run_id`. It must match `result.json["run_id"]`.
- `README.md` must say what was tried, the exact command, the expected and
  observed outcome, and what the result does **not** establish.
- `result.json` must validate with `python3.12 eval/verify_results.py`.
- Artifacts must stay inside the result folder. Use relative paths.
- Keep artifacts small (under 5 MB total). Do not commit raw provider logs,
  credentials, or account data.
- Do not put results directly in `auto-research/`; always use a track folder.

### `result.json`

```json
{
  "run_id": "2026-11-02-T06-dft-mult",
  "agent": "agent or model name",
  "date": "2026-11-02",
  "track": "encodings",
  "task": "T06",
  "claim": "C5",
  "outcome": "negative",
  "summary": "One or two sentences. State the observed outcome, not a hope.",
  "commands": ["python -m pytest tests/test_int_mult_lowdegree.py -q"],
  "environment": "Python 3.12.13, macOS 15.6, commit abc1234",
  "artifacts": ["artifacts/pytest.log"],
  "claim_status_recommendation": "no-change",
  "notes": "What failed, why, and what would change the conclusion."
}
```

Allowed `outcome`: `positive`, `negative`, `inconclusive`, `reproduced`,
`refuted`.

Allowed `claim_status_recommendation`: `no-change`, `promote-tested`,
`promote-proved`, `refute`.

Only a curator merges a status change. Your result can recommend one; it cannot
perform it.

## Writing a negative result

A good negative result answers:

1. **Question.** Which claim or sub-claim were you testing?
2. **Attempt.** What construction or check did you try?
3. **Command.** The exact command a reader can rerun.
4. **Expected.** What would have counted as success?
5. **Observed.** The actual output, including the failing case.
6. **Why it failed.** Your best explanation, clearly labelled as a hypothesis if
   it is one.
7. **What would change the conclusion.** A different parameter, a missing lemma,
   a bug in the oracle, etc.
8. **Next step.** The smallest useful follow-up.

Do not write "it didn't work" without a command and an observed output. Do not
delete the branch or the result if the approach fails.

## Evidence rules

- No fabricated measurements. If you did not run it, say so.
- No claim that a bounded test proves a general theorem. `tested` is bounded.
- No claim that a negative result refutes a claim. Use `refuted` only with a
  minimal counterexample.
- No real cryptographic targets. Toy curves only.
- No private keys, live secrets, account data, or attack instructions against
  deployed systems.
- If an artifact contains a provider log, redact credentials and account data
  before committing; if that is impossible, commit only a hash and a summary.

## Claim promotion

A result can recommend:

- `promote-tested` when a committed test fails before the change and passes
  after it.
- `promote-proved` when a Lean theorem with no `sorry` backs the claim.
- `refute` when a minimal counterexample exists.

A `negative` or `inconclusive` result normally recommends `no-change`. That is
still a contribution: it narrows the search space and prevents duplicate work.

## PR checklist

- [ ] The task verifier passes, or the result explains exactly why it fails.
- [ ] `auto-research/<track>/<run_id>/README.md` and `result.json` are committed.
- [ ] The index row in `auto-research/README.md` is added.
- [ ] `python3.12 -m pytest -q` passes.
- [ ] `python3.12 eval/verify_claims.py` passes.
- [ ] `python3.12 eval/verify_results.py` passes.
- [ ] No changes to `AXIOMS.md`, claim status cells, or verifier scripts.
- [ ] No secrets, real targets, or unredacted logs.

## Copy-paste prompt

If you are an agent and need a starting instruction, use this:

> Read `auto-research.md` in this repository and follow it. Pick one research
> track, run the task verifier, and add your result — including negative or
> inconclusive results — under `auto-research/`. Do not edit `AXIOMS.md`, claim
> statuses, or verifier scripts.
