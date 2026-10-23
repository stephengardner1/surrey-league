// Surrey League results panel for club websites (first user: belgraveharriers.com news articles).
// This whole file goes inline into each Squarespace Code Block, after the panel's stored copy.
// It is also run by build.mjs to write that stored copy, so the two always match.
//
// Safety: nothing is ever loaded as code from slarchive.org. The script only asks it for plain JSON,
// checks every value, and writes text with textContent (never innerHTML), so if slarchive.org were
// ever lost or taken over it could not run anything on the club's site. If it doesn't answer,
// the stored copy simply stays, and the "full results" link hides itself.
(function (root) {
  var BASE = 'https://slarchive.org';
  var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  function S(v, max) { return typeof v === 'string' ? v.slice(0, max || 120) : ''; }
  function N(v) { return typeof v === 'number' && isFinite(v) ? v : null; }
  function list(a, max) { return Array.isArray(a) ? a.slice(0, max) : []; }
  function ord(n) { var s = ['th', 'st', 'nd', 'rd'], v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); }
  function fmtDate(iso) { var m = /^(\d{4})-(\d\d)-(\d\d)$/.exec(iso || ''); return m ? (+m[3]) + ' ' + MONTHS[+m[2] - 1] + ' ' + m[1] : ''; }
  function fmtNum(v) { return Number.isInteger(v) ? String(v) : String(v).replace(/\.5$/, '½'); }

  // accept only the shape we expect, with sane lengths; anything else -> null (keep the stored copy)
  function clean(d, want) {
    if (!d || typeof d !== 'object' || d.v !== 1) return null;
    if (d.code !== want.code || d.club !== want.club || !!d.women !== want.women) return null;
    function teams(a, key) {
      return list(a, 40).map(function (t) { return { pos: N(t && t.pos), club: S(t && t.club, 6), name: S(t && t.name, 60), v: N(t && t[key]) }; })
        .filter(function (t) { return t.pos != null && t.v != null && t.name; });
    }
    var out = {
      code: want.code, club: want.club, women: want.women,
      season: S(d.season, 9), match: N(d.match), venue: S(d.venue, 60), date: S(d.date, 10),
      finishers: N(d.finishers), clubName: S(d.clubName, 60) || want.club,
      runners: list(d.runners, 400).map(function (r) {
        r = r || {};
        return { pos: N(r.pos), name: S(r.name, 80), time: S(r.time, 10), team: r.team === 'A' || r.team === 'B' ? r.team : null,
          pts: N(r.pts), ns: r.ns === true, sc: r.sc === true };
      }).filter(function (r) { return r.name; }),
      teamsA: teams(d.teamsA, 'score'), teamsB: teams(d.teamsB, 'score'),
      tableA: teams(d.tableA, 'total'), tableB: teams(d.tableB, 'total')
    };
    return out.runners.length && out.match ? out : null;
  }

  function render(doc, d) {
    function el(tag, cls, text) { var e = doc.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = String(text); return e; }
    function add(p, c) { p.appendChild(c); return c; }
    var wrap = el('div', 'bh-sl__in');
    var who = d.clubName.replace(/ Harriers$/, '');  // "Belgrave"

    add(wrap, el('div', 'bh-sl__eyebrow', 'Surrey League ' + (d.women ? "women's " : '') + 'Division 1 · match ' + d.match + ' of ' + d.season));
    add(wrap, el('div', 'bh-sl__title', [d.venue, fmtDate(d.date)].filter(Boolean).join(', ')));

    // one-line summary: team placings and turnout
    var mine = function (rows) { for (var i = 0; i < rows.length; i++) if (rows[i].club === d.club) return rows[i]; return null; };
    var a = mine(d.teamsA), b = mine(d.teamsB), bits = [];
    if (a) bits.push('A team ' + ord(a.pos) + ' (' + fmtNum(a.v) + ' pts)');
    if (b) bits.push('B team ' + ord(b.pos) + ' (' + fmtNum(b.v) + ' pts)');
    bits.push(d.runners.length + ' ' + who + ' finishers' + (d.finishers ? ' of ' + d.finishers : ''));
    add(wrap, el('div', 'bh-sl__sum', bits.join(' · ')));

    // the club's finishers: everyone up to the last scorer shown, the rest behind "show more"
    function runnerTable(rows, head) {
      var t = el('table', 'bh-sl__runners'), cg = add(t, el('colgroup'));
      ['pos', 'name', 'time', 'team'].forEach(function (c) { add(cg, el('col', 'bh-sl__c-' + c)); });
      if (head) {
        var hr = add(add(t, el('thead')), el('tr'));
        ['Pos', 'Name', 'Time', 'Scored'].forEach(function (h, i) { add(hr, el('th', i === 1 ? '' : 'bh-sl__num', h)); });
      }
      var tb = add(t, el('tbody'));
      rows.forEach(function (r) {
        var tr = add(tb, el('tr', r.team ? 'bh-sl__scorer' : ''));
        add(tr, el('td', 'bh-sl__num', r.pos != null ? r.pos : ''));
        var nm = add(tr, el('td', 'bh-sl__name', r.name));
        if (r.sc) { var sc = add(nm, el('abbr', 'bh-sl__2c', '2C')); sc.title = 'Second claim'; }
        add(tr, el('td', 'bh-sl__num', r.time));
        var tc = add(tr, el('td', 'bh-sl__num'));
        if (r.team) {
          var pill = add(tc, el('span', 'bh-sl__pill bh-sl__pill--' + r.team.toLowerCase(), r.team));
          pill.title = r.team + ' team scorer';
          add(tc, el('span', 'bh-sl__pts', r.pts != null ? fmtNum(r.pts) : ''));
        } else if (r.ns) {
          var ns = add(tc, el('span', 'bh-sl__pill bh-sl__pill--ns', 'NS')); ns.title = 'Non-scoring';
        }
      });
      return t;
    }
    var last = -1;
    d.runners.forEach(function (r, i) { if (r.team) last = i; });
    var shown = last < 0 ? d.runners.slice(0, 10) : d.runners.slice(0, last + 1), rest = d.runners.slice(shown.length);
    add(wrap, el('div', 'bh-sl__h', who + ' finishers'));
    add(wrap, runnerTable(shown, true));
    if (rest.length) {
      var det = add(wrap, el('details', 'bh-sl__more'));
      add(det, el('summary', '', 'Show ' + rest.length + ' more ' + who + ' finisher' + (rest.length > 1 ? 's' : '')));
      add(det, runnerTable(rest, false));
    }
    var keys = [], hasSc = d.runners.some(function (r) { return r.sc; }), hasNs = d.runners.some(function (r) { return r.ns; });
    keys.push('A/B: scored for the A or B team, with the points it counted');
    if (hasSc) keys.push('2C: second claim');
    if (hasNs) keys.push("NS: didn't score (e.g. over the second-claim limit)");
    add(wrap, el('div', 'bh-sl__key', keys.join(' · ')));

    // team scores on the day and the league tables after this match
    var grid = el('div', 'bh-sl__grid');
    function mini(title, rows, unit) {
      if (!rows.length) return;
      var box = add(grid, el('div', 'bh-sl__box'));
      add(box, el('div', 'bh-sl__h', title));
      var t = add(box, el('table', 'bh-sl__teams')), tb = add(t, el('tbody'));
      rows.forEach(function (r) {
        var tr = add(tb, el('tr', r.club === d.club ? 'bh-sl__us' : ''));
        add(tr, el('td', 'bh-sl__num', r.pos));
        add(tr, el('td', '', r.name));
        add(tr, el('td', 'bh-sl__num', fmtNum(r.v)));
      });
      if (unit) add(box, el('div', 'bh-sl__key', unit));
    }
    // A beside B; after match 1 the league table is the same as the day's scores, so it's left out
    mini('Match ' + d.match + ' · A teams', d.teamsA);
    mini('Match ' + d.match + ' · B teams', d.teamsB);
    if (d.match > 1) {
      mini('League after ' + d.match + ' matches · A', d.tableA);
      mini('League after ' + d.match + ' matches · B', d.tableB);
    }
    if (grid.childNodes.length) add(wrap, grid);

    var foot = add(wrap, el('div', 'bh-sl__foot'));
    var link = add(foot, el('a', 'bh-sl__link', 'Full results on slarchive.org →'));
    link.setAttribute('href', BASE + (d.women ? '/women' : '') + '/race/' + d.code);
    link.setAttribute('rel', 'noopener');
    return wrap;
  }

  // live refresh: replace the stored copy with the latest data, if slarchive.org answers properly
  function refresh(doc) {
    var nodes = doc.querySelectorAll('.bh-sl[data-race]:not([data-sl-live])');
    Array.prototype.forEach.call(nodes, function (n) {
      n.setAttribute('data-sl-live', '1');
      var want = { code: n.getAttribute('data-race') || '', club: n.getAttribute('data-club') || '', women: n.getAttribute('data-women') === '1' };
      var hide = function () { Array.prototype.forEach.call(n.querySelectorAll('.bh-sl__link'), function (a) { a.hidden = true; }); n.setAttribute('data-sl-state', 'stored'); };
      if (!/^\d{4}-\d{1,2}$/.test(want.code) || !/^[A-Z0-9&\/]{2,5}$/.test(want.club) || !root.fetch) return hide();
      var ctl = root.AbortController ? new AbortController() : null;
      if (ctl) setTimeout(function () { ctl.abort(); }, 8000);
      root.fetch(BASE + '/embed/' + (want.women ? 'women/' : '') + 'race/' + want.code + '.json?club=' + encodeURIComponent(want.club),
        { credentials: 'omit', mode: 'cors', referrerPolicy: 'no-referrer', signal: ctl ? ctl.signal : undefined })
        .then(function (r) {
          if (!r.ok || !/^application\/json/.test(r.headers.get('content-type') || '')) throw 0;
          return r.text();
        })
        .then(function (t) {
          if (t.length > 300000) throw 0;
          var d = clean(JSON.parse(t), want);
          if (!d) throw 0;
          var fresh = render(doc, d);
          while (n.firstChild) n.removeChild(n.firstChild);
          n.appendChild(fresh);
          n.setAttribute('data-sl-state', 'live');
        })
        .catch(hide);
    });
  }

  root.bhSlPanel = { clean: clean, render: render };
  if (root.document && !root.bhSlNoAuto) {
    if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', function () { refresh(root.document); });
    else refresh(root.document);
  }
})(typeof window !== 'undefined' ? window : globalThis);
