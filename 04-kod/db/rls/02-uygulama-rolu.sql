-- =============================================================================
-- 02 — UYGULAMA ROLÜ
--
-- NEDEN GEREKLİ?
-- PostgreSQL'de satır seviyesi güvenlik (RLS) **süper kullanıcıyı bağlamaz**.
-- Süper kullanıcı her satırı görür; ENABLE de FORCE de onu durdurmaz.
--
-- Docker imajı `POSTGRES_USER=tshift` kullanıcısını süper kullanıcı olarak
-- yaratır. Yani uygulamayı bu kullanıcıyla bağlarsak RLS yazmışız ama hiç
-- devreye girmiyor olur — güvenlik sadece kâğıt üstünde kalır.
--
-- Çözüm, üretimde de aynı olan çözüm: İKİ AYRI ROL.
--   tshift      → sahibi. Migration çalıştırır, tablo yaratır. RLS'i aşar.
--   tshift_app  → uygulamanın bağlandığı rol. Süper değil, RLS'e TABİ.
--
-- Bu betiği 01-rls.sql'den SONRA, `tshift` kullanıcısıyla çalıştır.
-- =============================================================================

-- ---- 1) Rolü oluştur (varsa dokunma) ---------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'tshift_app') THEN
        CREATE ROLE tshift_app
            LOGIN PASSWORD '{APP_DB_PASSWORD}'
            NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOINHERIT;
        RAISE NOTICE 'tshift_app rolu olusturuldu.';
    ELSE
        RAISE NOTICE 'tshift_app rolu zaten var, atlandi.';
    END IF;
END $$;

-- Süper yetki ve RLS muafiyeti kesinlikle kapalı olsun (rol önceden varsa diye).
ALTER ROLE tshift_app NOSUPERUSER NOBYPASSRLS;

-- T-34: parolayı da her koşulda eşitle. Rol daha önce ESKİ sabit parolayla
-- yaratılmış olabilir; yukarıdaki blok "zaten var" deyip atlar ve uygulama
-- artık ortam değişkeninden gelen parolayla bağlanamaz.
-- {APP_DB_PASSWORD} yer tutucusunu KurulumHizmeti doldurur.
ALTER ROLE tshift_app PASSWORD '{APP_DB_PASSWORD}';

-- ---- 2) Yetkiler ------------------------------------------------------------
-- Veri okuyup yazabilir; tablo yaratamaz, şema değiştiremez.
GRANT CONNECT ON DATABASE tshift TO tshift_app;
GRANT USAGE   ON SCHEMA public   TO tshift_app;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES    IN SCHEMA public TO tshift_app;
GRANT USAGE, SELECT                  ON ALL SEQUENCES IN SCHEMA public TO tshift_app;

-- ---- 3) Gelecekteki tablolar ------------------------------------------------
-- Yeni migration yeni tablo yarattığında yetkiyi elle vermeyi unutmayalım diye.
ALTER DEFAULT PRIVILEGES FOR ROLE tshift IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO tshift_app;
ALTER DEFAULT PRIVILEGES FOR ROLE tshift IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO tshift_app;

-- ---- 4) Kontrol -------------------------------------------------------------
-- Beklenen: tshift → super=t · tshift_app → super=f, bypassrls=f
SELECT rolname          AS rol,
       rolsuper         AS super_kullanici,
       rolbypassrls     AS rls_muafiyeti,
       rolcanlogin      AS giris_yapabilir
FROM   pg_roles
WHERE  rolname IN ('tshift', 'tshift_app')
ORDER  BY rolname;
