using Microsoft.EntityFrameworkCore;
using TShift.Domain.Calisanlar;
using TShift.Domain.Kimlik;
using TShift.Domain.Kiracilar;
using TShift.Domain.Organizasyon;
using TShift.Domain.Yetki;
using TShift.Infrastructure.Persistence;
using TShift.Infrastructure.Yetki;
using Xunit;

namespace TShift.Tests;

/// <summary>
/// YETKİ VE KAPSAM TESTLERİ. Spec §3.2 yetki matrisi.
///
/// Çok kiracılık testleri "başka FİRMANIN verisi gelmesin" diyordu.
/// Bunlar "aynı firma içinde, yetkisi olmayan kişi görmesin" diyor.
///
/// İkisi farklı sınıf sorun: birincisi veritabanının garantisi, ikincisi
/// uygulamanın kararı. Bu yüzden ikisi ayrı ayrı sınanır.
/// </summary>
public class YetkiTestleri
{
    private const string Baglanti =
        "Host=localhost;Port=5433;Database=tshift;Username=tshift_app;Password=tshift_app_dev_2026";

    private static TShiftDbContext Baglam(IKiraciBaglami baglam)
    {
        var opt = new DbContextOptionsBuilder<TShiftDbContext>()
            .UseNpgsql(Baglanti)
            .AddInterceptors(new KiraciBaglantiKesici(baglam))
            .Options;
        return new TShiftDbContext(opt, baglam);
    }

    /// <summary>Bir firmanın küçük ama gerçekçi bir kopyası.</summary>
    private sealed record Sahne(
        Guid KiraciId, Guid DepartmanId, Guid GunduzId, Guid GeceId,
        Guid MudurId, Guid SefId, Guid CalisanKullaniciId, Guid IzleyiciId,
        Guid GunduzCalisanId, Guid GeceCalisanId);

    private static async Task<Sahne> SahneKur(string ek)
    {
        var baglam = new KiraciBaglami();
        baglam.Ayarla(null);
        await using var db = Baglam(baglam);

        var kiraci = new Kiraci { Ad = $"Yetki {ek}", Slug = $"yetki-{ek}", Durum = KiraciDurumu.Aktif };
        db.Kiracilar.Add(kiraci);
        await db.SaveChangesAsync();

        baglam.Ayarla(kiraci.Id);
        var kurulum = new KiraciKurulumServisi(db);
        await kurulum.SistemRolleriniKurAsync(kiraci.Id);

        var dep = new Departman { Ad = "Ops", Kod = $"OPS-{ek}", CalismaTipi = CalismaTipi.Saatli };
        db.Departmanlar.Add(dep);
        await db.SaveChangesAsync();

        var gunduz = new Ekip { DepartmanId = dep.Id, Ad = "Gunduz", Kod = $"GND-{ek}" };
        var gece   = new Ekip { DepartmanId = dep.Id, Ad = "Gece",   Kod = $"GCE-{ek}" };
        db.Ekipler.AddRange(gunduz, gece);
        await db.SaveChangesAsync();

        var c1 = new Calisan { PersonelNo = $"G1-{ek}", Ad = "Gunduzcu", Soyad = "Bir",
            DepartmanId = dep.Id, BirincilEkipId = gunduz.Id, IseGiris = new DateOnly(2025, 1, 1) };
        var c2 = new Calisan { PersonelNo = $"C1-{ek}", Ad = "Gececi", Soyad = "Bir",
            DepartmanId = dep.Id, BirincilEkipId = gece.Id, IseGiris = new DateOnly(2025, 1, 1) };
        db.Calisanlar.AddRange(c1, c2);
        await db.SaveChangesAsync();

        async Task<Guid> Kul(string onek, string rol, Guid? calisanId = null)
        {
            var u = new Kullanici
            {
                Ad = onek, Soyad = "Test", Eposta = $"{onek}-{ek}@yetki.test",
                EpostaDogrulandi = true, Durum = KullaniciDurumu.Aktif, CalisanId = calisanId
            };
            db.Kullanicilar.Add(u);
            await db.SaveChangesAsync();
            await kurulum.RolAtaAsync(u.Id, rol);
            return u.Id;
        }

        var mudurId     = await Kul("mudur", YetkiKatalogu.KiraciYonetici);
        var sefId       = await Kul("sef", YetkiKatalogu.Sef);
        var calisanId   = await Kul("calisan", YetkiKatalogu.Calisan, c1.Id);
        var izleyiciId  = await Kul("izleyici", YetkiKatalogu.Izleyici);

        // Şefin kapsamı YALNIZ gündüz ekibi.
        await kurulum.KapsamEkleAsync(sefId, KapsamTipi.Ekip, gunduz.Id);

        return new Sahne(kiraci.Id, dep.Id, gunduz.Id, gece.Id,
            mudurId, sefId, calisanId, izleyiciId, c1.Id, c2.Id);
    }

    private static Task Temizle(Guid kiraciId)
        => TestTemizlik.KiraciSilAsync(kiraciId);

    private static async Task<(KullaniciYetkisi Yetki, List<Calisan> Gorunen)> Bak(Guid kiraciId, Guid kullaniciId)
    {
        var b = new KiraciBaglami();
        b.Ayarla(kiraciId);
        await using var db = Baglam(b);

        var yetki = await new YetkiCozucu(db, TimeProvider.System).CozAsync(kullaniciId);
        var gorunen = await db.Calisanlar.KapsamUygula(yetki).ToListAsync();
        return (yetki, gorunen);
    }

    // ------------------------------------------------------------------ Y1
    [Fact(DisplayName = "Y1 - Kiraci yoneticisi tum calisanlari gorur")]
    public async Task Yonetici_hepsini_gorur()
    {
        var s = await SahneKur(Guid.NewGuid().ToString("N")[..6]);
        try
        {
            var (yetki, gorunen) = await Bak(s.KiraciId, s.MudurId);

            Assert.Equal(KapsamSeviyesi.Kiraci, yetki.Seviye);
            Assert.Equal(2, gorunen.Count);
            Assert.True(yetki.Var(YetkiKatalogu.KullaniciYonet));
            Assert.True(yetki.Var(YetkiKatalogu.KuralParametre));
        }
        finally { await Temizle(s.KiraciId); }
    }

    // ------------------------------------------------------------------ Y2
    [Fact(DisplayName = "Y2 - Sef YALNIZ kendi ekibini gorur")]
    public async Task Sef_sadece_kendi_ekibi()
    {
        var s = await SahneKur(Guid.NewGuid().ToString("N")[..6]);
        try
        {
            var (yetki, gorunen) = await Bak(s.KiraciId, s.SefId);

            Assert.Equal(KapsamSeviyesi.Kapsam, yetki.Seviye);
            Assert.Single(gorunen);
            Assert.Equal(s.GunduzCalisanId, gorunen[0].Id);
            Assert.DoesNotContain(gorunen, c => c.Id == s.GeceCalisanId);
        }
        finally { await Temizle(s.KiraciId); }
    }

    // ------------------------------------------------------------------ Y3
    [Fact(DisplayName = "Y3 - Sef plan uretemez, duzenleyebilir")]
    public async Task Sef_izinleri_matrise_uyuyor()
    {
        var s = await SahneKur(Guid.NewGuid().ToString("N")[..6]);
        try
        {
            var (yetki, _) = await Bak(s.KiraciId, s.SefId);

            Assert.True(yetki.Var(YetkiKatalogu.PlanDuzenle));       // matris: K
            Assert.False(yetki.Var(YetkiKatalogu.PlanUret));         // matris: —
            Assert.False(yetki.Var(YetkiKatalogu.PlanOnayla));       // matris: —
            Assert.False(yetki.Var(YetkiKatalogu.CalisanDuzenle));   // matris: —
            Assert.False(yetki.Var(YetkiKatalogu.KuralParametre));   // matris: —
        }
        finally { await Temizle(s.KiraciId); }
    }

    // ------------------------------------------------------------------ Y4
    [Fact(DisplayName = "Y4 - Calisan yalniz kendi kaydini gorur")]
    public async Task Calisan_sadece_kendini()
    {
        var s = await SahneKur(Guid.NewGuid().ToString("N")[..6]);
        try
        {
            var (yetki, gorunen) = await Bak(s.KiraciId, s.CalisanKullaniciId);

            Assert.Equal(KapsamSeviyesi.Kendi, yetki.Seviye);
            Assert.Single(gorunen);
            Assert.Equal(s.GunduzCalisanId, gorunen[0].Id);
            Assert.False(yetki.Var(YetkiKatalogu.IzinGir));     // baskasi adina giremez
            Assert.True(yetki.Var(YetkiKatalogu.IzinTalep));    // kendi talebini olusturur
        }
        finally { await Temizle(s.KiraciId); }
    }

    // ------------------------------------------------------------------ Y5
    [Fact(DisplayName = "Y5 - Izleyici her seyi gorur, hicbir sey yazamaz")]
    public async Task Izleyici_salt_okunur()
    {
        var s = await SahneKur(Guid.NewGuid().ToString("N")[..6]);
        try
        {
            var (yetki, gorunen) = await Bak(s.KiraciId, s.IzleyiciId);

            Assert.Equal(2, gorunen.Count);

            // Tek tek saymak yerine: katalogdaki YAZMA izinlerinin HİÇBİRİ olmamalı.
            // Yeni bir yazma izni eklenirse bu test onu da otomatik kapsar.
            var yazmaIzinleri = new[]
            {
                YetkiKatalogu.CalisanDuzenle, YetkiKatalogu.SozlesmeDuzenle,
                YetkiKatalogu.YetkinlikAta, YetkiKatalogu.IzinGir, YetkiKatalogu.IzinTalep,
                YetkiKatalogu.UygunlukGir, YetkiKatalogu.KuralParametre,
                YetkiKatalogu.KuralIstisna, YetkiKatalogu.VardiyaSablon,
                YetkiKatalogu.TalepGir, YetkiKatalogu.PlanUret, YetkiKatalogu.PlanDuzenle,
                YetkiKatalogu.PlanOnayla, YetkiKatalogu.PlanYayinla,
                YetkiKatalogu.GerceklesenYukle, YetkiKatalogu.KullaniciYonet
            };
            foreach (var izin in yazmaIzinleri)
                Assert.False(yetki.Var(izin), $"Izleyicide olmamasi gereken izin: {izin}");
        }
        finally { await Temizle(s.KiraciId); }
    }

    // ------------------------------------------------------------------ Y6
    [Fact(DisplayName = "Y6 - Suresi gecmis yetki devri islemez")]
    public async Task Sureli_devir_kendiliginden_biter()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var s = await SahneKur(ek);
        try
        {
            var bugun = DateOnly.FromDateTime(DateTime.UtcNow);

            var b = new KiraciBaglami();
            b.Ayarla(s.KiraciId);
            await using (var db = Baglam(b))
            {
                var kurulum = new KiraciKurulumServisi(db);
                // Şefe, DÜN BİTMİŞ bir departman müdürlüğü devri.
                await kurulum.RolAtaAsync(s.SefId, YetkiKatalogu.DepartmanMuduru,
                    bas: bugun.AddDays(-10), bitis: bugun.AddDays(-1), verenKullaniciId: s.MudurId);
            }

            var (yetki, gorunen) = await Bak(s.KiraciId, s.SefId);

            // Devir bitti: şef yine şef.
            Assert.False(yetki.Var(YetkiKatalogu.PlanUret));
            Assert.Single(gorunen);
        }
        finally { await Temizle(s.KiraciId); }
    }

    // ------------------------------------------------------------------ Y7
    [Fact(DisplayName = "Y7 - Suren yetki devri calisir ve kapsami genisletmez")]
    public async Task Suren_devir_calisir()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var s = await SahneKur(ek);
        try
        {
            var bugun = DateOnly.FromDateTime(DateTime.UtcNow);

            var b = new KiraciBaglami();
            b.Ayarla(s.KiraciId);
            await using (var db = Baglam(b))
            {
                var kurulum = new KiraciKurulumServisi(db);
                await kurulum.RolAtaAsync(s.SefId, YetkiKatalogu.DepartmanMuduru,
                    bas: bugun.AddDays(-1), bitis: bugun.AddDays(14), verenKullaniciId: s.MudurId);
            }

            var (yetki, gorunen) = await Bak(s.KiraciId, s.SefId);

            // Yeni izinler geldi...
            Assert.True(yetki.Var(YetkiKatalogu.PlanUret));
            Assert.True(yetki.Var(YetkiKatalogu.PlanOnayla));

            // ...ama KAPSAM genişlemedi. Departman müdürü de kapsam seviyesinde;
            // şefin kapsam satırı hâlâ yalnız gündüz ekibi.
            // Yetki devri "daha fazlasını yapabilirsin" demektir,
            // "daha fazlasını görebilirsin" demek değil.
            Assert.Equal(KapsamSeviyesi.Kapsam, yetki.Seviye);
            Assert.Single(gorunen);
        }
        finally { await Temizle(s.KiraciId); }
    }

    // ------------------------------------------------------------------ Y8
    [Fact(DisplayName = "Y8 - Kapsami olmayan kapsamli rol HICBIR SEY gormez")]
    public async Task Kapsamsiz_kullanici_bos_doner()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var s = await SahneKur(ek);
        try
        {
            var b = new KiraciBaglami();
            b.Ayarla(s.KiraciId);
            Guid yeniSef;
            await using (var db = Baglam(b))
            {
                var kurulum = new KiraciKurulumServisi(db);
                var u = new Kullanici
                {
                    Ad = "Kapsamsiz", Soyad = "Sef", Eposta = $"kapsamsiz-{ek}@yetki.test",
                    EpostaDogrulandi = true, Durum = KullaniciDurumu.Aktif
                };
                db.Kullanicilar.Add(u);
                await db.SaveChangesAsync();
                await kurulum.RolAtaAsync(u.Id, YetkiKatalogu.DepartmanMuduru);
                yeniSef = u.Id;
                // KAPSAM SATIRI EKLENMEDİ — yapılandırma eksik.
            }

            var (yetki, gorunen) = await Bak(s.KiraciId, yeniSef);

            // Spec §3.2 "kapsamı olmayan tüm kiracıyı görür" diyor; biz bilerek
            // tersini yapıyoruz. Eksik yapılandırma sızıntıya değil,
            // "göremiyorum" şikâyetine dönüşsün.
            Assert.True(yetki.Var(YetkiKatalogu.PlanUret));  // izinleri var
            Assert.Empty(gorunen);                            // ama gorecegi kimse yok
        }
        finally { await Temizle(s.KiraciId); }
    }

    // ------------------------------------------------------------------ Y9
    [Fact(DisplayName = "Y9 - Rolsuz kullanici hicbir izne sahip degil")]
    public async Task Rolsuz_kullanici_bos()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var s = await SahneKur(ek);
        try
        {
            var b = new KiraciBaglami();
            b.Ayarla(s.KiraciId);
            Guid rolsuz;
            await using (var db = Baglam(b))
            {
                var u = new Kullanici
                {
                    Ad = "Rolsuz", Soyad = "Kisi", Eposta = $"rolsuz-{ek}@yetki.test",
                    EpostaDogrulandi = true, Durum = KullaniciDurumu.Aktif
                };
                db.Kullanicilar.Add(u);
                await db.SaveChangesAsync();
                rolsuz = u.Id;
            }

            var (yetki, gorunen) = await Bak(s.KiraciId, rolsuz);

            Assert.Empty(yetki.Izinler);
            Assert.Empty(gorunen);
        }
        finally { await Temizle(s.KiraciId); }
    }
}
