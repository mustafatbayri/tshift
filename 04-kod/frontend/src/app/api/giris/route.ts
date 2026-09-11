import { NextRequest, NextResponse } from "next/server";
import { apiAdresi, ERISIM_CEREZ, YENILEME_CEREZ } from "@/lib/api";

/**
 * Giriş. Tarayıcı doğrudan API'ye gitmez; buradan geçer.
 *
 * Bunun sebebi jetonları tarayıcı koduna hiç göstermemek. Yanıt gövdesinde
 * jeton DÖNMÜYORUZ — yalnızca `httpOnly` çerez olarak yazıyoruz. Sayfadaki
 * JavaScript jetonu ne okuyabilir ne de yanlışlıkla bir yere gönderebilir.
 */
export async function POST(istek: NextRequest) {
  const { firma, eposta, parola } = await istek.json();

  let cevap: Response;
  try {
    cevap = await fetch(`${apiAdresi()}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ firma, eposta, parola }),
      cache: "no-store",
    });
  } catch {
    // Arka uca hic ulasilamadi. 502 = "ben ayaktayim ama arkamdaki sunucu yok".
    // Kimlik hatasiyla (401) karistirilmamali: kullanicinin duzeltebilecegi
    // bir sey degil.
    return NextResponse.json(
      { kod: "ARKA_UC_YOK", mesaj: "Arka uca ulasilamadi." },
      { status: 502 }
    );
  }

  if (!cevap.ok) {
    // Hata mesajını olduğu gibi geçiriyoruz. API zaten bilerek belirsiz
    // konuşuyor ("firma, e-posta veya parola hatalı") — burada
    // ayrıntılandırmak o korumayı boşa çıkarırdı.
    const hata = await cevap.json().catch(() => ({ mesaj: "Giris yapilamadi." }));
    return NextResponse.json(hata, { status: cevap.status });
  }

  const { erisimJetonu, yenilemeJetonu } = await cevap.json();
  const sonuc = NextResponse.json({ tamam: true });

  const ortak = {
    httpOnly: true as const,
    sameSite: "lax" as const,
    path: "/",
    // Yerel geliştirmede http kullanıldığı için kapalı; canlıda AÇIK olmalı.
    secure: process.env.NODE_ENV === "production",
  };

  // Erişim jetonu 15 dakika yaşıyor (spec §7.4). Çerez ömrünü de ona eşitliyoruz
  // ki tarayıcı süresi geçmiş bir jetonu boşuna göndermesin.
  sonuc.cookies.set(ERISIM_CEREZ, erisimJetonu, { ...ortak, maxAge: 15 * 60 });
  sonuc.cookies.set(YENILEME_CEREZ, yenilemeJetonu, { ...ortak, maxAge: 30 * 24 * 60 * 60 });

  return sonuc;
}
