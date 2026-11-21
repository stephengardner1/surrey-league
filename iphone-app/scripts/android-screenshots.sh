#!/bin/bash
# Run by the "Android build" GitHub Action on a pretend Android phone:
# installs the app, opens each tab and saves a screenshot of each.
OUT="$1"; S="$OUT/screens"; mkdir -p "$S"
shot() { adb exec-out screencap -p > "$S/$1.png"; echo "saved $1"; }
# Tap something by the words on it (falls back to a screen position if the words can't be found)
tap() {
  adb shell uiautomator dump /sdcard/ui.xml >/dev/null 2>&1
  adb pull /sdcard/ui.xml /tmp/ui.xml >/dev/null 2>&1
  local xy
  xy=$(python3 - "$1" <<'PY'
import re, sys
try: x = open('/tmp/ui.xml', encoding='utf8').read()
except Exception: x = ''
want = sys.argv[1]
hits = []
for m in re.finditer(r'<node[^>]*?(?:text|content-desc)="%s"[^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"' % re.escape(want), x):
    a, b, c, d = map(int, m.groups()); hits.append(((a + c) // 2, (b + d) // 2))
if hits:
    hits.sort(key=lambda p: -p[1]); print(*hits[0])   # the lowest one on screen: the floating nav
PY
)
  if [ -n "$xy" ]; then echo "tap '$1' at $xy"; adb shell input tap $xy; else echo "couldn't find '$1', tapping $2 $3"; adb shell input tap "$2" "$3"; fi
  sleep 6
}

adb install -r "$OUT/surrey-league-test.apk"
adb shell am start -n org.slarchive.app/.MainActivity
sleep 4;  shot 00-launch
sleep 40; shot 01-tables
adb shell uiautomator dump /sdcard/ui.xml >/dev/null 2>&1; adb pull /sdcard/ui.xml "$OUT/screens/ui-tables.xml" >/dev/null 2>&1
adb shell input swipe 540 1700 540 700 400; sleep 3; shot 02-tables-scrolled
# Scroll back to the top: the floating nav shrinks while scrolling down and the taps below expect it full size
adb shell input swipe 540 700 540 1900 300; sleep 1; adb shell input swipe 540 700 540 1900 300; sleep 3
tap Races 324 2230;     shot 03-races
tap Stats 108 2230;     shot 04-stats
tap Following 756 2230; shot 05-following
adb shell input keyevent 4; sleep 3; shot 06-after-back-button
tap FantaXC 972 2230;   sleep 6; shot 07-fantaxc
adb shell input keyevent 4; sleep 3; shot 08-after-back-button-2
adb shell input keyevent 4; sleep 3; shot 09-after-back-button-3
# Notes for checking the home-screen icon
{ adb shell dumpsys package org.slarchive.app | grep -i -E "versionName|versionCode|icon" ; AAPT=$(ls "$ANDROID_HOME"/build-tools/*/aapt2 | tail -1); "$AAPT" dump badging "$OUT/surrey-league-test.apk" | grep -i -E "icon|label|sdk"; "$AAPT" dump resources "$OUT/surrey-league-test.apk" | grep -A8 "mipmap/ic_launcher" | head -60; } > "$S/icon-notes.txt" 2>&1
adb shell input keyevent 3; sleep 3; shot 10-home-screen
adb logcat -d -t 400 '*:E' > "$OUT/screens/errors.txt" 2>/dev/null || true
exit 0
