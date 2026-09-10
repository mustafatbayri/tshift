-- =============================================================================
-- TShift - Satir seviyesi guvenlik (Row Level Security)
--
-- NEDEN: Cok kiraciliktaki bir numarali felaket, bir sorguda tenant_id
-- filtresinin unutulmasi ve A firmasinin B firmasinin verisini gormesidir.
-- Uygulama katmani (EF sorgu filtresi) ilk savunma; bu dosya IKINCISI.
-- Uygulama hata yapsa bile veritabani baska kiracinin satirini dondurmez.
--
-- NASIL: Her istek acilan baglantida `app.tenant_id` oturum degiskeni yazilir
-- (KiraciBaglantiKesici.cs). Asagidaki politikalar o degiskeni okur.
--
-- FORCE: `tshift` kullanicisi tablolarin sahibi. PostgreSQL varsayilaninda tablo
-- sahibi RLS'ten muaftir. FORCE ile sahibi de kapsama aliyoruz - yoksa
-- guvenlik yalnizca kagit uzerinde kalirdi.
--
-- NOT: Bu betik simdilik elle calistiriliyor. Kimlik adiminda EF migration'a
-- tasinacak ki surum kontrolunde ve otomatik olsun.
-- =============================================================================

CREATE OR REPLACE FUNCTION app_tenant_id() RETURNS uuid
LANGUAGE sql STABLE AS $$
  SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid
$$;

DO $$
DECLARE
  t text;
  tablolar text[] := ARRAY['users','departments','teams','employees','employee_contracts'];
BEGIN
  FOREACH t IN ARRAY tablolar LOOP
    IF to_regclass('public.' || t) IS NULL THEN
      RAISE NOTICE 'Tablo yok, atlaniyor: %', t;
      CONTINUE;
    END IF;

    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format('ALTER TABLE public.%I FORCE ROW LEVEL SECURITY', t);
    EXECUTE format('DROP POLICY IF EXISTS kiraci_yalitimi ON public.%I', t);
    EXECUTE format($p$
      CREATE POLICY kiraci_yalitimi ON public.%I
      USING (tenant_id = app_tenant_id())
      WITH CHECK (tenant_id = app_tenant_id())
    $p$, t);

    RAISE NOTICE 'RLS acildi: %', t;
  END LOOP;
END $$;

-- Kontrol: her tablo icin rowsecurity ve forcerowsecurity true olmali
SELECT relname AS tablo, relrowsecurity AS rls_acik, relforcerowsecurity AS sahibe_de_uygula
FROM pg_class
WHERE relname IN ('users','departments','teams','employees','employee_contracts')
ORDER BY relname;
