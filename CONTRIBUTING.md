# Contributing

## The one rule

Do not upgrade a claim without evidence. `CLAIMS.md` is the contract; CI checks
it with `eval/verify_claims.py`.

## Local checks

```sh
python3.12 -m pip install -r requirements.txt
python3.12 -m pytest -q
python3.12 eval/verify_claims.py
python3.12 -m src.btn.ecdl
```

## Adding a claim

1. Add a row to `CLAIMS.md` with a new ID (`C` for paper claims, `B` for
   baselines).
2. Set the status to `open` unless you already have the evidence the status
   requires.
3. Add dependencies if the claim follows from other claims.
4. Add a task card in `tasks/` with a verifier.
5. Open a PR. A status promotion needs review from someone other than the
   author.

## Adding a task

A task card is YAML with at least:

```yaml
id: T12
claim: C6
title: ...
status: open
goal: ...
inputs: [...]
deliverable: ...
verifier: python3.12 -m pytest tests/test_....py -q
bounds: {...}
forbidden: [...]
```

The verifier must be runnable from the repository root and must fail before the
work is done.

## Adding a research result

Read [`auto-research.md`](auto-research.md). Every contribution — positive,
negative, or inconclusive — gets a folder:

```text
auto-research/<track>/<YYYY-MM-DD>-<task>-<slug>/
├── README.md
├── result.json
└── artifacts/          # optional
```

Start from `auto-research/_template/`, add a row to
`auto-research/README.md`, and run:

```sh
python3.12 eval/verify_results.py
```

Negative results are first-class. Do not delete a failed attempt, and do not
label it `refuted` unless you have a minimal counterexample.

## Evidence rules

- `tested`: source path and test path. The test must be bounded or exhaustive at
  a stated size.
- `proved`: a `.lean` file with no `sorry`.
- `implemented`: source path, but no exhaustive test yet.
- `conditional`: dependency IDs only.
- `assumed`: `AXIOMS.md#a1` only.
- `refuted`: a counterexample or a concrete gap with a path.
- `not-claimed`: no evidence.

## What not to submit

- Real keys, credentials, or account data.
- Attacks against live systems.
- A claim that the paper has been peer-reviewed.
- A claim that Theorem D.1 is true without a proof or a citation to one.
- A benchmark number without the command and environment that produced it.
