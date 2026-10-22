/* Static Hollow Wiki: menu drawer, search, and the main-menu scene on the home page. */
(function () {
  "use strict";
  var root = document.documentElement.getAttribute("data-root") || "";
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------------------ menu drawer (narrow screens) */
  var toggle = document.querySelector(".navtoggle");
  var sidebar = document.getElementById("sidebar");
  var scrim = document.querySelector(".scrim");
  function setNav(open) {
    if (!toggle) return;
    document.body.classList.toggle("nav-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (scrim) scrim.hidden = !open;
    if (open && sidebar) {
      var first = sidebar.querySelector("a[aria-current]") || sidebar.querySelector("a");
      if (first) first.focus({ preventScroll: false });
    }
  }
  if (toggle) {
    toggle.addEventListener("click", function () { setNav(!document.body.classList.contains("nav-open")); });
  }
  if (scrim) scrim.addEventListener("click", function () { setNav(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && document.body.classList.contains("nav-open")) { setNav(false); toggle.focus(); }
  });
  window.addEventListener("resize", function () { if (window.innerWidth > 960) setNav(false); });
  // keep the current page visible in a long sidebar
  if (sidebar) {
    var cur = sidebar.querySelector("a[aria-current]");
    if (cur && cur.offsetTop > sidebar.clientHeight - 80) sidebar.scrollTop = cur.offsetTop - 120;
  }

  /* ------------------------------------------------------------ search */
  var input = document.getElementById("q");
  var list = document.getElementById("results");
  var index = window.SH_INDEX || [];
  var active = -1, shown = [];

  function norm(s) {
    return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[‘’]/g, "'");
  }
  for (var i = 0; i < index.length; i++) {
    var e = index[i];
    e._p = norm(e.p); e._h = norm(e.h); e._t = norm(e.t);
  }
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function highlight(text, terms) {
    var out = esc(text);
    terms.forEach(function (t) {
      if (t.length < 2) return;
      var re = new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig");
      out = out.replace(re, "<mark>$1</mark>");
    });
    return out;
  }
  function snippet(e, terms) {
    var txt = e.t, low = e._t, at = -1;
    for (var k = 0; k < terms.length && at < 0; k++) at = low.indexOf(terms[k]);
    if (at < 0) return txt.slice(0, 140) + (txt.length > 140 ? "…" : "");
    var start = Math.max(0, at - 60), end = Math.min(txt.length, at + 110);
    return (start > 0 ? "…" : "") + txt.slice(start, end) + (end < txt.length ? "…" : "");
  }
  function search(q) {
    var nq = norm(q).trim();
    if (!nq) return [];
    var terms = nq.split(/\s+/).filter(Boolean);
    var NUM = { "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten" };
    var res = [];
    for (var i = 0; i < index.length; i++) {
      var e = index[i], score = 0, ok = true;
      for (var j = 0; j < terms.length; j++) {
        var best = 0, variants = NUM[terms[j]] ? [terms[j], NUM[terms[j]]] : [terms[j]];
        for (var v = 0; v < variants.length; v++) {
          var t = variants[v], s = 0;
          if (e._h.indexOf(t) >= 0) s += e._h.indexOf(t) === 0 ? 12 : 8;
          if (e._p.indexOf(t) >= 0) s += e.h ? (e._p.indexOf(t) === 0 ? 5 : 3) : (e._p.indexOf(t) === 0 ? 14 : 10);
          var c = 0, from = 0, pos;
          while (c < 4 && (pos = e._t.indexOf(t, from)) >= 0) { c++; from = pos + t.length; }
          s += c;
          if (s > best) best = s;
        }
        if (!best) { ok = false; break; }
        score += best;
      }
      if (!ok) continue;
      if (terms.length > 1) {
        if (e._h.indexOf(nq) >= 0) score += 14;
        else if (!e.h && e._p.indexOf(nq) >= 0) score += 18; // the whole phrase in a page's own title
        else if (e._t.indexOf(nq) >= 0) score += 5;
      }
      if (!e.h) score += 1; // page tops slightly ahead of their own sections on a tie
      res.push({ e: e, s: score });
    }
    res.sort(function (a, b) { return b.s - a.s; });
    // one or two hits per page so a single long page can't fill the list
    var perPage = {}, out = [];
    for (var r = 0; r < res.length && out.length < 9; r++) {
      var p = res[r].e.p;
      perPage[p] = (perPage[p] || 0) + 1;
      if (perPage[p] <= 2) out.push(res[r].e);
    }
    return { hits: out, terms: terms };
  }
  function render(q) {
    var r = search(q);
    active = -1;
    if (!q.trim()) { close(); return; }
    shown = r.hits || [];
    if (!shown.length) {
      list.innerHTML = '<li class="r-empty" role="option" aria-disabled="true">Nothing on this channel for “' + esc(q) + '”. Try a creature, a place or an item.</li>';
    } else {
      list.innerHTML = shown.map(function (e, n) {
        var where = e.h ? esc(e.p) + " › " + esc(e.h) : esc(e.p);
        var title = e.h ? highlight(e.h, r.terms) : highlight(e.p, r.terms);
        return '<li role="option" id="opt-' + n + '"><a href="' + root + e.u + '" tabindex="-1">' +
          '<span class="r-title">' + title + '</span>' +
          (e.h ? '<span class="r-where">' + where + '</span>' : '') +
          '<span class="r-snip">' + highlight(snippet(e, r.terms), r.terms) + '</span></a></li>';
      }).join("");
    }
    list.hidden = false;
    input.setAttribute("aria-expanded", "true");
  }
  function close() {
    list.hidden = true; list.innerHTML = ""; shown = []; active = -1;
    input.setAttribute("aria-expanded", "false");
    input.removeAttribute("aria-activedescendant");
  }
  function move(d) {
    if (!shown.length) return;
    active = (active + d + shown.length) % shown.length;
    var items = list.querySelectorAll("li[role=option]");
    items.forEach(function (li, n) { li.classList.toggle("is-active", n === active); li.setAttribute("aria-selected", n === active ? "true" : "false"); });
    input.setAttribute("aria-activedescendant", "opt-" + active);
    var el = items[active]; if (el && el.scrollIntoView) el.scrollIntoView({ block: "nearest" });
  }
  if (input && list) {
    var timer;
    input.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(function () { render(input.value); }, 70); });
    input.addEventListener("focus", function () { if (input.value.trim()) render(input.value); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
      else if (e.key === "Enter") {
        var pick = shown[active >= 0 ? active : 0];
        if (pick) { e.preventDefault(); window.location.href = root + pick.u; }
      } else if (e.key === "Escape") { if (input.value) { input.value = ""; } close(); }
    });
    document.addEventListener("click", function (e) { if (!e.target.closest || !e.target.closest(".search")) close(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== input && !/INPUT|TEXTAREA|SELECT/.test((document.activeElement || {}).tagName || "")) {
        e.preventDefault(); input.focus(); input.select();
      }
    });
  }

  /* ------------------------------------------------------------ home: the main menu, rebuilt from the mod's own layers */
  var stage = document.querySelector(".stage");
  if (stage) {
    var watcher = stage.querySelector(".l-watcher");
    var splash = stage.querySelector(".splash");
    var clock = stage.querySelector(".osd--time");
    var lines = [];
    try { lines = JSON.parse(stage.getAttribute("data-splashes") || "[]"); } catch (err) { lines = []; }
    if (splash && lines.length) splash.textContent = lines[Math.floor(Math.random() * lines.length)];

    var t0 = Date.now();
    function tick() {
      var s = Math.floor((Date.now() - t0) / 1000);
      var h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, ss = s % 60;
      if (clock) clock.textContent = h + ":" + (m < 10 ? "0" : "") + m + ":" + (ss < 10 ? "0" : "") + ss;
    }
    tick();
    if (!reduceMotion) setInterval(tick, 1000);

    // Each flash, the Watcher is somewhere else: the hill, the graves, the edge of the trees, gone.
    // Every third flash shows something huge standing behind the cathedral.
    var pos = 1, flashes = 0;
    function place(p) {
      if (!watcher) return;
      watcher.className = "l-watcher pos-" + p;
    }
    place(pos);
    function flash() {
      flashes++;
      var saint = flashes % 3 === 0;
      stage.classList.toggle("show-saint", saint);
      stage.classList.add("is-flash");
      setTimeout(function () {
        pos = (pos + 1) % 4; place(pos);
        stage.classList.remove("is-flash");
      }, 110);
      setTimeout(function () { stage.classList.add("is-flash"); }, 230);
      setTimeout(function () { stage.classList.remove("is-flash"); }, 330);
      schedule();
    }
    function schedule() { setTimeout(flash, 6500 + Math.random() * 5000); }
    if (!reduceMotion) setTimeout(flash, 2600);
  }
})();
