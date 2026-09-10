using TShift.Domain.Common;

namespace TShift.Domain.Denetim;

public enum DenetimIslemi
{
    Olustur = 1,
    Guncelle = 2,
    Sil = 3,
    // Aşağıdakiler otomatik yakalanmaz; iş akışı bunları açıkça yazar.
    Onayla = 4,
    Yayinla = 5,
    Giris = 6,
    YetkiDegisimi = 7
}

/// <summary>
/// Denetim kaydı. Spec §8.8 `audit_log`.
///
/// NEDEN BU TABLO ERTELENEMEZ:
/// Tutulmayan geçmiş sonradan üretilemez. Canlıya denetim kaydı olmadan
/// çıkıp altı ay sonra "bu vardiyayı kim değiştirdi, hangi kural sürümüyle
/// üretilmişti" diye sorarsan cevap yoktur ve hiçbir zaman olmayacaktır.
/// Diğer her şey sonradan eklenebilir; bu eklenemez.
///
/// ÜÇ ÖZELLİĞİ VAR, ÜÇÜ DE KASITLI:
///
/// 1. **Otomatiktir.** Kayıt, uçların içinde tek tek çağrılmaz; EF'in kaydetme
///    akışına bağlıdır. Elle hatırlanması gereken hiçbir şey uzun vadede
///    hatırlanmaz — yeni bir uç yazılır, denetim satırı eklenmeyi unutulur ve
///    o işlem sonsuza kadar görünmez olur.
///
/// 2. **Aynı işlemdedir.** Denetim satırı, değişikliğin kendisiyle aynı
///    veritabanı işleminde yazılır. Biri kaydedilip diğeri kaydedilemez;
///    ikisi de olur ya da ikisi de olmaz.
///
/// 3. **Sadece eklenir.** Uygulama rolünün bu tabloda GÜNCELLEME ve SİLME
///    yetkisi yoktur (05-denetim-kaydi.sql). Değiştirilebilen bir denetim
///    kaydı, denetim kaydı değildir — izini silebilen biri için hiçbir şey
///    ifade etmez.
/// </summary>
public class DenetimKaydi : VarlikTemel, IKiraciVarligi
{
    public Guid KiraciId { get; set; }

    /// <summary>İşlemi yapan. Sistem işlemlerinde boş olabilir.</summary>
    public Guid? KullaniciId { get; set; }

    /// <summary>Tablo adı: `employees`, `plans`...</summary>
    public required string Varlik { get; set; }
    public Guid VarlikId { get; set; }

    public DenetimIslemi Islem { get; set; }

    /// <summary>Değişen alanların önceki değerleri (jsonb). Oluşturmada boş.</summary>
    public string? Oncesi { get; set; }
    /// <summary>Değişen alanların yeni değerleri (jsonb). Silmede boş.</summary>
    public string? Sonrasi { get; set; }

    public string? Ip { get; set; }
    public string? Tarayici { get; set; }

    public DateTimeOffset Zaman { get; set; } = DateTimeOffset.UtcNow;
}
