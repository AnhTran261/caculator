"""Máy tính thường: tính giá trị một biểu thức số học.

Vào (stdin):  {"bieu_thuc": "2+3×sqrt(16)", "do": true, "ans": 5}
              "do" = true: góc lượng giác tính bằng độ, false: radian.
Ra  (stdout): {"ok": true, "ket_qua": "14", "gia_tri": 14.0}

Không dùng eval() — biểu thức được phân tích bằng ast và chỉ cho phép
các phép toán / hàm trong danh sách bên dưới.
"""
import ast
import math
import operator
import re

from chung import chay, LoiNguoiDung, thay_ky_hieu

PHEP_TOAN_2 = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: None,  # xử lý riêng để chặn số mũ quá lớn
}
PHEP_TOAN_1 = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def giai_thua(x):
    if float(x) != int(x) or x < 0:
        raise LoiNguoiDung("Giai thừa chỉ tính cho số nguyên không âm.")
    if x > 5000:
        raise LoiNguoiDung("Số quá lớn để tính giai thừa (tối đa 5000).")
    return math.factorial(int(x))


def tao_bang_ham(do):
    vao = math.radians if do else (lambda v: v)
    ra = math.degrees if do else (lambda v: v)

    def tan(x):
        if do and (x - 90) % 180 == 0:
            raise LoiNguoiDung(f"tan({x:g}°) không xác định.")
        return round(math.tan(vao(x)), 15)

    return {
        "sin": lambda x: round(math.sin(vao(x)), 15),
        "cos": lambda x: round(math.cos(vao(x)), 15),
        "tan": tan,
        "asin": lambda x: ra(math.asin(x)),
        "acos": lambda x: ra(math.acos(x)),
        "atan": lambda x: ra(math.atan(x)),
        "sqrt": math.sqrt,
        "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
        "ln": math.log,
        "log": lambda x, co_so=10: math.log(x, co_so),
        "exp": math.exp,
        "abs": abs,
        "round": round,
        "factorial": giai_thua,
    }


def chuan_hoa(s):
    s = thay_ky_hieu(s).replace("^", "**")
    # Nhân ngầm: 2pi -> 2*pi, 2(3) -> 2*(3), (1+2)(3) -> (1+2)*(3)
    s = re.sub(r"(\d|\))\s*(?=[a-zA-Z(])", r"\1*", s)
    return s


def tinh(node, ham, hang):
    if isinstance(node, ast.Expression):
        return tinh(node.body, ham, hang)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in PHEP_TOAN_2:
        trai, phai = tinh(node.left, ham, hang), tinh(node.right, ham, hang)
        if isinstance(node.op, ast.Pow):
            if abs(phai) > 10000 and abs(trai) > 1:
                raise OverflowError
            return trai ** phai
        return PHEP_TOAN_2[type(node.op)](trai, phai)
    if isinstance(node, ast.UnaryOp) and type(node.op) in PHEP_TOAN_1:
        return PHEP_TOAN_1[type(node.op)](tinh(node.operand, ham, hang))
    if isinstance(node, ast.Name):
        if node.id in hang:
            if hang[node.id] is None:
                raise LoiNguoiDung("Chưa có kết quả trước đó (Ans).")
            return hang[node.id]
        raise LoiNguoiDung(f"Không biết '{node.id}'.")
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
        if node.func.id not in ham:
            raise LoiNguoiDung(f"Không có hàm '{node.func.id}'.")
        return ham[node.func.id](*(tinh(a, ham, hang) for a in node.args))
    if isinstance(node, ast.Tuple):
        raise LoiNguoiDung("Dùng dấu chấm cho số thập phân (vd: 1.5), không dùng dấu phẩy.")
    raise LoiNguoiDung("Biểu thức không hợp lệ.")


def dinh_dang(v):
    if isinstance(v, complex):
        raise LoiNguoiDung("Kết quả là số phức (vd: căn của số âm) — không hỗ trợ.")
    if isinstance(v, float) and v.is_integer() and abs(v) < 1e15:
        v = int(v)
    if isinstance(v, int):
        s = str(abs(v))
        dau = "-" if v < 0 else ""
        return dau + (s if len(s) <= 20 else f"{s[0]}.{s[1:12]}e+{len(s) - 1}")
    return f"{v:.12g}"


def tinh_bieu_thuc(du_lieu):
    goc = (du_lieu.get("bieu_thuc") or "").strip()
    if not goc:
        raise LoiNguoiDung("Chưa nhập biểu thức.")
    try:
        cay = ast.parse(chuan_hoa(goc), mode="eval")
    except SyntaxError:
        raise LoiNguoiDung("Biểu thức sai cú pháp (kiểm tra lại dấu ngoặc, phép toán).")

    ans = du_lieu.get("ans")
    hang = {"pi": math.pi, "e": math.e, "ans": ans, "Ans": ans}
    try:
        v = tinh(cay, tao_bang_ham(bool(du_lieu.get("do", True))), hang)
    except ZeroDivisionError:
        raise LoiNguoiDung("Không thể chia cho 0.")
    except OverflowError:
        raise LoiNguoiDung("Kết quả quá lớn.")
    except ValueError:
        raise LoiNguoiDung("Giá trị nằm ngoài miền xác định của hàm.")
    except TypeError:
        raise LoiNguoiDung("Sai số lượng tham số của hàm.")

    ket_qua = dinh_dang(v)
    try:
        gia_tri = float(v)
    except OverflowError:
        gia_tri = None
    return {"ket_qua": ket_qua, "gia_tri": gia_tri}


if __name__ == "__main__":
    chay(tinh_bieu_thuc)
