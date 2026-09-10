using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.ChangeTracking;
using TShift.Domain.Common;
using TShift.Domain.Denetim;

namespace TShift.Infrastructure.Denetim;

/// <summary>
/// Değişiklik izleyicisine bakıp denetim satırlarını üretir.
///
/// Kaydetmeden ÖNCE çalışır. Bunun mümkün olmasının sebebi kimliklerin
/// istemci tarafında üretilmesi (<see cref="VarlikTemel"/> içinde
/// `Guid.CreateVersion7()`): veritabanı kimlik atamadığı için, satır
/// yazılmadan da kimliği biliyoruz. Böylece denetim kaydı değişiklikle
/// AYNI kaydetme işleminde gidiyor — biri yazılıp diğeri yazılamıyor.
/// </summary>
public static class DenetimToplayici
{
    /// <summary>
    /// Denetim dışı kalan varlıklar ve gerekçeleri.
    ///
    /// Bu liste kısa olmalı ve her maddesinin bir sebebi bulunmalı.
    /// "Gürültü yapıyor" iyi bir sebep değildir; "içinde sır var" ya da
    /// "kendi kendini kaydeder" iyi sebeplerdir.
    /// </summary>
    private static readonly HashSet<string> DisindaKalanlar =
    [
        "audit_log",       // kendi kendini kaydederse sonsuz döngü olur
        "login_attempts",  // zaten kendisi bir kayıt tablosu; her denemede satır
        "refresh_tokens"   // jeton özeti içerir; ayrıca her yenilemede yazılır
    ];

    /// <summary>
    /// Değeri ASLA kaydedilmeyen alanlar.
    ///
    /// Parola özeti ve jeton özeti denetim kaydına girmemeli. Aksi halde
    /// denetim kaydı, zaman içinde bütün parola özetlerinin arşivi hâline
    /// gelir — hem de "sadece eklenir" olduğu için hiç temizlenemeyen bir arşiv.
    /// Alanın DEĞİŞTİĞİ kaydedilir, DEĞERİ kaydedilmez.
    /// </summary>
    private static readonly HashSet<string> GizliAlanlar =
    [
        nameof(TShift.Domain.Kimlik.KullaniciKimlikBilgisi.SifreHash),
        "JetonOzeti",
        "OncekiJetonOzeti"
    ];

    private const string Gizlendi = "<gizlendi>";

    public static List<DenetimKaydi> Topla(ChangeTracker izleyici, IDenetimBaglami? baglam)
    {
        var simdi = DateTimeOffset.UtcNow;
        var kayitlar = new List<DenetimKaydi>();

        // Listeye önce topluyoruz: izleyici gezilirken ona yeni varlık eklenemez.
        var girdiler = izleyici.Entries()
            .Where(e => e.State is EntityState.Added or EntityState.Modified or EntityState.Deleted)
            .ToList();

        foreach (var g in girdiler)
        {
            var tablo = g.Metadata.GetTableName();
            if (tablo is null || DisindaKalanlar.Contains(tablo)) continue;

            // Kiracıya ait olmayan tablolar (tenants, permissions) şimdilik
            // kapsam dışı: denetim kaydının kendisi kiracıya ait olduğu için
            // bunları hangi kiracıya yazacağımız belirsiz. Kiracı yönetimi
            // uçları yazıldığında ayrı bir sistem kaydı gerekecek.
            if (g.Entity is not IKiraciVarligi kiraciVarligi) continue;

            var kimlik = Kimlik(g);
            if (kimlik is null) continue;

            var (oncesi, sonrasi) = Degerler(g);

            // Yalnızca gizli alanlar değiştiyse yine de kaydediyoruz:
            // "parola değişti" bilgisi denetim açısından önemli.
            kayitlar.Add(new DenetimKaydi
            {
                KiraciId = kiraciVarligi.KiraciId,
                KullaniciId = baglam?.KullaniciId,
                Varlik = tablo,
                VarlikId = kimlik.Value,
                Islem = g.State switch
                {
                    EntityState.Added => DenetimIslemi.Olustur,
                    EntityState.Deleted => DenetimIslemi.Sil,
                    _ => DenetimIslemi.Guncelle
                },
                Oncesi = oncesi,
                Sonrasi = sonrasi,
                Ip = baglam?.Ip,
                Tarayici = baglam?.Tarayici,
                Zaman = simdi
            });
        }

        return kayitlar;
    }

    private static Guid? Kimlik(EntityEntry g)
    {
        var anahtar = g.Metadata.FindPrimaryKey();
        if (anahtar is null || anahtar.Properties.Count != 1) return null;

        var deger = g.Property(anahtar.Properties[0].Name).CurrentValue;
        return deger is Guid k ? k : null;
    }

    private static (string? Oncesi, string? Sonrasi) Degerler(EntityEntry g)
    {
        var oncesi = new Dictionary<string, object?>();
        var sonrasi = new Dictionary<string, object?>();

        foreach (var p in g.Properties)
        {
            var ad = p.Metadata.Name;

            // Zaman damgaları her satırda değişir; kaydı şişirir, bilgi katmaz.
            if (ad is nameof(VarlikTemel.OlusturmaZamani) or nameof(VarlikTemel.GuncellemeZamani))
                continue;

            var gizli = GizliAlanlar.Contains(ad);

            switch (g.State)
            {
                case EntityState.Added:
                    sonrasi[ad] = gizli ? Gizlendi : Sadelestir(p.CurrentValue);
                    break;

                case EntityState.Deleted:
                    oncesi[ad] = gizli ? Gizlendi : Sadelestir(p.OriginalValue);
                    break;

                case EntityState.Modified when p.IsModified:
                    // Yalnızca DEĞİŞEN alanlar. Tüm satırı iki kez yazmak
                    // kaydı okunamaz hale getirir — "ne değişti" sorusunun
                    // cevabı gürültünün içinde kaybolur.
                    oncesi[ad] = gizli ? Gizlendi : Sadelestir(p.OriginalValue);
                    sonrasi[ad] = gizli ? Gizlendi : Sadelestir(p.CurrentValue);
                    break;
            }
        }

        return (
            oncesi.Count > 0 ? JsonSerializer.Serialize(oncesi) : null,
            sonrasi.Count > 0 ? JsonSerializer.Serialize(sonrasi) : null);
    }

    /// <summary>Enum'ları sayı yerine adıyla yazar — kayıt insan tarafından okunacak.</summary>
    private static object? Sadelestir(object? deger) => deger switch
    {
        null => null,
        Enum e => e.ToString(),
        _ => deger
    };
}
