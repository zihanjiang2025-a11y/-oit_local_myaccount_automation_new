#!/bin/bash

cd "$(dirname "$0")"

python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python main.py setup

echo
echo "Setup complete. Press Enter to close this window."
read