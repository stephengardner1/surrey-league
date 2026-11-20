// Runs on GitHub every time new results or corrections are published to the site.
// Compares the site's data before and after the change, writes each follower's
// notifications, and hands them to the back office to send.
//
//   node notifier/notify.mjs <before-commit> <after-commit>
//
// Needs (GitHub repository secrets): SL_API (back office address), SL_ADMIN_KEY.
// DRY_RUN=1 prints what would be sent instead of sending.
//
//   node notifier/notify.mjs --rehearse
// Rehearsal: pretends the latest race of the season (men's and women's) has just been
// published, and sends what followers would get to the APPROVER phone(s) only.
import { execFileSync } from 'node:child_process';
import { diffLeague, messagesFor, LEAGUE_LABEL, seasonRaces, currentSeason } from './compose.mjs';

const args = process.argv.slice(2);
const REHEARSE = args[0] === '--rehearse';
const [before, after = 'HEAD'] = REHEARSE ? ['HEAD', 'HEAD'] : args;
const API = process.env.SL_API, KEY = process.env.SL_ADMIN_KEY, DRY = !!process.env.DRY_RUN;

// `node notifier/notify.mjs --check`: confirm GitHub can reach the back office. Sends nothing.
if (before === '--check') {
  if (!API || !KEY) { console.error('Missing secret: ' + (!API ? 'SL_API ' : '') + (!KEY ? 'SL_ADMIN_KEY' : '')); process.exit(1); }
  const r = await fetch(`${API}/admin/status`, { headers: { authorization: `Bearer ${KEY}` } });
  if (r.status === 401 || r.status === 403) { console.error('The back office rejected SL_ADMIN_KEY. Re-paste it from the private settings file.'); process.exit(1); }
  if (!r.ok) { console.error(`Back office replied ${r.status}. Check SL_API.`); process.exit(1); }
  console.log('Connection OK. Back office status:', JSON.stringify(await r.json()));
  process.exit(0);
}

function at(ref, path) {
  if (!ref || /^0+$/.test(ref)) return null;
  try { return JSON.parse(execFileSync('git', ['show', `${ref}:${path}`], { maxBuffer: 1 << 28 }).toString()); }
  catch { return null; }
}

// New results the fast race-day check (notifier/fast.mjs) has already sent straight from
// surreyleague.org: don't send those again when the full import arrives here.
//   "<season>|<league>|m<N>|results"             team and individual results both sent
//   "<season>|<league>|m<N>|results|individual"  only the individual results were sent
const announced = new Set();
if (!REHEARSE && !DRY && API && KEY) {
  try {
    const r = await fetch(`${API}/admin/announced`, { headers: { authorization: `Bearer ${KEY}` } });
    if (r.ok) for (const a of await r.json()) announced.add(a.key);
  } catch { /* back office unreachable: carry on, the batch step will report it */ }
}
const resultsKey = (e) => `${e.season}|${e.league}|m${e.match}|results`;
const individualOnly = new Set(); // thread ids of races whose individual results have already gone out

const portraits = at(after, 'files/portraits/portraits.json') || {};
const leagues = [];
for (const [league, file] of [['men', 'files/data.json'], ['women', 'files/data-women.json']]) {
  let prev = at(before, file);
  const next = at(after, file);
  if (!prev || !next) continue;
  if (REHEARSE) { // the same data, minus the latest race of the season: as if it had just arrived
    const season = currentSeason(next);
    const last = Math.max(0, ...seasonRaces(next, season).map((r) => r.match));
    prev = { ...prev, races: prev.races.filter((r) => !(r.season === season && r.match === last)) };
  }
  const events = diffLeague(prev, next, league).filter((e) => {
    if (e.type !== 'results') return true;
    if (announced.has(resultsKey(e))) { console.log(`${LEAGUE_LABEL[league]} match ${e.match} results were already sent by the fast race-day check.`); return false; }
    if (announced.has(resultsKey(e) + '|individual')) individualOnly.add(`${league}-${e.season}-m${e.match}`);
    return true;
  });
  if (events.length) leagues.push({ league, prev, next, events });
}
if (!leagues.length) { console.log('No new results, corrections or season changes. Nothing to send.'); process.exit(0); }

const summary = leagues.flatMap(({ league, next, events }) => events.map((e) => {
  const race = e.match && seasonRaces(next, e.season).find((r) => r.match === e.match);
  const where = race ? ` match ${e.match} at ${race.venue}` : '';
  const what = { results: 'provisional results', corrections: `${e.changes?.length || ''} correction${e.changes?.length === 1 ? '' : 's'}`, complete: 'season complete', confirmed: 'results confirmed', champ: `individual standings (${e.stage})` }[e.type];
  return `${LEAGUE_LABEL[league]}${where}: ${what}`;
})).filter((v, i, a) => a.indexOf(v) === i).join('; ');
console.log('Changes:', summary);

let devices;
if (DRY) {
  devices = [
    { token: 'demo-men', follow: { men: true, corrections: true, clubs: [], runners: [] } },
    { token: 'demo-bel', follow: { men: true, women: true, corrections: true, clubs: ['BEL'], runners: [] } },
  ];
} else {
  if (!API || !KEY) { console.error('SL_API and SL_ADMIN_KEY must be set.'); process.exit(1); }
  const r = await fetch(`${API}/admin/devices`, { headers: { authorization: `Bearer ${KEY}` } });
  if (!r.ok) { console.error('Could not get the followers list:', r.status); process.exit(1); }
  devices = await r.json();
  if (REHEARSE) {
    const all = devices.length;
    devices = devices.filter((d) => d.admin);
    console.log(`Rehearsal: sending to the ${devices.length} approver phone(s) only (${all} phones registered).`);
    if (!devices.length) { console.error('No approver phone yet. In the app, open Notifications, tap Approver code and enter the code, then run this again.'); process.exit(1); }
  }
}

// Group identical notifications so each is stored once with all its recipients
const groups = new Map();
for (const d of devices) {
  for (const { league, prev, next, events } of leagues) {
    for (const m of messagesFor(d.follow, events, { prev, next, portraits })) {
      if (m.title === 'Surrey League provisional individual results' && individualOnly.has(m.threadId)) continue;
      const k = JSON.stringify([m.title, m.body, m.image, m.url, m.threadId]);
      if (!groups.has(k)) groups.set(k, { ...m, tokens: [] });
      groups.get(k).tokens.push(d.token);
    }
  }
}
const messages = [...groups.values()];
console.log(`${messages.length} different notifications for ${devices.length} phones.`);
if (DRY) {
  for (const m of messages) console.log(`\n[${m.tokens.length} phones] ${m.title}\n${m.body}`);
  process.exit(0);
}
if (!messages.length) process.exit(0);
const r = await fetch(`${API}/admin/batch`, {
  method: 'POST', headers: { authorization: `Bearer ${KEY}`, 'content-type': 'application/json' },
  body: JSON.stringify({ summary: (REHEARSE ? 'REHEARSAL (tap Don’t send): ' : '') + summary, messages }),
});
console.log('Back office replied:', r.status, await r.text());
if (!r.ok) process.exit(1);
// Record the new results sent here, so a late fast check doesn't send them a second time
const keys = REHEARSE ? [] : leagues.flatMap(({ events }) => events.filter((e) => e.type === 'results').map(resultsKey));
if (keys.length) await fetch(`${API}/admin/announced`, { method: 'POST', headers: { authorization: `Bearer ${KEY}`, 'content-type': 'application/json' }, body: JSON.stringify({ key: keys }) }).catch(() => {});
