using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

#pragma warning disable CA1814 // Prefer jagged arrays over multidimensional

namespace TShift.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class Yetki : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "permissions",
                schema: "public",
                columns: table => new
                {
                    kod = table.Column<string>(type: "character varying(60)", maxLength: 60, nullable: false),
                    aciklama = table.Column<string>(type: "character varying(300)", maxLength: 300, nullable: false),
                    kategori = table.Column<string>(type: "character varying(60)", maxLength: 60, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_permissions", x => x.kod);
                });

            migrationBuilder.CreateTable(
                name: "roles",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    kod = table.Column<string>(type: "character varying(60)", maxLength: 60, nullable: false),
                    ad = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    kapsam = table.Column<short>(type: "smallint", nullable: false),
                    sistem_mi = table.Column<bool>(type: "boolean", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_roles", x => x.id);
                    table.ForeignKey(
                        name: "FK_roles_tenants_tenant_id",
                        column: x => x.tenant_id,
                        principalSchema: "public",
                        principalTable: "tenants",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "user_scopes",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    kapsam_tipi = table.Column<short>(type: "smallint", nullable: false),
                    kapsam_id = table.Column<Guid>(type: "uuid", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_user_scopes", x => x.id);
                    table.ForeignKey(
                        name: "FK_user_scopes_tenants_tenant_id",
                        column: x => x.tenant_id,
                        principalSchema: "public",
                        principalTable: "tenants",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_user_scopes_users_user_id",
                        column: x => x.user_id,
                        principalSchema: "public",
                        principalTable: "users",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "role_permissions",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    role_id = table.Column<Guid>(type: "uuid", nullable: false),
                    permission_kod = table.Column<string>(type: "character varying(60)", maxLength: 60, nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_role_permissions", x => x.id);
                    table.ForeignKey(
                        name: "FK_role_permissions_permissions_permission_kod",
                        column: x => x.permission_kod,
                        principalSchema: "public",
                        principalTable: "permissions",
                        principalColumn: "kod",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_role_permissions_roles_role_id",
                        column: x => x.role_id,
                        principalSchema: "public",
                        principalTable: "roles",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_role_permissions_tenants_tenant_id",
                        column: x => x.tenant_id,
                        principalSchema: "public",
                        principalTable: "tenants",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "user_roles",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    role_id = table.Column<Guid>(type: "uuid", nullable: false),
                    gecerlilik_bas = table.Column<DateOnly>(type: "date", nullable: true),
                    gecerlilik_bitis = table.Column<DateOnly>(type: "date", nullable: true),
                    veren_user_id = table.Column<Guid>(type: "uuid", nullable: true),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_user_roles", x => x.id);
                    table.ForeignKey(
                        name: "FK_user_roles_roles_role_id",
                        column: x => x.role_id,
                        principalSchema: "public",
                        principalTable: "roles",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_user_roles_tenants_tenant_id",
                        column: x => x.tenant_id,
                        principalSchema: "public",
                        principalTable: "tenants",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_user_roles_users_user_id",
                        column: x => x.user_id,
                        principalSchema: "public",
                        principalTable: "users",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.InsertData(
                schema: "public",
                table: "permissions",
                columns: new[] { "kod", "aciklama", "kategori" },
                values: new object[,]
                {
                    { "calisan.duzenle", "Çalışan ekler ve düzenler", "Çalışan" },
                    { "calisan.gor", "Çalışan listesi ve detayını görür", "Çalışan" },
                    { "gerceklesen.yukle", "Gerçekleşen veri yükler", "Rapor" },
                    { "izin.gir", "Başkası adına izin girer", "İzin" },
                    { "izin.talep", "Kendi izin talebini oluşturur", "İzin" },
                    { "kullanici.yonet", "Kullanıcı ve yetki yönetir", "Yönetim" },
                    { "kural.istisna", "Kural istisnası tanımlar", "Kural" },
                    { "kural.parametre", "Kural parametrelerini değiştirir", "Kural" },
                    { "plan.duzenle", "Plan düzenler", "Plan" },
                    { "plan.onayla", "Planı onaylar", "Plan" },
                    { "plan.uret", "Plan üretir", "Plan" },
                    { "plan.yayinla", "Planı yayınlar", "Plan" },
                    { "rapor.gor", "Raporları görüntüler", "Rapor" },
                    { "sozlesme.duzenle", "Sözleşme bilgisi düzenler", "Çalışan" },
                    { "talep.gir", "Talep ve kapasite verisi girer", "Talep" },
                    { "uygunluk.gir", "Uygunluk kaydı girer", "İzin" },
                    { "vardiya.sablon", "Vardiya şablonu tanımlar", "Kural" },
                    { "yetkinlik.ata", "Çalışana yetkinlik atar", "Çalışan" }
                });

            migrationBuilder.CreateIndex(
                name: "IX_role_permissions_permission_kod",
                schema: "public",
                table: "role_permissions",
                column: "permission_kod");

            migrationBuilder.CreateIndex(
                name: "IX_role_permissions_tenant_id",
                schema: "public",
                table: "role_permissions",
                column: "tenant_id");

            migrationBuilder.CreateIndex(
                name: "ux_role_permissions",
                schema: "public",
                table: "role_permissions",
                columns: new[] { "role_id", "permission_kod" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "ux_roles_tenant_kod",
                schema: "public",
                table: "roles",
                columns: new[] { "tenant_id", "kod" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_user_roles_role_id",
                schema: "public",
                table: "user_roles",
                column: "role_id");

            migrationBuilder.CreateIndex(
                name: "IX_user_roles_tenant_id",
                schema: "public",
                table: "user_roles",
                column: "tenant_id");

            migrationBuilder.CreateIndex(
                name: "ix_user_roles_user",
                schema: "public",
                table: "user_roles",
                column: "user_id");

            migrationBuilder.CreateIndex(
                name: "IX_user_scopes_tenant_id",
                schema: "public",
                table: "user_scopes",
                column: "tenant_id");

            migrationBuilder.CreateIndex(
                name: "ux_user_scopes",
                schema: "public",
                table: "user_scopes",
                columns: new[] { "user_id", "kapsam_tipi", "kapsam_id" },
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "role_permissions",
                schema: "public");

            migrationBuilder.DropTable(
                name: "user_roles",
                schema: "public");

            migrationBuilder.DropTable(
                name: "user_scopes",
                schema: "public");

            migrationBuilder.DropTable(
                name: "permissions",
                schema: "public");

            migrationBuilder.DropTable(
                name: "roles",
                schema: "public");
        }
    }
}
