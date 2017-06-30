;;; 重启PIME
if not A_IsAdmin
{
    Run *RunAs "%A_ScriptFullPath%"  ; Requires v1.0.92.01+
    ExitApp
}
Process, Close, PIMELauncher.exe
Run, "c:\Program Files (x86)\PIME\PIMELauncher.exe"
