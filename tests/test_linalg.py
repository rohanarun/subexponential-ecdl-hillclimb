from src.btn.linalg import left_nullspace, nullspace, rank, rref


def test_rref_and_rank_over_prime_field():
    matrix = [[1, 2], [2, 4]]
    reduced, pivots = rref(matrix, 83)
    assert pivots == [0]
    assert reduced[0] == [1, 2]
    assert rank(matrix, 83) == 1


def test_nullspace_of_dependent_rows():
    basis = nullspace([[1, 2], [2, 4]], 2, 83)
    assert len(basis) == 1
    vector = basis[0]
    assert (vector[0] + 2 * vector[1]) % 83 == 0


def test_left_nullspace_vectors_have_row_length():
    matrix = [[1, 2], [2, 4], [3, 6]]
    basis = left_nullspace(matrix, 83)
    assert len(basis) == 2
    for vector in basis:
        assert len(vector) == 3
        for column in range(2):
            assert sum(vector[row] * matrix[row][column] for row in range(3)) % 83 == 0


def test_full_rank_matrix_has_trivial_left_nullspace():
    matrix = [[1, 0], [0, 1]]
    assert left_nullspace(matrix, 83) == []
