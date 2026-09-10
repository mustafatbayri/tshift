import { NextRequest, NextResponse } from "next/server";

/**
 * Giriş yapmamış kullanıcıyı giriş sayfasına yollar.
 *
 * DİKKAT — bu bir GÜVENLİK sınırı DEĞİLDİR, bir KULLANICI DENEYİMİ
 * düzenlemesidir. Buradaki kontrol yalnızca çerezin VAR OLUP OLMADIĞINA
 * bakar; içeriğini doğrulamaz, doğrulayamaz da (imza anahtarı burada yok).
 *
 * Asıl kontrol API'de: jeton imzası orada doğrulanıyor, izinler orada
 * kontrol ediliyor, satır seviyesi güvenlik orada işliyor. Biri bu ara
 * katmanı tamamen atlasa bile hiçbir veriye ulaşamaz.
 *
 * Arayüzdeki gizleme her zaman böyledir: kullanıcıyı yapamayacağı şeylerle
 * uğraştırmamak içindir, onu durdurmak için değil.
 */
const ACIK_YOLLAR = ["/giris"];

export function proxy(istek: NextRequest) {
  const yol = istek.nextUrl.pathname;

  if (ACIK_YOLLAR.some((a) => yol.startsWith(a))) return NextResponse.next();

  const oturumVar =
    istek.cookies.has("tshift_erisim") || istek.cookies.has("tshift_yenileme");

  if (!oturumVar) {
    const url = new URL("/giris", istek.url);
    url.searchParams.set("geri", yol);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  // API adresleri ve statik dosyalar hariç her şey.
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
