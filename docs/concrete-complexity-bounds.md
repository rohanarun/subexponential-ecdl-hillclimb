# Concrete Complexity and Crossover Bounds for Subexponential ECDL

- **Target**: Theorem 4 of "A Subexponential Time Algorithm for Elliptic Curve Discrete Logarithm" (Akshima et al., 2026).
- **Core Question**: Even if OpenAI's Theorem D.1 holds and the recursion threshold constant is reduced to $C_0 \le 256$, what is the exact concrete crossover bit-length $b^*$ where the algorithm outperforms Pollard's rho ($2^{b/2}$)?

---

## 1. Theorem 4 Cost Breakdown

For an elliptic curve $E(\mathbb{F}_p)$ with prime group order $r \approx p$, bit-length $b = \lceil \log p \rceil$, and factor-base splitting parameter $m \ge 2$, Theorem 4 decomposes total work into two competing bottlenecks:

1. **Step 3 (Linear Algebra / Gaussian Elimination)**:
   The reduction collects $N + 1$ relations across $m$ factor bases of size $O(r^{1/m})$, where:
   $$N = \sum_{i=1}^m |F_i| = O(m \cdot r^{1/m})$$
   Eliminating the factor-base columns via Gaussian elimination on an $(N + 1) \times N$ matrix over $\mathbb{F}_r$ costs:
   $$T_{\text{linalg}} = O\left(N^3 \cdot b^2\right) = O\left(m^3 r^{3/m} b^2\right) = 2^{\frac{3b}{m} + O(\log(mb))}$$

2. **Step 2 (Tensor Contraction Calls)**:
   The reduction makes $O(m^2 b r^{1/m})$ calls to the Boolean tensor contraction solver, each on a network with $s = O(mb)$ edges and degree $O(b^{3/4})$.
   Under Theorem D.1, each contraction costs $2^{O(s / \sqrt{\log s})}$. The total contraction cost is:
   $$T_{\text{contract}} = O\left(m^2 b r^{1/m}\right) \times 2^{O(s / \sqrt{\log s})} = 2^{\frac{b}{m} + O\left(\frac{mb}{\sqrt{\log(mb)}}\right)}$$

Total bit operations are bounded by:
$$T_{\text{total}}(b, m) \ge \max\left(2^{\frac{3b}{m}}, \; 2^{\frac{b}{m} + \frac{mb}{\sqrt{\log_2(mb)}}}\right)$$

---

## 2. Derivation of the Crossover Lower Bound ($b \ge 2^{193}$)

We compare $T_{\text{total}}$ against standard Pollard's rho, which solves ECDL in $2^{b/2}$ group operations ($O(2^{0.5 b})$).

### Condition 1: Linear Algebra Constraint ($m \ge 7$)
For the linear algebra step $2^{3b/m}$ to be strictly smaller than $2^{b/2}$:
$$\frac{3b}{m} < \frac{b}{2} \iff \frac{3}{m} < \frac{1}{2} \iff m > 6$$
Because $m$ is an integer, we must have **$m \ge 7$**.
*(For any $m \le 6$, Gaussian elimination alone takes $\ge 2^{3b/6} = 2^{b/2}$, already matching or exceeding Pollard's rho before counting any contraction cost).*

### Condition 2: Tensor Contraction Constraint ($\log_2(mb) > 4m^2$)
For $m \ge 7$, we require the tensor contraction exponent $\frac{mb}{\sqrt{\log_2(mb)}}$ to be less than the Pollard's rho margin $\frac{b}{2}$:
$$\frac{mb}{\sqrt{\log_2(mb)}} < \frac{b}{2} \iff \sqrt{\log_2(mb)} > 2m \iff \log_2(mb) > 4m^2$$

Substituting the minimal valid parameter $m = 7$:
$$\log_2(7b) > 4(7^2) = 4(49) = 196$$
$$7b > 2^{196} \implies b > \frac{2^{196}}{7} \approx 2^{193.2}$$

$$\mathbf{b^* \ge 2^{193} \approx 1.25 \times 10^{58} \text{ bits}}$$

### Theorem (Finite Field Infeasibility):
Under Theorem 4 and Theorem D.1, no choice of $m \ge 2$ achieves an operation count below Pollard's rho ($2^{b/2}$) for any field bit-length:
$$b \le 2^{193}$$

---

## 3. Concrete Security of Cryptographic Curves

Evaluating the concrete exponent $E(b, m) = \max\left(\frac{3b}{m}, \; \frac{b}{m} + \frac{mb}{\sqrt{\log_2(mb)}}\right)$ at standard parameters:

| Curve | Bit-length $b$ | Pollard's Rho | Optimal $m$ | Linear Algebra ($2^{3b/m}$) | Contraction ($2^{b/m + s/\sqrt{\log s}}$) | Total Index Calculus | Deficit vs. Pollard's Rho |
|---|---|---|---|---|---|---|---|
| **NIST P-256 / secp256k1** | 256 | $2^{128}$ | 3 | $2^{256.0}$ | $2^{333.4}$ | **$2^{333.4}$** | **$2^{205.4}\times$ slower** |
| **NIST P-384** | 384 | $2^{192}$ | 3 | $2^{384.0}$ | $2^{489.2}$ | **$2^{489.2}$** | **$2^{297.2}\times$ slower** |
| **NIST P-521** | 521 | $2^{260.5}$ | 3 | $2^{521.0}$ | $2^{653.5}$ | **$2^{653.5}$** | **$2^{393.0}\times$ slower** |

### Proof for $b = 256$:
* If $m = 2$: Linear algebra costs $2^{3(256)/2} = 2^{384} \gg 2^{128}$.
* If $m = 3$: Linear algebra costs $2^{256}$, contraction costs $2^{85.3 + 248.1} = 2^{333.4}$. Total: $2^{333.4}$.
* If $m = 4$: Linear algebra costs $2^{192}$, contraction costs $2^{64 + 323.8} = 2^{387.8}$. Total: $2^{387.8}$.
* If $m \ge 7$: Linear algebra costs $\le 2^{110}$, but $s = mb \ge 1792$, and $s / \sqrt{\log_2 s} \ge 546$, so contraction costs $\ge 2^{546} \gg 2^{128}$.

**Conclusion**: For NIST P-256, the attack is provably at least **$2^{205}$ times slower than Pollard's rho**, irrespective of whether the base-case recursion threshold is $C_0 = 131,072$ or $C_0 \le 256$.

---

## 4. Significance for Cryptanalysis

1. **Separation of Asymptotic vs. Practical Breakthrough**:
   - Asymptotically ($b \to \infty$): $2^{O(b / (\log b)^{1/4})} = o(2^{0.5 b})$, so the bound is subexponential.
   - Concretely ($b < 2^{193}$): The algorithm is strictly inferior to Pollard's rho by hundreds of orders of magnitude.
2. **Double Barrier**:
   Practical curves enjoy two distinct mathematical protections:
   - *Barrier 1 (Threshold)*: Generic tensor contraction requires $u_0 = \lfloor b / 2^{17} \rfloor \ge 1 \implies b \ge 131,072$.
   - *Barrier 2 (Trade-off Exponent)*: Balancing Gaussian elimination ($2^{3b/m}$) against contraction ($2^{mb / \sqrt{\log(mb)}}$) requires $b \ge 2^{193}$.
