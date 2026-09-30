"""Phần dùng chung cho các script được C# gọi.

Quy ước "API" giữa C# và Python:
  - C# ghi dữ liệu vào stdin dưới dạng JSON (UTF-8).
  - Python in ra đúng một dòng JSON (UTF-8), luôn có "ok" và "thong_bao".
"""
import json
import re
import sys


class LoiNguoiDung(Exception):
    """Lỗi do dữ liệu nhập — thông báo sẽ hiện nguyên văn cho người dùng."""


def chay(xu_ly):
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        du_lieu = json.loads(sys.stdin.buffer.read().decode("utf-8-sig") or "{}")
        ket_qua = xu_ly(du_lieu)
        ket_qua.setdefault("ok", True)
        ket_qua.setdefault("thong_bao", "")
    except LoiNguoiDung as ex:
        ket_qua = {"ok": False, "thong_bao": str(ex)}
    except Exception as ex:  # trả lỗi về cho C# thay vì in traceback
        ket_qua = {"ok": False, "thong_bao": f"Lỗi: {ex}"}
    print(json.dumps(ket_qua, ensure_ascii=False))


def dinh_dang_so(z):
    """Đổi một số (có thể phức) thành chuỗi gọn. Trả về (chuỗi, là_số_thực)."""
    z = complex(z)
    re = 0.0 if abs(z.real) < 1e-12 else z.real
    im = 0.0 if abs(z.imag) < 1e-12 else z.imag
    fmt = lambda v: f"{v:.10g}"
    if im == 0:
        return fmt(re), True
    ao = "i" if abs(im) == 1 else f"{fmt(abs(im))}i"
    if re == 0:
        return ("-" if im < 0 else "") + ao, False
    return f"{fmt(re)} {'+' if im > 0 else '-'} {ao}", False


def thay_ky_hieu(s):
    """Đổi các ký hiệu trên bàn phím máy tính (×, ÷, √, π...) sang cú pháp Python."""
    s = s.replace("π", "pi")
    # √9 -> sqrt(9), √2y -> sqrt(2)y, √x -> sqrt(x); √(…) và √sin(…) giữ nguyên
    s = re.sub(r"√\s*(\d+(?:\.\d+)?|[a-zA-Z]\w*(?![\w(]))", r"sqrt(\1)", s)
    for cu, moi in {"×": "*", "÷": "/", "−": "-", "√": "sqrt", "²": "^2", "³": "^3"}.items():
        s = s.replace(cu, moi)
    return s


def hien_thi(bieu_thuc):
    """Đổi biểu thức sympy sang dạng dễ đọc: 2**(1/3)*sqrt(3)*x -> 2^(1/3)·√3·x"""
    s = (str(bieu_thuc).replace("**", "^").replace("*", "·")
         .replace("sqrt", "√").replace("I", "i"))
    return re.sub(r"√\((\w+)\)", r"√\1", s)
