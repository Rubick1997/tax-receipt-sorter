#!/bin/sh
# Copy the sheet template into the skill, so the skill can set up a new user
# without the rest of this repository.
set -e
cd "$(dirname "$0")/.."
mkdir -p skills/sort-tax-receipts/assets
cp templates/tax-receipt-sorter-template.xlsx skills/sort-tax-receipts/assets/
