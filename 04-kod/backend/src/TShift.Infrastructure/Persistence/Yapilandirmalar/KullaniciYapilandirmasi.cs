using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using TShift.Domain.Kimlik;

namespace TShift.Infrastructure.Persistence.Yapilandirmalar;

public class KullaniciYapilandirmasi : IEntityTypeConfiguration<Kullanici>
{
    public void Configure(EntityTypeBuilder<Kullanici> b)
    {
        b.ToTable("users");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.KiraciId).HasColumnName("tenant_id").IsRequired();
        b.Property(x => x.Ad).HasColumnName("ad").HasMaxLength(100).IsRequired();
        b.Property(x => x.Soyad).HasColumnName("soyad").HasMaxLength(100).IsRequired();
        // citext: büyük/küçük harf duyarsız e-posta (01-init.sql'de kuruldu)
        b.Property(x => x.Eposta).HasColumnName("eposta").HasColumnType("citext").IsRequired();
        b.Property(x => x.EpostaDogrulandi).HasColumnName("eposta_dogrulandi");
        b.Property(x => x.Telefon).HasColumnName("telefon").HasMaxLength(30);
        b.Property(x => x.CalisanId).HasColumnName("employee_id");
        b.Property(x => x.MfaAktif).HasColumnName("mfa_aktif");
        b.Property(x => x.BasarisizGiris).HasColumnName("basarisiz_giris");
        b.Property(x => x.KilitBitis).HasColumnName("kilit_bitis");
        b.Property(x => x.DisKimlikSaglayici).HasColumnName("dis_kimlik_saglayici").HasMaxLength(60);
        b.Property(x => x.DisKimlikId).HasColumnName("dis_kimlik_id").HasMaxLength(200);
        b.Property(x => x.Durum).HasColumnName("durum").HasConversion<short>();
        b.Property(x => x.SonGiris).HasColumnName("son_giris");
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");

        b.HasIndex(x => new { x.KiraciId, x.Eposta }).IsUnique().HasDatabaseName("ux_users_tenant_eposta");
        b.HasOne<TShift.Domain.Kiracilar.Kiraci>().WithMany()
            .HasForeignKey(x => x.KiraciId).OnDelete(DeleteBehavior.Cascade);
    }
}
