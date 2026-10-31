"""稀疏矩陣的運算函式。"""

from sparse_matrix import SpaceMatrix, ElementNode


def negate(matrix):
    """回傳負矩陣，不修改原矩陣。時間 O(rows + e)。"""
    result = SpaceMatrix(matrix.rows, matrix.cols)
    source_row = matrix.first_row
    result_row = result.first_row

    while source_row is not None:
        element = source_row.first
        tail = None
        while element is not None:
            # 位置不變，只將值取負；建立新節點避免影響原矩陣。
            node = ElementNode(element.col, -element.value)
            if tail is None:
                result_row.first = node
            else:
                tail.next = node
            tail = node
            element = element.next

        # 全零列不建立元素節點，first 自然保持 None。
        source_row = source_row.next
        result_row = result_row.next

    return result


def add(matrix_a, matrix_b):
    """回傳兩個矩陣的和，不修改原矩陣。時間 O(rows + eA + eB)。"""
    # 只有列數和欄數都相同的矩陣才能相加。
    if matrix_a.rows != matrix_b.rows or matrix_a.cols != matrix_b.cols:
        raise ValueError("矩陣尺寸不同，無法相加")

    result = SpaceMatrix(matrix_a.rows, matrix_a.cols)
    row_a = matrix_a.first_row
    row_b = matrix_b.first_row
    row_result = result.first_row

    while row_a is not None:
        a = row_a.first
        b = row_b.first
        tail = None  # 結果列的尾端，讓每次接上新節點只需 O(1)。

        # 合併兩條已排序的串列；任一邊還有元素就繼續。
        while a is not None or b is not None:
            if b is None or (a is not None and a.col < b.col):
                # 這個欄位只有 A 有非零元素。
                col, value = a.col, a.value
                a = a.next
            elif a is None or b.col < a.col:
                # 這個欄位只有 B 有非零元素。
                col, value = b.col, b.value
                b = b.next
            else:
                # 欄號相同，將兩個值相加，兩邊都前進。
                col, value = a.col, a.value + b.value
                a = a.next
                b = b.next

            # 抵銷成 0 的結果不儲存；其餘建立獨立的新節點。
            if value != 0:
                node = ElementNode(col, value)
                if tail is None:
                    row_result.first = node
                else:
                    tail.next = node
                tail = node

        row_a = row_a.next
        row_b = row_b.next
        row_result = row_result.next

    return result


def subtract(matrix_a, matrix_b):
    """回傳 A − B，透過 A + (−B) 完成，不修改原矩陣。"""
    # 先檢查尺寸，避免無法相減時仍建立負矩陣。
    if matrix_a.rows != matrix_b.rows or matrix_a.cols != matrix_b.cols:
        raise ValueError("矩陣尺寸不同，無法相減")
    return add(matrix_a, negate(matrix_b))


def transpose(matrix):
    """回傳轉置矩陣。時間 O(rows + cols + e)，不修改原矩陣。"""
    # 原本 m × n 的矩陣，轉置後是 n × m。
    result = SpaceMatrix(matrix.cols, matrix.rows)

    # 暫存各結果列的入口與尾端，方便依原本欄號直接找到結果列。
    # 這兩個一維串列只存節點參照，沒有展開成完整二維矩陣。
    row_heads = []
    tails = [None] * matrix.cols
    result_row = result.first_row
    while result_row is not None:
        row_heads.append(result_row)
        result_row = result_row.next

    row_number = 1
    source_row = matrix.first_row
    while source_row is not None:
        element = source_row.first
        while element is not None:
            # 原位置 (row_number, element.col) 變成 (element.col, row_number)。
            index = element.col - 1  # 欄號從 1 開始，一維串列索引從 0 開始。
            node = ElementNode(row_number, element.value)
            if tails[index] is None:
                row_heads[index].first = node
            else:
                tails[index].next = node
            tails[index] = node
            element = element.next

        # 原矩陣依列號遞增走訪，因此結果列的欄號也會自然遞增。
        source_row = source_row.next
        row_number += 1

    return result


def multiply(matrix_a, matrix_b):
    """將 B 轉置後，逐列計算稀疏內積，回傳 A × B。"""
    if matrix_a.cols != matrix_b.rows:
        raise ValueError("A 的欄數必須等於 B 的列數，才能相乘")

    # B 的第 j 欄變成轉置矩陣的第 j 列，方便沿鏈結串列走訪。
    b_transposed = transpose(matrix_b)
    result = SpaceMatrix(matrix_a.rows, matrix_b.cols)
    row_a = matrix_a.first_row
    row_result = result.first_row

    while row_a is not None:
        # A 的全零列與任何欄做內積都為零，直接保留結果的空列。
        if row_a.first is None:
            row_a = row_a.next
            row_result = row_result.next
            continue
        row_bt = b_transposed.first_row
        col = 1
        tail = None
        while row_bt is not None:
            # 計算 C[i,j] = A 的第 i 列與 B 轉置後第 j 列的內積。
            a = row_a.first
            b = row_bt.first
            value = 0
            while a is not None and b is not None:
                if a.col < b.col:
                    # B 在這個索引的值為零，跳過 A 的元素。
                    a = a.next
                elif b.col < a.col:
                    # A 在這個索引的值為零，跳過 B 轉置後的元素。
                    b = b.next
                else:
                    # 只有索引相同的元素才需要相乘並累加。
                    value += a.value * b.value
                    a = a.next
                    b = b.next

            # 算完內積才決定是否建立節點，抵銷為零時直接跳過。
            if value != 0:
                node = ElementNode(col, value)
                if tail is None:
                    row_result.first = node
                else:
                    tail.next = node
                tail = node

            # 按結果欄號遞增處理，所以新節點直接接到尾端即可。
            row_bt = row_bt.next
            col += 1

        row_a = row_a.next
        row_result = row_result.next

    return result
