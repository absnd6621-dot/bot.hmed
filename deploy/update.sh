#!/usr/bin/env bash
# Run on the server from a checkout tracking main. Never run with uncommitted changes.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -n "$(git status --porcelain --untracked-files=normal)" ]]; then
  echo 'Deployment stopped: the server checkout has local changes.' >&2
  exit 1
fi
test -f .env || { echo 'Missing .env on server' >&2; exit 1; }
git fetch origin main
git checkout main
git merge --ff-only origin/main
docker compose config -q
docker compose up -d --wait postgres redis
docker compose build bot api migrate
docker compose run --rm migrate
docker compose up -d --no-deps bot api
docker compose ps
