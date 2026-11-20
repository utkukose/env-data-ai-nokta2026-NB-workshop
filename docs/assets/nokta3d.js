/* 3D scenes of the NOKTA workshop, built with three.js (MIT license):
   the campus twin, the point cloud for clustering and PCA, and the model surface. */
(function () {
  "use strict";
  var T = window.THREE;
  var BLUE = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"];
  function dark() { return document.documentElement.getAttribute("data-theme") === "dark"; }
  function lerpHex(a, b, k) {
    var ca = new T.Color(a), cb = new T.Color(b);
    return ca.lerp(cb, Math.max(0, Math.min(1, k)));
  }
  function seqColor(k) {
    k = Math.max(0, Math.min(1, k));
    var ramp = dark() ? BLUE.slice(0, 9) : BLUE.slice(3);
    if (dark()) ramp = ramp.slice().reverse();
    var x = k * (ramp.length - 1), i = Math.min(ramp.length - 2, Math.floor(x));
    return lerpHex(ramp[i], ramp[i + 1], x - i);
  }
  function rampColor(k) { // full light-to-dark ramp for surfaces; reversed on the dark theme
    k = Math.max(0, Math.min(1, k));
    var ramp = dark() ? BLUE.slice(1, 11).reverse() : BLUE.slice(0, 11);
    var x = k * (ramp.length - 1), i = Math.min(ramp.length - 2, Math.floor(x));
    return lerpHex(ramp[i], ramp[i + 1], x - i);
  }
  function divColor(k) { // k in [-1, 1]
    var mid = dark() ? "#4a4a46" : "#e4e2dc";
    return k < 0 ? lerpHex(mid, dark() ? "#3987e5" : "#2a78d6", -k) : lerpHex(mid, dark() ? "#e66767" : "#e34948", k);
  }
  function webglOK() {
    try { var c = document.createElement("canvas"); return !!(window.WebGLRenderingContext && (c.getContext("webgl2") || c.getContext("webgl"))); }
    catch (e) { return false; }
  }

  /* ---------------- text sprites ---------------- */
  function label(text, o) {
    o = o || {};
    var size = o.size || 44, pad = 14, font = "700 " + size + "px Atkinson Hyperlegible, Segoe UI, sans-serif";
    var c = document.createElement("canvas"), g = c.getContext("2d");
    g.font = font;
    var lines = String(text).split("\n"), w = 0;
    lines.forEach(function (l) { w = Math.max(w, g.measureText(l).width); });
    c.width = Math.ceil(w + pad * 2); c.height = Math.ceil(lines.length * size * 1.18 + pad * 1.4);
    g.font = font;
    if (o.bg !== null) {
      g.fillStyle = o.bg || "rgba(255,255,255,0.92)";
      var r = 14; g.beginPath();
      g.moveTo(r, 0); g.arcTo(c.width, 0, c.width, c.height, r); g.arcTo(c.width, c.height, 0, c.height, r);
      g.arcTo(0, c.height, 0, 0, r); g.arcTo(0, 0, c.width, 0, r); g.closePath(); g.fill();
      if (o.border) { g.strokeStyle = o.border; g.lineWidth = 5; g.stroke(); }
    }
    g.fillStyle = o.fg || "#18231F"; g.textBaseline = "top";
    lines.forEach(function (l, i) { g.fillText(l, pad, pad * 0.7 + i * size * 1.18); });
    var tex = new T.CanvasTexture(c); tex.colorSpace = T.SRGBColorSpace; tex.anisotropy = 4;
    var sp = new T.Sprite(new T.SpriteMaterial({ map: tex, depthTest: o.depthTest !== false, transparent: true }));
    var h = o.height || 3; sp.scale.set(h * c.width / c.height, h, 1);
    sp.userData.aspect = c.width / c.height;
    return sp;
  }
  function relabel(sp, text, o) {
    var n = label(text, o);
    sp.material.map.dispose(); sp.material.map = n.material.map; sp.material.needsUpdate = true;
    sp.scale.copy(n.scale);
  }

  /* ---------------- common stage ---------------- */
  function stage(container, o) {
    o = o || {};
    if (!T || !webglOK()) {
      container.insertAdjacentHTML("beforeend", '<div class="fallback">' + (o.fallback || "WebGL is not available in this browser.") + "</div>");
      return null;
    }
    var renderer = new T.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    renderer.outputColorSpace = T.SRGBColorSpace;
    if (o.shadows) { renderer.shadowMap.enabled = true; renderer.shadowMap.type = T.PCFSoftShadowMap; }
    container.appendChild(renderer.domElement);
    var scene = new T.Scene();
    var fov0 = o.fov || 42, fit = o.fitAspect || 1.15;
    var camera = new T.PerspectiveCamera(fov0, 1, 0.1, 3000);
    var controls = new T.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; controls.dampingFactor = 0.08;
    var frames = [], visible = true, clock = new T.Clock();
    function size() {
      var w = container.clientWidth || 600, h = container.clientHeight || 400;
      renderer.setSize(w, h, false); camera.aspect = w / h;
      // On stages narrower than the design ratio the vertical angle grows, so the scene keeps its width.
      camera.fov = camera.aspect < fit ? Math.atan(Math.tan(fov0 * Math.PI / 360) * fit / camera.aspect) * 360 / Math.PI : fov0;
      camera.updateProjectionMatrix();
    }
    size();
    if (window.ResizeObserver) new ResizeObserver(size).observe(container); else window.addEventListener("resize", size);
    if (window.IntersectionObserver) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(container);
    function loop() {
      requestAnimationFrame(loop);
      if (!visible) { clock.getDelta(); return; }
      var dt = Math.min(0.05, clock.getDelta());
      frames.forEach(function (f) { f(dt); });
      controls.update();
      renderer.render(scene, camera);
    }
    loop();
    return { renderer: renderer, scene: scene, camera: camera, controls: controls, el: container,
      onFrame: function (f) { frames.push(f); } };
  }

  function pick(st, objects, cb) {
    var ray = new T.Raycaster(), v = new T.Vector2(), down = null;
    st.renderer.domElement.addEventListener("pointerdown", function (e) { down = [e.clientX, e.clientY]; });
    st.renderer.domElement.addEventListener("pointerup", function (e) {
      if (!down || Math.abs(e.clientX - down[0]) + Math.abs(e.clientY - down[1]) > 6) return;
      var r = st.renderer.domElement.getBoundingClientRect();
      v.set((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1);
      ray.setFromCamera(v, st.camera);
      var hit = ray.intersectObjects(objects(), true)[0];
      if (hit) cb(hit, e);
    });
  }

  /* =================================================================
     Campus twin: six NOKTA points, one traveling station, the sun.
     ================================================================= */
  var LAYOUT = {
    shaded: [26, -33], traffic: [-40, 33], reference: [-54, -34],
    sunny_hard: [20, 8], crowded: [-13, 3], green: [55, 12]
  };
  function twin(container, o) {
    var st = stage(container, { shadows: true, fallback: o.fallback });
    if (!st) return null;
    var scene = st.scene, cam = st.camera;
    cam.position.set(-24, 115, 122); st.controls.target.set(0, 0, -4);
    st.controls.maxPolarAngle = Math.PI * 0.47; st.controls.minDistance = 40; st.controls.maxDistance = 320;
    var hemi = new T.HemisphereLight(0xdfefff, 0x6b7a55, 0.9); scene.add(hemi);
    var sun = new T.DirectionalLight(0xfff4dd, 1.9);
    sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
    var sc = sun.shadow.camera; sc.left = -95; sc.right = 95; sc.top = 95; sc.bottom = -95; sc.near = 10; sc.far = 420;
    sun.shadow.bias = -0.0005; scene.add(sun); scene.add(sun.target);
    var mat = function (c, extra) { return new T.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.9, metalness: 0.0 }, extra || {})); };
    function box(w, h, d, c, x, y, z, cast) {
      var m = new T.Mesh(new T.BoxGeometry(w, h, d), mat(c));
      m.position.set(x, y, z); m.castShadow = cast !== false; m.receiveShadow = true; scene.add(m); return m;
    }
    function plane(w, d, c, x, z, y) {
      var m = new T.Mesh(new T.PlaneGeometry(w, d), mat(c)); m.rotation.x = -Math.PI / 2;
      m.position.set(x, y || 0, z); m.receiveShadow = true; scene.add(m); return m;
    }
    // ground, road, square, lawns
    plane(190, 140, 0xcfd8bf, 0, 0, -0.02);
    plane(190, 11, 0x5d6266, 0, 45, 0.02);
    for (var i = -90; i < 90; i += 9) plane(4, 0.5, 0xf2f2ea, i, 45, 0.04);
    plane(34, 30, 0xe6e3dc, 20, 8, 0.03);
    plane(30, 38, 0x8fbf6a, 55, 11, 0.03);
    plane(36, 26, 0xa9cf86, -54, -34, 0.03);
    plane(26, 12, 0xd9d4ca, -13, 3, 0.035);
    // buildings with window rows
    function windows(w, h) {
      var c = document.createElement("canvas"); c.width = 128; c.height = 128; var g = c.getContext("2d");
      g.fillStyle = "#efe9de"; g.fillRect(0, 0, 128, 128); g.fillStyle = "#8aa2b4";
      for (var yy = 10; yy < 120; yy += 24) for (var xx = 8; xx < 120; xx += 20) g.fillRect(xx, yy, 12, 12);
      var t = new T.CanvasTexture(c); t.colorSpace = T.SRGBColorSpace; t.wrapS = t.wrapT = 1000;
      t.repeat.set(Math.max(1, w / 10), Math.max(1, h / 8)); return t;
    }
    function building(w, h, d, x, z, tint) {
      var m = new T.Mesh(new T.BoxGeometry(w, h, d), [
        mat(tint, { map: windows(d, h) }), mat(tint, { map: windows(d, h) }), mat(0xbdb6aa),
        mat(0xbdb6aa), mat(tint, { map: windows(w, h) }), mat(tint, { map: windows(w, h) })]);
      m.position.set(x, h / 2, z); m.castShadow = true; m.receiveShadow = true; scene.add(m); return m;
    }
    building(40, 16, 28, -40, 4, 0xffffff);
    building(22, 26, 28, 11, -34, 0xf6f1ea);
    building(22, 26, 28, 41, -34, 0xf3efe6);
    building(18, 10, 16, -62, 14, 0xfbf7ef);
    box(6, 4, 0.6, 0x3b6e91, -20, 2.5, 3.5);           // entrance canopy
    // trees
    function tree(x, z, s) {
      s = s || 1;
      var trunk = new T.Mesh(new T.CylinderGeometry(0.5 * s, 0.7 * s, 5 * s, 8), mat(0x7a5a3a));
      trunk.position.set(x, 2.5 * s, z); trunk.castShadow = true; scene.add(trunk);
      var crown = new T.Mesh(new T.SphereGeometry(3.6 * s, 14, 10), mat(0x3f8a3a));
      crown.position.set(x, 6.8 * s, z); crown.castShadow = true; crown.receiveShadow = true; scene.add(crown);
    }
    [[46, -2], [52, 0], [60, -3], [64, 6], [48, 9], [58, 18], [64, 24], [46, 24], [52, 28], [61, 13], [44, 16]].forEach(function (p) { tree(p[0], p[1], 1.05); });
    [[-68, -46], [-40, -46], [-70, -22]].forEach(function (p) { tree(p[0], p[1], 0.8); });
    // cars and a bus on the road
    var cars = [];
    [[-80, 42.5, 9, 0x2a78d6], [-20, 42.5, 11, 0xd95926], [40, 42.5, 8, 0xe6e3dc], [10, 47.5, -10, 0x6e7782], [70, 47.5, -12, 0x1baf7a]].forEach(function (c) {
      var m = box(6, 2.6, 3, c[3], c[0], 1.4, c[1]); cars.push({ m: m, v: c[2] });
    });
    var bus = box(14, 4, 3.4, 0xeda100, -60, 2.1, 47.5); cars.push({ m: bus, v: -6 });
    // people near the entrance
    var people = [];
    for (var p = 0; p < 12; p++) {
      var pm = new T.Mesh(new T.CapsuleGeometry(0.55, 1.4, 4, 8), mat([0x2a78d6, 0xe87ba4, 0x6250d6, 0xeb6834][p % 4]));
      pm.position.set(-13 + (Math.random() - 0.5) * 18, 1.25, 3 + (Math.random() - 0.5) * 9); pm.castShadow = true;
      scene.add(pm); people.push({ m: pm, a: Math.random() * 6.28, s: 1.5 + Math.random() * 2 });
    }
    // surroundings that set the campuses apart: A lies high inland, B inside a city, C on the coast
    var deco = { A: new T.Group(), B: new T.Group(), C: new T.Group() };
    Object.keys(deco).forEach(function (k) { scene.add(deco[k]); });
    function dplane(w, d, c, x, z, y, g) {
      var m = new T.Mesh(new T.PlaneGeometry(w, d), mat(c)); m.rotation.x = -Math.PI / 2; m.position.set(x, y, z); g.add(m); return m;
    }
    function dmesh(geo, c, x, y, z, g) { var m = new T.Mesh(geo, mat(c)); m.position.set(x, y, z); g.add(m); return m; }
    // A: upland with hills and snowy mountains
    dplane(900, 700, 0xc9c69a, 0, -100, -0.3, deco.A);
    [[-150, -96, 34, 20], [-75, -92, 30, 16], [5, -98, 36, 22], [85, -94, 30, 18], [160, -96, 34, 20]].forEach(function (h) {
      var m = dmesh(new T.SphereGeometry(1, 20, 12, 0, Math.PI * 2, 0, Math.PI / 2), 0x9fae7c, h[0], 0, h[1], deco.A);
      m.scale.set(h[2], h[3], h[2] * 0.7);
    });
    [[-190, -112, 26, 34], [-115, -118, 30, 40], [-40, -114, 26, 36], [40, -120, 32, 44], [120, -114, 26, 36], [195, -118, 28, 38],
     [-160, -200, 60, 110], [-60, -215, 70, 130], [50, -205, 64, 120], [150, -210, 70, 125]].forEach(function (m) {
      dmesh(new T.ConeGeometry(m[2], m[3], 7), 0x8b8676, m[0], m[3] / 2, m[1], deco.A);
      dmesh(new T.ConeGeometry(m[2] * 0.37, m[3] * 0.35, 7), 0xf6f6f2, m[0], m[3] * 0.825 + 0.4, m[1], deco.A);
    });
    // B: a city of tall blocks around the campus
    dplane(900, 700, 0xb4b8bc, 0, -100, -0.3, deco.B);
    function tower(w, h, x, z, tint) {
      var tx = windows(w, h), tm = mat(tint, { map: tx }), roof = mat(0x8d9399);
      var m = new T.Mesh(new T.BoxGeometry(w, h, w), [tm, tm, roof, roof, tm, tm]); m.position.set(x, h / 2, z); deco.B.add(m);
    }
    [[-170, -92, 22, 70], [-128, -96, 20, 95], [-88, -90, 22, 60], [-48, -98, 18, 110], [-8, -92, 22, 75], [34, -96, 20, 100], [74, -90, 22, 65], [114, -98, 18, 90], [154, -92, 22, 80],
     [-122, -50, 20, 55], [-124, -10, 18, 80], [-120, 28, 20, 50], [122, -50, 20, 70], [124, -10, 18, 50], [120, 28, 20, 85]].forEach(function (b, i) {
      tower(b[2], b[3], b[0], b[1], [0xd5d9de, 0xc7ccd2, 0xe0dcd4][i % 3]);
    });
    // C: a beach and the sea behind the campus
    dplane(900, 160, 0xcfd8bf, 0, -2, -0.3, deco.C);
    dplane(900, 12, 0xe9dcb2, 0, -76, -0.25, deco.C);
    dplane(900, 600, 0x3f86c4, 0, -382, -0.3, deco.C);
    [[-70, -125, 0xffffff], [60, -160, 0xf2f2f2], [150, -115, 0xe8e2d6]].forEach(function (b) {
      dmesh(new T.BoxGeometry(12, 2.4, 4.5), b[2], b[0], 1.0, b[1], deco.C);
      dmesh(new T.BoxGeometry(4, 3, 3.4), 0xd9dde2, b[0] - 1.5, 3.4, b[1], deco.C);
    });
    // sensor stations, columns, labels and particle clouds at the six points
    var points = {}, accent = new T.Color(o.accent || "#0E7A5F");
    Object.keys(LAYOUT).forEach(function (t) {
      var x = LAYOUT[t][0], z = LAYOUT[t][1], g = new T.Group(); g.position.set(x, 0, z); scene.add(g);
      var pole = new T.Mesh(new T.CylinderGeometry(0.25, 0.25, 3, 8), mat(0x555555)); pole.position.y = 1.5; g.add(pole);
      var head = new T.Mesh(new T.BoxGeometry(1.6, 1.2, 1.6), mat(0xffffff)); head.position.y = 3.4; head.castShadow = true; g.add(head);
      var ring = new T.Mesh(new T.RingGeometry(3.2, 3.9, 40), new T.MeshBasicMaterial({ color: new T.Color(NK.typeColor(t)), side: T.DoubleSide, transparent: true, opacity: 0.9 }));
      ring.rotation.x = -Math.PI / 2; ring.position.y = 0.08; g.add(ring);
      var col = new T.Mesh(new T.CylinderGeometry(2.1, 2.1, 1, 28), mat(0x2a78d6, { transparent: true, opacity: 0.88, roughness: 0.5 }));
      col.position.set(1.2, 0.5, 4.4); col.castShadow = true; col.scale.y = 0.001; g.add(col);
      var tag = label(NK.shortName(t), { height: 4.6, border: NK.typeColor(t), depthTest: false }); tag.position.set(1.2, 6.5, -0.6); tag.renderOrder = 20; g.add(tag);
      var val = label(" ", { height: 3.4, bg: null, fg: dark() ? "#e8f2ee" : "#18231F", depthTest: false }); val.position.set(1.2, 3, 4.4); val.renderOrder = 21; g.add(val);
      var n = 220, pos = new Float32Array(n * 3), seeds = [];
      for (var k = 0; k < n; k++) {
        var a = Math.random() * 6.28, rr = 2 + Math.random() * 6, h = 0.5 + Math.random() * 9;
        pos[k * 3] = Math.cos(a) * rr; pos[k * 3 + 1] = h; pos[k * 3 + 2] = Math.sin(a) * rr; seeds.push([a, rr, h, Math.random() * 6]);
      }
      var geo = new T.BufferGeometry(); geo.setAttribute("position", new T.BufferAttribute(pos, 3));
      var cloud = new T.Points(geo, new T.PointsMaterial({ color: 0x6b5a46, size: 0.55, transparent: true, opacity: 0.75, depthWrite: false }));
      cloud.geometry.setDrawRange(0, 0); g.add(cloud);
      points[t] = { g: g, col: col, tag: tag, val: val, cloud: cloud, seeds: seeds, target: 0.001, value: null, pm: 0 };
      head.userData.type = t; col.userData.type = t; ring.userData.type = t;
    });
    // the traveling station
    var mover = new T.Group(); scene.add(mover);
    var mpole = new T.Mesh(new T.CylinderGeometry(0.35, 0.35, 3.4, 8), mat(0x333333)); mpole.position.y = 1.7; mover.add(mpole);
    var mhead = new T.Mesh(new T.BoxGeometry(2.2, 1.6, 2.2), mat(accent, { emissive: accent, emissiveIntensity: 0.25 })); mhead.position.y = 4; mhead.castShadow = true; mover.add(mhead);
    var halo = new T.Mesh(new T.RingGeometry(4.5, 5.5, 48), new T.MeshBasicMaterial({ color: accent, side: T.DoubleSide, transparent: true, opacity: 0.6 }));
    halo.rotation.x = -Math.PI / 2; halo.position.y = 0.1; mover.add(halo);
    var mtag = label("NOKTA Station", { height: 3, bg: "rgba(14,122,95,0.92)", fg: "#ffffff" }); mtag.position.y = 8.5; mover.add(mtag);
    mover.visible = false;

    var state = { campus: "A", round: "1", variable: "pm25_ugm3", mode: "results", hour: 10, playing: false, speed: 1, onTick: null };
    function visits() { return window.NOKTA.twin[state.campus][state.round === "mean" ? "1" : state.round]; }
    function valueFor(t, upto) {
      var ch = state.variable;
      if (state.round === "mean") {
        var a = findVisit("1", t), b = findVisit("2", t);
        return (a.median[ch] + b.median[ch]) / 2;
      }
      var v = findVisit(state.round, t);
      if (upto === undefined) return v.median[ch];
      var ser = v.series[ch], mins = v.minutes, vals = [];
      for (var i = 0; i < mins.length; i++) if (mins[i] <= upto && ser[i] !== null) vals.push(ser[i]);
      if (!vals.length) return null;
      vals.sort(function (p, q) { return p - q; });
      return vals[Math.floor(vals.length / 2)];
    }
    function findVisit(r, t) { return window.NOKTA.twin[state.campus][r].filter(function (v) { return v.type === t; })[0]; }
    function range() {
      var ch = state.variable, lo = Infinity, hi = -Infinity;
      ["1", "2"].forEach(function (r) { window.NOKTA.twin[state.campus][r].forEach(function (v) { var x = v.median[ch]; if (x < lo) lo = x; if (x > hi) hi = x; }); });
      if (ch === "temperature_c") { lo -= 0.5; hi += 0.5; }
      return [lo, hi];
    }
    function setColumn(t, value) {
      var P = points[t];
      if (value === null || value === undefined) { P.target = 0.001; relabel(P.val, " ", { height: 3.4, bg: null }); return; }
      var rg = range(), k = (value - rg[0]) / (rg[1] - rg[0] || 1);
      P.target = 2 + 24 * Math.max(0, k); P.value = value;
      P.col.material.color.copy(seqColor(0.15 + 0.85 * k));
      var nd = state.variable === "light_lux" ? 0 : state.variable === "uvb_wm2" ? 2 : 1;
      relabel(P.val, NK.fmt(value, nd) + " " + NK.chUnit(state.variable), { height: 3.6, bg: dark() ? "rgba(16,32,28,0.85)" : "rgba(255,255,255,0.85)", fg: dark() ? "#e8f2ee" : "#18231F" });
    }
    function setPM(t, pm) { var P = points[t]; P.pm = pm; P.cloud.geometry.setDrawRange(0, Math.min(220, Math.round((pm || 0) * 7))); }
    function refresh() {
      Object.keys(deco).forEach(function (k) { deco[k].visible = state.campus === k; });
      if (state.mode === "results") {
        mover.visible = false;
        Object.keys(points).forEach(function (t) {
          setColumn(t, valueFor(t));
          var pmv = state.round === "mean" ? (findVisit("1", t).median.pm25_ugm3 + findVisit("2", t).median.pm25_ugm3) / 2 : findVisit(state.round, t).median.pm25_ugm3;
          setPM(t, pmv);
        });
      } else { applyTime(state.hour); }
      sunAt(state.hour);
    }
    function sunAt(h) {
      var az = (145 + (h - 10) * 19) * Math.PI / 180;
      var el = (22 + 10 * Math.sin(Math.min(1, (h - 9.2) / 2.6) * Math.PI / 2)) * Math.PI / 180;
      var d = 200;
      sun.position.set(Math.sin(az) * Math.cos(el) * d, Math.sin(el) * d, -Math.cos(az) * Math.cos(el) * d);
      sun.target.position.set(0, 0, 0);
    }
    function hhmm(h) { var m = Math.round(h * 60); return Math.floor(m / 60) + ":" + String(m % 60).padStart(2, "0"); }
    function applyTime(h) {
      state.hour = h;
      var vs = visits(), info = { hour: h, clock: hhmm(h), at: null, moving: false };
      mover.visible = true;
      for (var k = 0; k < vs.length; k++) {
        var s = 10 + (25 * k) / 60, e = s + 15 / 60, nxt = vs[k + 1];
        var P0 = LAYOUT[vs[k].type];
        if (h < s) { setColumn(vs[k].type, null); setPM(vs[k].type, 0); continue; }
        if (h <= e) {
          mover.position.set(P0[0] + 2.5, 0, P0[1] + 3);
          var upto = Math.floor((h - s) * 60);
          var v = upto >= 2 ? valueFor(vs[k].type, upto) : null;
          setColumn(vs[k].type, v); setPM(vs[k].type, upto >= 2 ? pmAt(vs[k], upto) : 0);
          info.at = vs[k].type; info.minute = upto;
        } else {
          setColumn(vs[k].type, valueFor(vs[k].type)); setPM(vs[k].type, vs[k].median.pm25_ugm3);
          if (nxt && h < s + 25 / 60) {
            var P1 = LAYOUT[nxt.type], f = (h - e) / (10 / 60);
            mover.position.set(P0[0] + 2.5 + (P1[0] - P0[0]) * f, 0, P0[1] + 3 + (P1[1] - P0[1]) * f);
            info.moving = true; info.next = nxt.type;
          }
        }
      }
      sunAt(h);
      if (state.onTick) state.onTick(info);
    }
    function pmAt(v, upto) {
      var ser = v.series.pm25_ugm3, mins = v.minutes;
      for (var i = mins.length - 1; i >= 0; i--) if (mins[i] <= upto && ser[i] !== null) return ser[i];
      return 0;
    }
    var tAcc = 0;
    st.onFrame(function (dt) {
      Object.keys(points).forEach(function (t) {
        var P = points[t], s = P.col.scale.y; s += (P.target - s) * Math.min(1, dt * 4);
        P.col.scale.y = s; P.col.position.y = s / 2; P.val.position.y = s + 2.6; P.tag.position.y = s + 6.5;
        var arr = P.cloud.geometry.attributes.position.array;
        for (var k = 0; k < P.seeds.length; k++) {
          var sd = P.seeds[k]; sd[0] += dt * 0.15;
          arr[k * 3] = Math.cos(sd[0]) * sd[1]; arr[k * 3 + 2] = Math.sin(sd[0]) * sd[1]; arr[k * 3 + 1] = sd[2] + Math.sin(tAcc + sd[3]) * 0.6;
        }
        P.cloud.geometry.attributes.position.needsUpdate = true;
      });
      tAcc += dt;
      cars.forEach(function (c) { c.m.position.x += c.v * dt * 1.6; if (c.m.position.x > 95) c.m.position.x = -95; if (c.m.position.x < -95) c.m.position.x = 95; });
      people.forEach(function (p) { p.a += (Math.random() - 0.5) * 0.4; p.m.position.x += Math.cos(p.a) * p.s * dt; p.m.position.z += Math.sin(p.a) * p.s * dt;
        if (Math.abs(p.m.position.x + 13) > 12 || Math.abs(p.m.position.z - 3) > 7) p.a += Math.PI; });
      halo.material.opacity = 0.35 + 0.3 * Math.sin(tAcc * 4);
      if (state.playing) {
        var h = state.hour + dt * state.speed * (140 / 60) / 40;
        if (h >= 12 + 20 / 60) { h = 12 + 20 / 60; state.playing = false; if (state.onEnd) state.onEnd(); }
        applyTime(h);
      }
    });
    pick(st, function () { var a = []; Object.keys(points).forEach(function (t) { points[t].g.traverse(function (c) { if (c.isMesh) a.push(c); }); }); return a; },
      function (hit) {
        var t = hit.object.userData.type; if (!t) { var p = hit.object.parent; t = p && p.children.map(function (c) { return c.userData.type; }).filter(Boolean)[0]; }
        if (t && o.onPick) o.onPick(t, state);
      });
    document.addEventListener("nokta:theme", function () { refresh(); });
    refresh();
    return {
      set: function (k, v) { state[k] = v; if (k !== "speed") refresh(); },
      get: function (k) { return state[k]; },
      play: function (onTick, onEnd) {
        state.mode = "replay"; state.onTick = onTick; state.onEnd = onEnd;
        if (state.hour >= 12.33) state.hour = 10;
        state.playing = true; applyTime(state.hour);
      },
      pause: function () { state.playing = false; },
      reset: function () { state.playing = false; state.hour = 10; state.mode = "replay"; applyTime(10); },
      results: function () { state.playing = false; state.mode = "results"; state.hour = 12; refresh(); },
      seek: function (h) { state.mode = "replay"; state.playing = false; applyTime(h); },
      view: function (name) {
        var v = { overview: [-24, 115, 122], top: [0, 190, 1], street: [-60, 14, 72] }[name] || [-24, 115, 122];
        cam.position.set(v[0], v[1], v[2]); st.controls.target.set(0, 0, -4);
      },
      stage: st
    };
  }

  /* =================================================================
     Point cloud for clustering and PCA.
     ================================================================= */
  function cloud(container, o) {
    var st = stage(container, { fallback: o.fallback });
    if (!st) return null;
    var scene = st.scene; st.camera.position.set(3.1, 2.3, 3.4); st.controls.target.set(0, 0, 0);
    st.controls.autoRotate = !!o.autoRotate; st.controls.autoRotateSpeed = 0.8;
    scene.add(new T.AmbientLight(0xffffff, 0.75));
    var dl = new T.DirectionalLight(0xffffff, 1.2); dl.position.set(3, 5, 4); scene.add(dl);
    var frameG = new T.Group(); scene.add(frameG);
    var edges = new T.LineSegments(new T.EdgesGeometry(new T.BoxGeometry(2, 2, 2)), new T.LineBasicMaterial({ color: 0x8a9a92, transparent: true, opacity: 0.45 }));
    frameG.add(edges);
    var grid = new T.GridHelper(2, 8, 0x9fb0a8, 0xc5d0ca); grid.position.y = -1; grid.material.transparent = true; grid.material.opacity = 0.35; frameG.add(grid);
    var axisLabels = [];
    function setAxes(names) {
      axisLabels.forEach(function (s) { frameG.remove(s); }); axisLabels = [];
      var pos = [[0.15, -1.18, 1.3], [1.32, -1.15, 0], [-1.3, 0.1, 1.15]];
      names.forEach(function (n, i) {
        var s = label(n, { height: 0.16, bg: dark() ? "rgba(16,32,28,0.88)" : "rgba(255,255,255,0.9)", fg: dark() ? "#e8f2ee" : "#18231F" });
        s.position.set(pos[i][0], pos[i][1], pos[i][2]); frameG.add(s); axisLabels.push(s);
      });
    }
    var n = o.n, geo = new T.SphereGeometry(o.radius || 0.035, 10, 8);
    var mesh = new T.InstancedMesh(geo, new T.MeshStandardMaterial({ roughness: 0.55 }), n);
    mesh.instanceMatrix.setUsage(T.DynamicDrawUsage); scene.add(mesh);
    var cur = new Float32Array(n * 3), from = new Float32Array(n * 3), to = new Float32Array(n * 3), tw = 1, tm = new T.Matrix4();
    var colors = [];
    for (var i = 0; i < n; i++) { mesh.setColorAt(i, new T.Color(0x888888)); }
    function place() {
      for (var i = 0; i < n; i++) { tm.makeTranslation(cur[i * 3], cur[i * 3 + 1], cur[i * 3 + 2]); mesh.setMatrixAt(i, tm); }
      mesh.instanceMatrix.needsUpdate = true;
    }
    function setPositions(P, animate) {
      // P: array of [x, y, z] already scaled to [-1, 1]; three.js y is up, data axis 2 is drawn up
      for (var i = 0; i < n; i++) {
        from[i * 3] = cur[i * 3]; from[i * 3 + 1] = cur[i * 3 + 1]; from[i * 3 + 2] = cur[i * 3 + 2];
        to[i * 3] = P[i][0]; to[i * 3 + 1] = P[i][2]; to[i * 3 + 2] = -P[i][1];
      }
      if (animate) tw = 0; else { cur.set(to); tw = 1; place(); }
    }
    function setColors(C) {
      colors = C;
      for (var i = 0; i < n; i++) mesh.setColorAt(i, new T.Color(C[i]));
      mesh.instanceColor.needsUpdate = true;
    }
    var cents = [], arrows = [];
    function setCentroids(list, cols) {
      cents.forEach(function (c) { scene.remove(c.g); }); cents = [];
      (list || []).forEach(function (p, k) {
        var g = new T.Group();
        var core = new T.Mesh(new T.SphereGeometry(0.11, 4, 2),
          new T.MeshStandardMaterial({ color: new T.Color(cols[k]), emissive: new T.Color(cols[k]), emissiveIntensity: 0.35 }));
        var ring = new T.Mesh(new T.TorusGeometry(0.17, 0.018, 8, 40), new T.MeshBasicMaterial({ color: dark() ? 0xffffff : 0x18231F }));
        g.add(core); g.add(ring); g.position.set(p[0], p[2], -p[1]); scene.add(g);
        cents.push({ g: g, to: g.position.clone(), ring: ring });
      });
    }
    function moveCentroids(list) { list.forEach(function (p, k) { if (cents[k]) cents[k].to = new T.Vector3(p[0], p[2], -p[1]); }); }
    function setArrows(list) {
      arrows.forEach(function (a) { scene.remove(a); }); arrows = [];
      (list || []).forEach(function (a) {
        var g = new T.Group();
        var geo2 = new T.BufferGeometry().setFromPoints([new T.Vector3(0, 0, 0), new T.Vector3(a.v[0], a.v[2], -a.v[1])]);
        g.add(new T.Line(geo2, new T.LineBasicMaterial({ color: dark() ? 0xffd27a : 0x8a3b00 })));
        var s = label(a.name, { height: 0.12, bg: dark() ? "rgba(40,30,10,0.9)" : "rgba(255,246,230,0.95)", fg: dark() ? "#ffd27a" : "#5a2a00" });
        s.position.set(a.v[0] * 1.12, a.v[2] * 1.12, -a.v[1] * 1.12); g.add(s);
        scene.add(g); arrows.push(g);
      });
    }
    var spin = 0;
    st.onFrame(function (dt) {
      if (tw < 1) {
        tw = Math.min(1, tw + dt / 0.9); var k = 1 - Math.pow(1 - tw, 3);
        for (var i = 0; i < n * 3; i++) cur[i] = from[i] + (to[i] - from[i]) * k;
        place();
      }
      spin += dt;
      cents.forEach(function (c) { c.g.position.lerp(c.to, Math.min(1, dt * 3.2)); c.ring.rotation.x = spin * 1.5; c.ring.rotation.y = spin; });
    });
    // hover tooltip
    var ray = new T.Raycaster(), v2 = new T.Vector2();
    st.renderer.domElement.addEventListener("mousemove", function (e) {
      if (!o.tip) return;
      var r = st.renderer.domElement.getBoundingClientRect();
      v2.set((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1);
      ray.setFromCamera(v2, st.camera);
      var h = ray.intersectObject(mesh)[0];
      if (h && h.instanceId !== undefined) NK.Tip.show(o.tip(h.instanceId), e.clientX, e.clientY); else NK.Tip.hide();
    });
    st.renderer.domElement.addEventListener("mouseleave", function () { NK.Tip.hide(); });
    return { setPositions: setPositions, setColors: setColors, setCentroids: setCentroids, moveCentroids: moveCentroids,
      setArrows: setArrows, setAxes: setAxes, autoRotate: function (b) { st.controls.autoRotate = b; }, stage: st };
  }

  /* =================================================================
     Surface of a model's answer over two inputs.
     ================================================================= */
  function surface(container, o) {
    var st = stage(container, { fallback: o.fallback });
    if (!st) return null;
    var scene = st.scene; st.camera.position.set(2.6, 2.1, 2.9); st.controls.target.set(0, -0.1, 0);
    st.controls.autoRotate = true; st.controls.autoRotateSpeed = 0.6;
    scene.add(new T.AmbientLight(0xffffff, 0.7));
    var dl = new T.DirectionalLight(0xffffff, 1.3); dl.position.set(2, 4, 3); scene.add(dl);
    var nx = o.nx, ny = o.ny;
    var geo = new T.PlaneGeometry(2, 2, nx - 1, ny - 1); geo.rotateX(-Math.PI / 2);
    var colArr = new Float32Array(geo.attributes.position.count * 3);
    geo.setAttribute("color", new T.BufferAttribute(colArr, 3));
    var surf = new T.Mesh(geo, new T.MeshStandardMaterial({ vertexColors: true, side: T.DoubleSide, roughness: 0.65, flatShading: true }));
    scene.add(surf);
    var wire = new T.LineSegments(new T.WireframeGeometry(geo), new T.LineBasicMaterial({ color: 0x18231F, transparent: true, opacity: 0.12 }));
    scene.add(wire);
    var frameL = new T.LineSegments(new T.EdgesGeometry(new T.BoxGeometry(2, 1.2, 2)), new T.LineBasicMaterial({ color: 0x8a9a92, transparent: true, opacity: 0.4 }));
    frameL.position.y = -0.4; scene.add(frameL);
    var marker = new T.Mesh(new T.SphereGeometry(0.06, 16, 12), new T.MeshStandardMaterial({ color: 0xffffff, emissive: 0xb8361f, emissiveIntensity: 0.6 }));
    scene.add(marker);
    var stem = new T.Line(new T.BufferGeometry().setFromPoints([new T.Vector3(), new T.Vector3()]), new T.LineBasicMaterial({ color: 0xb8361f }));
    scene.add(stem);
    var labels = [];
    function setLabels(xl, yl, zl) {
      labels.forEach(function (s) { scene.remove(s); }); labels = [];
      var opt = { height: 0.13, bg: dark() ? "rgba(16,32,28,0.9)" : "rgba(255,255,255,0.92)", fg: dark() ? "#e8f2ee" : "#18231F" };
      var a = label(xl, opt); a.position.set(0, -1.1, 1.25); scene.add(a); labels.push(a);
      var b = label(yl, opt); b.position.set(1.3, -1.1, 0); scene.add(b); labels.push(b);
      var c = label(zl, opt); c.position.set(-1.2, 0.35, -1.2); scene.add(c); labels.push(c);
    }
    var zlo = 0, zhi = 1;
    function setGrid(Z, lo, hi) {
      zlo = lo; zhi = hi;
      var pos = geo.attributes.position;
      for (var j = 0; j < ny; j++) for (var i = 0; i < nx; i++) {
        var idx = j * nx + i, z = Z[j][i], k = (z - lo) / (hi - lo || 1);
        pos.setY(idx, -1 + k * 1.2);
        var c = rampColor(k); colArr[idx * 3] = c.r; colArr[idx * 3 + 1] = c.g; colArr[idx * 3 + 2] = c.b;
      }
      pos.needsUpdate = true; geo.attributes.color.needsUpdate = true; geo.computeVertexNormals();
      wire.geometry.dispose(); wire.geometry = new T.WireframeGeometry(geo);
    }
    function setMarker(fx, fy, z) {
      var x = -1 + 2 * fx, zz = 1 - 2 * fy, y = -1 + (z - zlo) / (zhi - zlo || 1) * 1.2;
      marker.position.set(x, y + 0.04, zz);
      stem.geometry.setFromPoints([new T.Vector3(x, -1, zz), new T.Vector3(x, y, zz)]);
    }
    document.addEventListener("nokta:theme", function () { if (o.onTheme) o.onTheme(); });
    return { setGrid: setGrid, setMarker: setMarker, setLabels: setLabels, autoRotate: function (b) { st.controls.autoRotate = b; }, stage: st };
  }

  window.NOKTA3D = { twin: twin, cloud: cloud, surface: surface, seqColor: seqColor, divColor: divColor, label: label, webglOK: webglOK };
})();
