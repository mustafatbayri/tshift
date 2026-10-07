cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/09-motor && python3 - <<'PYEOF'
import io
p="mutasyon_kostur.py"
s=io.open(p,encoding="utf-8").read()
a=s.index("    # ---- \"once fazla mesaisiz\" (T-60 bulgu 20-21) -- K-61 (6 Ekim): URUNUN")
b=s.index("    ('fm_sifir', C, 'bulunamayinca alanlar geri acilmasin (K-38 yolu kapansin)',")
yeni='''    # ---- "once fazla mesaisiz" (T-60 bulgu 20-21) -- K-61 (6 Ekim): URUNUN
    # ---- VARSAYILANI; HAKEM AGIRLIKLARDIR: bulunan plan yalniz baslangic
    # ---- noktasidir, alanlar geri acilir (7 Ekim, O-18). Sert kesim yalniz
    # ---- olcum secenegidir (`fazla_mesai_sifirda_tut`).
    ('fm_sifir', C, 'K-61: varsayilan KAPALI olsun (karar geri alinsin)',
     '    "fazla_mesai_once_sifir": True,',
     '    "fazla_mesai_once_sifir": False,',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-18: sert kesim urunun varsayilani olsun (6 Ekim gecesinin hali)',
     '    "fazla_mesai_sifirda_tut": False,',
     '    "fazla_mesai_sifirda_tut": True,',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'secenek yok sayilsin',
     '    fm_eski = (_fazla_mesaiyi_sifirla(kuruldu)\\n               if ayar.get("fazla_mesai_once_sifir") else [])',
     '    fm_eski = []',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'secenek kapaliyken de uygulansin',
     '    fm_eski = (_fazla_mesaiyi_sifirla(kuruldu)\\n               if ayar.get("fazla_mesai_once_sifir") else [])',
     '    fm_eski = _fazla_mesaiyi_sifirla(kuruldu)',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-18: bulununca hep 0\\'da tutulsun (sert kesim; ilke cignenir)',
     '            sifirda = bulundu and bool(ayar.get("fazla_mesai_sifirda_tut"))',
     '            sifirda = bulundu',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-18: olcum secenegi acikken de 0\\'da tutulmasin',
     '            sifirda = bulundu and bool(ayar.get("fazla_mesai_sifirda_tut"))',
     '            sifirda = False',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-18: bulunamayinca da "0\\'da tutuldu" densin',
     '            sifirda = bulundu and bool(ayar.get("fazla_mesai_sifirda_tut"))',
     '            sifirda = bool(ayar.get("fazla_mesai_sifirda_tut"))',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-18: ciktida "sifirda_tutuldu" hep False yazsin',
     '                "sifirda_tutuldu": sifirda}',
     '                "sifirda_tutuldu": False}',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-18: ciktida "sifirda_tutuldu" bulundu\\'yu yazsin',
     '                "sifirda_tutuldu": sifirda}',
     '                "sifirda_tutuldu": bulundu}',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-18: alanlar yalniz bulunamayinca geri acilsin (6 Ekim gecesi)',
     '            if not sifirda:\\n                # ⚠ HAKEM AGIRLIKLARDIR (K-61).',
     '            if not bulundu:\\n                # ⚠ HAKEM AGIRLIKLARDIR (K-61).',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-18: alanlar hic geri acilmasin',
     '            if not sifirda:\\n                # ⚠ HAKEM AGIRLIKLARDIR (K-61).',
     '            if False:\\n                # ⚠ HAKEM AGIRLIKLARDIR (K-61).',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-18: sert kesimde de alanlar geri acilsin',
     '            if not sifirda:\\n                # ⚠ HAKEM AGIRLIKLARDIR (K-61).',
     '            if True:\\n                # ⚠ HAKEM AGIRLIKLARDIR (K-61).',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-18: geri acma yerine ipucu silinsin (fazla mesaisiz plan kaybolsun)',
     '                _fazla_mesaiyi_serbest_birak(kuruldu, fm_eski)\\n            if not bulundu:',
     '                _fazla_mesaiyi_serbest_birak(kuruldu, fm_eski)\\n                kuruldu.m.ClearHints()\\n            if not bulundu:',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'bulunamayinca not dusulmesin (sessiz geri donus)',
     '            if not bulundu:\\n                kuruldu.notlar.append(',
     '            if False:\\n                kuruldu.notlar.append(',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'bulununca da not dusulsun',
     '            if not bulundu:\\n                kuruldu.notlar.append(',
     '            if True:\\n                kuruldu.notlar.append(',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'not "en aza indirilir" diye kanit iddia etsin',
     '                    "(agirlikli arama azaltmaya calisir; en azi oldugu kanitli degildir)"',
     '                    "(yumusak cezayla en aza indirilir)"',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'bulunamayinca yeniden aranmasin',
     '                durum, c = _gecerli_plan_yeniden_ara(kuruldu, ayar, basladi)',
     '                pass',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'plan yokken de "bulundu" densin',
     '            bulundu = durum in (cp_model.OPTIMAL, cp_model.FEASIBLE)',
     '            bulundu = True',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'sure yetmemesi de kanit sayilsin',
     '                "kanitlandi_yok": durum == cp_model.INFEASIBLE,',
     '                "kanitlandi_yok": not bulundu,',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'not hep "kanitlandi" desin',
     '                       if durum == cp_model.INFEASIBLE\\n                       else "bu surede bulunamadi"))',
     '                       if True\\n                       else "bu surede bulunamadi"))',
     'testler/test_fazla_mesai_once_sifir.py'),
'''
# kaldirilacak eski kayitlar (b'den sonra, artik capasi olmayan ya da yeniyle cakisanlar)
s2 = s[:a] + yeni + s[b:]
for old in (
'''    ('fm_sifir', C, 'bulunamayinca alanlar geri acilmasin (K-38 yolu kapansin)',
     '                _fazla_mesaiyi_serbest_birak(kuruldu, fm_eski)\\n',
     '',
     'testler/test_fazla_mesai_once_sifir.py'),
''',
'''    ('fm_sifir', C, 'bulunamayinca yeniden aranmasin',
     '                durum, c = _gecerli_plan_yeniden_ara(kuruldu, ayar, basladi)',
     '                pass',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'plan yokken de "bulundu" densin',
     '            bulundu = durum in (cp_model.OPTIMAL, cp_model.FEASIBLE)',
     '            bulundu = True',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'bulununca alanlar geri acilsin (0 da kalmasin)',
     '                "molalar_sabit": mola_sabit}\\n',
     '                "molalar_sabit": mola_sabit}\\n            if bulundu:\\n                _fazla_mesaiyi_serbest_birak(kuruldu, fm_eski)\\n',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'sure yetmemesi de kanit sayilsin',
     '                "kanitlandi_yok": durum == cp_model.INFEASIBLE,',
     '                "kanitlandi_yok": not bulundu,',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'not hep "kanitlandi" desin',
     '                       if durum == cp_model.INFEASIBLE\\n                       else "bu surede bulunamadi"))',
     '                       if True\\n                       else "bu surede bulunamadi"))',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'not dusulmesin (sessiz geri donus)',
     '                kuruldu.notlar.append(\\n                    "fazla mesaisiz plan %s; fazla mesai serbest birakildi "\\n                    "(yumusak cezayla en aza indirilir)"\\n                    % ("yok (%skanitlandi)" % ("molalar sabitken " if mola_sabit else "")\\n                       if durum == cp_model.INFEASIBLE\\n                       else "bu surede bulunamadi"))',
     '                pass',
     'testler/test_fazla_mesai_once_sifir.py'),
''',
'''    ('fm_sifir', C, 'kanitin kapsami ciktida hep "sabit" yazsin',
     '                "molalar_sabit": mola_sabit}',
     '                "molalar_sabit": True}',
     'testler/test_fazla_mesai_once_sifir.py'),
''',
'''    ('fm_sifir', C, 'O-16: fazla mesaisiz kosu tam model sayilsin',
     '    if (getattr(kuruldu, "fazla_mesai_once_sifir", None) or {}).get("bulundu"):\\n        return "fazla_mesaisiz"',
     '    if False:\\n        return "fazla_mesaisiz"',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-16: deneme basarisizken de kisitli sayilsin',
     '    if (getattr(kuruldu, "fazla_mesai_once_sifir", None) or {}).get("bulundu"):',
     '    if getattr(kuruldu, "fazla_mesai_once_sifir", None):',
     'testler/test_fazla_mesai_once_sifir.py'),
''',
):
    assert s2.count(old)==1, old[:80]
    s2=s2.replace(old,"")
# yeni O-16 / sinir kapsami kayitlari + mola sabit + egri/yuvarlama
ek='''    ('fm_sifir', C, 'kanitin kapsami ciktida hep "sabit" yazsin',
     '                "molalar_sabit": mola_sabit,\\n',
     '                "molalar_sabit": True,\\n',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-16: sert kesim tam model sayilsin',
     '    if (getattr(kuruldu, "fazla_mesai_once_sifir", None) or {}).get("sifirda_tutuldu"):\\n        return "fazla_mesaisiz"',
     '    if False:\\n        return "fazla_mesaisiz"',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-16/O-18: urun yolu (bulundu, alanlar acik) kisitli sayilsin',
     '    if (getattr(kuruldu, "fazla_mesai_once_sifir", None) or {}).get("sifirda_tutuldu"):',
     '    if (getattr(kuruldu, "fazla_mesai_once_sifir", None) or {}).get("bulundu"):',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'O-16: deneme yapildiysa hep kisitli sayilsin',
     '    if (getattr(kuruldu, "fazla_mesai_once_sifir", None) or {}).get("sifirda_tutuldu"):',
     '    if getattr(kuruldu, "fazla_mesai_once_sifir", None):',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'iyilestirme egrisi yazilmasin',
     '    bilgi["iyilesme"] = _iyilesme_ozeti(sayac.egri, nokta=24)',
     '    bilgi["iyilesme"] = None',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'iyilestirme egrisine nokta eklenmesin',
     '        self.egri.append((round(time.time() - self.basladi, 2),\\n                          self.ObjectiveValue(), self.BestObjectiveBound()))',
     '        pass',
     'testler/test_fazla_mesai_once_sifir.py'),
    ('fm_sifir', C, 'amac degeri yuvarlanmasin, kirpilsin',
     '        return int(round(cozucu.ObjectiveValue()))\\n    except Exception:',
     '        return int(cozucu.ObjectiveValue())\\n    except Exception:',
     'testler/test_fazla_mesai_once_sifir.py'),
'''
marker='''    ('fm_sifir', C, 'O-16: fazla mesaisiz siniri yazilmasin','''
assert s2.count(marker)==1
s2=s2.replace(marker, ek+marker)
io.open(p,"w",encoding="utf-8").write(s2)
import re
print("fm_sifir entries:", len(re.findall(r"\('fm_sifir'", s2)), "total:", len(re.findall(r"^\s*\('[a-z_0-9]+', [A-Z]+, ", s2, re.M)))
PYEOF
python3 - <<'PYEOF'
# capa denetimi: her fm_sifir kaydinin capasi coz.py'de tam bir kez gecmeli
import io,re,sys
sys.path.insert(0,"/tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/09-motor")
import importlib.util
spec=importlib.util.spec_from_file_location("m","/tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/09-motor/mutasyon_kostur.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
import os
kok="/tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/09-motor"
bad=0; n=0
for grup,dosya,ad,eski,yeni,test in m.MUTASYONLAR:
    n+=1
    src=io.open(os.path.join(kok,dosya),encoding="utf-8").read()
    c=src.count(eski)
    if c!=1:
        bad+=1; print("CAPA %d kez: [%s] %s" % (c,grup,ad))
print("toplam",n,"bozuk",bad)
PYEOF