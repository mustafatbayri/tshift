cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/09-motor/cozucu && python3 - <<'EOF'
import io
p="coz.py"
s=io.open(p,encoding="utf-8").read()
old='''class _CozumSayaci(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.cozum_sayisi = 0

    def on_solution_callback(self):
        self.cozum_sayisi += 1
'''
new='''class _CozumSayaci(cp_model.CpSolverSolutionCallback):
    """Iyilestirme aramasinin sayaci ve EGRISI: her cozumde (saniye, amac,
    alt sinir). Egri 7 Ekim'de eklendi: iyilestirme butcenin %80'ini aliyor
    ve yalniz ilk/son amaci yaziliyordu -- plan hangi saniyede duzeldi,
    nerede duzlesti bilinmeden sure paylari olculemez (ana asamada ayni is
    `_ErkenDur.egri`)."""

    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.cozum_sayisi = 0
        self.basladi = time.time()
        self.egri = []

    def on_solution_callback(self):
        self.cozum_sayisi += 1
        self.egri.append((round(time.time() - self.basladi, 2),
                          self.ObjectiveValue(), self.BestObjectiveBound()))
'''
assert s.count(old)==1; s=s.replace(old,new)
old='''    bilgi["saniye"] = round(time.time() - t0, 2)
    bilgi["cozum_sayisi"] = sayac.cozum_sayisi
'''
new='''    bilgi["saniye"] = round(time.time() - t0, 2)
    bilgi["cozum_sayisi"] = sayac.cozum_sayisi
    # ⚠ O-16: egrideki sinirlar SABIT MOLALI modelindir, planin tamami icin
    #   kanit degil.
    bilgi["iyilesme"] = _iyilesme_ozeti(sayac.egri, nokta=24)
'''
assert s.count(old)==1; s=s.replace(old,new)
# amac degeri kirpma -> yuvarlama (inceleme bulgusu)
for old,new in (
 ('''        bilgi["iyilesmis_amac"] = int(c2.ObjectiveValue())''','''        bilgi["iyilesmis_amac"] = int(round(c2.ObjectiveValue()))'''),
 ('''            "amac_degeri": int(a["cozucu"].ObjectiveValue()) if planli else None,''','''            "amac_degeri": int(round(a["cozucu"].ObjectiveValue())) if planli else None,'''),
 ('''        return int(cozucu.ObjectiveValue())
    except Exception:''','''        return int(round(cozucu.ObjectiveValue()))
    except Exception:'''),
):
    assert s.count(old)==1,(old); s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
EOF
grep -n "ObjectiveValue()" coz.py | cut -c1-150