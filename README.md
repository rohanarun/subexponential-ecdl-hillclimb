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

## The Core Hillclimbing Goal: The Bound Frontier

The paper proves an asymptotic expected running time of $2^{O(b / (\log b)^{1/4})}$,
but the reduction is subject to an operational bottleneck in the generic bound: **OpenAI's Theorem D.1
has an internal recursion parameter $u_0 = \lfloor b / 2^{17} \rfloor = \lfloor b / 131,072 \rfloor$
(and stated network size bound $s \ge 2^{2^{17}} = 2^{131,072}$)**.
*(Note on typesetting: in raw unformatted PDF extractions, $2^{2^{17}};^4$ rendered as `2217,4`,
which was initially misread as $2^{217}$.)*
For generic graphs, $u_0 = 0$ for $b < 131,072$.

The primary hillclimb of this repository attacks this feasibility gap:

1. **The Recursion Threshold Frontier**: In `docs/threshold-bound-analysis.md`, we proved that
   for the specialized feed-forward DAG and exact ring structure of ECDL networks, the threshold
   constant $C_0 = 2^{17} = 131,072$ is reduced to $C_0 \le 256$, activating divide-and-conquer
   recursion for $b \ge 256$.
2. **The Encoding Degree Bound $\Delta$**: Theorem 3 achieves degree $O(d^{3/4})$
   via a 2-stage Fourier transform split ($L = L_1 L_2$), implemented in `src/btn/encodings/integer_mult_lowdegree.py`.
3. **Concrete Constant Tightening**: Theorem 3 upper bounds edge count by $< 1,100(d+1)$
   and degree by $< 136(d+1)^{3/4}$, verified across parameter sweeps in `tests/test_int_mult_lowdegree.py`.
4. **Concrete Complexity Crossover**: In `docs/concrete-complexity-bounds.md`, we prove that
   because Gaussian elimination requires $O(r^{3/m}) = 2^{3b/m}$, beating Pollard's rho ($2^{b/2}$)
   requires $m \ge 7$ and field bit-length $b > 2^{193} \approx 1.25 \times 10^{58}$ bits.

## Status

Phase 1 and foundational Phase 2/3/4 gates are executable and green:

| Piece | Status | Evidence / Notes |
|---|---|---|
| Exact BTN semantics (`Definition 1`) | tested | `src/btn/network.py`; `tests/test_network.py` |
| Baseline integer-multiplication encoding | tested | `d <= 5`; table oracle with linear degree $O(d)$ |
| Theorem 3: low-degree integer multiplication (`C5`, `T06`) | **tested** | `src/btn/encodings/integer_mult_lowdegree.py`; `tests/test_int_mult_lowdegree.py` |
| Baseline point-addition encoding | tested | `E(F_7)`; table oracle with linear degree $O(b)$ |
| Factor-base coverage experiments (`Lemma 10`, `T09`) | **tested** | `src/btn/factor_base.py`; `eval/results/coverage.json` |
| Formal Lean 4 interface (`Theorem 4`, `T10`) | **tested** | `lean/ECDL/Main.lean`; `lean/lakefile.lean` |
| Independent audit of Theorem D.1 (`C17`, `T11`) | **tested** | `docs/theorem-d1-audit.md`; `docs/threshold-bound-analysis.md` |
| Toy index calculus on `E(F_101)` | tested | exhaustive decomposition, not tensor contraction |
| Toy extraction algebra (`B4`) | tested | general `Lemma 12` (`C12`) is open |
| Claim graph + CI gate | green | 21 claims: 9 tested, 8 open, 2 conditional, 1 assumed, 1 not-claimed |
| Task runner | working | tested across macOS and Linux |

Active hillclimb targets:

- Low-degree modular arithmetic (`Lemma 8`, `T07`) and point addition (`Corollary 2`);
- Decomposition encoding network (`Lemma 11`, `T08`);
- Concrete crossover lower bound verification (`docs/concrete-complexity-bounds.md`).

See [`docs/roadmap.md`](docs/roadmap.md) for the phased plan and
[`docs/non-claims.md`](docs/non-claims.md) for the explicit exclusions.

## Quickstart

Requires Python 3.10+ (tested on 3.12).

```sh
python3.12 -m pip install -r requirements.txt
python3.12 -m pytest -q
python3.12 eval/verify_claims.py
python3.12 eval/verify_results.py
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
auto-research.md          agent entry point: tracks, result format, evidence rules
auto-research/            committed research results (including negative results)
src/btn/network.py        exact BTN semantics
src/btn/encodings/        baseline encodings (table oracles)
src/btn/ec/curve.py       toy prime-field curve arithmetic
src/btn/ecdl.py           toy index calculus
src/btn/linalg.py         linear algebra over F_p
tests/                    exhaustive and bounded checks
tasks/                    auto-research task cards
eval/run_task.py          task runner
eval/verify_claims.py     anti-overclaim CI gate
eval/verify_results.py    research-result format gate
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

Research agents should start with [`auto-research.md`](auto-research.md). It
defines the tracks, the result folder format, and how to contribute positive,
negative, or inconclusive results. Results are indexed in
[`auto-research/README.md`](auto-research/README.md).

## Contributors

Research agents: start with [`auto-research.md`](auto-research.md). It contains
the research tracks, the result format, the evidence rules, and the verification
commands.

Copy this prompt into your agent:

> Read `auto-research.md` in this repository and follow it. Pick one research
> track, run the task verifier, and add your result — including negative or
> inconclusive results — under `auto-research/`. Do not edit `AXIOMS.md`, claim
> statuses, or verifier scripts.

Negative results are welcome. They are committed, indexed, and never deleted.

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
