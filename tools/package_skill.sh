#!/bin/sh
# Build dist/sort-tax-receipts.zip, the file you upload to Claude as a skill.
set -e
cd "$(dirname "$0")/.."
tools/sync_skill_assets.sh
mkdir -p dist
rm -f dist/sort-tax-receipts.zip
(cd skills && zip -qr -X ../dist/sort-tax-receipts.zip sort-tax-receipts -x '*.DS_Store')
echo "dist/sort-tax-receipts.zip"
