# =============================================================================
# TShift — çok kiracılık yalıtımı canlı gösterimi
#
# Kullanım (API ayrı bir pencerede çalışıyorken):
#   .\YALITIM-KANITI.ps1 -Api http://localhost:5000
#
# Portu API'yi başlattığın pencerede "Now listening on:" satırından al.
# =============================================================================

param([string]$Api = "http://localhost:5000")

$ErrorActionPreference = "Stop"

function Baslik($m) { Write-Host "`n$m" -ForegroundColor Cyan }

# ---- 1 -----------------------------------------------------------------
Baslik "1) API ayakta mi?"
Invoke-RestMethod "$Api/health" | Format-List
Invoke-RestMethod "$Api/health/db" | Format-List

# ---- 2 -----------------------------------------------------------------
Baslik "2) Ornek veri (iki firma)"
try {
    Invoke-RestMethod -Method Post "$Api/dev/seed" | ConvertTo-Json -Depth 5
} catch {
    Write-Host "Ornek veri zaten var, devam ediliyor." -ForegroundColor DarkGray
}

# ---- 3 -----------------------------------------------------------------
Baslik "3) Sistemdeki kiracilar"
# Not: Invoke-RestMethod JSON dizisini bazen tek bir Object[] olarak dondurur.
# ForEach-Object'ten gecirmek diziyi tek tek ogelere acar; @() de sonucu sabitler.
$kiracilar = @(Invoke-RestMethod "$Api/dev/tenants" | ForEach-Object { $_ })
$kiracilar | Format-Table id, ad, slug, birimAdi

if ($kiracilar.Count -lt 2) { throw "Iki kiraci bekleniyordu, $($kiracilar.Count) bulundu." }
$a = $kiracilar[0]
$b = $kiracilar[1]

function Calisanlar($kimlik) {
    Invoke-RestMethod "$Api/api/v1/employees" -Headers @{ "X-Tenant-Id" = $kimlik }
}

# ---- 4 -----------------------------------------------------------------
Baslik "4) AYNI ADRES  ->  /api/v1/employees  ->  IKI FARKLI KIRACI"
Write-Host "   Degisen tek sey X-Tenant-Id basligi." -ForegroundColor DarkGray

foreach ($k in @($a, $b)) {
    $c = Calisanlar $k.id
    Write-Host "`n   --- $($k.ad)" -ForegroundColor Yellow
    Write-Host "       kiraci: $($k.id)   donen kayit: $($c.adet)" -ForegroundColor DarkGray
    $c.kayitlar | Format-Table personelNo, tamAd, durum
}

# ---- 5 -----------------------------------------------------------------
Baslik "5) Baslik hic gonderilmezse"
try {
    Invoke-RestMethod "$Api/api/v1/employees" | Out-Null
    Write-Host "   BEKLENMEDIK: istek gecti. Incelenmeli." -ForegroundColor Red
} catch {
    Write-Host "   Reddedildi. (beklenen davranis)" -ForegroundColor Green
}

# ---- 6 -----------------------------------------------------------------
Baslik "6) Uydurma bir kiraci kimligiyle"
$sahte = [guid]::NewGuid()
$r = Invoke-RestMethod "$Api/api/v1/employees" -Headers @{ "X-Tenant-Id" = $sahte }
Write-Host "   Kimlik : $sahte" -ForegroundColor DarkGray
Write-Host "   Kayit  : $($r.adet)" -ForegroundColor Green
if ($r.adet -ne 0) { Write-Host "   BEKLENMEDIK: sifir olmaliydi!" -ForegroundColor Red }

# ---- 7 -----------------------------------------------------------------
Baslik "7) A kiracisi, B kiracisinin bir calisanini ID ile isteyebilir mi?"
$bCalisanlari = @((Calisanlar $b.id).kayitlar | ForEach-Object { $_ })
if ($bCalisanlari.Count -gt 0) {
    $hedef = $bCalisanlari[0]
    $aListesi = @((Calisanlar $a.id).kayitlar | ForEach-Object { $_ })
    $sizdi = $aListesi | Where-Object { $_.id -eq $hedef.id }
    Write-Host "   Hedef  : $($hedef.tamAd)  ($($b.ad))" -ForegroundColor DarkGray
    if ($sizdi) { Write-Host "   SIZINTI VAR!" -ForegroundColor Red }
    else        { Write-Host "   A kiracisinin listesinde yok. Yalitim saglam." -ForegroundColor Green }
}

Write-Host "`nBitti.`n" -ForegroundColor Cyan
