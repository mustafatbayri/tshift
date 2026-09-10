export type Calisan = {
  id: string;
  personelNo: string;
  ad: string;
  soyad: string;
  tamAd: string;
  eposta: string | null;
  durum: string | number;
};

export type CalisanListesi = {
  kiraciId: string;
  kapsam: "Kendi" | "Kapsam" | "Kiraci";
  adet: number;
  kayitlar: Calisan[];
};

export type Ben = {
  id: string;
  ad: string;
  soyad: string;
  eposta: string;
  kiraciId: string;
  kapsam: "Kendi" | "Kapsam" | "Kiraci";
  izinler: string[];
  departmanSayisi: number;
  ekipSayisi: number;
};

export type Secenek = {
  id: string;
  ad: string;
  kod: string;
  departmanId?: string;
};
