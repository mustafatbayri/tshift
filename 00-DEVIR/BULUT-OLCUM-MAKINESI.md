# Bulut ölçüm makinesi — kurulum ve koşu rehberi (16 Ekim 2026)

**Neden:** 500 kişilik ölçümler Mustafa'nın PC'sini 7–9 saat kilitliyor (15 Ekim:
Windows Update gece bloğunu öldürdü; gündüz PC kullanılamıyor). Mustafa 16 Ekim
05:46: *"ekstra para harcamaya hazırım. Cloud ortamda ne gerekirse yapacağım."*
Karar Yılmaz'la görüşülüp verilecek; bu belge görüşme bittiği an kurulumun
**tek oturuşta** yapılabilmesi için hazır duruyor. Seçenek karşılaştırması ve
fiyatlar: `oturumlar/2026-10-14-k68-ayarlari-ve-veri-seti.md` §11.

**Değişmeyen kurallar**
- Makine **yalnız ölçüm sırasında** açık; blok bitince **silinir** (saatlik
  faturalama; CCX43 ≈ €0,40/sa, 8 saatlik blok ≈ €3,3). Açık unutulan makine ayda
  €276.
- Bulut makinesi **asla commit / push yapmaz** (tek yazar kuralı). Sonuç
  dosyaları `scp` ile Mustafa'nın PC'sine iner, Mustafa commit'ler.
- Kıyas kuralı (T-82): her makinenin **kendi tabanı**; iki yapılandırma aynı
  makinede kıyaslanır. `kalite-olc.py` kayıtlarında `makine` alanı (hostname)
  bu yüzden var.
- Mutasyon ve ölçüm **aynı anda koşmaz** (O-20/O-21).

---

## 1 · Bir kez: SSH anahtarı (Mustafa'nın PC'si, PowerShell)

```powershell
if (-not (Test-Path $env:USERPROFILE\.ssh\tshift_bulut)) { ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\tshift_bulut -N '""' -C "tshift-bulut" }
Get-Content $env:USERPROFILE\.ssh\tshift_bulut.pub
```

Çıkan tek satır (`ssh-ed25519 AAAA… tshift-bulut`) Hetzner'da **Security → SSH
keys → Add SSH key** ile eklenir (ad: `tshift-bulut`).

## 2 · Makineyi aç (Hetzner Cloud konsolu, ~2 dk)

Proje → **Add Server**: konum **Falkenstein** ya da **Nürnberg**; imaj **Ubuntu
24.04**; tür **Dedicated vCPU → CCX43** (8 fiziksel çekirdek, 64 GB; ilk taban
için) — ilk-çözüm sorunu için daha çok işçi denenecekse **CCX53** (16 fiziksel);
SSH key `tshift-bulut` işaretli; ad `tshift-olcum`. **Create & Buy**. Konsolda
görünen IPv4 adresi aşağıda `<IP>`.

Depo **özel** (private). Makinenin depoyu çekebilmesi için GitHub'da **salt okunur**
bir kişisel erişim belirteci (fine-grained token; yalnız `mustafatbayri/tshift`,
yalnız *Contents: Read*) üretilir ve aşağıda `<TOKEN>` yerine yazılır. Belirteç
yalnız makinede durur, makine silinince gider; depoya **yazılmaz**.

## 3 · Kurulum (PC'den tek komut; ~3 dk)

```powershell
ssh -i $env:USERPROFILE\.ssh\tshift_bulut root@<IP> "bash -s" -- < C:\Users\PC\Desktop\Tshift\00-DEVIR\bulut\kur.sh <TOKEN>
```

`kur.sh` ne yapar: paketleri günceller, Python 3.12 + `venv`, depoyu `/opt/tshift`'e
çeker, `09-motor/requirements.txt`'i kurar (ortools 9.15.6755, pytest 9.1.1),
üç test paketini koşar (09 / 08 / 10-v2) ve `nproc` + sonuçları yazar. **Yeşil
değilse ölçüm başlamaz** (çıktının son satırları söyler).

## 4 · Blok koşusu (PC'den; makine çalışırken PC kapanabilir)

```powershell
ssh -i $env:USERPROFILE\.ssh\tshift_bulut root@<IP> "cd /opt/tshift && nohup bash 00-DEVIR/bulut/blok.sh > /opt/blok.log 2>&1 &"
```

Blok `tmux`/oturum gerektirmez (`nohup`); SSH kapansa da sürer. İlerleme:

```powershell
ssh -i $env:USERPROFILE\.ssh\tshift_bulut root@<IP> "tail -n 20 /opt/blok.log"
```

`blok.sh` içeriği (sıra ve bütçeler orada; her adım `kosu-gunlugu-…-bulut.txt`'e
saat damgasıyla yazar): ekili sahne 500 (tanık; `ekili.py --olcek 1.0 --saniye
900`), ekili sahnede motor 1.800 × 3, VS2 500 referansı, L1 VS2 1.800 × 3,
çapraz denetim (`capraz-denetim.py --puan`), tam mutasyon (ölçümler **bittikten
sonra**), 751 referansı.

## 5 · Sonuçları indir ve makineyi sil

```powershell
cd C:\Users\PC\Desktop\Tshift
scp -i $env:USERPROFILE\.ssh\tshift_bulut -r "root@<IP>:/opt/tshift/08-motor-testleri/gercekci-veri-seti/kalite-olcumu-*bulut*.json" 08-motor-testleri\gercekci-veri-seti\
scp -i $env:USERPROFILE\.ssh\tshift_bulut -r "root@<IP>:/opt/tshift/08-motor-testleri/gercekci-veri-seti/planlar/kalite-olcumu-*bulut*" 08-motor-testleri\gercekci-veri-seti\planlar\
scp -i $env:USERPROFILE\.ssh\tshift_bulut -r "root@<IP>:/opt/tshift/08-motor-testleri/gercekci-veri-seti/fikstur/_*EK*.json" 08-motor-testleri\gercekci-veri-seti\fikstur\
scp -i $env:USERPROFILE\.ssh\tshift_bulut -r "root@<IP>:/opt/tshift/08-motor-testleri/gercekci-veri-seti/kosu-gunlugu-*bulut*.txt" 08-motor-testleri\gercekci-veri-seti\
git status --short
```

Sonra Hetzner konsolunda **Delete server** (ya da PC'den `hcloud` kuruluysa
`hcloud server delete tshift-olcum`). Silinmeden önce `/opt/blok.log`'un son
satırı `BLOK BITTI` olmalı. Commit her zamanki gibi Mustafa'nın PC'sinden,
`.mutasyon-suruyor` kontrolüyle.

## 6 · Bilinmesi gerekenler

- İlk koşuda bulut makinesinin **kendi tabanı** alınır (aynı sahne, aynı ayar,
  6 çekirdekli PC sonuçlarıyla yalnız yön kıyaslanır, sayı kıyaslanmaz).
- CP-SAT işçi sayısı varsayılan `os.cpu_count()` = 16 (CCX43'te 8 fiziksel ×2).
  `kalite-olc.py --isci 8` ile fiziksel çekirdek sayısında da ölçülmeli (ürün
  konteyneri sorusu, bulgu 30).
- Makine silinince **her şey gider**; indirilmeyen sonuç yoktur. `blok.sh` bu
  yüzden her adımın sonunda dosyaları makinedeki /opt/sonuc klasörüne de kopyalar — tek
  `scp -r root@<IP>:/opt/sonuc/ .` ile hepsi iner.
- Yedek yol: GitHub Actions kendi koşucusu (oturum §11 seçenek (b)); bu rehber
  önce (a) SSH yolunu kuruyor — daha az parça, hata ayıklaması daha kolay.
