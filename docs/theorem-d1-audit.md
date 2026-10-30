# Independent Audit of Theorem D.1 (Claim C17 / Task T11)

- **Task**: `T11`
- **Claim**: `C17`
- **Subject**: OpenAI Theorem D.1 ("The exponential time hypothesis is false", preprint, 17 October 2026, revised 25 October 2026, p. 53), as used in Theorem 2 and Axiom `A1` of "A Subexponential Time Algorithm for Elliptic Curve Discrete Logarithm" (v0.2, 29 October 2026).
- **Status**: Audit complete. No refutation of the reduction logic; external axiom `A1` confirmed conditional.

---

## 1. Executive Summary

Theorem 4 of the ECDL paper asserts that the discrete logarithm on an elliptic curve over $\mathbb{F}_p$ with prime order $r$ ($b = \lceil \log_2 r \rceil$) can be computed in expected time $2^{O(b / (\log b)^{1/4})}$.

This result is **strictly conditional** on Theorem D.1 of `[Ope26]`. This audit evaluates:
1. Whether the simplified Theorem 2 correctly and completely instantiates Theorem D.1 of `[Ope26]`.
2. The algebraic ring specialization from $\mathbb{Z}_{2^{P_0}}[X] / X^\ell$ to integer Boolean contraction.
3. The bipartite graph transformation.
4. The concrete versus asymptotic threshold ($s \ge 2^{2^{17}}$ and $u_0 = \lfloor b / 2^{17} \rfloor$).

---

## 2. Hypothesis Audit

| Parameter / Condition | Theorem D.1 Requirement | Simplified Theorem 2 Realization | Status / Audit Finding |
|---|---|---|---|
| **Graph structure** | Bipartite graph $G = (V_1, V_2, E)$ | General multigraph $G = (V, E)$ without self-loops | **Sound**: Remark 1 subdivides each edge with an equality vertex $x_{e_1} = x_{e_2}$. This produces a bipartite graph with $2s$ edges and does not increase maximum degree beyond $\max(2, \Delta)$. |
| **Edge size** | $s = \|E\| \ge 2$ | $s = \|E\| \ge 2$ | **Identical**. |
| **Maximum degree** | $\Delta = O(s^{9/10})$ | $\Delta = O(s^{9/10})$ | **Compatible**: The low-degree ECDL point addition network achieves $\Delta = O(b^{3/4})$ with $s = O(mb)$, so $\Delta \ll s^{9/10}$ holds asymptotically. |
| **Description length** | $\text{poly}(s)$ | $\text{poly}(s)$ | **Sound**: All vertex predicates are constructed from polynomial-size Boolean circuits. |
| **Predicate evaluation** | Uniform in $\text{poly}(s)$ | Uniform in $\text{poly}(s)$ | **Sound**: Finite field arithmetic and hash checks evaluate in $\text{poly}(s)$ bit operations. |

---

## 3. Ring Specialization & Exact Integer Counting

In `[Ope26]`, the tensor solver is formulated over the polynomial-quotient ring $\mathcal{R} = \mathbb{Z}_{2^{P_0}}[X] / X^\ell$.

Remark 1 of `[Boc26]` specializes this ring by fixing:
$$\ell = 1, \quad P_0 = s + 1$$
Under $\ell = 1$, the ring collapses to the integer residue ring $\mathbb{Z}_{2^{s+1}}$.

### Integer Precision Verification:
1. A Boolean tensor network with $s = |E|$ edges has exactly $2^s$ possible binary assignments $x \in \{0, 1\}^s$.
2. The contraction $\text{Contract}(\text{BTN}) = \sum_{x} \prod_v P_v(x)$ is an integer counting the number of satisfying assignments, satisfying:
   $$0 \le \text{Contract}(\text{BTN}) \le 2^s < 2^{s+1}$$
3. Because the exact integer value is strictly smaller than the modulus $2^{s+1}$, computing the contraction in $\mathbb{Z}_{2^{s+1}}$ uniquely and unconditionally determines the exact integer count in $\mathbb{N}$ without overflow, truncation, or modular wrap-around.

---

## 4. Complexity & Running Time Claims

Theorem D.1 claims that contraction takes:
- **Time**: $2^{O(s / \sqrt{\log s})}$
- **Space**: $\text{poly}(s)$

### Edge Subdivision Constant Tracking:
* Subdividing edges replaces $s$ with $s' = 2s$.
* Substituting $s' = 2s$ into the exponent gives:
  $$\frac{s'}{\sqrt{\log s'}} = \frac{2s}{\sqrt{\log(2s)}} = \frac{2s}{\sqrt{\log s + 1}} = O\left(\frac{s}{\sqrt{\log s}}\right)$$
* The constant factor $2$ is absorbed into the asymptotic $O(\cdot)$ notation. The space remains $\text{poly}(2s) = \text{poly}(s)$.

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
