// Runs on GitHub every time new results or corrections are published to the site.
// Compares the site's data before and after the change, writes each follower's
// notifications, and hands them to the back office to send.
//
//   node notifier/notify.mjs <before-commit> <after-commit>
//
// Needs (GitHub repository secrets): SL_API (back office address), SL_ADMIN_KEY.
// DRY_RUN=1 prints what would be sent instead of sending.
import { execFileSync } from 'node:child_process';
import { diffLeague, messagesFor, LEAGUE_LABEL, seasonRaces } from './compose.mjs';

const [before, after = 'HEAD'] = process.argv.slice(2);
const API = process.env.SL_API, KEY = process.env.SL_ADMIN_KEY, DRY = !!process.env.DRY_RUN;

function at(ref, path) {
  if (!ref || /^0+$/.test(ref)) return null;
  try { return JSON.parse(execFileSync('git', ['show', `${ref}:${path}`], { maxBuffer: 1 << 28 }).toString()); }
  catch { return null; }
}

const portraits = at(after, 'files/portraits/portraits.json') || {};
const leagues = [];
for (const [league, file] of [['men', 'files/data.json'], ['women', 'files/data-women.json']]) {
  const prev = at(before, file), next = at(after, file);
  if (!prev || !next) continue;
  const events = diffLeague(prev, next, league);
  if (events.length) leagues.push({ league, prev, next, events });
}
if (!leagues.length) { console.log('No new results, corrections or season changes. Nothing to send.'); process.exit(0); }

const summary = leagues.flatMap(({ league, next, events }) => events.map((e) => {
  const race = e.match && seasonRaces(next, e.season).find((r) => r.match === e.match);
  const where = race ? ` match ${e.match} at ${race.venue}` : '';
  const what = { results: 'provisional results', corrections: `${e.changes?.length || ''} correction${e.changes?.length === 1 ? '' : 's'}`, complete: 'season complete', champ: `individual standings (${e.stage})` }[e.type];
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
}

// Group identical notifications so each is stored once with all its recipients
const groups = new Map();
for (const d of devices) {
  for (const { league, prev, next, events } of leagues) {
    for (const m of messagesFor(d.follow, events, { prev, next, portraits })) {
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
  body: JSON.stringify({ summary, messages }),
});
console.log('Back office replied:', r.status, await r.text());
if (!r.ok) process.exit(1);
