// Builds files/sitemap.xml: the list of every page on slarchive.org, for Google and other search engines.
// Run by the "Sitemap" GitHub Action whenever the results data changes; or by hand: node tools/build_sitemap.mjs
//
// What goes in:
//   - the home page, the women's home page, /analysis, the privacy and support pages
//   - every race page          /race/<season>-<match>          and /women/race/…
//   - every runner's page      /athlete/<name>                 and /women/athlete/…
//   - the standalone form guide pages in files/form-guide/
// A runner who appears under several spellings is listed once, under the name the site shows
// (the data's own alias lists decide that). "Unknown athlete" and similar entries are left out.
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';

const SITE = 'https://slarchive.org';
const FILES = new URL('../files/', import.meta.url);

// The same rules the site itself uses (files/index.html): keep these in step with it
const nameToSlug = (n) => (n || '').toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
const seasonToCompact = (s) => (s ? s.replace('/', '').slice(-4) : ''); // "2013/14" -> "1314"
const norm = (n) => (n || '').toLowerCase().trim();
const isUnknown = (name) => { const n = (name || '').trim(); return !n || /^[\[(]?unknown\b/i.test(n) || /^\?/.test(n) || /^(no name|undeclared runner|a\.? ?other)$/i.test(n); };

function pagesFor(file, prefix) {
  const data = JSON.parse(readFileSync(new URL(file, FILES), 'utf8'));
  // every other spelling -> the name the site shows
  const alias = new Map();
  for (const [k, v] of Object.entries(data.nameAliases || {})) alias.set(norm(k), v);
  for (const [k, v] of Object.entries(data.aliases || {})) alias.set(norm(k), v);
  for (const [canonical, list] of Object.entries(data.athleteAliases || {})) for (const a of list || []) alias.set(norm(a), canonical);
  const shown = (n) => { let name = n; for (let i = 0; i < 3 && alias.has(norm(name)) && alias.get(norm(name)) !== name; i++) name = alias.get(norm(name)); return name; };

  const races = new Set(), athletes = new Set();
  for (const a of data.athletes || []) if (a.name && !isUnknown(a.name)) athletes.add(nameToSlug(shown(a.name)));
  for (const r of data.races || []) {
    if (r.season && r.match) races.add(`${seasonToCompact(r.season)}-${r.match}`);
    for (const x of r.results || []) {
      const n = x.n || x.name; // men's results use n, women's use name
      if (n && !isUnknown(n)) athletes.add(nameToSlug(shown(n)));
    }
  }
  athletes.delete('');
  return [
    ...[...races].sort().map((k) => `${prefix}/race/${k}`),
    ...[...athletes].sort().map((s) => `${prefix}/athlete/${s}`),
  ];
}

const formGuides = readdirSync(new URL('form-guide/', FILES)).filter((f) => f.endsWith('.html')).sort().map((f) => `/form-guide/${f.replace(/\.html$/, '')}`);
const paths = ['/', '/#women', '/analysis', ...pagesFor('data.json', ''), ...pagesFor('data-women.json', '/women'), ...formGuides, '/privacy', '/support']
  .filter((p) => !p.includes('#')); // addresses after a # are not separate pages to a search engine

if (paths.length > 50000) throw new Error(`Too many pages for one sitemap (${paths.length}): it needs splitting`);
const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${paths.map((p) => `<url><loc>${SITE}${p}</loc></url>`).join('\n')}\n</urlset>\n`;
writeFileSync(new URL('sitemap.xml', FILES), xml);
console.log(`sitemap.xml: ${paths.length} pages`);
