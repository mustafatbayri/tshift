namespace TShift.Infrastructure.Denetim;

/// <summary>
/// "Bu işi kim, nereden yaptı" bilgisi. İstek başına doldurulur.
///
/// Kiracı bağlamından ayrı tutuluyor çünkü farklı sorulara cevap veriyorlar:
/// kiracı bağlamı bir GÜVENLİK sınırı (hangi verilere erişilebilir),
/// denetim bağlamı bir KAYIT bilgisi (kim yaptı). Birini boş bırakmak
/// diğerini bozmamalı — kullanıcısı olmayan bir sistem işlemi de veri yazabilir.
/// </summary>
public interface IDenetimBaglami
{
    Guid? KullaniciId { get; }
    string? Ip { get; }
    string? Tarayici { get; }
    void Ayarla(Guid? kullaniciId, string? ip = null, string? tarayici = null);
}

public sealed class DenetimBaglami : IDenetimBaglami
{
    public Guid? KullaniciId { get; private set; }
    public string? Ip { get; private set; }
    public string? Tarayici { get; private set; }

    public void Ayarla(Guid? kullaniciId, string? ip = null, string? tarayici = null)
    {
        KullaniciId = kullaniciId;
        Ip = Kirp(ip, 60);
        Tarayici = Kirp(tarayici, 400);
    }

    private static string? Kirp(string? s, int n)
        => string.IsNullOrEmpty(s) ? s : (s.Length <= n ? s : s[..n]);
}
