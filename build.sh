#!/usr/bin/env bash
set -euo pipefail

echo "Build helper"
echo "1) PyInstaller executable"
echo "2) Docker image"
echo "3) RPM notes"
read -r -p "Choose [1-3]: " choice

case "$choice" in
  1)
    python3 -m pip install pyinstaller
    pyinstaller --onefile --windowed gui_designer.py
    ;;
  2)
    docker build -t gui-designer .
    ;;
  3)
    echo "Install fpm or rpmbuild, then package dist binary from PyInstaller."
    ;;
  *)
    echo "Invalid choice"; exit 1 ;;
esac
