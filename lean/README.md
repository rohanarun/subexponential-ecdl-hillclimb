# Lean 4 formalization (Phase 3)

This directory is a placeholder for the Lean 4 development. Phase 1 does not
ship Lean code; the executable tests and the claim graph come first.

## Target

State Definition 1 and Theorem 4 in Lean 4, with `A1` (Theorem D.1) as the only
axiom. The theorem statement should expose:

- the BTN type and `Contract`;
- parsimonious encodings;
- the index-calculus reduction;
- the expected-time and space bounds.

## Rules

- No `sorry` in a claim marked `proved`.
- No axioms beyond `A1`.
- A theorem that depends on `A1` is `conditional`, not `proved`.
- The asymptotic statements should be stated with explicit `IsBigO`-style
  bounds, not informal prose.

## Suggested layout

```text
lean/
├── lakefile.lean
├── lean-toolchain
└── ECDL/
    ├── BTN.lean
    ├── Encodings.lean
    ├── Modular.lean
    ├── PointAdd.lean
    ├── FactorBase.lean
    ├── Decomposition.lean
    ├── Extraction.lean
    ├── Cost.lean
    ├── Axioms.lean
    └── Main.lean
```

`ECDL/Axioms.lean` contains `A1` and nothing else. `ECDL/Main.lean` states
Theorem 4 with `A1` in its hypothesis list.
