#!/bin/bash
# Pull the latest version from GitHub and install it into Home Assistant.
# For manual installs that cloned this repo to /config/ha-nexia-filter-reminder.
# Run from the Terminal & SSH add-on:  bash /config/ha-nexia-filter-reminder/scripts/update.sh [--restart]
set -euo pipefail

REPO=/config/ha-nexia-filter-reminder
DEST=/config/custom_components/nexia

git -C "$REPO" pull --ff-only
mkdir -p /config/custom_components
rm -rf "$DEST"
cp -r "$REPO/custom_components/nexia" "$DEST"

VERSION=$(grep '"version"' "$DEST/manifest.json" | cut -d'"' -f4)
echo "Installed nexia $VERSION"

if [[ "${1:-}" == "--restart" ]]; then
  echo "Restarting Home Assistant..."
  ha core restart
else
  echo "Restart Home Assistant to load it (or re-run with --restart)."
fi
