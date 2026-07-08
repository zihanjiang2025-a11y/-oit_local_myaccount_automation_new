#!/bin/bash

cd "$(dirname "$0")"

source .venv/bin/activate

while true
do
    clear
    python main.py

    echo
    echo "===================================="
    echo "Program finished."
    echo
    echo "[R] Restart"
    echo "[Q] Quit"
    echo "===================================="

    read -p "> " choice

    case "$choice" in
        [Rr])
            ;;
        [Qq])
            break
            ;;
        *)
            echo "Invalid option."
            sleep 1
            ;;
    esac
done