# -*- coding: utf-8 -*-
"""D4: K-63 ipucu -> plan cevirisi.
  (a) cozum ipucuyla BIREBIR mi (butun degiskenler)?
  (b) ipucu (iyilestirme sonrasi, c2) ceza degiskenlerinde SIKI mi? amac(ipucu) vs
      ayni x/mola icin en kucuk amac.
  (c) iyilestirme KAPALI / plansiz -> ipucu AMACSIZ plan: ceza degiskenleri
      gevsek mi? (K-63 bu durumda ne dondurur: amac_degeri, not metni)
  (d) gevsek ipucu kabul ediliyor mu (fm ipucusu sisirilince bulundu/amac)?"""
import sys, time
from ortak import *
from test_fazla_mesai_once_sifir import _sahne, _ornek_sahne, AYAR_URUN


def ipucu_al(k):
    p = k.m.Proto()
    return dict(zip(p.solution_hint.vars, p.solution_hint.values))


def ipucu_amaci(k, h):
    return sum(a * h[v.Index()] for a, v in k.cezalar)


def birebir(k, h, cozucu):
    sol = list(cozucu.ResponseProto().solution)
    farkli = [i for i, d in h.items() if sol[i] != d]
    return len(sol), len(h), farkli


def incele(ad, g, ayar, olcek_notu=""):
    print("\n== %s %s" % (ad, olcek_notu))
    k, _ = kur(g)
    ayar = dict(C.VARSAYILAN, **ayar)
    t0 = time.time()
    ok = C._ipucu_ver(k, ayar)
    print("  _ipucu_ver:", ok, "%.1fs" % (time.time() - t0), "| iyilestirme:",
          {a: (k.ilk_asama_iyilestirme or {}).get(a) for a in ("plan_bulundu", "amacsiz_amac", "iyilesmis_amac", "optimum", "ipucu_korundu")})
    h = ipucu_al(k)
    p = k.m.Proto()
    print("  ipucu tam mi:", len(h) == len(p.variables), "(%d/%d)" % (len(h), len(p.variables)))
    sabit = C._atamalari_sabitle(k)
    print("  atamalar sabitlendi:", sabit)
    b = C._ipucu_planini_al(k, ayar)
    print("  _ipucu_planini_al:", {a: b[a] for a in ("bulundu", "saniye", "durum")})
    if not b["bulundu"]:
        return
    n_sol, n_h, farkli = birebir(k, h, b["cozucu"])
    print("  (a) cozum == ipucu? farkli degisken sayisi:", len(farkli), "| amac(cozucu)=%d amac(ipucu)=%d bound=%s"
          % (round(b["cozucu"].ObjectiveValue()), ipucu_amaci(k, h), round(b["cozucu"].BestObjectiveBound())))
    st, siki, _ = tam_amac(k, h)
    print("  (b/c) ayni x/mola icin SIKI amac: %s %s | ipucu amaci %d | fark %s"
          % (st, siki, ipucu_amaci(k, h), (ipucu_amaci(k, h) - siki) if siki is not None else "?"))
    # ceza degiskeni bazinda gevseklik
    _, _, cs = tam_amac(k, h)
    gevsek = {}
    for a, v in k.cezalar:
        d = h[v.Index()] - cs.Value(v)
        if d:
            onek = v.Name().split("_", 1)[0]
            gevsek[onek] = gevsek.get(onek, 0) + a * d
    print("  gevsek ceza (kural: fazla puan):", gevsek or "YOK")
    return k, h, b


# (a)(b): urun yolu (iyilestirme acik)
r = incele("_ornek_sahne(2000) urun", _ornek_sahne({"HEDEF_KAPSAMA": 2000}), dict(AYAR_URUN))
r = incele("_sahne(5) urun", _sahne(gun=5), dict(AYAR_URUN))
# (c): iyilestirme KAPALI -> amacsiz plan ipucu
r = incele("_ornek_sahne(2000) iyilestirme KAPALI", _ornek_sahne({"HEDEF_KAPSAMA": 2000}), dict(AYAR_URUN, ilk_asama_iyilestirme_saniye=0))
r = incele("_sahne(5) iyilestirme KAPALI", _sahne(gun=5), dict(AYAR_URUN, ilk_asama_iyilestirme_saniye=0))
r = incele("_sahne(6) iyilestirme KAPALI", _sahne(gun=6), dict(AYAR_URUN, ilk_asama_iyilestirme_saniye=0))

# (d): gevsek ipucu kabul ediliyor mu?
print("\n== (d) gevsek ipucu: fm ipucusu sisirilir")
g = _sahne(gun=5)
k, _ = kur(g)
ayar = dict(C.VARSAYILAN, **AYAR_URUN)
C._ipucu_ver(k, ayar)
p = k.m.Proto()
h = ipucu_al(k)
fm = [v for _, v in k.cezalar if v.Name().startswith("fm_")]
v0 = fm[0]
ust = list(p.variables[v0.Index()].domain)[-1]
print("  fm[0] ipucu", h[v0.Index()], "alan ust", ust)
vals = list(p.solution_hint.values)
vars_ = list(p.solution_hint.vars)
vals[vars_.index(v0.Index())] = ust
p.solution_hint.values.clear(); p.solution_hint.values.extend(vals)
C._atamalari_sabitle(k)
b = C._ipucu_planini_al(k, ayar)
print("  sisirilmis ipucu ->", {a: b[a] for a in ("bulundu", "saniye", "durum")},
      "| amac(cozucu)=%s (dogru plan amaci %s)" % (round(b["cozucu"].ObjectiveValue()) if b["bulundu"] else None, ipucu_amaci(k, h)))

# (c') K-63 yolunda uctan uca: iyilestirme plansiz (UNKNOWN) + ana asama UNKNOWN
print("\n== (c') uctan uca: iyilestirme UNKNOWN + ana asama UNKNOWN -> K-63 ne dondurur?")
for ad, g in (("_sahne(5)", _sahne(gun=5)), ("_sahne(6)", _sahne(gun=6)), ("_ornek(2000)", _ornek_sahne({"HEDEF_KAPSAMA": 2000}))):
    k, _ = kur(g)
    asil_iy = C._iyilestirme_coz
    asil_ana = C._durgunluk_bekcisiyle_coz
    C._iyilestirme_coz = lambda model, saniye, isci: (cp_model.UNKNOWN, None, C._CozumSayaci())
    C._durgunluk_bekcisiyle_coz = lambda cozucu, model, geri, ayar: cp_model.UNKNOWN
    try:
        c = C.coz(g, dict(AYAR_URUN), kuruldu=k)
    finally:
        C._iyilestirme_coz = asil_iy
        C._durgunluk_bekcisiyle_coz = asil_ana
    ist = c["cozum_istatistikleri"]
    print("  %s durum=%s sebep=%s amac_degeri=%s fm_saat=%s dagilim=%s" % (
        ad, c["durum"], ist["durma_sebebi"], ist["amac_degeri"], c["metrikler"]["fazla_mesai_saat"],
        {kk: vv["deger"] for kk, vv in (ist["amac_dagilimi"] or {}).items()}))
    if c["durum"] == "cozuldu":
        h = ipucu_al(k)
        st, siki, _ = tam_amac(k, h)
        print("     ayni atamalarin SIKI amaci: %s | rapor edilen %s | iyilestirme: %s" % (siki, ist["amac_degeri"], {a: ist["ilk_asama_iyilestirme"].get(a) for a in ("plan_bulundu", "amacsiz_amac")}))
        print("     notlar:", [n for n in c["uygulanmayan_notlar"]])
        r = dogrulayici.degerlendir(g, c["atamalar"])
        print("     dogrulayici yayinlanabilir:", r["yayin_kapisi"]["yayinlanabilir"])
