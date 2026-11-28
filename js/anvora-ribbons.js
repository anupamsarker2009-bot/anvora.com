/* Anvora "flowing ribbons": thick vertical ribbons that pinch and bow, drift sideways and shimmer.
   Drawn on <canvas data-ribbons="palette">, animated with GSAP (gsap.ticker + tweens). No video files. */
(function () {
  if (window.anvRibbons) { window.anvRibbons.init(); return; }
  var PALETTES = {
    original: ['#7A00F5', '#E10FB0', '#F78AD6', '#FCD7F0', '#FFFFFF', '#B347FF', '#F2A6E3'],
    brand: ['#6840FF', '#A1FF62', '#F4F4F4', '#151313', '#F84131', '#9C83FF', '#FFFFFF'],
    night: ['#6840FF', '#151313', '#2A2626', '#9C83FF', '#3B1FB0', '#A1FF62', '#201D1D'],
    ocean: ['#0B3BFF', '#00C2FF', '#BDF4FF', '#FFFFFF', '#5B2BFF', '#7FE3FF', '#1C1C6B']
  };
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var items = [];

  function Ribbons(cv) {
    var s = { t: 0, pinch: 0.42, mx: 0.5, speed: 1, playing: !reduce || cv.hasAttribute('data-force-play'), bands: +(cv.getAttribute('data-bands') || 16) };
    var palName = PALETTES[cv.getAttribute('data-ribbons')] ? cv.getAttribute('data-ribbons') : 'original', pal = PALETTES[palName];
    var ctx = cv.getContext('2d'), W = 0, H = 0, dpr = 1;
    function size() {
      // fixed-size canvases (used for video export) set data-w / data-h and data-dpr
      dpr = cv.hasAttribute('data-dpr') ? +cv.getAttribute('data-dpr') : Math.min(window.devicePixelRatio || 1, 2);
      W = +cv.getAttribute('data-w') || cv.clientWidth; H = +cv.getAttribute('data-h') || cv.clientHeight;
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw();
    }
    function draw() {
      if (!W || !H) return;
      var n = s.bands, sp = W / (n - 1), cx = W * s.mx;
      var shift = s.t * 26 * (W / 900), idx = Math.floor(shift / sp), frac = shift - idx * sp;
      var m = pal.length, flow = (s.t * 55) % H;
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = pal[3] || '#fff'; ctx.fillRect(0, 0, W, H);
      ctx.lineCap = 'butt';
      for (var i = -2; i <= n + 1; i++) {
        var base = i * sp + frac - sp;
        var ctrl = base + (cx - base) * s.pinch * 2;
        var id = i - idx, ci = ((id * 3) % m + m) % m;
        var rnd = Math.abs(Math.sin(id * 12.9898) * 43758.5453) % 1;   // stable per ribbon, so neighbours never line up
        var y0 = ((flow * (0.7 + rnd * 0.6) + rnd * H) % H) - H;
        var g = ctx.createLinearGradient(0, y0, 0, y0 + 2 * H);
        for (var k = 0; k <= 2 * m; k++) g.addColorStop(k / (2 * m), pal[(ci + k) % m]);
        ctx.strokeStyle = g; ctx.lineWidth = sp * 1.04 + 1;
        ctx.beginPath(); ctx.moveTo(base, -20); ctx.quadraticCurveTo(ctrl, H / 2, base, H + 20); ctx.stroke();
      }
    }
    // GSAP drives the motion: a yoyo "pinch" tween and the ticker for drift and shimmer
    var fixedClock = cv.hasAttribute('data-force-play') ? performance.now() : 0;
    var tween = !fixedClock && window.gsap ? gsap.to(s, { pinch: -0.32, duration: 2.25, ease: 'sine.inOut', yoyo: true, repeat: -1, paused: !s.playing }) : null;
    function tick(time, dt) {
      if (!cv.isConnected) { destroy(); return; }
      if (fixedClock) {  // export canvas: every frame is computed from real elapsed time, so the video is correct even if frames arrive unevenly
        var el = (performance.now() - fixedClock) / 1000 * s.speed;
        s.t = el; s.pinch = 0.05 + 0.37 * Math.cos(Math.PI * el / 2.25);
      } else if (s.playing) { s.t += (dt / 1000) * s.speed; if (tween) tween.timeScale(s.speed); }
      draw();
    }
    function destroy() { if (window.gsap) gsap.ticker.remove(tick); if (tween) tween.kill(); if (ro) ro.disconnect(); items = items.filter(function (x) { return x.cv !== cv; }); }
    var manual = cv.hasAttribute('data-manual');
    var ro = !manual && window.ResizeObserver ? new ResizeObserver(size) : null;
    if (ro) ro.observe(cv); else if (!manual) window.addEventListener('resize', size);
    cv.addEventListener('pointermove', function (e) {
      if (cv.getAttribute('data-follow') === 'off') return;
      var r = cv.getBoundingClientRect(), x = (e.clientX - r.left) / r.width;
      if (window.gsap) gsap.to(s, { mx: x, duration: 0.9, ease: 'power3.out', overwrite: 'auto' }); else s.mx = x;
    });
    cv.addEventListener('pointerleave', function () { if (window.gsap) gsap.to(s, { mx: 0.5, duration: 1.4, ease: 'power3.out', overwrite: 'auto' }); });
    size();
    if (manual) { if (tween) tween.kill(); } else if (window.gsap) gsap.ticker.add(tick); else (function loop() { if (!cv.isConnected) return; tick(0, 16); requestAnimationFrame(loop); })();
    var api = {
      cv: cv,
      palette: function (name) { if (PALETTES[name]) { palName = name; pal = PALETTES[name]; draw(); } },
      palName: function () { return palName; },
      speedVal: function () { return s.speed; },
      speed: function (v) { s.speed = v; },
      play: function (on) { s.playing = on; if (tween) tween.paused(!on); },
      playing: function () { return s.playing; },
      // draw the exact frame for time t (seconds); same motion as the live GSAP tween (sine yoyo between 0.42 and -0.32 every 2.25s)
      renderAt: function (t) { var e = t * s.speed; s.t = e; s.pinch = 0.05 + 0.37 * Math.cos(Math.PI * e / 2.25); draw(); }
    };
    return api;
  }
  // ---------- 15-second video export: a fixed-size copy of the animation is recorded with MediaRecorder
  var FORMATS = { '16x9': [1920, 1080, 16], '9x16': [1080, 1920, 9], '1x1': [1080, 1080, 11] };
  var recording = false;
  function pickType() {
    if (!window.MediaRecorder) return null;
    var types = ['video/mp4;codecs=avc1.640028', 'video/mp4;codecs=avc1.42E01F', 'video/mp4', 'video/webm;codecs=vp9', 'video/webm;codecs=vp8', 'video/webm'];
    for (var i = 0; i < types.length; i++) if (MediaRecorder.isTypeSupported(types[i])) return types[i];
    return null;
  }
  function record(src, fmt, secs, ui) {
    var type = pickType(), f = FORMATS[fmt] || FORMATS['16x9'];
    if (!type || !HTMLCanvasElement.prototype.captureStream) { ui.status('Your browser can’t record video. Please try the latest Chrome, Edge or Safari.'); return; }
    if (recording) return;
    recording = true;
    var c = document.createElement('canvas');
    c.setAttribute('data-ribbons', src.palName()); c.setAttribute('data-bands', f[2]);
    c.setAttribute('data-w', f[0]); c.setAttribute('data-h', f[1]); c.setAttribute('data-dpr', '1');
    c.setAttribute('data-follow', 'off'); c.setAttribute('data-force-play', ''); c.setAttribute('data-ribbons-init', '1');
    c.style.cssText = 'position:fixed;left:-20000px;top:0;width:' + f[0] + 'px;height:' + f[1] + 'px;pointer-events:none';
    document.body.appendChild(c);
    var r = Ribbons(c); items.push(r); r.speed(src.speedVal());
    var stream = c.captureStream(30), chunks = [];
    var rec = new MediaRecorder(stream, { mimeType: type, videoBitsPerSecond: 16000000 });
    rec.ondataavailable = function (e) { if (e.data && e.data.size) chunks.push(e.data); };
    rec.onstop = function () {
      var ext = type.indexOf('mp4') >= 0 ? 'mp4' : 'webm';
      var blob = new Blob(chunks, { type: type.split(';')[0] });
      var a = document.createElement('a'); a.href = URL.createObjectURL(blob);
      a.download = 'anvora-animation-' + fmt + '-' + secs + 's.' + ext;
      document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(a.href); }, 10000);
      c.remove(); recording = false;
      ui.done(ext, Math.round(blob.size / 1048576 * 10) / 10);
    };
    var t0 = performance.now();
    rec.start(500);
    (function count() {
      var left = Math.max(0, secs - (performance.now() - t0) / 1000);
      ui.progress(1 - left / secs, Math.ceil(left));
      if (left > 0) setTimeout(count, 200); else rec.stop();
    })();
  }
  var MUXER_URL = 'https://cdn.jsdelivr.net/npm/mp4-muxer@5.1.3/build/mp4-muxer.min.js';
  function loadMuxer() {
    if (window.Mp4Muxer) return Promise.resolve();
    return new Promise(function (ok, fail) {
      var s = document.createElement('script'); s.src = MUXER_URL; s.onload = function () { window.Mp4Muxer ? ok() : fail(); }; s.onerror = fail;
      document.head.appendChild(s);
    });
  }
  // yields to the browser without timers, so export keeps going even if the tab is in the background
  var chan = window.MessageChannel ? new MessageChannel() : null, waiting = [];
  if (chan) chan.port1.onmessage = function () { var f = waiting.shift(); if (f) f(); };
  function yieldNow() { return new Promise(function (r) { if (chan) { waiting.push(r); chan.port2.postMessage(0); } else setTimeout(r, 0); }); }
  async function pickCodec(w, h, fps, bitrate) {
    var list = ['avc1.64002A', 'avc1.640033', 'avc1.4D002A', 'avc1.4D0033', 'avc1.640028'];
    for (var i = 0; i < list.length; i++) {
      try { var s = await VideoEncoder.isConfigSupported({ codec: list[i], width: w, height: h, bitrate: bitrate, framerate: fps }); if (s.supported) return list[i]; } catch (e) {}
    }
    return null;
  }
  async function exportMp4(src, fmt, secs, ui) {
    var f = FORMATS[fmt] || FORMATS['16x9'], w = f[0], h = f[1], fps = 60, total = Math.round(secs * fps), bitrate = 14000000;
    var codec = await pickCodec(w, h, fps, bitrate);
    if (!codec) throw new Error('codec');
    await loadMuxer();
    var c = document.createElement('canvas');
    c.setAttribute('data-ribbons', src.palName()); c.setAttribute('data-bands', f[2]); c.setAttribute('data-manual', '');
    c.setAttribute('data-w', w); c.setAttribute('data-h', h); c.setAttribute('data-dpr', '1'); c.setAttribute('data-ribbons-init', '1');
    var r = Ribbons(c); r.speed(src.speedVal());
    var muxer = new Mp4Muxer.Muxer({ target: new Mp4Muxer.ArrayBufferTarget(), video: { codec: 'avc', width: w, height: h, frameRate: fps }, fastStart: 'in-memory' });
    var failed = null;
    var enc = new VideoEncoder({ output: function (chunk, meta) { muxer.addVideoChunk(chunk, meta); }, error: function (e) { failed = e; } });
    enc.configure({ codec: codec, width: w, height: h, bitrate: bitrate, framerate: fps, avc: { format: 'avc' } });
    for (var i = 0; i < total; i++) {
      if (failed) throw failed;
      r.renderAt(i / fps);
      var frame = new VideoFrame(c, { timestamp: Math.round(i * 1e6 / fps), duration: Math.round(1e6 / fps) });
      enc.encode(frame, { keyFrame: i % (fps * 2) === 0 });
      frame.close();
      while (enc.encodeQueueSize > 6) await yieldNow();
      if (i % 10 === 0) { ui.render(i / total); await yieldNow(); }
    }
    await enc.flush(); enc.close();
    muxer.finalize();
    return new Blob([muxer.target.buffer], { type: 'video/mp4' });
  }
  function save(blob, name) {
    var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(a.href); }, 10000);
  }
  window.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-rb-record]'); if (!b) return;
    if (b.disabled) return;
    if (window.VideoEncoder && window.VideoFrame && !b.hasAttribute('data-rb-live')) {
      var wrap0 = b.closest('[data-rb-controls]'), src0 = target(b); if (!src0) return;
      var sel0 = wrap0.querySelector('[data-rb-format]'), st0 = wrap0.querySelector('[data-rb-status]'), bar0 = wrap0.querySelector('[data-rb-progress]');
      var fmt0 = sel0 ? sel0.value : '16x9', secs0 = +(b.getAttribute('data-rb-record') || 15), label0 = b.textContent, t0 = performance.now();
      b.disabled = true; b.textContent = 'Making video… 0%';
      if (st0) st0.textContent = 'Drawing every frame (60 per second). This usually takes 10 to 40 seconds.';
      exportMp4(src0, fmt0, secs0, { render: function (p) { b.textContent = 'Making video… ' + Math.round(p * 100) + '%'; if (bar0) bar0.style.transform = 'scaleX(' + p + ')'; } })
        .then(function (blob) {
          b.disabled = false; b.textContent = label0; if (bar0) bar0.style.transform = 'scaleX(0)';
          save(blob, 'anvora-animation-' + fmt0 + '-' + secs0 + 's.mp4');
          if (st0) st0.textContent = 'Saved: exactly ' + secs0 + ' seconds, 60 fps, MP4 (' + (Math.round(blob.size / 1048576 * 10) / 10) + ' MB). Made in ' + Math.round((performance.now() - t0) / 1000) + 's.';
        }, function () {
          if (st0) st0.textContent = 'Couldn’t make an MP4 in this browser, so it will record live instead.';
          b.disabled = false; b.textContent = label0; if (bar0) bar0.style.transform = 'scaleX(0)';
          b.setAttribute('data-rb-live', ''); b.click(); b.removeAttribute('data-rb-live');
        });
      return;
    }
    var wrap = b.closest('[data-rb-controls]'), src = target(b); if (!src) return;
    var sel = wrap.querySelector('[data-rb-format]'), st = wrap.querySelector('[data-rb-status]'), bar = wrap.querySelector('[data-rb-progress]');
    var label = b.textContent, secs = +(b.getAttribute('data-rb-record') || 15);
    var ui = {
      status: function (t) { if (st) st.textContent = t; },
      progress: function (p, left) { b.disabled = true; b.textContent = 'Recording… ' + left + 's'; if (bar) bar.style.transform = 'scaleX(' + p + ')'; if (st) st.textContent = 'Keep this tab open and visible until it finishes.'; },
      done: function (ext, mb) {
        b.disabled = false; b.textContent = label; if (bar) bar.style.transform = 'scaleX(0)';
        if (st) st.textContent = 'Saved as .' + ext + ' (' + mb + ' MB).' + (ext === 'webm' ? ' Instagram needs MP4: open it in a free converter or record in Safari/Edge for MP4.' : '');
      }
    };
    record(src, sel ? sel.value : '16x9', secs, ui);
  });
  function find(el) { for (var i = 0; i < items.length; i++) if (items[i].cv === el) return items[i]; return null; }
  function init() {
    Array.prototype.forEach.call(document.querySelectorAll('canvas[data-ribbons]:not([data-ribbons-init])'), function (cv) {
      cv.setAttribute('data-ribbons-init', '1'); items.push(Ribbons(cv));
    });
  }
  // controls: [data-rb-target="#id"] with data-rb-palette / data-rb-speed / data-rb-pause / data-rb-follow
  function target(el) { var w = el.closest('[data-rb-controls]'); return w ? find(document.querySelector(w.getAttribute('data-rb-controls'))) : null; }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-rb-palette],[data-rb-pause],[data-rb-follow]'); if (!b) return;
    var r = target(b); if (!r) return;
    if (b.hasAttribute('data-rb-palette')) {
      r.palette(b.getAttribute('data-rb-palette'));
      Array.prototype.forEach.call(b.parentNode.querySelectorAll('[data-rb-palette]'), function (x) { x.classList.toggle('is--on', x === b); });
    } else if (b.hasAttribute('data-rb-pause')) {
      r.play(!r.playing()); b.textContent = r.playing() ? 'Pause' : 'Play';
    } else {
      var off = r.cv.getAttribute('data-follow') === 'off';
      r.cv.setAttribute('data-follow', off ? 'on' : 'off'); b.classList.toggle('is--on', off); b.textContent = off ? 'Follow mouse: on' : 'Follow mouse: off';
    }
  });
  document.addEventListener('input', function (e) {
    var t = e.target; if (!t.hasAttribute || !t.hasAttribute('data-rb-speed')) return;
    var r = target(t); if (r) r.speed(parseFloat(t.value));
  });
  window.anvRibbons = { init: init };
  init();
})();
