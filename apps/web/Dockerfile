FROM node:22-alpine

WORKDIR /workspace

COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json ./apps/web/package.json
COPY scripts/web-dev-entrypoint.sh /usr/local/bin/web-dev-entrypoint

RUN corepack enable && pnpm install --frozen-lockfile
RUN chmod +x /usr/local/bin/web-dev-entrypoint

COPY . .

WORKDIR /workspace/apps/web
EXPOSE 3000
