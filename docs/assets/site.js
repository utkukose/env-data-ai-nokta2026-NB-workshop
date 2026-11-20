/* Shared behavior of the NOKTA workshop site: theme, language, route, keys,
   predict-then-reveal polls, live numbers from the data and the session log. */
(function () {
  "use strict";
  var html = document.documentElement;
  var LANG = (html.lang || "en").slice(0, 2);

  /* ---------------- storage that never throws ---------------- */
  var Store = {
    get: function (k, d) {
      try { var v = window.localStorage.getItem("nokta." + k); return v === null ? d : JSON.parse(v); }
      catch (e) { return d; }
    },
    set: function (k, v) {
      try { window.localStorage.setItem("nokta." + k, JSON.stringify(v)); } catch (e) { /* private mode */ }
    },
    log: function (key, value) {
      var all = Store.get("log", {});
      all[key] = { v: value, t: Date.now() };
      Store.set("log", all);
    }
  };

  /* ---------------- labels in both languages ---------------- */
  var L = {
    en: {
      ch: {
        temperature_c: ["Temperature", "°C"], rel_humidity_pct: ["Relative humidity", "%"],
        pressure_hpa: ["Air pressure", "hPa"], pm1_ugm3: ["PM1", "µg/m³"],
        pm25_ugm3: ["PM2.5", "µg/m³"], pm10_ugm3: ["PM10", "µg/m³"],
        co2_ppm: ["CO₂", "ppm"], light_lux: ["Light", "lx"], uva_wm2: ["UVA", "W/m²"],
        uvb_wm2: ["UVB", "W/m²"]
      },
      type: {
        shaded: "Shaded, between buildings", traffic: "Near traffic", reference: "Quiet reference",
        sunny_hard: "Sunny hard surface", crowded: "Busy student area", green: "Green area"
      },
      short: { shaded: "Shaded", traffic: "Traffic", reference: "Reference", sunny_hard: "Sunny", crowded: "Busy", green: "Green" },
      campus: { A: "Campus A", B: "Campus B", C: "Campus C" },
      right: "Right.", wrong: "Not quite.", answered: "Your answer:", locked: "Answer the question above to reveal",
      copied: "Copied", round: "Round", mean2: "Two-round mean"
    },
    tr: {
      ch: {
        temperature_c: ["Sıcaklık", "°C"], rel_humidity_pct: ["Bağıl nem", "%"],
        pressure_hpa: ["Atmosfer basıncı", "hPa"], pm1_ugm3: ["PM1", "µg/m³"],
        pm25_ugm3: ["PM2,5", "µg/m³"], pm10_ugm3: ["PM10", "µg/m³"],
        co2_ppm: ["CO₂", "ppm"], light_lux: ["Işık şiddeti", "lx"], uva_wm2: ["UVA", "W/m²"],
        uvb_wm2: ["UVB", "W/m²"]
      },
      type: {
        shaded: "Gölgeli, bina arası", traffic: "Trafiğe yakın", reference: "Sakin referans",
        sunny_hard: "Güneşe açık sert zemin", crowded: "Öğrenci yoğun alan", green: "Yeşil alan"
      },
      short: { shaded: "Gölgeli", traffic: "Trafik", reference: "Referans", sunny_hard: "Güneşli", crowded: "Yoğun", green: "Yeşil" },
      campus: { A: "Kampüs A", B: "Kampüs B", C: "Kampüs C" },
      right: "Doğru.", wrong: "Tam olarak değil.", answered: "Cevabınız:", locked: "Görmek için yukarıdaki soruyu cevaplayın",
      copied: "Kopyalandı", round: "Tur", mean2: "İki turun ortalaması"
    }
  }[LANG] || null;

  var TYPES = ["shaded", "traffic", "reference", "sunny_hard", "crowded", "green"];
  function cssVar(name) { return getComputedStyle(html).getPropertyValue(name).trim(); }
  function typeColor(t) { return cssVar("--t" + (TYPES.indexOf(t) + 1)) || "#888"; }
  function accent() { return getComputedStyle(document.body).getPropertyValue("--accent").trim(); }

  function fmt(x, nd) {
    if (x === null || x === undefined || !isFinite(x)) return "–";
    nd = nd === undefined ? 1 : nd;
    try {
      return new Intl.NumberFormat(LANG === "tr" ? "tr-TR" : "en-US",
        { minimumFractionDigits: nd, maximumFractionDigits: nd }).format(x);
    } catch (e) { return Number(x).toFixed(nd); }
  }
  function signed(x, nd) { return (x > 0 ? "+" : x < 0 ? "−" : "") + fmt(Math.abs(x), nd); }
  function path(obj, p) {
    return p.split(".").reduce(function (o, k) { return o == null ? undefined : o[k]; }, obj);
  }

  /* ---------------- theme ---------------- */
  function applyTheme(t) {
    html.setAttribute("data-theme", t);
    Store.set("theme", t);
    document.dispatchEvent(new CustomEvent("nokta:theme", { detail: t }));
  }
  var saved = Store.get("theme", null);
  if (saved) html.setAttribute("data-theme", saved);
  else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) html.setAttribute("data-theme", "dark");
  else html.setAttribute("data-theme", "light");
  function toggleTheme() { applyTheme(html.getAttribute("data-theme") === "dark" ? "light" : "dark"); }

  /* ---------------- tooltip ---------------- */
  var tipEl = null;
  var Tip = {
    show: function (content, x, y) {
      if (!tipEl) { tipEl = document.createElement("div"); tipEl.className = "tooltip"; document.body.appendChild(tipEl); }
      tipEl.innerHTML = content;
      var w = tipEl.offsetWidth, h = tipEl.offsetHeight;
      var left = Math.min(window.innerWidth - w - 8, x + 14), top = y - h - 12;
      if (top < 8) top = y + 16;
      tipEl.style.left = Math.max(8, left) + "px"; tipEl.style.top = top + "px";
      tipEl.classList.add("on");
    },
    hide: function () { if (tipEl) tipEl.classList.remove("on"); }
  };

  /* ---------------- polls: predict, then reveal ---------------- */
  function initPolls() {
    document.querySelectorAll(".poll").forEach(function (poll) {
      var id = poll.getAttribute("data-id");
      var answer = poll.getAttribute("data-answer");
      var verdict = poll.querySelector(".verdict");
      var buttons = poll.querySelectorAll(".opts button");
      function settle(v, silent) {
        buttons.forEach(function (b) {
          b.classList.toggle("picked", b.getAttribute("data-v") === v);
          if (answer && b.getAttribute("data-v") === answer) b.classList.add("right");
        });
        if (verdict) {
          var ok = !answer || v === answer;
          var msgR = poll.querySelector(".msg-right"), msgW = poll.querySelector(".msg-wrong");
          verdict.innerHTML = "<b>" + (answer ? (ok ? L.right : L.wrong) : L.answered) + "</b> " +
            (ok && msgR ? msgR.innerHTML : (!ok && msgW ? msgW.innerHTML : (msgR ? msgR.innerHTML : "")));
        }
        document.querySelectorAll('.reveal-lock[data-for="' + id + '"]').forEach(function (el) {
          el.classList.remove("locked");
        });
        if (!silent) {
          Store.log("poll:" + id, { v: v, ok: answer ? v === answer : null });
          document.dispatchEvent(new CustomEvent("nokta:poll", { detail: { id: id, v: v } }));
        }
      }
      buttons.forEach(function (b) {
        b.addEventListener("click", function () { settle(b.getAttribute("data-v"), false); });
      });
      var prev = Store.get("log", {})["poll:" + id];
      if (prev && prev.v && prev.v.v) settle(prev.v.v, true);
    });
    document.querySelectorAll(".reveal-lock").forEach(function (el) {
      if (!el.getAttribute("data-msg")) el.setAttribute("data-msg", L.locked);
    });
  }

  /* ---------------- numbers bound to the data ---------------- */
  function bindNumbers() {
    if (!window.NOKTA) return;
    document.querySelectorAll("[data-num]").forEach(function (el) {
      var v = path(window.NOKTA, el.getAttribute("data-num"));
      var nd = +(el.getAttribute("data-nd") || 1);
      var sc = +(el.getAttribute("data-scale") || 1);
      if (typeof v === "number") el.textContent = el.hasAttribute("data-signed") ? signed(v * sc, nd) : fmt(v * sc, nd);
    });
  }

  /* ---------------- route and keys ---------------- */
  var PAGES = ["index", "part1", "part2", "part3", "part4", "part5", "lab"];
  var here = (location.pathname.split("/").pop() || "index.html").replace(".html", "") || "index";
  var visited = Store.get("visited", []);
  if (visited.indexOf(here) < 0) { visited.push(here); Store.set("visited", visited); }
  function initRoute() {
    document.querySelectorAll(".route li").forEach(function (li) {
      var p = li.getAttribute("data-page");
      if (p === here) li.classList.add("current");
      else if (visited.indexOf(p) >= 0) li.classList.add("visited");
    });
  }
  function stations() { return Array.prototype.slice.call(document.querySelectorAll(".station")); }
  function currentStation() {
    var s = stations(), y = window.scrollY + 90, idx = -1;
    s.forEach(function (el, i) { if (el.offsetTop <= y) idx = i; });
    return idx;
  }
  function go(delta) {
    var s = stations(); if (!s.length) return;
    var i = Math.max(0, Math.min(s.length - 1, currentStation() + delta));
    s[i].scrollIntoView({ behavior: "smooth", block: "start" });
  }
  function goPage(delta) {
    var i = PAGES.indexOf(here); if (i < 0) return;
    var j = Math.max(0, Math.min(PAGES.length - 1, i + delta));
    if (j !== i) location.href = PAGES[j] + ".html";
  }
  function toggleFull() {
    if (!document.fullscreenElement) { (document.documentElement.requestFullscreen || function () {}).call(document.documentElement); }
    else if (document.exitFullscreen) document.exitFullscreen();
  }
  function overlay(id) { var el = document.getElementById(id); if (el) el.hidden = !el.hidden; return el; }
  var breakTimer = null;
  function toggleBreak() {
    var el = overlay("break-overlay"); if (!el) return;
    if (el.hidden) { clearInterval(breakTimer); return; }
    var end = Date.now() + 5 * 60 * 1000, clock = el.querySelector(".breakclock");
    function tick() {
      var s = Math.max(0, Math.round((end - Date.now()) / 1000));
      clock.textContent = Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0");
      if (s === 0) clearInterval(breakTimer);
    }
    tick(); clearInterval(breakTimer); breakTimer = setInterval(tick, 500);
  }
  function initKeys() {
    document.addEventListener("keydown", function (e) {
      var tag = (e.target.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea" || tag === "select" || e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.key === "ArrowRight" || e.key === "PageDown") { go(1); e.preventDefault(); }
      else if (e.key === "ArrowLeft" || e.key === "PageUp") { go(-1); e.preventDefault(); }
      else if (e.key === "]") goPage(1);
      else if (e.key === "[") goPage(-1);
      else if (e.key === "t" || e.key === "T") toggleTheme();
      else if (e.key === "f" || e.key === "F") toggleFull();
      else if (e.key === "l" || e.key === "L") { var a = document.querySelector("a.lang"); if (a) location.href = a.href; }
      else if (e.key === "b" || e.key === "B") toggleBreak();
      else if (e.key === "?") overlay("help-overlay");
      else if (e.key === "Escape") document.querySelectorAll(".overlay").forEach(function (o) { o.hidden = true; });
    });
    document.querySelectorAll("[data-act]").forEach(function (b) {
      b.addEventListener("click", function () {
        var a = b.getAttribute("data-act");
        if (a === "theme") toggleTheme(); else if (a === "full") toggleFull();
        else if (a === "help") overlay("help-overlay"); else if (a === "break") toggleBreak();
        else if (a === "close") { var o = b.closest(".overlay"); if (o) o.hidden = true; if (o && o.id === "break-overlay") clearInterval(breakTimer); }
      });
    });
  }

  function copyText(text, btn) {
    function done() { if (btn) { var t = btn.textContent; btn.textContent = L.copied; setTimeout(function () { btn.textContent = t; }, 1300); } }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () { fallback(); });
    else fallback();
    function fallback() {
      var ta = document.createElement("textarea"); ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); } catch (e) { /* ignore */ } document.body.removeChild(ta); done();
    }
  }
  function download(name, text, type) {
    var blob = new Blob([text], { type: type || "text/markdown;charset=utf-8" });
    var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }

  window.NK = {
    LANG: LANG, L: L, TYPES: TYPES, Store: Store, Tip: Tip, fmt: fmt, signed: signed, path: path,
    typeColor: typeColor, cssVar: cssVar, accent: accent, copy: copyText, download: download,
    chName: function (c) { return L.ch[c] ? L.ch[c][0] : c; },
    chUnit: function (c) { return L.ch[c] ? L.ch[c][1] : ""; },
    typeName: function (t) { return L.type[t] || t; },
    shortName: function (t) { return L.short[t] || t; }
  };

  document.addEventListener("DOMContentLoaded", function () {
    initRoute(); initPolls(); bindNumbers(); initKeys();
    document.querySelectorAll("[data-copy]").forEach(function (b) {
      b.addEventListener("click", function () {
        var src = document.getElementById(b.getAttribute("data-copy"));
        if (src) copyText(src.value !== undefined && src.tagName === "TEXTAREA" ? src.value : src.textContent, b);
      });
    });
    document.querySelectorAll('a[href*="colab.research.google.com"]').forEach(function (a) {
      a.addEventListener("click", function () { Store.log("colab:" + here, true); });
    });
  });
})();
