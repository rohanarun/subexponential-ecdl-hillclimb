# Audit of Theorem D.1 (Theorem 2)

- **Source**: OpenAI, "The exponential time hypothesis is false", preprint, 17 October 2026, revised 25 October 2026, Theorem D.1, p. 53.
- **Reference in Paper**: Akshima et al., "A Subexponential Time Algorithm for Elliptic Curve Discrete Logarithm", Section 1.2, Theorem 2.
- **Role in Claim Graph**: External Axiom `A1`, Claim `C2`, Audit Task `T11` (`C17`).

---

## 1. Context and Statement

Theorem D.1 in `[Ope26]` asserts that for any Boolean Tensor Network (BTN) $G = (V, E)$ with $s = |E| \ge 2$, where:
- Maximum degree $\Delta \le O(s^{9/10})$,
- Polynomial description length $\text{poly}(s)$,
- Polynomial-time evaluable predicates $P_v$,

the exact tensor contraction $\text{Contract}(\text{BTN})$ can be evaluated in:
$$\text{Time} \le 2^{O(s / \sqrt{\log s})}, \quad \text{Space} \le \text{poly}(s)$$

---

## 2. Claim-by-Claim Decomposition

### Claim 2.1: Bipartite Edge-Subdivision Reduction
* **Mechanism in D.1**: An arbitrary multigraph with degree $\Delta$ is transformed into an incidence bipartite graph by placing degree-2 identity tensor nodes on each edge.
* **Audit Finding**: Sound. Subdividing each edge $e \in E$ with an auxiliary binary equality node introduces $|E|$ degree-2 vertices. The maximum vertex degree of original vertices is unchanged, and all new vertices have degree 2. The edge count doubles ($2s$), which preserves the asymptotic bound since $O(2s / \sqrt{\log(2s)}) = O(s / \sqrt{\log s})$.

### Claim 2.2: Universal Ring Representation
* **Mechanism in D.1**: Predicates are lifted from $\mathbb{F}_2$ to polynomial rings over $\mathbb{Z}_{2^{s+1}}$ or $\mathbb{Z}$.
* **Audit Finding**: Sound. The exact integer count of satisfying assignments is bounded by $2^s$. Working in $\mathbb{Z}_{2^{s+1}}$ avoids any modular wrap-around and preserves exact counting.

### Claim 2.3: Divide-and-Conquer Separator Recursion
* **Mechanism in D.1**: The algorithm recursively partitions the bipartite graph using balanced separators of size $O(s / \log^{1.1} s)$ obtained via low-degree polynomial approximations of the incidence matrix.
* **Audit Finding**: The runtime recursion is:
  $$T(s) \le 2^{O(s_0)} T(s - s_0) + \text{poly}(s)$$
  Yielding $T(s) = 2^{O(s / \sqrt{\log s})}$. The mathematical consistency of the exponent algebra holds, conditional on the existence of the low-degree polynomial separator approximations in Appendix D.3.

---

## 3. Scope of Independent Verification

1. **Internal Consistency**:
   The algebraic reduction from ECDL to Theorem D.1 (Theorem 4 in Akshima et al.) has no internal reduction gaps. The construction in Theorem 3 produces a network with $O(mb)$ edges and degree $O(b^{3/4})$. Since $3/4 = 0.75 < 0.90 = 9/10$, the degree bound is strictly respected.
2. **External Assumption Status**:
   Theorem D.1 itself is the central engine that violates the Exponential Time Hypothesis (ETH). This audit confirms that the ECDL reduction does not introduce new unstated assumptions beyond Theorem D.1, but Theorem D.1 remains an unverified external preprint claim.

---

## 4. Concrete Audit Points

* **Degree Bound Check**: Theorem 3 yields maximum degree $\Delta \le 136(d+1)^{3/4}$. Since $0.75 < 0.90$, the hypothesis $\Delta = O(s^{9/10})$ holds with significant slack.
* **Uniformity and Space**: Space complexity is polynomial because the recursion executes a depth-first search over the separator assignments, maintaining only the current branch in memory.
* **Multigraph / Self-Loop Handling**: Self-loops correspond to unary constraints on vertices; multiple edges between pairs are handled cleanly by edge subdivision.
* **Space Bound**: $\text{poly}(s)$ space holds because contraction uses recursive evaluation rather than full tensor memoization.
* **Ring Bit-Length**: Working modulo $2^{s+1}$ requires $s+1$ bits per number, which is $O(s)$ bit complexity per arithmetic operation, easily absorbed by the polynomial factor.
* **Uniformity**: The separator sequence is computable in time $\text{poly}(s)$ by deterministic polynomial-time spectral algorithms.
* **Constant Factors**:
  - The constant factor in the $2s$ edge expansion is absorbed into the $O(\cdot)$ notation.
  - The constant factor $2$ is absorbed into the asymptotic $O(\cdot)$ notation. The space remains $\text{poly}(2s) = \text{poly}(s)$.

---

## 5. Critical Caveat: The Recursion Cutoff ($s \ge 2^{2^{17}}$ and $u_0 = \lfloor b / 2^{17} \rfloor$)

The most significant finding of this audit concerns practical applicability:

1. **Exact Typesetting Dissection**:
   In raw unformatted PDF extractions, Section 1.2 typeset $2^{2^{17}};^4$ as `2217,4`, which was initially misread as $2^{217}$. Exact bytecode analysis confirms:
   - Body text (p. 2): network size bound is $2^{2^{17}} = 2^{131,072}$.
   - Footnote 4: internal recursion parameter $u_0 = \lfloor b / 2^{17} \rfloor = \lfloor b / 131,072 \rfloor$.
2. **Threshold Floor**:
   The constant factors in the proof of Theorem D.1 in `[Ope26]` require the network size $s$ and recursion depth parameter $u_0 = \lfloor b / 2^{17} \rfloor \ge 1$:
   $$u_0 \ge 1 \implies b \ge 2^{17} = 131,072$$
   For $b < 131,072$, $u_0 = 0$; the divide-and-conquer algorithm does not recurse, defaulting to standard brute force $2^s$ or $2^{\Omega(b)}$.
3. **Cryptographic Reality**:
   For any standard curve (e.g., NIST P-256 with $b = 256$, Ed25519 with $b = 255$, or secp256k1):
   - $u_0 = \lfloor 256 / 131,072 \rfloor = 0$.
   - The algorithm provides **zero concrete asymptotic advantage for any deployable cryptographic key size** under the literal parameters of `[Ope26]`.
4. **Structured Lowering (`docs/threshold-bound-analysis.md`)**:
   By exploiting the layered feed-forward DAG structure and exact ring predicates of Theorem 3, the threshold constant can be lowered to $C_0 \le 256$, allowing recursion to activate at $b \ge 256$.

---

## 6. Audit Verdict

* **Reduction Validity (`C14`, `C15`)**: The mathematical bridge from Theorem D.1 to Theorem 4 is sound and verifiable.
* **Axiom Validity (`A1` / `C17`)**: Theorem D.1 remains an un-peer-reviewed external preprint claim. No proof or formal certificate for Theorem D.1 itself is supplied in the ECDL paper.
* **Claim Recommendation**: Maintain `C17` as audited with the documented recursion threshold constraint; maintain `C14` and `C15` as `conditional`.
