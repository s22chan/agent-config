#!/usr/bin/env bash

set -eu

input=$(cat 2>/dev/null)
root=${S22CHAN_CLAUDE_CONFIG_ROOT:-"$HOME/.claude"}
[ -e "$root" ] || exit 0

root=$(realpath -m -- "$root")
tool=$(printf '%s' "$input" | jq -r '.tool_name // empty' 2>/dev/null)
candidate=

case "$tool" in
  Bash) candidate=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null) ;;
  Edit|Write) candidate=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null) ;;
  *) exit 0 ;;
esac

[ -n "$candidate" ] || exit 0
candidate=$(realpath -m -- "$candidate")
case "$candidate" in
  "$root"|"$root"/*) ;;
  *) exit 0 ;;
esac

if [ -d "$root/.git" ]; then
  git -C "$root" config core.sharedRepository 0640
fi

chmod go-w "$root"
for path in .git .gitignore bootstrap.sh CLAUDE.md settings.json \
  statusline-command.sh commands agents hooks skills tests; do
  [ ! -e "$root/$path" ] || chmod -R go-w "$root/$path"
done

for path in "$root/bootstrap.sh" "$root/statusline-command.sh" \
  "$root/hooks/"*.sh "$root/tests/"*.sh; do
  [ ! -e "$path" ] || chmod 750 "$path"
done
