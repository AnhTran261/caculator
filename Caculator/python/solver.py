"""Giải phương trình ax^4 + bx^3 + cx^2 + dx + e = 0 bằng sympy.

Vào (stdin):  {"a": 1, "b": 0, "c": -5, "d": 0, "e": 4}
Ra  (stdout): {"ok": true, "bac": 4, "thong_bao": "...", "nghiem": [{"gia_tri", "chinh_xac", "so_thuc"}]}
"""
import sympy as sp

from chung import chay, dinh_dang_so, hien_thi

TEN_BAC = {1: "bậc nhất", 2: "bậc hai", 3: "bậc ba", 4: "bậc bốn"}


def giai(a, b, c, d, e):
    x = sp.Symbol("x")
    he_so = [sp.nsimplify(v) for v in (a, b, c, d, e)]
    bieu_thuc = sum(k * x**(4 - i) for i, k in enumerate(he_so))

    bac = int(sp.degree(bieu_thuc, x)) if bieu_thuc != 0 else 0
    if bac <= 0:
        if bieu_thuc == 0:
            return {"bac": 0, "thong_bao": "Phương trình có VÔ SỐ NGHIỆM (0 = 0).", "nghiem": []}
        return {"bac": 0, "thong_bao": f"Phương trình VÔ NGHIỆM ({e:g} = 0 là vô lý).", "nghiem": []}

    nghiem = []
    for r in sp.solve(bieu_thuc, x):
        gia_tri, la_so_thuc = dinh_dang_so(sp.N(r, 15))
        chinh_xac = hien_thi(sp.simplify(r))
        nghiem.append({
            "gia_tri": gia_tri,
            "chinh_xac": chinh_xac if len(chinh_xac) <= 60 else "",
            "so_thuc": la_so_thuc,
        })

    so_thuc = sum(1 for n in nghiem if n["so_thuc"])
    thong_bao = (f"Phương trình {TEN_BAC[bac]}: {len(nghiem)} nghiệm phân biệt "
                 f"({so_thuc} thực, {len(nghiem) - so_thuc} phức).")
    return {"bac": bac, "thong_bao": thong_bao, "nghiem": nghiem}


if __name__ == "__main__":
    chay(lambda d: giai(*(float(d[k]) for k in "abcde")))
