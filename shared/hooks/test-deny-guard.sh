#!/usr/bin/env bash

set -u

guard=$(cd "$(dirname "$0")" && pwd)/deny-guard.sh
failures=0
checks=0

check() {
  local expected=$1 label=$2 command=$3 output actual=allow
  output=$(jq -cn --arg command "$command" '{tool_input: {command: $command}}' \
    | bash "$guard")
  if [ -n "$output" ]; then
    if printf '%s' "$output" \
      | jq -e '.hookSpecificOutput.permissionDecision == "deny"' >/dev/null; then
      actual=deny
    else
      printf 'FAIL %s: invalid hook output: %s\n' "$label" "$output" >&2
      failures=$((failures + 1))
      checks=$((checks + 1))
      return
    fi
  fi

  checks=$((checks + 1))
  if [ "$actual" != "$expected" ]; then
    printf 'FAIL %s: expected %s, got %s for %s\n' \
      "$label" "$expected" "$actual" "$command" >&2
    failures=$((failures + 1))
  fi
}

check deny gh-absolute '/usr/bin/gh pr view 1'
check deny gh-env 'env gh pr view 1'

check deny git-add-absolute '/usr/bin/git add .'
check deny git-commit-short-bypass 'git commit -m audit -n'
check deny git-config-bypass 'git -c core.hooksPath=/dev/null commit -m audit'
check deny git-config-case-bypass 'git -c Core.HooksPath=/dev/null commit -m audit'
check deny git-env-config-bypass \
  'env GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/dev/null git commit -m audit'
check deny git-export-skip-bypass \
  'export SKIP=1 && git commit -m audit'
check deny git-export-config-bypass \
  'export GIT_CONFIG_KEY_0=Core.HooksPath && git commit -m audit'
check deny git-force-late 'git push origin topic --force'
check deny git-force-wrapped 'env git push --force origin topic'
check deny git-force-qualified-lease \
  'git push --force-with-lease=refs/heads/topic:deadbeef origin topic'
check deny git-force-combined 'git push -fu origin topic'
check deny git-force-mirror 'git push --mirror origin'
check deny git-late-nested-bypass "bash -c 'echo ok; git commit -n -m audit'"

check deny mkfs-rtk 'rtk mkfs.ext4 /dev/sdz'
check deny mkfs-env-absolute 'env /usr/sbin/mkfs.ext4 /dev/sdz'
check deny dd-absolute '/usr/bin/dd if=image of=/dev/sdz'
check deny dd-rtk 'rtk dd if=image of=/dev/sdz'

check allow git-add-file 'git add src/app.py'
check allow git-commit-normal 'git commit -m audit'
check allow git-push-normal 'git push origin topic'
check allow git-force-canonical 'git push --force origin topic'
check allow git-force-rtk-canonical 'rtk git push --force-with-lease origin topic'
check allow git-amend-canonical '/usr/bin/git commit --amend -m audit'
check allow git-rebase-canonical 'git rebase -i main'
check allow git-abort-canonical 'git rebase --abort'
check allow dd-file-output 'dd if=/dev/zero of=image.bin count=1'
check allow command-query-rm 'command -v rm'
check allow quoted-rm-argument "printf '%s' rm"
check allow nested-rm-argument "bash -c 'printf \"%s\" rm'"
check allow nested-quoted-semicolon "bash -c 'printf \"%s\" \"x; rm\"'"

if [ "$failures" -ne 0 ]; then
  printf '%s/%s guard checks failed\n' "$failures" "$checks" >&2
  exit 1
fi

printf 'PASS %s guard checks\n' "$checks"
