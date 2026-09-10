import { cookies } from "next/headers";

/**
 * Backend'e sunucu tarafından istek atar.
 *
 * NEDEN SUNUCUDAN:
 * Jeton hiçbir zaman tarayıcıdaki JavaScript'e ulaşmıyor. `localStorage`'a
 * konsaydı, sayfada çalışan HERHANGİ bir betik onu okuyabilirdi — bir
 * bağımlılığa sızan kötü niyetli kod, bir XSS açığı, bir tarayıcı eklentisi.
 * Jetonlar `httpOnly` çerezde duruyor: tarayıcı isteğe ekliyor ama sayfa
 * kodu göremiyor.
 *
 * İkinci fayda: tarayıcı hiçbir zaman doğrudan API'ye gitmediği için CORS
 * ayarı gerekmiyor. Tarayıcı yalnız Next.js ile konuşuyor.
 */
const API = process.env.TSHIFT_API ?? "http://localhost:5146";

export const ERISIM_CEREZ = "tshift_erisim";
export const YENILEME_CEREZ = "tshift_yenileme";

export type Cevap<T> = { durum: number; veri: T | null };

export async function apiGet<T>(yol: string): Promise<Cevap<T>> {
  const kavanoz = await cookies();
  const jeton = kavanoz.get(ERISIM_CEREZ)?.value;

  const cevap = await fetch(`${API}${yol}`, {
    headers: jeton ? { Authorization: `Bearer ${jeton}` } : {},
    // Her istek taze: vardiya verisi önbellekten servis edilmemeli.
    cache: "no-store",
  });

  if (!cevap.ok) return { durum: cevap.status, veri: null };
  return { durum: cevap.status, veri: (await cevap.json()) as T };
}

export function apiAdresi() {
  return API;
}
