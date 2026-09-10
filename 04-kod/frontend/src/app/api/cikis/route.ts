import { NextRequest, NextResponse } from "next/server";
import { apiAdresi, ERISIM_CEREZ, YENILEME_CEREZ } from "@/lib/api";

/**
 * Çıkış. İki iş yapıyor ve ikisi de gerekli:
 *   1. Sunucudaki yenileme jetonunu iptal ediyor.
 *   2. Tarayıcıdaki çerezleri siliyor.
 *
 * Yalnız çerezi silmek yetmez: jeton sunucuda geçerli kalır ve bir kopyası
 * ele geçmişse çalışmaya devam eder. "Çıkış yaptım" demek, jetonun ölmesi
 * demek olmalı.
 */
export async function POST(istek: NextRequest) {
  const yenileme = istek.cookies.get(YENILEME_CEREZ)?.value;

  if (yenileme) {
    await fetch(`${apiAdresi()}/api/v1/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ yenilemeJetonu: yenileme }),
      cache: "no-store",
    }).catch(() => {
      // Sunucuya ulaşılamasa bile çerezleri silmeye devam ediyoruz:
      // kullanıcı açısından çıkış yapılmış olmalı.
    });
  }

  const sonuc = NextResponse.json({ tamam: true });
  sonuc.cookies.delete(ERISIM_CEREZ);
  sonuc.cookies.delete(YENILEME_CEREZ);
  return sonuc;
}
