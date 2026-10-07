cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo && python3 - <<'PYEOF'
import io
p="08-motor-testleri/gercekci-veri-seti/kesif/2026-10-06-veri-seti-merdiveni/OKU-BENI.md"
s=io.open(p,encoding="utf-8").read()
R=[('''| Geçen haftanın vardiyaları | 500 kişinin hepsinde **boş**; devreden adalet yükü hepsinde 0 |''',
'''| Geçen haftanın vardiyaları | 500 kişinin hepsinde **boş** (`gecmis_vardiyalar`). ~~Devreden adalet yükü hepsinde 0~~ — *düzeltme 7 Ekim (inceleme): üretici 500 kişinin 124'üne sıfırdan farklı `devir_yuk` yazıyor (adalet bilerek dengesiz); 6 Ekim'de tek bir kişinin satırına bakıp genellemiştim* |'''),
('''veride karşılığı olmadığı için temiz (geçmiş boş → ardışık gün, ardışık gece,
ardışık hafta sonu, gece postası devri geçmişten zorlanamıyor; yayınlanmış
plan yok → donmuş gün zorlanamıyor).''',
'''veride karşılığı olmadığı için temiz (geçen haftanın vardiyaları boş →
ardışık gün, ardışık gece, ardışık hafta sonu, gece postası devri geçmişten
zorlanamıyor; yayınlanmış plan yok → donmuş gün zorlanamıyor).'''),
]
for old,new in R:
    assert s.count(old)==1, old[:80]
    s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
PYEOF
grep -n "geçmiş boş" 00-DEVIR/00-BURADAN-BASLA.md 00-DEVIR/06-ACIK-RISKLER.md DEGISIM-GUNLUGU.md 00-DEVIR/oturumlar/2026-10-06-uc-profil-ve-fazla-mesai-artigi.md | cut -c1-120