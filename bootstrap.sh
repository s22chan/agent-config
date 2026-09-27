#!/usr/bin/env bash

set -euo pipefail

config_root=$(cd "$(dirname "$0")" && pwd)
command chmod -R go-w "$config_root"
command python3 "$config_root/sync.py"
command python3 "$config_root/sync.py" --check
