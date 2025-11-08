# start_all.ps1 — starts both services in new background processes (PowerShell)
# Usage: .\scripts\start_all.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$root = Join-Path $scriptDir ".." | Resolve-Path
$logs = Join-Path $root "logs"
if (-not (Test-Path $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }

Write-Host "Starting product-service... (logs -> $($logs)\product.log)"
Start-Process -FilePath "go" -ArgumentList "run","main.go" -WorkingDirectory (Join-Path $root "product-service") -NoNewWindow -RedirectStandardOutput (Join-Path $logs "product.log") -RedirectStandardError (Join-Path $logs "product.log")
Start-Sleep -Seconds 1

Write-Host "Starting gateway... (logs -> $($logs)\gateway.log)"
Start-Process -FilePath "go" -ArgumentList "run","main.go" -WorkingDirectory (Join-Path $root "gateway") -NoNewWindow -RedirectStandardOutput (Join-Path $logs "gateway.log") -RedirectStandardError (Join-Path $logs "gateway.log")

Write-Host "Services started. Check logs in $logs"
Write-Host "To stop the services: Get-Process -Name go | Where-Object { $_.Path -like '*go.exe' } | Stop-Process -Force  # be careful"