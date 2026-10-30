"""Tiny linear algebra over a prime field.

Only what the toy extraction step needs: row reduction and nullspaces.  This is
not optimized and is not intended for the paper's parameter regime.
"""

from __future__ import annotations

from typing import Sequence

__all__ = ["rref", "nullspace", "left_nullspace", "rank"]


def _normalize(row: Sequence[int], mod: int) -> list[int]:
    return [int(value) % mod for value in row]


def rref(matrix: Sequence[Sequence[int]], mod: int) -> tuple[list[list[int]], list[int]]:
    """Return ``(reduced matrix, pivot columns)`` over ``F_mod``."""
    if mod < 2:
        raise ValueError("mod must be at least 2")
    rows = [_normalize(row, mod) for row in matrix]
    if not rows:
        return [], []
    n_cols = len(rows[0])
    if any(len(row) != n_cols for row in rows):
        raise ValueError("ragged matrix")
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(n_cols):
        pivot = next(
            (index for index in range(pivot_row, len(rows)) if rows[index][column] % mod),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        inverse = pow(rows[pivot_row][column], -1, mod)
        rows[pivot_row] = [(value * inverse) % mod for value in rows[pivot_row]]
        for index in range(len(rows)):
            if index == pivot_row:
                continue
            factor = rows[index][column] % mod
            if factor:
                rows[index] = [
                    (rows[index][j] - factor * rows[pivot_row][j]) % mod
                    for j in range(n_cols)
                ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return rows, pivot_columns


def rank(matrix: Sequence[Sequence[int]], mod: int) -> int:
    return len(rref(matrix, mod)[1])


def nullspace(matrix: Sequence[Sequence[int]], n_cols: int, mod: int) -> list[list[int]]:
    """Basis of ``{x in F_mod^n_cols : matrix @ x = 0}``."""
    reduced, pivots = rref(matrix, mod)
    free = [column for column in range(n_cols) if column not in pivots]
    basis: list[list[int]] = []
    for free_column in free:
        vector = [0] * n_cols
        vector[free_column] = 1
        for row_index, pivot_column in enumerate(pivots):
            vector[pivot_column] = (-reduced[row_index][free_column]) % mod
        basis.append(vector)
    return basis


def left_nullspace(matrix: Sequence[Sequence[int]], mod: int) -> list[list[int]]:
    """Basis of ``{y : y^T @ matrix = 0}``.

    ``matrix`` is ``m x n``; the result vectors have length ``m``.
    """
    rows = [_normalize(row, mod) for row in matrix]
    if not rows:
        return []
    m = len(rows)
    n = len(rows[0])
    if any(len(row) != n for row in rows):
        raise ValueError("ragged matrix")
    transpose = [[rows[i][j] for i in range(m)] for j in range(n)]
    return nullspace(transpose, m, mod)
