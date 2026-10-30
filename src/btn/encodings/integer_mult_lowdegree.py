"""Low-degree parsimonious BTN encoding of integer multiplication (Theorem 3).

This implements the Schönhage-Strassen four-stage DFT tensor network construction
defined in Section 2.3 of 'A Subexponential Time Algorithm for Elliptic Curve
Discrete Logarithm' (v0.2, 29 October 2026):

- Ring A = Z / (2^J + 1), where J is the least power of 2 with J^2 >= 64(d + 1).
- Limb width k = J / 4, number of limbs n = ceil(d / k).
- Transform length L = 2^mu with L >= 2n, split as L = L_1 * L_2 with
  L_1 = 2^{floor(mu/2)}, L_2 = 2^{ceil(mu/2)}.
- Principal L-th root of unity omega = 2^{2J/L} in A.
- Stages:
  1. Forward DFT of a and b via 4-step factorization (Lemma 4) using L_2 and L_1 vertices.
  2. Pointwise products of transformed vectors in A.
  3. Inverse DFT using omega^{-1} and L^{-1}.
  4. Carries between limbs.

Total edges < 1100(d + 1) and maximum degree < 136(d + 1)^{3/4}, meeting the sub-linear
degree bound required by Theorem 2 (Theorem D.1).
"""

from __future__ import annotations

import math
from typing import Sequence

from ..network import BTN, Vertex
from .integer_mult import bits_to_int, int_to_bits

__all__ = [
    "mult_lowdegree_params",
    "mult_lowdegree_btn",
    "mult_lowdegree_witness",
]


def mult_lowdegree_params(d: int) -> dict[str, int]:
    """Compute the Theorem 3 Schönhage-Strassen parameters for bit-length ``d``."""
    if d < 1:
        raise ValueError("d must be at least 1")
    J = 16
    while J * J < 64 * (d + 1):
        J *= 2
    k = J // 4
    n = math.ceil(d / k)
    L = 1
    while L < 2 * n:
        L *= 2
    mu = int(math.log2(L))
    L1 = 1 << (mu // 2)
    L2 = 1 << (mu - (mu // 2))
    return {"J": J, "k": k, "n": n, "L": L, "L1": L1, "L2": L2}


def mult_lowdegree_btn(d: int) -> BTN:
    """Construct the Theorem 3 low-degree parsimonious BTN for d-bit multiplication.

    Interface edges 0..4d-1:
      - 0..d-1: integer a (d bits, little-endian)
      - d..2d-1: integer b (d bits, little-endian)
      - 2d..4d-1: integer z (2d bits, little-endian)
    """
    params = mult_lowdegree_params(d)
    J, k, n, L, L1, L2 = (
        params["J"],
        params["k"],
        params["n"],
        params["L"],
        params["L1"],
        params["L2"],
    )

    Mod = (1 << J) + 1
    omega = pow(2, (2 * J) // L, Mod)
    omega_inv = pow(omega, L - 1, Mod)
    L_inv = pow(L, -1, Mod)
    omega_L1 = pow(omega, L1, Mod)
    omega_L2 = pow(omega, L2, Mod)
    omega_inv_L1 = pow(omega_inv, L1, Mod)
    omega_inv_L2 = pow(omega_inv, L2, Mod)

    word_bits = J + 1

    # Edge index allocation
    curr_edge = 0

    def alloc_edges(count: int) -> tuple[int, ...]:
        nonlocal curr_edge
        res = tuple(range(curr_edge, curr_edge + count))
        curr_edge += count
        return res

    a_edges = alloc_edges(d)
    b_edges = alloc_edges(d)
    z_edges = alloc_edges(2 * d)
    interface_edges = a_edges + b_edges + z_edges

    # Edge allocators for words of (J + 1) bits
    def alloc_words(count: int) -> list[tuple[int, ...]]:
        return [alloc_edges(word_bits) for _ in range(count)]

    y_a_words = alloc_words(L)
    a_tilde_words = alloc_words(L)
    y_b_words = alloc_words(L)
    b_tilde_words = alloc_words(L)
    c_tilde_words = alloc_words(L)
    y_c_words = alloc_words(L)
    c_words = alloc_words(2 * n - 1)
    carry_words = alloc_words(2 * n - 1)

    vertices: list[Vertex] = []

    # Helper: read limb from input bits
    def get_input_limb(bits: tuple[bool, ...], limb_idx: int) -> int:
        start = limb_idx * k
        if start >= d:
            return 0
        end = min(d, start + k)
        val = 0
        for i in range(start, end):
            if bits[i]:
                val |= 1 << (i - start)
        return val

    # 1. Forward transform of a
    # Stage 1: L2 vertices F_{j2}
    for j2 in range(L2):
        in_edges = a_edges
        out_words = [y_a_words[j2 * L1 + t1] for t1 in range(L1)]
        all_edges = in_edges + tuple(e for w in out_words for e in w)

        def make_f_pred(j2_val: int):
            def pred(bits: tuple[bool, ...]) -> bool:
                a_bits_in = bits[:d]
                out_bits = bits[d:]
                for t1 in range(L1):
                    s = 0
                    for j1 in range(L1):
                        limb = get_input_limb(a_bits_in, L2 * j1 + j2_val)
                        term = (limb * pow(omega_L2, j1 * t1, Mod)) % Mod
                        s = (s + term) % Mod
                    y_expected = (s * pow(omega, j2_val * t1, Mod)) % Mod
                    w_bits = out_bits[t1 * word_bits : (t1 + 1) * word_bits]
                    if bits_to_int(w_bits) != y_expected:
                        return False
                return True
            return pred

        vertices.append(Vertex(all_edges, make_f_pred(j2)))

    # Stage 2: L1 vertices G_{t1}
    for t1 in range(L1):
        in_words = [y_a_words[j2 * L1 + t1] for j2 in range(L2)]
        out_words = [a_tilde_words[t1 + L1 * t2] for t2 in range(L2)]
        in_edges = tuple(e for w in in_words for e in w)
        out_edges = tuple(e for w in out_words for e in w)
        all_edges = in_edges + out_edges

        def make_g_pred(t1_val: int):
            def pred(bits: tuple[bool, ...]) -> bool:
                n_in = L2 * word_bits
                in_bits = bits[:n_in]
                out_bits = bits[n_in:]
                y_vals = [bits_to_int(in_bits[j2 * word_bits : (j2 + 1) * word_bits]) for j2 in range(L2)]
                for t2 in range(L2):
                    s = 0
                    for j2 in range(L2):
                        s = (s + y_vals[j2] * pow(omega_L1, j2 * t2, Mod)) % Mod
                    w_bits = out_bits[t2 * word_bits : (t2 + 1) * word_bits]
                    if bits_to_int(w_bits) != s:
                        return False
                return True
            return pred

        vertices.append(Vertex(all_edges, make_g_pred(t1)))

    # Forward transform of b (copies F', G')
    for j2 in range(L2):
        in_edges = b_edges
        out_words = [y_b_words[j2 * L1 + t1] for t1 in range(L1)]
        all_edges = in_edges + tuple(e for w in out_words for e in w)

        def make_f_b_pred(j2_val: int):
            def pred(bits: tuple[bool, ...]) -> bool:
                b_bits_in = bits[:d]
                out_bits = bits[d:]
                for t1 in range(L1):
                    s = 0
                    for j1 in range(L1):
                        limb = get_input_limb(b_bits_in, L2 * j1 + j2_val)
                        term = (limb * pow(omega_L2, j1 * t1, Mod)) % Mod
                        s = (s + term) % Mod
                    y_expected = (s * pow(omega, j2_val * t1, Mod)) % Mod
                    w_bits = out_bits[t1 * word_bits : (t1 + 1) * word_bits]
                    if bits_to_int(w_bits) != y_expected:
                        return False
                return True
            return pred

        vertices.append(Vertex(all_edges, make_f_b_pred(j2)))

    for t1 in range(L1):
        in_words = [y_b_words[j2 * L1 + t1] for j2 in range(L2)]
        out_words = [b_tilde_words[t1 + L1 * t2] for t2 in range(L2)]
        all_edges = tuple(e for w in in_words for e in w) + tuple(e for w in out_words for e in w)

        def make_g_b_pred(t1_val: int):
            def pred(bits: tuple[bool, ...]) -> bool:
                n_in = L2 * word_bits
                in_bits = bits[:n_in]
                out_bits = bits[n_in:]
                y_vals = [bits_to_int(in_bits[j2 * word_bits : (j2 + 1) * word_bits]) for j2 in range(L2)]
                for t2 in range(L2):
                    s = 0
                    for j2 in range(L2):
                        s = (s + y_vals[j2] * pow(omega_L1, j2 * t2, Mod)) % Mod
                    w_bits = out_bits[t2 * word_bits : (t2 + 1) * word_bits]
                    if bits_to_int(w_bits) != s:
                        return False
                return True
            return pred

        vertices.append(Vertex(all_edges, make_g_b_pred(t1)))

    # 2. Pointwise products: L vertices Pi_t
    for t in range(L):
        edges = a_tilde_words[t] + b_tilde_words[t] + c_tilde_words[t]

        def pred_pi(bits: tuple[bool, ...]) -> bool:
            at = bits_to_int(bits[:word_bits])
            bt = bits_to_int(bits[word_bits : 2 * word_bits])
            ct = bits_to_int(bits[2 * word_bits : 3 * word_bits])
            return ct == (at * bt) % Mod

        vertices.append(Vertex(edges, pred_pi))

    # 3. Inverse transform on c_tilde
    for j2 in range(L2):
        in_words = [c_tilde_words[L2 * j1 + j2] for j1 in range(L1)]
        out_words = [y_c_words[j2 * L1 + t1] for t1 in range(L1)]
        all_edges = tuple(e for w in in_words for e in w) + tuple(e for w in out_words for e in w)

        def make_f_c_pred(j2_val: int):
            def pred(bits: tuple[bool, ...]) -> bool:
                n_in = L1 * word_bits
                in_bits = bits[:n_in]
                out_bits = bits[n_in:]
                in_vals = [bits_to_int(in_bits[j1 * word_bits : (j1 + 1) * word_bits]) for j1 in range(L1)]
                for t1 in range(L1):
                    s = 0
                    for j1 in range(L1):
                        term = (in_vals[j1] * pow(omega_inv_L2, j1 * t1, Mod)) % Mod
                        s = (s + term) % Mod
                    y_expected = (s * pow(omega_inv, j2_val * t1, Mod)) % Mod
                    w_bits = out_bits[t1 * word_bits : (t1 + 1) * word_bits]
                    if bits_to_int(w_bits) != y_expected:
                        return False
                return True
            return pred

        vertices.append(Vertex(all_edges, make_f_c_pred(j2)))

    for t1 in range(L1):
        in_words = [y_c_words[j2 * L1 + t1] for j2 in range(L2)]
        out_words = [c_words[t1 + L1 * t2] for t2 in range(L2) if t1 + L1 * t2 < 2 * n - 1]
        out_indices = [t1 + L1 * t2 for t2 in range(L2) if t1 + L1 * t2 < 2 * n - 1]
        all_edges = tuple(e for w in in_words for e in w) + tuple(e for w in out_words for e in w)

        def make_g_c_pred(t1_val: int, out_idx_list: list[int]):
            def pred(bits: tuple[bool, ...]) -> bool:
                n_in = L2 * word_bits
                in_bits = bits[:n_in]
                out_bits = bits[n_in:]
                y_vals = [bits_to_int(in_bits[j2 * word_bits : (j2 + 1) * word_bits]) for j2 in range(L2)]
                for out_pos, target_idx in enumerate(out_idx_list):
                    t2 = target_idx // L1
                    s = 0
                    for j2 in range(L2):
                        s = (s + y_vals[j2] * pow(omega_inv_L1, j2 * t2, Mod)) % Mod
                    c_val = (s * L_inv) % Mod
                    w_bits = out_bits[out_pos * word_bits : (out_pos + 1) * word_bits]
                    if bits_to_int(w_bits) != c_val:
                        return False
                return True
            return pred

        vertices.append(Vertex(all_edges, make_g_c_pred(t1, out_indices)))

    # 4. Carries and Output Limbs
    for ell in range(2 * n):
        c_word = c_words[ell] if ell < 2 * n - 1 else ()
        in_carry = carry_words[ell - 1] if ell > 0 else ()
        out_carry = carry_words[ell] if ell < 2 * n - 1 else ()

        z_start = ell * k
        z_end = min(2 * d, z_start + k)
        z_limb_edges = z_edges[z_start:z_end]

        edges = c_word + in_carry + out_carry + z_limb_edges

        def make_carry_pred(ell_idx: int, z_len: int, has_c: bool, has_in_c: bool, has_out_c: bool):
            def pred(bits: tuple[bool, ...]) -> bool:
                offset = 0
                c_val = 0
                if has_c:
                    c_val = bits_to_int(bits[offset : offset + word_bits])
                    offset += word_bits
                in_c = 0
                if has_in_c:
                    in_c = bits_to_int(bits[offset : offset + word_bits])
                    offset += word_bits
                out_c = 0
                if has_out_c:
                    out_c = bits_to_int(bits[offset : offset + word_bits])
                    offset += word_bits
                z_limb_val = bits_to_int(bits[offset : offset + z_len])

                total = c_val + in_c
                expected_z = total & ((1 << k) - 1)
                expected_out_c = total >> k

                if z_limb_val != (expected_z & ((1 << z_len) - 1)):
                    return False
                if has_out_c and out_c != expected_out_c:
                    return False
                if not has_out_c and expected_out_c != 0:
                    return False
                return True
            return pred

        vertices.append(Vertex(
            edges,
            make_carry_pred(
                ell,
                len(z_limb_edges),
                bool(c_word),
                bool(in_carry),
                bool(out_carry)
            )
        ))

    return BTN(
        n_edges=curr_edge,
        vertices=tuple(vertices),
        interface=interface_edges,
    )


def mult_lowdegree_witness(a_val: int, b_val: int, d: int) -> tuple[bool, ...]:
    """Construct the unique canonical satisfying assignment for ``(a, b, a*b)``."""
    params = mult_lowdegree_params(d)
    J, k, n, L, L1, L2 = (
        params["J"],
        params["k"],
        params["n"],
        params["L"],
        params["L1"],
        params["L2"],
    )
    Mod = (1 << J) + 1
    omega = pow(2, (2 * J) // L, Mod)
    omega_inv = pow(omega, L - 1, Mod)
    L_inv = pow(L, -1, Mod)
    omega_L1 = pow(omega, L1, Mod)
    omega_L2 = pow(omega, L2, Mod)
    omega_inv_L1 = pow(omega_inv, L1, Mod)
    omega_inv_L2 = pow(omega_inv, L2, Mod)
    word_bits = J + 1

    a_limbs = [(a_val >> (i * k)) & ((1 << k) - 1) for i in range(n)] + [0] * (L - n)
    b_limbs = [(b_val >> (i * k)) & ((1 << k) - 1) for i in range(n)] + [0] * (L - n)

    # Stage 1 a
    y_a = [0] * L
    for j2 in range(L2):
        for t1 in range(L1):
            s = sum(a_limbs[L2 * j1 + j2] * pow(omega_L2, j1 * t1, Mod) for j1 in range(L1)) % Mod
            y_a[j2 * L1 + t1] = (s * pow(omega, j2 * t1, Mod)) % Mod

    # Stage 2 a
    a_tilde = [0] * L
    for t1 in range(L1):
        for t2 in range(L2):
            t = t1 + L1 * t2
            a_tilde[t] = sum(y_a[j2 * L1 + t1] * pow(omega_L1, j2 * t2, Mod) for j2 in range(L2)) % Mod

    # Stage 1 b
    y_b = [0] * L
    for j2 in range(L2):
        for t1 in range(L1):
            s = sum(b_limbs[L2 * j1 + j2] * pow(omega_L2, j1 * t1, Mod) for j1 in range(L1)) % Mod
            y_b[j2 * L1 + t1] = (s * pow(omega, j2 * t1, Mod)) % Mod

    # Stage 2 b
    b_tilde = [0] * L
    for t1 in range(L1):
        for t2 in range(L2):
            t = t1 + L1 * t2
            b_tilde[t] = sum(y_b[j2 * L1 + t1] * pow(omega_L1, j2 * t2, Mod) for j2 in range(L2)) % Mod

    # Pointwise products
    c_tilde = [(a_tilde[t] * b_tilde[t]) % Mod for t in range(L)]

    # Inverse Stage 1
    y_c = [0] * L
    for j2 in range(L2):
        for t1 in range(L1):
            s = sum(c_tilde[L2 * j1 + j2] * pow(omega_inv_L2, j1 * t1, Mod) for j1 in range(L1)) % Mod
            y_c[j2 * L1 + t1] = (s * pow(omega_inv, j2 * t1, Mod)) % Mod

    # Inverse Stage 2
    c_words = [0] * (2 * n - 1)
    for t1 in range(L1):
        for t2 in range(L2):
            idx = t1 + L1 * t2
            if idx < 2 * n - 1:
                s = sum(y_c[j2 * L1 + t1] * pow(omega_inv_L1, j2 * t2, Mod) for j2 in range(L2)) % Mod
                c_words[idx] = (s * L_inv) % Mod

    # Carries and z
    carries = [0] * (2 * n - 1)
    carry_in = 0
    for ell in range(2 * n):
        c_val = c_words[ell] if ell < 2 * n - 1 else 0
        tot = c_val + carry_in
        carry_out = tot >> k
        if ell < 2 * n - 1:
            carries[ell] = carry_out
        carry_in = carry_out

    z_val = a_val * b_val

    # Construct assignment in edge allocation order
    assignment: list[bool] = []
    assignment.extend(int_to_bits(a_val, d))
    assignment.extend(int_to_bits(b_val, d))
    assignment.extend(int_to_bits(z_val, 2 * d))
    for val in y_a:
        assignment.extend(int_to_bits(val, word_bits))
    for val in a_tilde:
        assignment.extend(int_to_bits(val, word_bits))
    for val in y_b:
        assignment.extend(int_to_bits(val, word_bits))
    for val in b_tilde:
        assignment.extend(int_to_bits(val, word_bits))
    for val in c_tilde:
        assignment.extend(int_to_bits(val, word_bits))
    for val in y_c:
        assignment.extend(int_to_bits(val, word_bits))
    for val in c_words:
        assignment.extend(int_to_bits(val, word_bits))
    for val in carries:
        assignment.extend(int_to_bits(val, word_bits))

    return tuple(assignment)

