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

// ---------- slarchive.org links open in the app ----------
// With the app installed, tapping a slarchive.org link (in WhatsApp, Messages, Mail…) opens the app instead of Safari,
// straight to that page. iOS hands us the link; we open the same page inside the app. Needs a build with the App plugin
// and the associated-domains setting; on older builds this does nothing and links keep opening in Safari.
(function openLinksInApp() {
  const AppP = NATIVE && window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.App;
  if (!AppP || !AppP.addListener) return;
  const open = (link) => {
    let u; try { u = new URL(link); } catch { return; }
    if (!/(^|\.)slarchive\.org$/i.test(u.hostname)) return;
    const path = (u.pathname || '/') + u.search + u.hash;
    if (path === '/' || path === '') { go('/'); return; }
    go(path);
  };
  AppP.addListener('appUrlOpen', (e) => e && e.url && open(e.url));
  // A link that started the app from closed: open it once (not again when the app refreshes itself later)
  if (AppP.getLaunchUrl) AppP.getLaunchUrl().then((r) => {
    const url = r && r.url; if (!url) return;
    try { if (sessionStorage.getItem('sl-launch-url') === url) return; sessionStorage.setItem('sl-launch-url', url); } catch {}
    setTimeout(() => open(url), 300);
  }).catch(() => {});
})();

// ---------- data for the screens ----------
let DATA = { men: null, women: null };
async function loadData() {
  const get = async (f) => { try { return await (await fetch(f)).json(); } catch { return null; } };
  [DATA.men, DATA.women] = await Promise.all([get('data.json'), get('data-women.json')]);
  delete LAST.men; delete LAST.women; delete ROSTER.men; delete ROSTER.women;
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
// Everyone who appears in the results, by league: the name as last printed, their latest club and season, and how many races.
// (Built from the results themselves because the women's file has no ready-made list of athletes.)
const ROSTER = {};
function roster(lg) {
  if (!ROSTER[lg]) {
    const m = new Map();
    const races = [...((DATA[lg] && DATA[lg].races) || [])].sort((a, b) => String(a.season).localeCompare(String(b.season)) || (a.match || 0) - (b.match || 0));
    for (const r of races) for (const x of r.results || []) {
      const name = x.n || x.name; if (!name || /^unknown/i.test(name)) continue;
      const k = name.toLowerCase(); const e = m.get(k) || { name, races: 0 };
      e.name = name; e.club = x.c || x.club || e.club; e.last = r.season; e.races++; m.set(k, e);
    }
    ROSTER[lg] = m;
  }
  return ROSTER[lg];
}
// An active runner has run this season or last season: the only runners who get a follow bell on their page.
// A runner's most recent appearance, looking under every spelling the archive knows them by
function latestRun(name, lg) {
  const d = DATA[lg]; if (!d || !name) return null;
  const names = [name, ...((d.athleteAliases || {})[name] || [])];
  let best = null;
  for (const n of names) { const e = roster(lg).get(n.toLowerCase()); if (e && (!best || e.last > best.last)) best = e; }
  return best;
}
function isActive(name, lg) {
  const e = latestRun(name, lg); if (!e) return false;
  const seasons = Object.keys(DATA[lg].seasonsData || {}).sort();
  return e.last >= (seasons[seasons.length - 2] || seasons[seasons.length - 1] || '');
}
function searchRunners(q) {
  q = q.trim().toLowerCase();
  if (q.length < 2) return [];
  const out = [];
  for (const lg of ['men', 'women']) {
    const d = DATA[lg]; if (!d) continue;
    const seen = new Set();
    for (const a of d.athletes || []) {
      if (!a.name || /^unknown/i.test(a.name)) continue;
      seen.add(a.name.toLowerCase());
      if (a.name.toLowerCase().includes(q)) out.push({ name: a.name, club: a.club, league: lg, races: a.races || 0, last: lastSeason(a, lg) });
    }
    // Runners in the results but not in that list (all the women, and newcomers), leaving out old spellings of someone already listed
    const variants = new Set([...Object.values(d.athleteAliases || {}).flat(), ...Object.keys(d.aliases || {})].map((n) => n.toLowerCase()));
    for (const [k, e] of roster(lg)) if (!seen.has(k) && !variants.has(k) && k.includes(q)) out.push({ name: e.name, club: e.club, league: lg, races: e.races, last: e.last });
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
  h('button', { type: 'button', role: 'switch', class: 'sl-switch' + (on ? ' on' : ''), 'aria-checked': on ? 'true' : 'false', 'aria-label': label, onclick: onTap }, h('span')));
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

const tellNav = (open) => window.dispatchEvent(new CustomEvent('sl-following', { detail: open }));
let panelOpen = false;
const BEHIND = '#main-content, #root footer, .app-top, a[href="#main-content"]';
function setBehind(hide) {
  if (hide) document.querySelectorAll(BEHIND).forEach((el) => { if (!el.hasAttribute('inert')) { el.setAttribute('inert', ''); el.setAttribute('data-sl-inert', ''); } });
  else document.querySelectorAll('[data-sl-inert]').forEach((el) => { el.removeAttribute('inert'); el.removeAttribute('data-sl-inert'); });
}
function openPanel() {
  if (!panel) { panel = h('div', { class: 'sl-panel', role: 'dialog', 'aria-labelledby': 'sl-following-title' }); document.body.append(panel); }
  const was = panelOpen;
  panelOpen = true; panel.hidden = false; panel.scrollTop = 0; document.body.classList.add('sl-lock'); renderPanel(); tellNav(true);
  setBehind(true);
  if (!was) { const t = document.getElementById('sl-following-title'); if (t) t.focus({ preventScroll: true }); }
}
function closePanel() {
  const was = panelOpen; panelOpen = false; if (panel) panel.hidden = true; document.body.classList.remove('sl-lock'); setBehind(false);
  if (was) { query = ''; tellNav(false);
    // hand VoiceOver and the keyboard back to the Following tab, unless something on the page has already taken focus
    const a = document.activeElement;
    if (!a || a === document.body || panel.contains(a)) { const tab = [...document.querySelectorAll('.app-nav > button')].find((b) => b.textContent.trim() === 'Following'); if (tab) tab.focus({ preventScroll: true }); } }
}
// The floating nav (drawn by the site's page) opens and closes the Following screen through this
window.slFollowing = (open) => { if (open) openPanel(); else closePanel(); };
// Privacy and Help pages open over the app (in-app browser), like FantaXC
function openWeb(url) {
  const C = window.Capacitor;
  if (C && C.isPluginAvailable && C.isPluginAvailable('Browser')) { C.Plugins.Browser.open({ url, presentationStyle: 'popover' }); return; }
  window.open(url, '_blank');
}
// FantaXC: Richard's site opens over the app, with Done to come back (an in-app browser if the build has one)
let fanta = null;
window.slFantaXC = () => {
  const url = 'https://fantaxc.com/surrey-league';
  const C = window.Capacitor;
  if (C && C.isPluginAvailable && C.isPluginAvailable('Browser')) { C.Plugins.Browser.open({ url, presentationStyle: 'popover' }); return; }
  fanta?.remove();
  const done = () => { fanta?.remove(); fanta = null; };
  fanta = h('div', { class: 'sl-web', role: 'dialog', 'aria-modal': 'true', 'aria-label': 'FantaXC' },
    h('div', { class: 'sl-web-bar' }, h('button', { type: 'button', class: 'sl-link', onclick: done }, 'Done'), h('span', { class: 'sl-strong' }, 'FantaXC'),
      h('a', { class: 'sl-link', href: url }, 'Safari')),
    h('iframe', { src: url, title: 'FantaXC', allow: 'clipboard-write' }));
  document.body.append(fanta);
};

async function change(fn) {
  const before = anyFollow();
  fn();
  if (!before && anyFollow() && pushState !== 'granted') await askForPush();
  saveFollow();
}

function openPage(hash) { closePanel(); location.hash = hash; window.scrollTo(0, 0); }
function searchClubs(q) {
  q = q.trim().toLowerCase(); if (q.length < 2) return [];
  return Object.keys(CLUB_NAMES).filter((c) => !follow.clubs.includes(c) && (clubName(c).toLowerCase().includes(q) || c.toLowerCase() === q)).slice(0, 4);
}
function renderPanel() {
  if (!panel || panel.hidden) return;
  const results = searchRunners(query).filter((m) => !follow.runners.some((r) => r.name === m.name && r.league === m.league));
  const clubHits = searchClubs(query);
  const none = !follow.clubs.length && !follow.runners.length;
  // the screen is redrawn after every change, so note which control had focus and give it back afterwards
  const act = document.activeElement, held = act && panel.contains(act) && act.id !== 'sl-search' ? [act.tagName, act.getAttribute('aria-label') || act.textContent] : null;
  panel.replaceChildren(...[
    h('div', { class: 'sl-head' }, h('h1', { id: 'sl-following-title', tabindex: '-1' }, 'Following'), h('p', { class: 'sl-muted' }, 'Get a notification on this phone the moment results are published for the leagues, clubs and runners you follow.')),
    pushState === 'denied' ? h('p', { class: 'sl-warn' }, 'Notifications are switched off for this app. Turn them on in your iPhone’s Settings › Surrey League › Notifications.') : null,
    !NATIVE ? h('p', { class: 'sl-warn' }, 'Notifications work in the iPhone app.') : null,
    h('section', {}, h('div', { class: 'sl-label' }, 'Leagues'), h('div', { class: 'sl-list' },
      toggle('Men', follow.men, () => change(() => { follow.men = !follow.men; })),
      toggle('Women', follow.women, () => change(() => { follow.women = !follow.women; })))),
    h('section', {}, h('div', { class: 'sl-label' }, 'Clubs and runners'),
      none ? h('p', { class: 'sl-muted' }, 'Nobody yet. Add a club or runner below, or tap the bell beside their name.') : null,
      h('div', { class: 'sl-list' },
        follow.clubs.map((c) => h('div', { class: 'sl-row' },
          h('button', { type: 'button', class: 'sl-open', onclick: () => openPage('#club/' + clubKey(c)) }, vest(c), h('span', { class: 'sl-grow sl-strong' }, clubName(c))),
          h('button', { type: 'button', class: 'sl-link', 'aria-label': 'Unfollow ' + clubName(c), onclick: () => change(() => { follow.clubs = follow.clubs.filter((x) => x !== c); }) }, 'Unfollow'))),
        follow.runners.map((r) => h('div', { class: 'sl-row' },
          h('button', { type: 'button', class: 'sl-open', onclick: () => openPage('#' + (r.league === 'women' ? 'women/' : '') + 'athlete/' + slug(r.name)) }, face(r.name, r.club),
            h('span', { class: 'sl-grow sl-col' }, h('span', { class: 'sl-strong' }, r.name), h('span', { class: 'sl-sub' }, `${clubName(r.club)}, ${r.league === 'women' ? 'women' : 'men'}`))),
          h('button', { type: 'button', class: 'sl-link', 'aria-label': 'Unfollow ' + r.name, onclick: () => change(() => { follow.runners = follow.runners.filter((x) => x !== r); }) }, 'Unfollow')))),
      h('label', { class: 'sl-search' }, searchIcon(), h('input', { id: 'sl-search', type: 'search', autocomplete: 'off', placeholder: 'Add a club or runner', 'aria-label': 'Add a club or runner', value: query,
        oninput: (e) => { query = e.target.value; renderPanel(); const f = document.getElementById('sl-search'); if (f) { f.focus(); f.setSelectionRange(query.length, query.length); } } })),
      h('div', { class: 'sl-list' },
        clubHits.map((c) => h('div', { class: 'sl-row' }, vest(c), h('span', { class: 'sl-grow sl-strong' }, clubName(c)),
          h('button', { type: 'button', class: 'sl-pill', 'aria-label': 'Follow ' + clubName(c), onclick: () => { query = ''; change(() => { follow.clubs = [...follow.clubs, c]; }); } }, 'Follow'))),
        results.map((m) => h('div', { class: 'sl-row' }, face(m.name, m.club), h('span', { class: 'sl-grow sl-col' }, h('span', { class: 'sl-strong' }, m.name),
          h('span', { class: 'sl-sub' }, `${clubName(m.club)}, ${m.league === 'women' ? 'women' : 'men'}${m.last ? ', last race ' + m.last : ''}`)),
          h('button', { type: 'button', class: 'sl-pill', 'aria-label': 'Follow ' + m.name,
            onclick: () => { query = ''; change(() => { follow.runners = [...follow.runners, { name: m.name, club: m.club, league: m.league }]; }); } }, 'Follow')))),
      query.trim().length >= 2 && !results.length && !clubHits.length ? h('p', { class: 'sl-muted' }, 'Nothing by that name. Runners can be found once they’ve run a Surrey League race.') : null,
      h('p', { class: 'sl-small' }, 'You’ll get a notification for a runner’s results even if their league is switched off.')),
    h('section', {}, h('div', { class: 'sl-list' },
      toggle('Corrections to results', follow.corrections, () => change(() => { follow.corrections = !follow.corrections; }), 'Get a notification when a result is changed after it’s published'))),
    h('p', { class: 'sl-small sl-foot sl-legal' },
      h('button', { type: 'button', class: 'sl-link sl-small', onclick: () => openWeb('https://slarchive.org/privacy') }, 'Privacy'), ' · ',
      h('button', { type: 'button', class: 'sl-link sl-small', onclick: () => openWeb('https://slarchive.org/support') }, 'Help')),
    h('p', { class: 'sl-small' }, h('button', { type: 'button', class: 'sl-link sl-small', onclick: approverCode },
      localStorage.getItem('sl-approver-code') ? 'Approver: this phone approves notifications' : 'Approver code')),
    h('p', { class: 'sl-small' }, window.SL_LIVE_VERSION ? `App updated ${new Date(+localStorage.getItem('sl-live-at') || Date.now()).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })} (${window.SL_LIVE_VERSION})` : `Built-in version (${window.SL_BUILT_HASH || '–'})`),
  ].filter(Boolean));
  if (held) {
    const again = [...panel.querySelectorAll('button, input')].find((e) => e.tagName === held[0] && (e.getAttribute('aria-label') || e.textContent) === held[1]);
    (again || document.getElementById('sl-following-title'))?.focus({ preventScroll: true });
  }
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
    const want = m[2].toLowerCase();
    const a = d && ((d.athletes || []).find((x) => slug(x.name) === want) || [...roster(lg).values()].find((x) => slug(x.name) === want));
    // The bell is only for active runners (see isActive); the club shown is the one they last ran for
    return a && isActive(a.name, lg) ? { kind: 'runner', name: a.name, club: latestRun(a.name, lg).club || a.club, league: lg } : null;
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
  placeFollow();
}
// Follow button: a small bell straight after the runner's or club's name at the top of their page
let tapped = null;
function placeFollow() {
  const s = pageSubject();
  const heading = s && [...document.querySelectorAll('h1')].find((e) => e.offsetParent && !e.closest('header'));
  const on = s && (s.kind === 'runner' ? follow.runners.some((r) => r.name === s.name && r.league === s.league) : follow.clubs.includes(s.club));
  const key = s ? `${s.kind}|${s.name || s.club}|${s.league}|${on}` : '';
  document.querySelectorAll('.sl-follow').forEach((b) => { const w = b.closest('.sl-follow-wrap') || b; if (b.dataset.key !== key || !heading || !heading.contains(w)) w.remove(); });
  if (!s || !heading || heading.querySelector('.sl-follow')) return;
  const label = s.kind === 'runner' ? s.name : clubName(s.club);
  // On a runner's page the bell goes inside the heading's no-break tail, straight after the surname and before the Power of 10
  // mark; elsewhere a word joiner glues it to the name's last word. Either way a long name never leaves it alone on a line
  const tail = heading.querySelector('[data-name-tail]');
  const bellEl = h('span', { class: 'sl-follow-wrap' }, '\u2060', h('button', { type: 'button', class: 'sl-follow' + (on ? ' on' : '') + (tapped === (s.name || s.club) ? (on ? ' sl-rung' : ' sl-hushed') : ''), 'data-key': key, 'aria-pressed': on ? 'true' : 'false',
    'aria-label': on ? `Following ${label}. Tap to stop` : `Follow ${label}`,
    onclick: (e) => {
      e.stopPropagation();
      tapped = s.name || s.club; setTimeout(() => { tapped = null; }, 1200); // the new bell swings once (see .sl-rung)
      if (s.kind === 'runner') change(() => { follow.runners = on ? follow.runners.filter((r) => !(r.name === s.name && r.league === s.league)) : [...follow.runners, { name: s.name, club: s.club, league: s.league }]; });
      else { change(() => { follow.clubs = on ? follow.clubs.filter((c) => c !== s.club) : [...follow.clubs, s.club]; if (!on && !follow.men && !follow.women) follow[s.league] = true; }); if (!on) openSheet(s.club); }
      toast(on ? `Stopped following ${label}` : `Following ${label}`);
    } }, bellIcon(!!on, s.club)));
  if (tail) tail.insertBefore(bellEl, tail.querySelector('a')); else heading.append(bellEl);
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
    h('div', { class: 'sl-sheet-foot' }, h('button', { type: 'button', class: 'sl-link', onclick: () => { sheet.remove(); sheet = null; openPanel(); } }, 'Following'),
      h('button', { type: 'button', class: 'sl-link', onclick: () => { sheet.remove(); sheet = null; } }, 'Done')));
  document.body.append(sheet);
}
const BELL = 'M44 174 44 175 47 175 47 175 60 175 72 174 82 174 168 174 180 174 192 174 196 175 196 174 198 172 198 170 198 168 198 166 196 164 196 163 190 164 183 164 181 159 177 150 176 142 174 131 174 119 174 100 173 91 172 87 171 79 168 71 166 67 162 62 157 57 152 52 146 49 140 46 134 44 128 43 128 29 127 29 127 27 124 25 122 24 118 24 117 25 114 26 113 29 112 29 112 42 106 43 99 45 94 47 90 49 84 53 79 58 77 61 73 67 70 75 68 82 67 87 66 96 66 116 66 128 65 139 63 147 60 154 56 164 44 163 44 164 43 165 42 167 41 169 42 170 42 172ZM73 164 73 164 76 158 78 152 79 145 80 139 81 126 82 96 82 89 85 80 87 74 89 70 94 64 100 59 106 55 111 53 120 52 126 52 132 53 137 55 139 56 143 59 149 64 153 71 156 79 157 86 158 92 159 123 159 132 160 139 161 145 163 151 165 157 169 164ZM97 198 96 199 98 201 102 204 105 205 110 207 114 208 119 209 124 210 128 209 132 209 135 208 139 205 143 202 145 199 144 199 145 197 144 194 143 191 140 189 137 189 134 189 132 191 131 191 129 194 127 197 124 199 121 200 117 200 113 199 112 198 110 196 108 192 107 192 105 191 103 190 101 191 99 191 98 193 97 195Z';
const BELL_FILL = 'M60 169 62 167 63 165 65 162 66 160 67 157 69 155 69 152 70 149 71 147 72 144 72 141 73 138 73 135 73 132 74 129 74 126 74 123 74 119 74 116 74 113 74 110 74 106 74 103 74 100 74 96 74 92 75 88 76 84 76 81 77 77 79 74 80 71 81 68 83 66 85 63 87 61 89 59 91 57 94 55 96 53 99 52 101 51 104 49 107 49 110 48 113 47 117 47 120 47 123 47 127 47 130 48 133 49 136 49 139 50 141 52 144 53 146 55 149 57 151 59 153 61 155 63 157 66 159 68 160 71 161 74 163 77 164 81 164 84 165 88 166 92 166 96 166 100 166 103 166 106 166 110 166 113 166 116 166 119 166 123 166 126 166 129 167 132 167 135 167 138 168 141 168 144 169 147 170 149 171 152 171 155 173 157 174 160 175 162 177 165 178 167 180 169Z';
const BELL_RING = 'M193 68 193 69 196 75 199 80 201 86 202 92 203 98 203 104 202 110 201 117 201 117 202 119 204 121 206 122 209 122 211 121 213 119 213 119 214 110 215 102 214 97 214 92 212 85 210 78 208 74 205 69 201 63 201 63 198 63 195 64 194 66ZM25 102 26 110 27 119 28 119 29 121 31 122 34 122 36 121 37 119 38 117 39 117 38 111 37 104 38 98 39 90 41 85 43 79 45 75 48 69 48 69 48 67 47 65 46 64 44 62 42 62 40 62 38 63 38 63 34 69 32 73 29 80 27 88 26 95Z';
const SEARCH = 'M34 105 34 112 35 118 37 124 39 132 43 138 47 144 51 150 56 154 60 158 67 162 73 166 79 168 85 170 91 172 97 173 104 174 110 174 118 173 124 172 131 170 137 167 143 164 148 161 191 204 195 209 198 214 199 213 202 214 204 214 206 214 210 212 211 211 213 210 213 208 214 204 214 202 213 199 214 198 209 195 202 188 162 148 167 140 170 133 173 127 175 120 176 112 176 105 176 98 175 92 173 84 170 78 167 72 163 66 159 61 154 56 149 51 143 48 137 44 131 42 125 40 119 38 113 37 106 36 98 36 93 37 86 38 79 40 72 43 67 46 61 49 55 55 51 59 48 62 46 65 43 70 39 77 37 83 36 87 35 91 34 97ZM56 107 57 100 57 95 59 91 60 86 62 82 65 77 68 73 71 70 74 66 78 63 82 61 87 58 91 57 96 55 101 54 106 54 111 54 116 54 123 57 129 60 133 63 137 66 141 69 144 73 146 77 149 82 151 86 152 91 153 95 154 100 154 105 153 110 152 115 150 122 148 128 145 133 142 137 139 140 136 144 132 147 128 149 123 152 119 153 114 155 109 156 104 156 99 156 94 156 90 154 85 153 81 150 77 147 73 144 69 141 66 137 64 133 61 128 59 124 58 119 57 115Z';
const mix = (a, b, t) => '#' + [1, 3, 5].map((k) => Math.round(parseInt(a.slice(k, k + 2), 16) + (parseInt(b.slice(k, k + 2), 16) - parseInt(a.slice(k, k + 2), 16)) * t).toString(16).padStart(2, '0')).join('');
const hex6 = (c) => (c.length === 4 ? '#' + [1, 2, 3].map((k) => c[k] + c[k]).join('') : c).toLowerCase();
// The club's main kit colour, read from its singlet artwork (first colour that isn't white)
function kitColour(club) {
  const svg = window.slVest && club ? window.slVest(club).split('<g transform')[0] : '';
  const all = [...svg.matchAll(/(?:fill|stroke)="(#[0-9a-fA-F]{3,6})"/g)].map((m) => hex6(m[1]));
  return all.find((c) => c !== '#ffffff') || '#686e66';
}
function pen(d, size) {
  const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  s.setAttribute('viewBox', '0 0 240 240'); s.setAttribute('width', size); s.setAttribute('height', size); s.setAttribute('aria-hidden', 'true');
  s.innerHTML = d; return s;
}
const searchIcon = () => pen(`<path d="${SEARCH}" fill="currentColor" fill-rule="evenodd"/>`, 18);
function bellIcon(on, club) {
  if (!on) return pen(`<path d="${BELL}" fill="currentColor" fill-rule="evenodd"/>`, 26);
  const tint = mix(hex6(GROUND[club] || '#e9ebe7'), kitColour(club), 0.38);
  return pen(`<path d="${BELL_FILL}" fill="${tint}"/><path d="${BELL}" fill="currentColor" fill-rule="evenodd"/><path d="${BELL_RING}" fill="currentColor" fill-rule="evenodd"/>`, 26);
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

// ---------- Text size: follow the iPhone's own Text Size setting (Settings › Display & Brightness › Text Size) ----------
// iPhone tells web pages its chosen text size through the "-apple-system-body" font: 17px at the standard setting,
// larger as the slider moves up. When it is set larger, the app's text grows in proportion, up to 112% (one notch up).
// That is as far as the screens still fit an iPhone's width; if a screen would spill off the side at that size, the
// text steps back down until it fits. Going further needs the tables redesigning for big text; pinch to zoom covers
// the rest. Smaller settings leave the app as designed. The floating nav keeps its size, as iPhone tab bars do
// (see .app-nav in app.css). window.SL_TEXT_PX stands in for the iPhone's setting when testing in a browser.
(function textSize() {
  const TEST = +window.SL_TEXT_PX || 0;
  if (!TEST) {
    if (!NATIVE || (Cap.getPlatform && Cap.getPlatform() !== 'ios')) return;
    if (!(window.CSS && CSS.supports && CSS.supports('font', '-apple-system-body'))) return;
  }
  let max = 112, now = 100;
  const root = document.documentElement;
  const probe = h('div', { 'aria-hidden': 'true', style: 'font:-apple-system-body;position:absolute;left:-999px;top:0;visibility:hidden;pointer-events:none' }, 'M');
  document.body.append(probe);
  const set = (pct) => { now = pct; root.style.setProperty('-webkit-text-size-adjust', pct + '%'); root.style.setProperty('text-size-adjust', pct + '%'); };
  const apply = () => {
    const px = TEST || parseFloat(getComputedStyle(probe).fontSize);
    if (!(px >= 10 && px <= 80)) return;
    const pct = Math.max(100, Math.min(max, Math.round(px / 17 * 100)));
    set(pct < 103 ? 100 : pct);
    fit();
  };
  // If this screen is now wider than the phone, step the text down (3% at a time) until it fits, and stay there
  const fit = () => { let n = 0; while (now > 100 && root.scrollWidth > root.clientWidth + 1 && n++ < 6) { max = Math.max(100, now - 3); set(max); } };
  let t1 = 0, t2 = 0;
  const later = () => { clearTimeout(t1); clearTimeout(t2); t1 = setTimeout(fit, 400); t2 = setTimeout(fit, 1800); };
  apply(); later();
  document.addEventListener('visibilitychange', () => { if (!document.hidden) { apply(); later(); } });
  window.addEventListener('popstate', later); window.addEventListener('hashchange', later);
  for (const fn of ['pushState', 'replaceState']) { const orig = history[fn].bind(history); history[fn] = (...a) => { const r = orig(...a); later(); return r; }; }
})();

// Is this touch inside something that scrolls sideways (the photo strip on a pre-race page, a wide table)?
function sidewaysScroller(el) {
  for (; el && el !== document.body && el.nodeType === 1; el = el.parentElement) {
    const o = getComputedStyle(el).overflowX;
    if ((o === 'auto' || o === 'scroll') && el.scrollWidth > el.clientWidth + 2) return true;
  }
  return false;
}

// ---------- Pull to refresh (the app turns off iPhone's own bounce, so it's drawn here) ----------
// Pull down at the top of a page: the page follows your finger with some resistance and a ring
// under the title fills; let go past the line to check for new results. Glides back, no bounce.
(function pullToRefresh() {
  if (!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform())) return;
  const TRIGGER = 64, MAX = 92, HOLD = 52, R = 9, C = 2 * Math.PI * R;
  const SPRING = 'transform 300ms cubic-bezier(.65, 0, .35, 1)'; // the site's "move": glides back, never overshoots
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
    ind.style.transition = animate ? 'opacity 200ms ease-out, transform 300ms cubic-bezier(.65, 0, .35, 1)' : 'none';
    ind.style.top = top() + 'px';
    ind.style.opacity = px ? Math.min(1, px / 32) : 0;
    ind.style.transform = `translate(-50%, ${Math.max(0, px - 36) / 2 + 8}px)`;
    if (!busy) arc.setAttribute('stroke-dashoffset', String(C * (1 - Math.min(1, px / TRIGGER))));
    const nowArmed = px >= TRIGGER;
    if (nowArmed !== armed) { armed = nowArmed; ind.classList.toggle('armed', armed); }
  }
  const settle = () => { draw(0, true); setTimeout(() => { const m = main(); if (m && !pull) m.style.transition = ''; }, 330); };

  // A sideways swipe (the photo strip, a wide table, next / previous race) is never a pull: the first 8px of
  // movement decide which way the finger is going, and a sideways start switches the pull off for that touch.
  let startX = 0, axis = '';
  addEventListener('touchstart', (e) => {
    startY = (blocked() || window.scrollY > 0 || e.touches.length !== 1 || sidewaysScroller(e.target)) ? null : e.touches[0].clientY;
    startX = e.touches[0] ? e.touches[0].clientX : 0; axis = '';
    pull = 0;
  }, { passive: true });
  addEventListener('touchmove', (e) => {
    if (startY == null) return;
    const dy = e.touches[0].clientY - startY;
    if (!axis) { const dx = Math.abs(e.touches[0].clientX - startX); if (dx < 8 && Math.abs(dy) < 8) return; axis = dx > Math.abs(dy) ? 'x' : 'y'; }
    if (axis === 'x') { startY = null; if (pull) { pull = 0; draw(0, false); } return; }
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
      if (!offline) {
        // Compare what matters, not the raw files: this season's results and their provisional/
        // completed status ("New results"), then anything else, such as archive fixes ("Updated")
        const season = (t) => { try { const d = JSON.parse(t); const latest = d.races.map((r) => r.season).sort().pop();
          return JSON.stringify(d.races.filter((r) => r.season === latest).map((r) => [r.match, r.officialStatus || r.provisional,
            (r.results || []).map((x) => [x.p ?? x.pos, x.n ?? x.name, x.c ?? x.club, x.t ?? x.time])])); } catch (e) { return null; } };
        const whole = (t) => { try { return JSON.stringify(JSON.parse(t)); } catch (e) { return null; } };
        changed = after.some((t, i) => before[i] != null && season(t) !== season(before[i])) ? 'results'
          : after.some((t, i) => before[i] != null && whole(t) !== whole(before[i])) ? 'archive' : false;
      }
    } catch (e) { offline = true; }
    await new Promise((r) => setTimeout(r, Math.max(0, 700 - (Date.now() - started)))); // long enough to see it working
    const msg = changed === 'results' ? 'New results' : changed ? 'Updated' : offline ? 'No signal: showing saved results' : 'Up to date';
    live.textContent = msg;
    ind.classList.remove('spin'); busy = false; pull = 0;
    settle();
    toast(msg);
    if (changed) setTimeout(() => location.reload(), 600);
  }
})();

// ---------- Soft page edges (iPhone: its own bounce is off, so a scroll used to hit the end and stop dead) ----------
// Arriving at the top or bottom of a page with some speed: the page carries on a little way (more
// for a faster scroll, 22px at most), slowing as it goes, then glides back. One movement, no bounce.
// At the bottom, pulling further makes the page follow your finger with resistance, as it does at the top.
// Reduce Motion turns both off. Android has its own edge effect, so this is iPhone only.
(function softEdges() {
  const cap = window.Capacitor;
  if (!(cap && cap.isNativePlatform && cap.isNativePlatform())) return;
  if (cap.getPlatform && cap.getPlatform() !== 'ios') return;
  const ENTER = 'cubic-bezier(.16, 1, .3, 1)', MOVE = 'cubic-bezier(.65, 0, .35, 1)';
  const GIVE_MAX = 22, OUT = 140, BACK = 300, PULL_MAX = 56;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const main = () => document.getElementById('main-content');
  const maxY = () => Math.max(0, document.documentElement.scrollHeight - innerHeight);
  const locked = () => reduce.matches || document.body.classList.contains('sl-lock');
  let lastY = scrollY, lastT = 0, lastV = 0, touched = -1e9, anim = null;

  function give(px) {
    const m = main(); if (!m || (anim && anim.playState === 'running')) return;
    const frames = [{ transform: 'translateY(0)', easing: ENTER },
      { transform: `translateY(${px}px)`, offset: OUT / (OUT + BACK), easing: MOVE }, { transform: 'translateY(0)' }];
    try { anim = m.animate(frames, { duration: OUT + BACK, composite: 'add' }); }
    catch (e) { try { anim = m.animate(frames, { duration: OUT + BACK }); } catch (e2) {} }
  }

  addEventListener('scroll', () => {
    const y = scrollY, t = performance.now(), dt = t - lastT, dy = y - lastY, max = maxY();
    // Only a real, continuous scroll counts: not a jump to the top on a new page, or a page changing height
    const v = dt > 0 && dt < 60 && Math.abs(dy) < 400 ? dy / dt : 0;
    if (v && t - touched < 5000 && !locked()) {
      const speed = Math.max(Math.abs(v), Math.sign(lastV) === Math.sign(v) ? Math.abs(lastV) : 0); // the last step is cut short by the edge
      const px = Math.min(GIVE_MAX, speed * 9);
      if (px >= 2) {
        if (y <= 0 && lastY > 0) give(px);
        else if (max > 0 && y >= max - 1 && lastY < max - 1) give(-px);
      }
    }
    lastY = y; lastT = t; lastV = v;
  }, { passive: true });

  // Pulling up at the bottom of a page
  let startY = null, pull = 0;
  const draw = (px, animate) => {
    const m = main(); if (!m) return;
    m.style.transition = animate ? `transform ${BACK}ms ${MOVE}` : 'none';
    m.style.transform = px ? `translateY(${-px}px)` : '';
    if (animate) setTimeout(() => { if (!pull && !m.style.transform) m.style.transition = ''; }, BACK + 30);
  };
  let startX = 0, axis = '';
  addEventListener('touchstart', (e) => {
    touched = performance.now();
    const max = maxY();
    startY = (locked() || max < 8 || scrollY < max - 1 || e.touches.length !== 1 || sidewaysScroller(e.target)) ? null : e.touches[0].clientY;
    startX = e.touches[0] ? e.touches[0].clientX : 0; axis = '';
    pull = 0;
  }, { passive: true });
  addEventListener('touchmove', (e) => {
    touched = performance.now();
    if (startY == null) return;
    const dy = startY - e.touches[0].clientY;
    if (!axis) { const dx = Math.abs(e.touches[0].clientX - startX); if (dx < 8 && Math.abs(dy) < 8) return; axis = dx > Math.abs(dy) ? 'x' : 'y'; }
    if (axis === 'x') { startY = null; if (pull) { pull = 0; draw(0, false); } return; }
    if (scrollY < maxY() - 1 || dy <= 0) { if (pull) { pull = 0; draw(0, false); } return; }
    pull = Math.min(PULL_MAX, dy * 0.3);
    draw(pull, false);
  }, { passive: true });
  const end = () => { touched = performance.now(); if (startY == null) return; startY = null; if (pull) { pull = 0; draw(0, true); } };
  addEventListener('touchend', end, { passive: true });
  addEventListener('touchcancel', end, { passive: true });
})();

// ---------- Tap the tab you're on to go back to the top ----------
// As in other iPhone apps: tapping Tables while you're further down Tables glides the page back to the top.
// It sets off briskly and eases in to land softly. From a long way down it first skips most of the distance
// so the glide never drags. Touching the screen stops it. Reduce Motion jumps straight there.
(function tapTabToTop() {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const ease = (t) => 1 - Math.pow(1 - t, 4); // fast start, long soft landing
  let raf = 0;
  const stop = () => { if (raf) { cancelAnimationFrame(raf); raf = 0; } };
  addEventListener('touchstart', stop, { passive: true });
  addEventListener('wheel', stop, { passive: true });
  function glide() {
    stop();
    if (reduce.matches) { scrollTo(0, 0); return; }
    let from = scrollY;
    const jump = innerHeight * 1.5; // never glide further than a screen and a half
    if (from > jump) { scrollTo(0, jump); from = jump; }
    const dur = Math.min(620, 320 + from * 0.25), t0 = performance.now();
    const step = (now) => {
      const t = Math.min(1, (now - t0) / dur);
      scrollTo(0, Math.round(from * (1 - ease(t))));
      raf = t < 1 ? requestAnimationFrame(step) : 0;
    };
    raf = requestAnimationFrame(step);
  }
  document.addEventListener('click', (e) => {
    const b = e.target.closest && e.target.closest('.app-nav button[aria-current="page"]');
    if (!b || document.body.classList.contains('sl-lock') || scrollY < 2) return;
    const before = location.href;
    // Only when the tap leaves you on the same page (from a race page, Races takes you back to the list instead)
    setTimeout(() => { if (location.href === before && !document.body.classList.contains('sl-lock')) glide(); }, 0);
  }, true);
})();

// ---------- Fonts added to the site after this build (e.g. Castoro Belgrave) ----------
// The page asks for /fonts/... files; if this build doesn't have them, fetch them from
// slarchive.org once, keep them on the phone, and hand them to the page.
(async function siteFonts() {
  const H = window.Capacitor?.Plugins?.CapacitorHttp;
  if (!window.Capacitor?.isNativePlatform?.() || !H) return;
  const site = (window.SL_CONFIG && window.SL_CONFIG.site) || 'https://slarchive.org';
  const faces = [];
  for (const sheet of document.styleSheets) {
    let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
    for (const r of rules || []) {
      if (r.type !== CSSRule.FONT_FACE_RULE) continue;
      const m = /url\(["']?(\/fonts\/[^"')]+\.woff2)["']?\)/.exec(r.style.getPropertyValue('src'));
      if (m) faces.push({ family: r.style.getPropertyValue('font-family').replace(/["']/g, '').trim(), url: m[1],
        weight: r.style.getPropertyValue('font-weight') || 'normal', style: r.style.getPropertyValue('font-style') || 'normal' });
    }
  }
  const b64 = (str) => { const bin = atob(str); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u.buffer; };
  for (const f of faces) {
    const desc = { weight: f.weight, style: f.style, display: 'swap' };
    try { await new FontFace(f.family, `url(${f.url})`, desc).load(); continue; } catch (e) { /* not in this build */ }
    const key = 'sl-font:' + f.url;
    let data = null;
    try { data = localStorage.getItem(key); } catch (e) {}
    if (!data) {
      try {
        const r = await H.get({ url: site + f.url, responseType: 'arraybuffer' });
        if (r.status === 200 && typeof r.data === 'string') { data = r.data; try { localStorage.setItem(key, data); } catch (e) {} }
      } catch (e) {}
    }
    if (!data) continue;
    try { const face = new FontFace(f.family, b64(data), desc); await face.load(); document.fonts.add(face); } catch (e) { console.warn('[SL] font', f.url, e && e.message); }
  }
})();

// ---------- Pictures added to the site after this build (race photos, portraits) ----------
// The built-in copy only has the pictures that existed when the app was built. When the page
// asks for one it doesn't have, load it from slarchive.org instead: first directly, and if that
// fails too, through the app (like the fonts above). Runs for every picture, including ones in
// the photo viewer that appear later, and re-checks any that had already failed.
(function newPictures() {
  if (!window.Capacitor?.isNativePlatform?.()) return;
  const site = (window.SL_CONFIG && window.SL_CONFIG.site) || 'https://slarchive.org';
  const H = window.Capacitor?.Plugins?.CapacitorHttp;
  const viaApp = new Map(); // path -> Promise<blob url>
  const pathOf = (img) => {
    let u; try { u = new URL(img.getAttribute('src') || '', location.href); } catch (e) { return null; }
    if (u.protocol === 'data:' || u.protocol === 'blob:') return null;
    if ((u.protocol === 'http:' || u.protocol === 'https:') && u.host !== location.host) return null; // already from elsewhere
    return u.pathname + u.search;
  };
  const fromSite = (path) => {
    if (!H) return Promise.reject(new Error('no http'));
    if (!viaApp.has(path)) viaApp.set(path, H.get({ url: site + path, responseType: 'blob' }).then((r) => {
      if (r.status !== 200 || typeof r.data !== 'string') throw new Error('status ' + r.status);
      const bin = atob(r.data); const u = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
      const type = /\.png$/i.test(path) ? 'image/png' : /\.svg$/i.test(path) ? 'image/svg+xml' : /\.webp$/i.test(path) ? 'image/webp' : 'image/jpeg';
      return URL.createObjectURL(new Blob([u], { type }));
    }).catch((e) => { viaApp.delete(path); throw e; }));
    return viaApp.get(path);
  };
  const fix = (img) => {
    const step = img.dataset.slPic || '';
    if (step === 'app' || step === 'done') return;
    if (step === 'site') { // the direct load from slarchive.org failed too
      img.dataset.slPic = 'app';
      fromSite(img.dataset.slPicPath).then((b) => { img.dataset.slPic = 'done'; img.src = b; }).catch(() => {});
      return;
    }
    const path = pathOf(img);
    const absolute = /^https?:/i.test(img.getAttribute('src') || '') && img.src.indexOf(site) === 0;
    if (!path && !absolute) return;
    if (absolute) { // already pointed at the site (e.g. by the built-in fallback): wait to see if that loads
      let u; try { u = new URL(img.src); } catch (e) { return; }
      img.dataset.slPicPath = u.pathname + u.search; img.dataset.slPic = 'site';
      if (img.complete && img.naturalWidth === 0 && img.dataset.slRetried) fix(img); // it already failed
      return;
    }
    img.dataset.slPicPath = path;
    img.dataset.slPic = 'site';
    img.src = site + path;
  };
  document.addEventListener('error', (e) => { if (e.target && e.target.tagName === 'IMG') fix(e.target); }, true);
  const sweep = () => { for (const img of document.images) if (img.complete && img.naturalWidth === 0 && img.getAttribute('src')) fix(img); };
  sweep(); setTimeout(sweep, 1500);
})();
