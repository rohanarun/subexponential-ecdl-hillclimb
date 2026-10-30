# T05 — Toy end-to-end index calculus

- **Agent / contributor:** OpenCode agent
- **Date:** 2026-10-30
- **Track:** reproduction
- **Task:** T05
- **Claim:** B3
- **Outcome:** `reproduced`
- **Verifier:** `python -m pytest tests/test_ecdl.py -q` and `python -m src.btn.ecdl`
- **Commit:** initial scaffold (`64020b8`)

## Question

Does the committed toy index calculus reproducibly recover `xi` on the pinned
curve `E(F_101): y^2 = x^3 + 6x + 9`, using exhaustive decomposition search
rather than Boolean tensor contraction?

This is a reproduction of baseline `B3`, not a test of the paper's Theorem 4.

## What was tried

Ran the committed demo and the end-to-end test suite on a clean local
environment:

```sh
python -m src.btn.ecdl
python -m pytest tests/test_ecdl.py -q
```

The demo uses two factor bases of size 10, collects 21 relations, and extracts
`xi` with a left-null combination of the relation rows.

## Command

```sh
python -m src.btn.ecdl
python -m pytest tests/test_ecdl.py -q
```

## Expected

The demo exits 0, prints `recovered: 19`, and the test module passes.

## Observed

```text
curve: y^2 = x^3 + 6x + 9 over F_101
group order: 83 (prime)
generator: Point(x=0, y=3)
target: Point(x=20, y=7) = [19]P
factor-base sizes: (10, 10)
relations: 21 / 21 needed
attempts: 28
recovered: 19
success: True (ok)
```

The full test module also passes. The raw demo output is in
`artifacts/demo.txt`.

## Interpretation

The extraction algebra and relation-collection interface work on this toy
instance. The observed `xi` reproduces the target, so the committed `B3`
artifact is reproducible.

## What this does not establish

- It does **not** test the paper's asymptotic running time or the low-degree
  encodings.
- It does **not** use Boolean tensor contraction; decomposition is exhaustive
  search over tiny factor bases.
- It does **not** say anything about P-256, Ed25519, or any deployed curve.
- It does **not** verify Theorem D.1 (`C17` remains open).

## Next step

Implement the low-degree integer-multiplication network (`T06`, claim `C5`) and
compare it exhaustively with the table oracle.

## Artifacts

- `artifacts/demo.txt` — stdout of `python -m src.btn.ecdl` on the pinned curve.
