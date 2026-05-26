Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Diagnostics;
public class WinMaxLoc {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
}
"@

# Open localhost in Chrome
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "http://localhost:3000"
Start-Sleep -Seconds 5

# Find Chrome and maximize it
$procs = Get-Process -Name "chrome" -ErrorAction SilentlyContinue
foreach ($p in $procs) {
    if ($p.MainWindowHandle -ne [IntPtr]::Zero) {
        [WinMaxLoc]::ShowWindow($p.MainWindowHandle, 3)  # SW_MAXIMIZE
        [WinMaxLoc]::SetForegroundWindow($p.MainWindowHandle)
        [WinMaxLoc]::BringWindowToTop($p.MainWindowHandle)
        break
    }
}
Start-Sleep -Seconds 3

# Screenshot
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
$gfx = [System.Drawing.Graphics]::FromImage($bmp)
$gfx.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
$bmp.Save('C:\statistica-offline-analysis-tool\chrome_localhost.png')
$gfx.Dispose()
$bmp.Dispose()
Write-Host "Done - screenshot saved as chrome_localhost.png"
