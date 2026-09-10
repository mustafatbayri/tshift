using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using TShift.Domain.Kimlik;

namespace TShift.Infrastructure.Persistence.Yapilandirmalar;

public class YenilemeJetonuYapilandirmasi : IEntityTypeConfiguration<YenilemeJetonu>
{
    public void Configure(EntityTypeBuilder<YenilemeJetonu> b)
    {
        b.ToTable("refresh_tokens");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.KiraciId).HasColumnName("tenant_id").IsRequired();
        b.Property(x => x.KullaniciId).HasColumnName("user_id").IsRequired();
        b.Property(x => x.JetonOzeti).HasColumnName("token_hash").HasMaxLength(100).IsRequired();
        b.Property(x => x.OncekiJetonOzeti).HasColumnName("onceki_token_hash").HasMaxLength(100);
        b.Property(x => x.Cihaz).HasColumnName("cihaz").HasMaxLength(300);
        b.Property(x => x.Ip).HasColumnName("ip").HasMaxLength(60);
        b.Property(x => x.SonKullanim).HasColumnName("son_kullanim");
        b.Property(x => x.Bitis).HasColumnName("bitis");
        b.Property(x => x.IptalZamani).HasColumnName("iptal_zamani");
        b.Property(x => x.IptalSebebi).HasColumnName("iptal_sebebi").HasConversion<short?>();
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");

        // Özet benzersiz: aynı jeton iki kez yazılamaz.
        b.HasIndex(x => x.JetonOzeti).IsUnique().HasDatabaseName("ux_refresh_tokens_hash");
        // "Bu kullanıcının tüm oturumlarını düşür" sorgusu bu indeksle çalışır.
        b.HasIndex(x => new { x.KullaniciId, x.IptalZamani }).HasDatabaseName("ix_refresh_tokens_user");

        b.HasOne<Kullanici>().WithMany()
            .HasForeignKey(x => x.KullaniciId).OnDelete(DeleteBehavior.Cascade);
        b.HasOne<TShift.Domain.Kiracilar.Kiraci>().WithMany()
            .HasForeignKey(x => x.KiraciId).OnDelete(DeleteBehavior.Cascade);
    }
}
