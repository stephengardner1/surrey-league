// Surrey League Compendium: notification wording engine.
// Pure functions, no network. Used by the notifier (GitHub Action) and by the
// test script. The rules follow the project doc claude/app-notifications-spec.md.
//
// Vocabulary
//   league   'men' | 'women'
//   data     the parsed files/data.json or files/data-women.json
//   follow   { men, women, corrections, clubs: ['BEL'], runners: [{ name, league }] }
//   event    something that happened between two versions of the data
//   message  { title, body, image, threadId, url }  (one push notification)

export const LEAGUE_LABEL = { men: 'Men’s', women: 'Women’s' };
const LEAGUE_LOWER = { men: 'men’s', women: 'women’s' };
const RELEGATION = { men: 2, women: 3 };
const CHAMP = {
  men: { name: 'Mitchell Cup', short: 'Mitchell Cup', count: 4, rule: 'all4' },
  women: { name: 'Women’s individual championship', short: 'individual championship', count: 3, rule: 'best3of4' },
};
const ARROW = ' ◂';

// ---------- small helpers ----------
export function ord(n) {
  const v = n % 100;
  if (v >= 11 && v <= 13) return n + 'th';
  return n + ({ 1: 'st', 2: 'nd', 3: 'rd' }[n % 10] || 'th');
}
const WORDS = ['', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth',
  'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth', 'twentieth'];
export const ordWord = (n) => WORDS[n] || ord(n);
export const slugOf = (n) => (n || '').toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
const key = (r) => (r.n + '|' + r.c).toLowerCase();

// Both data files describe a race slightly differently; normalise to one shape.
export function normRace(race) {
  if (!race) return null;
  const results = (race.results || []).map((x) => ({
    p: x.p ?? x.pos, n: x.n ?? x.name, c: x.c ?? x.club, t: x.t ?? x.time,
  })).filter((x) => x.n && x.p).sort((a, b) => a.p - b.p);
  return {
    season: race.season, match: race.match, venue: race.venue,
    provisional: race.provisional !== false, // missing flag = treat as provisional
    provisionalFlag: race.provisional,
    teamScores: race.teamScores || null,
    results,
  };
}

export function currentSeason(data) {
  const seasons = Object.keys(data.seasonsData || {}).sort();
  return seasons[seasons.length - 1];
}

export function seasonRaces(data, season) {
  return (data.races || []).filter((r) => r.season === season).map(normRace).sort((a, b) => a.match - b.match);
}

export function matchesPerSeason(data, season) {
  const s = (data.seasonsData || {})[season];
  return (s && s.matches && s.matches.length) || (data.config && data.config.matchesPerSeason) || 4;
}

// Team result for one match: [{ club, pts, pos }], best first.
export function teamResult(data, season, match) {
  const race = (data.races || []).find((r) => r.season === season && r.match === match);
  let rows = race && race.teamScores ? race.teamScores.map((t) => ({ club: t.club, pts: t.score })) : null;
  if (!rows) {
    const s = (data.seasonsData || {})[season];
    rows = (s ? s.standings : []).filter((t) => t['m' + match] != null).map((t) => ({ club: t.club, pts: t['m' + match] }));
  }
  rows.sort((a, b) => a.pts - b.pts);
  return withTies(rows);
}

// Equal points share a position, shown as "=2"
function withTies(rows) {
  let pos = 0;
  return rows.map((t, i) => {
    if (i === 0 || t.pts !== rows[i - 1].pts || t.ran !== rows[i - 1].ran) pos = i + 1;
    const tie = rows.some((u, j) => j !== i && u.pts === t.pts && u.ran === t.ran);
    return { ...t, pos, tie };
  });
}
const posLabel = (t) => (t.tie ? '=' : '') + t.pos;

// League table after a given match: [{ club, pts, pos }], lowest total first.
export function leagueTable(data, season, upTo) {
  const s = (data.seasonsData || {})[season];
  if (!s) return [];
  const rows = s.standings.map((t) => {
    let pts = 0, ran = 0;
    for (let m = 1; m <= upTo; m++) { if (t['m' + m] != null) { pts += t['m' + m]; ran++; } }
    return { club: t.club, pts, ran };
  }).filter((t) => t.ran > 0);
  // A club that missed a match ranks below those that ran them all
  rows.sort((a, b) => b.ran - a.ran || a.pts - b.pts);
  return withTies(rows);
}

// Mitchell Cup (men: total of all four positions) / women's individual championship (best 3 of 4).
export function champTable(data, league, season) {
  const races = seasonRaces(data, season);
  const per = new Map();
  for (const race of races) {
    const seen = new Set();
    for (const r of race.results) {
      if (/^unknown/i.test(r.n)) continue;
      const k = key(r);
      if (seen.has(k)) continue; // two runners sharing a name and club: count the first only
      seen.add(k);
      if (!per.has(k)) per.set(k, { n: r.n, c: r.c, scores: [] });
      per.get(k).scores.push(r.p);
    }
  }
  const cfg = CHAMP[league];
  const rows = [];
  for (const a of per.values()) {
    if (a.scores.length < cfg.count) continue;
    const best = [...a.scores].sort((x, y) => x - y).slice(0, cfg.count);
    rows.push({ n: a.n, c: a.c, pts: best.reduce((x, y) => x + y, 0) });
  }
  rows.sort((a, b) => a.pts - b.pts);
  return withTies(rows.map((r) => ({ ...r, ran: 0 })));
}

// ---------- detecting what changed ----------
// Compare two versions of one league's data. Returns a list of events.
export function diffLeague(prev, next, league) {
  const events = [];
  const season = currentSeason(next);
  const total = matchesPerSeason(next, season);
  const before = new Map(seasonRaces(prev || {}, season).map((r) => [r.match, r]));
  for (const race of seasonRaces(next, season)) {
    const old = before.get(race.match);
    if (!old) {
      events.push({ type: 'results', league, season, match: race.match, final: race.match === total });
      if (race.match === total) {
        events.push({ type: 'champ', league, season, stage: 'provisional' });
        if (race.provisionalFlag === false) { // arrived already marked complete
          events.push({ type: 'complete', league, season, match: race.match });
          events.push({ type: 'champ', league, season, stage: 'confirmed' });
        }
      }
      continue;
    }
    const changes = raceChanges(old, race);
    const teamsChanged = JSON.stringify(teamResult(prev, season, race.match)) !== JSON.stringify(teamResult(next, season, race.match));
    if (changes.length || teamsChanged) {
      events.push({ type: 'corrections', league, season, match: race.match, changes, final: race.match === total });
      if (race.match === total) {
        const a = champTable(prev, league, season).slice(0, 3).map((x) => x.n).join('|');
        const b = champTable(next, league, season).slice(0, 3).map((x) => x.n).join('|');
        if (a !== b) events.push({ type: 'champ', league, season, stage: 'correction' });
      }
    }
    if (race.match === total && old.provisionalFlag !== false && race.provisionalFlag === false) {
      events.push({ type: 'complete', league, season, match: race.match });
      events.push({ type: 'champ', league, season, stage: 'confirmed' });
    }
  }
  return events;
}

// What changed inside one race. Insertions push everyone behind down a place;
// those knock-on moves are not counted as corrections.
export function raceChanges(oldRace, newRace) {
  const a = oldRace.results, b = newRace.results;
  const lc = (x) => (x || '').toLowerCase();
  const pairs = []; // [oldRow, newRow]
  const usedA = new Set(), usedB = new Set();
  // 1. Same name and club: pair each with the nearest position (handles two James Turners, unknown athletes)
  const groups = new Map();
  for (const r of a) { const k = key(r); if (!groups.has(k)) groups.set(k, { a: [], b: [] }); groups.get(k).a.push(r); }
  for (const r of b) { const k = key(r); if (!groups.has(k)) groups.set(k, { a: [], b: [] }); groups.get(k).b.push(r); }
  const nearest = (xs, ys, ok = () => true) => {
    const cands = [];
    for (const x of xs) for (const y of ys) if (ok(x, y)) cands.push([Math.abs(x.p - y.p), x, y]);
    cands.sort((m, n) => m[0] - n[0]);
    for (const [, x, y] of cands) if (!usedA.has(x) && !usedB.has(y)) { usedA.add(x); usedB.add(y); pairs.push([x, y]); }
  };
  for (const g of groups.values()) nearest(g.a, g.b);
  const changes = [];
  // 2. Same real name, different club
  const realName = (n) => !/^unknown/i.test(n || '');
  const leftA = a.filter((r) => !usedA.has(r)), leftB = b.filter((r) => !usedB.has(r));
  const before = pairs.length;
  nearest(leftA, leftB, (x, y) => realName(x.n) && lc(x.n) === lc(y.n));
  for (const [x, y] of pairs.slice(before)) changes.push({ kind: 'club', n: y.n, c: y.c, from: x.c, p: y.p });
  // 3. What's left: a place given to someone else, or a runner added / removed
  const restA = a.filter((r) => !usedA.has(r)), restB = b.filter((r) => !usedB.has(r));
  const restAAt = new Map(restA.map((r) => [r.p, r]));
  const replacedOld = new Set();
  for (const r of restB) {
    const o = restAAt.get(r.p);
    if (o && !replacedOld.has(o)) { replacedOld.add(o); changes.push({ kind: 'replaced', n: r.n, c: r.c, p: r.p, was: o }); }
    else changes.push({ kind: 'added', n: r.n, c: r.c, p: r.p });
  }
  for (const r of restA) if (!replacedOld.has(r)) changes.push({ kind: 'removed', n: r.n, c: r.c, p: r.p });
  // 4. Moves: runners whose order relative to everyone else changed. Keep the longest run
  //    that stayed in order; anyone outside it genuinely moved (one move = one correction).
  const seq = pairs.slice().sort((m, n) => m[1].p - n[1].p);
  const keep = lisKeep(seq.map(([x]) => x.p));
  seq.forEach(([x, y], i) => { if (!keep.has(i)) changes.push({ kind: 'moved', n: y.n, c: y.c, p: y.p, from: x.p }); });
  // 5. Times
  for (const [x, y] of pairs) if (x.t && y.t && x.t !== y.t) changes.push({ kind: 'time', n: y.n, c: y.c, p: y.p, t: y.t, from: x.t });
  return changes;
}

// Indexes of the longest increasing subsequence of xs
function lisKeep(xs) {
  const tails = [], tailIdx = [], prev = new Array(xs.length).fill(-1);
  xs.forEach((v, i) => {
    let lo = 0, hi = tails.length;
    while (lo < hi) { const m = (lo + hi) >> 1; if (tails[m] < v) lo = m + 1; else hi = m; }
    tails[lo] = v; tailIdx[lo] = i; prev[i] = lo > 0 ? tailIdx[lo - 1] : -1;
  });
  const keep = new Set();
  for (let i = tailIdx[tails.length - 1]; i !== undefined && i >= 0; i = prev[i]) keep.add(i);
  return keep;
}

// ---------- who is affected ----------
function followedClubs(follow, data, season, match) {
  const inRace = new Set(teamResult(data, season, match).map((t) => t.club));
  return (follow.clubs || []).filter((c) => inRace.has(c));
}
function followedRunners(follow, league, race) {
  const names = new Set((follow.runners || []).filter((r) => !r.league || r.league === league).map((r) => r.name.toLowerCase()));
  return race.results.filter((r) => names.has(r.n.toLowerCase()));
}
const leagueOn = (follow, league) => !!follow[league];

// ---------- writing ----------
function teamLines(rows, extraClubs) {
  const top = rows.slice(0, 3);
  const extra = rows.filter((t) => t.pos > 3 && extraClubs.includes(t.club));
  return [...top, ...extra].map((t) => `${posLabel(t)} ${t.club} ${t.pts} pts`);
}
function runnerLines(race, mine) {
  const mineKeys = new Set(mine.map(key));
  const top = race.results.slice(0, 3);
  const extra = mine.filter((r) => r.p > 3).sort((x, y) => x.p - y.p);
  return [...top, ...extra].map((r) => `${r.p} ${r.n} ${r.c}${mineKeys.has(key(r)) ? ARROW : ''}`);
}

function leagueLine(club, before, after) {
  const a = after.find((t) => t.club === club);
  const b = before.find((t) => t.club === club);
  if (!a || !b) return null;
  if (a.pos === b.pos) return a.pos === 1 ? `League: ${club} stay top` : `League: ${club} stay ${ordWord(a.pos)}`;
  if (a.pos === 1) return `League: ${club} up to top`;
  return `League: ${club} ${a.pos < b.pos ? 'up' : 'down'} to ${ordWord(a.pos)}`;
}

function finalLeagueLine(league, club, after, provisional) {
  const a = after.find((t) => t.club === club);
  if (!a) return null;
  const tag = provisional ? ' (provisional)' : '';
  if (a.pos === 1) return `League: ${club} champions${tag}`;
  if (a.pos > after.length - RELEGATION[league]) return `League: ${club} relegated${tag}`;
  return `League: ${club} finish ${ordWord(a.pos)}${tag}`;
}

// How team positions moved between two versions of one match result.
function teamEffect(before, after, follow) {
  const mine = follow.clubs || [];
  const parts = [];
  const moved = after.filter((t) => { const b = before.find((x) => x.club === t.club); return b && b.pos !== t.pos; });
  const changedPts = after.filter((t) => { const b = before.find((x) => x.club === t.club); return b && b.pts !== t.pts; });
  // Followed clubs first: always say where they stand
  for (const c of mine) {
    const a = after.find((t) => t.club === c), b = before.find((t) => t.club === c);
    if (!a || !b) continue;
    if (a.pos === b.pos) parts.push(`${c} still ${ord(a.pos)}${a.pts !== b.pts ? `, now ${a.pts} pts` : ` on ${a.pts} pts`}.`);
    else parts.push(`${c} ${a.pos < b.pos ? 'up' : 'down'} to ${ord(a.pos)} on ${a.pts} pts.`);
  }
  if (!mine.length) {
    for (const t of changedPts.filter((t) => !moved.includes(t)).slice(0, 2)) parts.push(`${t.club} now ${t.pts} pts.`);
  }
  const otherMoves = moved.filter((t) => !mine.includes(t.club));
  if (otherMoves.length) {
    const b = (t) => before.find((x) => x.club === t.club);
    parts.push(otherMoves.slice(0, 3).map((t) => `${t.club} ${t.pos < b(t).pos ? 'up' : 'down'} to ${ord(t.pos)} on ${t.pts} pts`).join(', ') + '.');
  } else if (!moved.length) parts.push('Team positions unchanged.');
  return parts.join(' ');
}

function describeChange(ch, league, venue) {
  const L = LEAGUE_LOWER[league];
  switch (ch.kind) {
    case 'added': return `${ch.n} (${ch.c}) has been added to the ${L} results at ${venue} in ${ord(ch.p)}.`;
    case 'removed': return `${ch.n} (${ch.c}) has been removed from the ${L} results at ${venue}.`;
    case 'replaced': return `${ord(ch.p)} in the ${L} match at ${venue} is now ${ch.n} (${ch.c}), was ${ch.was.n} (${ch.was.c}).`;
    case 'moved': return `${ch.n} (${ch.c}) is now ${ord(ch.p)} in the ${L} match at ${venue}, was ${ord(ch.from)}.`;
    case 'club': return `${ch.n} in the ${L} match at ${venue} is now listed for ${ch.c}, was ${ch.from}.`;
    case 'time': return `${ch.n} (${ch.c})'s time in the ${L} match at ${venue} is now ${ch.t}, was ${ch.from}.`;
    default: return '';
  }
}

// ---------- pictures ----------
// image: { type: 'portrait', file } | { type: 'singlet', club } | null
function pictureFor(name, club, portraits) {
  const p = portraits && portraits[(name || '').toLowerCase()];
  return p ? { type: 'portrait', file: p.file, club } : { type: 'singlet', club };
}
function teamPicture(race, club, portraits) {
  for (const r of race.results) if (r.c === club && portraits && portraits[r.n.toLowerCase()]) return { type: 'portrait', file: portraits[r.n.toLowerCase()].file, club };
  return { type: 'singlet', club };
}

// ---------- turning one event into messages for one follower ----------
// ctx = { prev, next, portraits }  (prev/next: that league's data before and after)
export function render(event, follow, ctx) {
  const { league, season } = event;
  const data = ctx.next;
  const total = matchesPerSeason(data, season);
  const thread = `${league}-${season}-m${event.match || total}`;
  const compact = season.replace('/', '').slice(-4);
  const url = event.match && (event.type === 'results' || event.type === 'corrections')
    ? `${league === 'women' ? '/women' : ''}/race/${compact}-${event.match}`
    : `/${league === 'women' ? '#women/' : '#'}season/${compact}`;
  const out = [];

  if (event.type === 'results') {
    const race = seasonRaces(data, season).find((r) => r.match === event.match);
    const lead = `${LEAGUE_LABEL[league]} match at ${race.venue}`;
    const clubs = followedClubs(follow, data, season, event.match);
    const mine = followedRunners(follow, league, race);
    const teams = teamResult(data, season, event.match);
    if (!race || !race.results.length) return out;
    if (leagueOn(follow, league) && teams.length) {
      const lines = [lead, ...teamLines(teams, clubs)];
      if (event.match >= 2) {
        const before = leagueTable(data, season, event.match - 1);
        const after = leagueTable(data, season, event.match);
        for (const c of clubs) {
          const l = event.match === total ? finalLeagueLine(league, c, after, race.provisional) : leagueLine(c, before, after);
          if (l) lines.push(l);
        }
      }
      out.push({ title: 'Surrey League provisional team results', body: lines.join('\n'),
        image: teamPicture(race, clubs[0] || teams[0].club, ctx.portraits), threadId: thread, url });
    }
    if (leagueOn(follow, league) || mine.length) {
      out.push({ title: 'Surrey League provisional individual results', body: [lead, ...runnerLines(race, mine)].join('\n'),
        image: pictureFor(race.results[0].n, race.results[0].c, ctx.portraits), threadId: thread, url });
    }
    return out;
  }

  if (event.type === 'corrections') {
    if (!follow.corrections) return out;
    const race = seasonRaces(data, season).find((r) => r.match === event.match);
    const clubs = followedClubs(follow, data, season, event.match);
    const mineKeys = new Set((follow.runners || []).filter((r) => !r.league || r.league === league).map((r) => r.name.toLowerCase()));
    const before = teamResult(ctx.prev, season, event.match);
    const after = teamResult(data, season, event.match);
    const clubScoreChanged = clubs.some((c) => { const a = after.find((t) => t.club === c), b = before.find((t) => t.club === c); return a && b && (a.pts !== b.pts || a.pos !== b.pos); });
    const myRunnerChanges = event.changes.filter((ch) => mineKeys.has(ch.n.toLowerCase()) && ['moved', 'added', 'replaced', 'club', 'removed', 'time'].includes(ch.kind));
    let interested;
    if (leagueOn(follow, league) && !clubs.length) interested = true; // league follower: every correction
    else interested = (leagueOn(follow, league) && clubScoreChanged) || myRunnerChanges.length > 0;
    if (!interested) return out;

    const effect = teamEffect(before, after, { clubs });
    let body;
    const n = event.changes.length;
    if (n === 0) body = `Team scores for the ${LEAGUE_LOWER[league]} match at ${race.venue} have been updated. ` + effect;
    else if (n <= 2) body = event.changes.map((ch) => describeChange(ch, league, race.venue)).join(' ') + ' ' + effect;
    else {
      body = `${n} corrections to the ${LEAGUE_LOWER[league]} results at ${race.venue}. ` + effect;
      for (const ch of myRunnerChanges) if (ch.kind === 'moved') body += ` ${ch.n} (${ch.c}) now ${ord(ch.p)}, was ${ord(ch.from)}.`;
    }
    // League table moves for followed clubs (from match 2)
    if (event.match >= 2 && clubs.length) {
      const tPrev = leagueTable(ctx.prev, season, event.match), tNext = leagueTable(data, season, event.match);
      for (const c of clubs) {
        const a = tNext.find((t) => t.club === c), b = tPrev.find((t) => t.club === c);
        if (a && b && a.pos !== b.pos) body += `\nLeague: ${c} ${a.pos < b.pos ? 'up' : 'back'} to ${ordWord(a.pos)}`;
      }
    }
    out.push({ title: n > 1 ? 'Surrey League corrections' : 'Surrey League correction', body: body.trim(), image: null, threadId: thread, url });
    return out;
  }

  if (event.type === 'complete') {
    if (!leagueOn(follow, league)) return out;
    const after = leagueTable(data, season, total);
    const clubs = (follow.clubs || []).filter((c) => after.some((t) => t.club === c));
    const which = clubs.length ? clubs : [after[0].club];
    const lines = which.map((c) => {
      const a = after.find((t) => t.club === c);
      if (a.pos === 1) return `${c} title confirmed as results marked complete.`;
      if (a.pos > after.length - RELEGATION[league]) return `${c} confirmed relegated as match ${total} results marked complete.`;
      return `${c} confirmed ${ordWord(a.pos)} as match ${total} results marked complete.`;
    });
    out.push({ title: 'Surrey League season complete', body: lines.join('\n'), image: { type: 'singlet', club: which[0] }, threadId: `${league}-${season}-final`, url });
    return out;
  }

  if (event.type === 'champ') {
    if (!leagueOn(follow, league)) return out;
    const cfg = CHAMP[league];
    const table = champTable(data, league, season);
    if (!table.length) return out;
    const mine = new Set((follow.runners || []).map((r) => r.name.toLowerCase()));
    const top = table.slice(0, 3).map((t) => `${posLabel(t)} ${t.n} ${t.c} ${t.pts} pts${mine.has(t.n.toLowerCase()) ? ARROW : ''}`);
    const leader = table[0];
    let title, body;
    if (event.stage === 'provisional') {
      title = `${cfg.name} (provisional)`;
      body = [`${LEAGUE_LABEL[league]} individual standings after match ${total}`, ...top].join('\n');
    } else if (event.stage === 'correction') {
      if (!follow.corrections) return out;
      const old = champTable(ctx.prev, league, season);
      const oldLeader = old[0];
      const oldNow = oldLeader && table.find((t) => t.n === oldLeader.n && t.c === oldLeader.c);
      const first = oldLeader && oldLeader.n !== leader.n
        ? `${leader.n} (${leader.c}) now 1st on ${leader.pts} pts, ${oldLeader.n} (${oldLeader.c}) ${oldNow ? 'down to ' + ord(oldNow.pos) : 'no longer in the standings'} after corrections to match ${total}.`
        : `Top three changed after corrections to match ${total}.`;
      title = `${cfg.name} correction`;
      body = [first, ...top].join('\n');
    } else {
      title = `${cfg.name} confirmed`;
      body = [`${leader.n} (${leader.c}) wins the ${cfg.short} as results marked complete.`, ...top].join('\n');
    }
    out.push({ title, body, image: pictureFor(leader.n, leader.c, ctx.portraits), threadId: `${league}-${season}-champ`, url });
    return out;
  }
  return out;
}

// Convenience: every message for one follower from one league's data change.
export function messagesFor(follow, events, ctx) {
  return events.flatMap((e) => render(e, follow, ctx));
}
