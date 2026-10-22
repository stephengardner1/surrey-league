// Cloudflare Pages worker.
// Everything is served as normal static files, except athlete pages and race pages
// (/race/<season>-<match>, e.g. /race/6465-4: venue, date, winner and team winner; picture is the race photo,
// else the highest-placed runner with a portrait) and athlete pages
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

// ---- race pages: /race/<season>-<match> (e.g. /race/6465-4) and /women/race/... ----
const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const seasonOf = c => { const y = parseInt(c.slice(0, 2), 10); return `${y >= 62 && y <= 99 ? '19' : '20'}${c.slice(0, 2)}/${c.slice(2, 4)}`; };
function longDate(d) {  // "11th October 2025" / "2011-10-08" / "10 October 1992" -> "11 October 2025"; null if there's no full date
  if (!d) return null;
  let m = String(d).match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (m) return `${parseInt(m[3], 10)} ${MONTHS[parseInt(m[2], 10) - 1]} ${m[1]}`;
  m = String(d).match(/^(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})$/);
  if (m) { const mi = MONTHS.findIndex(x => x.toLowerCase().startsWith(m[2].toLowerCase().slice(0, 3))); if (mi >= 0) return `${parseInt(m[1], 10)} ${MONTHS[mi]} ${m[3]}`; }
  return null;
}
// the first photo for each race, read from RACE_PHOTOS in the site's own page so new photos need no extra step
async function racePhotos(env, origin) {
  if (cache.photos) return cache.photos;
  const r = await env.ASSETS.fetch(new Request(origin + '/'));
  const html = await r.text();
  const out = {};
  for (const m of html.matchAll(/'(w\|)?(\d{4}\/\d{2})\|(\d+)':\[\{src:'([^']+)'/g)) out[(m[1] ? 'w|' : '') + m[2] + '|' + m[3]] = m[4];
  return (cache.photos = out);
}

async function racePage(request, env, url, women, code, match, guide) {
  const origin = url.origin;
  const page = await env.ASSETS.fetch(new Request(origin + '/'));
  try {
    const data = await json(env, origin, women ? '/data-women.json' : '/data.json');
    const season = seasonOf(code);
    const race = (data.races || []).find(r => r.season === season && Number(r.match) === match);
    if (!race) return page;
    let clubs = {};
    try { clubs = (await json(env, origin, '/goat-ranks.json')).clubs || {}; } catch (e) {}
    const clubName = c => clubs[c] || null;  // unknown codes are left out rather than shown raw
    const venue = race.venue || 'Surrey League race';
    const when = longDate(race.date);
    const short = when ? when.replace(/ ([A-Z][a-z]{2})[a-z]+ /, ' $1 ') : `${season} match ${match}`;
    const W = women ? "women's " : '';
    const title = `${venue}, ${short}: ${guide ? W + 'form guide' : W + 'results'} | ${SITE_TITLE}`;
    const div = women ? "Women's Division 1" : 'Division 1';
    const bits = [`Surrey League ${div}, match ${match} of ${season}, at ${venue}${when ? ' on ' + when : ''}.`];
    const winner = (race.winner || '').split(' / ').map(n => n.trim()).filter(Boolean);
    const first = (race.results || []).find(x => Number(x.p ?? x.pos) === 1);  // the result line's club beats the race summary's
    const wClub = clubName((winner.length === 1 && first && (first.c || first.club)) || race.winnerClub);
    if (winner.length) bits.push(`Winner: ${winner.join(' and ')}${wClub ? ' (' + wClub + ')' : ''}.`);
    if (race.teamWinner) bits.push(`Team winners: ${clubName(race.teamWinner) || race.teamWinner}.`);
    if (race.finishers) bits.push(`${race.finishers} finishers.`);  // only the true field size, not the length of a partial results list
    const desc = bits.join(' ');
    // picture: the race photo if there is one, else the highest-placed runner with a portrait, else the winner's club vest
    let image = null, w = 600, h = 600, alt = '', large = false;
    try {
      const ph = (await racePhotos(env, origin))[(women ? 'w|' : '') + season + '|' + match];
      if (ph) { image = '/' + ph.replace(/^\//, ''); large = true; alt = `${venue}, ${short}`; w = h = 0; }
    } catch (e) {}
    if (!image) {
      try {
        const tops = await json(env, origin, '/portraits/race-tops.json');
        const f = tops[(women ? 'w/' : 'm/') + code + '-' + match];
        if (f) { image = `/portraits/og/athletes/${f}.png`; alt = 'Runner illustration'; }
      } catch (e) {}
    }
    if (!image && race.winnerClub && await exists(env, origin, `/portraits/og/clubs/${clubFile(race.winnerClub)}.png`)) { image = `/portraits/og/clubs/${clubFile(race.winnerClub)}.png`; alt = (clubName(race.winnerClub) || 'Club') + ' vest'; }
    const pageUrl = `${SITE}${women ? '/women' : ''}/race/${code}-${match}${guide ? '/form-guide' : ''}`;
    const setContent = v => ({ element(el) { el.setAttribute('content', v); } });
    let rw = new HTMLRewriter()
      .on('title', { element(el) { el.setInnerContent(title); } })
      .on('meta[property="og:title"]', setContent(title))
      .on('meta[property="og:description"]', setContent(desc))
      .on('meta[name="description"]', setContent(desc))
      .on('meta[property="og:url"]', setContent(pageUrl));
    if (image) {
      const extra = (w ? `<meta property="og:image:width" content="${w}"><meta property="og:image:height" content="${h}">` : '') + `<meta property="og:image:alt" content="${esc(alt)}">`;
      rw = rw
        .on('meta[property="og:image"]', setContent(SITE + image))
        .on('meta[name="twitter:card"]', setContent(large ? 'summary_large_image' : 'summary'))
        .on('head', { element(el) { el.append(extra, { html: true }); } });
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
    // poster download counter (see countSave in index.html): the address itself is what gets counted, so reply with nothing
    if (url.pathname.startsWith('/count/')) return new Response(null, { status: 204, headers: { 'Cache-Control': 'no-store' } });
    const m = url.pathname.match(/^\/(women\/)?athlete\/([^\/]+)\/?$/i);
    if (m && (request.method === 'GET' || request.method === 'HEAD')) {
      try {
        return await athletePage(request, env, url, !!m[1], slugOf(decodeURIComponent(m[2])).replace(/-poster$/, ''));  // /athlete/<slug>-poster is the opened sticker: same preview
      } catch (e) {
        return env.ASSETS.fetch(new Request(url.origin + '/'));
      }
    }
    const rm = url.pathname.match(/^\/(women\/)?race\/(\d{4})-(\d+)(\/form-guide)?\/?$/i);
    if (rm && (request.method === 'GET' || request.method === 'HEAD')) {
      try {
        return await racePage(request, env, url, !!rm[1], rm[2], parseInt(rm[3], 10), !!rm[4]);
      } catch (e) {
        return env.ASSETS.fetch(new Request(url.origin + '/'));
      }
    }
    if (/^\/analysis\/?$/i.test(url.pathname) && (request.method === 'GET' || request.method === 'HEAD')) {
      // the field depth analysis page: the normal site, with its own title and link preview
      try {
        const page = await env.ASSETS.fetch(new Request(url.origin + '/'));
        const title = `How deep was the field? | ${SITE_TITLE}`;
        const desc = 'Every Surrey League Division 1 race since 2016/17, men and women, ranked by how many finishers were in the UK 5K rankings or under a 5K form time.';
        const setContent = v => ({ element(el) { el.setAttribute('content', v); } });
        const res = new HTMLRewriter()
          .on('title', { element(el) { el.setInnerContent(title); } })
          .on('meta[property="og:title"]', setContent(title))
          .on('meta[property="og:description"]', setContent(desc))
          .on('meta[name="description"]', setContent(desc))
          .on('meta[property="og:url"]', setContent(SITE + '/analysis'))
          .transform(page);
        const out = new Response(res.body, res);
        out.headers.set('Cache-Control', 'public, max-age=300');
        return out;
      } catch (e) {
        return env.ASSETS.fetch(new Request(url.origin + '/'));
      }
    }
    return env.ASSETS.fetch(request);
  }
};
