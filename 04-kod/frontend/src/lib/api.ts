import { cookies, headers } from "next/headers";

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

/**
 * `durum: 0` = API'ye HİÇ ulaşılamadı (kapalı, yanlış port, ağ yok).
 * HTTP durum kodlarıyla karışmaz, çünkü 0 diye bir HTTP kodu yoktur.
 *
 * Bunu ayrı tutmak önemli: 401 "kimliğini bilmiyorum", 403 "yetkin yok",
 * 0 ise "sunucu orada değil". Üçü farklı sorun, üçünün çözümü farklı.
 */
export const ULASILAMADI = 0;

/**
 * API'ye iletilecek istemci kimliği başlıkları (T-35).
 *
 * NEDEN GEREKLİ:
 * Tarayıcı API'ye hiç gitmiyor; her istek Next.js üzerinden geçiyor. Bu
 * sayfanın en başında anlatılan fayda (jeton tarayıcıya hiç inmiyor) bir
 * yan etki üretiyordu: API'nin gördüğü adres HER ZAMAN bu sunucunun adresi.
 *
 * Sonucu ölçüldü: kaba kuvvet kilidi IP'ye de bakıyor ve o sorguda kiracı
 * filtresi yok (M-13, bilerek). Herkes tek adresten geliyor gibi görününce
 * herhangi bir kiracıda 5 yanlış parola KURULUMDAKİ HERKESİ kilitliyordu.
 * Denetim kaydındaki her IP de bu sunucunun adresiydi.
 *
 * GÜVENLİK NOTU: burada gönderilen başlığa API körlemesine GÜVENMEZ.
 * Yalnızca `TSHIFT_GUVENILEN_VEKILLER` listesindeki adreslerden geldiğinde
 * okur. Yani bu satır tek başına bir açık değil; listeyle birlikte anlamlı.
 *
 * Yerel geliştirmede önünde vekil olmadığı için `x-forwarded-for` gelmez ve
 * hiçbir şey iletilmez — API o durumda bağlantı adresini kullanır.
 */
export async function istemciBasliklari(): Promise<Record<string, string>> {
  const gelen = await headers();
  const adres = gelen.get("x-forwarded-for") ?? gelen.get("x-real-ip");
  return adres ? { "X-Forwarded-For": adres } : {};
}

export async function apiGet<T>(yol: string): Promise<Cevap<T>> {
  const kavanoz = await cookies();
  const jeton = kavanoz.get(ERISIM_CEREZ)?.value;
  const istemci = await istemciBasliklari();

  let cevap: Response;
  try {
    cevap = await fetch(`${API}${yol}`, {
      headers: {
        ...istemci,
        ...(jeton ? { Authorization: `Bearer ${jeton}` } : {}),
      },
      // Her istek taze: vardiya verisi önbellekten servis edilmemeli.
      cache: "no-store",
    });
  } catch {
    // Ağ hatasını yukarı fırlatmıyoruz. Fırlatsaydık kullanıcı
    // "Runtime TypeError: fetch failed" görürdü — hiçbir şey anlatmayan,
    // üstelik uygulamada bir çökme varmış izlenimi veren bir mesaj.
    // Oysa olan şey basit: arka uç çalışmıyor.
    return { durum: ULASILAMADI, veri: null };
  }

  if (!cevap.ok) return { durum: cevap.status, veri: null };
  return { durum: cevap.status, veri: (await cevap.json()) as T };
}

export function apiAdresi() {
  return API;
}
