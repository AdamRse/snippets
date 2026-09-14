#!/bin/bash
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

source .venv/bin/activate
file="main.py"
[[ -n $1 ]] && file=$1
cd "${SCRIPT_DIR}"
clear
find . -path "./.venv" -prune -o -name "*.py" -print | entr sh -c "clear && python $file"
