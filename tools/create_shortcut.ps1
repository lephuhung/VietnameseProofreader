param([string]$ExePath, [string]$WorkDir)

# Tự xác định Startup folder (không phụ thuộc tham số có spaces)
$StartupDir = [Environment]::GetFolderPath('Startup')

$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut("$StartupDir\VNGrammar.lnk")
$sc.TargetPath = $ExePath
$sc.WorkingDirectory = $WorkDir
$sc.Description = "VN Grammar Assistant"
$sc.WindowStyle = 7
$sc.Save()
Write-Host "       Shortcut created at: $StartupDir"
