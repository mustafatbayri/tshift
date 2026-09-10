namespace TShift.Infrastructure.Kimlik;

/// <summary>
/// Kimlik katmanının ayarları. Spec §7.4 tablosundaki değerler.
/// Sırlar buraya YAZILMAZ — ortam değişkeninden gelir.
/// </summary>
public sealed class KimlikAyarlari
{
    /// <summary>JWT imza anahtarı. En az 32 bayt. Ortam değişkeni: JWT_SECRET.</summary>
    public required string ImzaAnahtari { get; init; }

    public string Yayinci { get; init; } = "tshift";
    public string Hedef { get; init; } = "tshift-api";

    /// <summary>Erişim jetonu ömrü. Spec: 15 dakika.</summary>
    public TimeSpan ErisimOmru { get; init; } = TimeSpan.FromMinutes(15);

    /// <summary>Yenileme jetonu ömrü. Spec: 30 gün.</summary>
    public TimeSpan YenilemeOmru { get; init; } = TimeSpan.FromDays(30);

    /// <summary>Kaba kuvvet: kaç başarısız denemeden sonra kilit. Spec: 5.</summary>
    public int KilitEsigi { get; init; } = 5;

    /// <summary>Kilit süresi ve sayım penceresi. Spec: 15 dakika.</summary>
    public TimeSpan KilitSuresi { get; init; } = TimeSpan.FromMinutes(15);

    /// <summary>Parola politikası: en az uzunluk. Spec: 10.</summary>
    public int AsgariParolaUzunlugu { get; init; } = 10;
}
