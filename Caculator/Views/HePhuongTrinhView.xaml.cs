using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;

namespace Caculator.Views
{
    public partial class HePhuongTrinhView : UserControl
    {
        public HePhuongTrinhView()
        {
            InitializeComponent();
        }

        private void NutMau_Click(object sender, RoutedEventArgs e)
        {
            txtHe.Text = (string)((Button)sender).Tag;
            txtHe.Focus();
            txtHe.CaretIndex = txtHe.Text.Length;
        }

        private void TxtHe_PreviewKeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Enter && Keyboard.Modifiers == ModifierKeys.Control)
            {
                if (btnGiai.IsEnabled) BtnGiai_Click(sender, e);
                e.Handled = true;
            }
        }

        private async void BtnGiai_Click(object sender, RoutedEventArgs e)
        {
            string[] dong = txtHe.Text.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None);

            btnGiai.IsEnabled = false;
            lblDangTinh.Visibility = Visibility.Visible;
            lvNghiem.ItemsSource = null;
            try
            {
                KetQuaHePT kq = await PythonRunner.ChayAsync<KetQuaHePT>("he_pt.py", new { phuong_trinh = dong });

                lblThongBao.Text = kq.thong_bao;
                lblThongBao.Foreground = (Brush)FindResource(kq.ok ? "MauChu" : "MauLoi");

                icHieuLa.ItemsSource = kq.hieu_la;
                pnlHieuLa.Visibility = kq.hieu_la != null && kq.hieu_la.Count > 0 ? Visibility.Visible : Visibility.Collapsed;

                // Trải phẳng: mỗi (bộ nghiệm, ẩn) là một dòng; chỉ ghi số bộ ở dòng đầu của bộ
                var dongKetQua = new List<object>();
                var cacBo = kq.nghiem ?? new List<BoNghiem>();
                for (int i = 0; i < cacBo.Count; i++)
                {
                    var giaTri = cacBo[i].gia_tri ?? new List<GiaTriBien>();
                    for (int j = 0; j < giaTri.Count; j++)
                    {
                        dongKetQua.Add(new
                        {
                            Bo = j == 0 ? "#" + (i + 1) : "",
                            Bien = giaTri[j].bien,
                            ChinhXac = giaTri[j].chinh_xac,
                            XapXi = string.IsNullOrEmpty(giaTri[j].xap_xi) ? "—" : giaTri[j].xap_xi,
                        });
                    }
                }
                lvNghiem.ItemsSource = dongKetQua;
            }
            finally
            {
                btnGiai.IsEnabled = true;
                lblDangTinh.Visibility = Visibility.Collapsed;
            }
        }

        private void BtnXoa_Click(object sender, RoutedEventArgs e)
        {
            txtHe.Clear();
            lvNghiem.ItemsSource = null;
            icHieuLa.ItemsSource = null;
            pnlHieuLa.Visibility = Visibility.Collapsed;
            lblThongBao.Foreground = (Brush)FindResource("MauChu");
            lblThongBao.Text = "Nhập hệ rồi bấm “Giải hệ”.";
            txtHe.Focus();
        }
    }
}
