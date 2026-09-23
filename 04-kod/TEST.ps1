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

# ---- Sirlar (T-34) ---------------------------------------------------------
# Testler artik APP_DB_PASSWORD ve DB_PASSWORD istiyor; varsayilanlari yok.
# Degerler .env dosyasindan okunur -- git'e gitmeyen tek yerden.
$envDosya = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envDosya)) {
    Write-Host ".env bulunamadi: $envDosya" -ForegroundColor Red
    Write-Host ".env.example dosyasini kopyalayip .env yapin." -ForegroundColor Yellow
    exit 1
}
Get-Content $envDosya | ForEach-Object {
    if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2].Trim())
    }
}
foreach ($ad in @("DB_PASSWORD", "APP_DB_PASSWORD", "JWT_SECRET")) {
    if (-not [Environment]::GetEnvironmentVariable($ad)) {
        Write-Host "$ad .env icinde yok. Bkz. .env.example (T-34)" -ForegroundColor Red
        exit 1
    }
}

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
