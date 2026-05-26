Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinAPI {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@

$procs = Get-Process -Name "chrome" -ErrorAction SilentlyContinue
foreach ($p in $procs) {
    if ($p.MainWindowHandle -ne [IntPtr]::Zero) {
        [WinAPI]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
        [WinAPI]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
        Write-Host "Chrome brought to front"
        break
    }
}
