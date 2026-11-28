/* Anvora "Kinetic text": a sequence of short phrases, each with its own animation style, on a soft background.
   Drawn on a 2D canvas so the preview and the MP4 export are identical. Accent words: wrap in *stars*. New line: " / ". */
(function () {
  if (window.anvKT) { window.anvKT.init(); return; }

  var STYLES = [
    ['blurzoom', 'Blur zoom'], ['lettersBlur', 'Letters blur in'], ['wordsRise', 'Words rise'], ['lettersDrop', 'Letters drop'],
    ['lettersRise', 'Letters rise'], ['wordsSlide', 'Words slide in'], ['pop', 'Pop'], ['typewriter', 'Typewriter']
  ];
  var SIZES = [['big', 'Big'], ['medium', 'Medium'], ['small', 'Small']];
  var PALETTES = {
    sunset: [['#E0245E', '#FF7A45'], ['#FF2FB3', '#B84BFF'], ['#6A2CFF', '#3D7BFF'], ['#D81B60', '#8E24AA']],
    anvora: [['#6840FF', '#9C83FF'], ['#6840FF', '#3FB950'], ['#F84131', '#6840FF']],
    mono: [['#151313', '#7A7676']]
  };
  var BGS = { soft: { ink: '#1D1D1F' }, white: { ink: '#1D1D1F' }, dark: { ink: '#F4F4F4' } };
  var FORMATS = { '16x9': [1920, 1080], '9x16': [1080, 1920], '1x1': [1080, 1080] };
  var EXAMPLE = [
    ['Text', 'blurzoom', 'big'], ['Text *Animation*', 'lettersBlur', 'medium'], ['Animate your *text*', 'wordsRise', 'medium'],
    ['Type', 'lettersDrop', 'big'], ['*Adjust*', 'lettersRise', 'big'], ['*Preview*', 'lettersRise', 'big'], ['*Export*', 'lettersRise', 'big'],
    ['Pre-built *animations* / ready to use', 'wordsRise', 'small'], ['For *titles,* *ads,* *social*', 'wordsRise', 'small'],
    ['Boost your *workflow*', 'wordsSlide', 'medium'], ['Focus on *creativity*', 'pop', 'medium'], ['*Build*', 'lettersBlur', 'big'],
    ['*Faster*', 'lettersBlur', 'big'], ['Get *started* now', 'wordsRise', 'medium'], ['anvora.com', 'typewriter', 'small']
  ];
  var FONT = "'Haffer VF', 'Helvetica Neue', Arial, sans-serif";

  function clamp(x, a, b) { return Math.max(a, Math.min(b, x)); }
  function outCubic(x) { return 1 - Math.pow(1 - x, 3); }
  function outExpo(x) { return x >= 1 ? 1 : 1 - Math.pow(2, -10 * x); }
  function outBack(x) { var c = 1.6; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); }
  function hexRgb(h) { var n = parseInt(h.slice(1), 16); return [n >> 16, (n >> 8) & 255, n & 255]; }
  function mixHex(a, b, t) { var x = hexRgb(a), y = hexRgb(b); return 'rgb(' + Math.round(x[0] + (y[0] - x[0]) * t) + ',' + Math.round(x[1] + (y[1] - x[1]) * t) + ',' + Math.round(x[2] + (y[2] - x[2]) * t) + ')'; }

  // ---------- parsing and layout
  function parse(text) {
    return String(text || '').split(/\s\/\s|\n/).map(function (line) {
      return line.trim().split(/\s+/).filter(Boolean).map(function (w) {
        var acc = /^\*.+\*$/.test(w) || /^\*.+\*[,.!?:;]$/.test(w);
        return { text: w.replace(/\*/g, ''), accent: acc };
      });
    }).filter(function (l) { return l.length; });
  }
  function timing(scene, speed) {
    var lines = parse(scene.text), chars = 0, words = 0;
    lines.forEach(function (l) { l.forEach(function (w) { chars += w.text.length; words++; }); });
    var enter;
    switch (scene.style) {
      case 'blurzoom': enter = 0.7; break;
      case 'typewriter': enter = 0.25 + chars * 0.07; break;
      case 'wordsRise': case 'wordsSlide': case 'pop': enter = 0.4 + words * 0.11; break;
      case 'lettersDrop': enter = 0.45 + chars * 0.06; break;
      default: enter = 0.4 + chars * 0.04;
    }
    var hold = clamp(0.3 + chars * 0.02, 0.4, 1.0), exit = scene.style === 'typewriter' ? 0.4 : 0.35;
    return { enter: enter / speed, hold: hold / speed, exit: exit / speed };
  }
  function timeline(scenes, speed) {
    var t = 0.25, out = [];
    scenes.forEach(function (s) {
      if (!String(s.text || '').trim()) return;
      var d = timing(s, speed);
      out.push({ s: s, start: t, enter: d.enter, hold: d.hold, exit: d.exit, end: t + d.enter + d.hold + d.exit });
      t += d.enter + d.hold + d.exit * 0.45;  // next phrase starts while this one blurs away, like the original
    });
    return { items: out, total: t + 0.25 };
  }
  function layout(ctx, scene, W, H, pal, ink, offset) {
    var lines = parse(scene.text), ref = Math.min(H, W * 9 / 16);
    var size = ref * ({ big: 0.26, medium: 0.12, small: 0.072 }[scene.size] || 0.12);
    var weight = scene.size === 'big' ? 600 : 500;
    function setFont(sz) { ctx.font = weight + ' ' + sz + 'px ' + FONT; if ('letterSpacing' in ctx) ctx.letterSpacing = (-0.035 * sz) + 'px'; }
    // shrink to fit the frame
    setFont(size);
    var widest = 0;
    lines.forEach(function (l) { var w = ctx.measureText(l.map(function (x) { return x.text; }).join(' ')).width; widest = Math.max(widest, w); });
    if (widest > W * 0.86) { size *= (W * 0.86) / widest; setFont(size); }
    var lh = size * 1.12, glyphs = [], wordsOut = [], gi = 0, wi = 0, ai = offset || 0;  // each scene starts on the next gradient, so colours change from scene to scene
    var top = H / 2 - ((lines.length - 1) * lh) / 2;
    lines.forEach(function (l, li) {
      var lineText = l.map(function (x) { return x.text; }).join(' '), lw = ctx.measureText(lineText).width, x = W / 2 - lw / 2, y = top + li * lh;
      var cursor = 0;
      l.forEach(function (w, k) {
        var prefix = l.slice(0, k).map(function (x) { return x.text; }).join(' ') + (k ? ' ' : '');
        var wx = x + ctx.measureText(prefix).width, ww = ctx.measureText(w.text).width;
        var grad = w.accent ? pal[ai++ % pal.length] : null;
        var word = { x0: wx, x1: wx + ww, y: y, grad: grad, idx: wi, glyphs: [] };
        for (var c = 0; c < w.text.length; c++) {
          var gx = wx + ctx.measureText(w.text.slice(0, c)).width;
          var g = { ch: w.text[c], x: gx, y: y, w: ctx.measureText(w.text[c]).width, word: word, idx: gi++, char: cursor++ };
          word.glyphs.push(g); glyphs.push(g);
        }
        cursor++; wordsOut.push(word); wi++;
      });
    });
    return { glyphs: glyphs, words: wordsOut, size: size, font: weight + ' ' + size + 'px ' + FONT, ink: ink, lines: lines.length, cx: W / 2, cy: H / 2 };
  }

  // ---------- drawing
  function fillFor(ctx, g, L) {
    if (!g.word.grad) return L.ink;
    var gr = ctx.createLinearGradient(g.word.x0, 0, g.word.x1, 0);
    gr.addColorStop(0, g.word.grad[0]); gr.addColorStop(1, g.word.grad[1]); return gr;
  }
  function solidFor(g, L) {
    if (!g.word.grad) return L.ink;
    var t = (g.x + g.w / 2 - g.word.x0) / Math.max(1, g.word.x1 - g.word.x0); return mixHex(g.word.grad[0], g.word.grad[1], clamp(t, 0, 1));
  }
  var hasFilter = null, blurScale = 1; // blur is in screen pixels, so it is scaled with the preview size
  function glyph(ctx, g, L, o) {
    if (o.a <= 0.003) return;
    var blur = (o.blur || 0) * blurScale, x = g.x + (o.dx || 0), y = g.y + (o.dy || 0);
    ctx.save(); ctx.globalAlpha = clamp(o.a, 0, 1); ctx.font = L.font; ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
    if ('letterSpacing' in ctx) ctx.letterSpacing = '0px';
    if (o.scale && o.scale !== 1) { var px = o.ox != null ? o.ox : g.x + g.w / 2, py = o.oy != null ? o.oy : g.y; ctx.translate(px, py); ctx.scale(o.scale, o.scale); ctx.translate(-px, -py); }
    if (hasFilter === null) { hasFilter = typeof ctx.filter === 'string'; }
    if (o.smear) { // vertical motion blur: faint copies trailing behind the letter
      var n = 6; ctx.fillStyle = solidFor(g, L);
      for (var i = n; i >= 1; i--) { ctx.globalAlpha = clamp(o.a, 0, 1) * 0.12 * (1 - i / (n + 1)); ctx.fillText(g.ch, x, y - o.smear * i / n); }
      ctx.globalAlpha = clamp(o.a, 0, 1);
    }
    if (blur > 0.4 && hasFilter) { ctx.filter = 'blur(' + blur.toFixed(1) + 'px)'; ctx.fillStyle = fillFor(ctx, g, L); ctx.fillText(g.ch, x, y); }
    else if (blur > 0.4) { ctx.shadowColor = solidFor(g, L); ctx.shadowBlur = blur * 2; ctx.shadowOffsetX = 20000; ctx.fillStyle = '#000'; ctx.fillText(g.ch, x - 20000, y); }
    else { ctx.fillStyle = fillFor(ctx, g, L); ctx.fillText(g.ch, x, y); }
    ctx.restore();
  }
  function drawScene(ctx, it, L, t, W, H) {
    var lt = t - it.start, sty = it.s.style, sz = L.size, k = it.enter; // k = enter length
    var ex = clamp((t - (it.start + it.enter + it.hold)) / it.exit, 0, 1), exE = outCubic(ex);
    var exitA = 1 - exE, exitBlur = 18 * exE * (sz / 100), exitDy = -0.12 * sz * exE;
    if (sty === 'typewriter') { exitBlur = 0; exitDy = 0; }
    var G = L.glyphs, n = G.length, words = L.words;
    function prog(delay, dur) { return clamp((lt - delay) / dur, 0, 1); }
    if (sty === 'typewriter') {
      var per = (k - 0.25) / Math.max(1, n), shown = Math.floor(clamp((lt - 0.2) / per, 0, n));
      G.forEach(function (g, i) { if (i < shown) glyph(ctx, g, L, { a: exitA }); });
      var last = shown > 0 ? G[shown - 1] : null, cx = last ? last.x + last.w + sz * 0.06 : (G[0] ? G[0].x : W / 2), cy = last ? last.y : (G[0] ? G[0].y : H / 2);
      var typing = shown < n, blink = typing || Math.floor(lt / 0.45) % 2 === 0;
      if (blink && exitA > 0.01) { ctx.save(); ctx.globalAlpha = exitA; ctx.fillStyle = (L.pal[0] || ['#E0245E'])[0]; ctx.fillRect(cx, cy - sz * 0.48, Math.max(2, sz * 0.07), sz * 0.96); ctx.restore(); }
      return;
    }
    G.forEach(function (g, i) {
      var o = { a: 1, blur: 0, dx: 0, dy: 0 }, e;
      switch (sty) {
        case 'blurzoom':
          e = outExpo(prog(0, k)); o.a = clamp(e * 1.4, 0, 1); o.blur = 30 * (1 - e) * (sz / 100); o.scale = 1 + 0.55 * (1 - e); o.ox = L.cx; o.oy = L.cy; break;
        case 'lettersBlur':
          e = outCubic(prog(i * 0.035, 0.45)); o.a = e; o.blur = 16 * (1 - e) * (sz / 100); o.dx = sz * 0.12 * (1 - e); break;
        case 'lettersRise':
          e = outExpo(prog(i * 0.04, 0.6)); o.a = clamp(e * 1.3, 0, 1); o.blur = 14 * (1 - e) * (sz / 100); o.dy = sz * 0.55 * (1 - e); break;
        case 'lettersDrop':
          e = outCubic(prog(i * 0.06, 0.5)); o.a = clamp(e * 1.6, 0, 1); o.dy = -sz * 0.9 * (1 - e); o.smear = sz * 0.9 * (1 - e) * 0.8; o.blur = 4 * (1 - e); break;
        case 'wordsRise':
          e = outCubic(prog(g.word.idx * 0.11, 0.5)); o.a = e; o.blur = 10 * (1 - e) * (sz / 100); o.dy = sz * 0.45 * (1 - e); break;
        case 'wordsSlide':
          e = outExpo(prog(g.word.idx * 0.11, 0.6)); o.a = e; o.blur = 12 * (1 - e) * (sz / 100); o.dx = sz * 0.9 * (1 - e); break;
        case 'pop':
          e = prog(g.word.idx * 0.11, 0.45); o.a = clamp(e * 2, 0, 1); o.scale = 0.55 + 0.45 * outBack(e); o.ox = (g.word.x0 + g.word.x1) / 2; o.oy = g.y; o.blur = 6 * (1 - e); break;
      }
      o.a *= exitA; o.blur += exitBlur; o.dy += exitDy;
      glyph(ctx, g, L, o);
    });
  }
  function background(ctx, W, H, bg, t, cache) {
    var key = W + 'x' + H + bg;
    if (!cache.bg || cache.key !== key) {
      var c = document.createElement('canvas'); c.width = Math.round(W * 1.1); c.height = Math.round(H * 1.1); var x = c.getContext('2d'), cw = c.width, ch = c.height;
      if (bg === 'dark') {
        x.fillStyle = '#151313'; x.fillRect(0, 0, cw, ch);
        [[0.1, 0.1, '#6840FF', 0.22], [0.9, 0.9, '#6840FF', 0.18], [0.92, 0.08, '#A1FF62', 0.06]].forEach(function (b) { var r = x.createRadialGradient(cw * b[0], ch * b[1], 0, cw * b[0], ch * b[1], Math.max(cw, ch) * 0.55); r.addColorStop(0, hexA(b[2], b[3])); r.addColorStop(1, hexA(b[2], 0)); x.fillStyle = r; x.fillRect(0, 0, cw, ch); });
      } else if (bg === 'white') { x.fillStyle = '#FFFFFF'; x.fillRect(0, 0, cw, ch); }
      else {
        x.fillStyle = '#ECECEE'; x.fillRect(0, 0, cw, ch);
        [[0.0, 0.0, '#DDEFC2', 0.9], [1.0, 0.1, '#D7E9F2', 0.9], [0.05, 1.0, '#D9EEF0', 0.8], [0.95, 0.95, '#E6F2C8', 0.9], [0.5, 0.5, '#F2F2F4', 0.9]].forEach(function (b) {
          var r = x.createRadialGradient(cw * b[0], ch * b[1], 0, cw * b[0], ch * b[1], Math.max(cw, ch) * (b[0] === 0.5 ? 0.38 : 0.5)); r.addColorStop(0, hexA(b[2], b[3])); r.addColorStop(1, hexA(b[2], 0)); x.fillStyle = r; x.fillRect(0, 0, cw, ch);
        });
        // fine grain
        var img = x.getImageData(0, 0, cw, ch), d = img.data;
        for (var i = 0; i < d.length; i += 4) { var nz = (Math.random() - 0.5) * 10; d[i] += nz; d[i + 1] += nz; d[i + 2] += nz; }
        x.putImageData(img, 0, 0);
      }
      cache.bg = c; cache.key = key;
    }
    var dx = Math.sin(t * 0.35) * W * 0.02 - W * 0.05, dy = Math.cos(t * 0.27) * H * 0.02 - H * 0.05;
    ctx.drawImage(cache.bg, dx, dy);
  }
  function hexA(h, a) { var c = hexRgb(h); return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + a + ')'; }

  function Engine(cv) {
    var ctx = cv.getContext('2d'), cache = {}, layouts = {};
    return {
      ctx: ctx,
      frame: function (st, TL, t, W, H) {
        background(ctx, W, H, st.bg, t, cache);
        var pal = PALETTES[st.palette], ink = BGS[st.bg].ink;
        for (var i = 0; i < TL.items.length; i++) {
          var it = TL.items[i]; if (t < it.start || t > it.end) continue;
          var key = it.s.text + '|' + it.s.size + '|' + W + 'x' + H + '|' + st.palette + '|' + st.bg;
          var L = layouts[key + '|' + i] || (layouts[key + '|' + i] = layout(ctx, it.s, W, H, pal, ink, i)); L.pal = pal;
          drawScene(ctx, it, L, t, W, H);
        }
      }
    };
  }

  // ---------- MP4 export (frame by frame, 60 fps)
  var MUXER_URL = 'https://cdn.jsdelivr.net/npm/mp4-muxer@5.1.3/build/mp4-muxer.min.js';
  function loadMuxer() {
    if (window.Mp4Muxer) return Promise.resolve();
    return new Promise(function (ok, fail) { var s = document.createElement('script'); s.src = MUXER_URL; s.onload = function () { window.Mp4Muxer ? ok() : fail(); }; s.onerror = fail; document.head.appendChild(s); });
  }
  var chan = window.MessageChannel ? new MessageChannel() : null, waiting = [];
  if (chan) chan.port1.onmessage = function () { var f = waiting.shift(); if (f) f(); };
  function yieldNow() { return new Promise(function (r) { if (chan) { waiting.push(r); chan.port2.postMessage(0); } else setTimeout(r, 0); }); }
  async function pickCodec(w, h, fps, bitrate) {
    var list = ['avc1.64002A', 'avc1.640033', 'avc1.4D002A', 'avc1.4D0033', 'avc1.640028'];
    for (var i = 0; i < list.length; i++) { try { var s = await VideoEncoder.isConfigSupported({ codec: list[i], width: w, height: h, bitrate: bitrate, framerate: fps }); if (s.supported) return list[i]; } catch (e) {} }
    return null;
  }
  async function exportMp4(st, onProgress) {
    if (!window.VideoEncoder || !window.VideoFrame) throw new Error('unsupported');
    var f = FORMATS[st.format], w = f[0], h = f[1], fps = 60, bitrate = 12000000;
    var TL = timeline(st.scenes, st.speed), total = Math.round(TL.total * fps);
    var codec = await pickCodec(w, h, fps, bitrate); if (!codec) throw new Error('codec');
    await loadMuxer();
    var c = document.createElement('canvas'); c.width = w; c.height = h; var eng = Engine(c);
    var muxer = new Mp4Muxer.Muxer({ target: new Mp4Muxer.ArrayBufferTarget(), video: { codec: 'avc', width: w, height: h, frameRate: fps }, fastStart: 'in-memory' });
    var failed = null;
    var enc = new VideoEncoder({ output: function (chunk, meta) { muxer.addVideoChunk(chunk, meta); }, error: function (e) { failed = e; } });
    enc.configure({ codec: codec, width: w, height: h, bitrate: bitrate, framerate: fps, avc: { format: 'avc' } });
    for (var i = 0; i < total; i++) {
      if (failed) throw failed;
      eng.frame(st, TL, i / fps, w, h);
      var fr = new VideoFrame(c, { timestamp: Math.round(i * 1e6 / fps), duration: Math.round(1e6 / fps) });
      enc.encode(fr, { keyFrame: i % fps === 0 }); fr.close();
      while (enc.encodeQueueSize > 6) await yieldNow();
      if (i % 8 === 0) { onProgress(i / total); await yieldNow(); }
    }
    await enc.flush(); enc.close(); muxer.finalize();
    return { blob: new Blob([muxer.target.buffer], { type: 'video/mp4' }), len: total / fps };
  }

  // ---------- widget
  function opts(list, val) { return list.map(function (o) { return '<option value="' + o[0] + '"' + (o[0] === val ? ' selected' : '') + '>' + o[1] + '</option>'; }).join(''); }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;'); }
  function fmt(s) { return (Math.floor(s / 60)) + ':' + String(Math.floor(s % 60)).padStart(2, '0'); }

  function Widget(root) {
    var cv = root.querySelector('[data-kt-canvas]'), stage = root.querySelector('.anv-kt__stage');
    var st = { scenes: EXAMPLE.map(function (e) { return { text: e[0], style: e[1], size: e[2] }; }), palette: 'sunset', bg: 'soft', speed: 1, format: '16x9', playing: true, clock: 0, scrubbing: false };
    var eng = Engine(cv), TL = timeline(st.scenes, st.speed);
    var list = root.querySelector('[data-kt-scenes]'), scrub = root.querySelector('[data-kt-scrub]'), timeEl = root.querySelector('[data-kt-time]'), playBtn = root.querySelector('[data-kt-play]');
    function rebuild() { TL = timeline(st.scenes, st.speed); root.querySelector('[data-kt-total]').textContent = TL.total.toFixed(1) + ' s'; }
    function renderList() {
      list.innerHTML = st.scenes.map(function (s, i) {
        return '<div class="anv-kt-row" data-i="' + i + '"><span class="anv-kt-row__n">' + String(i + 1).padStart(2, '0') + '</span>' +
          '<input type="text" value="' + esc(s.text) + '" data-k="text" aria-label="Text for scene ' + (i + 1) + '" maxlength="60">' +
          '<select data-k="style" aria-label="Animation style">' + opts(STYLES, s.style) + '</select>' +
          '<select data-k="size" aria-label="Text size">' + opts(SIZES, s.size) + '</select>' +
          '<button type="button" data-kt-jump title="Preview this scene" aria-label="Preview scene ' + (i + 1) + '">▶</button>' +
          '<button type="button" data-kt-up title="Move up" aria-label="Move scene up"' + (i ? '' : ' disabled') + '>↑</button>' +
          '<button type="button" data-kt-del title="Remove" aria-label="Remove scene">✕</button></div>';
      }).join('');
      rebuild();
    }
    function size() {
      var f = FORMATS[st.format], dpr = Math.min(window.devicePixelRatio || 1, 2);
      stage.style.aspectRatio = f[0] + ' / ' + f[1]; stage.setAttribute('data-format', st.format);
      var cw = cv.clientWidth || 800; cv.width = Math.round(cw * dpr); cv.height = Math.round(cw * f[1] / f[0] * dpr);
    }
    function tick(time, dt) {
      if (!cv.isConnected) { if (window.gsap) gsap.ticker.remove(tick); return; }
      if (st.playing) { st.clock = (st.clock + (dt || 16) / 1000) % TL.total; scrub.value = Math.round(st.clock / TL.total * 1000); }
      timeEl.textContent = fmt(st.clock) + ' / ' + fmt(TL.total);
      // preview is drawn at a 1920-wide reference size and scaled, so it matches the export exactly
      var f = FORMATS[st.format], k = cv.width / f[0];
      blurScale = k; eng.ctx.setTransform(k, 0, 0, k, 0, 0); eng.frame(st, TL, st.clock, f[0], f[1]); eng.ctx.setTransform(1, 0, 0, 1, 0, 0); blurScale = 1;
    }
    renderList(); size();
    if (window.ResizeObserver) new ResizeObserver(size).observe(cv);
    var fontsReady = document.fonts ? Promise.all(["500 80px 'Haffer VF'", "600 80px 'Haffer VF'"].map(function (f) { return document.fonts.load(f); })).catch(function () {}) : Promise.resolve();
    fontsReady.then(function () { if (window.gsap) gsap.ticker.add(tick); else (function loop() { if (!cv.isConnected) return; tick(0, 16); requestAnimationFrame(loop); })(); });

    list.addEventListener('input', function (e) {
      var row = e.target.closest('.anv-kt-row'); if (!row) return; var i = +row.getAttribute('data-i'), k = e.target.getAttribute('data-k');
      st.scenes[i][k] = e.target.value; rebuild();
      if (k !== 'text') jump(i); // jump to a scene when its style/size changes
    });
    list.addEventListener('change', function (e) { if (e.target.tagName === 'SELECT') { var row = e.target.closest('.anv-kt-row'); jump(+row.getAttribute('data-i')); } });
    function jump(i) {
      var it = TL.items.filter(function (x) { return x.s === st.scenes[i]; })[0]; if (!it) return;
      st.clock = Math.max(0, it.start - 0.05); st.playing = true; playBtn.textContent = 'Pause';
    }
    root.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b || !root.contains(b)) return;
      var row = b.closest('.anv-kt-row'), i = row ? +row.getAttribute('data-i') : -1;
      if (b.hasAttribute('data-kt-del')) { st.scenes.splice(i, 1); if (!st.scenes.length) st.scenes.push({ text: 'Your *text*', style: 'wordsRise', size: 'medium' }); renderList(); }
      else if (b.hasAttribute('data-kt-up') && i > 0) { var s = st.scenes.splice(i, 1)[0]; st.scenes.splice(i - 1, 0, s); renderList(); }
      else if (b.hasAttribute('data-kt-jump')) jump(i);
      else if (b.hasAttribute('data-kt-add')) {
        if (st.scenes.length >= 25) return;
        st.scenes.push({ text: 'New *scene*', style: STYLES[st.scenes.length % STYLES.length][0], size: 'medium' }); renderList();
        var inp = list.querySelector('.anv-kt-row:last-child input'); if (inp) { inp.focus(); inp.select(); } jump(st.scenes.length - 1);
      }
      else if (b.hasAttribute('data-kt-example')) { st.scenes = EXAMPLE.map(function (e) { return { text: e[0], style: e[1], size: e[2] }; }); renderList(); st.clock = 0; }
      else if (b.hasAttribute('data-kt-shuffle')) { st.scenes.forEach(function (s) { s.style = STYLES[Math.floor(Math.random() * STYLES.length)][0]; }); renderList(); st.clock = 0; }
      else if (b.hasAttribute('data-kt-play')) { st.playing = !st.playing; b.textContent = st.playing ? 'Pause' : 'Play'; }
      else if (b.hasAttribute('data-kt-palette') || b.hasAttribute('data-kt-bg') || b.hasAttribute('data-kt-speed')) {
        var attr = b.hasAttribute('data-kt-palette') ? 'data-kt-palette' : b.hasAttribute('data-kt-bg') ? 'data-kt-bg' : 'data-kt-speed';
        var v = b.getAttribute(attr);
        if (attr === 'data-kt-palette') st.palette = v; else if (attr === 'data-kt-bg') st.bg = v; else { st.speed = +v; rebuild(); }
        Array.prototype.forEach.call(root.querySelectorAll('[' + attr + ']'), function (x) { x.classList.toggle('is--on', x === b); });
      }
      else if (b.hasAttribute('data-kt-export')) doExport(b);
    });
    root.addEventListener('input', function (e) { if (e.target === scrub) { st.playing = false; playBtn.textContent = 'Play'; st.clock = (+scrub.value / 1000) * TL.total; } });
    root.addEventListener('change', function (e) { if (e.target.hasAttribute('data-kt-format')) { st.format = e.target.value; size(); } });
    function doExport(b) {
      if (b.disabled) return;
      var status = root.querySelector('[data-kt-status]'), bar = root.querySelector('[data-kt-progress]'), label = b.textContent, t0 = performance.now();
      b.disabled = true; b.textContent = 'Making video… 0%'; status.textContent = 'Drawing every frame at 60 fps. Longer videos take a little longer.';
      exportMp4(st, function (p) { b.textContent = 'Making video… ' + Math.round(p * 100) + '%'; bar.style.transform = 'scaleX(' + p + ')'; })
        .then(function (res) {
          var a = document.createElement('a'); a.href = URL.createObjectURL(res.blob); a.download = 'anvora-kinetic-text-' + st.format + '.mp4';
          document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(a.href); }, 10000);
          status.textContent = 'Saved: ' + res.len.toFixed(2) + ' seconds, 60 fps, MP4 (' + (Math.round(res.blob.size / 1048576 * 10) / 10) + ' MB). Made in ' + Math.round((performance.now() - t0) / 1000) + 's.';
        }, function () { status.textContent = 'This browser can’t make MP4 videos. Please use the latest Chrome, Edge or Safari.'; })
        .then(function () { b.disabled = false; b.textContent = label; bar.style.transform = 'scaleX(0)'; });
    }
  }
  function init() { Array.prototype.forEach.call(document.querySelectorAll('[data-kt]:not([data-kt-init])'), function (el) { el.setAttribute('data-kt-init', '1'); Widget(el); }); }
  window.anvKT = { init: init, _timeline: timeline };
  init();
})();
