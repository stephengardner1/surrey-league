// Cloudflare Pages worker.
// Everything is served as normal static files, except athlete pages
// (/athlete/<slug> and /women/athlete/<slug>). For those it serves the normal
// site but rewrites the page title and the link-preview (Open Graph) tags, so a
// link pasted into WhatsApp or social shows "<name> | Surrey League compendium",
// a line with their club GOAT rank,
// and the athlete's portrait (or the grey runner in their club vest).
// If anything goes wrong it falls back to the plain site, never an error page.

const SITE = 'https://slarchive.org';
const SITE_TITLE = 'Surrey League compendium';
const cache = {};

const slugOf = n => (n || '').toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
const clubFile = c => c.replace(/\//g, '').replace(/&/g, 'and');
const esc = s => String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');

async function json(env, origin, path) {
  if (!cache[path]) {
    const r = await env.ASSETS.fetch(new Request(origin + path));
    if (!r.ok) throw new Error(path + ' ' + r.status);
    cache[path] = await r.json();
  }
  return cache[path];
}

// slug -> { name, club }: every runner in the race results (latest race wins for club), plus the athlete list
function athleteIndex(data, women) {
  const key = women ? 'idx-w' : 'idx-m';
  if (cache[key]) return cache[key];
  const idx = {};
  for (const a of data.athletes || []) if (a.name) idx[slugOf(a.name)] = { name: a.name, club: a.club };
  const races = (data.races || []).slice().sort((p, q) => (p.season || '').localeCompare(q.season || '') || (p.match || 0) - (q.match || 0));
  for (const r of races) for (const x of r.results || []) {
    const n = x.n || x.name, c = x.c || x.club;  // men's results use n/c, women's use name/club
    if (n && c && c !== 'GUEST' && c !== 'N/S') idx[slugOf(n)] = { name: n, club: c };
  }
  return (cache[key] = idx);
}

async function exists(env, origin, path) {
  const r = await env.ASSETS.fetch(new Request(origin + path, { method: 'HEAD' }));
  return r.ok;
}

async function athletePage(request, env, url, women, slug) {
  const origin = url.origin;
  const page = await env.ASSETS.fetch(new Request(origin + '/'));
  try {
    const data = await json(env, origin, women ? '/data-women.json' : '/data.json');
    const a = athleteIndex(data, women)[slug];
    if (!a) return page;
    const name = a.name.replace(/\s*\([^)]*\)$/, '');
    const club = a.club || '';
    const portraits = await json(env, origin, '/portraits/portraits.json');
    const p = portraits[name.toLowerCase()];
    let image = null;
    if (p && p.club === club) image = `/portraits/og/athletes/${p.file}.png`;
    else if (club && await exists(env, origin, `/portraits/og/clubs/${clubFile(club)}.png`)) image = `/portraits/og/clubs/${clubFile(club)}.png`;
    const title = `${name} | ${SITE_TITLE}`;
    let desc = `Surrey League cross country career of ${name}`;
    try {  // "…, the #3🐐 of Belgrave Harriers." from goat-ranks.json (built by tools/build_goat_ranks.py)
      const g = await json(env, origin, '/goat-ranks.json');
      const rank = (g[women ? 'women' : 'men'][slug] || {})[club];
      if (rank) desc += `, the #${rank}🐐 of ${g.clubs[club] || club}.`;
    } catch (e) {}
    const pageUrl = `${SITE}${women ? '/women' : ''}/athlete/${slug}`;
    const setContent = v => ({ element(el) { el.setAttribute('content', v); } });
    let rw = new HTMLRewriter()
      .on('title', { element(el) { el.setInnerContent(title); } })
      .on('meta[property="og:title"]', setContent(title))
      .on('meta[property="og:description"]', setContent(desc))
      .on('meta[name="description"]', setContent(desc))
      .on('meta[property="og:url"]', setContent(pageUrl));
    if (image) {
      rw = rw
        .on('meta[property="og:image"]', setContent(SITE + image))
        .on('meta[name="twitter:card"]', setContent('summary'))
        .on('head', { element(el) { el.append(`<meta property="og:image:width" content="600"><meta property="og:image:height" content="600"><meta property="og:image:alt" content="${esc('Illustration of ' + name)}">`, { html: true }); } });
    }
    const res = rw.transform(page);
    const out = new Response(res.body, res);
    out.headers.set('Cache-Control', 'public, max-age=300');
    return out;
  } catch (e) {
    return page;
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const m = url.pathname.match(/^\/(women\/)?athlete\/([^\/]+)\/?$/i);
    if (m && (request.method === 'GET' || request.method === 'HEAD')) {
      try {
        return await athletePage(request, env, url, !!m[1], slugOf(decodeURIComponent(m[2])).replace(/-poster$/, ''));  // /athlete/<slug>-poster is the opened sticker: same preview
      } catch (e) {
        return env.ASSETS.fetch(new Request(url.origin + '/'));
      }
    }
    return env.ASSETS.fetch(request);
  }
};
