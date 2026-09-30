using System.Collections.ObjectModel;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;

namespace Caculator.Views
{
    public class DongLichSu
    {
        public string BieuThuc { get; set; }
        public string KetQua { get; set; }
        public string KetQuaHienThi { get { return "= " + KetQua; } }
    }

    public partial class MayTinhView : UserControl
    {
        // Sau khi bấm "=", bấm một toán tử sẽ tính tiếp từ Ans; bấm số thì bắt đầu biểu thức mới
        private static readonly string[] ToanTu = { "+", "−", "-", "×", "*", "÷", "/", "^", "²" };

        private readonly ObservableCollection<DongLichSu> lichSu = new ObservableCollection<DongLichSu>();
        private double? ans;
        private bool vuaTinh;
        private bool dangTinh;

        public MayTinhView()
        {
            InitializeComponent();
            lstLichSu.ItemsSource = lichSu;
            Loaded += (s, e) => txtBieuThuc.Focus();
        }

        private void Nut_Click(object sender, RoutedEventArgs e)
        {
            string tag = (string)((Button)sender).Tag;
            switch (tag)
            {
                case "=":
                    Tinh();
                    return;
                case "C":
                    XoaHet();
                    break;
                case "DEL":
                    XoaMotKyTu();
                    break;
                default:
                    BatDauTuKetQuaCu(tag);
                    Chen(tag);
                    break;
            }
            vuaTinh = false;
            txtBieuThuc.Focus();
        }

        private void BatDauTuKetQuaCu(string chuSapGo)
        {
            if (!vuaTinh) return;
            txtBieuThuc.Text = ToanTu.Contains(chuSapGo) ? "Ans" : "";
            txtBieuThuc.CaretIndex = txtBieuThuc.Text.Length;
            vuaTinh = false;
        }

        private void Chen(string s)
        {
            int viTri = txtBieuThuc.SelectionStart;
            txtBieuThuc.SelectedText = s;
            txtBieuThuc.SelectionLength = 0;
            txtBieuThuc.CaretIndex = viTri + s.Length;
        }

        private void XoaMotKyTu()
        {
            if (txtBieuThuc.SelectionLength > 0) { txtBieuThuc.SelectedText = ""; return; }
            int viTri = txtBieuThuc.CaretIndex;
            if (viTri == 0) return;
            txtBieuThuc.Text = txtBieuThuc.Text.Remove(viTri - 1, 1);
            txtBieuThuc.CaretIndex = viTri - 1;
        }

        private void XoaHet()
        {
            txtBieuThuc.Clear();
            lblKetQua.Text = "0";
            lblLoi.Text = "";
        }

        private async void Tinh()
        {
            string bieuThuc = txtBieuThuc.Text.Trim();
            if (bieuThuc.Length == 0 || dangTinh) return;

            dangTinh = true;
            lblDangTinh.Visibility = Visibility.Visible;
            try
            {
                var duLieu = new { bieu_thuc = bieuThuc, @do = rbDo.IsChecked == true, ans = ans };
                KetQuaTinhToan kq = await PythonRunner.ChayAsync<KetQuaTinhToan>("calc.py", duLieu);

                if (kq.ok)
                {
                    lblKetQua.Text = kq.ket_qua;
                    lblLoi.Text = "";
                    ans = kq.gia_tri;
                    lichSu.Insert(0, new DongLichSu { BieuThuc = bieuThuc, KetQua = kq.ket_qua });
                    vuaTinh = true;
                }
                else
                {
                    lblLoi.Text = kq.thong_bao;
                }
            }
            finally
            {
                dangTinh = false;
                lblDangTinh.Visibility = Visibility.Hidden;
                txtBieuThuc.Focus();
                txtBieuThuc.CaretIndex = txtBieuThuc.Text.Length;
            }
        }

        private void TxtBieuThuc_PreviewKeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Enter) { Tinh(); e.Handled = true; }
            else if (e.Key == Key.Escape) { XoaHet(); vuaTinh = false; e.Handled = true; }
            else if (e.Key == Key.Back || e.Key == Key.Delete) vuaTinh = false;
        }

        private void TxtBieuThuc_PreviewTextInput(object sender, TextCompositionEventArgs e)
        {
            BatDauTuKetQuaCu(e.Text);
        }

        private void LstLichSu_Click(object sender, MouseButtonEventArgs e)
        {
            var dong = lstLichSu.SelectedItem as DongLichSu;
            if (dong == null) return;
            txtBieuThuc.Text = dong.BieuThuc;
            lblKetQua.Text = dong.KetQua;
            lblLoi.Text = "";
            vuaTinh = false;
            lstLichSu.SelectedItem = null;
            txtBieuThuc.Focus();
            txtBieuThuc.CaretIndex = txtBieuThuc.Text.Length;
        }

        private void BtnXoaLichSu_Click(object sender, RoutedEventArgs e)
        {
            lichSu.Clear();
        }
    }
}
