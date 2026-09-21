#!/bin/bash
# Installs the daemn bridge panel into Premiere Pro. Claude runs this — Damon never does.
set -e

ID="com.daemn.premiere.bridge"
VER="1.0.0"
SRC="$(cd "$(dirname "$0")" && pwd)/plugin"
DEST="$HOME/Library/Application Support/Adobe/UXP/Plugins/External/${ID}_${VER}"

mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
mkdir -p "$DEST"
cp -R "$SRC"/ "$DEST"/

echo "installed -> $DEST"
ls "$DEST"
