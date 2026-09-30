using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using Caculator.Views;

namespace Caculator
{
    public partial class MainWindow : Window
    {
        // Mỗi màn hình chỉ tạo một lần, nên chuyển qua lại không mất dữ liệu đang nhập
        private readonly Dictionary<RadioButton, UserControl> manHinh = new Dictionary<RadioButton, UserControl>();
        private readonly Dictionary<RadioButton, Func<UserControl>> taoManHinh;

        public MainWindow()
        {
            InitializeComponent();
            taoManHinh = new Dictionary<RadioButton, Func<UserControl>>
            {
                { mnuPhuongTrinh, () => new PhuongTrinhView() },
                { mnuMayTinh,     () => new MayTinhView() },
                { mnuHePT,        () => new HePhuongTrinhView() },
            };
            mnuPhuongTrinh.IsChecked = true;
        }

        private void Menu_Checked(object sender, RoutedEventArgs e)
        {
            if (taoManHinh == null) return;   // đang khởi tạo
            var muc = (RadioButton)sender;
            UserControl view;
            if (!manHinh.TryGetValue(muc, out view))
            {
                view = taoManHinh[muc]();
                manHinh[muc] = view;
            }
            noiDung.Content = view;
        }

        private void Window_PreviewKeyDown(object sender, KeyEventArgs e)
        {
            if (Keyboard.Modifiers != ModifierKeys.Control) return;
            if (e.Key == Key.D1 || e.Key == Key.NumPad1) { mnuPhuongTrinh.IsChecked = true; e.Handled = true; }
            else if (e.Key == Key.D2 || e.Key == Key.NumPad2) { mnuMayTinh.IsChecked = true; e.Handled = true; }
            else if (e.Key == Key.D3 || e.Key == Key.NumPad3) { mnuHePT.IsChecked = true; e.Handled = true; }
        }
    }
}
