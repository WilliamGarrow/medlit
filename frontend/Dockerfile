FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm install

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 medlit && \
    adduser --system --uid 1001 medlit

COPY --from=builder /app/public ./public
COPY --from=builder --chown=medlit:medlit /app/.next/standalone ./
COPY --from=builder --chown=medlit:medlit /app/.next/static ./.next/static

USER medlit

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
