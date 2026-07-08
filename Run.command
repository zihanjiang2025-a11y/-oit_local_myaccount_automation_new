#!/bin/bash

cd "$(dirname "$0")"

source .venv/bin/activate

python main.py

echo
echo "Program finished. Press Enter to close this window."
read