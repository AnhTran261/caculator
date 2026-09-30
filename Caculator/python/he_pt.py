"""Giải hệ phương trình (tuyến tính hoặc phi tuyến) bằng sympy.

Vào (stdin):  {"phuong_trinh": ["2x + 3y = 7", "x - y = 1"]}
Ra  (stdout): {"ok": true, "thong_bao": "...",
               "hieu_la": ["2·x + 3·y = 7", ...],      # cách máy hiểu từng phương trình
               "bien": ["x", "y"],
               "nghiem": [ {"gia_tri": [{"bien", "chinh_xac", "xap_xi"}, ...]}, ... ]}
"""
import re
import string

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor, implicit_multiplication_application, parse_expr, standard_transformations)

from chung import chay, LoiNguoiDung, dinh_dang_so, hien_thi, thay_ky_hieu

BIEN_DOI = standard_transformations + (implicit_multiplication_application, convert_xor)
TOI_DA_PHUONG_TRINH = 8


def doc_bieu_thuc(s):
    # Mỗi chữ cái là một ẩn (xy = x·y), trừ E (số e) và I (đơn vị ảo).
    # Tên có chỉ số như x1, x_2 được giữ nguyên là một ẩn.
    bien = {c: sp.Symbol(c) for c in string.ascii_letters if c not in "EI"}
    for ten in re.findall(r"[A-Za-z]_?\d+", s):
        bien[ten] = sp.Symbol(ten)
    return parse_expr(s, local_dict=bien, transformations=BIEN_DOI)


def doc_phuong_trinh(dong, stt):
    s = thay_ky_hieu(dong)
    if "__" in s or not re.fullmatch(r"[\w\s+\-*/^().,=]*", s):
        raise LoiNguoiDung(f"Phương trình {stt} có ký tự không hợp lệ: {dong}")
    ve = s.split("=")
    if len(ve) > 2:
        raise LoiNguoiDung(f"Phương trình {stt} có nhiều hơn một dấu '=': {dong}")
    try:
        trai = doc_bieu_thuc(ve[0])
        phai = doc_bieu_thuc(ve[1]) if len(ve) == 2 else sp.Integer(0)
    except Exception:
        raise LoiNguoiDung(f"Không hiểu phương trình {stt}: {dong}")
    return trai, phai


def la_tuyen_tinh(bieu_thuc, bien):
    try:
        return all(sp.Poly(bt, *bien).total_degree() <= 1 for bt in bieu_thuc)
    except sp.PolynomialError:
        return False


def mo_ta_gia_tri(ten, gt):
    chinh_xac = hien_thi(sp.simplify(gt))
    xap_xi = "" if gt.free_symbols else dinh_dang_so(sp.N(gt, 15))[0]
    return {"bien": ten, "chinh_xac": chinh_xac if len(chinh_xac) <= 80 else "(quá dài)", "xap_xi": xap_xi}


def giai_he(du_lieu):
    dong = [d.strip() for d in du_lieu.get("phuong_trinh", []) if d.strip()]
    if not dong:
        raise LoiNguoiDung("Chưa nhập phương trình nào.")
    if len(dong) > TOI_DA_PHUONG_TRINH:
        raise LoiNguoiDung(f"Tối đa {TOI_DA_PHUONG_TRINH} phương trình.")

    cap = [doc_phuong_trinh(d, i + 1) for i, d in enumerate(dong)]
    hieu_la = [f"{hien_thi(t)} = {hien_thi(p)}" for t, p in cap]
    bieu_thuc = [sp.expand(t - p) for t, p in cap]
    bien = sorted(set().union(*(bt.free_symbols for bt in bieu_thuc)), key=str)
    ten_bien = [str(b) for b in bien]

    ket_qua = {"hieu_la": hieu_la, "bien": ten_bien, "nghiem": []}
    if not bien:
        raise LoiNguoiDung("Không tìm thấy ẩn nào trong hệ.")

    mo_ta_he = f"Hệ {len(dong)} phương trình, {len(bien)} ẩn ({', '.join(ten_bien)})"

    if la_tuyen_tinh(bieu_thuc, bien):
        tap = sp.linsolve(bieu_thuc, bien)
        if tap == sp.EmptySet:
            ket_qua["thong_bao"] = f"{mo_ta_he}, tuyến tính: HỆ VÔ NGHIỆM."
            return ket_qua
        bo = list(tap)[0]
        tu_do = sorted(set().union(*(gt.free_symbols for gt in bo)) & set(bien), key=str)
        ket_qua["nghiem"] = [{"gia_tri": [mo_ta_gia_tri(t, gt) for t, gt in zip(ten_bien, bo)]}]
        if tu_do:
            ket_qua["thong_bao"] = (f"{mo_ta_he}, tuyến tính: HỆ CÓ VÔ SỐ NGHIỆM "
                                    f"({', '.join(map(str, tu_do))} lấy giá trị tùy ý).")
        else:
            ket_qua["thong_bao"] = f"{mo_ta_he}, tuyến tính: hệ có NGHIỆM DUY NHẤT."
        return ket_qua

    cac_bo = sp.solve(bieu_thuc, bien, dict=True)
    if not cac_bo:
        ket_qua["thong_bao"] = f"{mo_ta_he}, phi tuyến: không tìm được nghiệm (có thể hệ vô nghiệm)."
        return ket_qua
    for bo in cac_bo:
        ket_qua["nghiem"].append({"gia_tri": [
            mo_ta_gia_tri(t, bo.get(b, b)) for t, b in zip(ten_bien, bien)]})
    ket_qua["thong_bao"] = f"{mo_ta_he}, phi tuyến: tìm được {len(cac_bo)} bộ nghiệm."
    return ket_qua


if __name__ == "__main__":
    chay(giai_he)
