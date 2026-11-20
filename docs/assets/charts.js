/* Small SVG charts for the NOKTA workshop: lines, bars, box plots and scatters.
   Thin marks, recessive axes, hover tooltips; text uses the ink colors. */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  function fmt(x, nd) { return window.NK ? NK.fmt(x, nd) : (+x).toFixed(nd); }
  function niceTicks(lo, hi, n) {
    if (!(hi > lo)) { hi = lo + 1; }
    var span = hi - lo, step = Math.pow(10, Math.floor(Math.log10(span / n)));
    var err = n / span * step;
    if (err <= 0.15) step *= 10; else if (err <= 0.35) step *= 5; else if (err <= 0.75) step *= 2;
    var t = [], s = Math.ceil(lo / step) * step;
    for (var v = s; v <= hi + step * 1e-9; v += step) t.push(+v.toFixed(10));
    return { ticks: t, step: step };
  }
  function decimals(step) { return step >= 1 ? 0 : Math.min(3, Math.ceil(-Math.log10(step))); }
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;"); }
  function ext(arr) {
    var lo = Infinity, hi = -Infinity;
    arr.forEach(function (v) { if (v !== null && isFinite(v)) { if (v < lo) lo = v; if (v > hi) hi = v; } });
    return [lo, hi];
  }
  // Width of the drawing in px of the container, so that text keeps its size in narrow columns.
  function fitW(el, def, min) {
    var cs = getComputedStyle(el), w = el.clientWidth - parseFloat(cs.paddingLeft || 0) - parseFloat(cs.paddingRight || 0);
    return w > 0 ? Math.round(Math.max(min, Math.min(def, w))) : def;
  }
  function frame(el, W, H) {
    el.innerHTML = "";
    var svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("role", "img");
    el.appendChild(svg);
    return svg;
  }
  function axes(o) {
    // o: W,H,m,xs,ys,xt,yt,xlab,ylab,xfmt,yfmt
    var s = "";
    s += '<g class="ch-grid">';
    o.yt.ticks.forEach(function (v) { s += '<line x1="' + o.m.l + '" x2="' + (o.W - o.m.r) + '" y1="' + o.ys(v) + '" y2="' + o.ys(v) + '"/>'; });
    s += "</g><g class=\"ch-axis\">";
    o.yt.ticks.forEach(function (v) { s += '<text x="' + (o.m.l - 8) + '" y="' + (o.ys(v) + 4) + '" text-anchor="end">' + o.yfmt(v) + "</text>"; });
    if (o.xt) o.xt.ticks.forEach(function (v) { s += '<text x="' + o.xs(v) + '" y="' + (o.H - o.m.b + 18) + '" text-anchor="middle">' + o.xfmt(v) + "</text>"; });
    s += '<line x1="' + o.m.l + '" x2="' + (o.W - o.m.r) + '" y1="' + (o.H - o.m.b) + '" y2="' + (o.H - o.m.b) + '"/>';
    if (o.xlab) s += '<text x="' + ((o.m.l + o.W - o.m.r) / 2) + '" y="' + (o.H - 6) + '" text-anchor="middle">' + esc(o.xlab) + "</text>";
    if (o.ylab) s += '<text x="' + o.m.l + '" y="' + (o.m.t - 12) + '" text-anchor="start" class="ch-title">' + esc(o.ylab) + "</text>";
    return s + "</g>";
  }

  /* ---------------- line chart ---------------- */
  function line(el, o) {
    var W = o.width || fitW(el, 720, 360), H = o.height || 300, m = Object.assign({ l: 54, r: 16, t: 30, b: 42 }, o.margin || {});
    var xsAll = [], ysAll = [];
    o.series.forEach(function (s) { s.pts.forEach(function (p) { xsAll.push(p[0]); if (p[1] !== null) ysAll.push(p[1]); }); });
    (o.marks || []).forEach(function (p) { ysAll.push(p.y); });
    (o.hlines || []).forEach(function (h) { ysAll.push(h.y); });
    var xe = ext(xsAll), ye = ext(ysAll);
    if (o.x && o.x.min !== undefined) xe[0] = o.x.min; if (o.x && o.x.max !== undefined) xe[1] = o.x.max;
    if (o.y && o.y.min !== undefined) ye[0] = o.y.min; if (o.y && o.y.max !== undefined) ye[1] = o.y.max;
    var pad = (ye[1] - ye[0]) * 0.06 || 1; if (!(o.y && o.y.min !== undefined)) ye[0] -= pad; if (!(o.y && o.y.max !== undefined)) ye[1] += pad;
    var xs = function (v) { return m.l + (v - xe[0]) / (xe[1] - xe[0] || 1) * (W - m.l - m.r); };
    var ys = function (v) { return H - m.b - (v - ye[0]) / (ye[1] - ye[0] || 1) * (H - m.t - m.b); };
    var yt = niceTicks(ye[0], ye[1], 5), xt = niceTicks(xe[0], xe[1], 7);
    var yfmt = (o.y && o.y.fmt) || function (v) { return fmt(v, decimals(yt.step)); };
    var xfmt = (o.x && o.x.fmt) || function (v) { return fmt(v, decimals(xt.step)); };
    var svg = frame(el, W, H), s = "";
    (o.bands || []).forEach(function (b) {
      s += '<rect x="' + xs(b.x0) + '" y="' + m.t + '" width="' + Math.max(1, xs(b.x1) - xs(b.x0)) + '" height="' + (H - m.t - m.b) + '" fill="' + b.fill + '" opacity="' + (b.opacity || 0.14) + '"/>';
      if (b.label) s += '<text class="ch-lbl" x="' + (xs(b.x0) + 4) + '" y="' + (m.t + 13) + '">' + esc(b.label) + "</text>";
    });
    s += axes({ W: W, H: H, m: m, xs: xs, ys: ys, xt: xt, yt: yt, xlab: o.x && o.x.label, ylab: o.y && o.y.label, xfmt: xfmt, yfmt: yfmt });
    (o.hlines || []).forEach(function (h) {
      s += '<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + ys(h.y) + '" y2="' + ys(h.y) + '" stroke="' + (h.color || "currentColor") + '" stroke-width="1.5" stroke-dasharray="' + (h.dash || "5 4") + '"/>';
      if (h.label) s += '<text class="ch-lbl" x="' + (W - m.r - 4) + '" y="' + (ys(h.y) - 5) + '" text-anchor="end">' + esc(h.label) + "</text>";
    });
    o.series.forEach(function (sr) {
      var d = "", pen = false;
      sr.pts.forEach(function (p) {
        if (p[1] === null || !isFinite(p[1])) { pen = false; return; }
        d += (pen ? "L" : "M") + xs(p[0]).toFixed(1) + "," + ys(p[1]).toFixed(1); pen = true;
      });
      s += '<path d="' + d + '" fill="none" stroke="' + sr.color + '" stroke-width="' + (sr.width || 2) + '" stroke-linejoin="round" stroke-linecap="round"' + (sr.dash ? ' stroke-dasharray="' + sr.dash + '"' : "") + (sr.opacity ? ' opacity="' + sr.opacity + '"' : "") + "/>";
      if (sr.dots) sr.pts.forEach(function (p) { if (p[1] !== null) s += '<circle cx="' + xs(p[0]) + '" cy="' + ys(p[1]) + '" r="' + (sr.r || 4) + '" fill="' + sr.color + '" stroke="var(--panel)" stroke-width="2"/>'; });
      if (sr.label) { var lp = sr.pts.filter(function (p) { return p[1] !== null; }).pop(); if (lp) s += '<text class="ch-val" x="' + (xs(lp[0]) + 6) + '" y="' + (ys(lp[1]) + 4) + '">' + esc(sr.label) + "</text>"; }
    });
    (o.marks || []).forEach(function (p) {
      var cx = xs(p.x), cy = ys(p.y), c = p.color || "var(--bad)";
      if (p.shape === "x") s += '<path d="M' + (cx - 5) + "," + (cy - 5) + "L" + (cx + 5) + "," + (cy + 5) + "M" + (cx - 5) + "," + (cy + 5) + "L" + (cx + 5) + "," + (cy - 5) + '" stroke="' + c + '" stroke-width="2.4"/>';
      else s += '<circle cx="' + cx + '" cy="' + cy + '" r="' + (p.r || 7) + '" fill="none" stroke="' + c + '" stroke-width="2.4"/>';
    });
    s += '<line class="xh" x1="0" x2="0" y1="' + m.t + '" y2="' + (H - m.b) + '" stroke="var(--muted)" stroke-width="1" opacity="0"/>';
    s += '<rect class="ch-hit" x="' + m.l + '" y="' + m.t + '" width="' + (W - m.l - m.r) + '" height="' + (H - m.t - m.b) + '"/>';
    svg.innerHTML = s;
    if (o.tooltip) {
      var hit = svg.querySelector(".ch-hit"), xh = svg.querySelector(".xh");
      hit.addEventListener("mousemove", function (e) {
        var r = svg.getBoundingClientRect(), px = (e.clientX - r.left) / r.width * W;
        var xv = xe[0] + (px - m.l) / (W - m.l - m.r) * (xe[1] - xe[0]);
        var res = o.tooltip(xv); if (!res) return;
        xh.setAttribute("x1", xs(res.x)); xh.setAttribute("x2", xs(res.x)); xh.setAttribute("opacity", "0.7");
        NK.Tip.show(res.html, e.clientX, e.clientY);
      });
      hit.addEventListener("mouseleave", function () { xh.setAttribute("opacity", "0"); NK.Tip.hide(); });
    }
    return { xs: xs, ys: ys, svg: svg };
  }

  /* ---------------- bar chart with a smooth transition ---------------- */
  function bars(el, o) {
    var items = o.items, n = items.length;
    var W = o.width || fitW(el, 640, 420), rowH = o.rowH || 34, m = Object.assign({ l: o.labelW || 170, r: 70, t: o.title ? 30 : 10, b: 26 }, o.margin || {});
    var H = o.height || (m.t + m.b + n * rowH);
    var vals = items.map(function (d) { return d.value; });
    var lo = o.min !== undefined ? o.min : Math.min(0, Math.min.apply(null, vals));
    var hi = o.max !== undefined ? o.max : Math.max(0, Math.max.apply(null, vals));
    if (hi === lo) hi = lo + 1;
    var xs = function (v) { return m.l + (v - lo) / (hi - lo) * (W - m.l - m.r); };
    var prev = el._prev || vals.map(function () { return o.from !== undefined ? o.from : 0; });
    var start = null, dur = o.instant ? 0 : 650;
    var svg = frame(el, W, H), t0 = xs(Math.max(lo, Math.min(hi, 0)));
    function draw(k) {
      var s = "";
      if (o.title) s += '<text class="ch-title" x="' + m.l + '" y="18">' + esc(o.title) + "</text>";
      var xt = niceTicks(lo, hi, 5);
      s += '<g class="ch-grid">';
      xt.ticks.forEach(function (v) { s += '<line x1="' + xs(v) + '" x2="' + xs(v) + '" y1="' + m.t + '" y2="' + (H - m.b) + '"/>'; });
      s += '</g><g class="ch-axis">';
      xt.ticks.forEach(function (v) { s += '<text x="' + xs(v) + '" y="' + (H - m.b + 16) + '" text-anchor="middle">' + fmt(v, decimals(xt.step)) + "</text>"; });
      s += '<line x1="' + t0 + '" x2="' + t0 + '" y1="' + m.t + '" y2="' + (H - m.b) + '" stroke="var(--muted)"/></g>';
      items.forEach(function (d, i) {
        var v = prev[i] + (d.value - prev[i]) * k, y = m.t + i * rowH + 5, h = rowH - 10;
        var x0 = Math.min(t0, xs(v)), w = Math.max(1.5, Math.abs(xs(v) - t0));
        s += '<text class="ch-lbl" x="' + (m.l - 10) + '" y="' + (y + h / 2 + 4) + '" text-anchor="end"' + (d.bold ? ' font-weight="700" style="fill:var(--ink)"' : "") + ">" + esc(d.label) + "</text>";
        s += '<rect x="' + x0 + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="4" fill="' + (d.color || "var(--accent)") + '"' + (d.opacity ? ' opacity="' + d.opacity + '"' : "") + ' data-i="' + i + '"/>';
        var tx = v >= 0 ? xs(v) + 6 : xs(v) - 6;
        s += '<text class="ch-val" x="' + tx + '" y="' + (y + h / 2 + 4) + '" text-anchor="' + (v >= 0 ? "start" : "end") + '">' + (o.signed ? NK.signed(v, o.nd === undefined ? 1 : o.nd) : fmt(v, o.nd === undefined ? 1 : o.nd)) + (o.unit ? " " + esc(o.unit) : "") + "</text>";
      });
      svg.innerHTML = s;
    }
    function step(ts) {
      if (start === null) start = ts;
      var k = dur ? Math.min(1, (ts - start) / dur) : 1;
      k = 1 - Math.pow(1 - k, 3);
      draw(k);
      if (k < 1) requestAnimationFrame(step); else { el._prev = vals.slice(); bindTips(); }
    }
    function bindTips() {
      if (!o.tip) return;
      svg.querySelectorAll("rect[data-i]").forEach(function (r) {
        r.addEventListener("mousemove", function (e) { NK.Tip.show(o.tip(items[+r.getAttribute("data-i")]), e.clientX, e.clientY); });
        r.addEventListener("mouseleave", NK.Tip.hide);
      });
    }
    if (dur) requestAnimationFrame(step); else { draw(1); el._prev = vals.slice(); bindTips(); }
  }

  /* ---------------- box plot ---------------- */
  function box(el, o) {
    var g = o.groups, W = o.width || fitW(el, 720, 420), H = o.height || 320, m = { l: 54, r: 14, t: 30, b: 54 };
    var all = []; g.forEach(function (d) { all.push(d.lo, d.hi); (d.out || []).forEach(function (v) { all.push(v); }); });
    var ye = ext(all); var pad = (ye[1] - ye[0]) * 0.06; ye[0] -= pad; ye[1] += pad;
    var ys = function (v) { return H - m.b - (v - ye[0]) / (ye[1] - ye[0]) * (H - m.t - m.b); };
    var bw = (W - m.l - m.r) / g.length, yt = niceTicks(ye[0], ye[1], 5);
    var svg = frame(el, W, H);
    var s = axes({ W: W, H: H, m: m, xs: null, ys: ys, xt: null, yt: yt, ylab: o.ylabel, yfmt: function (v) { return fmt(v, decimals(yt.step)); } });
    if (ye[0] < 0 && ye[1] > 0) s += '<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + ys(0) + '" y2="' + ys(0) + '" stroke="var(--muted)" stroke-width="1.2"/>';
    g.forEach(function (d, i) {
      var cx = m.l + bw * (i + 0.5), w = Math.min(46, bw * 0.5);
      s += '<line x1="' + cx + '" x2="' + cx + '" y1="' + ys(d.lo) + '" y2="' + ys(d.hi) + '" stroke="var(--muted)" stroke-width="1.5"/>';
      s += '<rect x="' + (cx - w / 2) + '" y="' + ys(d.q3) + '" width="' + w + '" height="' + Math.max(1, ys(d.q1) - ys(d.q3)) + '" rx="4" fill="' + d.color + '" opacity="0.85" data-i="' + i + '"/>';
      s += '<line x1="' + (cx - w / 2) + '" x2="' + (cx + w / 2) + '" y1="' + ys(d.med) + '" y2="' + ys(d.med) + '" stroke="var(--ink)" stroke-width="2.5"/>';
      if (o.showMean) s += '<circle cx="' + cx + '" cy="' + ys(d.mean) + '" r="4" fill="var(--panel)" stroke="var(--ink)" stroke-width="2"/>';
      (d.out || []).forEach(function (v) { s += '<circle cx="' + cx + '" cy="' + ys(v) + '" r="2.6" fill="none" stroke="var(--muted)"/>'; });
      s += '<text class="ch-lbl" x="' + cx + '" y="' + (H - m.b + 18) + '" text-anchor="middle">' + esc(d.label) + "</text>";
      if (d.sub) s += '<text class="ch-lbl" x="' + cx + '" y="' + (H - m.b + 34) + '" text-anchor="middle">' + esc(d.sub) + "</text>";
    });
    svg.innerHTML = s;
    if (o.tip) svg.querySelectorAll("rect[data-i]").forEach(function (r) {
      r.addEventListener("mousemove", function (e) { NK.Tip.show(o.tip(g[+r.getAttribute("data-i")]), e.clientX, e.clientY); });
      r.addEventListener("mouseleave", NK.Tip.hide);
    });
  }

  /* ---------------- scatter ---------------- */
  function scatter(el, o) {
    var W = o.width || fitW(el, 640, 360), H = o.height || 380, m = { l: 60, r: 16, t: 30, b: 44 };
    var xe = ext(o.pts.map(function (p) { return p.x; })), ye = ext(o.pts.map(function (p) { return p.y; }));
    var px = (xe[1] - xe[0]) * 0.05, py = (ye[1] - ye[0]) * 0.06; xe[0] -= px; xe[1] += px; ye[0] -= py; ye[1] += py;
    var xs = function (v) { return m.l + (v - xe[0]) / (xe[1] - xe[0]) * (W - m.l - m.r); };
    var ys = function (v) { return H - m.b - (v - ye[0]) / (ye[1] - ye[0]) * (H - m.t - m.b); };
    var xt = niceTicks(xe[0], xe[1], 6), yt = niceTicks(ye[0], ye[1], 5);
    var svg = frame(el, W, H);
    var s = axes({ W: W, H: H, m: m, xs: xs, ys: ys, xt: xt, yt: yt, xlab: o.x.label, ylab: o.y.label, xfmt: function (v) { return fmt(v, decimals(xt.step)); }, yfmt: function (v) { return fmt(v, decimals(yt.step)); } });
    o.pts.forEach(function (p, i) {
      s += '<circle cx="' + xs(p.x).toFixed(1) + '" cy="' + ys(p.y).toFixed(1) + '" r="' + (p.r || 4) + '" fill="' + p.color + '" fill-opacity="' + (p.op || 0.75) + '" stroke="var(--panel)" stroke-width="1" data-i="' + i + '"/>';
    });
    (o.lines || []).forEach(function (l) {
      s += '<line x1="' + xs(l.x0) + '" y1="' + ys(l.y0) + '" x2="' + xs(l.x1) + '" y2="' + ys(l.y1) + '" stroke="' + l.color + '" stroke-width="' + (l.w || 2.5) + '"' + (l.dash ? ' stroke-dasharray="' + l.dash + '"' : "") + "/>";
      if (l.label) s += '<text class="ch-val" x="' + (xs(l.x1) + 4) + '" y="' + (ys(l.y1) + 4) + '">' + esc(l.label) + "</text>";
    });
    svg.innerHTML = s;
    if (o.tip) svg.querySelectorAll("circle[data-i]").forEach(function (c) {
      c.addEventListener("mousemove", function (e) { NK.Tip.show(o.tip(o.pts[+c.getAttribute("data-i")]), e.clientX, e.clientY); });
      c.addEventListener("mouseleave", NK.Tip.hide);
    });
    return { xs: xs, ys: ys };
  }

  function legend(el, items) {
    el.innerHTML = items.map(function (d) {
      return '<span><i class="sw" style="background:' + d.color + '"></i>' + esc(d.label) + "</span>";
    }).join("");
  }

  window.Charts = { line: line, bars: bars, box: box, scatter: scatter, legend: legend, niceTicks: niceTicks };
})();
