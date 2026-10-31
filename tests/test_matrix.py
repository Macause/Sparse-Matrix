"""執行：python -m unittest discover -s tests -v。

測試用小型二維串列提供獨立的預期答案；正式矩陣運算仍使用鏈結串列。
"""
import io
import random
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from sparse_matrix import SpaceMatrix
from matrix_operations import add, subtract, negate, transpose, multiply
from main import main


def build(values):
    matrix = SpaceMatrix(len(values), len(values[0]))
    for i, row in enumerate(values, 1):
        for j, value in enumerate(row, 1):
            matrix.set(i, j, value)
    return matrix


class MatrixTests(unittest.TestCase):
    def check_matrix(self, matrix, expected):
        """同時檢查數值、列數、排序、零節點及記憶體統計。"""
        self.assertEqual((matrix.rows, matrix.cols), (len(expected), len(expected[0])))
        row = matrix.first_row
        count = 0
        for values in expected:
            self.assertIsNotNone(row)
            actual = []
            node = row.first
            while node is not None:
                # 限制節點數也能避免錯誤的環狀鏈結造成無限迴圈。
                self.assertLess(len(actual), matrix.cols)
                actual.append((node.col, node.value))
                node = node.next
            wanted = [(j, v) for j, v in enumerate(values, 1) if v != 0]
            self.assertEqual(actual, wanted)
            count += len(actual)
            row = row.next
        self.assertIsNone(row)
        self.assertEqual(matrix.memory_units(), 3 + 2 * matrix.rows + 3 * count)

    def test_01_read_and_output(self):
        lines = ['4 5', '3 3 5 4 0', '3 5 4 7 0', '0', '2 2 3 6 0']
        with patch('builtins.input', side_effect=lines):
            matrix = SpaceMatrix.read()
        self.check_matrix(matrix, [[0,0,3,0,4], [0,0,5,7,0], [0,0,0,0,0], [0,2,6,0,0]])
        output = io.StringIO()
        with redirect_stdout(output):
            matrix.print_regular()
            matrix.print_list()
        self.assertEqual(output.getvalue(),
            '0 0 3 0 4\n0 0 5 7 0\n0 0 0 0 0\n0 2 6 0 0\n'
            '4 5\n3 3 5 4 0\n3 5 4 7 0\n0\n2 2 3 6 0\n'
            'Memory: 29 units (assignment model)\n')

    def test_02_unordered_duplicate_input(self):
        # 刪除尾節點後再插入，確認尾指標不會失效。
        with patch('builtins.input', side_effect=['1 5', '5 4 2 3 5 0 4 7 2 -1 1 0 0']):
            matrix = SpaceMatrix.read()
        self.check_matrix(matrix, [[0,-1,0,7,0]])

    def test_03_set_get_remove(self):
        matrix = SpaceMatrix(1, 5)
        for col in (5, 1, 3):
            matrix.set(1, col, col)
        matrix.set(1, 3, -8)
        self.assertEqual(matrix.get(1, 3), -8)
        self.assertEqual(matrix.get(1, 2), 0)
        for col in (1, 5, 3):
            matrix.set(1, col, 0)
        self.check_matrix(matrix, [[0,0,0,0,0]])

    def test_04_add_cancel(self):
        a = build([[2,0,5,0,4], [0,7,0,0,0]])
        b = build([[0,8,3,0,-4], [0,-7,0,0,0]])
        self.check_matrix(add(a,b), [[2,8,8,0,0], [0,0,0,0,0]])

    def test_05_negate_subtract(self):
        a = build([[2,0,-3], [0,4,0]])
        b = build([[2,5,1], [0,-4,0]])
        self.check_matrix(negate(b), [[-2,-5,-1], [0,4,0]])
        self.check_matrix(subtract(a,b), [[0,-5,-4], [0,8,0]])
        self.check_matrix(subtract(a,a), [[0,0,0], [0,0,0]])

    def test_06_transpose_rectangular(self):
        a = build([[2,0,3], [0,4,0]])
        self.check_matrix(transpose(a), [[2,0], [0,4], [3,0]])
        self.check_matrix(transpose(transpose(a)), [[2,0,3], [0,4,0]])
        self.check_matrix(transpose(build([[0,0,0]])), [[0],[0],[0]])

    def test_07_multiply_rectangular(self):
        a = build([[2,0,3], [0,4,0], [0,0,0]])
        b = build([[5,0], [0,6], [-2,7]])
        self.check_matrix(multiply(a,b), [[4,21], [0,24], [0,0]])
        self.check_matrix(multiply(build([[1,1]]), build([[3],[-3]])), [[0]])
        self.check_matrix(multiply(build([[0]]), build([[-7]])), [[0]])

    def test_08_dimensions(self):
        a, b = SpaceMatrix(2,3), SpaceMatrix(3,2)
        for operation in (add, subtract):
            with self.assertRaises(ValueError):
                operation(a,b)
        with self.assertRaises(ValueError):
            multiply(a,a)

    def test_09_no_shared_nodes(self):
        a, b = build([[2,0],[0,3]]), build([[1,4],[0,5]])
        for result in (add(a,b), subtract(a,b), negate(a), transpose(a), multiply(a,b)):
            # 修改結果的既有節點，確認原矩陣沒有被共用或修改。
            result.first_row.first.value = 999
            self.check_matrix(a, [[2,0],[0,3]])
            self.check_matrix(b, [[1,4],[0,5]])

    def test_10_random_reference(self):
        # 固定亂數種子，方便重現；以普通數學公式提供獨立答案。
        rng = random.Random(42)
        for _ in range(100):
            l, m, n = [rng.randint(1,6) for _ in range(3)]
            av = [[rng.choice([0,0,0,-2,3]) for _ in range(m)] for _ in range(l)]
            bv = [[rng.choice([0,0,0,-3,2]) for _ in range(n)] for _ in range(m)]
            a, b = build(av), build(bv)
            expected = [[sum(av[i][k]*bv[k][j] for k in range(m)) for j in range(n)] for i in range(l)]
            self.check_matrix(multiply(a,b), expected)
            self.check_matrix(transpose(a), [list(row) for row in zip(*av)])
            self.check_matrix(add(a,a), [[2*v for v in row] for row in av])
            self.check_matrix(subtract(a,a), [[0]*m for _ in range(l)])

    def test_11_main_independent_dimensions(self):
        # 不能相加仍應繼續相乘；能相加也不代表能相乘。
        cases = [(['1 2','1 1 0','2 1','1 3 0','1 4 0'], 'A x B:\n', 'Cannot add'),
                 (['1 2','1 1 0','1 2','2 3 0'], 'A + B:\n', 'Cannot multiply')]
        for lines, valid, invalid in cases:
            output = io.StringIO()
            with patch('builtins.input', side_effect=lines), redirect_stdout(output):
                main()
            self.assertIn(valid, output.getvalue())
            self.assertIn(invalid, output.getvalue())
            self.assertIn('Memory:', output.getvalue())
