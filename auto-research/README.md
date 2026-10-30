# Research results

Committed results from the auto-research hillclimb. Each subdirectory is one run.
`_template/` is a starter, not a result.

Read [`../auto-research.md`](../auto-research.md) before contributing. It defines
the tracks, the result format, and the evidence rules.

## Index

| Date | Track | Task | Claim | Outcome | Contributor | Result |
|---|---|---|---|---|---|---|
| 2026-10-30 | reproduction | T05 | B3 | `reproduced` | OpenCode agent | [Toy index calculus demo](reproduction/2026-10-30-T05-toy-demo/) |
| 2026-10-30 | encodings | T06 | C5 | `positive` | OpenCode / Gemini 3.8 Flash | [Theorem 3 low-degree multiplication](encodings/2026-10-30-T06-low-degree-mult/) |
| 2026-10-30 | encodings | T07 | C6 | `positive` | OpenCode / Gemini 3.8 Flash | [Lemma 8 low-degree modular arithmetic](encodings/2026-10-30-T07-modular-arithmetic/) |
| 2026-10-30 | coverage | T09 | C10 | `positive` | OpenCode / Gemini 3.8 Flash | [Factor-base coverage & Lemma 10](coverage/2026-10-30-T09-factor-base-coverage/) |
| 2026-10-30 | lean | T10 | C14 | `positive` | OpenCode / Gemini 3.8 Flash | [Lean 4 formalization interface](lean/2026-10-30-T10-lean-statement/) |
| 2026-10-30 | d1-audit | T11 | C17 | `positive` | OpenCode / Gemini 3.8 Flash | [Theorem D.1 audit & 2^{17} cutoff](d1-audit/2026-10-30-T11-d1-audit/) |

## Add a result

1. Pick a track in `auto-research.md`.
2. Copy the template:

   ```sh
   cp -r auto-research/_template auto-research/<track>/<YYYY-MM-DD>-<task>-<slug>
   ```

3. Fill in `README.md` and `result.json`.
4. Add a row to the index table above.
5. Run:

   ```sh
   python3.12 eval/verify_results.py
   python3.12 -m pytest -q
   python3.12 eval/verify_claims.py
   ```

6. Commit the result folder and the index row.

## Negative results

A failed attempt is a result. Use `outcome: "negative"` and explain what was
tried, the exact command, the expected and observed output, and what would change
the conclusion. Do not delete it, and do not label it `refuted` unless you have a
minimal counterexample.

## Folder names

```text
auto-research/<track>/<YYYY-MM-DD>-<task>-<slug>/
```

Allowed tracks: `encodings`, `coverage`, `lean`, `d1-audit`, `reproduction`,
`other`.

The folder name is the `run_id` and must match `result.json["run_id"]`.
