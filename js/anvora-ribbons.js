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
    var s = { t: 0, pinch: 0.42, mx: 0.5, speed: 1, playing: !reduce, bands: +(cv.getAttribute('data-bands') || 16) };
    var pal = PALETTES[cv.getAttribute('data-ribbons')] || PALETTES.original;
    var ctx = cv.getContext('2d'), W = 0, H = 0, dpr = 1;
    function size() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = cv.clientWidth; H = cv.clientHeight;
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
    var tween = window.gsap ? gsap.to(s, { pinch: -0.32, duration: 2.25, ease: 'sine.inOut', yoyo: true, repeat: -1, paused: !s.playing }) : null;
    function tick(time, dt) {
      if (!cv.isConnected) { destroy(); return; }
      if (s.playing) { s.t += (dt / 1000) * s.speed; if (tween) tween.timeScale(s.speed); }
      draw();
    }
    function destroy() { if (window.gsap) gsap.ticker.remove(tick); if (tween) tween.kill(); if (ro) ro.disconnect(); items = items.filter(function (x) { return x.cv !== cv; }); }
    var ro = window.ResizeObserver ? new ResizeObserver(size) : null;
    if (ro) ro.observe(cv); else window.addEventListener('resize', size);
    cv.addEventListener('pointermove', function (e) {
      if (cv.getAttribute('data-follow') === 'off') return;
      var r = cv.getBoundingClientRect(), x = (e.clientX - r.left) / r.width;
      if (window.gsap) gsap.to(s, { mx: x, duration: 0.9, ease: 'power3.out', overwrite: 'auto' }); else s.mx = x;
    });
    cv.addEventListener('pointerleave', function () { if (window.gsap) gsap.to(s, { mx: 0.5, duration: 1.4, ease: 'power3.out', overwrite: 'auto' }); });
    size();
    if (window.gsap) gsap.ticker.add(tick); else (function loop() { if (!cv.isConnected) return; tick(0, 16); requestAnimationFrame(loop); })();
    var api = {
      cv: cv,
      palette: function (name) { if (PALETTES[name]) { pal = PALETTES[name]; draw(); } },
      speed: function (v) { s.speed = v; },
      play: function (on) { s.playing = on; if (tween) tween.paused(!on); },
      playing: function () { return s.playing; }
    };
    return api;
  }
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
