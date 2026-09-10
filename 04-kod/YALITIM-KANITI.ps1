# =============================================================================
# TShift - kimlik ve cok kiracilik yalitimi canli gosterimi
#
# Kullanim (API ayri bir pencerede calisiyorken):
#   .\YALITIM-KANITI.ps1 -Api http://localhost:5146
#
# Kaba kuvvet kilidini de gormek istersen:
#   .\YALITIM-KANITI.ps1 -Api http://localhost:5146 -KabaKuvvet
#   DIKKAT: bu, localhost'u 15 dakika kilitler. Temizleme komutu sonda yaziyor.
#
# NOT: Bu dosya bilerek yalnizca ASCII karakter icerir. Windows PowerShell 5.1
# .ps1 dosyalarini ANSI olarak okur; UTF-8 turkce karakterler ayristiriciyi bozar.
# =============================================================================

param(
    [string]$Api = "http://localhost:5000",
    [switch]$KabaKuvvet
)

$ErrorActionPreference = "Stop"

function Baslik($m) { Write-Host "`n$m" -ForegroundColor Cyan }
function Iyi($m)    { Write-Host "   $m" -ForegroundColor Green }
function Kotu($m)   { Write-Host "   $m" -ForegroundColor Red }
function Soluk($m)  { Write-Host "   $m" -ForegroundColor DarkGray }

# HTTP hatalarini istisna firlatmadan yakalayan sarmalayici.
# Hem Windows PowerShell 5.1 hem PowerShell 7 ile calisir - ikisinde hata
# nesnesinin sekli farkli oldugu icin iki yol da denenir.
function Iste {
    param($Yol, $Metod = "GET", $Govde = $null, $Jeton = $null, $EkBaslik = @{})

    $bas = @{}
    foreach ($k in $EkBaslik.Keys) { $bas[$k] = $EkBaslik[$k] }
    if ($Jeton) { $bas["Authorization"] = "Bearer $Jeton" }

    $p = @{ Uri = "$Api$Yol"; Method = $Metod; Headers = $bas; UseBasicParsing = $true }
    if ($Govde) {
        # Turkce karakterler bozulmasin diye govdeyi UTF-8 bayt dizisi olarak yolluyoruz.
        $p.Body = [System.Text.Encoding]::UTF8.GetBytes(($Govde | ConvertTo-Json -Depth 5))
        $p.ContentType = "application/json; charset=utf-8"
    }

    try {
        $c = Invoke-WebRequest @p
        $g = $null
        if ($c.Content) { try { $g = $c.Content | ConvertFrom-Json } catch { $g = $c.Content } }
        return [pscustomobject]@{ Kod = [int]$c.StatusCode; Govde = $g }
    }
    catch {
        $resp = $_.Exception.Response
        if ($null -eq $resp) { throw }

        $kod = 0
        try { $kod = [int]$resp.StatusCode } catch { }

        # PowerShell 7: govde ErrorDetails icinde. 5.1: akistan okunur.
        $metin = $null
        if ($_.ErrorDetails -and $_.ErrorDetails.Message) {
            $metin = $_.ErrorDetails.Message
        } else {
            try {
                $sr = New-Object System.IO.StreamReader($resp.GetResponseStream())
                $metin = $sr.ReadToEnd()
                $sr.Close()
            } catch { }
        }

        $g = $null
        if ($metin) { try { $g = $metin | ConvertFrom-Json } catch { $g = $metin } }
        return [pscustomobject]@{ Kod = $kod; Govde = $g }
    }
}

# ---- 1 -----------------------------------------------------------------
Baslik "1) API ayakta mi?"
$s = Iste "/health"
Soluk "durum: $($s.Govde.durum)   HTTP $($s.Kod)"
if ($s.Kod -ne 200) { throw "API yanit vermiyor. Portu ve calisan pencereyi kontrol et." }

# ---- 2 -----------------------------------------------------------------
Baslik "2) Ornek veri"
$seed = Iste "/dev/seed" "POST"
if ($seed.Kod -eq 200) {
    $parola = $seed.Govde.parola
    Soluk "Iki firma olusturuldu. Ornek parola: $parola"
} else {
    $parola = "TShift2026!Deneme"
    Soluk "Ornek veri zaten var. Bilinen parola kullanilacak."
}

$kiracilar = @((Iste "/dev/tenants").Govde | ForEach-Object { $_ })
$kiracilar | Format-Table ad, slug
if ($kiracilar.Count -lt 2) { throw "Iki kiraci bekleniyordu, $($kiracilar.Count) bulundu." }

$a = $kiracilar[0]
$b = $kiracilar[1]
$epostaA = "mudur@$($a.slug).test"
$epostaB = "mudur@$($b.slug).test"

# ---- 3 -----------------------------------------------------------------
Baslik "3) Iki firmadan giris"
function Giris($firma, $eposta, $sifre) {
    Iste "/api/v1/auth/login" "POST" @{ firma = $firma; eposta = $eposta; parola = $sifre }
}

$girisA = Giris $a.slug $epostaA $parola
$girisB = Giris $b.slug $epostaB $parola

if ($girisA.Kod -ne 200 -or $girisB.Kod -ne 200) {
    Kotu "Giris basarisiz. A=$($girisA.Kod) B=$($girisB.Kod)"
    Soluk "Hesap kilitliyse 15 dakika bekle ya da sondaki temizleme komutunu calistir."
    throw "Giris yapilamadi."
}

$jetonA = $girisA.Govde.erisimJetonu
$jetonB = $girisB.Govde.erisimJetonu
Iyi "$($a.ad) -> jeton alindi"
Iyi "$($b.ad) -> jeton alindi"
Soluk "Erisim jetonu bitis: $($girisA.Govde.bitis)"

# ---- 4 -----------------------------------------------------------------
Baslik "4) AYNI ADRES -> /api/v1/employees -> IKI FARKLI JETON"
foreach ($ikili in @(,@($a, $jetonA)) + @(,@($b, $jetonB))) {
    $c = (Iste "/api/v1/employees" "GET" $null $ikili[1]).Govde
    Write-Host "`n   --- $($ikili[0].ad)   $($c.adet) kayit" -ForegroundColor Yellow
    $c.kayitlar | Format-Table personelNo, tamAd
}

# ---- 5 -----------------------------------------------------------------
Baslik "5) Jetonsuz istek"
$r = Iste "/api/v1/employees"
if ($r.Kod -eq 401) { Iyi "401 Unauthorized. (beklenen)" } else { Kotu "BEKLENMEDIK: HTTP $($r.Kod)" }

# ---- 6 -----------------------------------------------------------------
Baslik "6) ASIL SINAV: A'nin jetonu + B'nin kimligi baslikta"
Soluk "Dun bu basliga guveniyorduk. Simdi kiraci imzali jetondan okunuyor,"
Soluk "yani baslik yazilsa bile hicbir sey degistiremiyor."
$sahte = (Iste "/api/v1/employees" "GET" $null $jetonA @{ "X-Tenant-Id" = $b.id }).Govde
if ($sahte.kiraciId -eq $a.id) {
    Iyi "Baslik yok sayildi. Donen veri hala $($a.ad) -> $($sahte.adet) kayit."
} else {
    Kotu "SIZINTI: baslik dikkate alindi!"
}

# ---- 7 -----------------------------------------------------------------
Baslik "7) Yanlis parola"
$r = Giris $a.slug $epostaA "bu-parola-yanlis"
if ($r.Kod -eq 401) { Iyi "401  kod: $($r.Govde.kod)" } else { Kotu "BEKLENMEDIK: HTTP $($r.Kod)" }
Soluk "Mesaj bilerek belirsiz: 'firma, e-posta veya parola hatali'."
Soluk "Hangisi oldugu soylenmez, yoksa kayitli e-postalar tespit edilebilir."

# ---- 8 -----------------------------------------------------------------
Baslik "8) Doner yenileme jetonu"
$yeni = Iste "/api/v1/auth/refresh" "POST" @{ yenilemeJetonu = $girisA.Govde.yenilemeJetonu }
if ($yeni.Kod -eq 200) { Iyi "Yeni jeton cifti alindi." } else { Kotu "Yenileme basarisiz: HTTP $($yeni.Kod)" }

# ---- 9 -----------------------------------------------------------------
Baslik "9) CALINMIS JETON: ayni yenileme jetonu ikinci kez"
$hirsiz = Iste "/api/v1/auth/refresh" "POST" @{ yenilemeJetonu = $girisA.Govde.yenilemeJetonu }
if ($hirsiz.Kod -eq 401 -and $hirsiz.Govde.kod -eq "OTURUM_GUVENLIGI") {
    Iyi "Tespit edildi -> $($hirsiz.Govde.kod)"
    $olu = Iste "/api/v1/auth/refresh" "POST" @{ yenilemeJetonu = $yeni.Govde.yenilemeJetonu }
    if ($olu.Kod -ne 200) { Iyi "Mesru kullanicinin yeni jetonu da dusuruldu. (beklenen)" }
    else { Kotu "BEKLENMEDIK: diger oturum hala ayakta." }
} else {
    Kotu "BEKLENMEDIK: HTTP $($hirsiz.Kod)"
}

# ---- 10 ----------------------------------------------------------------
if ($KabaKuvvet) {
    Baslik "10) Kaba kuvvet kilidi"
    Soluk "5 yanlis deneme yapiliyor..."
    for ($i = 1; $i -le 5; $i++) { Giris $a.slug $epostaA "yanlis-$i" | Out-Null }

    $r = Giris $a.slug $epostaA $parola   # DOGRU parola
    if ($r.Kod -eq 429) { Iyi "429  $($r.Govde.kod) - dogru parola bile gecmiyor." }
    else { Kotu "BEKLENMEDIK: HTTP $($r.Kod)" }

    Write-Host ""
    Write-Host "   Kilidi kaldirmak icin 15 dakika beklemek yerine:" -ForegroundColor Yellow
    Soluk 'docker compose exec db psql -U tshift -d tshift -c "DELETE FROM login_attempts;"'
    Soluk 'docker compose exec db psql -U tshift -d tshift -c "UPDATE users SET kilit_bitis=NULL, basarisiz_giris=0;"'
} else {
    Baslik "10) Kaba kuvvet kilidi - atlandi"
    Soluk "Gormek icin -KabaKuvvet ekle. (localhost'u 15 dk kilitler)"
}

Write-Host "`nBitti.`n" -ForegroundColor Cyan
