#!/usr/bin/env bash
# Status line for Claude Code
# Fields: session name (or session id fallback) | cwd | model | context% | cost | git repo/branch

input=$(cat)

# -- session name, falling back to first 8 chars of session id (bold/bright yellow) --
session_name=$(echo "$input" | jq -r '.session_name // ((.session_id // empty) | .[0:8])')
if [ -n "$session_name" ]; then
  session_name_fmt=$(printf '\033[01;33m%s\033[00m' "$session_name")
else
  session_name_fmt=""
fi

# -- cwd --
cwd=$(echo "$input" | jq -r '.cwd')
cwd_fmt=$(printf '\033[01;34m%s\033[00m' "$cwd")

# -- model --
model=$(echo "$input" | jq -r '.model | if type == "object" then .display_name else . end // empty')

# -- context window % --
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
if [ -n "$used_pct" ]; then
  ctx_fmt=$(printf 'ctx:%.0f%%' "$used_pct")
else
  ctx_fmt=""
fi

# -- session cost --
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // empty')
if [ -n "$cost" ]; then
  cost_fmt=$(printf '$%.2f' "$cost")
else
  cost_fmt=""
fi

# -- git repo/branch --
repo=$(echo "$input" | jq -r '.workspace.repo | if . then .owner + "/" + .name else empty end')
branch=$(git -C "$cwd" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null)
if [ -n "$repo" ] && [ -n "$branch" ]; then
  git_fmt="$repo ($branch)"
elif [ -n "$branch" ]; then
  git_fmt="($branch)"
else
  git_fmt=""
fi

# -- assemble --
parts=()
[ -n "$session_name_fmt" ] && parts+=("$session_name_fmt")
parts+=("$cwd_fmt")
[ -n "$model" ]   && parts+=("$model")
[ -n "$ctx_fmt" ] && parts+=("$ctx_fmt")
[ -n "$cost_fmt" ] && parts+=("$cost_fmt")
[ -n "$git_fmt" ] && parts+=("$git_fmt")

# join with " | "
out=""
for p in "${parts[@]}"; do
  [ -z "$out" ] && out="$p" || out="$out | $p"
done

printf '%s' "$out"
