using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using TShift.Domain.Denetim;

namespace TShift.Infrastructure.Persistence.Yapilandirmalar;

public class DenetimKaydiYapilandirmasi : IEntityTypeConfiguration<DenetimKaydi>
{
    public void Configure(EntityTypeBuilder<DenetimKaydi> b)
    {
        b.ToTable("audit_log");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.KiraciId).HasColumnName("tenant_id").IsRequired();
        b.Property(x => x.KullaniciId).HasColumnName("user_id");
        b.Property(x => x.Varlik).HasColumnName("varlik").HasMaxLength(80).IsRequired();
        b.Property(x => x.VarlikId).HasColumnName("varlik_id").IsRequired();
        b.Property(x => x.Islem).HasColumnName("islem").HasConversion<short>();
        b.Property(x => x.Oncesi).HasColumnName("oncesi").HasColumnType("jsonb");
        b.Property(x => x.Sonrasi).HasColumnName("sonrasi").HasColumnType("jsonb");
        b.Property(x => x.Ip).HasColumnName("ip").HasMaxLength(60);
        b.Property(x => x.Tarayici).HasColumnName("user_agent").HasMaxLength(400);
        b.Property(x => x.Zaman).HasColumnName("zaman");
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");

        // "Bu kaydın gecmisi" sorgusu bu indeksle calisir.
        b.HasIndex(x => new { x.Varlik, x.VarlikId, x.Zaman })
            .HasDatabaseName("ix_audit_varlik");
        // "Bu kullanici neler yapti" sorgusu.
        b.HasIndex(x => new { x.KullaniciId, x.Zaman })
            .HasDatabaseName("ix_audit_kullanici");
        // Zaman araligi taramasi.
        b.HasIndex(x => x.Zaman).HasDatabaseName("ix_audit_zaman");

        // DIKKAT: user_id icin yabanci anahtar YOK.
        // Sebep: kullanici silinirse denetim kaydi da silinir ya da bloke olur.
        // Ikisi de istenmez - denetim kaydi, kaydettigi kisiden UZUN yasamali.
        // Silinen kullanicinin kimligi kayitta durur; kim oldugu ayrica aranir.
        b.HasOne<TShift.Domain.Kiracilar.Kiraci>().WithMany()
            .HasForeignKey(x => x.KiraciId).OnDelete(DeleteBehavior.Cascade);
    }
}
