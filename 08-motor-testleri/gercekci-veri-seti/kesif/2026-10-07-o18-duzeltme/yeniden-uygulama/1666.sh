cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/09-motor && python3 - <<'PYEOF'
import io
p="testler/test_demir_secenekleri.py"
s=io.open(p,encoding="utf-8").read()
old='''def test_O16_sinir_kapsami_TAM_model_mi_kisitli_mi():
    """Ana asamanin cozdugu model tam model degilse sinir kuresel degildir.
    Iki kisit: atamalar sabit (mola adimi); fazla mesai degiskenleri 0'da
    (deneme plan BULDUYSA -- bulamadiysa alanlar geri acilmistir)."""
    class K(object):
        pass
    k = K()
    assert C._sinir_kapsami(False, k) is None                       # secenek hic kosmadi
    k.fazla_mesai_once_sifir = None
    assert C._sinir_kapsami(False, k) is None
    k.fazla_mesai_once_sifir = {"bulundu": False}
    assert C._sinir_kapsami(False, k) is None                       # alanlar geri acildi: tam model
    assert C._sinir_kapsami(True, k) == "mola_adimi"
    # K-61: agirlik kosulu tutmadiysa deneme hic yapilmaz, alanlara
    # dokunulmaz -- model tamdir.
    k.fazla_mesai_once_sifir = {"uygulandi": False, "sebep": "agirlik"}
    assert C._sinir_kapsami(False, k) is None
    k.fazla_mesai_once_sifir = {"bulundu": True}
    assert C._sinir_kapsami(False, k) == "fazla_mesaisiz"
    assert C._sinir_kapsami(True, k) == "mola_adimi"                # ikisi birden: mola adimi
    assert C._KANIT_SEBEPLERI == ("optimum", "hedef_bosluk")
'''
new='''def test_O16_sinir_kapsami_TAM_model_mi_kisitli_mi():
    """Ana asamanin cozdugu model tam model degilse sinir kuresel degildir.
    Iki kisit: atamalar sabit (mola adimi); fazla mesai degiskenleri 0'da
    TUTULMUSSA (yalniz olcum secenegi `fazla_mesai_sifirda_tut`; urun
    yolunda bulunan plan ipucudur, alanlar geri acilir -- 7 Ekim, O-18)."""
    class K(object):
        pass
    k = K()
    assert C._sinir_kapsami(False, k) is None                       # secenek hic kosmadi
    k.fazla_mesai_once_sifir = None
    assert C._sinir_kapsami(False, k) is None
    k.fazla_mesai_once_sifir = {"bulundu": False, "sifirda_tutuldu": False}
    assert C._sinir_kapsami(False, k) is None                       # alanlar geri acildi: tam model
    assert C._sinir_kapsami(True, k) == "mola_adimi"
    # URUN YOLU: bulundu ama 0'da tutulmadi -> alanlar acik, model tamdir.
    k.fazla_mesai_once_sifir = {"bulundu": True, "sifirda_tutuldu": False}
    assert C._sinir_kapsami(False, k) is None
    # SERT KESIM (olcum): 0'da tutuldu -> kisitli model.
    k.fazla_mesai_once_sifir = {"bulundu": True, "sifirda_tutuldu": True}
    assert C._sinir_kapsami(False, k) == "fazla_mesaisiz"
    assert C._sinir_kapsami(True, k) == "mola_adimi"                # ikisi birden: mola adimi
    assert C._KANIT_SEBEPLERI == ("optimum", "hedef_bosluk")
'''
assert s.count(old)==1; s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
PYEOF
sed -n 115,127p testler/test_demir_secenekleri.py