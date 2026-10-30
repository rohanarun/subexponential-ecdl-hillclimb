# Axioms

This repository has exactly one mathematical axiom. CI rejects any Lean
declaration or claim row that depends on an unlisted axiom.

<a id="a1"></a>

## A1 — Theorem D.1 of OpenAI (simplified Theorem 2)

**Status:** assumed, external, not peer-reviewed, not independently verified by
the authors of the ECDL paper or by this repository.

**Statement used by the paper.** Let `BTN = (G, {P_v})` be a Boolean tensor
network with `s = |E| >= 2`. Assume:

- the maximum degree is `O(s^{9/10})`;
- the number of vertices and the total description length are `poly(s)`;
- each predicate `P_v` is computable in time `poly(s)`, uniformly in `v`.

Then there is a deterministic algorithm that computes `Contract(BTN)` exactly
in time `2^{O(s/sqrt(log s))}` and space `poly(s)`.

**Source.** OpenAI, "The exponential time hypothesis is false", preprint,
17 October 2026, revised 25 October 2026, Theorem D.1, p. 53, as cited in the
ECDL paper's reference `[Ope26]`.

**Pinned ECDL paper.** "A Subexponential Time Algorithm for Elliptic Curve
Discrete Logarithm", version 0.2, 29 October 2026, 19 pages.
URL: <https://github.com/bochum-crypto/subexponential-ecdl/blob/main/subexponential-ecdl.pdf>
SHA-256: `82e273629b437660607117d5e99f400141ed7aa78b25c6749b03651f42deaa11`

**What A1 does not say.**

- It does not say the ECDL paper is correct or peer-reviewed.
- It does not give a concrete attack on any deployed curve.
- It does not assert that the $2^{2^{17}}$ ($2^{131,072}$) network size threshold or $u_0 = \lfloor b / 2^{17} \rfloor$ recursion threshold is practical.
- It does not discharge the ECDL paper's Lemmas 3-13; those are separate.

**What would discharge A1.**

1. A peer-reviewed proof of Theorem D.1, or
2. a machine-checked proof of Theorem D.1 in a proof assistant, or
3. a published refutation. A refutation makes the conditional ECDL theorem
   vacuous; it does not invalidate the reduction itself.

**Audit track.** `C17` in `CLAIMS.md` tracks independent verification or
refutation. Until it closes, every use of A1 is marked `conditional` or
`assumed`.
