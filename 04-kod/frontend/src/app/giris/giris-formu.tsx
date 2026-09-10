"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function GirisFormu() {
  const yonlendir = useRouter();
  const parametreler = useSearchParams();
  const geri = parametreler.get("geri") ?? "/calisanlar";
  const sebep = parametreler.get("sebep");

  const [firma, setFirma] = useState("anadolu-cm");
  const [eposta, setEposta] = useState("mudur@anadolu-cm.test");
  const [parola, setParola] = useState("");
  const [hata, setHata] = useState<string | null>(
    sebep === "oturum" ? "Oturumun sona erdi. Tekrar giris yap." : null
  );
  const [bekliyor, setBekliyor] = useState(false);

  async function gonder(e: React.FormEvent) {
    e.preventDefault();
    setHata(null);
    setBekliyor(true);

    const cevap = await fetch("/api/giris", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ firma, eposta, parola }),
    });

    setBekliyor(false);

    if (!cevap.ok) {
      const g = await cevap.json().catch(() => null);
      // API'nin belirsiz mesajını olduğu gibi gösteriyoruz. "E-posta bulunamadı"
      // demek, kayıtlı e-postaları tespit etmeyi mümkün kılardı.
      setHata(g?.mesaj ?? "Giris yapilamadi.");
      return;
    }

    yonlendir.push(geri);
    yonlendir.refresh();
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--brand)] text-lg font-bold text-white">
            TS
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-[var(--ink)]">
            TShift
          </h1>
          <p className="mt-1 text-sm text-[var(--gri)]">
            Vardiya planlama ve optimizasyon
          </p>
        </div>

        <form
          onSubmit={gonder}
          className="rounded-2xl border border-[var(--cizgi)] bg-white p-6 shadow-sm"
        >
          <Alan
            etiket="Firma"
            deger={firma}
            degistir={setFirma}
            ipucu="Canlida alan adindan gelecek; simdilik elle yaziliyor."
          />
          <Alan etiket="E-posta" tip="email" deger={eposta} degistir={setEposta} />
          <Alan etiket="Parola" tip="password" deger={parola} degistir={setParola} />

          {hata && (
            <p className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {hata}
            </p>
          )}

          <button
            type="submit"
            disabled={bekliyor}
            className="w-full rounded-lg bg-[var(--brand)] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[var(--brand-ink)] disabled:opacity-50"
          >
            {bekliyor ? "Giris yapiliyor..." : "Giris yap"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs leading-relaxed text-[var(--gri)]">
          Ornek kullanicilar: <code>mudur@</code>, <code>sef@</code>,{" "}
          <code>calisan@</code>, <code>izleyici@</code>
          <br />
          Ayni parola, farkli yetki. Fark listede gorunuyor.
        </p>
      </div>
    </main>
  );
}

function Alan({
  etiket,
  deger,
  degistir,
  tip = "text",
  ipucu,
}: {
  etiket: string;
  deger: string;
  degistir: (d: string) => void;
  tip?: string;
  ipucu?: string;
}) {
  return (
    <label className="mb-4 block">
      <span className="mb-1.5 block text-sm font-medium text-[var(--ink)]">
        {etiket}
      </span>
      <input
        type={tip}
        value={deger}
        onChange={(e) => degistir(e.target.value)}
        required
        className="w-full rounded-lg border border-[var(--cizgi)] px-3 py-2 text-sm outline-none transition focus:border-[var(--brand)] focus:ring-2 focus:ring-[var(--brand-soft)]"
      />
      {ipucu && <span className="mt-1 block text-xs text-[var(--gri)]">{ipucu}</span>}
    </label>
  );
}
