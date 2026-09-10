-- =============================================================================
-- 05 — DENETİM KAYDI: satır seviyesi güvenlik + SADECE EKLENİR
--
-- Migration çalıştıktan SONRA, `tshift` kullanıcısıyla çalıştır.
--
-- Bu betiğin ikinci yarısı bu projedeki en önemli birkaç satırdan biri.
-- =============================================================================

-- ---- 1) Kiracı yalıtımı -----------------------------------------------------
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log FORCE  ROW LEVEL SECURITY;
DROP POLICY IF EXISTS kiraci_yalitimi ON audit_log;
CREATE POLICY kiraci_yalitimi ON audit_log
    USING (tenant_id = app_tenant_id())
    WITH CHECK (tenant_id = app_tenant_id());

-- ---- 2) SADECE EKLENİR ------------------------------------------------------
--
-- Uygulama rolü denetim kaydına satır YAZABİLİR, ama yazılmış bir satırı
-- DEĞİŞTİREMEZ ve SİLEMEZ.
--
-- Neden bu kadar önemli: değiştirilebilen bir denetim kaydı, denetim kaydı
-- değildir. Uygulamada bir açık bulan biri, önce istediğini yapar sonra izini
-- siler; kayıt bir şey ifade etmez hale gelir. Yetkiyi uygulama katmanında
-- değil, VERİTABANINDA kapatıyoruz — çünkü uygulama katmanı, açığın bulunduğu
-- katmandır.
--
-- Bu kısıt uygulama kodunun doğru davranmasına GÜVENMEZ. Kod hatalı olsa,
-- hatta kötü niyetli olsa bile veritabanı UPDATE ve DELETE'i reddeder.
--
-- Saklama süresi dolduğunda temizlik gerekirse, bunu sahibi rol (`tshift`)
-- bilinçli ve kayıtlı bir bakım işiyle yapar — uygulama asla.
GRANT  SELECT, INSERT   ON audit_log TO tshift_app;
REVOKE UPDATE, DELETE   ON audit_log FROM tshift_app;

COMMENT ON TABLE audit_log IS
    'Denetim kaydi. SADECE EKLENIR: uygulama rolunun UPDATE/DELETE yetkisi yoktur. '
    'Bu kisit kasitlidir; kaldirmak denetim kaydini anlamsizlastirir.';

-- ---- 3) Kontrol -------------------------------------------------------------
-- Beklenen: SELECT ve INSERT var; UPDATE ve DELETE YOK.
SELECT privilege_type AS yetki
FROM   information_schema.table_privileges
WHERE  grantee = 'tshift_app' AND table_name = 'audit_log'
ORDER  BY privilege_type;

SELECT c.relname             AS tablo,
       c.relrowsecurity      AS rls_acik,
       c.relforcerowsecurity AS sahibe_de_uygula
FROM   pg_class c
JOIN   pg_namespace n ON n.oid = c.relnamespace
WHERE  n.nspname = 'public' AND c.relname = 'audit_log';
