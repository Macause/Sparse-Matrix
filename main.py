"""執行 python main.py，依序輸入兩個矩陣。"""

from sparse_matrix import SpaceMatrix
from matrix_operations import add, subtract, transpose, multiply


def print_result(title, matrix):
    """統一顯示標題、完整格式、串列格式及記憶體用量。"""
    print(title)
    print("Regular format:")
    matrix.print_regular()
    print("List format:")
    matrix.print_list()


def main():
    """依序讀入 A、B，示範矩陣轉置、加減法與乘法。"""
    # read 內部使用 input 讀取矩陣資料。
    a = SpaceMatrix.read()
    b = SpaceMatrix.read()
    print_result("A:", a)
    print_result("B:", b)
    # 轉置不要求 A、B 的尺寸相同，因此先各自示範。
    print_result("Transpose of A:", transpose(a))
    print_result("Transpose of B:", transpose(b))
    # 加法與乘法的尺寸限制不同，分別判斷，避免互相影響。
    if a.rows != b.rows or a.cols != b.cols:
        print("Cannot add matrices with different dimensions.")
        print("Cannot subtract matrices with different dimensions.")
    else:
        print_result("A + B:", add(a, b))
        print_result("A - B:", subtract(a, b))

    if a.cols != b.rows:
        print("Cannot multiply: A's columns must equal B's rows.")
    else:
        print_result("A x B:", multiply(a, b))


if __name__ == "__main__":
    # 直接執行此檔案才啟動 main；被其他程式 import 時不啟動。
    main()
