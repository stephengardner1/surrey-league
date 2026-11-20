// Surrey League Compendium back office (Cloudflare Worker + D1 database).
//  - Phones register what they follow:            POST /v1/register
//  - The results notifier (GitHub Action) asks
//    who follows what, then hands over a batch:   GET /admin/devices, POST /admin/batch
//  - Pilot mode: each batch goes to Steve's phone
//    first; he taps Approve to send to everyone:  GET/POST /approve/<id>?k=…
//  - Sending happens in small chunks (Cloudflare limits how many messages one
//    request can send), carried on by a once-a-minute timer.
//
// Settings (wrangler.toml [vars]) and secrets (set with `wrangler secret put`):
//   APNS_KEY_ID, APNS_TEAM_ID, APNS_TOPIC (org.slarchive.app)   vars
//   APNS_P8            secret: the text of Apple's AuthKey_XXXX.p8 file
//   ADMIN_KEY          secret: password the GitHub Action uses
//   ADMIN_CODE         secret: code Steve types into the app to mark his phone as the approver
//   APPROVAL           var: "on" (pilot: Steve approves every batch) or "off"
//   FCM_SERVICE_ACCOUNT secret: the whole text of the Firebase private key file (.json). Android
//                      phones are reached through Google's Firebase service instead of Apple's.
//                      Without it, iPhones carry on as normal and Android sends are marked failed.
//
// Fast race-day results (20 Nov 2026): on match days the once-a-minute timer also looks at
// the league's own results feed. The moment a senior race has results it asks GitHub to run
// the "Fast results" Action (notifier/fast.mjs), which writes the notifications and hands
// them back here marked auto: those go straight out, with no approval step.
//   FAST_MATCHES       var: JSON list of the league's match ids to watch, e.g.
//                      [{"id":197,"match":3,"date":"2027-01-16"}]
//   GITHUB_REPO        var: the website repository, e.g. stephengardner1/surrey-league
//   GITHUB_TOKEN       secret: lets this back office start that GitHub Action

const CHUNK = 40; // messages per request (free plan allows 50 outgoing requests)

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    try {
      if (req.method === 'OPTIONS') return cors(new Response(null, { status: 204 }));
      if (url.pathname === '/') return text('Surrey League Compendium notifications: running.');
      if (url.pathname === '/v1/register' && req.method === 'POST') return cors(await register(req, env));
      if (url.pathname === '/v1/unregister' && req.method === 'POST') return cors(await unregister(req, env));
      if (url.pathname === '/v1/live' && req.method === 'GET') return cors(await liveList(env));
      if (url.pathname.startsWith('/admin/')) {
        if (!(await isAdmin(req, env))) return json({ error: 'not allowed' }, 401);
        if (url.pathname === '/admin/devices' && req.method === 'GET') return json(await devices(env));
        if (url.pathname === '/admin/batch' && req.method === 'POST') return json(await newBatch(req, env, ctx));
        if (url.pathname === '/admin/status' && req.method === 'GET') return json(await status(env));
        if (url.pathname === '/admin/test' && req.method === 'POST') return json(await testPush(req, env));
        if (url.pathname === '/admin/announced' && req.method === 'GET') return json(await announcedList(env));
        if (url.pathname === '/admin/announced' && req.method === 'POST') return json(await announcedAdd(req, env));
        if (url.pathname === '/admin/live' && req.method === 'POST') return json(await liveSet(req, env));
        if (url.pathname === '/admin/fast' && req.method === 'GET') return json(await fastStatus(env));
        if (url.pathname === '/admin/fast-check' && req.method === 'POST') return json(await fastCheck(env, (await req.json().catch(() => ({}))).now));
      }
      const m = url.pathname.match(/^\/approve\/([a-z0-9-]+)$/);
      if (m) return approve(req, env, ctx, m[1], url.searchParams.get('k'));
      return json({ error: 'not found' }, 404);
    } catch (e) {
      console.error(e);
      return json({ error: 'server error' }, 500);
    }
  },
  async scheduled(_event, env, ctx) {
    ctx.waitUntil(sendWaiting(env));
    ctx.waitUntil(fastCheck(env).catch((e) => console.error('fast check failed', e)));
  },
};

// ---------- phones ----------
async function register(req, env) {
  const b = await req.json().catch(() => null);
  if (!b || !validToken(b.token)) return json({ error: 'bad token' }, 400);
  const follow = cleanFollow(b.follow);
  const now = new Date().toISOString();
  const admin = b.adminCode && env.ADMIN_CODE && safeEqual(String(b.adminCode), env.ADMIN_CODE) ? 1 : null;
  await env.DB.prepare(
    `INSERT INTO devices (token, follow, admin, created, updated) VALUES (?1, ?2, COALESCE(?3, 0), ?4, ?4)
     ON CONFLICT(token) DO UPDATE SET follow = ?2, admin = COALESCE(?3, admin), updated = ?4`,
  ).bind(b.token, JSON.stringify(follow), admin, now).run();
  const row = await env.DB.prepare('SELECT admin FROM devices WHERE token = ?1').bind(b.token).first();
  return json({ ok: true, approver: !!(row && row.admin) });
}
async function unregister(req, env) {
  const b = await req.json().catch(() => null);
  if (!b || !validToken(b.token)) return json({ error: 'bad token' }, 400);
  await env.DB.prepare('DELETE FROM devices WHERE token = ?1').bind(b.token).run();
  return json({ ok: true });
}
// A phone's address. iPhones: a long run of 0-9 and a-f from Apple. Android phones: a longer
// mixed string from Firebase (it always contains a colon), so the two can be told apart on sight.
const appleToken = (t) => typeof t === 'string' && /^[0-9a-f]{64,200}$/i.test(t);
const androidToken = (t) => typeof t === 'string' && !appleToken(t) && /^[A-Za-z0-9_-]{5,60}:[A-Za-z0-9_-]{60,4000}$/.test(t);
const validToken = (t) => appleToken(t) || androidToken(t);
function cleanFollow(f) {
  f = f && typeof f === 'object' ? f : {};
  const clubs = Array.isArray(f.clubs) ? f.clubs.filter((c) => typeof c === 'string' && c.length <= 5).slice(0, 20) : [];
  const runners = Array.isArray(f.runners) ? f.runners.filter((r) => r && typeof r.name === 'string' && r.name.length <= 80).slice(0, 50)
    .map((r) => ({ name: r.name, club: typeof r.club === 'string' ? r.club.slice(0, 5) : '', league: r.league === 'women' ? 'women' : 'men' })) : [];
  return { men: !!f.men, women: !!f.women, corrections: f.corrections !== false, clubs, runners };
}

// ---------- the notifier's side ----------
async function devices(env) {
  const { results } = await env.DB.prepare('SELECT token, follow, admin FROM devices').all();
  return results.map((r) => ({ token: r.token, follow: JSON.parse(r.follow), admin: !!r.admin }));
}

// body: { summary, messages: [{ tokens: [...], title, body, image, threadId, url }], auto, claim, fast }
//   auto: true   new results from the fast race-day check: send straight away, no approval step
//   claim: key   only send if nobody has announced this already (e.g. "2026/27|men|m3|results");
//                the key is recorded in the same step, so two senders can never both win
//   fast: key    which fast race-day check this answers (e.g. "197|Senior Men"), so it stops retrying
async function newBatch(req, env, ctx) {
  const b = await req.json();
  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  const approval = (env.APPROVAL || 'on') === 'on' && b.auto !== true;
  if (b.fast) await env.DB.prepare('UPDATE fast_races SET announced_at = ?1 WHERE key = ?2 AND announced_at IS NULL').bind(now, String(b.fast)).run();
  if (b.claim) {
    const r = await env.DB.prepare('INSERT OR IGNORE INTO announced (key, at, batch) VALUES (?1, ?2, ?3)').bind(String(b.claim).slice(0, 200), now, id).run();
    if (!r.meta || !r.meta.changes) return { ok: true, skipped: 'already announced', queued: 0 };
  }
  const admins = new Set((await env.DB.prepare('SELECT token FROM devices WHERE admin = 1').all()).results.map((r) => r.token));
  const stmts = [env.DB.prepare('INSERT INTO batches (id, created, summary, status) VALUES (?1, ?2, ?3, ?4)')
    .bind(id, now, String(b.summary || 'Update').slice(0, 300), approval ? 'awaiting_approval' : 'sending')];
  let count = 0;
  for (const m of b.messages || []) {
    for (const token of m.tokens || []) {
      if (!validToken(token)) continue;
      const isAdmin = admins.has(token) ? 1 : 0;
      stmts.push(env.DB.prepare('INSERT INTO deliveries (batch, token, payload, is_admin) VALUES (?1, ?2, ?3, ?4)')
        .bind(id, token, JSON.stringify(apnsPayload(m)), isAdmin));
      count++;
    }
  }
  // In pilot mode, every approver gets a preview of each different message, plus an "Approve" notification
  if (approval) {
    const seen = new Set();
    for (const token of admins) {
      for (const m of b.messages || []) {
        const sig = token + m.title + m.body;
        if (seen.has(sig) || (m.tokens || []).includes(token)) continue;
        seen.add(sig);
        stmts.push(env.DB.prepare('INSERT INTO deliveries (batch, token, payload, is_admin) VALUES (?1, ?2, ?3, 1)')
          .bind(id, token, JSON.stringify(apnsPayload({ ...m, title: 'Preview: ' + m.title }))));
      }
      const link = `${new URL(req.url).origin}/approve/${id}?k=${await approveKey(env, id)}`;
      stmts.push(env.DB.prepare('INSERT INTO deliveries (batch, token, payload, is_admin) VALUES (?1, ?2, ?3, 1)')
        .bind(id, token, JSON.stringify({ aps: { alert: { title: 'Approve notifications?', body: `${b.summary}\n${count} notifications ready. Tap to check and send.` }, sound: 'default' }, url: link })));
    }
  }
  for (let i = 0; i < stmts.length; i += 50) await env.DB.batch(stmts.slice(i, i + 50));
  ctx.waitUntil(sendWaiting(env));
  return { ok: true, id, queued: count, approval };
}

// ---------- what has already been announced ----------
// Stops the same new results being sent twice: once by the fast race-day check and again
// when the full results reach slarchive.org a few minutes later.
async function announcedList(env) {
  return (await env.DB.prepare('SELECT key, at FROM announced ORDER BY at DESC LIMIT 200').all()).results;
}
async function announcedAdd(req, env) {
  const b = await req.json().catch(() => ({}));
  const now = new Date().toISOString();
  for (const k of [].concat(b.key || []).slice(0, 20)) {
    await env.DB.prepare('INSERT OR IGNORE INTO announced (key, at) VALUES (?1, ?2)').bind(String(k).slice(0, 200), now).run();
  }
  if (b.fast) await env.DB.prepare('UPDATE fast_races SET announced_at = ?1 WHERE key = ?2 AND announced_at IS NULL').bind(now, String(b.fast)).run();
  return { ok: true };
}

// ---------- "first results" copies of a race ----------
// The fast race-day check also leaves a copy of the race here (every finisher, team scores).
// slarchive.org and the app lay it over their normal data, so a tap on the notification opens
// a real results page straight away. When the full results are published the copy is marked
// replaced, and open pages swap themselves over.
//   POST /admin/live { key: "2026/27|men|m3", league, race: {...} }   store a copy
//   POST /admin/live { replaced: ["2026/27|men|m3"] }                 the full results are out
//   GET  /v1/live                                                     public: the last few days' copies
async function liveSet(req, env) {
  const b = await req.json().catch(() => ({}));
  const now = new Date().toISOString();
  if (b.key && b.race) {
    const body = JSON.stringify({ key: String(b.key), league: b.league === 'women' ? 'women' : 'men', at: now, race: b.race });
    if (body.length > 400000) return { ok: false, error: 'too big' };
    await env.DB.prepare('INSERT INTO live_races (key, body, at) VALUES (?1, ?2, ?3) ON CONFLICT(key) DO UPDATE SET body = ?2, at = ?3 WHERE replaced_at IS NULL')
      .bind(String(b.key).slice(0, 100), body, now).run();
  }
  for (const k of [].concat(b.replaced || []).slice(0, 10)) {
    await env.DB.prepare('UPDATE live_races SET replaced_at = ?1 WHERE key = ?2 AND replaced_at IS NULL').bind(now, String(k)).run();
  }
  return { ok: true };
}
async function liveList(env) {
  const since = new Date(Date.now() - 4 * 864e5).toISOString();
  const rows = (await env.DB.prepare('SELECT key, body, replaced_at FROM live_races WHERE at > ?1 ORDER BY at').bind(since).all()).results;
  // The stored text is already JSON: stitch it together rather than re-reading it (keeps this quick)
  const parts = rows.map((r) => (r.replaced_at ? JSON.stringify({ key: r.key, replaced: true }) : r.body));
  return new Response('{"races":[' + parts.join(',') + ']}', { headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });
}

// ---------- fast race-day check ----------
// Runs every minute but only does anything inside a match's window: 1pm (London) on match
// day until midnight the next day. Cloudflare's free plan allows very little thinking time
// per run, so this only LOOKS for results and rings GitHub; the writing happens there.
const FAST_RACES = ['Senior Men', 'Senior Women'];
const FAST_MIN_FINISHERS = 50;      // ignore a half-published or test race
const FAST_WAIT_FOR_TEAMS = 20 * 60e3; // individual results up but no team scores: wait this long, then go anyway
const FAST_RETRY_AFTER = 5 * 60e3;  // nothing sent 5 minutes after ringing GitHub: ring again
const FAST_MAX_TRIES = 3;
const LEAGUE_SITE = 'https://www.surreyleague.org';

function fastMatches(env) {
  try { const v = JSON.parse(env.FAST_MATCHES || '[]'); return Array.isArray(v) ? v.filter((m) => m && m.id && /^\d{4}-\d\d-\d\d$/.test(m.date || '')) : []; }
  catch { return []; }
}
// "2027-01-16 14:05" as a clock in London would show it
function londonStamp(ms) {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/London', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' })
    .formatToParts(new Date(ms)).map((x) => [x.type, x.value]));
  return `${p.year}-${p.month}-${p.day} ${p.hour}:${p.minute}`;
}
function nextDay(date) {
  const d = new Date(date + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + 1);
  return d.toISOString().slice(0, 10);
}
function inFastWindow(date, ms) {
  const now = londonStamp(ms);
  return now >= `${date} 13:00` && now <= `${nextDay(date)} 23:59`;
}

async function fastCheck(env, nowOverride) {
  const nowMs = nowOverride ? Date.parse(nowOverride) : Date.now();
  const now = new Date(nowMs).toISOString();
  const log = [];
  for (const match of fastMatches(env)) {
    if (!inFastWindow(match.date, nowMs)) continue;
    const keys = FAST_RACES.map((r) => `${match.id}|${r}`);
    const rows = new Map((await env.DB.prepare('SELECT * FROM fast_races WHERE key IN (?1, ?2)').bind(...keys).all()).results.map((r) => [r.key, r]));
    const finished = (r) => r && (r.announced_at || r.tries >= FAST_MAX_TRIES);
    if (keys.every((k) => finished(rows.get(k)))) continue; // both races dealt with: nothing left to watch
    const feed = await fetch(`${LEAGUE_SITE}/match/${match.id}/json/`, { headers: { 'user-agent': 'slarchive.org results check' }, cf: { cacheTtl: 0 } });
    if (!feed.ok) { log.push(`match ${match.id}: feed replied ${feed.status}`); continue; }
    let data; try { data = await feed.json(); } catch { log.push(`match ${match.id}: feed unreadable`); continue; }
    let matchPage = null;
    for (const race of FAST_RACES) {
      const key = `${match.id}|${race}`;
      let row = rows.get(key);
      if (finished(row)) continue;
      const res = (data.results || []).find((r) => r && r.name === race);
      if (!res || !Array.isArray(res.positions) || res.positions.length < FAST_MIN_FINISHERS) continue;
      if (!row) {
        await env.DB.prepare('INSERT OR IGNORE INTO fast_races (key, first_seen, tries) VALUES (?1, ?2, 0)').bind(key, now).run();
        row = { key, first_seen: now, tries: 0 };
        log.push(`${key}: results first seen`);
      }
      if (row.dispatched_at) {
        if (nowMs - Date.parse(row.dispatched_at) < FAST_RETRY_AFTER) continue;
      } else if (nowMs - Date.parse(row.first_seen) < FAST_WAIT_FOR_TEAMS) {
        // Team scores normally appear with the individual results. Check the race page for them.
        if (matchPage === null) matchPage = await fetch(`${LEAGUE_SITE}/match/${match.id}/`).then((r) => (r.ok ? r.text() : '')).catch(() => '');
        if (!(await hasTeamScores(matchPage, race))) { log.push(`${key}: waiting for team scores`); continue; }
      }
      const ok = await ringGitHub(env, match.id, race);
      await env.DB.prepare('UPDATE fast_races SET dispatched_at = ?1, tries = tries + 1, note = ?2 WHERE key = ?3').bind(now, ok.note, key).run();
      log.push(`${key}: asked GitHub to send (${ok.note})`);
    }
  }
  if (log.length) console.log(log.join('; '));
  return { now, log };
}

// Is there at least one row in the race page's "Match results" (team) table?
async function hasTeamScores(matchPage, race) {
  const m = matchPage.match(new RegExp('<a href="/race/(\\d+)/">\\s*' + race + '\\s*</a>'));
  if (!m) return false;
  const r = await fetch(`${LEAGUE_SITE}/race/${m[1]}/`).catch(() => null);
  if (!r || !r.ok) return false;
  const page = await r.text();
  const a = page.indexOf('>Match results<');
  if (a < 0) return false;
  const row = page.indexOf(' team-row"', a);
  const b = page.indexOf('>B team results<', a);
  return row >= 0 && (b < 0 || row < b);
}

async function ringGitHub(env, matchId, race) {
  if (!env.GITHUB_TOKEN || !env.GITHUB_REPO) return { ok: false, note: 'GITHUB_TOKEN or GITHUB_REPO not set' };
  const r = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/dispatches`, {
    method: 'POST',
    headers: { authorization: `Bearer ${env.GITHUB_TOKEN}`, accept: 'application/vnd.github+json', 'x-github-api-version': '2022-11-28', 'user-agent': 'sl-notify', 'content-type': 'application/json' },
    body: JSON.stringify({ event_type: 'fast-results', client_payload: { matchId, race } }),
  }).catch(() => null);
  return r && r.status === 204 ? { ok: true, note: 'ok' } : { ok: false, note: 'GitHub replied ' + (r ? r.status : 'nothing') };
}

async function fastStatus(env) {
  const now = Date.now();
  return {
    watching: fastMatches(env).map((m) => ({ ...m, windowOpen: inFastWindow(m.date, now) })),
    githubToken: !!env.GITHUB_TOKEN, repo: env.GITHUB_REPO || null,
    races: (await env.DB.prepare('SELECT * FROM fast_races ORDER BY first_seen DESC LIMIT 20').all()).results,
  };
}

async function status(env) {
  const batches = (await env.DB.prepare('SELECT * FROM batches ORDER BY created DESC LIMIT 10').all()).results;
  const devicesCount = (await env.DB.prepare('SELECT COUNT(*) AS n FROM devices').first()).n;
  return { devices: devicesCount, batches };
}

async function testPush(req, env) {
  const b = await req.json().catch(() => ({}));
  const rows = (await env.DB.prepare(b.token ? 'SELECT token, env FROM devices WHERE token = ?1' : 'SELECT token, env FROM devices WHERE admin = 1').bind(...(b.token ? [b.token] : [])).all()).results;
  const out = [];
  for (const r of rows) out.push(await sendOne(env, r, { aps: { alert: { title: 'Surrey League test', body: 'Notifications are working.' }, sound: 'default' } }));
  return { sent: out };
}

// ---------- approval page ----------
async function approveKey(env, id) {
  const data = new TextEncoder().encode(id + ':' + env.ADMIN_KEY);
  const h = await crypto.subtle.digest('SHA-256', data);
  return [...new Uint8Array(h)].slice(0, 12).map((x) => x.toString(16).padStart(2, '0')).join('');
}
async function approve(req, env, ctx, id, k) {
  if (!k || !safeEqual(k, await approveKey(env, id))) return html('<p>This link isn’t valid.</p>', 403);
  const batch = await env.DB.prepare('SELECT * FROM batches WHERE id = ?1').bind(id).first();
  if (!batch) return html('<p>Not found.</p>', 404);
  if (req.method === 'POST') {
    const form = await req.formData();
    const action = form.get('action');
    if (batch.status === 'awaiting_approval') {
      if (action === 'send') await env.DB.prepare("UPDATE batches SET status = 'sending' WHERE id = ?1").bind(id).run();
      if (action === 'cancel') await env.DB.prepare("UPDATE batches SET status = 'cancelled' WHERE id = ?1").bind(id).run();
      ctx.waitUntil(sendWaiting(env));
    }
    return Response.redirect(new URL(req.url).toString(), 303);
  }
  const rows = (await env.DB.prepare('SELECT payload, COUNT(*) AS n FROM deliveries WHERE batch = ?1 AND is_admin = 0 GROUP BY payload ORDER BY n DESC').bind(id).all()).results;
  const counts = await env.DB.prepare('SELECT SUM(sent = 1) AS sent, SUM(sent = 2) AS failed, SUM(sent = 0) AS waiting FROM deliveries WHERE batch = ?1 AND is_admin = 0').bind(id).first();
  const list = rows.map((r) => { const p = JSON.parse(r.payload); return `<li><b>${esc(p.aps.alert.title)}</b> <span class="n">× ${r.n}</span><pre>${esc(p.aps.alert.body)}</pre></li>`; }).join('');
  const state = { awaiting_approval: 'Waiting for your approval', sending: 'Sending', done: 'Sent', cancelled: 'Cancelled' }[batch.status] || batch.status;
  const buttons = batch.status === 'awaiting_approval'
    ? `<form method="post"><button name="action" value="send" class="go">Send to everyone</button><button name="action" value="cancel" class="stop">Don’t send</button></form>` : '';
  return html(`<h1>${esc(batch.summary)}</h1><p class="state">${state}. Sent ${counts.sent || 0}, waiting ${counts.waiting || 0}, failed ${counts.failed || 0}.</p>${buttons}<ul>${list}</ul>`);
}

// ---------- sending ----------
async function sendWaiting(env) {
  const rows = (await env.DB.prepare(
    `SELECT d.id, d.token, d.payload, dev.env FROM deliveries d JOIN batches b ON b.id = d.batch
     LEFT JOIN devices dev ON dev.token = d.token
     WHERE d.sent = 0 AND (b.status = 'sending' OR (b.status = 'awaiting_approval' AND d.is_admin = 1))
     ORDER BY d.id LIMIT ?1`).bind(CHUNK).all()).results;
  for (const r of rows) {
    const res = await sendOne(env, r, JSON.parse(r.payload));
    await env.DB.prepare('UPDATE deliveries SET sent = ?1, result = ?2 WHERE id = ?3').bind(res.ok ? 1 : 2, res.reason || 'ok', r.id).run();
  }
  // Mark finished batches
  await env.DB.prepare(`UPDATE batches SET status = 'done' WHERE status = 'sending' AND NOT EXISTS
    (SELECT 1 FROM deliveries d WHERE d.batch = batches.id AND d.sent = 0)`).run();
  return rows.length;
}

let jwtCache = { token: null, at: 0 };
async function apnsJwt(env) {
  const now = Math.floor(Date.now() / 1000);
  if (jwtCache.token && now - jwtCache.at < 50 * 60) return jwtCache.token;
  const enc = (o) => b64url(new TextEncoder().encode(JSON.stringify(o)));
  const head = enc({ alg: 'ES256', kid: env.APNS_KEY_ID });
  const claims = enc({ iss: env.APNS_TEAM_ID, iat: now });
  const pem = env.APNS_P8.replace(/-----[^-]+-----/g, '').replace(/\s+/g, '');
  const key = await crypto.subtle.importKey('pkcs8', Uint8Array.from(atob(pem), (c) => c.charCodeAt(0)), { name: 'ECDSA', namedCurve: 'P-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign({ name: 'ECDSA', hash: 'SHA-256' }, key, new TextEncoder().encode(head + '.' + claims));
  jwtCache = { token: `${head}.${claims}.${b64url(new Uint8Array(sig))}`, at: now };
  return jwtCache.token;
}

// ---------- Android (Firebase) ----------
// Google wants a short-lived pass, earned by signing a request with the private key.
let fcmCache = { token: null, until: 0, project: null };
async function fcmAccess(env) {
  const now = Math.floor(Date.now() / 1000);
  if (fcmCache.token && now < fcmCache.until) return fcmCache;
  const sa = JSON.parse(env.FCM_SERVICE_ACCOUNT);
  const enc = (o) => b64url(new TextEncoder().encode(JSON.stringify(o)));
  const head = enc({ alg: 'RS256', typ: 'JWT' });
  const claims = enc({ iss: sa.client_email, scope: 'https://www.googleapis.com/auth/firebase.messaging', aud: 'https://oauth2.googleapis.com/token', iat: now, exp: now + 3600 });
  const pem = sa.private_key.replace(/-----[^-]+-----/g, '').replace(/\s+/g, '');
  const key = await crypto.subtle.importKey('pkcs8', Uint8Array.from(atob(pem), (c) => c.charCodeAt(0)), { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', key, new TextEncoder().encode(head + '.' + claims));
  const r = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: 'grant_type=' + encodeURIComponent('urn:ietf:params:oauth:grant-type:jwt-bearer') + '&assertion=' + `${head}.${claims}.${b64url(new Uint8Array(sig))}`,
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok || !j.access_token) throw new Error('Firebase sign-in failed: ' + (j.error_description || j.error || r.status));
  fcmCache = { token: j.access_token, until: now + Math.min(j.expires_in || 3600, 3600) - 300, project: sa.project_id };
  return fcmCache;
}

// The same message, in the shape Firebase wants. Everything is stored in Apple's shape
// (see apnsPayload), so the approval page and the app read one format.
function fcmMessage(token, payload) {
  const alert = (payload.aps && payload.aps.alert) || {};
  const image = payload.image;
  const notification = { title: alert.title || '', body: alert.body || '' };
  const android = { priority: 'HIGH', notification: {} };
  // A runner's portrait comes straight from slarchive.org. (Club singlets are built into the
  // iPhone app; Android gets them once they are published on the site.)
  if (image && image.type === 'portrait' && image.file) android.notification.image = `https://slarchive.org/portraits/og/athletes/${encodeURIComponent(image.file)}.png`;
  const data = { url: String(payload.url || '/') };
  if (image) data.image = JSON.stringify(image);
  return { message: { token, notification, data, android } };
}

async function sendAndroid(env, row, payload) {
  if (!env.FCM_SERVICE_ACCOUNT) return { ok: false, reason: 'Android not set up (no Firebase key)' };
  let access;
  try { access = await fcmAccess(env); } catch (e) { return { ok: false, reason: String(e.message || e).slice(0, 200) }; }
  const r = await fetch(`https://fcm.googleapis.com/v1/projects/${access.project}/messages:send`, {
    method: 'POST',
    headers: { authorization: `Bearer ${access.token}`, 'content-type': 'application/json' },
    body: JSON.stringify(fcmMessage(row.token, payload)),
  });
  if (r.ok) return { ok: true, reason: 'android' };
  const j = await r.json().catch(() => ({}));
  const err = (j.error && j.error.details && (j.error.details.find((d) => d.errorCode) || {}).errorCode) || (j.error && j.error.status) || String(r.status);
  if (r.status === 401) fcmCache = { token: null, until: 0, project: null }; // pass expired early: get a new one next time
  // The app has been removed from that phone, or the address was never a real one
  if (err === 'UNREGISTERED' || (err === 'INVALID_ARGUMENT' && /registration token/i.test((j.error && j.error.message) || ''))) {
    await env.DB.prepare('DELETE FROM devices WHERE token = ?1').bind(row.token).run();
  }
  return { ok: false, reason: err };
}

// TestFlight and App Store phones use Apple's live service; phones running a build
// straight from Xcode use the test ("sandbox") service. Try live first and remember.
async function sendOne(env, row, payload) {
  if (androidToken(row.token)) return sendAndroid(env, row, payload);
  const order = row.env === 'sandbox' ? ['sandbox', 'production'] : ['production', 'sandbox'];
  let last = null;
  for (const which of order) {
    const host = which === 'production' ? 'https://api.push.apple.com' : 'https://api.sandbox.push.apple.com';
    const r = await fetch(`${host}/3/device/${row.token}`, {
      method: 'POST',
      headers: {
        authorization: `bearer ${await apnsJwt(env)}`,
        'apns-topic': env.APNS_TOPIC || 'org.slarchive.app',
        'apns-push-type': 'alert',
        'apns-priority': '10',
        'content-type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    if (r.ok) {
      if (row.env !== which) await env.DB.prepare('UPDATE devices SET env = ?1 WHERE token = ?2').bind(which, row.token).run();
      return { ok: true, reason: which };
    }
    const reason = (await r.json().catch(() => ({}))).reason || String(r.status);
    last = reason;
    if (reason !== 'BadDeviceToken' && reason !== 'BadEnvironmentKeyInToken') break;
  }
  if (last === 'Unregistered' || last === 'BadDeviceToken') await env.DB.prepare('DELETE FROM devices WHERE token = ?1').bind(row.token).run();
  return { ok: false, reason: last };
}

function apnsPayload(m) {
  return {
    aps: { alert: { title: m.title, body: m.body }, sound: 'default', 'mutable-content': m.image ? 1 : 0, 'thread-id': m.threadId || 'sl' },
    url: m.url || '/',
    image: m.image || null,
  };
}

// ---------- helpers ----------
async function isAdmin(req, env) {
  const h = req.headers.get('authorization') || '';
  return !!env.ADMIN_KEY && safeEqual(h, 'Bearer ' + env.ADMIN_KEY);
}
function safeEqual(a, b) {
  if (a.length !== b.length) return false;
  let x = 0;
  for (let i = 0; i < a.length; i++) x |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return x === 0;
}
const b64url = (bytes) => btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { 'content-type': 'application/json' } });
const text = (s) => new Response(s, { headers: { 'content-type': 'text/plain; charset=utf-8' } });
function cors(r) {
  r.headers.set('access-control-allow-origin', '*');
  r.headers.set('access-control-allow-methods', 'GET, POST, OPTIONS');
  r.headers.set('access-control-allow-headers', 'content-type');
  return r;
}
function html(body, status = 200) {
  return new Response(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Surrey League notifications</title><style>
body{font:16px/1.45 -apple-system,system-ui,sans-serif;margin:0 auto;max-width:640px;padding:24px 16px;color:#1d211d;background:#fff}
h1{font-size:22px;margin:0 0 8px}.state{color:#4c514a}ul{list-style:none;padding:0}li{border-top:1px solid #dfe2dd;padding:12px 0}
pre{white-space:pre-wrap;font:inherit;margin:4px 0 0;color:#3c403a}.n{color:#686e66}
form{display:flex;gap:12px;margin:16px 0}button{font:inherit;min-height:48px;padding:0 20px;border-radius:999px;border:1px solid #1b649e}
.go{background:#1b649e;color:#fff}.stop{background:#fff;color:#1b649e}</style></head><body>${body}</body></html>`,
  { status, headers: { 'content-type': 'text/html; charset=utf-8' } });
}
