// Prints the notifications different followers would receive, using the real
// 2026/27 Match 1 results, plus made-up corrections and a made-up rest of season
// to exercise every rule. Run: npm run test-notifications
import { readFileSync, existsSync } from 'node:fs';
import { diffLeague, messagesFor, currentSeason } from '../../notifier/compose.mjs';

const SRC = process.env.SITE_FILES || (existsSync('../files/data.json') ? '../files' : '.site-cache/files');
const load = (f) => JSON.parse(readFileSync(`${SRC}/${f}`, 'utf8'));
const portraits = existsSync(`${SRC}/portraits/portraits.json`) ? load('portraits/portraits.json') : {};
const clone = (x) => structuredClone(x);

const PROFILES = {
  'Men\'s league only': { men: true, women: false, corrections: true, clubs: [], runners: [] },
  'Men\'s league + THH + Sam Tyas': { men: true, women: false, corrections: true, clubs: ['THH'], runners: [{ name: 'Sam Tyas', league: 'men' }] },
  'Men\'s league + BEL': { men: true, women: false, corrections: true, clubs: ['BEL'], runners: [] },
  'Sam Tyas only': { men: false, women: false, corrections: true, clubs: [], runners: [{ name: 'Sam Tyas', league: 'men' }] },
  'Women\'s league + BEL': { men: false, women: true, corrections: true, clubs: ['BEL'], runners: [] },
  'Both leagues + WOK': { men: true, women: true, corrections: true, clubs: ['WOK'], runners: [] },
};

function show(heading, league, prev, next) {
  console.log('\n' + '='.repeat(72) + '\n' + heading + '\n' + '='.repeat(72));
  const events = diffLeague(prev, next, league);
  console.log('Events:', events.map((e) => e.type + (e.stage ? ':' + e.stage : '') + (e.match ? ' m' + e.match : '') + (e.changes ? ` (${e.changes.length} changes)` : '')).join(', ') || 'none');
  for (const [name, follow] of Object.entries(PROFILES)) {
    const msgs = messagesFor(follow, events, { prev, next, portraits });
    console.log(`\n--- ${name}: ${msgs.length ? msgs.length + ' notification(s)' : 'nothing'}`);
    for (const m of msgs) {
      const pic = m.image ? (m.image.type === 'portrait' ? `portrait ${m.image.file}` : `singlet ${m.image.club}`) : 'no picture';
      console.log(`  [Surrey League] ${m.title}   (${pic})`);
      for (const line of m.body.split('\n')) console.log('    ' + line);
    }
  }
}

// ---------- Men: Match 1 arrives ----------
const men = load('data.json');
const season = currentSeason(men);
const menBefore = clone(men);
menBefore.races = menBefore.races.filter((r) => !(r.season === season && r.match === 1));
show('MEN: Match 1 results arrive (real data)', 'men', menBefore, men);

// ---------- Men: one correction (a THH runner added in 57th) ----------
const menFix1 = clone(men);
{
  const race = menFix1.races.find((r) => r.season === season && r.match === 1);
  for (const r of race.results) if (r.p >= 57) r.p += 1;
  race.results.push({ p: 57, n: 'Test Runner', c: 'THH', t: '26:40', s: 57 });
  race.results.sort((a, b) => a.p - b.p);
  race.teamScores.find((t) => t.club === 'THH').score += 7;
  menFix1.seasonsData[season].standings.find((t) => t.club === 'THH').m1 += 7;
}
show('MEN: one correction (made up: Test Runner, THH, added in 57th)', 'men', men, menFix1);

// ---------- Men: five corrections that swap HHH and THH ----------
const menFix5 = clone(men);
{
  const race = menFix5.races.find((r) => r.season === season && r.match === 1);
  const tyas = race.results.find((r) => r.n === 'Sam Tyas');
  const ahead = race.results.find((r) => r.p === tyas.p - 1);
  ahead.p += 1; tyas.p -= 1;
  for (const n of ['Daniel Shaw', 'Tom Austin', 'Rowan Board']) race.results.find((r) => r.n === n).t = '26:59';
  race.results.find((r) => r.n === 'Liam Burthem').c = 'KEN';
  race.results.sort((a, b) => a.p - b.p);
  const ts = (c) => race.teamScores.find((t) => t.club === c);
  ts('THH').score = 360; ts('HHH').score = 375; ts('BEL').score = 323;
  const st = (c) => menFix5.seasonsData[season].standings.find((t) => t.club === c);
  st('THH').m1 = 360; st('HHH').m1 = 375; st('BEL').m1 = 323;
}
show('MEN: five corrections in one update (made up)', 'men', men, menFix5);

// ---------- Men: a made-up rest of season, to show League lines, match 4 and the Mitchell Cup ----------
function addMatch(data, match, venue, shuffle, teamDelta) {
  const d = clone(data);
  const m1 = d.races.find((r) => r.season === season && r.match === 1);
  const race = clone(m1);
  race.match = match; race.venue = venue; race.provisional = true; race.officialStatus = 'provisional';
  const rs = race.results;
  for (const [i, j] of shuffle) { const a = rs[i].p; rs[i].p = rs[j].p; rs[j].p = a; }
  rs.sort((a, b) => a.p - b.p);
  race.teamScores = m1.teamScores.map((t) => ({ club: t.club, score: t.score + (teamDelta[t.club] || 0) }));
  d.races.push(race);
  for (const t of d.seasonsData[season].standings) t['m' + match] = race.teamScores.find((x) => x.club === t.club).score;
  return d;
}
const menM2 = addMatch(men, 2, 'Beckenham Place Park', [[0, 1]], { THH: -60, HHH: 10, DUL: -40, WOK: -50 });
show('MEN: Match 2 arrives (made-up results, to show League lines)', 'men', men, menM2);
const menM3 = addMatch(menM2, 3, 'Godalming', [[1, 2]], { THH: -50, WOK: -30 });
const menM4 = addMatch(menM3, 4, 'Morden Park', [[0, 2]], { THH: -40 });
show('MEN: Match 4 arrives (made up): final standings + Mitchell Cup', 'men', menM3, menM4);
const menDone = clone(menM4);
menDone.races.find((r) => r.season === season && r.match === 4).officialStatus = 'completed';
show('MEN: Match 4 results marked complete (made up)', 'men', menM4, menDone);

// ---------- Women: Match 1 arrives ----------
const women = load('data-women.json');
const womenBefore = clone(women);
womenBefore.races = womenBefore.races.filter((r) => !(r.season === season && r.match === 1));
show('WOMEN: Match 1 results arrive (real data)', 'women', womenBefore, women);
