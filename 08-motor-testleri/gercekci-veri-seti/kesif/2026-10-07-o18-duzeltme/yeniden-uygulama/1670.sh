cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/09-motor/cozucu && python3 - <<'PYEOF'
import io
p="coz.py"
s=io.open(p,encoding="utf-8").read()
R=[]
R.append(('''  1. gecerli plan   : molalar sablonun ideal yerinde SABIT, amac yok      (<= %20)
                      K-61 (6 Ekim): ONCE FAZLA MESAISIZ aranir; bulunursa
                      fazla mesai sonraki asamalarda da 0'da kalir, bulunamazsa
                      fazla mesai serbestken yeniden aranir. Hakem agirliklardir:
                      kisayol yalniz fazla mesainin kazanamayacagi agirliklarda
                      uygulanir (bkz. VARSAYILAN, `_fazla_mesai_kisayolu_gecerli`)
  2. iyilestirme    : molalar hala sabit, amac geri konur, atamalar iyilesir (%80, kalibrasyon)
''','''  1. gecerli plan   : molalar sablonun ideal yerinde SABIT, amac yok      (pay <= %20)
                      K-61 (6 Ekim): ONCE FAZLA MESAISIZ aranir (fazla mesai
                      degiskenleri [0,0]). Bulunursa o plan IPUCUDUR ve alanlar
                      GERI ACILIR -- hakem agirliklardir, fazla mesaili daha
                      iyi plan disarida kalmaz (7 Ekim duzeltmesi, O-18).
                      Bulunamazsa alanlar yine acilir, fazla mesai serbestken
                      bir kez daha aranir (en kotu halde iki pay: 2 x %20).
  2. iyilestirme    : molalar hala sabit, amac geri konur, atamalar iyilesir (%80, kalibrasyon);
                      ipucu 1'in plani -- fazla mesaisiz bulunduysa fazla
                      mesai yalniz agirliklara gore KAZANIYORSA eklenir
'''))
R.append(('''    # K-61 (6 Ekim, Mustafa: "Evet") -- "ONCE FAZLA MESAISIZ" URUNUN
    #   VARSAYILANI. Birinci asama gecerli plani fazla mesai degiskenleri
    #   [0,0]'a SABITKEN arar. Bulursa fazla mesai butun asamalarda 0'da kalir.
    #   NEDEN (olculdu; 500 kisi, 900 sn, ucer kosu, Mustafa'nin makinesi):''','''    # K-61 (6 Ekim, Mustafa: "Evet") -- "ONCE FAZLA MESAISIZ" URUNUN
    #   VARSAYILANI. Birinci asama gecerli plani fazla mesai degiskenleri
    #   [0,0]'a SABITKEN arar. Bulursa o plan iyilestirmenin IPUCUDUR; alanlar
    #   geri acilir ve kararı agirliklar verir (asagida "HAKEM AGIRLIKLARDIR").
    #   NEDEN (olculdu; 500 kisi, 900 sn, ucer kosu, Mustafa'nin makinesi):'''))
R.append(('''    #     bulgu 21 -- bu arama acikken alti kosunun altisinda fazla mesai 0;
    #       amac DENGELI 26.407-26.494, KAPSAMA 13.834-13.914; fazla mesai
    #       disindaki kalemler de iyilesti; kosudan kosuya fark %40 -> %0,3.
    #   Dayanak K-30 (Mustafa, 16 Eylul; "Zaten hedef hic gitmemek.
    #   Gidilecekse de minimum gitmek."), kararin tablosu:
    #     yalniz HEDEF kapsama iyilesecek        -> fazla mesai YAPILMAZ
    #     ASGARI (sert) fazla mesaisiz tutmuyor  -> YAPILIR, gereken kadar
    #   Bulamazsa (kanit ya da sure) alanlar GERI ACILIR, onceki yol aynen
    #   isler (ikinci satir: yumusak cezayla en aza indirilir; zorunlu fazla
    #   mesai yolu KAPANMAZ, K-38) ve not duser.
    #   ⚠ HAKEM AGIRLIKLARDIR (Mustafa, 6 Ekim 23:44): "...agirliklar baz
    #     alindiginda ornegin 3 saat fazla mesai iceren en optimum plan var
    #     ve fazla mesaisiz plandan oldukca daha optimum bir plan ise en
    #     optimum olani secmeliyiz." Bu arama bir KISAYOLDUR, kural degil:
    #     fazla mesaisiz plan varken fazla mesaili planlara BAKMAZ. Yalniz
    #     fazla mesainin agirliklara gore kazanamayacagi yerde uygulanir
    #     (`_fazla_mesai_kisayolu_gecerli`); agirliklar bunu bozuyorsa
    #     UYGULANMAZ, not duser, karari agirlikli arama verir.
    #   KAPSAM: yalniz iki asamali yol (`_ipucu_ver`). Esigin altindaki
    #   model ve baslangic plani verilen kosu (K-54, "Iyilestir") bu
    #   aramadan etkilenmez -- orada birinci asama yok.
    #   ⚠ "Bu surede bulunamadi" halinde donen plan fazla mesaili olabilir
    #   ve fazla mesaisizi VAR olabilir; not bunu soyler, sessiz kalmaz.
    #   ⚠ Fazla mesainin ZORUNLU oldugu veride (K-30'un ikinci satiri) bu
    #   arama bir sey kazandirmaz ve o durum tam olcekte OLCULMEDI (kesif,
    #   151 kisi, tek kosu: en az 3,5 saat zorunluyken 9,75-11,25 saat
    #   yazildi -- T-60 bulgu 22).
    #   False = 6 Ekim oncesinin davranisi (olcum ve kiyas icin).
    "fazla_mesai_once_sifir": True,
    "fazla_mesai_sifirda_tut": False,
}''','''    #     bulgu 21 -- SERT KESIMLE (bulununca 0'da tutularak) alti kosunun
    #       altisinda fazla mesai 0; amac DENGELI 26.407-26.494, KAPSAMA
    #       13.834-13.914 (toplam iyilesti; adalet ve hedef asimi cok az
    #       kotulesti); kosudan kosuya fark DENGELI %40 -> %0,3, KAPSAMA
    #       %26 -> %0,6.
    #   Dayanak K-30 (Mustafa, 16 Eylul; "Zaten hedef hic gitmemek.
    #   Gidilecekse de minimum gitmek."), kararin tablosu:
    #     yalniz HEDEF kapsama iyilesecek        -> fazla mesai YAPILMAZ
    #     ASGARI (sert) fazla mesaisiz tutmuyor  -> YAPILIR, gereken kadar
    #   Bulamazsa (kanit ya da sure) alanlar GERI ACILIR, onceki yol aynen
    #   isler (ikinci satir; zorunlu fazla mesai yolu KAPANMAZ, K-38) ve not
    #   duser. ⚠ O yolun "gereken kadar"i KANITLI DEGIL: agirlikli arama
    #   azaltmaya calisir (kesif, 151 kisi, tek kosu: en az 3,5 saat
    #   zorunluyken 9,75-11,25 saat yazildi -- T-60 bulgu 22; merdivenin 4.
    #   seviyesi olcecek).
    #   ⚠ HAKEM AGIRLIKLARDIR (Mustafa, 6 Ekim 23:44): "...agirliklar baz
    #     alindiginda ornegin 3 saat fazla mesai iceren en optimum plan var
    #     ve fazla mesaisiz plandan oldukca daha optimum bir plan ise en
    #     optimum olani secmeliyiz." Bu yuzden bulunan fazla mesaisiz plan
    #     yalniz BASLANGIC NOKTASIDIR: alanlar geri acilir, iyilestirme tam
    #     agirlikli amacla o plandan baslar. Fazla mesai ancak agirliklara
    #     gore kazaniyorsa plana girer; K-30'un ilk satirini agirliklar
    #     saglar (bir saat fazla mesai 3.000 puan, hedefin bir kisi-saat
    #     altinda kalmak 9/20/5).
    #   ⚠ O-18 (7 Ekim): 6 Ekim gecesi yazilan hal bulununca fazla mesaiyi
    #     BUTUN asamalarda 0'da tutuyordu ("sert kesim") ve "urun
    #     agirliklarinda fazla mesaili plan daha iyi olamaz" deniyordu. YANLIS:
    #     15 dakikalik bir fazla mesai adimi bir haftalik duzenin kilidini
    #     acabiliyor (kanitli optimum 750 iken sert kesim 2.256; 12 kiside
    #     9.000'e karsi 12.000 -- Mustafa'nin 3 saatlik ornegi; bagimsiz
    #     inceleme, test_fazla_mesai_once_sifir.py bolum 5). Sert kesim
    #     OLCUM secenegi olarak kaldi (`fazla_mesai_sifirda_tut`).
    #   KAPSAM: yalniz iki asamali yol (`_ipucu_ver`). Esigin altindaki
    #   model ve baslangic plani verilen kosu (K-54, "Iyilestir") bu
    #   aramadan etkilenmez -- orada birinci asama yok. (Kucuk model tek
    #   aramada agirliklarla ayni karari verir; "Iyilestir" fazla mesaili
    #   bir plandan basliyorsa onu azaltmak aramaya kalir -- olculmedi.)
    #   ⚠ "Bu surede bulunamadi" halinde donen plan fazla mesaili olabilir
    #   ve fazla mesaisizi VAR olabilir; not bunu soyler, sessiz kalmaz.
    #   ⚠ Duzeltilmis yol (alanlar acik) tam olcekte HENUZ OLCULMEDI; bulgu
    #   21 sert kesimin olcumudur. Olcum: kalite-olc.py `fm_once` /
    #   `fm_sert` / `fm_once_kapali` yapilandirmalari.
    #   False = 6 Ekim oncesinin davranisi (olcum ve kiyas icin).
    "fazla_mesai_once_sifir": True,
    # OLCUM: True = 6 Ekim gecesinin SERT KESIMI -- fazla mesaisiz plan
    #   bulununca fazla mesai degiskenleri sonraki asamalarda da [0,0]'da
    #   kalir; cozulen model tam model degildir (kuresel sinir yazilmaz,
    #   `_sinir_kapsami` "fazla_mesaisiz"). Urun yolunda KAPALI (O-18).
    #   Yalniz `fazla_mesai_once_sifir` acikken anlamlidir.
    "fazla_mesai_sifirda_tut": False,
}'''))
R.append(('''        #   kalan sure bugunku yolun en kotu haliyle AYNI (120 + 720).
                dusulecek = deneme''','''        #   kalan sure deneme yapilmamis gibi kalir (120 + 720).
                dusulecek = deneme'''))
R.append(('''      `dusulecek`: iyilestirmenin suresinden dusulen saniye -- "once fazla
      mesaisiz" denemesi BASARISIZ olduysa onun suresi (bkz. `_ipucu_ver`).
      Hem paydan hem acikca istenen sureden duser: mola adimina kalan sure
      deneme yapilmamis gibi kalir. Urunun varsayilan yolunda 0'dir.''','''      `dusulecek`: iyilestirmenin suresinden dusulen saniye -- "once fazla
      mesaisiz" denemesi BASARISIZ olduysa onun suresi (bkz. `_ipucu_ver`).
      Hem paydan hem acikca istenen sureden duser: mola adimina kalan sure
      deneme yapilmamis gibi kalir. Deneme plan bulduysa 0'dir (o arama
      birinci asamanin kendisidir).'''))
R.append(('''        # K-61 "once fazla mesaisiz". None = denenmedi (iki asama yok,
        # daraltilacak fazla mesai degiskeni yok ya da kapali). Sozluk:
        # `uygulandi` False ise agirlik kosulu tutmadi (`sebep: agirlik`);
        # True ise `bulundu` / `kanitlandi_yok` / `saniye` denemenin sonucu.''','''        # K-61 "once fazla mesaisiz". None = denenmedi (iki asama yok,
        # daraltilacak fazla mesai degiskeni yok ya da kapali). Sozluk:
        # `bulundu` / `kanitlandi_yok` / `saniye` denemenin sonucu;
        # `sifirda_tutuldu` yalniz olcum secenegiyle True (sert kesim).'''))
for old,new in R:
    assert s.count(old)==1, old[:70]
    s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
PYEOF
grep -n "kisayol\|KISAYOL\|uygulandi" coz.py | cut -c1-140; python3 -c "import ast,io;ast.parse(io.open('coz.py',encoding='utf-8').read());print('syntax ok')"