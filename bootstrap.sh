#!/usr/bin/env bash

set -euo pipefail

config_root=$(cd "$(dirname "$0")" && pwd)
codex_repo=${S22CHAN_CODEX_REPO:-git@github.com:s22chan/codex.git}
claude_repo=${S22CHAN_CLAUDE_REPO:-git@github.com:s22chan/claude.git}

ensure_checkout() {
  local target=$1 remote=$2
  if [ -d "$target/.git" ]; then
    return
  fi
  if [ -e "$target" ]; then
    printf 'Expected a Git checkout at %s; refusing to replace it.\n' "$target" >&2
    return 1
  fi
  command git clone "$remote" "$target"
}

ensure_checkout "$HOME/.codex" "$codex_repo"
ensure_checkout "$HOME/.claude" "$claude_repo"
command python3 "$config_root/sync.py"
command python3 "$config_root/sync.py" --check
command chmod -R go-w "$config_root"
