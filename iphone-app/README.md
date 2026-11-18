# Surrey League Compendium: the iPhone app

Everything for the iPhone app lives in this folder. The website doesn't use it.

## Shipping a new version to TestFlight

In Terminal:

```
cd ~/Documents/"Surrey League archive"/iphone-app
./ship.sh
```

Or tell Claude Code in Terminal: **"ship the app"**.

It gets the latest from GitHub, builds the app with the current site built in, and uploads it to
App Store Connect (about 5-10 minutes). Phones in the TestFlight group get it 10-30 minutes later.

## Most changes don't need a new version

The app updates itself from slarchive.org:
- **Results** come live every time.
- **The site's design and pages**, and **the app's own layer** (Notifications screen, follow bells,
  app-only layout in `app-src/app.js` and `app-src/app.css`), are downloaded each launch and used
  from the next one. Pushing a change to `app-src/app.js`, `app-src/app.css` or `notifier/compose.mjs`
  publishes it to `files/app/` automatically (GitHub Action "Publish app layer").

A new version (`./ship.sh`) is only needed for changes to `app-src/early.js`, `app-src/config.js`,
the iOS project (`ios/`: notification pictures, icon, plugins) or `capacitor.config.json`.

## What's in here

| | |
|---|---|
| `ship.sh` | Build and upload, in one go |
| `app-src/` | The app's own layer, added on top of the site |
| `ios/` | The Xcode project. `NotificationImages/` puts portraits and singlets on notifications |
| `scripts/update-site.mjs` | Builds the app's copy of the site (`www/`) from `../files/` |
| `worker/` | The notifications back office on Cloudflare (`npm run deploy` inside it) |
| `../notifier/` | Notification wording (shared with the GitHub Action that sends them) |

Keys and passwords are never in GitHub. They live in Documents › Apple keys on Steve's MacBook:
the push key, the App Store Connect upload key (`app-store-upload.env` + `.p8`), and the private settings file.
