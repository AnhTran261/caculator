using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;

namespace Caculator.Views
{
    public partial class PhuongTrinhView : UserControl
    {
        private static readonly string[] MuX = { "x⁴", "x³", "x²", "x", "" };
        private static readonly Brush NenLoi = new SolidColorBrush(Color.FromRgb(0xFE, 0xE2, 0xE2));

        public PhuongTrinhView()
        {
            InitializeComponent();
            CapNhatPhuongTrinh();
        }

        private TextBox[] CacO
        {
            get { return new[] { txtA, txtB, txtC, txtD, txtE }; }
        }

        /// <summary>Đọc số, chấp nhận cả dấu chấm và dấu phẩy thập phân. Ô trống = 0.</summary>
        private static bool DocSo(string s, out double giaTri)
        {
            s = (s ?? "").Trim().Replace(',', '.');
            if (s.Length == 0) { giaTri = 0; return true; }
            return double.TryParse(s, NumberStyles.Float, CultureInfo.InvariantCulture, out giaTri)
                   && !double.IsNaN(giaTri) && !double.IsInfinity(giaTri);
        }

        private void HeSo_TextChanged(object sender, TextChangedEventArgs e)
        {
            var box = (TextBox)sender;
            double v;
            box.Background = DocSo(box.Text, out v) ? Brushes.White : NenLoi;
            CapNhatPhuongTrinh();
        }

        private void HeSo_GotFocus(object sender, RoutedEventArgs e)
        {
            ((TextBox)sender).SelectAll();
        }

        private void HeSo_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Enter && btnGiai.IsEnabled) BtnGiai_Click(sender, e);
        }

        private void CapNhatPhuongTrinh()
        {
            if (lblPhuongTrinh == null) return;
            var sb = new StringBuilder();
            TextBox[] o = CacO;
            for (int i = 0; i < 5; i++)
            {
                double v;
                if (o[i] == null || !DocSo(o[i].Text, out v)) { lblPhuongTrinh.Text = "Hệ số không hợp lệ"; return; }
                if (v == 0) continue;

                double tri = Math.Abs(v);
                string so = (tri == 1 && MuX[i] != "") ? "" : tri.ToString("G10", CultureInfo.InvariantCulture);

                if (sb.Length == 0) sb.Append(v < 0 ? "−" : "");
                else sb.Append(v < 0 ? " − " : " + ");
                sb.Append(so + MuX[i]);
            }
            lblPhuongTrinh.Text = (sb.Length == 0 ? "0" : sb.ToString()) + " = 0";
        }

        private async void BtnGiai_Click(object sender, RoutedEventArgs e)
        {
            var heSo = new double[5];
            TextBox[] o = CacO;
            for (int i = 0; i < 5; i++)
            {
                if (!DocSo(o[i].Text, out heSo[i]))
                {
                    MessageBox.Show(Window.GetWindow(this), "Hệ số \"" + o[i].Text + "\" không phải là số hợp lệ.",
                                    "Lỗi nhập liệu", MessageBoxButton.OK, MessageBoxImage.Warning);
                    o[i].Focus();
                    return;
                }
            }

            btnGiai.IsEnabled = false;
            lblDangTinh.Visibility = Visibility.Visible;
            lvNghiem.ItemsSource = null;
            try
            {
                var duLieu = new { a = heSo[0], b = heSo[1], c = heSo[2], d = heSo[3], e = heSo[4] };
                KetQuaPhuongTrinh kq = await PythonRunner.ChayAsync<KetQuaPhuongTrinh>("solver.py", duLieu);

                lblThongBao.Text = kq.thong_bao;
                lblThongBao.Foreground = (Brush)FindResource(kq.ok ? "MauChu" : "MauLoi");
                lvNghiem.ItemsSource = (kq.nghiem ?? new List<NghiemPT>())
                    .Select((n, i) => new
                    {
                        STT = "x" + (i + 1),
                        GiaTri = n.gia_tri,
                        ChinhXac = string.IsNullOrEmpty(n.chinh_xac) ? "(quá dài)" : n.chinh_xac,
                        Loai = n.so_thuc ? "Thực" : "Phức",
                    })
                    .ToList();
            }
            finally
            {
                btnGiai.IsEnabled = true;
                lblDangTinh.Visibility = Visibility.Collapsed;
            }
        }

        private void BtnXoa_Click(object sender, RoutedEventArgs e)
        {
            foreach (TextBox box in CacO) box.Text = "0";
            lvNghiem.ItemsSource = null;
            lblThongBao.Foreground = (Brush)FindResource("MauChu");
            lblThongBao.Text = "Nhập hệ số rồi bấm “Giải phương trình” (hoặc Enter).";
            txtA.Focus();
        }
    }
}
