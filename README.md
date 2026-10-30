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
but the reduction is subject to a massive operational bottleneck: **OpenAI's Theorem D.1
requires network size $s \ge 2^{217} \approx 2.11 \times 10^{65}$ before achieving any
speedup over brute force**. For real-world curves (e.g. NIST P-256 with $b=256$, where
$s \approx 10^5$), the algorithm provides zero speedup.

The primary hillclimb of this repository attacks this feasibility gap:

1. **The $2^{217}$ Cutoff Frontier**: Can the tree-decomposition and polynomial partition
   constants in Theorem D.1 be reduced toward finite, computable scales ($s \le 10^5$), or
   is the threshold an insurmountable barrier of the polynomial method?
2. **The Encoding Degree Bound $\Delta$**: Can the integer multiplication and point-addition
   encoding degrees be tightened from the paper's $O(b^{3/4})$ down to $O(b^{2/3})$ via
   multi-stage Fourier factorizations ($L = L_1 L_2 L_3$)?
3. **Concrete Constant Tightening**: Can the loose upper bounds in Theorem 3 ($< 1,100(d+1)$
   edges and $< 136(d+1)^{3/4}$ ports) be hillclimbed to minimal finite constants?

## Status

Phase 1 and foundational Phase 2/3/4 gates are executable and green:

| Piece | Status | Evidence / Notes |
|---|---|---|
| Exact BTN semantics (`Definition 1`) | tested | `src/btn/network.py`; `tests/test_network.py` |
| Baseline integer-multiplication encoding | tested | `d <= 5`; table oracle with linear degree $O(d)$ |
| Baseline point-addition encoding | tested | `E(F_7)`; table oracle with linear degree $O(b)$ |
| Factor-base coverage experiments (`Lemma 10`, `T09`) | **tested** | `src/btn/factor_base.py`; `eval/results/coverage.json` |
| Formal Lean 4 interface (`Theorem 4`, `T10`) | **tested** | `lean/ECDL/Main.lean`; `lean/lakefile.lean` |
| Independent audit of Theorem D.1 (`C17`, `T11`) | **tested** | `docs/theorem-d1-audit.md`; documented $2^{217}$ threshold |
| Toy index calculus on `E(F_101)` | tested | exhaustive decomposition, not tensor contraction |
| Toy extraction algebra (`B4`) | tested | general `Lemma 12` (`C12`) is open |
| Claim graph + CI gate | green | 21 claims: 8 tested, 9 open, 2 conditional, 1 assumed, 1 not-claimed |
| Task runner | working | tested across macOS and Linux |

Active hillclimb targets:

- Theorem 3: low-degree $O(d^{3/4})$ integer multiplication network (`T06`);
- Low-degree modular arithmetic (`Lemma 8`, `T07`) and point addition (`Corollary 2`);
- Decomposition encoding network (`Lemma 11`, `T08`);
- Tightening the $s \ge 2^{217}$ threshold boundary.

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
