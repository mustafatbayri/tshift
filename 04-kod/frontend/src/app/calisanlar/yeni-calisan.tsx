"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type Secenek = { id: string; ad: string; kod: string; departmanId?: string };

export default function YeniCalisan({
  departmanlar,
  ekipler,
}: {
  departmanlar: Secenek[];
  ekipler: Secenek[];
}) {
  const yonlendir = useRouter();
  const [acik, setAcik] = useState(false);

  return (
    <>
      <button
        onClick={() => setAcik(true)}
        className="rounded-lg bg-[var(--brand)] px-4 py-2 text-sm font-medium text-white transition hover:bg-[var(--brand-ink)]"
      >
        Yeni calisan
      </button>

      {acik && (
        <Modal
          departmanlar={departmanlar}
          ekipler={ekipler}
          kapat={() => setAcik(false)}
          bitti={() => {
            setAcik(false);
            // Sunucu bileşenini yeniden çalıştırır: liste tazelenir.
            yonlendir.refresh();
          }}
        />
      )}
    </>
  );
}

function Modal({
  departmanlar,
  ekipler,
  kapat,
  bitti,
}: {
  departmanlar: Secenek[];
  ekipler: Secenek[];
  kapat: () => void;
  bitti: () => void;
}) {
  const [form, setForm] = useState({
    personelNo: "",
    ad: "",
    soyad: "",
    eposta: "",
    telefon: "",
    departmanId: departmanlar[0]?.id ?? "",
    birincilEkipId: "",
    iseGiris: new Date().toISOString().slice(0, 10),
  });
  const [hata, setHata] = useState<string | null>(null);
  const [bekliyor, setBekliyor] = useState(false);

  // Ekip listesi seçilen departmana göre daralıyor. Sunucu da aynı kuralı
  // kontrol ediyor (EKIP_UYUMSUZ); buradaki daraltma yalnızca kullanıcıyı
  // yanlış seçim yapmaktan korumak için.
  const uygunEkipler = ekipler.filter((e) => e.departmanId === form.departmanId);

  function degistir(alan: string, deger: string) {
    setForm((o) => ({
      ...o,
      [alan]: deger,
      // Departman değişince eski ekip seçimi geçersiz kalır.
      ...(alan === "departmanId" ? { birincilEkipId: "" } : {}),
    }));
  }

  async function gonder(e: React.FormEvent) {
    e.preventDefault();
    setHata(null);
    setBekliyor(true);

    const cevap = await fetch("/api/calisan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...form,
        eposta: form.eposta || null,
        telefon: form.telefon || null,
        birincilEkipId: form.birincilEkipId || null,
      }),
    });

    setBekliyor(false);

    if (!cevap.ok) {
      const g = await cevap.json().catch(() => null);
      setHata(g?.mesaj ?? "Kayit olusturulamadi.");
      return;
    }

    bitti();
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[var(--ink)]/40 p-4"
      onClick={kapat}
    >
      <div
        className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-5 flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold tracking-tight">Yeni calisan</h3>
            <p className="mt-0.5 text-sm text-[var(--gri)]">
              Yalniz kendi kapsamindaki departmanlar listeleniyor.
            </p>
          </div>
          <button
            onClick={kapat}
            className="rounded-lg px-2 py-1 text-xl leading-none text-[var(--gri)] hover:bg-[var(--zemin)]"
            aria-label="Kapat"
          >
            &times;
          </button>
        </div>

        <form onSubmit={gonder}>
          <div className="grid grid-cols-2 gap-3">
            <Alan etiket="Personel no" deger={form.personelNo}
              degistir={(d) => degistir("personelNo", d)} zorunlu />
            <Alan etiket="Ise giris" tip="date" deger={form.iseGiris}
              degistir={(d) => degistir("iseGiris", d)} zorunlu />
            <Alan etiket="Ad" deger={form.ad} degistir={(d) => degistir("ad", d)} zorunlu />
            <Alan etiket="Soyad" deger={form.soyad} degistir={(d) => degistir("soyad", d)} zorunlu />
            <Alan etiket="E-posta" tip="email" deger={form.eposta}
              degistir={(d) => degistir("eposta", d)} />
            <Alan etiket="Telefon" deger={form.telefon}
              degistir={(d) => degistir("telefon", d)} />
          </div>

          <Secim
            etiket="Departman"
            deger={form.departmanId}
            degistir={(d) => degistir("departmanId", d)}
            secenekler={departmanlar.map((d) => ({ deger: d.id, metin: `${d.ad} (${d.kod})` }))}
          />

          <Secim
            etiket="Birincil ekip"
            deger={form.birincilEkipId}
            degistir={(d) => degistir("birincilEkipId", d)}
            secenekler={[
              { deger: "", metin: "— ekip yok —" },
              ...uygunEkipler.map((e) => ({ deger: e.id, metin: `${e.ad} (${e.kod})` })),
            ]}
          />

          {hata && (
            <p className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{hata}</p>
          )}

          <div className="mt-2 flex justify-end gap-2">
            <button
              type="button"
              onClick={kapat}
              className="rounded-lg border border-[var(--cizgi)] px-4 py-2 text-sm text-[var(--gri)] hover:text-[var(--ink)]"
            >
              Vazgec
            </button>
            <button
              type="submit"
              disabled={bekliyor || !form.departmanId}
              className="rounded-lg bg-[var(--brand)] px-4 py-2 text-sm font-medium text-white transition hover:bg-[var(--brand-ink)] disabled:opacity-50"
            >
              {bekliyor ? "Kaydediliyor..." : "Kaydet"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function Alan({
  etiket, deger, degistir, tip = "text", zorunlu = false,
}: {
  etiket: string; deger: string; degistir: (d: string) => void;
  tip?: string; zorunlu?: boolean;
}) {
  return (
    <label className="mb-3 block">
      <span className="mb-1.5 block text-sm font-medium">{etiket}</span>
      <input
        type={tip}
        value={deger}
        required={zorunlu}
        onChange={(e) => degistir(e.target.value)}
        className="w-full rounded-lg border border-[var(--cizgi)] px-3 py-2 text-sm outline-none transition focus:border-[var(--brand)] focus:ring-2 focus:ring-[var(--brand-soft)]"
      />
    </label>
  );
}

function Secim({
  etiket, deger, degistir, secenekler,
}: {
  etiket: string; deger: string; degistir: (d: string) => void;
  secenekler: { deger: string; metin: string }[];
}) {
  return (
    <label className="mb-3 block">
      <span className="mb-1.5 block text-sm font-medium">{etiket}</span>
      <select
        value={deger}
        onChange={(e) => degistir(e.target.value)}
        className="w-full rounded-lg border border-[var(--cizgi)] bg-white px-3 py-2 text-sm outline-none transition focus:border-[var(--brand)] focus:ring-2 focus:ring-[var(--brand-soft)]"
      >
        {secenekler.map((s) => (
          <option key={s.deger} value={s.deger}>{s.metin}</option>
        ))}
      </select>
    </label>
  );
}
