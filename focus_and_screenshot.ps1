Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Diagnostics;
public class WinHelper {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
    
    public static void FocusChrome() {
        foreach (Process p in Process.GetProcessesByName("chrome")) {
            if (p.MainWindowHandle != IntPtr.Zero) {
                ShowWindow(p.MainWindowHandle, 5);  // SW_SHOW
                ShowWindow(p.MainWindowHandle, 9);  // SW_RESTORE
                SetForegroundWindow(p.MainWindowHandle);
                BringWindowToTop(p.MainWindowHandle);
                break;
            }
        }
    }
}
"@

[WinHelper]::FocusChrome()
Start-Sleep -Seconds 2
Write-Host "Chrome focused, taking screenshot..."

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
$bmp.Save('C:\statistica-offline-analysis-tool\chrome_screenshot.png')
$graphics.Dispose()
$bmp.Dispose()
Write-Host "Screenshot saved!"
