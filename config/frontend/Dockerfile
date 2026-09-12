FROM node:22-alpine AS dependencies
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
FROM dependencies AS builder
ENV NEXT_TELEMETRY_DISABLED=1
COPY frontend/ ./
RUN npm run build && npm run typecheck && npm run lint
FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static
COPY --from=builder --chown=node:node /app/public ./public
USER node
CMD ["node", "server.js"]
