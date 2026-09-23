import { NextRequest, NextResponse } from "next/server";
import { apiAdresi, istemciBasliklari, ERISIM_CEREZ, YENILEME_CEREZ } from "@/lib/api";

/**
 * Erişim jetonu süresi dolduğunda buraya uğranır.
 *
 * Neden ayrı bir adres: sayfa bileşenleri çerez YAZAMAZ (yanıt başlıkları
 * çoktan gönderilmiş olur). Yazabilen tek yer bir yönlendirme noktası.
 * Sayfa 401 alınca buraya gönderiyor, burası jetonu yeniliyor ve kullanıcıyı
 * geldiği sayfaya geri bırakıyor. Kullanıcı bir şey fark etmiyor.
 */
export async function GET(istek: NextRequest) {
  const geri = istek.nextUrl.searchParams.get("geri") ?? "/calisanlar";
  const yenileme = istek.cookies.get(YENILEME_CEREZ)?.value;

  if (!yenileme) {
    return NextResponse.redirect(new URL("/giris", istek.url));
  }

  const cevap = await fetch(`${apiAdresi()}/api/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(await istemciBasliklari()) },   // T-35
    body: JSON.stringify({ yenilemeJetonu: yenileme }),
    cache: "no-store",
  });

  if (!cevap.ok) {
    // Jeton geçersiz ya da güvenlik nedeniyle tüm oturumlar düşürülmüş olabilir.
    // İkisinde de yapılacak şey aynı: yeniden giriş.
    const sonuc = NextResponse.redirect(new URL("/giris?sebep=oturum", istek.url));
    sonuc.cookies.delete(ERISIM_CEREZ);
    sonuc.cookies.delete(YENILEME_CEREZ);
    return sonuc;
  }

  const { erisimJetonu, yenilemeJetonu } = await cevap.json();
  const sonuc = NextResponse.redirect(new URL(geri, istek.url));

  const ortak = {
    httpOnly: true as const,
    sameSite: "lax" as const,
    path: "/",
    secure: process.env.NODE_ENV === "production",
  };

  // Döner jeton: eskisi artık ölü, yenisini saklıyoruz.
  sonuc.cookies.set(ERISIM_CEREZ, erisimJetonu, { ...ortak, maxAge: 15 * 60 });
  sonuc.cookies.set(YENILEME_CEREZ, yenilemeJetonu, { ...ortak, maxAge: 30 * 24 * 60 * 60 });

  return sonuc;
}
