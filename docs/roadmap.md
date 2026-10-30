# Roadmap

## Phase 1 — executable reduction (current)

- [x] Exact BTN semantics and exhaustive oracle.
- [x] Baseline table encodings for integer multiplication and point addition.
- [x] Toy end-to-end index calculus with exhaustive decomposition.
- [x] Extraction algebra over a prime field.
- [x] Claim graph and CI gate against overclaiming.
- [x] Task runner for auto-research.

Exit criterion: `pytest` and `eval/verify_claims.py` are green, and the toy
demo recovers `xi` reproducibly.

## Phase 2 — paper's low-degree gadgets

- [ ] Theorem 3 integer multiplication network (DFT construction).
- [ ] Lemma 8 modular addition and multiplication.
- [ ] Corollary 1 constraint composition.
- [ ] Corollary 2 point addition and `m`-fold sums.
- [ ] Lemma 11 decomposition encoding.
- [ ] Lemma 10 coverage experiments.

Exit criterion: each gadget is exhaustively compared with the Phase 1 oracle at
small parameters, and its edge/degree bounds are checked symbolically.

## Phase 3 — Lean 4 formalization

- [ ] Definition 1 and the encoding interface.
- [ ] Lemmas 1-2.
- [ ] Theorem 3 and Lemmas 5-7.
- [ ] Lemma 8 and Corollaries 1-2.
- [ ] Lemmas 9-13.
- [ ] Theorem 4 and the asymptotic corollary.

Exit criterion: `lake build` is green, `C14`/`C15` become `proved`, and the only
axiom is `A1`.

## Phase 4 — audit of Theorem D.1

- [ ] Read the pinned OpenAI manuscript.
- [ ] Write `docs/theorem-d1-audit.md`.
- [ ] Check the degree bound, ring choice, runtime, space, and uniformity.
- [ ] Either discharge `A1`, or record a concrete gap/refutation.

Exit criterion: `C17` is `proved` or `refuted` with evidence. A refutation is a
successful outcome for the audit, not a failure of the repository.

## Phase 5 — scale experiments (optional)

- [ ] Implement the contraction solver interface with a small exact solver.
- [ ] Measure the decomposition encoding on larger toy curves.
- [ ] Compare against exhaustive search and record the crossover.

This phase is explicitly **not** a concrete attack track. It is a scaling study
of the reduction's constants on toy inputs.
