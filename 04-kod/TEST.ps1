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
$eksik = @()
foreach ($ad in @("DB_PASSWORD", "APP_DB_PASSWORD", "JWT_SECRET")) {
    if (-not [Environment]::GetEnvironmentVariable($ad)) { $eksik += $ad }
}
if ($eksik.Count -gt 0) {
    # Hepsini birden soyluyoruz: tek tek bildirmek her seferinde bir kosum
    # daha demek. Eksik listesi tam olsun ki tek duzenlemede bitsin.
    Write-Host "" 
    Write-Host ".env icinde eksik degisken(ler):" -ForegroundColor Red
    foreach ($ad in $eksik) { Write-Host "  - $ad" -ForegroundColor Red }
    Write-Host ""
    Write-Host "Ornekler icin: 04-kod\.env.example  (T-34)" -ForegroundColor Yellow
    Write-Host "Not: APP_DB_PASSWORD, veritabanindaki tshift_app rolunun" -ForegroundColor DarkGray
    Write-Host "     mevcut parolasiyla AYNI olmali; degistirmek istersen" -ForegroundColor DarkGray
    Write-Host "     once TSHIFT_KURULUM=true ile kurulum kosusu gerekir." -ForegroundColor DarkGray
    exit 1
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
