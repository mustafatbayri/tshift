# -*- coding: utf-8 -*-
"""D5 (0.1 ve 0.2 olcek): (i) amacsiz planin ve c2 planinin ceza SIKILIGI,
(ii) _ipucu_planini_al suresi (atamalar sabitken), (iii) 0.2 uctan uca: azami 20,
ana asama UNKNOWN (monkeypatch) -> K-63 plan + dogrulayici; (iv) 0.2 DOGAL kosu
azami 20 (bulgu 24 kendiliginden olusuyor mu?)."""
import json, sys, time
from ortak import *

OLCEK = float(sys.argv[1]) if len(sys.argv) > 1 else 0.1
AZAMI = float(sys.argv[2]) if len(sys.argv) > 2 else 20
MOD = sys.argv[3] if len(sys.argv) > 3 else "ipucu"      # ipucu | uctan | dogal

g = sahne(OLCEK)
k, kurma = kur(g)
print("olcek %.2f kisi %d kurma %.1fs %s" % (OLCEK, len(g["calisanlar"]), kurma, ozet(k)))
ayar = dict(C.VARSAYILAN, azami_saniye=AZAMI, isci_sayisi=2)


def ipucu_al(k):
    p = k.m.Proto()
    return dict(zip(p.solution_hint.vars, p.solution_hint.values))


def ipucu_amaci(k, h):
    return sum(a * h[v.Index()] for a, v in k.cezalar)


def sikilik(etiket, h):
    t0 = time.time()
    st, siki, cs = tam_amac(k, h)
    gevsek = {}
    for a, v in k.cezalar:
        d = h[v.Index()] - cs.Value(v)
        if d:
            onek = v.Name().split("_", 1)[0]
            gevsek[onek] = gevsek.get(onek, 0) + a * d
    print("  SIKILIK %-10s amac(ipucu)=%d siki=%s (%s, %.1fs) fark=%s gevsek=%s" % (
        etiket, ipucu_amaci(k, h), siki, st, time.time() - t0, ipucu_amaci(k, h) - (siki or 0), gevsek or "YOK"))
    sys.stdout.flush()


if MOD == "ipucu":
    kayit = []
    asil = C._tam_ipucu_yaz

    def kaydet(kuruldu, cozucu):
        asil(kuruldu, cozucu)
        kayit.append(ipucu_al(kuruldu))
    C._tam_ipucu_yaz = kaydet
    t0 = time.time()
    ok = C._ipucu_ver(k, ayar)
    C._tam_ipucu_yaz = asil
    iy = k.ilk_asama_iyilestirme or {}
    print("  _ipucu_ver=%s %.1fs | fm_once=%s | iyilestirme=%s" % (
        ok, time.time() - t0, {a: k.fazla_mesai_once_sifir.get(a) for a in ("bulundu", "saniye", "denemeler")} if k.fazla_mesai_once_sifir else None,
        {a: iy.get(a) for a in ("saniye", "plan_bulundu", "amacsiz_amac", "iyilesmis_amac", "optimum", "ipucu_korundu", "cozum_sayisi")}))
    print("  _tam_ipucu_yaz cagri sayisi:", len(kayit))
    sikilik("amacsiz", kayit[0])
    if len(kayit) > 1:
        sikilik("c2", kayit[-1])
    h = ipucu_al(k)
    print("  ipucu tam:", len(h) == len(k.m.Proto().variables))
    sabit = C._atamalari_sabitle(k)
    for i in range(3):
        b = C._ipucu_planini_al(k, ayar)
        sol = list(b["cozucu"].ResponseProto().solution) if b["bulundu"] else []
        farkli = sum(1 for ix, d in h.items() if sol and sol[ix] != d)
        print("  _ipucu_planini_al #%d: %s | cozum==ipucu farkli=%d | amac=%s" % (
            i + 1, {a: b[a] for a in ("bulundu", "saniye", "durum")}, farkli,
            round(b["cozucu"].ObjectiveValue()) if b["bulundu"] else None))
    # ayni is 2 isciyle ve sabitleme kapaliyken (kiyas): sure
    c = cp_model.CpSolver(); c.parameters.max_time_in_seconds = 30; c.parameters.num_search_workers = 2
    c.parameters.fix_variables_to_their_hinted_value = True
    t0 = time.time(); st = c.Solve(k.m); print("  kiyas: 2 isci sabitleme acik: %s %.2fs" % (c.StatusName(st), time.time() - t0))

elif MOD in ("uctan", "dogal"):
    if MOD == "uctan":
        C._durgunluk_bekcisiyle_coz = lambda cozucu, model, geri, ayar: cp_model.UNKNOWN
    t0 = time.time()
    c = C.coz(g, {"azami_saniye": AZAMI, "isci_sayisi": 2}, kuruldu=k)
    duvar = time.time() - t0
    ist = c["cozum_istatistikleri"]
    print("  durum=%s sebep=%s duvar=%.1fs ilk_asama=%s ana_butce=%s cozum_suresi=%s ipucu_plani=%s" % (
        c["durum"], ist["durma_sebebi"], duvar, ist["ilk_asama_sn"], ist["ana_asama_butce_sn"], ist["cozum_suresi_sn"], ist["ipucu_plani"]))
    print("  fm_once=%s" % ({a: ist["fazla_mesai_once_sifir"].get(a) for a in ("bulundu", "saniye", "denemeler")} if ist["fazla_mesai_once_sifir"] else None))
    iy = ist["ilk_asama_iyilestirme"] or {}
    print("  iyilestirme=%s" % {a: iy.get(a) for a in ("saniye", "plan_bulundu", "amacsiz_amac", "iyilesmis_amac", "cozum_sayisi", "ipucu_korundu")})
    print("  amac=%s alt_sinir=%s mola_adimi_alt_sinir=%s cozum_sayisi=%s ilk_cozum_sn=%s iyilesme=%s" % (
        ist["amac_degeri"], ist["alt_sinir"], ist["mola_adimi_alt_sinir"], ist["cozum_sayisi"], ist["ilk_cozum_sn"], ist["iyilesme"]))
    print("  notlar:", c["uygulanmayan_notlar"])
    if c["durum"] == "cozuldu":
        print("  metrikler:", {a: c["metrikler"][a] for a in ("fazla_mesai_saat", "asgari_kapsama_yuzde", "hedef_kapsama_yuzde", "optimuma_uzaklik_yuzde")})
        t0 = time.time()
        r = dogrulayici.degerlendir(g, c["atamalar"])
        print("  dogrulayici yayinlanabilir=%s (%.1fs) sert_ihlal=%s" % (r["yayin_kapisi"]["yayinlanabilir"], time.time() - t0, r["metrikler"].get("sert_ihlal")))
        if not r["yayin_kapisi"]["yayinlanabilir"]:
            print("  ihlaller:", r["ihlaller"][:5])
        h = ipucu_al(k)
        if len(h) == len(k.m.Proto().variables):
            sikilik("donen", h)
        json.dump(c, open("d5_%s_%.1f_%d.json" % (MOD, OLCEK, AZAMI), "w"), default=str)
