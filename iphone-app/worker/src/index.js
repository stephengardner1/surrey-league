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

const CHUNK = 40; // messages per request (free plan allows 50 outgoing requests)

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    try {
      if (req.method === 'OPTIONS') return cors(new Response(null, { status: 204 }));
      if (url.pathname === '/') return text('Surrey League Compendium notifications: running.');
      if (url.pathname === '/v1/register' && req.method === 'POST') return cors(await register(req, env));
      if (url.pathname === '/v1/unregister' && req.method === 'POST') return cors(await unregister(req, env));
      if (url.pathname.startsWith('/admin/')) {
        if (!(await isAdmin(req, env))) return json({ error: 'not allowed' }, 401);
        if (url.pathname === '/admin/devices' && req.method === 'GET') return json(await devices(env));
        if (url.pathname === '/admin/batch' && req.method === 'POST') return json(await newBatch(req, env, ctx));
        if (url.pathname === '/admin/status' && req.method === 'GET') return json(await status(env));
        if (url.pathname === '/admin/test' && req.method === 'POST') return json(await testPush(req, env));
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
const validToken = (t) => typeof t === 'string' && /^[0-9a-f]{64,200}$/i.test(t);
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

// body: { summary, messages: [{ tokens: [...], title, body, image, threadId, url }] }
async function newBatch(req, env, ctx) {
  const b = await req.json();
  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  const approval = (env.APPROVAL || 'on') === 'on';
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

// TestFlight and App Store phones use Apple's live service; phones running a build
// straight from Xcode use the test ("sandbox") service. Try live first and remember.
async function sendOne(env, row, payload) {
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
  r.headers.set('access-control-allow-methods', 'POST, OPTIONS');
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
