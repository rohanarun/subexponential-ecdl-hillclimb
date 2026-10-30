"""Low-degree parsimonious BTN encodings of modular arithmetic (Lemma 8).

This implements the canonical modular addition and multiplication constructions
defined in Section 2.4 of 'A Subexponential Time Algorithm for Elliptic Curve
Discrete Logarithm' (v0.2, 29 October 2026):

- Modulus q with bit-length d = max(1, (q - 1).bit_length()).
- Canonical range checks: x < q, y < q, z < q.
- Modular Addition (x + y = z mod q):
    Guesses carry bit alpha in {0, 1} and (d + 1)-bit sum s, checking:
      x + y = s   and   z + alpha * q = s.
    Since x + y < 2q, alpha = [x + y >= q] is uniquely determined.
    Bitwise full-adder carry chains keep vertex degrees bounded by O(1).
- Modular Multiplication (x * y = z mod q):
    Guesses quotient kappa < q (d bits) and checks:
      x * y = kappa * q + z
    using Theorem 3 low-degree multiplication networks for p_1 = x * y and
    p_2 = kappa * q, with p_1 = p_2 + z verified via bitwise carry chain.
    Degree is bounded by O(d^{3/4}) and edge count by O(d).
"""

from __future__ import annotations

from ..network import BTN, Vertex
from .integer_mult import bits_to_int, int_to_bits
from .integer_mult_lowdegree import (
    mult_lowdegree_btn,
    mult_lowdegree_params,
    mult_lowdegree_witness,
)

__all__ = [
    "mod_word",
    "mod_add_btn",
    "mod_add_witness",
    "mod_mult_table_btn",
    "mod_mult_lowdegree_btn",
    "mod_mult_lowdegree_witness",
]


def mod_word(x: int, y: int, z: int, d: int) -> tuple[bool, ...]:
    """Return the little-endian interface word ``(x, y, z)``."""
    return int_to_bits(x, d) + int_to_bits(y, d) + int_to_bits(z, d)


def _remap_sub_btn(sub_btn: BTN, edge_map: dict[int, int]) -> list[Vertex]:
    """Instantiate sub-network vertices under remapped edge indices."""
    new_vertices: list[Vertex] = []
    for v in sub_btn.vertices:
        new_edges = tuple(edge_map[e] for e in v.edges)
        new_vertices.append(Vertex(new_edges, v.predicate))
    return new_vertices


def _make_range_check_vertex(edges: tuple[int, ...], bound: int) -> Vertex:
    """Return a vertex checking ``bits_to_int(edges) < bound``."""
    return Vertex(edges, lambda bits, b=bound: bits_to_int(bits) < b)


def _carry_chain_adder_vertices(
    a_edges: tuple[int, ...],
    b_edges: tuple[int, ...],
    sum_edges: tuple[int, ...],
    carry_edges: tuple[int, ...],
) -> list[Vertex]:
    """Bitwise full-adder carry chain asserting ``sum = a + b``.

    Every vertex has degree <= 5, maintaining constant degree.
    """
    width = len(sum_edges)
    vertices: list[Vertex] = []

    for i in range(width):
        a_e = a_edges[i] if i < len(a_edges) else None
        b_e = b_edges[i] if i < len(b_edges) else None
        s_e = sum_edges[i]
        c_in_e = carry_edges[i - 1] if i > 0 else None
        c_out_e = carry_edges[i] if i < width - 1 else None

        edges = []
        if a_e is not None:
            edges.append(a_e)
        if b_e is not None:
            edges.append(b_e)
        if c_in_e is not None:
            edges.append(c_in_e)
        edges.append(s_e)
        if c_out_e is not None:
            edges.append(c_out_e)

        def make_full_adder_pred(has_a: bool, has_b: bool, has_cin: bool, has_cout: bool):
            def pred(bits: tuple[bool, ...]) -> bool:
                offset = 0
                a_b = int(bits[offset]) if has_a else 0
                if has_a:
                    offset += 1
                b_b = int(bits[offset]) if has_b else 0
                if has_b:
                    offset += 1
                cin_b = int(bits[offset]) if has_cin else 0
                if has_cin:
                    offset += 1
                s_b = int(bits[offset])
                offset += 1
                cout_b = int(bits[offset]) if has_cout else 0

                tot = a_b + b_b + cin_b
                exp_s = tot & 1
                exp_cout = tot >> 1

                if s_b != exp_s:
                    return False
                if has_cout and cout_b != exp_cout:
                    return False
                if not has_cout and exp_cout != 0:
                    return False
                return True

            return pred

        vertices.append(
            Vertex(
                tuple(edges),
                make_full_adder_pred(
                    a_e is not None, b_e is not None, c_in_e is not None, c_out_e is not None
                ),
            )
        )

    return vertices


def mod_add_btn(q: int, d: int | None = None) -> BTN:
    """Construct low-degree parsimonious BTN encoding ``x + y = z mod q`` (Lemma 8).

    Interface edges 0..3d-1:
      - 0..d-1: x (d bits, little-endian)
      - d..2d-1: y (d bits, little-endian)
      - 2d..3d-1: z (d bits, little-endian)
    """
    if q < 2:
        raise ValueError("q must be at least 2")
    if d is None:
        d = q.bit_length()
    if (1 << d) < q:
        raise ValueError(f"d={d} is too small for modulus q={q}")

    curr_edge = 0

    def alloc(n: int) -> tuple[int, ...]:
        nonlocal curr_edge
        res = tuple(range(curr_edge, curr_edge + n))
        curr_edge += n
        return res

    x_edges = alloc(d)
    y_edges = alloc(d)
    z_edges = alloc(d)
    interface_edges = x_edges + y_edges + z_edges

    alpha_edge = alloc(1)
    s_edges = alloc(d + 1)
    carries1_edges = alloc(d)  # for x + y = s (width d+1)
    carries2_edges = alloc(d)  # for z + alpha*q = s (width d+1)

    # Word alpha * q of (d + 1) bits:
    # bit i is alpha if (q >> i) & 1, else constant 0
    alpha_q_edges = alloc(d + 1)

    vertices: list[Vertex] = []

    # 1. Canonical range checks: x < q, y < q, z < q
    for edges in (x_edges, y_edges, z_edges):
        vertices.append(_make_range_check_vertex(edges, q))

    # 2. Wire alpha_q_edges to alpha_edge where q bit is 1, and 0 otherwise
    for i in range(d + 1):
        q_bit = bool((q >> i) & 1)
        aq_e = alpha_q_edges[i]
        if q_bit:
            # aq_e == alpha
            vertices.append(Vertex((aq_e, alpha_edge[0]), lambda bits: bits[0] == bits[1]))
        else:
            # aq_e == 0
            vertices.append(Vertex((aq_e,), lambda bits: bits[0] is False))

    # 3. Addition 1: x + y = s
    vertices.extend(_carry_chain_adder_vertices(x_edges, y_edges, s_edges, carries1_edges))

    # 4. Addition 2: z + alpha*q = s
    vertices.extend(_carry_chain_adder_vertices(z_edges, alpha_q_edges, s_edges, carries2_edges))

    return BTN(n_edges=curr_edge, vertices=tuple(vertices), interface=interface_edges)


def mod_add_witness(x: int, y: int, q: int, d: int | None = None) -> tuple[bool, ...]:
    """Construct the unique canonical satisfying assignment for ``(x, y, (x+y)%q)``."""
    if d is None:
        d = q.bit_length()
    z = (x + y) % q
    alpha = 1 if (x + y) >= q else 0
    s = x + y

    # Carry chain 1 for x + y = s
    carries1: list[bool] = []
    cin = 0
    for i in range(d):
        xb = (x >> i) & 1
        yb = (y >> i) & 1
        cout = (xb + yb + cin) >> 1
        carries1.append(bool(cout))
        cin = cout

    # Word alpha * q
    alpha_q = alpha * q

    # Carry chain 2 for z + alpha*q = s
    carries2: list[bool] = []
    cin = 0
    for i in range(d):
        zb = (z >> i) & 1
        aqb = (alpha_q >> i) & 1
        cout = (zb + aqb + cin) >> 1
        carries2.append(bool(cout))
        cin = cout

    asgn: list[bool] = []
    asgn.extend(int_to_bits(x, d))
    asgn.extend(int_to_bits(y, d))
    asgn.extend(int_to_bits(z, d))
    asgn.append(bool(alpha))
    asgn.extend(int_to_bits(s, d + 1))
    asgn.extend(carries1)
    asgn.extend(carries2)
    asgn.extend(int_to_bits(alpha_q, d + 1))

    return tuple(asgn)


def mod_mult_table_btn(q: int, d: int | None = None) -> BTN:
    """Table-based baseline modular multiplication BTN for small moduli."""
    from .integer_mult import mult_table_btn

    if q < 2:
        raise ValueError("q must be at least 2")
    if d is None:
        d = q.bit_length()

    curr = 0

    def alloc(n: int) -> tuple[int, ...]:
        nonlocal curr
        res = tuple(range(curr, curr + n))
        curr += n
        return res

    x_edges = alloc(d)
    y_edges = alloc(d)
    z_edges = alloc(d)
    kappa_edges = alloc(d)
    p1_edges = alloc(2 * d)
    p2_edges = alloc(2 * d)
    q_edges = alloc(d)

    vertices: list[Vertex] = []
    for edges in (x_edges, y_edges, z_edges, kappa_edges):
        vertices.append(_make_range_check_vertex(edges, q))

    q_bits = int_to_bits(q, d)
    vertices.append(Vertex(q_edges, lambda bits, qb=q_bits: bits == qb))

    # m1: x * y = p1
    m1 = mult_table_btn(d)
    map1 = {i: x_edges[i] for i in range(d)}
    map1.update({d + i: y_edges[i] for i in range(d)})
    map1.update({2 * d + i: p1_edges[i] for i in range(2 * d)})
    vertices.extend(_remap_sub_btn(m1, map1))

    # m2: kappa * q = p2
    m2 = mult_table_btn(d)
    map2 = {i: kappa_edges[i] for i in range(d)}
    map2.update({d + i: q_edges[i] for i in range(d)})
    map2.update({2 * d + i: p2_edges[i] for i in range(2 * d)})
    vertices.extend(_remap_sub_btn(m2, map2))

    # sum: p1 = p2 + z
    sum_edges = p2_edges + z_edges + p1_edges

    def sum_pred(bits: tuple[bool, ...]) -> bool:
        p2 = bits_to_int(bits[: 2 * d])
        z = bits_to_int(bits[2 * d : 3 * d])
        p1 = bits_to_int(bits[3 * d :])
        return p1 == p2 + z

    vertices.append(Vertex(sum_edges, sum_pred))

    return BTN(n_edges=curr, vertices=tuple(vertices), interface=x_edges + y_edges + z_edges)


def mod_mult_lowdegree_btn(q: int, d: int | None = None) -> BTN:
    """Construct Lemma 8 low-degree parsimonious BTN encoding ``x * y = z mod q``.

    Uses Theorem 3 low-degree multiplication networks for ``x * y = p_1`` and
    ``kappa * q = p_2``, with ``p_1 = p_2 + z`` verified via bitwise carry chain.
    Maximum degree is bounded by O(d^{3/4}) and edges by O(d).
    """
    if q < 2:
        raise ValueError("q must be at least 2")
    if d is None:
        d = q.bit_length()
    if (1 << d) < q:
        raise ValueError(f"d={d} is too small for modulus q={q}")

    curr_edge = 0

    def alloc(n: int) -> tuple[int, ...]:
        nonlocal curr_edge
        res = tuple(range(curr_edge, curr_edge + n))
        curr_edge += n
        return res

    x_edges = alloc(d)
    y_edges = alloc(d)
    z_edges = alloc(d)
    interface_edges = x_edges + y_edges + z_edges

    kappa_edges = alloc(d)
    p1_edges = alloc(2 * d)
    p2_edges = alloc(2 * d)
    q_edges = alloc(d)
    carry_edges = alloc(2 * d - 1)  # carry chain for p1 = p2 + z (width 2d)

    vertices: list[Vertex] = []

    # 1. Canonical range checks: x < q, y < q, z < q, kappa < q
    for edges in (x_edges, y_edges, z_edges, kappa_edges):
        vertices.append(_make_range_check_vertex(edges, q))

    # 2. Hardcoded modulus q
    q_bits = int_to_bits(q, d)
    vertices.append(Vertex(q_edges, lambda bits, qb=q_bits: bits == qb))

    # 3. Low-degree multiplication 1: x * y = p1 (Theorem 3)
    btn_mult1 = mult_lowdegree_btn(d)
    aux1_edges = alloc(btn_mult1.n_edges - 4 * d)
    map1: dict[int, int] = {}
    for i in range(d):
        map1[i] = x_edges[i]
    for i in range(d):
        map1[d + i] = y_edges[i]
    for i in range(2 * d):
        map1[2 * d + i] = p1_edges[i]
    for i in range(len(aux1_edges)):
        map1[4 * d + i] = aux1_edges[i]
    vertices.extend(_remap_sub_btn(btn_mult1, map1))

    # 4. Low-degree multiplication 2: kappa * q = p2 (Theorem 3)
    btn_mult2 = mult_lowdegree_btn(d)
    aux2_edges = alloc(btn_mult2.n_edges - 4 * d)
    map2: dict[int, int] = {}
    for i in range(d):
        map2[i] = kappa_edges[i]
    for i in range(d):
        map2[d + i] = q_edges[i]
    for i in range(2 * d):
        map2[2 * d + i] = p2_edges[i]
    for i in range(len(aux2_edges)):
        map2[4 * d + i] = aux2_edges[i]
    vertices.extend(_remap_sub_btn(btn_mult2, map2))

    # 5. Carry chain addition asserting p1 = p2 + z (width 2d)
    vertices.extend(_carry_chain_adder_vertices(p2_edges, z_edges, p1_edges, carry_edges))

    return BTN(n_edges=curr_edge, vertices=tuple(vertices), interface=interface_edges)


def mod_mult_lowdegree_witness(x: int, y: int, q: int, d: int | None = None) -> tuple[bool, ...]:
    """Construct the unique canonical satisfying assignment for ``(x, y, (x*y)%q)``."""
    if d is None:
        d = q.bit_length()
    p1 = x * y
    kappa = p1 // q
    p2 = kappa * q
    z = p1 % q

    w1 = mult_lowdegree_witness(x, y, d)
    w2 = mult_lowdegree_witness(kappa, q, d)

    # Carries for p1 = p2 + z (width 2d)
    carries: list[bool] = []
    cin = 0
    for i in range(2 * d - 1):
        p2_b = (p2 >> i) & 1
        z_b = (z >> i) & 1 if i < d else 0
        cout = (p2_b + z_b + cin) >> 1
        carries.append(bool(cout))
        cin = cout

    asgn: list[bool] = []
    asgn.extend(int_to_bits(x, d))
    asgn.extend(int_to_bits(y, d))
    asgn.extend(int_to_bits(z, d))
    asgn.extend(int_to_bits(kappa, d))
    asgn.extend(int_to_bits(p1, 2 * d))
    asgn.extend(int_to_bits(p2, 2 * d))
    asgn.extend(int_to_bits(q, d))
    asgn.extend(carries)
    asgn.extend(w1[4 * d :])
    asgn.extend(w2[4 * d :])

    return tuple(asgn)
