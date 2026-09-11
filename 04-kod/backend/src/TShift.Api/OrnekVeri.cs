using TShift.Domain.Calisanlar;
using TShift.Domain.Kimlik;
using TShift.Domain.Kiracilar;
using TShift.Domain.Organizasyon;
using TShift.Domain.Yetki;
using TShift.Infrastructure.Kimlik;
using TShift.Infrastructure.Persistence;
using TShift.Infrastructure.Yetki;

namespace TShift.Api;

/// <summary>
/// Geliştirme ve inceleme için örnek veri: iki firma, departman, iki ekip,
/// çalışanlar ve firma başına dört farklı roldeki kullanıcı.
///
/// TEK YERDE DURUYOR, çünkü iki yerden çağrılıyor: `POST /dev/seed` ucundan ve
/// kutu içi kurulumdan. İki kopya olsaydı biri güncellenir, diğeri unutulurdu —
/// ve "benim makinemde farklı veri var" diye yarım gün kaybedilirdi.
///
/// Amaç yalnız veri doldurmak değil: dört rolün AYNI ekranda farklı davrandığını
/// gösterebilmek. Bu yüzden iki ayrı ekip var ve şefin kapsamı yalnız birine bağlı.
/// </summary>
public static class OrnekVeri
{
    public const string Parola = "TShift2026!Deneme";

    public static async Task<List<object>> KurAsync(IServiceProvider saglayici)
    {
        var db = saglayici.GetRequiredService<TShiftDbContext>();
        var baglam = saglayici.GetRequiredService<IKiraciBaglami>();
        var parolalar = saglayici.GetRequiredService<IParolaServisi>();
        var kurulum = saglayici.GetRequiredService<IKiraciKurulumServisi>();


        var sonuc = new List<object>();

        foreach (var (ad, slug, sektor, birim) in new[]
        {
            ("Anadolu Çağrı Merkezi", "anadolu-cm", "cagri_merkezi", "Departman"),
            ("Marmara Perakende", "marmara-perakende", "perakende", "Şube"),
        })
        {
            // Kiracı kaydının kendisi kiracıya ait değildir; bağlamı boşaltarak yazıyoruz.
            baglam.Ayarla(null);
            var kiraci = new Kiraci { Ad = ad, Slug = slug, SektorPaketi = sektor, BirimAdi = birim, Durum = KiraciDurumu.Aktif };
            db.Kiracilar.Add(kiraci);
            await db.SaveChangesAsync();

            // Bundan sonrası o kiracının bağlamında.
            baglam.Ayarla(kiraci.Id);

            // Sistem rolleri her yeni kiracıya kurulur.
            await kurulum.SistemRolleriniKurAsync(kiraci.Id);

            var dep = new Departman
            {
                Ad = birim == "Şube" ? "Kadıköy Şubesi" : "Çağrı Merkezi Operasyon",
                Kod = "OPS", CalismaTipi = CalismaTipi.Saatli, AcilisSaat = 8m, KapanisSaat = 24m
            };
            db.Departmanlar.Add(dep);
            await db.SaveChangesAsync();

            // İKİ ekip: kapsam sınırının gerçekten iş gördüğünü görebilmek için.
            var gunduz = new Ekip { DepartmanId = dep.Id, Ad = "Gündüz Ekibi", Kod = "GND" };
            var gece   = new Ekip { DepartmanId = dep.Id, Ad = "Akşam Ekibi",  Kod = "AKS" };
            db.Ekipler.AddRange(gunduz, gece);
            await db.SaveChangesAsync();

            var kisiler = slug == "anadolu-cm"
                ? new[] { ("A4101", "Mert", "Kaya", gunduz.Id), ("A4102", "Selin", "Arslan", gunduz.Id),
                          ("A4103", "Burak", "Demir", gece.Id) }
                : new[] { ("P7001", "Ayşe", "Yıldız", gunduz.Id), ("P7002", "Emre", "Doğan", gece.Id) };

            var calisanlar = new List<Calisan>();
            foreach (var (no, cad, csoyad, ekipId) in kisiler)
            {
                var c = new Calisan
                {
                    PersonelNo = no, Ad = cad, Soyad = csoyad,
                    DepartmanId = dep.Id, BirincilEkipId = ekipId,
                    IseGiris = new DateOnly(2024, 1, 15), Durum = CalisanDurumu.Aktif
                };
                db.Calisanlar.Add(c);
                await db.SaveChangesAsync();
                calisanlar.Add(c);

                db.CalisanSozlesmeleri.Add(new CalisanSozlesmesi
                {
                    CalisanId = c.Id, Tip = SozlesmeTipi.TamZamanli,
                    HaftalikSaat = 45m, Baslangic = new DateOnly(2024, 1, 15), Aktif = true
                });
            }
            await db.SaveChangesAsync();

            // Dört farklı roldeki kullanıcı — yetki farkını gözle görmek için.
            async Task<Kullanici> KullaniciKur(string kad, string ksoyad, string onek,
                                                string rolKodu, Guid? calisanId = null)
            {
                var u = new Kullanici
                {
                    Ad = kad, Soyad = ksoyad, Eposta = $"{onek}@{slug}.test",
                    EpostaDogrulandi = true, Durum = KullaniciDurumu.Aktif,
                    CalisanId = calisanId
                };
                db.Kullanicilar.Add(u);
                await db.SaveChangesAsync();

                db.KullaniciKimlikBilgileri.Add(new KullaniciKimlikBilgisi
                {
                    KullaniciId = u.Id,
                    SifreHash = parolalar.Ozetle(Parola)
                });
                await db.SaveChangesAsync();

                await kurulum.RolAtaAsync(u.Id, rolKodu);
                return u;
            }

            await KullaniciKur("Murat", "Kaya", "mudur", YetkiKatalogu.KiraciYonetici);

            // Şefin kapsamı YALNIZ gündüz ekibi.
            var sef = await KullaniciKur("Sema", "Toprak", "sef", YetkiKatalogu.Sef);
            await kurulum.KapsamEkleAsync(sef.Id, KapsamTipi.Ekip, gunduz.Id);

            // Çalışan kullanıcısı ilk çalışan kaydına bağlı.
            await KullaniciKur(calisanlar[0].Ad, calisanlar[0].Soyad, "calisan",
                               YetkiKatalogu.Calisan, calisanlar[0].Id);

            await KullaniciKur("Deniz", "Ak", "izleyici", YetkiKatalogu.Izleyici);

            sonuc.Add(new
            {
                kiraci = ad, firma = slug, id = kiraci.Id,
                calisan = kisiler.Length,
                kullanicilar = new[] { $"mudur@{slug}.test", $"sef@{slug}.test",
                                       $"calisan@{slug}.test", $"izleyici@{slug}.test" }
            });
        }

        baglam.Ayarla(null);
        return sonuc;
    }
}
