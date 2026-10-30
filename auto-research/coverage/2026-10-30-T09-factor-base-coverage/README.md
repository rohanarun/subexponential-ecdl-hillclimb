# Factor-Base Coverage & Lemma 10 Verification

- **Task**: `T09`
- **Claim**: `C10` (backed by `C9`)
- **Outcome**: `positive`
- **Date**: 2026-10-30
- **Agent**: OpenCode / Gemini 3.8 Flash

## Summary

This experiment implements the linear hash family factor bases $\mathcal{F}_i = \{A \in G \setminus \{\mathcal{O}\} : H_i(\text{enc}(A)) < \tau\}$ defined in Section 3.2 of the paper and tests:
1. **Lemma 9 (Factor-Base Properties)**:
   - Evaluated membership probability $\Pr[A \in \mathcal{F}_i] = \rho = \tau / s$ over 5,000 trials.
   - Evaluated distinct-pair joint membership probability $\Pr[A, B \in \mathcal{F}_i] = \frac{\tau(\tau - 1)}{s(s - 1)} \le \rho^2$.
2. **Lemma 10 (Decomposition Coverage)**:
   - Tested curves $E(\mathbb{F}_{109})$ of order $r = 127$ and $E(\mathbb{F}_{139})$ of order $r = 131$.
   - Verified that when $L = (r - 1)\tau / s \ge \max(r^{1/m}, 10m)$ for $m=2$, the empirical decomposition success rate across 300 random hash seeds per point clears the theoretical lower bound of $\frac{2}{5} = 0.40$ (achieving 97.3% - 100%).

## Commands to Reproduce

```bash
# Run unit tests
PYTHONPATH=. .venv/bin/python -m pytest tests/test_coverage.py -q

# Run empirical parameter grid evaluation
PYTHONPATH=. .venv/bin/python eval/run_task.py T09
```

## Artifacts

- `artifacts/coverage.json`: Full parameter sweep and Wilson 95% confidence intervals.
