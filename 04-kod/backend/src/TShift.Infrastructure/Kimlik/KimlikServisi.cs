using Microsoft.EntityFrameworkCore;
using TShift.Domain.Kimlik;
using TShift.Infrastructure.Persistence;
using TShift.Infrastructure.Yetki;

namespace TShift.Infrastructure.Kimlik;

public enum KimlikHatasi
{
    Yok = 0,
    /// <summary>E-posta, parola veya firma yanlış. Hangisi olduğu ASLA söylenmez.</summary>
    KimlikGecersiz,
    /// <summary>Kaba kuvvet kilidi devrede.</summary>
    Kilitli,
    HesapPasif,
    JetonGecersiz,
    JetonSuresiDoldu,
    /// <summary>Kullanılmış jeton tekrar geldi — tüm oturumlar düşürüldü.</summary>
    JetonYenidenKullanildi
}

public sealed record OturumSonucu(
    KimlikHatasi Hata,
    string? ErisimJetonu = null,
    string? YenilemeJetonu = null,
    DateTimeOffset? ErisimBitis = null,
    Guid? KullaniciId = null,
    Guid? KiraciId = null,
    bool ZorunluParolaDegisimi = false)
{
    public bool Basarili => Hata == KimlikHatasi.Yok;
    public static OturumSonucu Basarisiz(KimlikHatasi h) => new(h);
}

public interface IKimlikServisi
{
    Task<OturumSonucu> GirisAsync(string firmaSlug, string eposta, string parola,
        string? ip, string? tarayici, CancellationToken ct = default);

    Task<OturumSonucu> YenileAsync(string yenilemeJetonu,
        string? ip, string? tarayici, CancellationToken ct = default);

    Task<bool> CikisAsync(string yenilemeJetonu, CancellationToken ct = default);
    Task<int> TumOturumlariKapatAsync(Guid kullaniciId, CancellationToken ct = default);
}

/// <summary>
/// Giriş, yenileme ve çıkış akışı. Spec §7.4 ve §10.1.
///
/// Bu sınıfın en kritik özelliği, HTTP'den hiçbir şey bilmemesi. Test edilebilir
/// olması için: kimlik güvenliği testleri bir tarayıcı ya da sunucu ayağa
/// kaldırmadan, doğrudan bu sınıfa karşı yazılabilir.
/// </summary>
public sealed class KimlikServisi(
    TShiftDbContext db,
    IKiraciBaglami baglam,
    IParolaServisi parolalar,
    IJetonServisi jetonlar,
    IYetkiCozucu yetkiler,
    KimlikAyarlari ayarlar,
    TimeProvider saat) : IKimlikServisi
{
    // ---------------------------------------------------------------- giriş
    public async Task<OturumSonucu> GirisAsync(string firmaSlug, string eposta, string parola,
        string? ip, string? tarayici, CancellationToken ct = default)
    {
        var simdi = saat.GetUtcNow();
        eposta = eposta.Trim();
        firmaSlug = firmaSlug.Trim().ToLowerInvariant();

        // 1) Kaba kuvvet kilidi — kullanıcı aranmadan ÖNCE.
        //    Önce bakmanın sebebi: kilitli bir hesapta parola kontrolü yapmak,
        //    saldırgana her denemede bir Argon2 hesabı bedavaya yaptırmak olur.
        if (await KilitliMi(eposta, ip, simdi, ct))
        {
            await DenemeKaydet(firmaSlug, eposta, ip, tarayici, false, simdi, ct);
            return OturumSonucu.Basarisiz(KimlikHatasi.Kilitli);
        }

        // 2) Firmayı bul. `tenants` tablosu RLS'e tabi değil, bağlamsız okunur.
        var oncekiBaglam = baglam.KiraciId;
        baglam.Ayarla(null);
        var kiraci = await db.Kiracilar
            .AsNoTracking()
            .FirstOrDefaultAsync(k => k.Slug == firmaSlug, ct);

        if (kiraci is null)
        {
            // Firma yok. Yine de Argon2 çalıştırıyoruz ki süre aynı olsun —
            // yoksa "bu firma var mı" sorusu zamanlamayla cevaplanabilir hale gelir.
            parolalar.BosaCalis();
            await DenemeKaydet(firmaSlug, eposta, ip, tarayici, false, simdi, ct);
            baglam.Ayarla(oncekiBaglam);
            return OturumSonucu.Basarisiz(KimlikHatasi.KimlikGecersiz);
        }

        // 3) Bundan sonrası o kiracının bağlamında. RLS artık bizi o firmaya kilitler:
        //    yanlış bir sorgu yazsak bile başka firmanın kullanıcısı gelemez.
        baglam.Ayarla(kiraci.Id);

        var kullanici = await db.Kullanicilar
            .FirstOrDefaultAsync(k => k.Eposta == eposta, ct);

        if (kullanici is null)
        {
            parolalar.BosaCalis();
            await DenemeKaydet(firmaSlug, eposta, ip, tarayici, false, simdi, ct);
            return OturumSonucu.Basarisiz(KimlikHatasi.KimlikGecersiz);
        }

        if (kullanici.KilitBitis is { } kb && kb > simdi)
        {
            await DenemeKaydet(firmaSlug, eposta, ip, tarayici, false, simdi, ct);
            return OturumSonucu.Basarisiz(KimlikHatasi.Kilitli);
        }

        var kimlik = await db.KullaniciKimlikBilgileri
            .FirstOrDefaultAsync(x => x.KullaniciId == kullanici.Id, ct);

        if (kimlik is null || !parolalar.Dogrula(parola, kimlik.SifreHash))
        {
            if (kimlik is null) parolalar.BosaCalis();

            kullanici.BasarisizGiris++;
            if (kullanici.BasarisizGiris >= ayarlar.KilitEsigi)
                kullanici.KilitBitis = simdi.Add(ayarlar.KilitSuresi);

            await DenemeKaydet(firmaSlug, eposta, ip, tarayici, false, simdi, ct);
            await db.SaveChangesAsync(ct);
            return OturumSonucu.Basarisiz(KimlikHatasi.KimlikGecersiz);
        }

        // Parola doğru ama hesap kapalıysa giriş yok.
        if (kullanici.Durum != KullaniciDurumu.Aktif)
        {
            await DenemeKaydet(firmaSlug, eposta, ip, tarayici, false, simdi, ct);
            await db.SaveChangesAsync(ct);
            return OturumSonucu.Basarisiz(KimlikHatasi.HesapPasif);
        }

        // 4) Başarılı. Sayaçlar sıfırlanır.
        kullanici.BasarisizGiris = 0;
        kullanici.KilitBitis = null;
        kullanici.SonGiris = simdi;

        await DenemeKaydet(firmaSlug, eposta, ip, tarayici, true, simdi, ct);
        var sonuc = await OturumAc(kullanici, null, ip, tarayici, simdi, kimlik.ZorunluDegisim, ct);
        await db.SaveChangesAsync(ct);
        return sonuc;
    }

    // -------------------------------------------------------------- yenileme
    public async Task<OturumSonucu> YenileAsync(string yenilemeJetonu,
        string? ip, string? tarayici, CancellationToken ct = default)
    {
        var simdi = saat.GetUtcNow();

        // Jetonun ön ekinden kiracıyı çözüyoruz — RLS'in satırı görebilmesi için şart.
        if (!jetonlar.KiraciCoz(yenilemeJetonu, out var kiraciId))
            return OturumSonucu.Basarisiz(KimlikHatasi.JetonGecersiz);

        baglam.Ayarla(kiraciId);

        var ozet = jetonlar.Ozetle(yenilemeJetonu);
        var kayit = await db.YenilemeJetonlari.FirstOrDefaultAsync(x => x.JetonOzeti == ozet, ct);

        if (kayit is null)
            return OturumSonucu.Basarisiz(KimlikHatasi.JetonGecersiz);

        // GÜVENLİK OLAYI: kullanılmış bir jeton tekrar geldi.
        // Meşru istemci bunu yapmaz — jetonu kullandıktan sonra yenisini saklar.
        // Aynı jetonun ikinci kez gelmesi, birinin kopyasını ele geçirdiği anlamına
        // gelir. Hangisinin hırsız olduğunu bilemeyiz, bu yüzden HEPSİ düşürülür.
        if (kayit.IptalZamani is not null && kayit.IptalSebebi == TShift.Domain.Kimlik.IptalSebebi.Kullanildi)
        {
            await TumOturumlariKapatAsync(kayit.KullaniciId, ct);
            return OturumSonucu.Basarisiz(KimlikHatasi.JetonYenidenKullanildi);
        }

        if (kayit.IptalZamani is not null)
            return OturumSonucu.Basarisiz(KimlikHatasi.JetonGecersiz);

        if (kayit.Bitis <= simdi)
            return OturumSonucu.Basarisiz(KimlikHatasi.JetonSuresiDoldu);

        var kullanici = await db.Kullanicilar.FirstOrDefaultAsync(k => k.Id == kayit.KullaniciId, ct);
        if (kullanici is null || kullanici.Durum != KullaniciDurumu.Aktif)
            return OturumSonucu.Basarisiz(KimlikHatasi.HesapPasif);

        // Döner jeton: eski iptal, yeni verilir.
        kayit.IptalZamani = simdi;
        kayit.IptalSebebi = TShift.Domain.Kimlik.IptalSebebi.Kullanildi;
        kayit.SonKullanim = simdi;

        var sonuc = await OturumAc(kullanici, kayit.JetonOzeti, ip, tarayici, simdi, false, ct);
        await db.SaveChangesAsync(ct);
        return sonuc;
    }

    // ----------------------------------------------------------------- çıkış
    public async Task<bool> CikisAsync(string yenilemeJetonu, CancellationToken ct = default)
    {
        if (!jetonlar.KiraciCoz(yenilemeJetonu, out var kiraciId)) return false;
        baglam.Ayarla(kiraciId);

        var ozet = jetonlar.Ozetle(yenilemeJetonu);
        var kayit = await db.YenilemeJetonlari.FirstOrDefaultAsync(x => x.JetonOzeti == ozet, ct);
        if (kayit is null || kayit.IptalZamani is not null) return false;

        kayit.IptalZamani = saat.GetUtcNow();
        kayit.IptalSebebi = TShift.Domain.Kimlik.IptalSebebi.Cikis;
        await db.SaveChangesAsync(ct);
        return true;
    }

    public async Task<int> TumOturumlariKapatAsync(Guid kullaniciId, CancellationToken ct = default)
    {
        var simdi = saat.GetUtcNow();

        // Toplu güncelleme: satırları tek SQL ile iptal eder.
        var sayi = await db.YenilemeJetonlari
            .Where(x => x.KullaniciId == kullaniciId && x.IptalZamani == null)
            .ExecuteUpdateAsync(s => s
                .SetProperty(x => x.IptalZamani, (DateTimeOffset?)simdi)
                .SetProperty(x => x.IptalSebebi, (TShift.Domain.Kimlik.IptalSebebi?)TShift.Domain.Kimlik.IptalSebebi.Guvenlik), ct);

        // ExecuteUpdate veritabanını değiştirir ama EF'in bellekteki kopyalarını
        // değiştirmez. Temizlemezsek, aynı bağlamda yapılan bir sonraki sorgu
        // iptal edilmiş jetonu HÂLÂ GEÇERLİ olarak görür — yani güvenlik olayından
        // sonra çalınmış jeton çalışmaya devam eder. Bellekteki kopyaları atıyoruz.
        db.ChangeTracker.Clear();

        return sayi;
    }

    // ------------------------------------------------------------- yardımcı
    private async Task<OturumSonucu> OturumAc(Kullanici kullanici, string? oncekiOzet,
        string? ip, string? tarayici, DateTimeOffset simdi, bool zorunluDegisim, CancellationToken ct)
    {
        // İzinler jetona yazılacağı için giriş anında çözülür.
        var yetki = await yetkiler.CozAsync(kullanici.Id, ct);

        var (ham, ozet) = jetonlar.YenilemeJetonuUret(kullanici.KiraciId);

        db.YenilemeJetonlari.Add(new YenilemeJetonu
        {
            KiraciId = kullanici.KiraciId,
            KullaniciId = kullanici.Id,
            JetonOzeti = ozet,
            OncekiJetonOzeti = oncekiOzet,
            Cihaz = Kirp(tarayici, 300),
            Ip = Kirp(ip, 60),
            SonKullanim = simdi,
            Bitis = simdi.Add(ayarlar.YenilemeOmru)
        });

        return new OturumSonucu(
            KimlikHatasi.Yok,
            jetonlar.ErisimJetonuUret(kullanici, yetki),
            ham,
            simdi.Add(ayarlar.ErisimOmru),
            kullanici.Id,
            kullanici.KiraciId,
            zorunluDegisim);
    }

    private async Task<bool> KilitliMi(string eposta, string? ip, DateTimeOffset simdi, CancellationToken ct)
    {
        var pencere = simdi.Subtract(ayarlar.KilitSuresi);

        // login_attempts RLS'e tabi değil; bağlamdan bağımsız sayılır.
        var epostaSayisi = await db.GirisDenemeleri.CountAsync(
            d => d.Eposta == eposta && !d.Basarili && d.Zaman >= pencere, ct);
        if (epostaSayisi >= ayarlar.KilitEsigi) return true;

        if (string.IsNullOrWhiteSpace(ip)) return false;

        var ipSayisi = await db.GirisDenemeleri.CountAsync(
            d => d.Ip == ip && !d.Basarili && d.Zaman >= pencere, ct);
        return ipSayisi >= ayarlar.KilitEsigi;
    }

    private async Task DenemeKaydet(string? firmaSlug, string eposta, string? ip, string? tarayici,
        bool basarili, DateTimeOffset simdi, CancellationToken ct)
    {
        db.GirisDenemeleri.Add(new GirisDenemesi
        {
            FirmaSlug = Kirp(firmaSlug, 80),
            Eposta = Kirp(eposta, 320)!,
            Ip = Kirp(ip, 60),
            Tarayici = Kirp(tarayici, 400),
            Basarili = basarili,
            Zaman = simdi
        });
        await db.SaveChangesAsync(ct);
    }

    private static string? Kirp(string? s, int n)
        => string.IsNullOrEmpty(s) ? s : (s.Length <= n ? s : s[..n]);
}
