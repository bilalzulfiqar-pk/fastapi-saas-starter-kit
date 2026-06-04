#!/bin/sh
set -eu

LOCKFILE_HASH_FILE="/workspace/node_modules/.pnpm-lock.hash"
CURRENT_LOCKFILE_HASH="$(sha256sum /workspace/pnpm-lock.yaml | awk '{print $1}')"

if [ ! -f "/workspace/apps/web/node_modules/next/package.json" ] || [ ! -f "$LOCKFILE_HASH_FILE" ] || [ "$(cat "$LOCKFILE_HASH_FILE")" != "$CURRENT_LOCKFILE_HASH" ]; then
  corepack enable
  CI=true pnpm install --dir /workspace --frozen-lockfile
  printf '%s' "$CURRENT_LOCKFILE_HASH" > "$LOCKFILE_HASH_FILE"
fi

cd /workspace/apps/web
exec pnpm dev --hostname 0.0.0.0 --port 3000
