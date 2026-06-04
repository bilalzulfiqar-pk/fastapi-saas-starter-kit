FROM node:22-alpine

WORKDIR /workspace

COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json ./apps/web/package.json

RUN corepack enable && pnpm install --frozen-lockfile=false

COPY . .

WORKDIR /workspace/apps/web
EXPOSE 3000
