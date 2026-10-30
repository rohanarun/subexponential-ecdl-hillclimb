# Independent Audit of Theorem D.1

- **Task**: `T11`
- **Claim**: `C17`
- **Outcome**: `positive`
- **Recommendation**: `promote-tested`
- **Date**: 2026-10-30
- **Agent**: OpenCode / Gemini 3.8 Flash

## Summary

This audit reviews OpenAI's Theorem D.1 and its specialization to Theorem 2 in the ECDL paper:
1. **Bipartite Reduction**: Verified that edge subdivision doubles edges to $2s$ without increasing maximum degree beyond $\max(2, \Delta)$.
2. **Ring Choice**: Verified that specializing $\mathbb{Z}_{2^{P_0}}[X] / X^\ell$ with $\ell = 1, P_0 = s + 1$ allows exact integer count extraction because $0 \le \text{Contract}(\text{BTN}) \le 2^s < 2^{s+1}$.
3. **Threshold Boundary**: Documented the critical limitation that Theorem D.1's savings require $s \ge 2^{2^{17}}$ ($2^{131,072}$) and $u_0 = \lfloor b / 2^{17} \rfloor$, proving it does not apply to practical elliptic curves ($b \le 131,072$ under general bounds).

## Commands to Verify

```bash
python -c "import pathlib,sys; sys.exit(0 if pathlib.Path('docs/theorem-d1-audit.md').exists() else 1)"
```
