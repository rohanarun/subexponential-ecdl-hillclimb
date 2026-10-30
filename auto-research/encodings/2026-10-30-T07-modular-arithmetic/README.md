# T07 — Low-degree modular addition and multiplication (Lemma 8)

- **Agent / contributor:** OpenCode / Gemini 3.8 Flash
- **Date:** 2026-10-30
- **Track:** encodings
- **Task:** T07
- **Claim:** C6
- **Outcome:** `positive`
- **Claim status recommendation:** `promote-tested`
- **Verifier:** `python -m pytest tests/test_modular.py -q`

---

## Question

Can canonical modular addition ($x + y \equiv z \pmod q$) and canonical modular
multiplication ($x \cdot y \equiv z \pmod q$) be parsimoniously encoded as Boolean
tensor networks with $O(d)$ edges and maximum vertex degree $O(d^{3/4})$, as claimed
in Lemma 8 of the paper?

---

## What was tried

Implemented `src/btn/encodings/modular.py` following the exact construction of Lemma 8:

1. **Modular Addition (`mod_add_btn`)**:
   - Guesses carry bit $\alpha \in \{0, 1\}$ and sum $s \in [0, 2q-2]$ ($d+1$ bits).
   - Verifies $x + y = s$ and $z + \alpha q = s$ via bitwise full-adder carry chains.
   - Enforces canonical range checks $x < q, y < q, z < q$.
   - Every adder vertex has degree $\le 5 = O(1)$, keeping maximum degree strictly $O(d^{3/4})$ and edges $O(d)$.
   - Unique parsimony: $\alpha = [x + y \ge q]$ and $s = x + y$ are uniquely determined.

2. **Modular Multiplication (`mod_mult_lowdegree_btn`)**:
   - Guesses quotient $\kappa = \lfloor xy / q \rfloor < q$ ($d$ bits).
   - Computes $p_1 = x \cdot y$ ($2d$ bits) and $p_2 = \kappa \cdot q$ ($2d$ bits) using Theorem 3 low-degree Schönhage-Strassen multiplication networks (`mult_lowdegree_btn(d)`).
   - Verifies $p_1 = p_2 + z$ via bitwise carry chain of degree $\le 5$.
   - Maximum degree is bounded by $136(d+1)^{3/4} = O(d^{3/4})$ and edges by $O(d)$.

---

## Command

```sh
PYTHONPATH=. .venv/bin/python -m pytest tests/test_modular.py -q
PYTHONPATH=. .venv/bin/python eval/run_task.py tasks/T07-modular-arithmetic.yaml
```

---

## Expected

1. All valid modular sums and products are accepted with canonical witnesses.
2. All non-canonical residues ($x \ge q, y \ge q, z \ge q$) and non-congruent results are rejected.
3. Full parsimony on exhaustive words for small moduli.
4. Maximum degree strictly bounded by $136(d+1)^{3/4}$.

---

## Observed

```text
.................                                                        [100%]
17 passed in 12.17s
T07: PASS (exit 0)
```

17 tests passing across small moduli ($q \in \{2, 3, 5, 7, 11, 13\}$) and parameter sweeps up to $q = 257$ ($d = 9$).

---

## Interpretation

Lemma 8 is sound and executable. Parsimonious canonical modular arithmetic can be
realized with sub-linear degree $O(d^{3/4})$ and $O(d)$ edges using Theorem 3 integer
multiplication and constant-degree carry chain adders.

---

## Artifacts

- `artifacts/test_results.txt`: stdout log of `pytest tests/test_modular.py -q`.
