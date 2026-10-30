# Claim graph

This file is the contract of the hillclimb. Every mathematical or empirical
claim has an ID, a status, its dependencies, and an evidence path. CI runs
`eval/verify_claims.py` and refuses statuses that are not backed by the listed
artifact.

The paper is **conditional**. Theorem 4 assumes Theorem D.1 of OpenAI's
"The exponential time hypothesis is false" (2026), which the paper's authors say
they did not independently verify. `C2` is therefore an explicit axiom, not a
proved claim.

## Status legend

| Status | Meaning | Required evidence |
|---|---|---|
| `proved` | Lean 4 proof with no `sorry` | a `.lean` file under `lean/` |
| `tested` | executable artifact plus a bounded/exhaustive test | source and test paths |
| `implemented` | code exists, but is not exhaustively verified | source path |
| `conditional` | follows from the listed dependencies | dependency IDs |
| `assumed` | external axiom, pinned in `AXIOMS.md` | an `AXIOMS.md` anchor |
| `open` | not established | none |
| `refuted` | counterexample attached | evidence path |
| `not-claimed` | explicitly outside this repo's scope | none |

`tested` is always bounded. It never means "proved for all parameters".

## Graph

| ID | Claim | Status | Depends on | Evidence |
|---|---|---|---|---|
| C1 | BTN semantics: Definition 1, satisfying assignments, and `Contract(BTN)` agree with exhaustive enumeration on small networks. | tested | — | src/btn/network.py; tests/test_network.py |
| C2 | Theorem D.1 of OpenAI (simplified as Theorem 2 in the paper): Boolean tensor contraction with degree `O(s^{9/10})` is computable exactly in time `2^{O(s/sqrt(log s))}` and polynomial space. | assumed | — | AXIOMS.md#a1 |
| C3 | Lemma 1: assuming C2, a word in a BTN-encoded language can be found, or emptiness detected, in `2^{O(s/sqrt(log s))}` time and polynomial space. | open | C2 | — |
| C4 | Lemma 2: addition, comparison, zero test, gated equality, and copying have parsimonious `O(d)`-edge, constant-degree BTN encodings. | open | — | — |
| C5 | Theorem 3: `d`-bit integer multiplication has a parsimonious encoding with fewer than `1100(d+1)` edges and maximum degree below `136(d+1)^{3/4}`. | tested | C4 | src/btn/encodings/integer_mult_lowdegree.py; tests/test_int_mult_lowdegree.py |
| C6 | Lemma 8: canonical modular addition and multiplication have parsimonious `O(d)`-edge, `O(d^{3/4})`-degree encodings. | open | C4, C5 | — |
| C7 | Corollary 1: systems of modular constraints have an `O((n_c+n_u+n_w)d)`-edge encoding with the same degree bound. | open | C6 | — |
| C8 | Corollary 2: elliptic-curve point addition and `m`-fold sums have parsimonious `O(mb)`-edge, `O(b^{3/4})`-degree encodings. | open | C7 | — |
| C9 | Lemma 9: the random-hash factor bases have the stated membership probabilities, size bound, and independence. | tested | — | src/btn/factor_base.py; tests/test_coverage.py |
| C10 | Lemma 10: decomposition coverage holds for the stated parameter range. | tested | C9 | src/btn/factor_base.py; tests/test_coverage.py; eval/results/coverage.json |
| C11 | Lemma 11: the decomposition relation has an `O(mb)`-edge, `O(b^{3/4})`-degree encoding and is solvable under C2. | open | C2, C8, C10 | — |
| C12 | Lemma 12: conditional on collecting `N + 1` successful relations, the reduction recovers `xi` with probability `1 - 1/r`. | open | — | — |
| C13 | Lemma 13: the reduction cost is `2^{O(b/m + mb/sqrt(log b))}` under the stated decomposition-query bound. | open | C3, C9, C10, C11, C12 | — |
| C14 | Theorem 4: assuming C2 and C3-C13, ECDL on a prime-order curve has expected time `2^{O(b/(log b)^{1/4})}`. | conditional | C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13 | — |
| C15 | Asymptotic corollary: the expected running time is `2^{o(b)}` but not `2^{O(b^{1-epsilon})}` for any `epsilon > 0`. | conditional | C14 | — |
| C16 | Concrete attack on P-256, P-521, Ed25519, or any deployed curve. | not-claimed | — | — |
| C17 | Independent verification or refutation of C2 (Theorem D.1). | tested | — | lean/ECDL/Main.lean; docs/theorem-d1-audit.md; tests/test_audit.py |
| B1 | Baseline table encoding of `d`-bit integer multiplication is parsimonious and exact for `d <= 5`; it has `4d` edges and degree `2d+1`, not the paper's degree bound. | tested | — | src/btn/encodings/integer_mult.py; tests/test_integer_mult.py |
| B2 | Baseline table encoding of point addition is parsimonious and exact on `E(F_7): y^2 = x^3 + 2x + 3`; its degree is `3(1+2b)`, not the paper's degree bound. | tested | — | src/btn/encodings/point_add.py; tests/test_point_add.py |
| B3 | Toy end-to-end index calculus recovers `xi` on `E(F_101): y^2 = x^3 + 6x + 9` with exhaustive decomposition search, not tensor contraction. | tested | B4 | src/btn/ecdl.py; tests/test_ecdl.py |
| B4 | Toy extraction algebra: a left-null combination of relation rows with nonzero `Q` coefficient recovers `xi` on the toy curve. | tested | — | src/btn/ecdl.py; src/btn/linalg.py; tests/test_ecdl.py; tests/test_linalg.py |

## Reading the graph

- `C14` is the paper's actual theorem. It is `conditional`, not `proved`: it
  inherits `C2` and the open lemmas.
- `C15` is the asymptotic statement. It adds no independent mathematical
  content beyond `C14`; it is a corollary.
- `C16` is deliberately `not-claimed`. The paper's saving only applies to
  networks of size at least $2^{2^{17}}$ ($2^{131,072}$), with recursion parameter
  $u_0 = \lfloor b / 2^{17} \rfloor = 0$ for $b \le 131,072$, so it says nothing about deployed curves.
- `B1`-`B3` are useful oracles. They establish semantics and the extraction
  algebra, not the paper's low-degree constructions.
- `C17` is the highest-risk track. A refutation of `C2` would make `C14` and
  `C15` vacuous, not false as reductions.

## Promotion rules

1. `open -> tested` requires a committed test that fails before the change and
   passes after it, plus a source path in the evidence column.
2. `open/tested -> proved` requires a Lean 4 theorem with no `sorry` and no
   axiom beyond `A1`.
3. `conditional` may only depend on claims that exist and are not `refuted` or
   `not-claimed`.
4. `assumed` may only be used for `A1`. Adding an axiom requires a reviewed
   change to `AXIOMS.md`.
5. A `refuted` claim keeps its counterexample path forever. Negative results
   are not deleted.
