# TradePulse landing — build from repo root:
#   docker build -f apps/landing/Dockerfile -t tradepulse-landing .
#
# Mirrors apps/web/Dockerfile. This app is deliberately independent of
# apps/web: it runs Next 16 and Tailwind 4 while the workbench stays on
# Next 15 and Tailwind 3, and the repo is not an npm workspace, so the two
# dependency trees never meet.
FROM node:22-alpine AS deps
WORKDIR /app
COPY apps/landing/package.json apps/landing/package-lock.json ./
RUN npm ci

FROM node:22-alpine AS builder
WORKDIR /app
ARG NEXT_PUBLIC_REVIEW_DESK_URL=https://tradepulse-web-gk63mqpoca-el.a.run.app/workbench
ENV NEXT_PUBLIC_REVIEW_DESK_URL=$NEXT_PUBLIC_REVIEW_DESK_URL \
    NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY apps/landing/ ./
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME=0.0.0.0 \
    NEXT_TELEMETRY_DISABLED=1
RUN addgroup -S nodejs && adduser -S nextjs -G nodejs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
