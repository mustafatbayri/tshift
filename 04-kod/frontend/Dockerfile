# =============================================================================
# TShift arayuz kutusu
#
# Next.js "standalone" ciktisi kullaniliyor: sunucu, yalniz gerekli paketlerle
# tek klasore toplaniyor. node_modules'un tamami kutuya girmiyor.
# =============================================================================

FROM node:22-alpine AS bagimliliklar
WORKDIR /uygulama
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS derle
WORKDIR /uygulama
COPY --from=bagimliliklar /uygulama/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-alpine
WORKDIR /uygulama
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Kok olmayan kullanici: kutu icinde bir acik bulunsa bile yetkisi sinirli olsun.
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

COPY --from=derle --chown=nextjs:nodejs /uygulama/.next/standalone ./
COPY --from=derle --chown=nextjs:nodejs /uygulama/.next/static ./.next/static
COPY --from=derle --chown=nextjs:nodejs /uygulama/public ./public

USER nextjs
EXPOSE 3000
ENV PORT=3000 HOSTNAME=0.0.0.0

CMD ["node", "server.js"]
