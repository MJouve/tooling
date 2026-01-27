#!/bin/bash
# Script wrapper pour sprite_cutter.py

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

python3 "${SCRIPT_DIR}/sprite_cutter.py" "$@"

