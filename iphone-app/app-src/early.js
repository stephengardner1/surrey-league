/* Surrey League Compendium app: keeps the app up to date without new builds.
   Loaded first in <head>, before the site's own code.

   1. Results: the site's data files come live from slarchive.org when there's
      signal (and are saved on the phone); with no signal, the last saved copy is
      used; failing that, the copy built into the app.
   2. The site itself (design, pages, the app's Notifications screen): each launch
      the app downloads the latest version from slarchive.org in the background and
      saves it. From the next launch (or when you come back to the app after a
      while) that saved version is shown instead of the one built in.
      Safety net: if a saved version doesn't start properly, the app goes back to
      the built-in version and ignores that one.
   3. Pictures and files added to the site after this build come from slarchive.org. */
(function () {
  if (window.__slEarly) return; // runs once, even after switching to the saved version
  window.__slEarly = true;

  var SITE = (window.SL_CONFIG && window.SL_CONFIG.site) || 'https://slarchive.org';
  var LIVE = /^(data\.json|data-women\.json|field-depth\.json|field-scores\.json|goat-ranks\.json|portraits\/race-tops\.json|portraits\/portraits\.json)$/;
  var TIMEOUT = 5000;
  var origFetch = window.fetch.bind(window);
  var cap = function () { return window.Capacitor; };
  var native = function () { var C = cap(); return !!(C && C.isNativePlatform && C.isNativePlatform()); };
  var http = function () { var C = cap(); return C && C.Plugins && C.Plugins.CapacitorHttp; };
  var LS = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); return true; } catch (e) { return false; } },
    del: function (k) { try { localStorage.removeItem(k); } catch (e) {} },
  };
  function fnv(str) { var x = 0x811c9dc5; for (var k = 0; k < str.length; k++) { x ^= str.charCodeAt(k); x = Math.imul(x, 16777619) >>> 0; } return x.toString(16); }

  // ---------- 2a. Switch to the saved newer version, if there is one ----------
  var BUILT = window.SL_BUILT_HASH || '';
  var live = null;
  function boot() {
    if (!native() || window.SL_NO_LIVE) return;
    var hash = LS.get('sl-live-hash'), html = LS.get('sl-live-html');
    if (!hash || !html || hash === BUILT) return;
    if (LS.get('sl-live-bad') === hash) return;
    if (LS.get('sl-live-boot') === hash + ':starting') { // last try didn't start properly
      LS.set('sl-live-bad', hash); LS.del('sl-live-boot'); return;
    }
    if (LS.get('sl-live-neednet') === '1' && navigator.onLine === false) return;
    var compose = LS.get('sl-live-compose');
    var composeUrl = compose ? URL.createObjectURL(new Blob([compose], { type: 'text/javascript' })) : '/app/compose.mjs';
    LS.set('sl-live-boot', hash + ':starting');
    live = hash;
    window.SL_LIVE_VERSION = hash;
    // Write the saved version in place of the built-in page; <plaintext> swallows the rest of the built-in page unread
    // Started properly once the site has drawn its navigation
    var tries = 0, ok = setInterval(function () {
      if (document.querySelector('header nav')) { clearInterval(ok); LS.set('sl-live-boot', live + ':ok'); }
      else if (++tries > 30) { clearInterval(ok); LS.set('sl-live-bad', live); LS.del('sl-live-boot'); location.reload(); } // 15s: go back to built-in
    }, 500);
    document.write(html.split('__SL_COMPOSE__').join(composeUrl) + '<plaintext hidden style="display:none">');
  }

  // ---------- a tiny saved-copy store for results (IndexedDB) ----------
  var dbp = null;
  function db() {
    if (dbp) return dbp;
    dbp = new Promise(function (res, rej) {
      try {
        var r = indexedDB.open('sl-cache', 1);
        r.onupgradeneeded = function () { r.result.createObjectStore('files'); };
        r.onsuccess = function () { res(r.result); };
        r.onerror = function () { rej(r.error); };
      } catch (e) { rej(e); }
    });
    return dbp;
  }
  function getSaved(k) {
    return db().then(function (d) {
      return new Promise(function (res) {
        var q = d.transaction('files').objectStore('files').get(k);
        q.onsuccess = function () { res(q.result || null); };
        q.onerror = function () { res(null); };
      });
    }).catch(function () { return null; });
  }
  function save(k, text) {
    return db().then(function (d) {
      d.transaction('files', 'readwrite').objectStore('files').put({ text: text, at: Date.now() }, k);
    }).catch(function () {});
  }

  // ---------- fetching from slarchive.org through the app (no browser restrictions) ----------
  function get(path, ms) {
    var H = http();
    if (!H) return Promise.reject(new Error('not in the app'));
    var req = H.get({ url: SITE + '/' + path + (path.indexOf('?') < 0 ? '?' : '&') + 'app=' + Date.now(), responseType: 'text', headers: { 'Cache-Control': 'no-cache' } })
      .then(function (r) {
        if (r.status !== 200) throw new Error('status ' + r.status);
        return typeof r.data === 'string' ? r.data : JSON.stringify(r.data);
      });
    if (!ms) return req;
    return Promise.race([req, new Promise(function (_, rej) { setTimeout(function () { rej(new Error('timeout')); }, ms); })]);
  }
  function remote(path) {
    var req = get(path);
    req.then(function (text) { save(path, text); }).catch(function () {}); // saved even if the timeout wins
    return Promise.race([req, new Promise(function (_, rej) { setTimeout(function () { rej(new Error('timeout')); }, TIMEOUT); })]);
  }
  function typeOf(path) {
    return /\.svg$/.test(path) ? 'image/svg+xml' : /\.json$/.test(path) ? 'application/json' : /\.css$/.test(path) ? 'text/css' : /\.m?js$/.test(path) ? 'text/javascript' : 'text/plain';
  }

  // ---------- 1 and 3. The site's own requests ----------
  window.fetch = function (input, init) {
    var url = typeof input === 'string' ? input : (input && input.url) || '';
    var u;
    try { u = new URL(url, location.href); } catch (e) { return origFetch(input, init); }
    if (u.origin !== location.origin || (init && init.method && init.method.toUpperCase() !== 'GET')) return origFetch(input, init);
    var path = u.pathname.replace(/^\/+/, '');
    if (LIVE.test(path)) {
      return remote(path)
        .then(function (text) { window.SL_DATA_SOURCE = 'live'; return new Response(text, { status: 200, headers: { 'Content-Type': 'application/json' } }); })
        .catch(function () {
          return getSaved(path).then(function (c) {
            if (c) { window.SL_DATA_SOURCE = 'saved'; window.SL_DATA_SAVED_AT = c.at; return new Response(c.text, { status: 200, headers: { 'Content-Type': 'application/json' } }); }
            window.SL_DATA_SOURCE = 'built-in';
            return origFetch(input, init);
          });
        });
    }
    // Anything added to the site after this build (new portraits, new data files): fetch it from the site
    return origFetch(input, init).then(function (r) {
      if (r.ok || !http()) return r;
      return get(path + u.search, TIMEOUT).then(function (text) {
        return new Response(text, { status: 200, headers: { 'Content-Type': typeOf(path) } });
      }).catch(function () { return r; });
    }, function (e) {
      if (!http()) throw e;
      return get(path + u.search, TIMEOUT).then(function (text) { return new Response(text, { status: 200, headers: { 'Content-Type': typeOf(path) } }); });
    });
  };

  // Pictures added after this build (portraits, race photos): load them from the site instead
  document.addEventListener('error', function (e) {
    var el = e.target;
    if (!el || el.tagName !== 'IMG' || el.dataset.slRetried) return;
    var u; try { u = new URL(el.getAttribute('src') || '', location.href); } catch (x) { return; }
    if (u.origin !== location.origin) return;
    el.dataset.slRetried = '1';
    el.src = SITE + u.pathname + u.search;
  }, true);

  // ---------- 2b. Download the latest version of the site, ready for next time ----------
  // Turn the site's page into the app's page: saved copies of outside scripts and fonts, room
  // for the iPhone's notch, and the app's own additions (latest versions when available).
  function makeAppPage(raw, map, css, js, hasCompose) {
    var html = raw, needNet = false;
    (map || []).forEach(function (p) { html = html.split(p[0]).join(p[1]); });
    if (/<script[^>]+src="https:\/\//i.test(html) || /<link[^>]+href="https:\/\/fonts/i.test(html)) needNet = true;
    html = html.replace(/<link rel="preconnect"[^>]*>\s*/g, '');
    html = html.replace(/(<meta name="viewport" content=")([^"]*)"/i, function (m, a, b) { return a + (b.indexOf('viewport-fit') >= 0 ? b : b + ', viewport-fit=cover') + '"'; });
    html = html.replace(/<head>/i, '<head>\n<script src="/app/config.js"></script>\n<script src="/app/early.js"></script>');
    var i = html.indexOf('const getClubVestSvg='), j = i < 0 ? -1 : html.indexOf('\n};', i);
    var vests = j > 0 ? '<script>(() => {\n' + html.slice(i, j + 3) + '\nwindow.slVest = getClubVestSvg;\n})();</script>' : '<script src="/app/vests.js"></script>';
    var style = css ? '<style>' + css + '</style>' : '<link rel="stylesheet" href="/app/app.css">';
    var script = js ? '<script type="module">' + js.replace(/from\s+['"]\.\/compose\.mjs['"]/, "from '" + (hasCompose ? '__SL_COMPOSE__' : '/app/compose.mjs') + "'") + '</script>'
      : '<script type="module" src="/app/app.js"></script>';
    // Use $ functions so nothing in the site's code is read as a replacement pattern
    html = html.replace(/<\/body>/i, function () { return style + '\n' + vests + '\n' + script + '\n</body>'; });
    return { html: html, needNet: needNet };
  }
  var checking = false;
  function checkForUpdate() {
    if (checking || !native() || !http()) return;
    checking = true;
    var opt = function (p) { return get(p, 20000).catch(function () { return null; }); };
    Promise.all([get('', 20000), opt('app/app.css'), opt('app/app.js'), opt('app/compose.mjs')]).then(function (f) {
      var raw = f[0], css = f[1], js = f[2], compose = f[3];
      if (raw.indexOf('</body>') < 0 || raw.indexOf('<script') < 0) throw new Error('not the site');
      // A real app.css / app.js / compose.mjs, not the site's page served in their place
      if (css && (/<html/i.test(css) || !/\.sl-/.test(css))) css = null;
      if (js && (/<html/i.test(js) || !/renderPanel|SL_CONFIG/.test(js))) js = null;
      if (compose && (/<html/i.test(compose) || !/export /.test(compose))) compose = null;
      if (!css || !js || !compose) throw new Error('app files unavailable'); // try again next time
      // Fingerprint of the site page AND the app's own files: either changing means a new version
      var hash = fnv(raw + '\n' + css + '\n' + js + '\n' + compose);
      if (hash === BUILT) { ['sl-live-hash', 'sl-live-html', 'sl-live-compose', 'sl-live-neednet'].forEach(LS.del); return; }
      if (hash === LS.get('sl-live-hash') || hash === LS.get('sl-live-bad')) return;
      return origFetch('/app/vendor-map.json').then(function (r) { return r.json(); }).catch(function () { return []; }).then(function (map) {
        var page = makeAppPage(raw, map, css, js, true);
        LS.del('sl-live-html');
        if (!LS.set('sl-live-html', page.html)) return;
        LS.set('sl-live-compose', compose);
        LS.set('sl-live-neednet', page.needNet ? '1' : '0');
        LS.set('sl-live-hash', hash);
        LS.set('sl-live-at', String(Date.now()));
        window.SL_UPDATE_READY = hash;
      });
    }).catch(function (e) { console.warn('[SL] update check', e && e.message); })
      .then(function () { checking = false; });
  }
  window.addEventListener('load', function () { setTimeout(checkForUpdate, 4000); });

  // Coming back to the app after a while: check again, and show a newer version if one is waiting
  var hiddenAt = 0;
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) { hiddenAt = Date.now(); return; }
    if (!hiddenAt) return;
    var away = Date.now() - hiddenAt;
    if (away > 10 * 60 * 1000 && LS.get('sl-live-hash') && LS.get('sl-live-hash') !== (live || BUILT) && LS.get('sl-live-hash') !== LS.get('sl-live-bad')) {
      location.reload();
    } else if (away > 60 * 1000) checkForUpdate();
  });

  boot(); // last, so the safety nets above are in place for the saved version too
})();
