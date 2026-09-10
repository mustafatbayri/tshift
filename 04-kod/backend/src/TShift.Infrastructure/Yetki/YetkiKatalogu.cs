using TShift.Domain.Yetki;

namespace TShift.Infrastructure.Yetki;

/// <summary>
/// İzin kataloğu ve sistem rollerinin şablonu. Spec §3.2 yetki matrisinin
/// koddaki karşılığı.
///
/// Neden kodda: izin KODLARI sistemin sözlüğüdür — `plan.uret` diye bir izin
/// olup olmadığı ürün kararıdır, müşteri ayarı değil. Müşterinin
/// değiştirebildiği şey, hangi rolün hangi izne sahip olduğudur; o bilgi
/// veritabanında (role_permissions) durur ve kiracıya aittir.
///
/// Yeni bir izin eklerken: buraya kodu ekle, ilgili rollere dağıt, migration
/// çalıştır. Sistem rolleri her kiracı için buradan kurulur.
/// </summary>
public static class YetkiKatalogu
{
    // ---- İzin kodları -------------------------------------------------------
    public const string CalisanGor        = "calisan.gor";
    public const string CalisanDuzenle    = "calisan.duzenle";
    public const string SozlesmeDuzenle   = "sozlesme.duzenle";
    public const string YetkinlikAta      = "yetkinlik.ata";
    public const string IzinGir           = "izin.gir";
    public const string IzinTalep         = "izin.talep";
    public const string UygunlukGir       = "uygunluk.gir";
    public const string KuralParametre    = "kural.parametre";
    public const string KuralIstisna      = "kural.istisna";
    public const string VardiyaSablon     = "vardiya.sablon";
    public const string TalepGir          = "talep.gir";
    public const string PlanUret          = "plan.uret";
    public const string PlanDuzenle       = "plan.duzenle";
    public const string PlanOnayla        = "plan.onayla";
    public const string PlanYayinla       = "plan.yayinla";
    public const string GerceklesenYukle  = "gerceklesen.yukle";
    public const string RaporGor          = "rapor.gor";
    public const string KullaniciYonet    = "kullanici.yonet";

    public sealed record IzinTanimi(string Kod, string Aciklama, string Kategori);

    public static readonly IReadOnlyList<IzinTanimi> Izinler =
    [
        new(CalisanGor,       "Çalışan listesi ve detayını görür",        "Çalışan"),
        new(CalisanDuzenle,   "Çalışan ekler ve düzenler",               "Çalışan"),
        new(SozlesmeDuzenle,  "Sözleşme bilgisi düzenler",               "Çalışan"),
        new(YetkinlikAta,     "Çalışana yetkinlik atar",                 "Çalışan"),
        new(IzinGir,          "Başkası adına izin girer",                "İzin"),
        new(IzinTalep,        "Kendi izin talebini oluşturur",           "İzin"),
        new(UygunlukGir,      "Uygunluk kaydı girer",                    "İzin"),
        new(KuralParametre,   "Kural parametrelerini değiştirir",        "Kural"),
        new(KuralIstisna,     "Kural istisnası tanımlar",                "Kural"),
        new(VardiyaSablon,    "Vardiya şablonu tanımlar",                "Kural"),
        new(TalepGir,         "Talep ve kapasite verisi girer",          "Talep"),
        new(PlanUret,         "Plan üretir",                             "Plan"),
        new(PlanDuzenle,      "Plan düzenler",                           "Plan"),
        new(PlanOnayla,       "Planı onaylar",                           "Plan"),
        new(PlanYayinla,      "Planı yayınlar",                          "Plan"),
        new(GerceklesenYukle, "Gerçekleşen veri yükler",                 "Rapor"),
        new(RaporGor,         "Raporları görüntüler",                    "Rapor"),
        new(KullaniciYonet,   "Kullanıcı ve yetki yönetir",              "Yönetim")
    ];

    // ---- Sistem rolleri -----------------------------------------------------
    public const string KiraciYonetici  = "kiraci_yonetici";
    public const string DepartmanMuduru = "departman_muduru";
    public const string Sef             = "sef";
    public const string Calisan         = "calisan";
    public const string Izleyici        = "izleyici";

    public sealed record RolTanimi(string Kod, string Ad, KapsamSeviyesi Kapsam, string[] Izinler);

    /// <summary>Spec §3.2 matrisinin satır satır karşılığı.</summary>
    public static readonly IReadOnlyList<RolTanimi> Roller =
    [
        new(KiraciYonetici, "Kiracı yöneticisi", KapsamSeviyesi.Kiraci,
        [
            CalisanGor, CalisanDuzenle, SozlesmeDuzenle, YetkinlikAta,
            IzinGir, IzinTalep, UygunlukGir,
            KuralParametre, KuralIstisna, VardiyaSablon, TalepGir,
            PlanUret, PlanDuzenle, PlanOnayla, PlanYayinla,
            GerceklesenYukle, RaporGor, KullaniciYonet
        ]),

        new(DepartmanMuduru, "Departman müdürü", KapsamSeviyesi.Kapsam,
        [
            CalisanGor, CalisanDuzenle, SozlesmeDuzenle, YetkinlikAta,
            IzinGir, UygunlukGir,
            KuralIstisna, VardiyaSablon, TalepGir,
            PlanUret, PlanDuzenle, PlanOnayla, PlanYayinla,
            GerceklesenYukle, RaporGor
            // kural.parametre YOK: kural değerleri yalnız kiracı yöneticisinde.
            // kullanici.yonet YOK.
        ]),

        new(Sef, "Şef / takım lideri", KapsamSeviyesi.Kapsam,
        [
            CalisanGor, YetkinlikAta, IzinGir, UygunlukGir, TalepGir,
            PlanDuzenle, GerceklesenYukle, RaporGor
            // plan.uret / onayla / yayinla YOK: şef düzenler, onaya gönderir.
            // calisan.duzenle YOK: çalışan bilgisi görür, değiştiremez.
        ]),

        new(Calisan, "Çalışan", KapsamSeviyesi.Kendi,
        [
            CalisanGor, IzinTalep, UygunlukGir, RaporGor
            // Kapsam "Kendi" olduğu için bu izinler yalnız kendi kaydında işler.
        ]),

        new(Izleyici, "İzleyici", KapsamSeviyesi.Kiraci,
        [
            CalisanGor, RaporGor
            // Her şeyi görür, hiçbir şeyi değiştiremez. Yazma izni YOK.
        ])
    ];
}
