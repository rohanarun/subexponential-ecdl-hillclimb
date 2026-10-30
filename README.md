# Subexponential ECDL: a claim-by-claim research hillclimb

An auto-research harness for **A Subexponential Time Algorithm for Elliptic
Curve Discrete Logarithm** (version 0.2, 29 October 2026).

The paper's Theorem 4 is **conditional** on Theorem D.1 of OpenAI's
"The exponential time hypothesis is false" (2026), which the paper's authors say
they did not independently verify. This repository does not claim an
unconditional break of ECDL. It separates three tracks:

1. **The reduction** `Theorem D.1 => Theorem 4` — the paper's contribution.
2. **The finite gadgets and lemmas** — testable at small scale.
3. **The external Theorem D.1** — an open audit, tracked as `C17`.

The hillclimb is the claim graph in [`CLAIMS.md`](CLAIMS.md): each task advances
one claim, and CI refuses a status that is not backed by a committed artifact.

## Status

Phase 1 is executable and green:

| Piece | Status |
|---|---|
| Exact BTN semantics (`Definition 1`) | tested on small networks |
| Baseline integer-multiplication encoding | tested for `d <= 5`; **not** the paper's low-degree construction |
| Baseline point-addition encoding | tested on `E(F_7)`; **not** the paper's low-degree construction |
| Toy index calculus on `E(F_101)` | tested; exhaustive decomposition, not tensor contraction |
| Toy extraction algebra (`B4`) | tested; general `Lemma 12` (`C12`) is open |
| Claim graph + CI gate | green |
| Task runner | working |

Not yet implemented:

- the paper's `O(d)`-edge, `O(d^{3/4})`-degree multiplication network;
- low-degree modular arithmetic and point addition;
- the decomposition encoding and factor-base coverage at paper scale;
- the Lean 4 formalization;
- an independent audit of Theorem D.1.

See [`docs/roadmap.md`](docs/roadmap.md) for the phased plan and
[`docs/non-claims.md`](docs/non-claims.md) for the explicit exclusions.

## Quickstart

Requires Python 3.10+ (tested on 3.12).

```sh
python3.12 -m pip install -r requirements.txt
python3.12 -m pytest -q
python3.12 eval/verify_claims.py
python3.12 -m src.btn.ecdl
```

The demo prints a reproducible run on

```text
E(F_101): y^2 = x^3 + 6x + 9,  group order 83 (prime)
```

and recovers `xi = 19` from `Q = [19]P` using two factor bases and exhaustive
decomposition search.

## Layout

```text
CLAIMS.md                 claim graph and status rules
AXIOMS.md                 the single axiom: Theorem D.1
src/btn/network.py        exact BTN semantics
src/btn/encodings/        baseline encodings (table oracles)
src/btn/ec/curve.py       toy prime-field curve arithmetic
src/btn/ecdl.py           toy index calculus
src/btn/linalg.py         linear algebra over F_p
tests/                    exhaustive and bounded checks
tasks/                    auto-research task cards
eval/run_task.py          task runner
eval/verify_claims.py     anti-overclaim CI gate
docs/                     paper notes, roadmap, non-claims
lean/                     Phase 3 placeholder
```

## Auto-research loop

Each file in `tasks/` is a small, verifiable unit:

```sh
python3.12 eval/run_task.py tasks/T01-btn-core.yaml
```

The runner executes the task's `verifier`, records the exit code and output in
`eval/results/<id>.json`, and does not care who or what wrote the code. A task is
done only when its verifier passes and its claim's evidence column points at the
committed artifact.

Agents may edit `src/` and `tests/` for their task. They may not edit
`AXIOMS.md`, the status cells in `CLAIMS.md`, or the verifier. See
[`AGENTS.md`](AGENTS.md).

## What is actually being tested

The toy code checks the **algebra** of the reduction:

- relations are of the form `[u]P + [v]Q = A_1 + ... + A_m`;
- the first `N` columns are eliminated by a left-null combination;
- the remaining `P`/`Q` coefficients recover `xi` when `V != 0`.

It does **not** test the paper's running time, the low-degree encodings, or the
external contraction algorithm. Those are separate claims in `CLAIMS.md`.

## Citation

```bibtex
@misc{ecdl2026subexponential,
  title  = {A Subexponential Time Algorithm for Elliptic Curve Discrete Logarithm},
  author = {Akshima and Bacho, Renas and Huang, Yu-Hsuan and Kiltz, Eike and
            Nishaburi, Aysan and Nooripoor, Samin and Tittelbach, Noah and
            Wiedijk, Emiel},
  year   = {2026},
  note   = {Version 0.2, 29 October 2026},
  url    = {https://github.com/bochum-crypto/subexponential-ecdl/blob/main/subexponential-ecdl.pdf}
}
```

This repository is not affiliated with the paper's authors or with OpenAI.

## License

MIT for the code in this repository. The paper is cited, not redistributed.
