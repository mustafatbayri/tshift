import { redirect } from "next/navigation";
import { apiGet, ULASILAMADI } from "@/lib/api";
import type { Ben, CalisanListesi, Secenek } from "@/lib/tipler";
import CikisDugmesi from "./cikis-dugmesi";
import YeniCalisan from "./yeni-calisan";

const KAPSAM_METNI: Record<string, string> = {
  Kiraci: "Tum firma",
  Kapsam: "Yalniz kendi departman/ekipleri",
  Kendi: "Yalniz kendi kaydi",
};

export default async function CalisanlarSayfasi() {
  const [ben, liste, departmanlar, ekipler] = await Promise.all([
    apiGet<Ben>("/api/v1/me"),
    apiGet<CalisanListesi>("/api/v1/employees"),
    apiGet<Secenek[]>("/api/v1/departments"),
    apiGet<Secenek[]>("/api/v1/teams"),
  ]);

  // Arka uca hiç ulaşılamadı. Bu bir yetki sorunu değil, bir çalıştırma sorunu —
  // kullanıcıya da öyle anlatmak gerekir.
  if (ben.durum === ULASILAMADI || liste.durum === ULASILAMADI) {
    return (
      <Kabuk ben={null}>
        <Uyari
          baslik="Arka uca ulasilamiyor"
          metin="API calismiyor gorunuyor. Ayri bir pencerede `dotnet run` ile baslat, ya da `docker compose --profile tam up` ile tum yigini ayaga kaldir."
        />
      </Kabuk>
    );
  }

  // Erişim jetonunun süresi dolmuş. Yenileme adresine uğrayıp geri dönüyoruz;
  // kullanıcı bunu fark etmiyor. Yenileme de başarısızsa oradan giriş
  // sayfasına yönlendirilecek.
  if (ben.durum === 401 || liste.durum === 401) {
    redirect("/api/yenile?geri=/calisanlar");
  }

  // 403, 401'den farklı bir şey söylüyor: kim olduğun belli, ama bu ekranı
  // görme iznin yok. Kullanıcıya da böyle anlatmak gerekir.
  if (liste.durum === 403) {
    return (
      <Kabuk ben={ben.veri}>
        <Uyari
          baslik="Bu ekrani gorme yetkin yok"
          metin="Calisan listesi icin `calisan.gor` izni gerekiyor. Firma yoneticinden isteyebilirsin."
        />
      </Kabuk>
    );
  }

  if (!ben.veri || !liste.veri) {
    return (
      <Kabuk ben={ben.veri}>
        <Uyari
          baslik="Veri alinamadi"
          metin="API'ye ulasilamadi. Arka ucun calistigindan emin ol."
        />
      </Kabuk>
    );
  }

  const { kapsam, adet, kayitlar } = liste.veri;

  return (
    <Kabuk ben={ben.veri}>
      <div className="mb-6 flex items-end justify-between">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">Calisanlar</h2>
          <p className="mt-1 text-sm text-[var(--gri)]">
            {adet} kayit &middot; {KAPSAM_METNI[kapsam] ?? kapsam}
          </p>
        </div>

        {/* Yetkisi olmayana buton gösterilmiyor. Bu bir güvenlik önlemi DEĞİL —
            asıl kontrol sunucuda. Kullanıcıyı yapamayacağı bir işle
            uğraştırmamak için. */}
        {ben.veri.izinler.includes("calisan.duzenle") && (
          <YeniCalisan
            departmanlar={departmanlar.veri ?? []}
            ekipler={ekipler.veri ?? []}
          />
        )}
      </div>

      {kayitlar.length === 0 ? (
        <Uyari
          baslik="Gorunen calisan yok"
          metin="Kapsamin icinde kayitli calisan bulunmuyor. Kapsam atamasi eksikse firma yoneticisi ekleyebilir."
        />
      ) : (
        <div className="overflow-hidden rounded-xl border border-[var(--cizgi)] bg-white">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--cizgi)] bg-[var(--zemin)] text-left text-xs uppercase tracking-wide text-[var(--gri)]">
                <th className="px-4 py-3 font-medium">Personel no</th>
                <th className="px-4 py-3 font-medium">Ad soyad</th>
                <th className="px-4 py-3 font-medium">E-posta</th>
              </tr>
            </thead>
            <tbody>
              {kayitlar.map((c) => (
                <tr
                  key={c.id}
                  className="border-b border-[var(--cizgi)] last:border-0 hover:bg-[var(--brand-soft)]/40"
                >
                  <td className="px-4 py-3 font-mono text-xs text-[var(--gri)]">
                    {c.personelNo}
                  </td>
                  <td className="px-4 py-3 font-medium">{c.tamAd}</td>
                  <td className="px-4 py-3 text-[var(--gri)]">{c.eposta ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Izinler izinler={ben.veri.izinler} />
    </Kabuk>
  );
}

function Kabuk({ ben, children }: { ben: Ben | null; children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="border-b border-[var(--cizgi)] bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
          {/* Rozetin icinde zaten "T-Shift by TEKNOVISOR" yaziyor.
              Yanina bir daha yazmak tekrar olurdu. */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/tshift.png"
            alt="T-Shift"
            width={72}
            height={82}
            className="rounded-2xl shadow-sm"
          />

          {ben && (
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm font-medium">
                  {ben.ad} {ben.soyad}
                </div>
                <div className="text-xs text-[var(--gri)]">{ben.eposta}</div>
              </div>
              <CikisDugmesi />
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-8">{children}</main>
    </div>
  );
}

function Uyari({ baslik, metin }: { baslik: string; metin: string }) {
  return (
    <div className="rounded-xl border border-[var(--cizgi)] bg-white p-8 text-center">
      <p className="font-medium">{baslik}</p>
      <p className="mx-auto mt-1 max-w-md text-sm text-[var(--gri)]">{metin}</p>
    </div>
  );
}

/**
 * Bu bölüm kalıcı bir ürün özelliği değil — dikey dilim boyunca yetkinin
 * gerçekten çalıştığını gözle görebilmek için duruyor. Gerçek ekranlarda
 * kullanıcı izin kodlarını görmez; menüde neyin görünüp görünmediğinden anlar.
 */
function Izinler({ izinler }: { izinler: string[] }) {
  return (
    <details className="mt-8 rounded-xl border border-[var(--cizgi)] bg-white p-4">
      <summary className="cursor-pointer text-sm font-medium text-[var(--gri)]">
        Bu kullanicinin izinleri ({izinler.length})
      </summary>
      <div className="mt-3 flex flex-wrap gap-1.5">
        {izinler.map((i) => (
          <span
            key={i}
            className="rounded-md bg-[var(--brand-soft)] px-2 py-1 font-mono text-xs text-[var(--brand-ink)]"
          >
            {i}
          </span>
        ))}
      </div>
    </details>
  );
}
