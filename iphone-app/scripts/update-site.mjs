// Builds the app's copy of slarchive.org in www/.
//  1. Gets the latest site from GitHub (never changes GitHub or the live site).
//  2. Copies the site files the app needs.
//  3. Saves the outside scripts and fonts the site uses (React, Tailwind, Google Fonts)
//     inside the app, so it opens with no signal.
//  4. Adds the app's own pieces: up-to-date data, Follow buttons, Notifications screen.
// Run with: npm run update-site
import { execSync } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';

const REPO = 'https://github.com/stephengardner1/surrey-league.git';
const CACHE = '.site-cache';
const OUT = 'www';
const VENDOR = join(OUT, 'vendor');
const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1';

// Working files in the site folder that the app doesn't need
const SKIP = [
  /^_worker\.js$/, /^_headers$/, /\.mjs$/, /^fetch-.*\.js$/, /^sync-.*\.js$/, /^prototype\.html$/,
  /^data \(\d+\)\.json$/, /^data\.fixed\.json$/, /^data-with-weather\.json$/, /-backup-/, /^index-backup/, /^\.DS_Store$/,
];

const sh = (cmd) => execSync(cmd, { stdio: 'inherit' });

// 1. Latest site. Inside the website's own folder (iphone-app/), use the site right next door;
//    otherwise fetch a copy from GitHub.
const INSIDE = existsSync(join('..', 'files', 'index.html')) && existsSync(join('..', 'notifier', 'compose.mjs'));
const SITE_REPO = INSIDE ? '..' : CACHE;
if (!INSIDE) {
  if (existsSync(join(CACHE, '.git'))) {
    sh(`git -C ${CACHE} fetch --depth 1 origin main`);
    sh(`git -C ${CACHE} checkout -q FETCH_HEAD`);
  } else {
    sh(`git clone --depth 1 ${REPO} ${CACHE}`);
  }
}

// 2. Site files (vendor/ is kept between runs so a failed download doesn't break the app)
mkdirSync(OUT, { recursive: true });
for (const name of readdirSync(OUT)) if (name !== 'vendor') rmSync(join(OUT, name), { recursive: true, force: true });
const src = join(SITE_REPO, 'files');
for (const name of readdirSync(src)) {
  if (SKIP.some((re) => re.test(name))) continue;
  cpSync(join(src, name), join(OUT, name), { recursive: true });
}

// 3. Outside scripts and fonts, saved locally
mkdirSync(join(VENDOR, 'fonts'), { recursive: true });
async function download(url, file, transform) {
  const dest = join(VENDOR, file);
  try {
    const r = await fetch(url, { headers: { 'User-Agent': UA } });
    if (!r.ok) throw new Error(r.status);
    if (transform) writeFileSync(dest, await transform(await r.text()));
    else writeFileSync(dest, Buffer.from(await r.arrayBuffer()));
  } catch (e) {
    if (!existsSync(dest)) throw new Error(`Could not download ${url} (${e.message}) and no saved copy exists`);
    console.log(`  (kept saved copy of ${file}: ${e.message})`);
  }
  return '/vendor/' + file;
}
let html = readFileSync(join(OUT, 'index.html'), 'utf8');
const swaps = [];
for (const m of html.matchAll(/<script src="(https:\/\/(?:unpkg\.com|cdn\.tailwindcss\.com)\/[^"]+)"/g)) {
  const url = m[1];
  const file = url.replace(/^https:\/\//, '').replace(/[^a-z0-9.@-]+/gi, '_') + (url.endsWith('.js') ? '' : '.js');
  swaps.push([url, await download(url, file)]);
}
const fontsMatch = html.match(/<link href="(https:\/\/fonts\.googleapis\.com\/css2[^"]+)" rel="stylesheet">/);
if (fontsMatch) {
  const cssUrl = fontsMatch[1].replace(/&amp;/g, '&');
  const local = await download(cssUrl, 'fonts/fonts.css', async (css) => {
    let n = 0;
    for (const u of [...new Set(css.match(/https:\/\/fonts\.gstatic\.com\/[^)]+/g) || [])]) {
      const name = `f${n++}.woff2`;
      const r = await fetch(u, { headers: { 'User-Agent': UA } });
      writeFileSync(join(VENDOR, 'fonts', name), Buffer.from(await r.arrayBuffer()));
      css = css.split(u).join(name);
    }
    return css;
  });
  swaps.push([fontsMatch[1], local]);
}
const rawSiteHtml = html;
const fnv = (str) => { let x = 0x811c9dc5; for (let k = 0; k < str.length; k++) { x ^= str.charCodeAt(k); x = Math.imul(x, 16777619) >>> 0; } return x.toString(16); };
for (const [from, to] of swaps) html = html.split(from).join(to);
html = html.replace(/<link rel="preconnect"[^>]*>\s*/g, '');

// 4. The app's own pieces
cpSync('app-src', join(OUT, 'app'), { recursive: true });
cpSync(INSIDE ? join('..', 'notifier', 'compose.mjs') : 'notifier/compose.mjs', join(OUT, 'app', 'compose.mjs'));
html = html.replace(/<head>/i, () => `<head>\n<script>window.SL_BUILT_HASH='${fnv(rawSiteHtml)}';</script>\n<script src="/app/config.js"></script>\n<script src="/app/early.js"></script>`);
// Let the page run edge to edge so the app can pad around the notch and home bar itself
html = html.replace(/(<meta name="viewport" content=")([^"]*)"/i, (m, a, b) => a + (b.includes('viewport-fit') ? b : b + ', viewport-fit=cover') + '"');
// The site's club vests, for the app's own screens (copied from the site so they always match)
{
  const i = html.indexOf('const getClubVestSvg=');
  const j = html.indexOf('\n};', i);
  if (i < 0 || j < 0) throw new Error('Could not find the club vests in index.html');
  writeFileSync(join(OUT, 'app', 'vests.js'), '(() => {\n' + html.slice(i, j + 3) + '\nwindow.slVest = getClubVestSvg;\n})();\n');
}
html = html.replace(/<\/body>/i, '<link rel="stylesheet" href="/app/app.css">\n<script src="/app/vests.js"></script>\n<script type="module" src="/app/app.js"></script>\n</body>');
writeFileSync(join(OUT, 'index.html'), html);
// For live updates: which outside files the app has saved copies of, and a fingerprint of the
// site version built in (the app compares it with slarchive.org to spot a newer version)
writeFileSync(join(OUT, 'app', 'vendor-map.json'), JSON.stringify(swaps));
writeFileSync(join(OUT, 'app', 'site-hash.txt'), fnv(rawSiteHtml));

const commit = execSync(`git -C ${SITE_REPO} log -1 --format="%h %ad %s" --date=short`).toString().trim();
writeFileSync(join(OUT, 'app', 'built-from.txt'), commit + '\n');
console.log(`Built www/ from GitHub commit: ${commit}`);
