import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import { apiAdresi, istemciBasliklari, ERISIM_CEREZ } from "@/lib/api";

/**
 * Yeni çalışan kaydı. Tarayıcı doğrudan API'ye gitmiyor; buradan geçiyor,
 * çünkü jeton yalnızca sunucudaki çerezde duruyor.
 *
 * Burada HİÇBİR yetki kontrolü yok ve olmamalı: kim ne yapabilir kararı
 * API'nin işi. Buradan bir kontrol koymak, aynı kuralın ikinci bir kopyası
 * olurdu ve zamanla asıl kuraldan ayrışırdı.
 */
export async function POST(istek: NextRequest) {
  const kavanoz = await cookies();
  const jeton = kavanoz.get(ERISIM_CEREZ)?.value;

  if (!jeton) {
    return NextResponse.json({ mesaj: "Oturum bulunamadi." }, { status: 401 });
  }

  const govde = await istek.json();

  const cevap = await fetch(`${apiAdresi()}/api/v1/employees`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${jeton}`,
      ...(await istemciBasliklari()),   // T-35
    },
    body: JSON.stringify(govde),
    cache: "no-store",
  });

  const sonuc = await cevap.json().catch(() => null);
  return NextResponse.json(sonuc ?? { mesaj: "Kayit olusturulamadi." }, {
    status: cevap.status,
  });
}
