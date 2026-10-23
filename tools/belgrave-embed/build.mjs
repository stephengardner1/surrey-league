// Builds the Squarespace Code Block for a race: the stored copy of the panel + its style + the live-refresh script.
// The data comes from the same code that serves https://slarchive.org/embed/race/... (files/_worker.js),
// run here against the local data files, so the stored copy matches what the live feed will send.
//
//   node tools/belgrave-embed/build.mjs 2526-1 2526-2            men's races, Belgrave
//   node tools/belgrave-embed/build.mjs w:2526-4 --club=BEL     women's race
// Writes tools/belgrave-embed/blocks/<race>.html (paste the whole file into a Code Block).
import fs from 'fs';
import path from 'path';
import { fileURLToPath, pathToFileURL } from 'url';
import { parseHTML } from 'linkedom';

const here = path.dirname(fileURLToPath(import.meta.url));
const files = path.resolve(here, '../../files');
const args = process.argv.slice(2);
const club = ((args.find(a => a.startsWith('--club=')) || '--club=BEL').slice(7)).toUpperCase();
const races = args.filter(a => !a.startsWith('--'));

// load the site's worker as a module and give it the local files in place of Cloudflare's
const tmp = path.join(here, '.worker.mjs');
fs.copyFileSync(path.join(files, '_worker.js'), tmp);
const worker = (await import(pathToFileURL(tmp).href + '?' + Date.now())).default;
fs.unlinkSync(tmp);
const env = { ASSETS: { fetch: async req => {
  const p = decodeURIComponent(new URL(req.url).pathname), f = path.join(files, p === '/' ? 'index.html' : p);
  return fs.existsSync(f) ? new Response(fs.readFileSync(f)) : new Response('', { status: 404 });
} } };

const panelJs = fs.readFileSync(path.join(here, 'panel.js'), 'utf8');
const panelCss = fs.readFileSync(path.join(here, 'panel.css'), 'utf8');
globalThis.bhSlNoAuto = true;
new Function(panelJs)();
const { clean, render } = globalThis.bhSlPanel;

fs.mkdirSync(path.join(here, 'blocks'), { recursive: true });
for (const r of races) {
  const women = r.startsWith('w:'), code = r.replace(/^w:/, '');
  const res = await worker.fetch(new Request(`https://slarchive.org/embed/${women ? 'women/' : ''}race/${code}.json?club=${encodeURIComponent(club)}`), env);
  if (!res.ok) { console.error(`${r}: no data (${res.status})`); process.exitCode = 1; continue; }
  const d = clean(await res.json(), { code, club, women });
  const { document } = parseHTML('<!doctype html><html><body></body></html>');
  const stored = render(document, d).outerHTML;
  const block =
`<!-- Surrey League results panel: ${d.venue}, ${d.season} match ${d.match}. Built ${new Date().toISOString().slice(0, 10)} by slarchive tools/belgrave-embed. -->
<div class="bh-sl" data-race="${code}" data-club="${club}" data-women="${women ? 1 : 0}">${stored}</div>
<style>
${panelCss.trim()}
</style>
<script>
${panelJs.trim()}
</script>
`;
  const out = path.join(here, 'blocks', `${women ? 'w-' : ''}${code}-${club.replace(/[^A-Z0-9]/g, '')}.html`);
  fs.writeFileSync(out, block);
  console.log(`${r}: ${d.venue}, ${d.runners.length} finishers -> ${path.relative(process.cwd(), out)} (${(block.length / 1024).toFixed(1)} KB)`);
}
