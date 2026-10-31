# Sparse Matrix

資料結構與圖論演算法 Programming Assignment IV，以 Python 自行實作列鏈結串列與非零元素鏈結串列。

## 執行環境

- Python 3.8 以上，僅使用標準函式庫，不需安裝額外套件。
- 在儲存庫根目錄執行指令。

## 檔案分工

| 檔案 | 用途 |
|---|---|
| `sparse_matrix.py` | `ElementNode`、`RowNode`、`SpaceMatrix`，以及存取、輸入輸出和記憶體計算 |
| `matrix_operations.py` | `add`、`negate`、`subtract`、`transpose`、`multiply` |
| `main.py` | 讀取 A、B，示範轉置、加法、減法與乘法 |
| `sample_input.txt` | 單一矩陣範例，適用於 `SpaceMatrix.read()`，不是主程式的完整輸入 |
| `sample_add_input.txt` | 兩個可相加減的矩陣 |
| `sample_multiply_input.txt` | 可相乘的 2×3、3×2 矩陣 |
| `tests/` | 自動測試、測試說明與實際執行紀錄 |

## 執行主程式

```shell
python main.py
```

依序輸入兩個矩陣。每個矩陣第一行為 `列數 欄數`，接著每列輸入 `欄號 值` 配對，以單獨的 `0` 結束；列號、欄號從 1 開始。例如：

```text
2 3
1 2 3 3 0
2 4 0
3 2
1 5 0
2 6 0
1 -2 2 7 0
```

上例乘積為：

```text
4 21
0 24
```

PowerShell 可直接使用範例檔：

```powershell
Get-Content sample_add_input.txt | python main.py
Get-Content sample_multiply_input.txt | python main.py
```

在 Bash 或 Windows cmd 可使用：

```shell
python main.py < sample_multiply_input.txt
```

主程式分別判斷加減法與乘法的維度限制，不合法的運算顯示訊息，其他合法運算仍會執行。所有矩陣均顯示完整格式、串列格式及記憶體用量。

## 在其他程式中使用

```python
from sparse_matrix import SpaceMatrix
from matrix_operations import add, subtract, negate, transpose, multiply

a = SpaceMatrix(2, 2)
b = SpaceMatrix(2, 2)
a.set(1, 2, 3)
b.set(2, 1, 4)

add(a, b).print_regular()
subtract(a, b).print_regular()
negate(a).print_regular()
transpose(a).print_regular()
multiply(a, b).print_regular()
```

運算建立新節點，不修改原矩陣。每列元素依欄號排序，只存非零值。設為零時移除節點；讀取時允許亂序，重複位置以最後一筆為準。目前假設尺寸、索引與輸入格式合法。

## 記憶體與效率

作業模型將每個整數或指標視為一單位。`memory_units()` 回傳：

```text
3 + 2 × 列數 + 3 × 非零元素數
```

這是矩陣本身的抽象儲存量，不是 Python 實際位元組數，也不包含運算暫存。

- 加減法：O(m + eA + eB)。減法重用 `add(A, negate(B))`，額外建立 −B。
- 取負：O(m + e)。
- 轉置：O(m + n + e)，另用 O(n) 節點參照作為暫存。
- 乘法：先轉置 B，再使用兩條排序串列做內積。A 為 l×m、B 為 m×n 時，時間上界為 O(l + m + n + ln + n·eA + l·eB)。若皆為 N×N 且各有 O(N) 個非零元素，則為 O(N²)；一般尺寸不直接宣稱 O(ln + e)。
- 單一矩陣儲存量為 O(列數 + 非零元素數)，乘積還須計入結果的非零元素數。

## 測試

```shell
python -m unittest discover -s tests -v
```

11 個測試方法涵蓋節點操作、輸入輸出、排序、零值抵銷、長方形運算、錯誤尺寸、結果獨立性及記憶體統計。其中包含固定種子 42 的 100 組小型亂數資料，以獨立數學公式對照結果。

詳細案例見 [測試設計](tests/README.md)，實際紀錄見 [test_results.txt](tests/test_results.txt)。測試中的二維串列只用於產生預期答案，正式矩陣運算未展開二維陣列。

## AI 使用聲明

本作業使用 ChatGPT／Codex 協助討論資料結構與演算法、產生及修改程式、撰寫註釋、分析效率、建立與執行測試，以及整理說明文件。使用者提出每列獨立串列、以負矩陣配合加法實作減法，以及轉置後計算乘法等方向。AI 的參與不限於文字潤飾。
