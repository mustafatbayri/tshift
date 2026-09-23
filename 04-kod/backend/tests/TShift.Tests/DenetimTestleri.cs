using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Npgsql;
using TShift.Domain.Calisanlar;
using TShift.Domain.Denetim;
using TShift.Domain.Kimlik;
using TShift.Domain.Kiracilar;
using TShift.Domain.Organizasyon;
using TShift.Infrastructure.Denetim;
using TShift.Infrastructure.Kimlik;
using TShift.Infrastructure.Persistence;
using Xunit;

namespace TShift.Tests;

/// <summary>
/// DENETİM KAYDI TESTLERİ.
///
/// Bu tablonun ertelenemez olmasının sebebi basit: tutulmayan geçmiş sonradan
/// üretilemez. Diğer her şey sonradan eklenebilir; bu eklenemez.
///
/// Sorulan sorular:
///   D1. Kayıt oluşturmak otomatik olarak iz bırakıyor mu
///   D2. Güncellemede SADECE değişen alanlar kaydediliyor mu
///   D3. Parola özeti denetim kaydına sızıyor mu (sızmamalı)
///   D4. Yazılmış bir kayıt DEĞİŞTİRİLEBİLİYOR mu (kesinlikle hayır)
///   D5. Yazılmış bir kayıt SİLİNEBİLİYOR mu (kesinlikle hayır)
///   D6. Denetim kaydı kiracılar arasında sızıyor mu
///   D7. İşlemi yapan kullanıcı kaydediliyor mu
/// </summary>
public class DenetimTestleri
{
    private static readonly string Baglanti = TestAyarlari.UygulamaBaglantisi;   // T-34

    private static TShiftDbContext Baglam(IKiraciBaglami b, IDenetimBaglami? d = null)
    {
        var opt = new DbContextOptionsBuilder<TShiftDbContext>()
            .UseNpgsql(Baglanti)
            .AddInterceptors(new KiraciBaglantiKesici(b))
            .Options;
        return new TShiftDbContext(opt, b, d);
    }

    private static async Task<(Guid KiraciId, Guid DepartmanId)> KiraciKur(string ek)
    {
        var b = new KiraciBaglami();
        b.Ayarla(null);
        await using var db = Baglam(b);

        var k = new Kiraci { Ad = $"Denetim {ek}", Slug = $"denetim-{ek}", Durum = KiraciDurumu.Aktif };
        db.Kiracilar.Add(k);
        await db.SaveChangesAsync();

        b.Ayarla(k.Id);
        var d = new Departman { Ad = "Ops", Kod = $"OPS-{ek}", CalismaTipi = CalismaTipi.Saatli };
        db.Departmanlar.Add(d);
        await db.SaveChangesAsync();

        return (k.Id, d.Id);
    }

    /// <summary>
    /// Temizlik SAHİBİ rolle yapılır — uygulama rolü denetim kaydını silemez,
    /// ki bu testlerin yarısının konusu tam olarak bu kısıt.
    /// </summary>
    private static Task Temizle(Guid kiraciId)
        => TestTemizlik.KiraciSilAsync(kiraciId);

    private static async Task<List<DenetimKaydi>> Kayitlar(Guid kiraciId, string varlik)
    {
        var b = new KiraciBaglami();
        b.Ayarla(kiraciId);
        await using var db = Baglam(b);
        return await db.DenetimKayitlari
            .Where(k => k.Varlik == varlik)
            .OrderBy(k => k.Zaman)
            .ToListAsync();
    }

    // ------------------------------------------------------------------ D1
    [Fact(DisplayName = "D1 - Kayit olusturmak otomatik iz birakir")]
    public async Task Olusturma_kaydediliyor()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var (kiraciId, depId) = await KiraciKur(ek);
        try
        {
            var b = new KiraciBaglami(); b.Ayarla(kiraciId);
            await using (var db = Baglam(b))
            {
                db.Calisanlar.Add(new Calisan
                {
                    PersonelNo = $"D1-{ek}", Ad = "Deniz", Soyad = "Ak",
                    DepartmanId = depId, IseGiris = new DateOnly(2025, 1, 1)
                });
                await db.SaveChangesAsync();
            }

            var kayitlar = await Kayitlar(kiraciId, "employees");

            // Hicbir yerde "denetim yaz" cagrisi yapmadik. Yine de var.
            var kayit = Assert.Single(kayitlar);
            Assert.Equal(DenetimIslemi.Olustur, kayit.Islem);
            Assert.Null(kayit.Oncesi);
            Assert.NotNull(kayit.Sonrasi);
            Assert.Contains("Deniz", kayit.Sonrasi);
        }
        finally { await Temizle(kiraciId); }
    }

    // ------------------------------------------------------------------ D2
    [Fact(DisplayName = "D2 - Guncellemede SADECE degisen alanlar kaydedilir")]
    public async Task Guncelleme_sadece_degisenler()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var (kiraciId, depId) = await KiraciKur(ek);
        try
        {
            var b = new KiraciBaglami(); b.Ayarla(kiraciId);
            Guid calisanId;

            await using (var db = Baglam(b))
            {
                var c = new Calisan
                {
                    PersonelNo = $"D2-{ek}", Ad = "Eski", Soyad = "Ad",
                    DepartmanId = depId, IseGiris = new DateOnly(2025, 1, 1)
                };
                db.Calisanlar.Add(c);
                await db.SaveChangesAsync();
                calisanId = c.Id;
            }

            await using (var db = Baglam(b))
            {
                var c = await db.Calisanlar.FirstAsync(x => x.Id == calisanId);
                c.Ad = "Yeni";
                await db.SaveChangesAsync();
            }

            var guncelleme = (await Kayitlar(kiraciId, "employees"))
                .Single(k => k.Islem == DenetimIslemi.Guncelle);

            var oncesi = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(guncelleme.Oncesi!)!;
            var sonrasi = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(guncelleme.Sonrasi!)!;

            Assert.Equal("Eski", oncesi["Ad"].GetString());
            Assert.Equal("Yeni", sonrasi["Ad"].GetString());

            // Degismeyen alanlar kayda GIRMEMELI. Tum satiri iki kez yazmak
            // "ne degisti" sorusunu cevapsiz birakir.
            Assert.False(oncesi.ContainsKey("Soyad"), "Degismeyen alan kayda girmis");
            Assert.False(oncesi.ContainsKey("PersonelNo"), "Degismeyen alan kayda girmis");
        }
        finally { await Temizle(kiraciId); }
    }

    // ------------------------------------------------------------------ D3
    [Fact(DisplayName = "D3 - Parola ozeti denetim kaydina SIZMAZ")]
    public async Task Parola_sizmaz()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var (kiraciId, _) = await KiraciKur(ek);
        const string parola = "Denetim-Sizinti-Testi-2026!";
        try
        {
            var b = new KiraciBaglami(); b.Ayarla(kiraciId);
            string hash;

            await using (var db = Baglam(b))
            {
                var u = new Kullanici
                {
                    Ad = "Test", Soyad = "Kisi", Eposta = $"d3-{ek}@denetim.test",
                    EpostaDogrulandi = true, Durum = KullaniciDurumu.Aktif
                };
                db.Kullanicilar.Add(u);
                await db.SaveChangesAsync();

                hash = new ParolaServisi().Ozetle(parola);
                db.KullaniciKimlikBilgileri.Add(new KullaniciKimlikBilgisi
                {
                    KullaniciId = u.Id, SifreHash = hash
                });
                await db.SaveChangesAsync();
            }

            var kayitlar = await Kayitlar(kiraciId, "user_credentials");
            var kayit = Assert.Single(kayitlar);

            // Parolanin DEGISTIGI kaydedilir, DEGERI kaydedilmez.
            Assert.DoesNotContain(hash, kayit.Sonrasi);
            Assert.DoesNotContain(parola, kayit.Sonrasi);
            Assert.Contains("gizlendi", kayit.Sonrasi);
        }
        finally { await Temizle(kiraciId); }
    }

    // ------------------------------------------------------------------ D4
    /// <summary>
    /// Bu projedeki en önemli testlerden biri.
    ///
    /// Değiştirilebilen bir denetim kaydı, denetim kaydı değildir. Uygulamada
    /// açık bulan biri önce istediğini yapar, sonra izini siler. Bu yüzden
    /// yetki uygulama katmanında değil, VERİTABANINDA kapalı — uygulama
    /// katmanı zaten açığın bulunduğu katmandır.
    /// </summary>
    [Fact(DisplayName = "D4 - Yazilmis denetim kaydi DEGISTIRILEMEZ")]
    public async Task Kayit_degistirilemez()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var (kiraciId, depId) = await KiraciKur(ek);
        try
        {
            var b = new KiraciBaglami(); b.Ayarla(kiraciId);
            await using var db = Baglam(b);

            db.Calisanlar.Add(new Calisan
            {
                PersonelNo = $"D4-{ek}", Ad = "Iz", Soyad = "Birakan",
                DepartmanId = depId, IseGiris = new DateOnly(2025, 1, 1)
            });
            await db.SaveChangesAsync();

            // Uygulama rolüyle kaydı örtbas etmeye çalışıyoruz.
            var hata = await Assert.ThrowsAsync<PostgresException>(async () =>
                await db.Database.ExecuteSqlAsync(
                    $"UPDATE audit_log SET sonrasi = '{{}}'::jsonb WHERE tenant_id = {kiraciId}"));

            // 42501 = yetersiz yetki
            Assert.Equal("42501", hata.SqlState);
        }
        finally { await Temizle(kiraciId); }
    }

    // ------------------------------------------------------------------ D5
    [Fact(DisplayName = "D5 - Yazilmis denetim kaydi SILINEMEZ")]
    public async Task Kayit_silinemez()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var (kiraciId, depId) = await KiraciKur(ek);
        try
        {
            var b = new KiraciBaglami(); b.Ayarla(kiraciId);
            await using var db = Baglam(b);

            db.Calisanlar.Add(new Calisan
            {
                PersonelNo = $"D5-{ek}", Ad = "Silinemez", Soyad = "Iz",
                DepartmanId = depId, IseGiris = new DateOnly(2025, 1, 1)
            });
            await db.SaveChangesAsync();

            var hata = await Assert.ThrowsAsync<PostgresException>(async () =>
                await db.Database.ExecuteSqlAsync(
                    $"DELETE FROM audit_log WHERE tenant_id = {kiraciId}"));

            Assert.Equal("42501", hata.SqlState);
        }
        finally { await Temizle(kiraciId); }
    }

    // ------------------------------------------------------------------ D6
    /// <summary>
    /// B kiracısı, A'nın denetim kayıtlarını göremez.
    ///
    /// DİKKAT — iddianın doğru kurulması: "B hiçbir kayıt görmemeli" YANLIŞ bir
    /// iddiadır, çünkü B'nin kendi işlemleri de kayıt bırakır ve onları
    /// görmesi gerekir. Doğru iddia: A'nın kayıtlarının HİÇBİRİ B'ye görünmez.
    /// Bu yüzden sayı değil, KİMLİK karşılaştırıyoruz.
    /// </summary>
    [Fact(DisplayName = "D6 - Bir kiraci digerinin denetim kaydini goremez")]
    public async Task Kayit_kiraci_yalitimli()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var a = await KiraciKur($"a{ek}");
        var b2 = await KiraciKur($"b{ek}");
        try
        {
            var ba = new KiraciBaglami(); ba.Ayarla(a.KiraciId);
            await using (var db = Baglam(ba))
            {
                db.Calisanlar.Add(new Calisan
                {
                    PersonelNo = $"D6-{ek}", Ad = "Gizli", Soyad = "Kisi",
                    DepartmanId = a.DepartmanId, IseGiris = new DateOnly(2025, 1, 1)
                });
                await db.SaveChangesAsync();
            }

            // A'nin butun kayitlarinin kimlikleri.
            List<Guid> aKimlikleri;
            await using (var dbA = Baglam(ba))
                aKimlikleri = await dbA.DenetimKayitlari.Select(k => k.Id).ToListAsync();

            Assert.NotEmpty(aKimlikleri);   // A gercekten kayit birakmis olmali

            // B'nin gorebildikleri.
            var bb = new KiraciBaglami(); bb.Ayarla(b2.KiraciId);
            await using var dbB = Baglam(bb);
            var bKimlikleri = await dbB.DenetimKayitlari.Select(k => k.Id).ToListAsync();

            // Kesisim BOS olmali. B kendi kayitlarini gorur, A'nınkileri asla.
            var sizan = bKimlikleri.Intersect(aKimlikleri).ToList();
            Assert.Empty(sizan);

            // Ayrica: B, A'nin olusturdugu calisanin kaydini hic gormemeli.
            var calisanKayitlari = await dbB.DenetimKayitlari
                .CountAsync(k => k.Varlik == "employees");
            Assert.Equal(0, calisanKayitlari);
        }
        finally { await Temizle(a.KiraciId); await Temizle(b2.KiraciId); }
    }

    // ------------------------------------------------------------------ D7
    [Fact(DisplayName = "D7 - Islemi yapan kullanici ve IP kaydedilir")]
    public async Task Kim_yapti_kaydediliyor()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var (kiraciId, depId) = await KiraciKur(ek);
        var kullaniciId = Guid.CreateVersion7();
        try
        {
            var b = new KiraciBaglami(); b.Ayarla(kiraciId);
            var denetim = new DenetimBaglami();
            denetim.Ayarla(kullaniciId, "10.20.30.40", "test-tarayici");

            await using (var db = Baglam(b, denetim))
            {
                db.Calisanlar.Add(new Calisan
                {
                    PersonelNo = $"D7-{ek}", Ad = "Kim", Soyad = "Yapti",
                    DepartmanId = depId, IseGiris = new DateOnly(2025, 1, 1)
                });
                await db.SaveChangesAsync();
            }

            var kayit = Assert.Single(await Kayitlar(kiraciId, "employees"));
            Assert.Equal(kullaniciId, kayit.KullaniciId);
            Assert.Equal("10.20.30.40", kayit.Ip);
            Assert.Equal("test-tarayici", kayit.Tarayici);
        }
        finally { await Temizle(kiraciId); }
    }
}
