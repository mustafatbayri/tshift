cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo && python3 - <<'PYEOF'
import io
for p,old,new in [
 ("00-DEVIR/00-BURADAN-BASLA.md","350 kişi-saat; asgari talep sözleşme saatlerinin %65'i), geçmiş boş,","350 kişi-saat; asgari talep sözleşme saatlerinin %65'i), geçen haftanın vardiyaları boş (devreden adalet yükü 124 kişide var — 7 Ekim düzeltmesi),"),
 ("DEGISIM-GUNLUGU.md","altında 350 kişi-saat), geçmiş boş, yayınlanmış plan yok, herkes tek ekipte.","altında 350 kişi-saat), geçen haftanın vardiyaları boş *(\"geçmiş boş\" yazılmıştı; devreden adalet yükü 124 kişide var — 7 Ekim düzeltmesi)*, yayınlanmış plan yok, herkes tek ekipte."),
]:
    s=io.open(p,encoding="utf-8").read()
    assert s.count(old)==1,(p,old[:50])
    s=s.replace(old,new)
    io.open(p,"w",encoding="utf-8").write(s)
print("ok")
PYEOF
cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/09-motor && grep -n "^MUTASYONLAR\|GRUPLAR\|def _kostur" mutasyon_kostur.py | head -5; sed -n 1,60p mutasyon_kostur.py | grep -n "tam-kosu\|damga\|OZET" | head