import { Suspense } from "react";
import GirisFormu from "./giris-formu";

/**
 * `useSearchParams` kullanan bir istemci bileşeni Suspense sınırı içinde
 * olmak zorunda: adres çubuğundaki parametreler sunucuda önceden bilinemez,
 * bu yüzden Next.js o parçayı ayrı ele almak ister. Sınır konmazsa derleme
 * hata verir.
 */
export default function GirisSayfasi() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-sm text-[var(--gri)]">Yukleniyor...</div>}>
      <GirisFormu />
    </Suspense>
  );
}
