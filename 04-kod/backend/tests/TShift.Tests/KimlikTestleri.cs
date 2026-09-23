using Microsoft.EntityFrameworkCore;
using TShift.Domain.Kimlik;
using TShift.Domain.Kiracilar;
using TShift.Infrastructure.Kimlik;
using TShift.Infrastructure.Persistence;
using TShift.Infrastructure.Yetki;
using Xunit;

namespace TShift.Tests;

/// <summary>
/// KİMLİK KATMANI TESTLERİ.
///
/// Bu testler HTTP kullanmaz; doğrudan <see cref="KimlikServisi"/> ile konuşur.
/// Sebep: sınanmak istenen şey web çatısı değil, güvenlik kararlarının kendisi.
///
/// Sorulan sorular:
///   1. Doğru parola çalışıyor mu (temel)
///   2. Yanlış parola reddediliyor mu
///   3. Başka firmanın kullanıcısıyla giriş yapılabiliyor mu
///   4. Kaba kuvvet kilidi gerçekten kilitliyor mu
///   5. Yenileme jetonu dönüyor mu (eski jeton ölüyor mu)
///   6. Çalınmış jeton tespit edilip tüm oturumlar düşüyor mu
///   7. Parola veritabanında düz metin olarak durmuyor, değil mi
/// </summary>
public class KimlikTestleri
{
    // Testler de uygulama gibi kısıtlı rolle bağlanır — RLS geçerli olsun diye.
    private static readonly string Baglanti = TestAyarlari.UygulamaBaglantisi;   // T-34

    private const string DogruParola = "Deneme-Parolasi-2026!";

    private static readonly KimlikAyarlari Ayarlar = new()
    {
        ImzaAnahtari = "test-imza-anahtari-en-az-otuz-iki-bayt-uzunlugunda!"
    };

    private static TShiftDbContext Baglam(IKiraciBaglami baglam)
    {
        var opt = new DbContextOptionsBuilder<TShiftDbContext>()
            .UseNpgsql(Baglanti)
            .AddInterceptors(new KiraciBaglantiKesici(baglam))
            .Options;
        return new TShiftDbContext(opt, baglam);
    }

    private static (KimlikServisi Servis, TShiftDbContext Db, IKiraciBaglami Baglam) Kur()
    {
        var baglam = new KiraciBaglami();
        var db = Baglam(baglam);
        var parolalar = new ParolaServisi();
        var jetonlar = new JetonServisi(Ayarlar, TimeProvider.System);
        var yetkiler = new YetkiCozucu(db, TimeProvider.System);
        return (new KimlikServisi(db, baglam, parolalar, jetonlar, yetkiler, Ayarlar, TimeProvider.System), db, baglam);
    }

    /// <summary>Bir firma + bir kullanıcı + parola oluşturur. Slug'ı döner.</summary>
    private static async Task<(string Slug, Guid KiraciId, string Eposta)> FirmaKur(string etiket, string ek)
    {
        var baglam = new KiraciBaglami();
        baglam.Ayarla(null);
        await using var db = Baglam(baglam);

        var slug = $"test-{etiket}-{ek}".ToLowerInvariant();
        var kiraci = new Kiraci { Ad = $"Test {etiket} {ek}", Slug = slug, Durum = KiraciDurumu.Aktif };
        db.Kiracilar.Add(kiraci);
        await db.SaveChangesAsync();

        baglam.Ayarla(kiraci.Id);
        var eposta = $"{etiket}-{ek}@deneme.test";
        var kullanici = new Kullanici
        {
            Ad = "Deneme", Soyad = etiket, Eposta = eposta,
            EpostaDogrulandi = true, Durum = KullaniciDurumu.Aktif
        };
        db.Kullanicilar.Add(kullanici);
        await db.SaveChangesAsync();

        db.KullaniciKimlikBilgileri.Add(new KullaniciKimlikBilgisi
        {
            KullaniciId = kullanici.Id,
            SifreHash = new ParolaServisi().Ozetle(DogruParola)
        });
        await db.SaveChangesAsync();

        return (slug, kiraci.Id, eposta);
    }

    private static Task Temizle(params Guid[] kiraciler)
        => TestTemizlik.KiraciSilAsync(kiraciler);

    private static Task DenemeleriTemizle(params string[] epostalar)
        => TestTemizlik.GirisDenemeleriniSilAsync(epostalar);

    // ------------------------------------------------------------------ 1
    [Fact(DisplayName = "K1 - Dogru parola ile giris yapilir ve jeton verilir")]
    public async Task Dogru_parola_calisir()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var a = await FirmaKur("A", ek);
        var (servis, db, _) = Kur();
        try
        {
            var sonuc = await servis.GirisAsync(a.Slug, a.Eposta, DogruParola, "10.0.0.1", "test");

            Assert.True(sonuc.Basarili, $"Giris basarisiz: {sonuc.Hata}");
            Assert.False(string.IsNullOrWhiteSpace(sonuc.ErisimJetonu));
            Assert.False(string.IsNullOrWhiteSpace(sonuc.YenilemeJetonu));
            Assert.Equal(a.KiraciId, sonuc.KiraciId);
        }
        finally { await db.DisposeAsync(); await DenemeleriTemizle(a.Eposta); await Temizle(a.KiraciId); }
    }

    // ------------------------------------------------------------------ 2
    [Fact(DisplayName = "K2 - Yanlis parola reddedilir")]
    public async Task Yanlis_parola_reddedilir()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var a = await FirmaKur("A", ek);
        var (servis, db, _) = Kur();
        try
        {
            var sonuc = await servis.GirisAsync(a.Slug, a.Eposta, "bu-parola-yanlis", "10.0.0.2", "test");

            Assert.False(sonuc.Basarili);
            Assert.Equal(KimlikHatasi.KimlikGecersiz, sonuc.Hata);
            Assert.Null(sonuc.ErisimJetonu);
        }
        finally { await db.DisposeAsync(); await DenemeleriTemizle(a.Eposta); await Temizle(a.KiraciId); }
    }

    // ------------------------------------------------------------------ 3
    [Fact(DisplayName = "K3 - Baska firmanin adiyla giris yapilamaz")]
    public async Task Firma_karismaz()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var a = await FirmaKur("A", ek);
        var b = await FirmaKur("B", ek);
        var (servis, db, _) = Kur();
        try
        {
            // A firmasının kullanıcısı, B firmasının adıyla giriş denemesi yapıyor.
            // Parola doğru — ama kullanıcı o firmada yok.
            var sonuc = await servis.GirisAsync(b.Slug, a.Eposta, DogruParola, "10.0.0.3", "test");

            Assert.False(sonuc.Basarili);
            Assert.Equal(KimlikHatasi.KimlikGecersiz, sonuc.Hata);
        }
        finally
        {
            await db.DisposeAsync();
            await DenemeleriTemizle(a.Eposta, b.Eposta);
            await Temizle(a.KiraciId, b.KiraciId);
        }
    }

    // ------------------------------------------------------------------ 4
    [Fact(DisplayName = "K4 - Bes basarisiz denemeden sonra hesap kilitlenir")]
    public async Task Kaba_kuvvet_kilidi()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var a = await FirmaKur("A", ek);
        var (servis, db, _) = Kur();
        try
        {
            for (var i = 0; i < 5; i++)
            {
                var d = await servis.GirisAsync(a.Slug, a.Eposta, $"yanlis-{i}", "10.0.0.4", "test");
                Assert.Equal(KimlikHatasi.KimlikGecersiz, d.Hata);
            }

            // Altıncı deneme DOĞRU parolayla — yine de girilememeli.
            var sonuc = await servis.GirisAsync(a.Slug, a.Eposta, DogruParola, "10.0.0.4", "test");

            Assert.False(sonuc.Basarili);
            Assert.Equal(KimlikHatasi.Kilitli, sonuc.Hata);
        }
        finally { await db.DisposeAsync(); await DenemeleriTemizle(a.Eposta); await Temizle(a.KiraciId); }
    }

    // ------------------------------------------------------------------ 5
    [Fact(DisplayName = "K5 - Yenileme jetonu doner; eski jeton olur")]
    public async Task Jeton_doner()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var a = await FirmaKur("A", ek);
        var (servis, db, _) = Kur();
        try
        {
            var giris = await servis.GirisAsync(a.Slug, a.Eposta, DogruParola, "10.0.0.5", "test");
            Assert.True(giris.Basarili);

            var yeni = await servis.YenileAsync(giris.YenilemeJetonu!, "10.0.0.5", "test");

            Assert.True(yeni.Basarili, $"Yenileme basarisiz: {yeni.Hata}");
            Assert.NotEqual(giris.YenilemeJetonu, yeni.YenilemeJetonu);
        }
        finally { await db.DisposeAsync(); await DenemeleriTemizle(a.Eposta); await Temizle(a.KiraciId); }
    }

    // ------------------------------------------------------------------ 6
    [Fact(DisplayName = "K6 - Calinmis jeton tekrar kullanilirsa TUM oturumlar duser")]
    public async Task Jeton_hirsizligi_yakalanir()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var a = await FirmaKur("A", ek);
        var (servis, db, _) = Kur();
        try
        {
            var giris = await servis.GirisAsync(a.Slug, a.Eposta, DogruParola, "10.0.0.6", "test");
            var eskiJeton = giris.YenilemeJetonu!;

            // Meşru kullanıcı jetonunu kullanıyor, yenisini alıyor.
            var yeni = await servis.YenileAsync(eskiJeton, "10.0.0.6", "test");
            Assert.True(yeni.Basarili);

            // Şimdi hırsız, ele geçirdiği ESKİ jetonla geliyor.
            var hirsiz = await servis.YenileAsync(eskiJeton, "203.0.113.9", "hirsiz");

            Assert.False(hirsiz.Basarili);
            Assert.Equal(KimlikHatasi.JetonYenidenKullanildi, hirsiz.Hata);

            // Ve meşru kullanıcının YENİ jetonu da artık ölmüş olmalı —
            // hangisinin hırsız olduğunu bilemediğimiz için hepsi düşürüldü.
            var mesru = await servis.YenileAsync(yeni.YenilemeJetonu!, "10.0.0.6", "test");
            Assert.False(mesru.Basarili);
        }
        finally { await db.DisposeAsync(); await DenemeleriTemizle(a.Eposta); await Temizle(a.KiraciId); }
    }

    // ------------------------------------------------------------------ 7
    [Fact(DisplayName = "K7 - Parola veritabaninda duz metin olarak durmaz")]
    public async Task Parola_duz_metin_degil()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var a = await FirmaKur("A", ek);

        var baglam = new KiraciBaglami();
        baglam.Ayarla(a.KiraciId);
        await using var db = Baglam(baglam);
        try
        {
            var hash = await db.KullaniciKimlikBilgileri
                .Select(x => x.SifreHash).FirstAsync();

            Assert.DoesNotContain(DogruParola, hash);
            Assert.StartsWith("argon2id$", hash);

            // Aynı parola iki kez özetlenince FARKLI çıkmalı — her kayıtta ayrı tuz var.
            // Aksi halde "aynı parolayı kullanan kullanıcılar" veritabanından okunabilirdi.
            var p = new ParolaServisi();
            Assert.NotEqual(p.Ozetle(DogruParola), p.Ozetle(DogruParola));
            Assert.True(p.Dogrula(DogruParola, hash));
        }
        finally { await db.DisposeAsync(); await DenemeleriTemizle(a.Eposta); await Temizle(a.KiraciId); }
    }
}
