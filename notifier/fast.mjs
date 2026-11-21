// Fast race-day results: "first person in the pub to know".
//
// Started by the back office (Cloudflare) the moment a senior race appears in the league's
// own results feed, before the full results have been imported into slarchive.org.
// Builds the new race straight from surreyleague.org, writes each follower's "provisional
// results" notifications with the usual wording engine, and hands them to the back office
// marked auto, so they go straight out with no approval step.
//
//   node notifier/fast.mjs <league match id> "Senior Men" | "Senior Women"
//
//   --rehearse   pretend the race isn't on slarchive.org yet and send to the APPROVER phone(s) only
//   DRY_RUN=1    print what would be sent to two made-up followers; sends nothing
//
// Needs (GitHub repository secrets): SL_API (back office address), SL_ADMIN_KEY.
import { readFileSync } from 'node:fs';
import { diffLeague, messagesFor, LEAGUE_LABEL, currentSeason, teamResult } from './compose.mjs';

const SITE = 'https://www.surreyleague.org';
const flags = process.argv.slice(2).filter((a) => a.startsWith('--'));
const [matchId, raceName] = process.argv.slice(2).filter((a) => !a.startsWith('--'));
const REHEARSE = flags.includes('--rehearse');
const API = process.env.SL_API, KEY = process.env.SL_ADMIN_KEY, DRY = !!process.env.DRY_RUN;
const LEAGUES = { 'Senior Men': ['men', 'files/data.json'], 'Senior Women': ['women', 'files/data-women.json'] };

if (!/^\d+$/.test(matchId || '') || !LEAGUES[raceName]) {
  console.error('Usage: node notifier/fast.mjs <league match id> "Senior Men" | "Senior Women"');
  process.exit(1);
}
const [league, file] = LEAGUES[raceName];
const fastKey = `${matchId}|${raceName}`;
const admin = (path, body) => fetch(`${API}${path}`, {
  method: body ? 'POST' : 'GET',
  headers: { authorization: `Bearer ${KEY}`, 'content-type': 'application/json' },
  body: body ? JSON.stringify(body) : undefined,
});
async function get(url, as) {
  for (let i = 0; i < 3; i++) {
    try { const r = await fetch(url, { headers: { 'user-agent': 'slarchive.org results check' } }); if (r.ok) return await r[as](); } catch { /* try again */ }
    await new Promise((res) => setTimeout(res, 2000));
  }
  throw new Error('Could not read ' + url);
}

// ---------- 1. the race, from the league's feed ----------
const feed = await get(`${SITE}/match/${matchId}/json/`, 'json');
const res = (feed.results || []).find((r) => r.name === raceName);
if (!res || !(res.positions || []).length) { console.log(`${raceName} has no results in the league's feed yet. Nothing to send.`); process.exit(0); }
const raceDate = (res.startTime || feed.startDate || '').slice(0, 10);

let data = JSON.parse(readFileSync(file, 'utf8'));
const season = currentSeason(data);
const fixture = ((data.seasonsData[season] || {}).matches || []).find((m) => m.date === raceDate);
if (!fixture) { console.error(`No ${season} match on ${raceDate} in ${file}; can't tell which match this is.`); process.exit(1); }
const match = fixture.num;
const announceKey = `${season}|${league}|m${match}|results`;
const already = data.races.some((r) => r.season === season && r.match === match);

if (REHEARSE && already) { // take the race back out, as if it had not been imported yet
  data = { ...data, races: data.races.filter((r) => !(r.season === season && r.match === match)),
    seasonsData: { ...data.seasonsData, [season]: { ...data.seasonsData[season],
      standings: data.seasonsData[season].standings.map((t) => { const c = { ...t }; delete c['m' + match]; return c; }) } } };
} else if (already) {
  console.log(`${LEAGUE_LABEL[league]} match ${match} is already on slarchive.org: the normal notifier has it. Nothing to send.`);
  if (!DRY && API && KEY) await admin('/admin/announced', { fast: fastKey });
  process.exit(0);
}

// Names as slarchive.org spells them, so runner followers match
const lc = (s) => s.toLowerCase();
const alias = new Map();
for (const src of [data.aliases, data.nameAliases]) for (const [k, v] of Object.entries(src || {})) if (typeof v === 'string') alias.set(lc(k), v);
const known = new Map((data.athletes || []).filter((a) => a && a.name).map((a) => [lc(a.name), a.name]));
function siteName(given, family) {
  const n = `${given || ''} ${family || ''}`.replace(/\s+/g, ' ').trim();
  if (!n) return 'Unknown';
  return alias.get(lc(n)) || known.get(lc(n)) || n;
}
const results = res.positions
  .filter((p) => Number.isInteger(p.rank) && p.rank > 0)
  .map((p) => ({ p: p.rank, n: siteName(p.givenName, p.familyName), c: (p.club || '').trim(), t: p.perf || '' }))
  .sort((a, b) => a.p - b.p);

// ---------- 2. team scores, from the league's race page ----------
const unescape = (s) => s.replace(/&amp;/g, '&').replace(/&#x27;|&#39;/g, "'").trim();
async function teamScores() {
  const matchPage = await get(`${SITE}/match/${matchId}/`, 'text');
  const link = matchPage.match(new RegExp('<a href="/race/(\\d+)/">\\s*' + raceName + '\\s*</a>'));
  if (!link) return [];
  const page = await get(`${SITE}/race/${link[1]}/`, 'text');
  const a = page.indexOf('>Match results<');
  if (a < 0) return [];
  let b = page.indexOf('>B team results<', a);
  if (b < 0) b = page.indexOf('>Individual results<', a);
  const table = page.slice(a, b < 0 ? undefined : b);
  const rows = [];
  const re = /<tr class="rank-\d+ team-row"[\s\S]*?team-scores-name[^>]*>([^<]+)<[\s\S]*?<td class="text-center">\s*(\d+(?:\.\d+)?)\s*<\/td>/g;
  for (let m; (m = re.exec(table));) rows.push({ club: unescape(m[1]), score: Number(m[2]) });
  return rows;
}
let teams = [];
try { teams = await teamScores(); } catch (e) { console.log('Could not read team scores:', e.message); }
// Only trust team rows for clubs that actually have runners in this race
const racing = new Set(results.map((r) => r.c));
teams = teams.filter((t) => racing.has(t.club) && Number.isFinite(t.score));
console.log(`${LEAGUE_LABEL[league]} match ${match} at ${fixture.venue}: ${results.length} finishers, ${teams.length} team scores.`);

// ---------- 3. the data as it will look once this race is imported ----------
const race = league === 'men'
  ? { season, match, venue: fixture.venue, date: raceDate, results, officialStatus: 'provisional', provisional: true }
  : { season, match, venue: fixture.venue, date: raceDate, results: results.map((r) => ({ pos: r.p, name: r.n, club: r.c, time: r.t })), officialStatus: 'provisional', provisional: true };
const standings = data.seasonsData[season].standings.map((t) => ({ ...t }));
if (teams.length) {
  race.teamScores = teams;
  for (const t of teams) {
    let row = standings.find((s) => s.club === t.club);
    if (!row) standings.push((row = { club: t.club }));
    row['m' + match] = t.score;
  }
}
const next = { ...data, races: [...data.races, race], seasonsData: { ...data.seasonsData, [season]: { ...data.seasonsData[season], standings } } };
const events = diffLeague(data, next, league).filter((e) => e.type === 'results' && e.match === match);
if (!events.length) { console.log('Nothing new to announce.'); process.exit(0); }
const withTeams = teamResult(next, season, match).length > 0;

// ---------- 4. who gets what ----------
let portraits = {};
try { portraits = JSON.parse(readFileSync('files/portraits/portraits.json', 'utf8')); } catch { /* singlets instead */ }
let devices;
if (DRY) {
  devices = [
    { token: 'demo-league', follow: { men: true, women: true, corrections: true, clubs: [], runners: [] } },
    { token: 'demo-bel', follow: { men: true, women: true, corrections: true, clubs: ['BEL'], runners: [] } },
    { token: 'demo-runner', follow: { men: false, women: false, corrections: true, clubs: [], runners: [{ name: results[Math.min(19, results.length - 1)].n, league }] } },
  ];
} else {
  if (!API || !KEY) { console.error('SL_API and SL_ADMIN_KEY must be set.'); process.exit(1); }
  if (!REHEARSE) { // someone else may have announced it in the last few seconds
    const r = await admin('/admin/announced');
    if (r.ok && (await r.json()).some((a) => a.key === announceKey)) {
      console.log('Already announced. Nothing to send.');
      await admin('/admin/announced', { fast: fastKey });
      process.exit(0);
    }
  }
  const r = await admin('/admin/devices');
  if (!r.ok) { console.error('Could not get the followers list:', r.status); process.exit(1); }
  devices = await r.json();
  if (REHEARSE) {
    const all = devices.length;
    devices = devices.filter((d) => d.admin);
    console.log(`Rehearsal: sending to the ${devices.length} approver phone(s) only (${all} phones registered).`);
    if (!devices.length) { console.error('No approver phone registered.'); process.exit(1); }
  }
}

const groups = new Map();
for (const d of devices) {
  for (const m0 of messagesFor(d.follow, events, { prev: data, next, portraits })) {
    const m = m0; // a tap opens the race page, drawn from the "first results" copy left below
    const k = JSON.stringify([m.title, m.body, m.image, m.url, m.threadId]);
    if (!groups.has(k)) groups.set(k, { ...m, tokens: [] });
    groups.get(k).tokens.push(d.token);
  }
}
const messages = [...groups.values()];
const summary = `${REHEARSE ? 'REHEARSAL: ' : ''}${LEAGUE_LABEL[league]} match ${match} at ${fixture.venue}: provisional results, sent straight from surreyleague.org${withTeams ? '' : ' (individual only, no team scores yet)'}`;
console.log(summary);
console.log(`${messages.length} different notifications for ${devices.length} phones.`);
if (DRY) {
  for (const m of messages) console.log(`\n[${m.tokens.join(', ')}] ${m.title}\n${m.body}\n(picture: ${JSON.stringify(m.image)}; opens ${m.url})`);
  process.exit(0);
}

// Leave a "first results" copy of the race with the back office. slarchive.org and the app show
// it as the race page (marked as first results, more to come) until the full import is published.
if (!REHEARSE) {
  const live = await admin('/admin/live', { key: `${season}|${league}|m${match}`, league,
    race: { season, match, venue: fixture.venue, date: raceDate, results, teamScores: teams, source: `${SITE}/match/${matchId}/` } });
  console.log('First-results page copy stored:', live.status);
}

// The back office records the key and takes the batch in one step, so it can never go out twice.
// Without team scores only the individual results are claimed: the team results follow from the full import.
const body = { summary, messages, auto: true };
if (!REHEARSE) { body.claim = withTeams ? announceKey : announceKey + '|individual'; body.fast = fastKey; }
if (REHEARSE) await admin('/admin/announced', { fast: fastKey }); // a drill started by the back office: tell it this race is dealt with, so it doesn't ring again
if (!messages.length) { console.log('Nothing to send to those phones.'); process.exit(0); }
const sent = await admin('/admin/batch', body);
console.log('Back office replied:', sent.status, await sent.text());
if (!sent.ok) process.exit(1);
