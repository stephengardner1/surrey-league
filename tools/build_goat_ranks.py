"""Builds files/goat-ranks.json: every athlete's club GOAT rank (the 🐐 #n on their profile),
so link previews can say "the #3🐐 of Belgrave Harriers".
It opens the site in a headless browser and uses the site's own data loading and name aliases,
then repeats the profile page's ranking sum for every club, so the numbers always match the site.
Run from the repo root after importing results:  python3 tools/build_goat_ranks.py"""
import os, json, subprocess, time
from playwright.sync_api import sync_playwright
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'files')
JS = r"""
async () => {
  const csv = await fetch(ALIASES_URL).then(r => r.text()).catch(() => '');
  const aliases = {...BUILTIN_ALIASES, ...(csv ? parseAliases(csv) : {}), ...(typeof OVERRIDE_ALIASES!=='undefined'?OVERRIDE_ALIASES:{})};
  const slug = n => (n || '').toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  const out = {clubs: {}};
  for (const c of Object.keys(CLUBS)) out.clubs[c] = CLUBS[c].name || c;
  for (const [div, file] of [['men', 'data.json'], ['women', 'data-women.json']]) {
    const raw = await fetch(file).then(r => r.json());
    const rawCopy = JSON.parse(JSON.stringify(raw));
    const data = normalizeData(raw, div, aliases);
    const dc = DIVISIONS[div] || DIVISIONS.men;
    const hidden = new Set(Object.entries(CLUBS).filter(([k, v]) => v.hidden).map(([k]) => k)); hidden.add('G');
    const stats = {};  // club -> normalized name -> {name, value}
    const add = (club, name, v) => { if (isUnknownAthlete(name)) return; const k = normalizeNameForCompare(name); (stats[club] ||= {}); (stats[club][k] ||= {name, value: 0}); stats[club][k].value += v; };
    for (const race of data.races) {
      const ts = (dc.historicTeamSize?.(race.season) || dc.teamSize || {a: 10, b: 10}).a;
      if (!race.results?.length) {
        if (race.winners) race.winners.forEach(w => w.club && add(w.club, w.name, ts));
        else if (race.winner && race.winnerClub) add(race.winnerClub, race.winner, ts);
        continue;
      }
      const byClub = {};
      for (const r of race.results) if (r.club && !r.ns) (byClub[r.club] ||= []).push(r);
      for (const [club, rs] of Object.entries(byClub)) {
        const scorers = race.results.filter(x => x.club === club && x.pts != null && x.b_pts == null && !x.ns);
        for (const r of rs) {
          const p = scorers.findIndex(x => namesMatch(x.name, r.name)) + 1;
          add(club, r.name, p >= 1 && p <= ts ? ts - p + 1 : 0);
        }
      }
    }
    const ranks = {};
    for (const [club, m] of Object.entries(stats)) {
      if (hidden.has(club)) continue;
      Object.values(m).sort((a, b) => b.value - a.value).forEach((a, i) => { (ranks[slug(a.name)] ||= {})[club] = i + 1; });
    }
    for (const [from, to] of Object.entries(aliases)) if (ranks[slug(to)] && !ranks[slug(from)]) ranks[slug(from)] = ranks[slug(to)];
    // raw spellings in the data file (what the link-preview worker sees) -> the site's merged name
    const key = r => r.season + '|' + r.match;
    const norm = {}; for (const r of data.races) norm[key(r)] = r;
    for (const r of rawCopy.races || []) {
      const n = norm[key(r)]; const rr = r.results || [];
      if (!n || !n.results || n.results.length !== rr.length) continue;
      rr.forEach((x, i) => { const s = slug(x.n || x.name), to = slug(n.results[i].name); if (s !== to && ranks[to] && !ranks[s]) ranks[s] = ranks[to]; });
    }
    out[div] = ranks;
  }
  return out;
}
"""
srv = subprocess.Popen(['python3', '-m', 'http.server', '8766'], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    time.sleep(1)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        pg.goto('http://localhost:8766/'); pg.wait_for_function('typeof normalizeData === "function"', timeout=60000)
        res = pg.evaluate(JS); b.close()
finally:
    srv.terminate()
json.dump(res, open(os.path.join(ROOT, 'goat-ranks.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
print(len(res['men']), 'men,', len(res['women']), 'women ranked')
