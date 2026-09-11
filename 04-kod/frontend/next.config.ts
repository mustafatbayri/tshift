import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Kutuya girerken gerekli: sunucuyu ve yalniz kullanilan paketleri tek
  // klasore toplar. Bu olmadan .next/standalone uretilmez ve Dockerfile calismaz.
  output: "standalone",
};

export default nextConfig;
