# -*- coding: utf-8 -*-
"""
TShift veri seti v1 -- DONUSTURUCU: tablolar (sartname #8) -> motor girdisi (#11.2)

Backend'in plan kosusu icin yapacagi isin REFERANS uygulamasi: bir plan
satirindan baslar, kapsamindaki departman / ekip / calisan / sablon / kural /
talep / gecmis satirlarini toplar ve motorun `/solve` girdisini kurar.
Yilmaz'in kuyruga koyacagi is mesaji bu ciktinin kendisidir.

Kurallar (her biri bir karar; kaynak parantezde):
  * Kapsam: planin departmani + butun alt departmanlari (hiyerarsi). Calisan
    `employees.department_id` ile kapsama girer; durumu ne olursa olsun
    gonderilir -- pasif / ayrilmis kisiyi AKTIF_CALISAN kurali dislar.
  * Sozlesme: plan haftasinin ilk gunu gecerli olan; yoksa en son baslayan.
    K-58: saat kisiden gelmez -- tam zamanli `haftalik_saat` 45 (kanun),
    `gun_sayisi` = `haftalik_gun`; yari zamanli yalniz tip.
  * Izin: plan haftasina dusen TUM GUN izinler, gun gun (K-31). Durum aynen
    gider (yalniz onayli baglar).
  * Uygunluk: haftalik satirlar aynen; tarihli satirlar plan haftasina
    dusen gunlere acilir.
  * Gecmis: plandan once yayinlanmis (`yayinda`) iki haftanin secili
    versiyonunun atamalari -> `gecmis_vardiyalar` (gun -14..-1; molalar ve
    sablonun gece isaretiyle) ve `gecmis_bilinen_gunler` (-14..-1; K-55:
    kaynak TShift'in kendi yayinlanmis plani).
  * Denge: `employee_balances` (plan ayi) -> `devir_yuk`,
    `yil_ici_fazla_mesai_saat`.
  * Kurallar: aktif `tenant_rules`; tur = gecersiz kilma ya da katalog;
    yasal / kabul edilebilir KATALOGDAN; satir bazli kuralin her
    gerekliligi ayri kural (bayrak satirdan). Planin `kural_degerleri`
    parametrelere birlestirilir (K-68).
  * Agirliklar: varsayilan profilin agirliklari (#5.4).
"""

import datetime as dt

GECMIS_HAFTA = 2


def _tarih(s):
    return dt.date.fromisoformat(s) if s else None


def _bos_degilse(d, anahtar, deger):
    if deger not in (None, [], {}):
        d[anahtar] = deger


def motor_girdisi(veri, plan_id=None):
    """`veri`: veri seti sozlugu (tablolar). `plan_id` verilmezse durumu
    `taslak` olan tek plan. Donen: motor girdisi (sozluk)."""
    T = {ad: satirlar for ad, satirlar in veri.items() if not ad.startswith("_")}
    by_id = {ad: {s["id"]: s for s in satirlar if "id" in s} for ad, satirlar in T.items()}

    if plan_id is None:
        adaylar = [p for p in T["plans"] if p["durum"] == "taslak"]
        assert len(adaylar) == 1, "taslak plan tek olmali (%d)" % len(adaylar)
        plan = adaylar[0]
    else:
        plan = by_id["plans"][plan_id]
    hafta = _tarih(plan["hafta_baslangic"])
    firma = T["tenants"][0]

    # ---- kapsam: departman + alt departmanlar
    kapsam = {plan["department_id"]}
    degisti = True
    while degisti:
        degisti = False
        for d in T["departments"]:
            if d["ust_department_id"] in kapsam and d["id"] not in kapsam:
                kapsam.add(d["id"])
                degisti = True
    ekipler = [t for t in T["teams"] if t["department_id"] in kapsam and t["aktif"]]
    ekip_kod = {t["id"]: t["kod"] for t in T["teams"]}
    ekip_ids = {t["id"] for t in ekipler}

    # ---- calisanlar
    soz = {}
    for s in T["employee_contracts"]:
        soz.setdefault(s["employee_id"], []).append(s)
    uyelik = {}
    for u in sorted(T["employee_teams"], key=lambda u: u["oncelik"]):
        uyelik.setdefault(u["employee_id"], []).append(u["team_id"])
    yet = {}
    yet_kod = {s["id"]: s["kod"] for s in T["skills"]}
    for y in T["employee_skills"]:
        if y.get("sertifika_bitis") and _tarih(y["sertifika_bitis"]) < hafta:
            continue
        yet.setdefault(y["employee_id"], []).append(yet_kod[y["skill_id"]])
    rol_kod = {r["id"]: r["kod"] for r in T["operational_roles"]}
    hafta_gunleri = [hafta + dt.timedelta(days=i) for i in range(7)]
    izin = {}
    for l in T["leaves"]:
        if not l["tum_gun"]:
            continue                                       # K-31
        for i, g in enumerate(hafta_gunleri):
            if _tarih(l["baslangic"]) <= g <= _tarih(l["bitis"]):
                izin.setdefault(l["employee_id"], []).append({"gun": i, "tip": l["tip"], "durum": l["durum"]})
    uyg = {}
    for a in T["employee_availability"]:
        satirlar = []
        if a["tekrar"] == "haftalik":
            satirlar.append(a["gun"])
        else:
            satirlar += [i for i, g in enumerate(hafta_gunleri)
                         if _tarih(a["baslangic_tarih"]) <= g <= _tarih(a["bitis_tarih"])]
        for gun in satirlar:
            uyg.setdefault(a["employee_id"], []).append(
                {"tip": a["tip"], "gun": gun, "bas": a["baslangic_saat"], "bit": a["bitis_saat"]})
    donem = hafta.strftime("%Y-%m")
    denge = {b["employee_id"]: b for b in T["employee_balances"] if b["donem"] == donem}

    # gecmis: plandan once yayinlanmis haftalar
    sablon = by_id["shift_templates"]
    molalar = {}
    for m in T["assignment_breaks"]:
        molalar.setdefault(m["assignment_id"], []).append(m)
    gecmis, bilinen = {}, set()
    for k in range(1, GECMIS_HAFTA + 1):
        h = (hafta - dt.timedelta(days=7 * k)).isoformat()
        p = [x for x in T["plans"] if x["hafta_baslangic"] == h and x["department_id"] == plan["department_id"]
             and x["durum"] == "yayinda" and x.get("secili_version_id")]
        if not p:
            continue
        bilinen |= {g - 7 * k for g in range(7)}
        surum = p[0]["secili_version_id"]
        for a in T["assignments"]:
            if a["plan_version_id"] != surum:
                continue
            kayit = {"gun": a["gun"] - 7 * k, "bas": a["baslangic_saat"], "bit": a["bitis_saat"]}
            t = sablon.get(a["shift_template_id"]) if a.get("shift_template_id") else None
            if t is not None and t.get("gece_vardiyasi") is not None:
                kayit["gece"] = t["gece_vardiyasi"]
            kayit["molalar"] = [{"bas": m["baslangic_saat"], "bit": m["bitis_saat"], "tip": m["tip"]}
                                for m in sorted(molalar.get(a["id"], []), key=lambda m: m["baslangic_saat"])]
            gecmis.setdefault(a["employee_id"], []).append(kayit)

    calisanlar = []
    for e in sorted((e for e in T["employees"] if e["department_id"] in kapsam), key=lambda e: e["personel_no"]):
        s = sorted(soz.get(e["id"], []), key=lambda s: s["baslangic"])
        gecerli = [x for x in s if _tarih(x["baslangic"]) <= hafta and (not x["bitis"] or _tarih(x["bitis"]) >= hafta)]
        sozlesme = (gecerli or s)[-1]
        if sozlesme["tip"] == "tam_zamanli":
            sz = {"tip": "tam_zamanli", "haftalik_saat": 45}
            if sozlesme.get("haftalik_gun"):
                sz["gun_sayisi"] = sozlesme["haftalik_gun"]
        else:
            sz = {"tip": sozlesme["tip"]}
        b = denge.get(e["id"]) or {}
        c = {"id": e["personel_no"],
             "ekipler": [ekip_kod[t] for t in uyelik.get(e["id"], []) if t in ekip_ids],
             "operasyonel_rol": rol_kod.get(e.get("operational_role_id")),
             "yetkinlikler": yet.get(e["id"], []),
             "sozlesme": sz,
             "izinler": izin.get(e["id"], []),
             "uygunluk": uyg.get(e["id"], []),
             "devir_yuk": {"gece": b.get("devir_gece", 0), "hafta_sonu": b.get("devir_hafta_sonu", 0),
                           "saat": b.get("devir_saat", 0), "cumartesi": b.get("devir_cumartesi", 0)},
             "gecmis_vardiyalar": sorted(gecmis.get(e["id"], []), key=lambda k: (k["gun"], k["bas"])),
             "yil_ici_fazla_mesai_saat": b.get("yil_ici_fazla_mesai_saat", 0)}
        if bilinen:
            c["gecmis_bilinen_gunler"] = sorted(bilinen)
        if e.get("gece_calisamaz"):
            c["gece_calisamaz"] = True
        if e["durum"] != "aktif":
            c["durum"] = e["durum"]
        calisanlar.append(c)

    # ---- sablonlar
    sablonlar = []
    for t in T["shift_templates"]:
        if not t["aktif"]:
            continue
        if t.get("team_id") and t["team_id"] not in ekip_ids:
            continue
        if not t.get("team_id") and t.get("department_id") and t["department_id"] not in kapsam:
            continue
        s = {"id": t["kod"], "bas": t["baslangic_saat"], "bit": t["bitis_saat"], "mola_dk": t["mola_dk"]}
        if t.get("team_id"):
            s["ekip"] = ekip_kod[t["team_id"]]
        _bos_degilse(s, "gece_vardiyasi", t.get("gece_vardiyasi"))
        if t.get("gece_vardiyasi") is False:
            s["gece_vardiyasi"] = False
        _bos_degilse(s, "mola_politikasi", t.get("mola_politikasi"))
        _bos_degilse(s, "gunler", t.get("gunler"))
        sablonlar.append(s)

    # ---- talep
    talep = [{"ekip": ekip_kod[h["team_id"]], "gun": h["gun"], "saat": h["saat"],
              "asgari": h["asgari_kisi"], "hedef": h["hedef_kisi"]}
             for h in T["demand_cells"]
             if h["demand_profile_id"] == plan.get("demand_profile_id") and h["team_id"] in ekip_ids]

    # ---- kurallar
    katalog = {k["kod"]: k for k in T["rule_types"]}
    plan_deger = plan.get("kural_degerleri") or {}
    kurallar = []
    for r in T["tenant_rules"]:
        if not r["aktif"]:
            continue
        kk = katalog[r["rule_type_kod"]]
        tur = r.get("tur_gecersiz_kilma") or kk["tur"]
        par = dict(r.get("parametreler") or {})
        par.update(plan_deger.get(r["rule_type_kod"]) or {})
        if kk["bayrak_satir_bazli"]:
            for sat in par.get("gereklilikler", []):
                sat = dict(sat)
                k = {"kod": kk["kod"], "tur": tur, "aktif": True, "yasal": bool(sat.pop("yasal", False))}
                kabul = sat.pop("kabul_edilebilir", None)
                if kabul is not None:
                    k["kabul_edilebilir"] = kabul
                k["parametreler"] = sat
                kurallar.append(k)
            continue
        k = {"kod": kk["kod"], "tur": tur, "aktif": True, "yasal": kk["yasal"]}
        if kk["kabul_edilebilir"] is not None:
            k["kabul_edilebilir"] = kk["kabul_edilebilir"]
        if par:
            k["parametreler"] = par
        kurallar.append(k)

    # ---- departmanlar (alt departmanlar; calisma saati olanlar)
    departmanlar = []
    for d in T["departments"]:
        if d["id"] not in kapsam or d.get("acik") is None:
            continue
        departmanlar.append({"id": d["kod"], "ad": d["ad"],
                             "ekipler": [t["kod"] for t in ekipler if t["department_id"] == d["id"]],
                             "acik": d["acik"]})

    profil = [p for p in T["plan_profiles"] if p["varsayilan_mi"]][0]
    kilitler = []
    for k in T["plan_locks"]:
        if k["plan_id"] != plan["id"]:
            continue
        x = {"calisan": by_id["employees"][k["employee_id"]]["personel_no"]}
        if k.get("team_id"):
            x["ekip"] = ekip_kod[k["team_id"]]
        x["gun"] = k["gun"]
        if k.get("baslangic_saat") is not None:
            x["bas"], x["bit"] = k["baslangic_saat"], k["bitis_saat"]
        if k["tip"] != "sabit":
            x["tip"] = k["tip"]                            # yasak: "buraya koyma"
        kilitler.append(x)

    return {
        "ad": "%s -- %s" % (firma["ad"], plan["hafta_baslangic"]),
        "surum": "2.0",
        "hafta_baslangic": plan["hafta_baslangic"],
        "sektor": firma.get("sektor"),
        "kiraci_saat_dilimi": firma["zaman_dilimi"],
        "profil": profil["kod"],
        "agirliklar": dict(profil["agirliklar"]),
        "cok_ekipli_sayim": firma.get("cok_ekipli_sayim", "hepsi"),
        "calisanlar": calisanlar,
        "vardiya_sablonlari": sablonlar,
        "talep": talep,
        "kurallar": kurallar,
        "departmanlar": departmanlar,
        "kilitler": kilitler,
        "donmus_gunler": [],
        "sabit_atamalar": [],
        "devir_kapsama": [],
        "denetim_disi_kabul": [],
    }


def yukle(yol):
    import io
    import json
    return json.load(io.open(yol, encoding="utf-8"))
