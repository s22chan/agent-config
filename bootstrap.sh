#!/usr/bin/env bash

set -euo pipefail

config_root=$(cd "$(dirname "$0")" && pwd)
command chmod -R go-w "$config_root"
command "$config_root/sync.py"
command "$config_root/sync.py" --check
