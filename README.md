# Sparse Matrix

以 Python 鏈結串列實作的稀疏矩陣，只儲存非零元素，支援加減法、取負、轉置與乘法，不建立完整二維陣列。

## 環境

Python 3.8 以上，僅使用標準函式庫，不需安裝額外套件。

## 模組

| 檔案 | 功能 |
|---|---|
| `sparse_matrix.py` | 節點與 `SpaceMatrix` 類別，提供元素存取、輸入輸出與記憶體統計 |
| `matrix_operations.py` | `add`、`subtract`、`negate`、`transpose`、`multiply` |
| `main.py` | 讀入兩個矩陣並顯示各項運算結果 |
| `tests/test_matrix.py` | 自動測試 |

## 快速開始

在儲存庫根目錄執行：

```shell
python main.py
```

依序輸入兩個矩陣。每個矩陣第一行為 `列數 欄數`，接著每列輸入 `欄號 值` 配對，以單獨的 `0` 結束。列號、欄號從 1 開始，全零列只需輸入 `0`。

例如，以下輸入兩個尺寸為 2×3、3×2 的矩陣：

```text
2 3
1 2 3 3 0
2 4 0
3 2
1 5 0
2 6 0
1 -2 2 7 0
```

主程式顯示兩個矩陣及其轉置；尺寸符合時執行加減法與乘法，不符合時顯示對應訊息。上例乘積為：

```text
4 21
0 24
```

每個結果都會顯示完整矩陣、非零元素串列及抽象記憶體用量。

## 作為模組使用

```python
from sparse_matrix import SpaceMatrix
from matrix_operations import add, subtract, negate, transpose, multiply

a = SpaceMatrix(2, 2)
b = SpaceMatrix(2, 2)
a.set(1, 2, 3)
b.set(2, 1, 4)

print(a.get(1, 2))  # 3
print(a.get(1, 1))  # 0

add(a, b).print_regular()
subtract(a, b).print_regular()
negate(a).print_regular()
transpose(a).print_regular()
multiply(a, b).print_regular()

a.set(1, 2, 0)  # 設為零時移除該元素節點
```

### 矩陣方法

| 方法 | 說明 |
|---|---|
| `SpaceMatrix(rows, cols)` | 建立指定尺寸的全零矩陣 |
| `SpaceMatrix.read()` | 使用 `input()` 依上述格式讀取一個矩陣 |
| `set(row, col, value)` | 新增或更新元素；值為零時移除節點 |
| `get(row, col)` | 取得元素；未儲存的位置回傳零 |
| `print_regular()` | 逐格輸出並補零 |
| `print_list()` | 輸出尺寸、各列的欄號與值，最後顯示記憶體用量 |
| `memory_units()` | 回傳抽象記憶體單位數 |

### 運算函式

| 函式 | 說明與尺寸限制 |
|---|---|
| `add(a, b)` | A + B，尺寸必須相同 |
| `subtract(a, b)` | A − B，尺寸必須相同；透過 A + (−B) 計算 |
| `negate(a)` | 每個非零元素取負 |
| `transpose(a)` | 交換列、欄位置與矩陣尺寸 |
| `multiply(a, b)` | A × B，A 的欄數必須等於 B 的列數；先轉置 B 再計算內積 |

所有運算回傳新矩陣，不修改輸入矩陣。加減法、乘法尺寸不符時拋出 `ValueError`。

## 儲存與輸入規則

- 每列有獨立的元素鏈結串列，元素依欄號排序。
- 只儲存非零值；運算抵銷為零時不建立節點。
- 讀取時允許欄號亂序；重複指定同一位置時，以最後一筆為準。
- 輸入尺寸應為正整數，值為整數，索引須在矩陣範圍內；目前假設輸入合法。
- `memory_units()` 以每個整數與指標各一單位計算，公式為 `3 + 2 × 列數 + 3 × 非零元素數`，不代表 Python 實際位元組數或運算暫存空間。

## 執行測試

```shell
python -m unittest discover -s tests -v
```

測試涵蓋輸入輸出、節點插入與移除、排序、零值抵銷、轉置、加減乘、尺寸錯誤、結果獨立性與記憶體統計，並包含固定種子的 100 組小型亂數資料。
