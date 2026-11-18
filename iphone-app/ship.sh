#!/bin/bash
# Builds the Surrey League iPhone app and uploads it to TestFlight, in one go.
#
#   In Terminal:   cd ~/Documents/"Surrey League archive"/iphone-app && ./ship.sh
#   Or just tell Claude Code in Terminal: "ship the app"
#
# Takes about 5-10 minutes. Phones in the TestFlight group get the update 10-30 minutes after it finishes.
# Needs (one-time setup, already done if this has worked before):
#   - Xcode, opened at least once
#   - Documents/Apple keys/app-store-upload.env  (the App Store Connect upload key's details)
set -euo pipefail
cd "$(dirname "$0")"
step() { printf '\n\033[1m%s\033[0m\n' "$1"; }
fail() { printf '\n\033[31m%s\033[0m\n' "$1"; exit 1; }

KEYS="$HOME/Documents/Apple keys"
[ -f "$KEYS/app-store-upload.env" ] || fail "Missing $KEYS/app-store-upload.env (the App Store Connect upload key). Ask Claude to set it up."
# shellcheck disable=SC1091
source "$KEYS/app-store-upload.env"   # ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_FILE
[ -f "$ASC_KEY_FILE" ] || fail "The upload key file $ASC_KEY_FILE isn't there."
AUTH=(-allowProvisioningUpdates -authenticationKeyPath "$ASC_KEY_FILE" -authenticationKeyID "$ASC_KEY_ID" -authenticationKeyIssuerID "$ASC_ISSUER_ID")

xcodebuild -version >/dev/null 2>&1 || fail "Terminal can't find Xcode. Run this once, then try again:  sudo xcode-select -s /Applications/Xcode.app"
command -v npm >/dev/null || fail "Node.js isn't installed (needed to build the app's copy of the site)."

step "1/5  Getting the latest from GitHub"
git -C .. pull --ff-only || fail "Couldn't update from GitHub (are there unsaved changes in the Surrey League archive folder?). Nothing was built."

step "2/5  Checking the build tools"
[ -d node_modules/@capacitor ] && [ node_modules/.package-lock.json -nt package-lock.json ] || npm ci --no-audit --no-fund

step "3/5  Building the app's copy of slarchive.org"
npm run --silent sync

BUILD=$(date +%y%m%d%H%M)   # build numbers must always go up: the date and time does that
step "4/5  Building the app (version 1.0, build $BUILD)"
rm -rf build
xcodebuild -quiet -project ios/App/App.xcodeproj -scheme App -configuration Release \
  -destination 'generic/platform=iOS' -archivePath build/App.xcarchive archive \
  "${AUTH[@]}" DEVELOPMENT_TEAM=TR7WKKL578 CURRENT_PROJECT_VERSION="$BUILD"

step "5/5  Uploading to Apple"
xcodebuild -quiet -exportArchive -archivePath build/App.xcarchive \
  -exportOptionsPlist scripts/ExportOptions.plist -exportPath build/upload "${AUTH[@]}"

printf '\n\033[32mDone: build %s is uploaded.\033[0m TestFlight will offer it on your phone in 10-30 minutes.\n' "$BUILD"
