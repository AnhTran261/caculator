import sympy as sp

def nhap_he_so(ten_he_so):
    """Hàm đảm bảo người dùng nhập đúng một số thực, nếu nhập sai sẽ bắt nhập lại"""
    while True:
        try:
            thong_tin_nhap = input(f"Nhập hệ số {ten_he_so}: ")
            # Chuyển đổi chuỗi vừa nhập thành số thực (float)
            gia_tri = float(thong_tin_nhap)
            return gia_tri
        except ValueError:
            print("❌ Lỗi: Vui lòng chỉ nhập số thực (Ví dụ: 1, -2, 5.5). Hãy thử lại!")

def giai_phuong_trinh_tong_quat(a, b, c, d, e):
    x = sp.Symbol('x')
    print("\n" + "="*50)
    print(f"Xét phương trình: {a}x^4 + {b}x^3 + {c}x^2 + {d}x + {e} = 0")
    print("="*50)
    
    if a != 0:
        print("-> Tiến hành giải phương trình bậc 4")
        phuong_trinh = a*x**4 + b*x**3 + c*x**2 + d*x + e
    elif b != 0:
        print("-> Tiến hành giải phương trình bậc 3")
        phuong_trinh = b*x**3 + c*x**2 + d*x + e
    elif c != 0:
        print("-> Tiến hành giải phương trình bậc 2")
        phuong_trinh = c*x**2 + d*x + e
    elif d != 0:
        print("-> Tiến hành giải phương trình bậc 1")
        phuong_trinh = d*x + e
    else:
        if e == 0:
            return "Kết quả: Phương trình có VÔ SỐ NGHIỆM (0 = 0)"
        else:
            return f"Kết quả: Phương trình VÔ NGHIỆM ({e} = 0 là vô lý)"

    # Giải phương trình
    nghiem = sp.solve(phuong_trinh, x)
    return f"Kết quả nghiệm: {nghiem}"

# --- CHƯƠNG TRÌNH CHÍNH ---
if __name__ == "__main__":
    print("=== CHƯƠNG TRÌNH GIẢI PHƯƠNG TRÌNH TỰ DO (BẬC 1 ĐẾN BẬC 4) ===")
    print("Phương trình dạng tổng quát: ax^4 + bx^3 + cx^2 + dx + e = 0\n")
    
    # Tiến hành nhận dữ liệu nhập từ người dùng
    a = nhap_he_so('a')
    b = nhap_he_so('b')
    c = nhap_he_so('c')
    d = nhap_he_so('d')
    e = nhap_he_so('e')
    
    # Gọi hàm giải phương trình và in kết quả
    ket_qua = giai_phuong_trinh_tong_quat(a, b, c, d, e)
    print(ket_qua)