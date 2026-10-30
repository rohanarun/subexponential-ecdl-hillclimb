# Paper notes

Source: **A Subexponential Time Algorithm for Elliptic Curve Discrete
Logarithm**, version 0.2, 29 October 2026, 19 pages.

Authors: Akshima, Renas Bacho, Yu-Hsuan Huang, Eike Kiltz, Aysan Nishaburi,
Samin Nooripoor, Noah Tittelbach, Emiel Wiedijk.

Pinned URL:
<https://github.com/bochum-crypto/subexponential-ecdl/blob/main/subexponential-ecdl.pdf>

SHA-256: `82e273629b437660607117d5e99f400141ed7aa78b25c6749b03651f42deaa11`

The paper is **conditional and asymptotic**. It is not a concrete attack on
deployed curves and it has not been peer-reviewed.

## The dependency

The paper's engine is a claimed algorithm for Boolean tensor contraction:

> **Theorem 2 (simplified Theorem D.1 of [Ope26]).** Let `BTN = (G, {P_v})` be a
> Boolean tensor network with `s = |E| >= 2`, degree `O(s^{9/10})`,
> `poly(s)` vertices and description length, and predicates evaluable in
> `poly(s)` time. Then `Contract(BTN)` can be computed exactly in time
> `2^{O(s/sqrt(log s))}` and space `poly(s)`.

`[Ope26]` is OpenAI, "The exponential time hypothesis is false", preprint,
17 October 2026, revised 25 October 2026, Theorem D.1, p. 53. The ECDL authors
state that they did not independently verify it. In this repository it is axiom
`A1`.

## Main theorem

> **Theorem 4.** Let `E/F_p`, `p > 3`, have prime order `r`, let `P` generate
> `E(F_p)`, and put `b = ceil(log p)`. For every integer `m >= 2` that is not
> too large compared with `b`, there is a randomized algorithm that, given
> `Q = [xi]P`, returns `xi`, never returns a wrong value, and uses in
> expectation:
>
> - `O(m^2 b r^{1/m})` calls to a Boolean tensor contraction solver, each on a
>   graph with `O(mb)` edges and maximum degree `O(b^{3/4})`;
> - `O(m^3 r^{3/m} b^2)` further bit operations for Gaussian elimination, and
>   `poly(b)` bit operations per call for everything else;
> - `O(m^2 r^{2/m} b)` bits of space, plus the space of one call.
>
> If Theorem 2 holds, the expected running time is
> `2^{O(b/m + mb/sqrt(log b))}`, and for `m = ceil((log b)^{1/4})` the expected
> running time and space are `2^{O(b/(log b)^{1/4})}`.

The saving is `2^{o(b)}`, but not `2^{O(b^{1-epsilon})}` for any `epsilon > 0`.
The paper notes that the OpenAI proof only saves for networks of size at least
$2^{2^{17}}$ ($2^{131,072}$), with internal recursion parameter $u_0 = \lfloor b / 2^{17} \rfloor$;
smaller sizes fall back to brute force. That is why the result says
nothing about P-256 or Ed25519.

## Reduction structure

1. **Factor-base selection.** Choose `m` factor bases `F_1, ..., F_m`, each of
   size `O(r^{1/m})`, using random hash functions.
2. **Relation finding.** For random `u, v`, find
   `[u]P + [v]Q = A_1 + ... + A_m` with `A_i in F_i`. Encode the decomposition
   as a BTN with `O(mb)` edges and degree `O(b^{3/4})`, then use the contraction
   solver.
3. **Linear algebra.** Collect `N + 1` relations, where `N = sum_i |F_i| =
   O(m r^{1/m})`. Eliminate the factor-base columns to obtain
   `[U]P + [V]Q = O`.
4. **Extraction.** Since `Q = [xi]P`, `U + V xi = 0 mod r`, so
   `xi = -U/V` when `V != 0`. Randomization makes `V != 0` with probability
   `1 - 1/r`.

## Lemma map

| Paper item | Content | Claim ID | Repo status |
|---|---|---|---|
| <a id="definition-1"></a>Definition 1 | BTN, assignments, `Contract` | C1 | tested on small networks |
| Theorem 2 / D.1 | external contraction algorithm | C2 | assumed (A1) |
| Lemma 1 | find a word / detect emptiness | C3 | open |
| Lemma 2 | addition, comparison, zero test, gated equality, copying | C4 | open |
| <a id="theorem-3"></a>Theorem 3 | integer multiplication network | C5 | open |
| Lemma 5 | parameter choices for the DFT construction | part of C5 | open |
| Lemma 6 | correctness of multiplication network | part of C5 | open |
| Lemma 7 | edge and degree bounds | part of C5 | open |
| <a id="lemma-8"></a>Lemma 8 | modular addition and multiplication | C6 | open |
| Corollary 1 | systems of modular constraints | C7 | open |
| <a id="corollary-2"></a>Corollary 2 | point addition and `m`-fold sums | C8 | open |
| Lemma 9 | factor-base membership probabilities | C9 | open |
| <a id="lemma-10"></a>Lemma 10 | decomposition coverage | C10 | open |
| <a id="lemma-11"></a>Lemma 11 | decomposition encoding | C11 | open |
| <a id="lemma-12"></a>Lemma 12 | extraction | C12 | open; toy algebra is B4 |
| Lemma 13 | reduction cost | C13 | open |
| <a id="theorem-4"></a>Theorem 4 | ECDL reduction | C14 | conditional |
| asymptotic corollary | `2^{o(b)}` | C15 | conditional |

## What the toy code does and does not do

`src/btn/ecdl.py` implements the *algebra* of steps 1-4 with an exhaustive
decomposition search over toy factor bases. It is a semantic check of relation
collection and extraction, not a test of the paper's running time. The
decomposition search is exponential in `m` and would not scale.

`src/btn/encodings/integer_mult.py` and `src/btn/encodings/point_add.py` are
table encodings. They are parsimonious and exact on small inputs, but their
degree is `O(d)` and `O(b)`, not the paper's `O(d^{3/4})` / `O(b^{3/4})`. They
exist so later low-degree work has a trusted oracle.

## Non-claims

See `docs/non-claims.md`. The short version: no deployed-curve attack, no claim
that Theorem D.1 is true, no claim that the toy code meets the paper's
asymptotic bounds, and no world record.
