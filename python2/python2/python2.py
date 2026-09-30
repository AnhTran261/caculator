import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ==========================================
# 1. ĐỌC VÀ CHUẨN HÓA LẠI DỮ LIỆU SẠCH
# ==========================================
df = pd.read_excel('result.xlsx')
df.columns = ['Ngay', 'Ket_Qua', 'Jackpot_1', 'Jackpot_2']
df['Ngay_Sach'] = df['Ngay'].astype(str).str.split(',').str[-1].str.strip()
df['Ngay_Chuan'] = pd.to_datetime(df['Ngay_Sach'], format='%d/%m/%Y', errors='coerce')
df = df.dropna(subset=['Ngay_Chuan']).sort_values('Ngay_Chuan').reset_index(drop=True)

# Tách thành ma trận số
df_split = df['Ket_Qua'].astype(str).str.strip().str.split(r'\s+', expand=True).astype(int)
df_split.columns = [f'Num_{i}' for i in range(1, 8)]

# ==========================================
# 2. PHÂN TÍCH BẰNG CHỨNG THỐNG KÊ (TOÀN BỘ FILE)
# ==========================================
# Khởi tạo bảng điểm từ 1 đến 55 (mặc định ban đầu bằng 0)
diem_so = pd.Series(0.0, index=range(1, 56))

# --- Tiêu chí 1: Tần suất xuất hiện lịch sử ---
tat_ca_so = df_split.values.flatten()
tan_suat = pd.Series(tat_ca_so).value_counts()
# Chuẩn hóa điểm tần suất về khoảng từ 0 đến 1
tan_suat_score = (tan_suat - tan_suat.min()) / (tan_suat.max() - tan_suat.min())
diem_so = diem_so.add(tan_suat_score, fill_value=0)

# --- Tiêu chí 2: Ma trận dịch chuyển Markov (Hành vi gối đầu) ---
matrix_markov = np.zeros((56, 56))
for i in range(len(df_split) - 1):
    ky_nay = df_split.iloc[i].values
    ky_sau = df_split.iloc[i+1].values
    for s_nay in ky_nay:
        for s_sau in ky_sau:
            matrix_markov[s_nay][s_sau] += 1

# Lấy bộ số của kỳ cuối cùng làm gốc để tìm số gối đầu
ky_cuoi_cung = df_split.iloc[-1].values
diem_goi_dau = np.zeros(56)
for so in ky_cuoi_cung:
    diem_goi_dau += matrix_markov[so]

# Chuẩn hóa điểm Markov về khoảng 0 đến 1 và cộng vào bảng điểm tổng
markov_score = pd.Series(diem_goi_dau[1:], index=range(1, 56))
markov_score_norm = (markov_score - markov_score.min()) / (markov_score.max() - markov_score.min())
diem_so = diem_so.add(markov_score_norm, fill_value=0)

# --- Tiêu chí 3: Xu hướng Tuyến tính vị trí ---
X = np.array(df_split.index).reshape(-1, 1)
ky_tiep_theo = len(df_split)
for i in range(1, 8):
    y = df_split[f'Num_{i}'].values
    model = LinearRegression()
    model.fit(X, y)
    pred = int(np.clip(round(model.predict([[ky_tiep_theo]])[0]), 1, 55))
    # Cộng điểm thưởng lớn (cộng thẳng 0.5 điểm) cho số trúng xu hướng tuyến tính
    if pred in diem_so.index:
        diem_so[pred] += 0.5

# ==========================================
# 3. ĐƯA RA DỰ ĐOÁN CUỐI CÙNG
# ==========================================
# Sắp xếp các số có tổng điểm cao nhất dựa trên tất cả bằng chứng
cac_so_uu_tien = diem_so.sort_values(ascending=False)

# Chọn ra 6 số chính có điểm cao nhất và sắp xếp từ nhỏ đến lớn
sau_so_chinh = sorted(list(cac_so_uu_tien.head(6).index))

# Chọn số tiếp theo trong danh sách làm số đặc biệt (Jackpot 2)
so_dac_biet_du_doan = cac_so_uu_tien.index[6]

# Hiển thị kết quả
print("============================================================")
print("📊 BÁO CÁO DỰ ĐOÁN DỰA TRÊN TOÀN BỘ BẰNG CHỨNG THỐNG KÊ 📊")
print("============================================================")
print(f"-> 6 số chính dự đoán (Jackpot 1):  {' '.join([f'{x:02d}' for x in sau_so_chinh])}")
print(f"-> Số đặc biệt dự đoán (Jackpot 2): {so_dac_biet_du_doan:02d}")
print("------------------------------------------------------------")
print("💡 Top 6 con số có 'hành vi' mạnh nhất được mô hình chấm điểm cao nhất:")
for rank, (num, score) in enumerate(cac_so_uu_tien.head(6).items(), 1):
    print(f"   Hạng {rank}: Số {num:02d} (Tổng điểm quy đổi: {score:.2f})")
print("============================================================")