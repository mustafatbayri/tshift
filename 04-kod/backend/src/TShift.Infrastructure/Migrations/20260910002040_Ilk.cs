using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace TShift.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class Ilk : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "public");

            migrationBuilder.AlterDatabase()
                .Annotation("Npgsql:PostgresExtension:citext", ",,");

            migrationBuilder.CreateTable(
                name: "tenants",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    ad = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    slug = table.Column<string>(type: "character varying(80)", maxLength: 80, nullable: false),
                    sektor_paketi = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    birim_adi = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    zaman_dilimi = table.Column<string>(type: "character varying(60)", maxLength: 60, nullable: false),
                    hafta_baslangic = table.Column<short>(type: "smallint", nullable: false),
                    durum = table.Column<short>(type: "smallint", nullable: false),
                    deneme_bitis = table.Column<DateOnly>(type: "date", nullable: true),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_tenants", x => x.id);
                });

            migrationBuilder.CreateTable(
                name: "departments",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    ad = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    kod = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    ust_department_id = table.Column<Guid>(type: "uuid", nullable: true),
                    calisma_tipi = table.Column<short>(type: "smallint", nullable: false),
                    acilis_saat = table.Column<decimal>(type: "numeric(5,2)", precision: 5, scale: 2, nullable: true),
                    kapanis_saat = table.Column<decimal>(type: "numeric(5,2)", precision: 5, scale: 2, nullable: true),
                    aktif = table.Column<bool>(type: "boolean", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_departments", x => x.id);
                    table.ForeignKey(
                        name: "FK_departments_tenants_tenant_id",
                        column: x => x.tenant_id,
                        principalSchema: "public",
                        principalTable: "tenants",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "users",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    ad = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    soyad = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    eposta = table.Column<string>(type: "citext", nullable: false),
                    eposta_dogrulandi = table.Column<bool>(type: "boolean", nullable: false),
                    telefon = table.Column<string>(type: "character varying(30)", maxLength: 30, nullable: true),
                    employee_id = table.Column<Guid>(type: "uuid", nullable: true),
                    mfa_aktif = table.Column<bool>(type: "boolean", nullable: false),
                    basarisiz_giris = table.Column<short>(type: "smallint", nullable: false),
                    kilit_bitis = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true),
                    dis_kimlik_saglayici = table.Column<string>(type: "character varying(60)", maxLength: 60, nullable: true),
                    dis_kimlik_id = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: true),
                    durum = table.Column<short>(type: "smallint", nullable: false),
                    son_giris = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_users", x => x.id);
                    table.ForeignKey(
                        name: "FK_users_tenants_tenant_id",
                        column: x => x.tenant_id,
                        principalSchema: "public",
                        principalTable: "tenants",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "teams",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    department_id = table.Column<Guid>(type: "uuid", nullable: false),
                    ad = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    kod = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    aciklama = table.Column<string>(type: "character varying(500)", maxLength: 500, nullable: true),
                    aktif = table.Column<bool>(type: "boolean", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_teams", x => x.id);
                    table.ForeignKey(
                        name: "FK_teams_departments_department_id",
                        column: x => x.department_id,
                        principalSchema: "public",
                        principalTable: "departments",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "employees",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    personel_no = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    ad = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    soyad = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    eposta = table.Column<string>(type: "citext", nullable: true),
                    telefon = table.Column<string>(type: "character varying(30)", maxLength: 30, nullable: true),
                    department_id = table.Column<Guid>(type: "uuid", nullable: false),
                    birincil_team_id = table.Column<Guid>(type: "uuid", nullable: true),
                    ise_giris = table.Column<DateOnly>(type: "date", nullable: false),
                    isten_cikis = table.Column<DateOnly>(type: "date", nullable: true),
                    durum = table.Column<short>(type: "smallint", nullable: false),
                    user_id = table.Column<Guid>(type: "uuid", nullable: true),
                    dis_sistem_id = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: true),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_employees", x => x.id);
                    table.ForeignKey(
                        name: "FK_employees_departments_department_id",
                        column: x => x.department_id,
                        principalSchema: "public",
                        principalTable: "departments",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_employees_teams_birincil_team_id",
                        column: x => x.birincil_team_id,
                        principalSchema: "public",
                        principalTable: "teams",
                        principalColumn: "id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "employee_contracts",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    employee_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tip = table.Column<short>(type: "smallint", nullable: false),
                    haftalik_saat = table.Column<decimal>(type: "numeric(5,2)", precision: 5, scale: 2, nullable: false),
                    gunluk_azami_saat = table.Column<decimal>(type: "numeric(5,2)", precision: 5, scale: 2, nullable: true),
                    baslangic = table.Column<DateOnly>(type: "date", nullable: false),
                    bitis = table.Column<DateOnly>(type: "date", nullable: true),
                    aktif = table.Column<bool>(type: "boolean", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_employee_contracts", x => x.id);
                    table.ForeignKey(
                        name: "FK_employee_contracts_employees_employee_id",
                        column: x => x.employee_id,
                        principalSchema: "public",
                        principalTable: "employees",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "ux_departments_tenant_kod",
                schema: "public",
                table: "departments",
                columns: new[] { "tenant_id", "kod" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "ix_contracts_employee_aktif",
                schema: "public",
                table: "employee_contracts",
                columns: new[] { "employee_id", "aktif" });

            migrationBuilder.CreateIndex(
                name: "IX_employees_birincil_team_id",
                schema: "public",
                table: "employees",
                column: "birincil_team_id");

            migrationBuilder.CreateIndex(
                name: "IX_employees_department_id",
                schema: "public",
                table: "employees",
                column: "department_id");

            migrationBuilder.CreateIndex(
                name: "ix_employees_tenant_dept_durum",
                schema: "public",
                table: "employees",
                columns: new[] { "tenant_id", "department_id", "durum" });

            migrationBuilder.CreateIndex(
                name: "ux_employees_tenant_personel_no",
                schema: "public",
                table: "employees",
                columns: new[] { "tenant_id", "personel_no" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_teams_department_id",
                schema: "public",
                table: "teams",
                column: "department_id");

            migrationBuilder.CreateIndex(
                name: "ux_teams_tenant_kod",
                schema: "public",
                table: "teams",
                columns: new[] { "tenant_id", "kod" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "ux_tenants_slug",
                schema: "public",
                table: "tenants",
                column: "slug",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "ux_users_tenant_eposta",
                schema: "public",
                table: "users",
                columns: new[] { "tenant_id", "eposta" },
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "employee_contracts",
                schema: "public");

            migrationBuilder.DropTable(
                name: "users",
                schema: "public");

            migrationBuilder.DropTable(
                name: "employees",
                schema: "public");

            migrationBuilder.DropTable(
                name: "teams",
                schema: "public");

            migrationBuilder.DropTable(
                name: "departments",
                schema: "public");

            migrationBuilder.DropTable(
                name: "tenants",
                schema: "public");
        }
    }
}
