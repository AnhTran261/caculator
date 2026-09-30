using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Web.Script.Serialization;

namespace Caculator
{
    /// <summary>Phần chung của mọi kết quả trả về từ Python.</summary>
    public class KetQuaCoBan
    {
        public bool ok { get; set; }
        public string thong_bao { get; set; }
    }

    /// <summary>
    /// Gọi một script trong thư mục python\ như một "API":
    /// gửi JSON vào stdin, nhận một dòng JSON từ stdout.
    /// </summary>
    public static class PythonRunner
    {
        // Lệnh chạy Python. Đổi thành đường dẫn đầy đủ (vd: @"C:\Python312\python.exe")
        // nếu máy có nhiều bản Python và bản trên PATH không có sympy.
        public static string PythonExe = "python";

        private const int TimeoutMs = 60000;

        public static Task<T> ChayAsync<T>(string tenScript, object duLieu) where T : KetQuaCoBan, new()
        {
            return Task.Run(() => Chay<T>(tenScript, duLieu));
        }

        private static T Chay<T>(string tenScript, object duLieu) where T : KetQuaCoBan, new()
        {
            string script = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "python", tenScript);
            if (!File.Exists(script))
                return Loi<T>("Không tìm thấy file " + script);

            var json = new JavaScriptSerializer();
            var psi = new ProcessStartInfo
            {
                FileName = PythonExe,
                Arguments = "\"" + script + "\"",
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8,
            };
            psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";

            Process p;
            try
            {
                p = Process.Start(psi);
            }
            catch (Exception ex)
            {
                return Loi<T>("Không chạy được Python (\"" + PythonExe + "\"): " + ex.Message);
            }

            using (p)
            {
                Task<string> stdout = p.StandardOutput.ReadToEndAsync();
                Task<string> stderr = p.StandardError.ReadToEndAsync();

                // Ghi JSON dạng UTF-8 (không BOM) vào stdin rồi đóng lại để Python đọc hết
                try
                {
                    byte[] dauVao = new UTF8Encoding(false).GetBytes(json.Serialize(duLieu));
                    p.StandardInput.BaseStream.Write(dauVao, 0, dauVao.Length);
                    p.StandardInput.Close();
                }
                catch (IOException) { /* Python đã thoát sớm — lỗi sẽ nằm trong stderr */ }

                if (!p.WaitForExit(TimeoutMs))
                {
                    try { p.Kill(); } catch { }
                    return Loi<T>("Python chạy quá lâu (> " + TimeoutMs / 1000 + " giây).");
                }

                string output = stdout.Result.Trim();
                if (p.ExitCode != 0 || output.Length == 0)
                    return Loi<T>("Python báo lỗi:\n" + stderr.Result.Trim());

                try
                {
                    return json.Deserialize<T>(output);
                }
                catch (Exception ex)
                {
                    return Loi<T>("Không đọc được kết quả từ Python: " + ex.Message + "\n" + output);
                }
            }
        }

        private static T Loi<T>(string thongBao) where T : KetQuaCoBan, new()
        {
            return new T { ok = false, thong_bao = thongBao };
        }
    }

    // ===== Kiểu dữ liệu trả về của từng script =====

    /// <summary>python\solver.py</summary>
    public class KetQuaPhuongTrinh : KetQuaCoBan
    {
        public int bac { get; set; }
        public List<NghiemPT> nghiem { get; set; }
    }

    public class NghiemPT
    {
        public string gia_tri { get; set; }
        public string chinh_xac { get; set; }
        public bool so_thuc { get; set; }
    }

    /// <summary>python\calc.py</summary>
    public class KetQuaTinhToan : KetQuaCoBan
    {
        public string ket_qua { get; set; }
        public double? gia_tri { get; set; }
    }

    /// <summary>python\he_pt.py</summary>
    public class KetQuaHePT : KetQuaCoBan
    {
        public List<string> hieu_la { get; set; }
        public List<string> bien { get; set; }
        public List<BoNghiem> nghiem { get; set; }
    }

    public class BoNghiem
    {
        public List<GiaTriBien> gia_tri { get; set; }
    }

    public class GiaTriBien
    {
        public string bien { get; set; }
        public string chinh_xac { get; set; }
        public string xap_xi { get; set; }
    }
}
