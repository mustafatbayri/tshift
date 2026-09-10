using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using TShift.Domain.Kimlik;

namespace TShift.Infrastructure.Persistence.Yapilandirmalar;

public class KullaniciKimlikBilgisiYapilandirmasi : IEntityTypeConfiguration<KullaniciKimlikBilgisi>
{
    public void Configure(EntityTypeBuilder<KullaniciKimlikBilgisi> b)
    {
        b.ToTable("user_credentials");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.KiraciId).HasColumnName("tenant_id").IsRequired();
        b.Property(x => x.KullaniciId).HasColumnName("user_id").IsRequired();
        b.Property(x => x.SifreHash).HasColumnName("sifre_hash").HasMaxLength(400).IsRequired();
        b.Property(x => x.Algoritma).HasColumnName("algoritma").HasMaxLength(30).IsRequired();
        b.Property(x => x.DegisimZamani).HasColumnName("degisim_zamani");
        b.Property(x => x.ZorunluDegisim).HasColumnName("zorunlu_degisim");
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");

        // Kullanıcı başına tek parola kaydı.
        b.HasIndex(x => x.KullaniciId).IsUnique().HasDatabaseName("ux_user_credentials_user");

        b.HasOne<Kullanici>().WithMany()
            .HasForeignKey(x => x.KullaniciId).OnDelete(DeleteBehavior.Cascade);
        b.HasOne<TShift.Domain.Kiracilar.Kiraci>().WithMany()
            .HasForeignKey(x => x.KiraciId).OnDelete(DeleteBehavior.Cascade);
    }
}
