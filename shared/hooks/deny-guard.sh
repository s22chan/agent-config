#!/usr/bin/env bash
# Conservative lexical guard for personal command prohibitions; not a shell parser.

input=$(cat 2>/dev/null)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)
[ -z "$cmd" ] && exit 0

deny() {
  printf '%s' "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"$1\"}}"
  exit 0
}

boundary=$'\034'

lex_shell() {
  local source=$1 token= ch quote= escaped=0 have_token=0 i
  for ((i = 0; i < ${#source}; i++)); do
    ch=${source:i:1}
    if [ "$escaped" = 1 ]; then
      token+=$ch
      have_token=1
      escaped=0
      continue
    fi

    case "$quote" in
      "'")
        if [ "$ch" = "'" ]; then
          quote=
        else
          token+=$ch
        fi
        ;;
      '"')
        case "$ch" in
          '\\') escaped=1 ;;
          '"') quote= ;;
          *) token+=$ch ;;
        esac
        ;;
      *)
        case "$ch" in
          '\\') escaped=1; have_token=1 ;;
          "'"|'"') quote=$ch; have_token=1 ;;
          ' '|$'\t')
            if [ "$have_token" = 1 ]; then
              printf '%s\n' "$token"
              token=
              have_token=0
            fi
            ;;
          $'\n'|$'\r')
            if [ "$have_token" = 1 ]; then
              printf '%s\n' "$token"
              token=
              have_token=0
            fi
            printf '%s\n' "$boundary"
            ;;
          ';'|'&'|'|')
            if [ "$have_token" = 1 ]; then
              printf '%s\n' "$token"
              token=
              have_token=0
            fi
            printf '%s\n' "$boundary"
            ;;
          *) token+=$ch; have_token=1 ;;
        esac
        ;;
    esac
  done

  [ "$escaped" = 1 ] && token+='\'
  [ "$have_token" = 1 ] && printf '%s\n' "$token"
}

reset_command_state() {
  command_start=1
  wrapper_kind=
  wrapper_arg=0
  wrapper_count=0
  prompt_prefix_ok=$base_prompt_ok
  command_kind=
  git_subcommand=
  git_arg_index=0
  git_config_arg=0
  hook_bypass=0
}

is_prompt_rule_git_path() {
  case "$1" in
    git|/bin/git|/usr/bin/git|/usr/local/bin/git) return 0 ;;
    *) return 1 ;;
  esac
}

inspect_line() {
  local line=$1 base_prompt_ok=$2
  local -a words
  local command_start wrapper_kind wrapper_arg wrapper_count prompt_prefix_ok
  local command_kind git_subcommand git_arg_index git_config_arg hook_bypass
  local tok lower name i

  mapfile -t words < <(lex_shell "$line")
  reset_command_state

  for ((i = 0; i < ${#words[@]}; i++)); do
    tok=${words[i]}
    if [ "$tok" = "$boundary" ]; then
      reset_command_state
      continue
    fi
    name=${tok##*/}
    lower=${tok,,}

    if [ "$command_start" = 1 ]; then
      if [ "$wrapper_arg" = 1 ]; then
        wrapper_arg=0
        continue
      fi

      case "$tok" in
        GIT_CONFIG_COUNT=*|GIT_CONFIG_KEY_*=*|GIT_CONFIG_VALUE_*=*|SKIP=*)
          hook_bypass=1
          continue
          ;;
        *=*) continue ;;
      esac

      case "$name" in
        sudo|command|env|proxy|time|nice|nohup|stdbuf|builtin|noglob|xargs)
          wrapper_kind=$name
          wrapper_count=$((wrapper_count + 1))
          prompt_prefix_ok=0
          continue
          ;;
        timeout)
          wrapper_kind=timeout
          wrapper_count=$((wrapper_count + 1))
          prompt_prefix_ok=0
          continue
          ;;
      esac

      if [ "$wrapper_kind" = timeout ]; then
        case "$tok" in
          -k|--kill-after|-s|--signal) wrapper_arg=1; continue ;;
          --kill-after=*|--signal=*|--preserve-status|--foreground|--verbose|-*) continue ;;
          *) wrapper_kind=; continue ;;
        esac
      fi

      case "$wrapper_kind:$tok" in
        sudo:-u|sudo:--user|sudo:-g|sudo:--group|sudo:-h|sudo:--host|sudo:-p|sudo:--prompt|sudo:-C|sudo:--close-from|sudo:-T|sudo:--command-timeout|sudo:-R|sudo:--chroot|sudo:-D|sudo:--chdir)
          wrapper_arg=1
          continue
          ;;
        env:-u|env:--unset|env:-C|env:--chdir)
          wrapper_arg=1
          continue
          ;;
        nice:-n|nice:--adjustment|time:-f|time:--format|time:-o|time:--output|stdbuf:-i|stdbuf:--input|stdbuf:-o|stdbuf:--output|stdbuf:-e|stdbuf:--error|xargs:-a|xargs:--arg-file|xargs:-E|xargs:--eof|xargs:-I|xargs:--replace|xargs:-L|xargs:--max-lines|xargs:-n|xargs:--max-args|xargs:-P|xargs:--max-procs|xargs:-s|xargs:--max-chars)
          wrapper_arg=1
          continue
          ;;
        command:-v|command:-V)
          command_start=0
          continue
          ;;
        env:-S|env:--split-string)
          i=$((i + 1))
          if [ "$i" -lt "${#words[@]}" ]; then
            inspect_line "${words[i]}" 0
          fi
          command_start=0
          continue
          ;;
        *:--|*:-*) continue ;;
      esac

      case "$name" in
        gh)
          deny "gh is disabled; prepare the PR operation for the GitHub web UI"
          ;;
        git)
          is_prompt_rule_git_path "$tok" || prompt_prefix_ok=0
          command_kind=git
          command_start=0
          ;;
        export)
          command_kind=export
          command_start=0
          ;;
        dd)
          command_kind=dd
          command_start=0
          ;;
        mkfs|mkfs.*)
          deny "mkfs is blocked by deny-guard"
          ;;
        bash|sh)
          command_kind=shell
          command_start=0
          prompt_prefix_ok=0
          ;;
        *) command_start=0 ;;
      esac
      continue
    fi

    if [ "$command_kind" = shell ]; then
      case "$tok" in
        -c|-lc|-cl)
          i=$((i + 1))
          if [ "$i" -lt "${#words[@]}" ]; then
            inspect_line "${words[i]}" 0
          fi
          command_kind=shell_done
          ;;
      esac
      continue
    fi

    if [ "$command_kind" = export ]; then
      case "$tok" in
        SKIP|SKIP=*)
          deny "Git hook configuration bypass is disabled"
          ;;
      esac
      case "$lower" in
        git_config_key_*=core.hookspath)
          deny "Git hook configuration bypass is disabled"
          ;;
      esac
      continue
    fi

    if [ "$command_kind" = dd ]; then
      case "$tok" in
        of=/dev/*) deny "dd to a device is blocked by deny-guard" ;;
      esac
      continue
    fi

    if [ "$command_kind" = git ]; then
      if [ -z "$git_subcommand" ]; then
        if [ "$git_config_arg" = 1 ]; then
          case "$lower" in
            core.hookspath=*) hook_bypass=1 ;;
          esac
          git_config_arg=0
          continue
        fi

        case "$lower" in
          -c|--config-env) git_config_arg=1; continue ;;
          -ccore.hookspath=*|--config-env=core.hookspath=*)
            hook_bypass=1
            continue
            ;;
          -*) continue ;;
        esac

        git_subcommand=$tok
        case "$git_subcommand" in
          commit|merge|rebase)
            [ "$hook_bypass" = 1 ] \
              && deny "Git hook configuration bypass is disabled"
            ;;
        esac
        continue
      fi

      git_arg_index=$((git_arg_index + 1))

      case "$git_subcommand:$tok" in
        add:.|add:-A|add:--all)
          deny "stage explicit files instead of git add ., -A, or --all"
          ;;
        commit:--no-verify|commit:-n|merge:--no-verify|rebase:--no-verify)
          deny "Git hook bypass is disabled; fix the owning hook failure"
          ;;
        push:--force|push:-f|push:--force-with-lease)
          if [ "$prompt_prefix_ok" != 1 ] || [ "$git_arg_index" -ne 1 ]; then
            deny "run the force option immediately after git push, directly, so the approval rule can prompt"
          fi
          ;;
        push:--force-with-lease=*|push:+*|push:--mirror)
          deny "this force-push spelling cannot reach the approval rule; use an explicitly prompted form"
          ;;
        rebase:-i|rebase:--interactive)
          if [ "$prompt_prefix_ok" != 1 ] || [ "$git_arg_index" -ne 1 ]; then
            deny "run the interactive option immediately after git rebase, directly, so the approval rule can prompt"
          fi
          ;;
      esac

      if [ "$git_subcommand" = push ] && [[ "$tok" =~ ^-[^-]*f ]]; then
        [ "$tok" = -f ] \
          || deny "combined force-push flags cannot reach the approval rule; use a separately prompted -f option"
      fi
    fi
  done
}

inspect_line "$cmd" 1
exit 0
