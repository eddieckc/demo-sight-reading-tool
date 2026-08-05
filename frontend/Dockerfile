# ==============================================================================
# Cloud Run Optimized Dockerfile for Next.js Standalone Frontend (Powered by PNPM)
# Multi-stage build minimizing container footprint and running as non-root user.
# ==============================================================================
FROM node:20-alpine AS base
WORKDIR /app

# Enable corepack so PNPM is natively available
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

# Stage 1: Install dependencies with PNPM
FROM base AS deps
RUN apk add --no-cache libc6-compat
COPY package.json ./
RUN pnpm install

# Stage 2: Build Next.js application with PNPM
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

RUN pnpm run build

# Stage 3: Production runner
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
