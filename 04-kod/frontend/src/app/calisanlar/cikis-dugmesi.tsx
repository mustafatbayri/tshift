"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function CikisDugmesi() {
  const yonlendir = useRouter();
  const [bekliyor, setBekliyor] = useState(false);

  async function cik() {
    setBekliyor(true);
    // Yalnız çerezi silmiyoruz; sunucudaki yenileme jetonu da iptal ediliyor.
    // Aksi halde jetonun bir kopyası çalışmaya devam ederdi.
    await fetch("/api/cikis", { method: "POST" });
    yonlendir.push("/giris");
    yonlendir.refresh();
  }

  return (
    <button
      onClick={cik}
      disabled={bekliyor}
      className="rounded-lg border border-[var(--cizgi)] px-3 py-1.5 text-sm text-[var(--gri)] transition hover:border-[var(--gri-2)] hover:text-[var(--ink)] disabled:opacity-50"
    >
      {bekliyor ? "..." : "Cikis"}
    </button>
  );
}
