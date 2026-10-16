#!/usr/bin/env bash
# TShift bulut olcum makinesi -- OLCUM BLOGU (kur.sh sonrasi; nohup ile; commit YOK)
#   nohup bash /opt/tshift/00-DEVIR/bulut/blok.sh > /opt/blok.log 2>&1 &
# Her adim gunluge saat damgasiyla yazar; sonuclar /opt/sonuc/ altina da kopyalanir
# (tek scp ile iner). Rehber: 00-DEVIR/BULUT-OLCUM-MAKINESI.md
# Sira: once olcumler, EN SONA mutasyon (O-20/O-21: ikisi ayni anda kosmaz).
set -uo pipefail
PY=/opt/venv/bin/python
K=/opt/tshift
O=$K/08-motor-testleri/gercekci-veri-seti
G=$O/kosu-gunlugu-$(date +%F)-bulut.txt
MAK=$(hostname)
yaz() { echo "$(date '+%H:%M:%S')  $*" | tee -a "$G"; }
topla() { mkdir -p /opt/sonuc; cp -f "$O"/kalite-olcumu-*bulut*.json /opt/sonuc/ 2>/dev/null; cp -rf "$O"/planlar/kalite-olcumu-*bulut* /opt/sonuc/ 2>/dev/null; cp -f "$O"/fikstur/_*EK*.json "$O"/fikstur/_referans-L1*.json "$O"/fikstur/_sahne-L1*.json /opt/sonuc/ 2>/dev/null; cp -f "$O"/kosu-gunlugu-*bulut*.txt /opt/sonuc/ 2>/dev/null; }
cd "$K" && git log --oneline -1 | tee -a "$G"
yaz "BLOK BASLADI ($MAK, $(nproc) cekirdek)"
cd "$O"
# 1. Ekili sahne 500 (tanik; A1) -- fm'siz, asimsiz, eksiksiz planin KESIN var oldugu sahne
if [ ! -f "$O/fikstur/_sahne-L1-EK-95.json" ]; then
  yaz "ekili 500 (uretec tabani) basliyor: tanik 900 sn"
  $PY ekili.py --olcek 1.0 --saniye 900 2>&1 | tee -a "$G"; yaz "ekili 500 cikis ${PIPESTATUS[0]}"
fi
if [ -f "$O/fikstur/_sahne-L1-EK-95.json" ]; then
  yaz "EK L1 varsayilan 1800 x 3 basliyor (--devam)"
  $PY kalite-olc.py --seviye 1 --kaynak ekili --saniye 1800 --tekrar 3 --yapilandirma varsayilan --etiket ekili-bulut-1800 --devam; yaz "EK 1800 x 3 cikis $?"
  topla
fi
# 2. VS2 500 referansi + L1 VS2 olcumu
if [ ! -f "$O/fikstur/_sahne-L1-VS2-95.json" ]; then
  yaz "VS2 500 referansi basliyor (1800 sn)"
  $PY merdiven.py referans --olcek 1.0 --kaynak veri-seti --saniye 1800 2>&1 | tee -a "$G"; yaz "VS2 500 referansi cikis ${PIPESTATUS[0]}"
fi
if [ -f "$O/fikstur/_sahne-L1-VS2-95.json" ]; then
  yaz "VS2 L1 varsayilan 1800 x 3 basliyor (--devam)"
  $PY kalite-olc.py --seviye 1 --kaynak veri-seti --saniye 1800 --tekrar 3 --yapilandirma varsayilan --etiket bulut-1800 --devam; yaz "VS2 1800 x 3 cikis $?"
  topla
fi
# 3. Capraz denetim (D): her referans / tanik / kayitli plan bugunku dogrulayicidan
yaz "capraz denetim basliyor (--puan)"
$PY capraz-denetim.py --puan --json "$O/capraz-denetim-$(date +%F)-bulut.json" 2>&1 | tail -n 30 | tee -a "$G"; yaz "capraz denetim cikis ${PIPESTATUS[0]} (0 = sart tutmayan yok)"
cp -f "$O"/capraz-denetim-*bulut.json /opt/sonuc/ 2>/dev/null
# 4. Tam mutasyon -- olcumler BITTI, simdi
cd "$K/09-motor"; yaz "tam mutasyon basliyor"
$PY mutasyon_kostur.py 2>&1 | tail -n 5 | tee -a "$G"; yaz "tam mutasyon cikis ${PIPESTATUS[0]}"
# 5. 751 referansi (T-82 merdiveni)
cd "$O"
if [ ! -f "$O/fikstur/_referans-L1-95-1.5.json" ]; then
  yaz "merdiven 751: uretec referansi basliyor (3600 sn)"
  $PY merdiven.py referans --olcek 1.5 --saniye 3600 2>&1 | tail -n 5 | tee -a "$G"; yaz "751 referansi cikis ${PIPESTATUS[0]}"
fi
topla
yaz "BLOK BITTI -- sonuclar /opt/sonuc/ ; indir, sonra makineyi SIL"
