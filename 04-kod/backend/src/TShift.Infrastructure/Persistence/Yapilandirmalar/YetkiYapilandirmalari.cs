using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using TShift.Domain.Yetki;
using TShift.Infrastructure.Yetki;

namespace TShift.Infrastructure.Persistence.Yapilandirmalar;

public class RolYapilandirmasi : IEntityTypeConfiguration<Rol>
{
    public void Configure(EntityTypeBuilder<Rol> b)
    {
        b.ToTable("roles");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.KiraciId).HasColumnName("tenant_id").IsRequired();
        b.Property(x => x.Kod).HasColumnName("kod").HasMaxLength(60).IsRequired();
        b.Property(x => x.Ad).HasColumnName("ad").HasMaxLength(120).IsRequired();
        b.Property(x => x.Kapsam).HasColumnName("kapsam").HasConversion<short>();
        b.Property(x => x.SistemMi).HasColumnName("sistem_mi");
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");

        b.HasIndex(x => new { x.KiraciId, x.Kod }).IsUnique().HasDatabaseName("ux_roles_tenant_kod");
        b.HasOne<TShift.Domain.Kiracilar.Kiraci>().WithMany()
            .HasForeignKey(x => x.KiraciId).OnDelete(DeleteBehavior.Cascade);
    }
}

public class IzinYapilandirmasi : IEntityTypeConfiguration<Izin>
{
    public void Configure(EntityTypeBuilder<Izin> b)
    {
        b.ToTable("permissions");
        b.HasKey(x => x.Kod);
        b.Property(x => x.Kod).HasColumnName("kod").HasMaxLength(60);
        b.Property(x => x.Aciklama).HasColumnName("aciklama").HasMaxLength(300).IsRequired();
        b.Property(x => x.Kategori).HasColumnName("kategori").HasMaxLength(60).IsRequired();

        // Katalog kodda tanımlı; migration ile veritabanına da yazılıyor.
        // Böylece role_permissions yabancı anahtarla bağlanabiliyor ve
        // uydurma bir izin kodu yazmak veritabanı seviyesinde imkânsız oluyor.
        b.HasData(YetkiKatalogu.Izinler.Select(i => new Izin
        {
            Kod = i.Kod, Aciklama = i.Aciklama, Kategori = i.Kategori
        }));
    }
}

public class RolIzniYapilandirmasi : IEntityTypeConfiguration<RolIzni>
{
    public void Configure(EntityTypeBuilder<RolIzni> b)
    {
        b.ToTable("role_permissions");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.KiraciId).HasColumnName("tenant_id").IsRequired();
        b.Property(x => x.RolId).HasColumnName("role_id").IsRequired();
        b.Property(x => x.IzinKodu).HasColumnName("permission_kod").HasMaxLength(60).IsRequired();
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");

        b.HasIndex(x => new { x.RolId, x.IzinKodu }).IsUnique().HasDatabaseName("ux_role_permissions");

        b.HasOne<Rol>().WithMany().HasForeignKey(x => x.RolId).OnDelete(DeleteBehavior.Cascade);
        b.HasOne<Izin>().WithMany().HasForeignKey(x => x.IzinKodu).OnDelete(DeleteBehavior.Restrict);
        b.HasOne<TShift.Domain.Kiracilar.Kiraci>().WithMany()
            .HasForeignKey(x => x.KiraciId).OnDelete(DeleteBehavior.Cascade);
    }
}

public class KullaniciRoluYapilandirmasi : IEntityTypeConfiguration<KullaniciRolu>
{
    public void Configure(EntityTypeBuilder<KullaniciRolu> b)
    {
        b.ToTable("user_roles");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.KiraciId).HasColumnName("tenant_id").IsRequired();
        b.Property(x => x.KullaniciId).HasColumnName("user_id").IsRequired();
        b.Property(x => x.RolId).HasColumnName("role_id").IsRequired();
        b.Property(x => x.GecerlilikBas).HasColumnName("gecerlilik_bas");
        b.Property(x => x.GecerlilikBitis).HasColumnName("gecerlilik_bitis");
        b.Property(x => x.VerenKullaniciId).HasColumnName("veren_user_id");
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");

        b.HasIndex(x => x.KullaniciId).HasDatabaseName("ix_user_roles_user");

        b.HasOne<TShift.Domain.Kimlik.Kullanici>().WithMany()
            .HasForeignKey(x => x.KullaniciId).OnDelete(DeleteBehavior.Cascade);
        b.HasOne<Rol>().WithMany().HasForeignKey(x => x.RolId).OnDelete(DeleteBehavior.Cascade);
        b.HasOne<TShift.Domain.Kiracilar.Kiraci>().WithMany()
            .HasForeignKey(x => x.KiraciId).OnDelete(DeleteBehavior.Cascade);
    }
}

public class KullaniciKapsamiYapilandirmasi : IEntityTypeConfiguration<KullaniciKapsami>
{
    public void Configure(EntityTypeBuilder<KullaniciKapsami> b)
    {
        b.ToTable("user_scopes");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.KiraciId).HasColumnName("tenant_id").IsRequired();
        b.Property(x => x.KullaniciId).HasColumnName("user_id").IsRequired();
        b.Property(x => x.Tip).HasColumnName("kapsam_tipi").HasConversion<short>();
        b.Property(x => x.HedefId).HasColumnName("kapsam_id").IsRequired();
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");

        b.HasIndex(x => new { x.KullaniciId, x.Tip, x.HedefId })
            .IsUnique().HasDatabaseName("ux_user_scopes");

        b.HasOne<TShift.Domain.Kimlik.Kullanici>().WithMany()
            .HasForeignKey(x => x.KullaniciId).OnDelete(DeleteBehavior.Cascade);
        b.HasOne<TShift.Domain.Kiracilar.Kiraci>().WithMany()
            .HasForeignKey(x => x.KiraciId).OnDelete(DeleteBehavior.Cascade);
    }
}
