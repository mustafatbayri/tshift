using TShift.Domain.Common;

namespace TShift.Domain.Kimlik;

/// <summary>
/// Giriş denemesi kaydı. Spec §8.1 `login_attempts`. Kaba kuvvet kilidi
/// bu tablodaki sayımla çalışır: aynı e-posta veya IP için 15 dakikada
/// 5 başarısız deneme → 15 dakika kilit.
///
/// DİKKAT — bu tablo bilerek <see cref="IKiraciVarligi"/> UYGULAMAZ,
/// yani satır seviyesi güvenliğe tabi değildir.
///
/// Sebep: giriş denemesi, kiracının kim olduğu HENÜZ BİLİNMEDEN kaydedilmek
/// zorunda. Var olmayan bir firma adıyla ya da var olmayan bir e-postayla
/// yapılan denemeler de sayılmalı — yoksa saldırgan, kaydı olmayan bir
/// e-posta deneyerek kilidi bypass eder.
///
/// Bedeli: bu tabloda tüm kiracıların e-posta adresleri bir arada durur.
/// Bu yüzden hiçbir API ucu bu tabloyu dışarı açmaz; yalnızca giriş akışı
/// içinden sayım amacıyla okunur.
/// </summary>
public class GirisDenemesi : VarlikTemel
{
    /// <summary>Denenen firma kısa adı. Var olmayan bir firma da kaydedilir.</summary>
    public string? FirmaSlug { get; set; }

    public required string Eposta { get; set; }
    public string? Ip { get; set; }
    public string? Tarayici { get; set; }

    public bool Basarili { get; set; }
    public DateTimeOffset Zaman { get; set; } = DateTimeOffset.UtcNow;
}
