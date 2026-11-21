// Start times for matches that haven't happened yet, read from surreyleague.org and saved to
// files/fixture-times.json for the site's pre-race pages. Run daily by the "Fixture times" Action,
// so if the league changes a start time the site follows within a day.
//   node tools/fixture_times.mjs        (writes the file only if something changed)
// The matches to look at are the same list the fast race-day check uses (FAST_MATCHES in
// iphone-app/worker/wrangler.toml).
import { readFileSync, writeFileSync, existsSync } from 'node:fs';

const OUT = 'files/fixture-times.json';
const toml = readFileSync('iphone-app/worker/wrangler.toml', 'utf8');
const list = JSON.parse((toml.match(/^FAST_MATCHES\s*=\s*'([^']+)'/m) || [])[1] || '[]');
const seasonOf = (date) => { const y = +date.slice(0, 4), m = +date.slice(5, 7); const a = m >= 8 ? y : y - 1; return `${a}/${String(a + 1).slice(-2)}`; };
const clean = (s) => s.replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();
// "12:15 p.m." / "2 p.m." / "noon" -> "12:15"
function to24(t) {
  const s = t.toLowerCase().replace(/\./g, '');
  if (s === 'noon') return '12:00';
  const m = s.match(/^(\d{1,2})(?::(\d\d))?\s*(am|pm)$/);
  if (!m) return null;
  let h = +m[1] % 12; if (m[3] === 'pm') h += 12;
  return `${String(h).padStart(2, '0')}:${m[2] || '00'}`;
}
async function get(url, as) {
  for (let i = 0; i < 3; i++) {
    try { const r = await fetch(url, { headers: { 'user-agent': 'slarchive.org fixture check' } }); if (r.ok) return await r[as](); } catch { /* try again */ }
    await new Promise((res) => setTimeout(res, 2000));
  }
  throw new Error('Could not read ' + url);
}

const out = existsSync(OUT) ? JSON.parse(readFileSync(OUT, 'utf8')) : {};
const today = new Date().toISOString().slice(0, 10);
for (const m of list) {
  if (m.date < today) continue; // already run: leave whatever was last saved
  const [page, feed] = await Promise.all([get(`https://www.surreyleague.org/match/${m.id}/`, 'text'), get(`https://www.surreyleague.org/match/${m.id}/json/`, 'json')]);
  const entry = { date: feed.startDate || m.date, confirmed: !!feed.status && feed.status !== 'tentative' };
  for (const row of page.match(/<tr[\s\S]*?<\/tr>/g) || []) {
    const cells = (row.match(/<t[dh][^>]*>[\s\S]*?<\/t[dh]>/g) || []).map(clean);
    for (const [name, key] of [['Senior Men', 'men'], ['Senior Women', 'women']]) {
      const i = cells.indexOf(name);
      if (i >= 0 && cells[i + 1] && to24(cells[i + 1])) entry[key] = to24(cells[i + 1]);
    }
  }
  if (!entry.men && !entry.women) { console.log(`Match ${m.match}: no senior start times on the league's page; left as it was.`); continue; }
  const season = seasonOf(m.date);
  (out[season] ||= {})[String(m.match)] = entry;
  console.log(`Match ${m.match} (${m.date}): men ${entry.men || '?'}, women ${entry.women || '?'}, ${entry.confirmed ? 'confirmed' : 'to be confirmed'}`);
}
const text = JSON.stringify(out, null, 1) + '\n';
if (!existsSync(OUT) || readFileSync(OUT, 'utf8') !== text) { writeFileSync(OUT, text); console.log('Saved ' + OUT); } else console.log('No change.');
