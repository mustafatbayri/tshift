# =============================================================================
# TShift - testleri calistir
#
#   .\TEST.ps1
#
# Neden bu betik var: calisan API, derleyicinin degistirmesi gereken DLL'leri
# kilitler ve "dosya baska bir surec tarafindan kullaniliyor" hatasi cikar.
# Hata kodla ilgili degildir ama okumasi uzun surer ve dikkat dagitir.
# Betik once API'yi durdurur, sonra testleri calistirir.
# =============================================================================

$ErrorActionPreference = "Stop"

$surecler = Get-Process -Name TShift.Api -ErrorAction SilentlyContinue
if ($surecler) {
    Write-Host "Calisan API durduruluyor ($($surecler.Count) surec)..." -ForegroundColor DarkGray
    $surecler | Stop-Process -Force
    Start-Sleep -Milliseconds 700
}

$db = docker ps --filter name=tshift-db --format "{{.Status}}"
if (-not $db) {
    Write-Host "Veritabani ayakta degil. Baslatiliyor..." -ForegroundColor Yellow
    docker compose up -d | Out-Null
    Start-Sleep -Seconds 3
}

Push-Location "$PSScriptRoot\backend"
try {
    dotnet test
}
finally {
    Pop-Location
}
