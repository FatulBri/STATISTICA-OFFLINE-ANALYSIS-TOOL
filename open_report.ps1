Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Diagnostics;
public class WinMax {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
}
"@

# Open report in Chrome
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "file:///C:/statistica-offline-analysis-tool/output/sample/report.html"
Start-Sleep -Seconds 3

# Find Chrome and maximize it
$procs = Get-Process -Name "chrome" -ErrorAction SilentlyContinue
foreach ($p in $procs) {
    if ($p.MainWindowHandle -ne [IntPtr]::Zero) {
        [WinMax]::ShowWindow($p.MainWindowHandle, 3)  # SW_MAXIMIZE
        [WinMax]::SetForegroundWindow($p.MainWindowHandle)
        [WinMax]::BringWindowToTop($p.MainWindowHandle)
        break
    }
}
Start-Sleep -Seconds 2

# Screenshot
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
$gfx = [System.Drawing.Graphics]::FromImage($bmp)
$gfx.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
$bmp.Save('C:\statistica-offline-analysis-tool\chrome_report.png')
$gfx.Dispose()
$bmp.Dispose()
Write-Host "Done - screenshot saved as chrome_report.png"
