"""以列鏈結串列與元素鏈結串列儲存稀疏矩陣。

示範程式：python main.py
輸入第一行為列數與欄數，接著每列輸入「欄號 值」配對，以 0 結尾。
列號與欄號都從 1 開始；不建立完整的二維陣列。
"""


class ElementNode:
    """同一列中的非零元素，依欄號遞增串接。"""

    def __init__(self, col, value, next_node=None):
        self.col = col           # 這個元素的欄號，從 1 開始
        self.value = value       # 這個位置的非零數值
        self.next = next_node    # 指向同一列的下一個元素


class RowNode:
    """每一列都有入口節點，全零列的 first 為 None。"""

    def __init__(self):
        self.first = None        # 指向本列第一個元素；None 表示全零列
        self.next = None         # 指向下一列的入口節點


class SpaceMatrix:
    """使用 O(rows + 非零元素數) 空間的稀疏矩陣。"""

    def __init__(self, rows, cols):
        # 只建立列入口，不為每個矩陣位置建立元素節點。
        self.rows = rows
        self.cols = cols
        self.first_row = None
        tail = None              # 記錄目前最後一個列節點
        for _ in range(rows):
            node = RowNode()
            if tail is None:
                # 第一個列節點成為整個矩陣的入口。
                self.first_row = node
            else:
                # 將新列接到原本最後一列的後面。
                tail.next = node
            tail = node

    def _find_row(self, row):
        """從第一列往後走，回傳指定列的入口節點。"""
        node = self.first_row
        # 列號從 1 開始，所以找到第 row 列需要走 row - 1 次。
        for _ in range(row - 1):
            node = node.next
        return node

    @staticmethod
    def _set_in_row(row_node, col, value):
        """在指定列插入、更新或移除元素，保持欄號遞增。"""
        # 此方法只需要傳入的列節點，不需要矩陣物件 self。
        previous = None
        current = row_node.first
        # 找到第一個欄號 >= col 的節點，並記住它的前一個節點。
        while current is not None and current.col < col:
            previous, current = current, current.next

        if current is not None and current.col == col:
            # 目標位置已經有節點。
            if value != 0:
                current.value = value
            elif previous is None:
                # 刪除首節點：讓列入口改指向下一個元素。
                row_node.first = current.next
            else:
                # 刪除中間或尾端節點：讓前一個節點跳過 current。
                previous.next = current.next
        elif value != 0:
            # 目標位置沒有節點：將新節點插在 previous 與 current 之間。
            node = ElementNode(col, value, current)
            if previous is None:
                row_node.first = node
            else:
                previous.next = node
        # 目標位置不存在且 value 為 0 時，不需要建立節點。

    def set(self, row, col, value):
        """插入或覆寫元素；設為零時移除節點。"""
        # 先找到列入口，再處理該列內的元素串列。
        self._set_in_row(self._find_row(row), col, value)

    def get(self, row, col):
        """未儲存的位置回傳 0。"""
        node = self._find_row(row).first
        # 欄號已排序，遇到 >= col 的節點就能停止尋找。
        while node is not None and node.col < col:
            node = node.next
        # 只有欄號相同才代表找到，否則該位置的值就是 0。
        return node.value if node is not None and node.col == col else 0

    @classmethod
    def read(cls):
        """讀取一個矩陣；重複欄號以最後一次的值為準。"""
        # input 每次讀取一行，split 將內容依空白分割。
        dimensions = input().split()
        # map 將文字轉成整數，分別指定給 rows 和 cols。
        # cls 是呼叫此方法的類別，此處通常就是 SpaceMatrix。
        rows, cols = map(int, dimensions)
        matrix = cls(rows, cols)
        row_node = matrix.first_row
        for _ in range(matrix.rows):
            tokens = list(map(int, input().split()))
            index = 0
            tail = None
            while True:
                # 每組資料是「欄號、值」；欄號位置出現 0 表示列結束。
                col = tokens[index]
                if col == 0:
                    break
                value = tokens[index + 1]
                if tail is None or col > tail.col:
                    # 欄號遞增時直接接到尾端，每個元素只需 O(1)。
                    if value != 0:
                        node = ElementNode(col, value)
                        if tail is None:
                            row_node.first = node
                        else:
                            tail.next = node
                        tail = node
                else:
                    # 亂序或重複欄號仍使用原本的插入／更新邏輯。
                    removed_tail = col == tail.col and value == 0
                    matrix._set_in_row(row_node, col, value)
                    if removed_tail:
                        # 尾端被刪除後，重新找到尾端，避免之後接錯位置。
                        tail = row_node.first
                        while tail is not None and tail.next is not None:
                            tail = tail.next
                index += 2
            # 本列處理完畢，前往下一個列入口。
            row_node = row_node.next
        return matrix

    def print_regular(self):
        """逐格輸出並補零，沒有建立二維陣列。"""
        row_node = self.first_row
        while row_node is not None:
            element = row_node.first
            for col in range(1, self.cols + 1):
                # 預設印 0；目前欄號有對應元素時才取出節點中的值。
                value = 0
                if element is not None and element.col == col:
                    value = element.value
                    element = element.next
                # 每列最後一欄換行，其餘欄位以空白分隔。
                print(value, end="\n" if col == self.cols else " ")
            row_node = row_node.next

    def print_list(self):
        """輸出作業的串列格式，最後顯示抽象記憶體用量。"""
        # 第一行印尺寸，之後每列只印非零元素。
        print(self.rows, self.cols)
        row_node = self.first_row
        while row_node is not None:
            element = row_node.first
            while element is not None:
                print(element.col, element.value, end=" ")
                element = element.next
            # 即使是全零列，也需要印出結束符號 0。
            print(0)
            row_node = row_node.next
        print(f"Memory: {self.memory_units()} units (assignment model)")

    def memory_units(self):
        """計算題目定義的儲存單位，不是 Python 實際使用的位元組數。"""
        # 矩陣本身：rows、cols、first_row，共 3 單位。
        units = 3
        row_node = self.first_row
        while row_node is not None:
            # 每列入口：first、next，共 2 單位；空指標也占一個單位。
            units += 2
            element = row_node.first
            while element is not None:
                # 每個非零元素：col、value、next，共 3 單位。
                units += 3
                element = element.next
            row_node = row_node.next
        return units
