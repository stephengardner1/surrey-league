/* Surrey League Compendium app: following and notifications.
   Adds a Notifications screen, Follow buttons on club and athlete pages, and
   connects to the back office that sends the notifications. */
import { diffLeague, messagesFor, currentSeason, seasonRaces } from './compose.mjs';

const CFG = window.SL_CONFIG || {};
const Cap = window.Capacitor;
const NATIVE = !!(Cap && Cap.isNativePlatform && Cap.isNativePlatform());
const Push = Cap && Cap.Plugins && Cap.Plugins.PushNotifications;
const Http = Cap && Cap.Plugins && Cap.Plugins.CapacitorHttp;

const CLUB_NAMES = {
  BEL: 'Belgrave Harriers', 'H/W': 'Hercules Wimbledon', HHH: 'Herne Hill Harriers', THH: 'Thames Hare & Hounds',
  KEN: 'Kent AC', 'G&G': 'Guildford & Godalming', HOL: 'Holland Sports', DUL: 'Dulwich Runners', WOK: 'Woking AC',
  RAN: 'Ranelagh Harriers', 'C/C': 'Clapham Chasers', SLH: 'South London Harriers', STR: 'Stragglers',
  REI: 'Reigate Priory AC', VAC: 'Veterans AC', 'W/W': 'Windmilers', CRO: 'Croydon Harriers', 'S&D': 'Sutton & District',
};
const GROUND = { BEL: '#eadfc8', HOL: '#d3dce8', HHH: '#edd9d3', 'G&G': '#d6e6d2', KEN: '#d3dce6', DUL: '#edd9d3', 'C/C': '#d6dee6', RAN: '#d3dce8', STR: '#f1e6c6', WOK: '#f2dfcf', REI: '#edd9d3', SLH: '#e6dcde', THH: '#dce2e6', 'H/W': '#f1e6c6', VAC: '#eaecef', 'W/W': '#e6dcdc' };
const clubName = (c) => CLUB_NAMES[c] || c;
const slug = (n) => (n || '').toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
const clubKey = (c) => c.toLowerCase().replace('/', '').replace('&', '');

// ---------- saved choices ----------
const BLANK = { men: false, women: false, corrections: true, clubs: [], runners: [] };
function loadFollow() {
  try { return { ...BLANK, ...JSON.parse(localStorage.getItem('sl-follow') || '{}') }; } catch { return { ...BLANK }; }
}
let follow = loadFollow();
let pushToken = localStorage.getItem('sl-push-token') || null;
let pushState = localStorage.getItem('sl-push-state') || 'unknown'; // unknown | granted | denied

function saveFollow() {
  localStorage.setItem('sl-follow', JSON.stringify(follow));
  sync();
  renderAll();
}
const anyFollow = () => follow.men || follow.women || follow.runners.length > 0;

// ---------- talking to the back office ----------
let syncTimer = null;
function sync() {
  clearTimeout(syncTimer);
  syncTimer = setTimeout(async () => {
    if (!pushToken || !CFG.api || /REPLACE-ME/.test(CFG.api)) return;
    const body = JSON.stringify({ token: pushToken, platform: 'ios', follow, adminCode: localStorage.getItem('sl-approver-code') || undefined });
    try {
      if (Http) await Http.post({ url: CFG.api + '/v1/register', headers: { 'Content-Type': 'application/json' }, data: JSON.parse(body) });
      else await fetch(CFG.api + '/v1/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body });
      localStorage.setItem('sl-synced', String(Date.now()));
    } catch (e) { console.warn('[SL] sync failed', e); }
  }, 600);
}

// ---------- push notifications ----------
async function setupPush() {
  if (!NATIVE || !Push) return;
  Push.addListener('registration', (t) => {
    pushToken = t.value; localStorage.setItem('sl-push-token', pushToken); sync();
  });
  Push.addListener('registrationError', (e) => console.warn('[SL] push registration error', e));
  Push.addListener('pushNotificationActionPerformed', (a) => {
    const url = a && a.notification && a.notification.data && a.notification.data.url;
    if (url && /\/approve\/[^/?#]+\?k=/.test(url)) openApproval(url);
    else if (url) go(url);
  });
  const p = await Push.checkPermissions();
  if (p.receive === 'granted') { pushState = 'granted'; await Push.register(); }
  else if (p.receive === 'denied') pushState = 'denied';
  localStorage.setItem('sl-push-state', pushState);
}
// Called from a tap, as Apple requires
async function askForPush() {
  if (!NATIVE || !Push) return;
  const p = await Push.requestPermissions();
  pushState = p.receive === 'granted' ? 'granted' : 'denied';
  localStorage.setItem('sl-push-state', pushState);
  if (pushState === 'granted') await Push.register();
  renderAll();
}
function go(url) {
  if (/^https?:/.test(url)) { location.href = url; return; } // opens in Safari
  if (url.startsWith('/#') || url.startsWith('#')) { location.hash = url.replace(/^\//, ''); return; }
  history.pushState({ sl: 1 }, '', url);
  window.dispatchEvent(new PopStateEvent('popstate'));
  window.scrollTo(0, 0);
}

// ---------- data for the screens ----------
let DATA = { men: null, women: null };
async function loadData() {
  const get = async (f) => { try { return await (await fetch(f)).json(); } catch { return null; } };
  [DATA.men, DATA.women] = await Promise.all([get('data.json'), get('data-women.json')]);
  delete LAST.men; delete LAST.women;
  renderAll();
}
function currentClubs() {
  const set = new Set();
  for (const lg of ['men', 'women']) {
    const d = DATA[lg]; if (!d) continue;
    const s = d.seasonsData[currentSeason(d)];
    for (const t of (s && s.standings) || []) set.add(t.club);
  }
  return [...set].sort((a, b) => clubName(a).localeCompare(clubName(b)));
}
function searchRunners(q) {
  q = q.trim().toLowerCase();
  if (q.length < 2) return [];
  const out = [];
  for (const lg of ['men', 'women']) {
    const d = DATA[lg]; if (!d) continue;
    for (const a of d.athletes || []) {
      if (!a.name || /^unknown/i.test(a.name)) continue;
      if (a.name.toLowerCase().includes(q)) out.push({ name: a.name, club: a.club, league: lg, races: a.races || 0, last: lastSeason(a, lg) });
    }
  }
  out.sort((x, y) => (y.last || '').localeCompare(x.last || '') || y.races - x.races);
  return out.slice(0, 8);
}
const LAST = {};
function lastSeason(a, lg) {
  if (!LAST[lg]) {
    LAST[lg] = {};
    for (const r of (DATA[lg] && DATA[lg].races) || []) for (const x of r.results || []) {
      const n = (x.n || x.name || '').toLowerCase();
      if (!LAST[lg][n] || LAST[lg][n] < r.season) LAST[lg][n] = r.season;
    }
  }
  return LAST[lg][a.name.toLowerCase()] || '';
}

// ---------- a little HTML helper ----------
const h = (tag, attrs = {}, ...kids) => {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k.startsWith('on')) el.addEventListener(k.slice(2).toLowerCase(), v);
    else if (k === 'style') el.style.cssText = v;
    else if (v === true) el.setAttribute(k, '');
    else if (v !== false && v != null) el.setAttribute(k, v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) el.append(k.nodeType ? k : String(k));
  return el;
};
const toggle = (label, on, onTap, sub) => h('div', { class: 'sl-row' },
  h('span', { class: 'sl-row-label' }, h('span', { class: 'sl-strong' }, label), sub ? h('span', { class: 'sl-sub' }, sub) : null),
  h('button', { type: 'button', class: 'sl-switch' + (on ? ' on' : ''), 'aria-pressed': on ? 'true' : 'false', 'aria-label': label, onclick: onTap }, h('span')));
// Club vest, drawn by the site's own vest artwork (vests.js), as an image so each one stands alone
const vest = (code) => {
  const svg = window.slVest ? window.slVest(code || '') : null;
  return svg ? h('img', { class: 'sl-vest', alt: '', 'aria-hidden': 'true', src: 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg) })
    : h('span', { class: 'sl-badge', style: `background:${GROUND[code] || '#f3f4f2'}` }, code);
};
// Runner picture: their portrait if they have one, otherwise the grey runner in their club's singlet
let PORTRAITS = null;
fetch('/portraits/portraits.json').then((r) => r.json()).then((p) => { PORTRAITS = p; renderPanel(); }).catch(() => {});
const portraitSrc = (name, club) => {
  const p = PORTRAITS && PORTRAITS[(name || '').toLowerCase()];
  if (p && (!club || !p.club || p.club === club)) return `/portraits/athletes/${p.file}.svg`;
  return club ? `/portraits/clubs/${club.replace(/\//g, '').replace(/&/g, 'and')}.svg` : null;
};
const face = (name, club) => {
  const src = portraitSrc(name, club);
  if (!src) return vest(club);
  const img = h('img', { class: 'sl-face', alt: '', 'aria-hidden': 'true', src });
  img.addEventListener('error', () => img.replaceWith(vest(club)), { once: true });
  return img;
};

// ---------- the Notifications screen ----------
let panel = null, query = '';
// ---------- Approving a batch of notifications (Steve's phone), inside the app ----------
let approvalEl = null;
async function openApproval(url) {
  const H = window.Capacitor?.Plugins?.CapacitorHttp;
  if (!H) { location.href = url; return; }
  if (!approvalEl) { approvalEl = h('div', { class: 'sl-panel', role: 'dialog', 'aria-modal': 'true', 'aria-label': 'Approve notifications' }); document.body.append(approvalEl); }
  approvalEl.hidden = false; document.body.classList.add('sl-lock');
  const close = () => { approvalEl.hidden = true; if (!panel || panel.hidden) document.body.classList.remove('sl-lock'); };
  const top = h('div', { class: 'sl-top' }, h('button', { type: 'button', class: 'sl-link', onclick: close }, '‹ Back'));
  const show = (...kids) => approvalEl.replaceChildren(top, ...kids.filter(Boolean));
  show(h('p', { class: 'sl-muted' }, 'Loading…'));
  let page;
  try { page = await H.get({ url, responseType: 'text' }); }
  catch (e) { show(h('div', { class: 'sl-head' }, h('h1', {}, 'Couldn’t load'), h('p', { class: 'sl-muted' }, 'Check your signal and tap the notification again.'))); return; }
  const doc = new DOMParser().parseFromString(String(page.data || ''), 'text/html');
  const title = doc.querySelector('h1')?.textContent || 'Notifications';
  const state = doc.querySelector('.state')?.textContent || '';
  const waiting = !!doc.querySelector('button[value="send"]');
  const items = [...doc.querySelectorAll('li')].map((li) => ({ t: li.querySelector('b')?.textContent || '', n: li.querySelector('.n')?.textContent || '', b: li.querySelector('pre')?.textContent || '' }));
  const act = async (action, label) => {
    show(h('p', { class: 'sl-muted' }, label));
    try { await H.post({ url, headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, data: 'action=' + action }); } catch (e) {}
    openApproval(url);
  };
  show(
    h('div', { class: 'sl-head' }, h('h1', {}, 'Approve notifications'), h('p', { class: 'sl-muted' }, title)),
    h('p', { class: 'sl-small' }, state),
    waiting ? h('div', { class: 'sl-approve-actions' },
      h('button', { type: 'button', class: 'sl-approve-go', onclick: () => act('send', 'Sending…') }, 'Send to everyone'),
      h('button', { type: 'button', class: 'sl-approve-stop', onclick: () => act('cancel', 'Cancelling…') }, 'Don’t send')) : null,
    items.length ? h('section', {}, h('div', { class: 'sl-label' }, items.length === 1 ? '1 different notification' : `${items.length} different notifications`),
      ...items.map((m) => h('div', { class: 'sl-note' }, h('span', { class: 'sl-appicon', 'aria-hidden': 'true' }),
        h('div', { class: 'sl-col sl-grow' }, h('span', { class: 'sl-strong' }, m.t, ' ', h('span', { class: 'sl-sub' }, m.n)), h('span', { class: 'sl-body' }, m.b))))) : null,
  );
}

function openPanel() { if (!panel) { panel = h('div', { class: 'sl-panel', role: 'dialog', 'aria-modal': 'true', 'aria-label': 'Notifications' }); document.body.append(panel); } panel.hidden = false; document.body.classList.add('sl-lock'); renderPanel(); }
function closePanel() { if (panel) panel.hidden = true; document.body.classList.remove('sl-lock'); }

async function change(fn) {
  const before = anyFollow();
  fn();
  if (!before && anyFollow() && pushState !== 'granted') await askForPush();
  saveFollow();
}

function renderPanel() {
  if (!panel || panel.hidden) return;
  const clubs = currentClubs();
  const results = searchRunners(query);
  panel.replaceChildren(...[
    h('div', { class: 'sl-top' }, h('button', { type: 'button', class: 'sl-link', onclick: closePanel }, '‹ Back')),
    h('div', { class: 'sl-head' }, h('h1', {}, 'Notifications'), h('p', { class: 'sl-muted' }, 'Results and corrections as soon as they’re published.')),
    pushState === 'denied' ? h('p', { class: 'sl-warn' }, 'Notifications are switched off for this app. Turn them on in your iPhone’s Settings › Surrey League › Notifications.') : null,
    !NATIVE ? h('p', { class: 'sl-warn' }, 'Notifications work in the iPhone app.') : null,
    h('section', {}, h('div', { class: 'sl-label' }, 'Leagues'), h('div', { class: 'sl-list' },
      toggle('Men', follow.men, () => change(() => { follow.men = !follow.men; })),
      toggle('Women', follow.women, () => change(() => { follow.women = !follow.women; })),
      toggle('Corrections', follow.corrections, () => change(() => { follow.corrections = !follow.corrections; }), 'When a result is changed after it’s published'))),
    h('section', {}, h('div', { class: 'sl-label' }, 'Your clubs'), h('div', { class: 'sl-list' },
      clubs.map((c) => h('button', { type: 'button', class: 'sl-row sl-pick', 'aria-pressed': follow.clubs.includes(c) ? 'true' : 'false',
        onclick: () => change(() => { follow.clubs = follow.clubs.includes(c) ? follow.clubs.filter((x) => x !== c) : [...follow.clubs, c]; }) },
        vest(c), h('span', { class: 'sl-grow' }, clubName(c)), h('span', { class: 'sl-tick' }, follow.clubs.includes(c) ? '✓' : '')))),
      h('p', { class: 'sl-small' }, 'Optional. Notifications will be tailored to the clubs you follow.')),
    h('section', {}, h('div', { class: 'sl-label' }, 'Runners'),
      h('div', { class: 'sl-list' }, follow.runners.map((r) => h('div', { class: 'sl-row' }, face(r.name, r.club),
        h('span', { class: 'sl-grow sl-col' }, h('span', { class: 'sl-strong' }, r.name), h('span', { class: 'sl-sub' }, `${clubName(r.club)} · ${r.league === 'women' ? 'Women' : 'Men'}`)),
        h('button', { type: 'button', class: 'sl-link', 'aria-label': 'Unfollow ' + r.name, onclick: () => change(() => { follow.runners = follow.runners.filter((x) => x !== r); }) }, 'Unfollow')))),
      h('label', { for: 'sl-search', class: 'sl-strong sl-pad' }, 'Find a runner'),
      h('input', { id: 'sl-search', type: 'search', autocomplete: 'off', placeholder: 'Type a name', value: query,
        oninput: (e) => { query = e.target.value; renderPanel(); document.getElementById('sl-search')?.focus(); } }),
      h('div', { class: 'sl-list' }, results.filter((m) => !follow.runners.some((r) => r.name === m.name && r.league === m.league)).map((m) =>
        h('div', { class: 'sl-row' }, face(m.name, m.club), h('span', { class: 'sl-grow sl-col' }, h('span', { class: 'sl-strong' }, m.name),
          h('span', { class: 'sl-sub' }, `${clubName(m.club)} · ${m.league === 'women' ? 'Women' : 'Men'}${m.last ? ' · last race ' + m.last : ''}`)),
          h('button', { type: 'button', class: 'sl-pill', 'aria-label': 'Follow ' + m.name,
            onclick: () => { query = ''; change(() => { follow.runners = [...follow.runners, { name: m.name, club: m.club, league: m.league }]; }); } }, 'Follow')))),
      query.trim().length >= 2 && !results.length ? h('p', { class: 'sl-muted' }, 'No runner by that name yet. Runners can be found once they’ve run a Surrey League race.') : null,
      h('p', { class: 'sl-small' }, 'Anyone who has run a Surrey League race. You’ll hear about their results even if their league is switched off.')),
    h('section', {}, h('div', { class: 'sl-label' }, 'What you’ll get'), preview()),
    h('p', { class: 'sl-small sl-foot' }, h('button', { type: 'button', class: 'sl-link sl-small', onclick: approverCode },
      localStorage.getItem('sl-approver-code') ? 'Approver: this phone approves notifications' : 'Approver code')),
    h('p', { class: 'sl-small' }, window.SL_LIVE_VERSION ? `App updated ${new Date(+localStorage.getItem('sl-live-at') || Date.now()).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })} (${window.SL_LIVE_VERSION})` : `Built-in version (${window.SL_BUILT_HASH || '–'})`),
  ].filter(Boolean));
}

// Steve's phone: typing the approver code makes it the phone that approves each batch
function approverCode() {
  const v = window.prompt('Approver code (only needed on the phone that approves notifications)', localStorage.getItem('sl-approver-code') || '');
  if (v === null) return;
  if (v.trim()) localStorage.setItem('sl-approver-code', v.trim()); else localStorage.removeItem('sl-approver-code');
  sync(); renderPanel();
}

// Preview: what the latest race would have sent, written by the same code as the real thing
function preview() {
  if (!anyFollow()) return h('p', { class: 'sl-muted' }, 'Turn on a league or follow a runner to get notifications.');
  const out = [];
  for (const lg of ['men', 'women']) {
    const d = DATA[lg]; if (!d) continue;
    const season = currentSeason(d);
    const races = seasonRaces(d, season); if (!races.length) continue;
    const last = races[races.length - 1].match;
    const prev = structuredClone(d); prev.races = prev.races.filter((r) => !(r.season === season && r.match === last));
    const events = diffLeague(prev, d, lg);
    for (const m of messagesFor(follow, events, { prev, next: d, portraits: null })) out.push(m);
  }
  if (!out.length) return h('p', { class: 'sl-muted' }, 'Nothing from the latest race for what you follow.');
  return h('div', { class: 'sl-previews' }, out.map((m) => h('div', { class: 'sl-note' },
    h('span', { class: 'sl-appicon', 'aria-hidden': 'true' }),
    h('div', { class: 'sl-col sl-grow' }, h('span', { class: 'sl-strong' }, m.title), h('span', { class: 'sl-body' }, m.body)))));
}

// ---------- Follow buttons on club and athlete pages ----------
let fab = null, bell = null, sheet = null;
function pageSubject() {
  const p = location.pathname, hsh = location.hash;
  let m = hsh.match(/^#(women\/)?athlete\/([^/]+)/i) || (!/^#./.test(hsh) && p.match(/^\/(women\/)?athlete\/([^/]+?)(?:-poster)?\/?$/i));
  if (m) {
    const lg = m[1] ? 'women' : 'men'; const d = DATA[lg];
    const a = d && (d.athletes || []).find((x) => slug(x.name) === m[2].toLowerCase());
    return a ? { kind: 'runner', name: a.name, club: a.club, league: lg } : null;
  }
  m = hsh.match(/^#(women\/)?club\/([^/]+)/i);
  if (m) {
    const code = currentClubs().find((c) => clubKey(c) === m[2].toLowerCase()) || Object.keys(CLUB_NAMES).find((c) => clubKey(c) === m[2].toLowerCase());
    return code ? { kind: 'club', club: code, league: m[1] ? 'women' : 'men' } : null;
  }
  return null;
}
function renderFab() {
  if (!document.querySelector('.sl-statusbar')) document.body.append(h('div', { class: 'sl-statusbar', 'aria-hidden': 'true' }));
  if (!bell) { bell = h('button', { type: 'button', class: 'sl-bell', 'aria-label': 'Notifications', onclick: openPanel }, bellIcon()); document.body.append(bell); }
  placeFollow();
}
// Follow button: a small bell straight after the runner's or club's name at the top of their page
function placeFollow() {
  const s = pageSubject();
  const heading = s && [...document.querySelectorAll('h1')].find((e) => e.offsetParent && !e.closest('header'));
  const on = s && (s.kind === 'runner' ? follow.runners.some((r) => r.name === s.name && r.league === s.league) : follow.clubs.includes(s.club));
  const key = s ? `${s.kind}|${s.name || s.club}|${s.league}|${on}` : '';
  document.querySelectorAll('.sl-follow').forEach((b) => { if (b.dataset.key !== key || b.parentElement !== heading) b.remove(); });
  if (!s || !heading || heading.querySelector('.sl-follow')) return;
  const label = s.kind === 'runner' ? s.name : clubName(s.club);
  heading.append(h('button', { type: 'button', class: 'sl-follow' + (on ? ' on' : ''), 'data-key': key, 'aria-pressed': on ? 'true' : 'false',
    'aria-label': on ? `Following ${label}. Tap to stop` : `Follow ${label}`,
    onclick: (e) => {
      e.stopPropagation();
      if (s.kind === 'runner') change(() => { follow.runners = on ? follow.runners.filter((r) => !(r.name === s.name && r.league === s.league)) : [...follow.runners, { name: s.name, club: s.club, league: s.league }]; });
      else { change(() => { follow.clubs = on ? follow.clubs.filter((c) => c !== s.club) : [...follow.clubs, s.club]; if (!on && !follow.men && !follow.women) follow[s.league] = true; }); if (!on) openSheet(s.club); }
      toast(on ? `Stopped following ${label}` : `Following ${label}`);
    } }, bellIcon(!!on)));
}
let toastEl = null;
function toast(text) {
  toastEl?.remove();
  toastEl = h('div', { class: 'sl-toast', role: 'status' }, text);
  document.body.append(toastEl);
  const t = toastEl; setTimeout(() => t.remove(), 2200);
}
let placing = 0;
new MutationObserver(() => { if (!placing) placing = setTimeout(() => { placing = 0; placeFollow(); }, 120); }).observe(document.documentElement, { childList: true, subtree: true });
function openSheet(club) {
  sheet?.remove();
  const pill = (lg) => h('button', { type: 'button', class: 'sl-chip' + (follow[lg] ? ' on' : ''), 'aria-pressed': follow[lg] ? 'true' : 'false',
    onclick: () => change(() => { follow[lg] = !follow[lg]; }) }, (follow[lg] ? '✓ ' : '') + (lg === 'men' ? 'Men' : 'Women'));
  sheet = h('div', { class: 'sl-sheet', role: 'dialog', 'aria-label': 'Choose leagues', 'data-club': club },
    h('p', {}, `You’ll get ${clubName(club)}’s results and corrections for:`),
    h('div', { class: 'sl-chips' }, pill('men'), pill('women')),
    h('div', { class: 'sl-sheet-foot' }, h('button', { type: 'button', class: 'sl-link', onclick: () => { sheet.remove(); sheet = null; openPanel(); } }, 'Notification settings'),
      h('button', { type: 'button', class: 'sl-link', onclick: () => { sheet.remove(); sheet = null; } }, 'Done')));
  document.body.append(sheet);
}
function bellIcon(filled) {
  const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  s.setAttribute('viewBox', '0 0 24 24'); s.setAttribute('width', '18'); s.setAttribute('height', '18'); s.setAttribute('aria-hidden', 'true');
  s.innerHTML = `<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" fill="${filled ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>`;
  return s;
}

function renderAll() { renderFab(); renderPanel(); if (sheet) openSheet(sheet.dataset.club); }

// Watch the site's page changes
for (const fn of ['pushState', 'replaceState']) {
  const orig = history[fn].bind(history);
  history[fn] = (...a) => { const r = orig(...a); setTimeout(renderFab, 0); return r; };
}
window.addEventListener('popstate', () => setTimeout(renderFab, 0));
window.addEventListener('hashchange', () => setTimeout(renderFab, 0));
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && panel && !panel.hidden) closePanel(); });

loadData();
setupPush().then(renderAll);
// Keep the back office up to date (e.g. after a reinstall)
if (pushToken) sync();

// ---------- Pull to refresh (the app turns off iPhone's own bounce, so it's drawn here) ----------
// Pull down at the top of a page: the page follows your finger with some resistance and a ring
// under the title fills; let go past the line to check for new results. Springs back gently.
(function pullToRefresh() {
  if (!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform())) return;
  const TRIGGER = 64, MAX = 92, HOLD = 52, R = 9, C = 2 * Math.PI * R;
  const SPRING = 'transform 420ms cubic-bezier(.3, 1.25, .5, 1)'; // settles with a slight overshoot
  const ring = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  ring.setAttribute('viewBox', '0 0 24 24'); ring.setAttribute('width', '24'); ring.setAttribute('height', '24');
  ring.innerHTML = `<circle cx="12" cy="12" r="${R}" fill="none" stroke="var(--sl-rule)" stroke-width="2"></circle>`
    + `<circle class="sl-ptr-arc" cx="12" cy="12" r="${R}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-dasharray="${C}" stroke-dashoffset="${C}" transform="rotate(-90 12 12)"></circle>`;
  const ind = h('div', { class: 'sl-ptr', 'aria-hidden': 'true' }, ring);
  const live = h('div', { class: 'sl-visually-hidden', role: 'status', 'aria-live': 'polite' });
  document.body.append(ind, live);
  const arc = ring.querySelector('.sl-ptr-arc');
  const main = () => document.getElementById('main-content');
  const top = () => { const t = document.querySelector('header > div:first-child'); const r = t && t.getBoundingClientRect(); return r && r.bottom > 0 ? r.bottom : 0; };
  const blocked = () => busy || document.body.classList.contains('sl-lock') || (panel && !panel.hidden) || (approvalEl && !approvalEl.hidden);
  let startY = null, pull = 0, busy = false, armed = false;

  function draw(px, animate) {
    const m = main(); if (!m) return;
    m.style.transition = animate ? SPRING : 'none';
    m.style.transform = px ? `translateY(${px}px)` : '';
    ind.style.transition = animate ? 'opacity 200ms ease-out, transform 420ms cubic-bezier(.3, 1.25, .5, 1)' : 'none';
    ind.style.top = top() + 'px';
    ind.style.opacity = px ? Math.min(1, px / 32) : 0;
    ind.style.transform = `translate(-50%, ${Math.max(0, px - 36) / 2 + 8}px)`;
    if (!busy) arc.setAttribute('stroke-dashoffset', String(C * (1 - Math.min(1, px / TRIGGER))));
    const nowArmed = px >= TRIGGER;
    if (nowArmed !== armed) { armed = nowArmed; ind.classList.toggle('armed', armed); }
  }
  const settle = () => { draw(0, true); setTimeout(() => { const m = main(); if (m && !pull) m.style.transition = ''; }, 450); };

  addEventListener('touchstart', (e) => {
    startY = (blocked() || window.scrollY > 0 || e.touches.length !== 1) ? null : e.touches[0].clientY;
    pull = 0;
  }, { passive: true });
  addEventListener('touchmove', (e) => {
    if (startY == null) return;
    const dy = e.touches[0].clientY - startY;
    if (window.scrollY > 0 || dy <= 0) { if (pull) { pull = 0; draw(0, false); } return; }
    pull = Math.min(MAX, dy * 0.45); // resistance: the page moves less than your finger
    draw(pull, false);
  }, { passive: true });
  const end = () => {
    if (startY == null) return;
    startY = null;
    if (pull >= TRIGGER) refresh(); else { pull = 0; settle(); }
  };
  addEventListener('touchend', end, { passive: true });
  addEventListener('touchcancel', end, { passive: true });

  // What the app showed last time, from the saved copies early.js keeps
  const saved = (path) => new Promise((res) => {
    try {
      const r = indexedDB.open('sl-cache', 1);
      r.onsuccess = () => { try { const q = r.result.transaction('files').objectStore('files').get(path); q.onsuccess = () => res(q.result ? q.result.text : null); q.onerror = () => res(null); } catch (e) { res(null); } };
      r.onerror = () => res(null);
    } catch (e) { res(null); }
  });

  async function refresh() {
    busy = true; pull = HOLD; draw(HOLD, true);
    ind.classList.add('spin'); arc.setAttribute('stroke-dashoffset', String(C * 0.72));
    const files = ['data.json', 'data-women.json'];
    const started = Date.now();
    let changed = false, offline = false;
    try {
      const before = await Promise.all(files.map(saved));
      const after = await Promise.all(files.map((f) => fetch('/' + f, { cache: 'no-store' }).then((r) => r.text())));
      offline = window.SL_DATA_SOURCE !== 'live';
      changed = !offline && after.some((t, i) => before[i] != null && t !== before[i]);
    } catch (e) { offline = true; }
    await new Promise((r) => setTimeout(r, Math.max(0, 700 - (Date.now() - started)))); // long enough to see it working
    const msg = changed ? 'New results' : offline ? 'No signal: showing saved results' : 'Up to date';
    live.textContent = msg;
    ind.classList.remove('spin'); busy = false; pull = 0;
    settle();
    toast(msg);
    if (changed) setTimeout(() => location.reload(), 600);
  }
})();
