/* Anvora social media posts: each post is drawn on a 1080x1350 canvas, so the JPG download matches the preview exactly. */
(function () {
  if (window.anvPosts) return;
  var W = 1080, H = 1350, P = 84, TOTAL = 12;
  var C = { purple: '#6840FF', electric: '#A1FF62', coral: '#F84131', dark: '#201D1D', ink: '#151313', light: '#F4F4F4', white: '#FFFFFF', card: '#2A2626' };
  var XH = "'Haffer XH', Arial, sans-serif", VF = "'Haffer VF', Arial, sans-serif", MONO = "'Haffer Mono', 'Courier New', monospace";
  var MARK = new Path2D("__MARK__");
  var HANDLE = '@thumbnailanvora';

  function setFont(c, f, s, w) { c.font = (w || 400) + ' ' + s + 'px ' + f; }
  function ls(c, v) { if ('letterSpacing' in c) c.letterSpacing = v + 'px'; }
  function wrap(c, str, maxW) {
    var out = [];
    str.split('\n').forEach(function (par) {
      var line = '';
      par.split(' ').forEach(function (w) {
        var t = line ? line + ' ' + w : w;
        if (c.measureText(t).width > maxW && line) { out.push(line); line = w; } else line = t;
      });
      out.push(line);
    });
    return out;
  }
  // draws text with its top edge at y and returns the bottom y
  function text(c, str, x, y, o) {
    setFont(c, o.f || VF, o.size, o.w); ls(c, o.ls || 0);
    c.fillStyle = o.color; c.textAlign = o.align || 'left'; c.textBaseline = 'alphabetic';
    var lines = wrap(c, str, o.maxW || W - 2 * P), lh = o.size * (o.lh || 1.25);
    lines.forEach(function (l, i) { c.fillText(l, x, y + o.size * 0.78 + i * lh); });
    ls(c, 0);
    return y + (lines.length - 1) * lh + o.size * 1.0;
  }
  // big display headline that shrinks until it fits
  function head(c, str, x, y, o) {
    var s = o.size, maxW = o.maxW || W - 2 * P;
    while (s > 40) {
      setFont(c, XH, s, 400); ls(c, -s * 0.045);
      var lines = wrap(c, str, maxW);
      var wide = lines.some(function (l) { return c.measureText(l).width > maxW; });
      if (!wide && (!o.maxLines || lines.length <= o.maxLines)) break;
      s -= 4;
    }
    return text(c, str, x, y, { f: XH, size: s, ls: -s * 0.045, lh: o.lh || 0.98, color: o.color, maxW: maxW, align: o.align });
  }
  function rr(c, x, y, w, h, r) {
    c.beginPath();
    if (c.roundRect) c.roundRect(x, y, w, h, r);
    else { c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }
  }
  function pill(c, label, x, y, o) {
    var s = o.size || 24;
    setFont(c, MONO, s, 400); ls(c, 1.5);
    var w = c.measureText(label.toUpperCase()).width + s * 1.6, h = s * 2.1;
    if (o.align === 'right') x -= w;
    rr(c, x, y, w, h, h / 2);
    if (o.fill) { c.fillStyle = o.fill; c.fill(); }
    if (o.stroke) { c.strokeStyle = o.stroke; c.lineWidth = 2; c.stroke(); }
    c.fillStyle = o.color; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText(label.toUpperCase(), x + w / 2, y + h / 2 + 1);
    ls(c, 0); c.textBaseline = 'alphabetic';
    return w;
  }
  function mark(c, x, y, size, color) {
    c.save(); c.translate(x, y); var k = size / 1426; c.scale(k, k); c.fillStyle = color; c.fill(MARK); c.restore();
  }
  function alpha(hex, a) {
    var n = parseInt(hex.slice(1), 16); return 'rgba(' + (n >> 16) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + a + ')';
  }
  // shared frame: tag top-left, number top-right, brand bar at the bottom
  function frame(c, o) {
    c.fillStyle = o.bg; c.fillRect(0, 0, W, H);
    if (o.draw) o.draw();
    if (o.tag) pill(c, o.tag, P, P, { stroke: alpha(o.fg, 0.45), color: o.fg });
    setFont(c, MONO, 24, 400); ls(c, 1.5); c.fillStyle = alpha(o.footFg || o.fg, 0.6); c.textAlign = 'right';
    if (!o.noNum) { c.fillStyle = alpha(o.fg, 0.6); c.fillText(String(o.n).padStart(2, '0') + ' / ' + TOTAL, W - P, P + 34); }
    ls(c, 0);
    var fg = o.footFg || o.fg, ly = H - P - 84;
    c.fillStyle = alpha(fg, 0.25); c.fillRect(P, ly, W - 2 * P, 2);
    mark(c, P, H - P - 46, 50, fg);
    setFont(c, VF, 44, 700); ls(c, -1.5); c.fillStyle = fg; c.textAlign = 'left'; c.fillText('anvora', P + 66, H - P - 4); ls(c, 0);
    setFont(c, MONO, 24, 400); ls(c, 1); c.fillStyle = alpha(fg, 0.7); c.textAlign = 'right'; c.fillText(HANDLE, W - P, H - P - 10); ls(c, 0);
  }
  function rows(c, items, y, o) {
    items.forEach(function (t, i) {
      c.fillStyle = alpha(o.color, 0.25); c.fillRect(P, y, W - 2 * P, 2);
      setFont(c, MONO, 26, 400); c.fillStyle = o.num || o.color; c.textAlign = 'left'; c.fillText(String(i + 1).padStart(2, '0'), P, y + 62);
      y = text(c, t, P + 110, y + 36, { size: o.size || 40, w: 500, color: o.color, maxW: W - 2 * P - 110, lh: 1.2 }) + 36;
    });
    c.fillStyle = alpha(o.color, 0.25); c.fillRect(P, y, W - 2 * P, 2);
    return y;
  }

  var POSTS = {
    intro: function (c) {
      frame(c, { n: 1, bg: C.purple, fg: C.white, tag: 'Hello, world', draw: function () { mark(c, W - P - 250, 170, 250, C.electric); } });
      var y = head(c, 'Marketing\nbuilt to grow.', P, 450, { size: 168, color: C.white });
      text(c, 'Anvora is a new marketing company for ambitious small businesses. Strategy, content and ads under one roof.', P, y + 44, { size: 38, color: alpha(C.white, 0.85), maxW: 820, lh: 1.35 });
    },
    promise: function (c) {
      frame(c, { n: 2, bg: C.electric, fg: C.dark, tag: 'Our promise' });
      var y = head(c, 'We’re new.\nHere’s what you\ncan count on.', P, 200, { size: 120, color: C.dark });
      rows(c, ['Honest monthly reports, including what didn’t work.', 'Your ad accounts and your data stay yours. Always.', 'No guaranteed miracles. Just steady, measurable work.'], y + 70, { color: C.dark, num: C.purple });
    },
    founding: function (c) {
      frame(c, { n: 3, bg: C.coral, fg: C.white, tag: 'Now open', draw: function () {
        c.fillStyle = alpha(C.white, 0.12); c.beginPath(); c.arc(W - 40, 360, 300, 0, Math.PI * 2); c.fill(); } });
      var y = head(c, 'Now welcoming\nfounding\nclients.', P, 200, { size: 160, color: C.white });
      y = text(c, 'A small number of businesses.\nA reduced founding rate.\nExtra attention from day one.', P, y + 56, { size: 42, w: 500, color: C.white, lh: 1.3 });
      pill(c, 'Apply via the link in bio →', P, y + 50, { fill: C.white, color: C.dark, size: 28 });
    },
    'tip-google': function (c) {
      frame(c, { n: 4, bg: C.ink, fg: C.light, tag: 'Marketing tip' });
      var y = head(c, '3 signs your Google profile is costing you customers', P, 200, { size: 104, color: C.light, maxLines: 4 });
      y += 60;
      ['Your opening hours are out of date', 'Your newest photo is over a year old', 'Reviews sit there with no reply'].forEach(function (t, i) {
        rr(c, P, y, W - 2 * P, 132, 22); c.fillStyle = C.card; c.fill();
        setFont(c, XH, 72, 400); c.fillStyle = C.electric; c.textAlign = 'left'; c.fillText(String(i + 1), P + 36, y + 94);
        text(c, t, P + 130, y + 46, { size: 38, w: 500, color: C.light, maxW: W - 2 * P - 170 });
        y += 150;
      });
    },
    principle: function (c) {
      frame(c, { n: 5, bg: C.light, fg: C.dark, tag: 'How we think', draw: function () {
        var cx = W - P - 150, cy = H - P - 84 - 210;
        c.fillStyle = C.purple; c.beginPath(); c.arc(cx, cy, 150, 0, Math.PI * 2); c.fill();
        mark(c, cx - 70, cy - 65, 140, C.white); } });
      var y = head(c, 'Goals\nbefore\ntactics.', P, 220, { size: 200, color: C.dark });
      text(c, 'We start with what your business needs to achieve. Then we pick the channels. Never the other way round.', P, y + 50, { size: 38, color: alpha(C.dark, 0.7), maxW: 560, lh: 1.35 });
    },
    audit: function (c) {
      frame(c, { n: 6, bg: C.purple, fg: C.white, tag: 'Free' });
      var y = head(c, 'Get a free\nmarketing audit', P, 200, { size: 130, color: C.white });
      var cy = y + 60, ch = 430;
      rr(c, P, cy, W - 2 * P, ch, 28); c.fillStyle = C.white; c.fill();
      setFont(c, MONO, 22, 400); ls(c, 1.5); c.fillStyle = alpha(C.dark, 0.55); c.textAlign = 'left'; c.fillText('SAMPLE REPORT', P + 40, cy + 58); ls(c, 0);
      var rx = P + 190, ry = cy + 250;
      c.lineWidth = 26; c.lineCap = 'round';
      c.strokeStyle = '#EAEAEA'; c.beginPath(); c.arc(rx, ry, 120, 0, Math.PI * 2); c.stroke();
      c.strokeStyle = C.purple; c.beginPath(); c.arc(rx, ry, 120, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * 0.65); c.stroke();
      setFont(c, XH, 96, 400); c.fillStyle = C.dark; c.textAlign = 'center'; c.fillText('65', rx, ry + 30);
      setFont(c, MONO, 22, 400); c.fillStyle = alpha(C.dark, 0.55); c.fillText('/ 100', rx, ry + 66);
      var bx = P + 380, bw = W - 2 * P - 380 - 40, by = cy + 110;
      [['Website', 81], ['Paid ads', 58], ['SEO', 64], ['Social', 77], ['Email', 46]].forEach(function (b, i) {
        var yy = by + i * 62;
        setFont(c, VF, 28, 500); c.fillStyle = C.dark; c.textAlign = 'left'; c.fillText(b[0], bx, yy + 10);
        rr(c, bx + 150, yy - 6, bw - 150, 16, 8); c.fillStyle = '#EAEAEA'; c.fill();
        rr(c, bx + 150, yy - 6, (bw - 150) * b[1] / 100, 16, 8); c.fillStyle = C.purple; c.fill();
      });
      text(c, 'Clear scores and your top opportunities. Free, with no strings attached.', P, cy + ch + 40, { size: 34, color: alpha(C.white, 0.85), maxW: 860, lh: 1.3 });
    },
    services: function (c) {
      frame(c, { n: 7, bg: C.ink, fg: C.light, tag: 'Services' });
      var y = head(c, 'What we do', P, 200, { size: 150, color: C.light });
      var items = [['Brand Strategy', C.purple, C.white], ['Performance Marketing', C.card, C.light], ['Social Media', C.card, C.light],
                   ['Content Studio', C.electric, C.dark], ['SEO & Growth', C.card, C.light], ['Web & Landing Pages', C.coral, C.white]];
      var gx = 24, cw = (W - 2 * P - gx) / 2, chh = 176, top = y + 70;
      items.forEach(function (it, i) {
        var x = P + (i % 2) * (cw + gx), yy = top + Math.floor(i / 2) * (chh + gx);
        rr(c, x, yy, cw, chh, 22); c.fillStyle = it[1]; c.fill();
        setFont(c, MONO, 22, 400); c.fillStyle = alpha(it[2], 0.6); c.textAlign = 'left'; c.fillText(String(i + 1).padStart(2, '0'), x + 30, yy + 50);
        text(c, it[0], x + 30, yy + chh - 30 - (it[0].length > 18 ? 84 : 42), { size: 38, w: 500, color: it[2], maxW: cw - 60, lh: 1.1 });
      });
    },
    myth: function (c) {
      var half = 640;
      frame(c, { n: 8, bg: C.electric, fg: C.light, footFg: C.dark, draw: function () { c.fillStyle = C.ink; c.fillRect(0, 0, W, half); } });
      pill(c, 'Myth', P, P, { fill: C.coral, color: C.white });
      var y = head(c, 'You need to post every single day.', P, 210, { size: 104, color: C.light, maxLines: 3 });
      c.strokeStyle = C.coral; c.lineWidth = 10; c.lineCap = 'round';
      c.beginPath(); c.moveTo(P, y + 40); c.lineTo(P + 260, y + 40); c.stroke();
      pill(c, 'Fact', P, half + 64, { fill: C.dark, color: C.electric });
      var y2 = head(c, 'Consistency beats volume.', P, half + 170, { size: 96, color: C.dark, maxLines: 2 });
      text(c, 'Three thoughtful posts a week will do more for you than seven rushed ones.', P, y2 + 34, { size: 36, color: alpha(C.dark, 0.75), maxW: 820, lh: 1.3 });
    },
    process: function (c) {
      frame(c, { n: 9, bg: C.light, fg: C.dark, tag: 'Our process' });
      var y = head(c, 'How we work', P, 200, { size: 140, color: C.dark }) + 70;
      var steps = [['Discover', 'A free call and audit to understand your goals.'], ['Plan', 'Channels, budget, timeline and the numbers we track.'],
                   ['Launch', 'We build your brand, content and campaigns.'], ['Improve', 'Weekly tweaks and a clear monthly review.']];
      var gap = 168;
      c.fillStyle = alpha(C.purple, 0.3); c.fillRect(P + 39, y + 40, 3, gap * 3);
      steps.forEach(function (s, i) {
        var yy = y + i * gap;
        c.fillStyle = C.purple; c.beginPath(); c.arc(P + 40, yy + 40, 40, 0, Math.PI * 2); c.fill();
        setFont(c, MONO, 26, 400); c.fillStyle = C.white; c.textAlign = 'center'; c.fillText(String(i + 1).padStart(2, '0'), P + 40, yy + 49);
        text(c, s[0], P + 120, yy + 4, { size: 46, w: 600, color: C.dark });
        text(c, s[1], P + 120, yy + 66, { size: 32, color: alpha(C.dark, 0.65), maxW: W - 2 * P - 120 });
      });
    },
    'five-second-test': function (c) {
      frame(c, { n: 10, bg: C.coral, fg: C.white, tag: 'Website tip' });
      var y = head(c, 'The 5-second\nhomepage test', P, 200, { size: 132, color: C.white });
      y = text(c, 'Show your homepage to someone for five seconds. Then ask them:', P, y + 44, { size: 38, color: C.white, maxW: 820, lh: 1.3 }) + 44;
      ['What does this business do?', 'Who is it for?', 'What should I do next?'].forEach(function (t) {
        rr(c, P, y, W - 2 * P, 116, 22); c.fillStyle = C.white; c.fill();
        c.fillStyle = C.purple; c.beginPath(); c.arc(P + 62, y + 58, 26, 0, Math.PI * 2); c.fill();
        c.strokeStyle = C.white; c.lineWidth = 6; c.lineCap = 'round'; c.lineJoin = 'round';
        c.beginPath(); c.moveTo(P + 50, y + 59); c.lineTo(P + 59, y + 68); c.lineTo(P + 75, y + 50); c.stroke();
        text(c, t, P + 116, y + 36, { size: 40, w: 500, color: C.dark });
        y += 136;
      });
    },
    'coffee-shop': function (c) {
      frame(c, { n: 11, bg: C.electric, fg: C.dark, tag: 'Example approach' });
      var y = head(c, 'How we’d market a local coffee shop', P, 200, { size: 112, color: C.dark, maxLines: 3 }) + 54;
      [['Weeks 1–2', 'Get found on Google Maps'], ['Weeks 3–4', 'Film a month of short videos'], ['Weeks 5–8', 'Launch a loyalty stamp card'], ['Weeks 9–12', 'Small, local ads nearby']].forEach(function (r) {
        rr(c, P, y, W - 2 * P, 104, 20); c.fillStyle = C.dark; c.fill();
        setFont(c, MONO, 22, 400); ls(c, 1.5); c.fillStyle = C.electric; c.textAlign = 'left'; c.fillText(r[0].toUpperCase(), P + 32, y + 60); ls(c, 0);
        text(c, r[1], P + 250, y + 32, { size: 36, w: 500, color: C.light, maxW: W - 2 * P - 280 });
        y += 120;
      });
      text(c, 'Example plan, not a past client. Full plan on our website.', P, y + 16, { size: 28, color: alpha(C.dark, 0.7) });
    },
    question: function (c) {
      frame(c, { n: 12, bg: C.purple, fg: C.white, tag: 'Your turn' });
      var y = head(c, 'What’s your\nbiggest marketing\nheadache?', P, 200, { size: 124, color: C.white }) + 60;
      [['A', 'Not enough leads'], ['B', 'No time for content'], ['C', 'Ads that don’t pay off']].forEach(function (o) {
        rr(c, P, y, W - 2 * P, 104, 52); c.strokeStyle = alpha(C.white, 0.5); c.lineWidth = 2; c.stroke();
        c.fillStyle = C.electric; c.beginPath(); c.arc(P + 52, y + 52, 30, 0, Math.PI * 2); c.fill();
        setFont(c, MONO, 26, 500); c.fillStyle = C.dark; c.textAlign = 'center'; c.fillText(o[0], P + 52, y + 61);
        text(c, o[1], P + 110, y + 32, { size: 38, w: 500, color: C.white });
        y += 122;
      });
      setFont(c, MONO, 26, 400); ls(c, 1.5); c.fillStyle = C.electric; c.textAlign = 'left'; c.fillText('TELL US IN THE COMMENTS', P, y + 40); ls(c, 0);
    }
  };

  var fontsReady = null;
  function loadFonts() {
    if (!fontsReady) fontsReady = Promise.all([
      document.fonts.load("400 100px 'Haffer XH'"), document.fonts.load("500 40px 'Haffer VF'"), document.fonts.load("700 40px 'Haffer VF'"),
      document.fonts.load("400 24px 'Haffer Mono'"), document.fonts.load("500 24px 'Haffer Mono'")
    ]).catch(function () {});
    return fontsReady;
  }
  function render() {
    var list = document.querySelectorAll('canvas[data-post]:not([data-drawn])');
    if (!list.length) return;
    list.forEach(function (cv) { cv.setAttribute('data-drawn', 'pending'); });
    loadFonts().then(function () {
      list.forEach(function (cv) {
        var fn = POSTS[cv.getAttribute('data-post')];
        if (!fn) return;
        cv.width = W; cv.height = H;
        var c = cv.getContext('2d'); c.clearRect(0, 0, W, H); fn(c);
        cv.setAttribute('data-drawn', '1');
      });
    });
  }
  function download(id) {
    var cv = document.querySelector('canvas[data-post="' + id + '"]');
    if (!cv) return;
    var n = String(Array.prototype.indexOf.call(document.querySelectorAll('canvas[data-post]'), cv) + 1).padStart(2, '0');
    cv.toBlob(function (b) {
      var a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'anvora-post-' + n + '-' + id + '.jpg';
      document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
    }, 'image/jpeg', 0.95);
  }
  document.addEventListener('click', function (e) {
    var d = e.target.closest && e.target.closest('[data-download]');
    if (d) {
      e.preventDefault();
      var id = d.getAttribute('data-download');
      if (id === 'all') {
        Array.prototype.forEach.call(document.querySelectorAll('canvas[data-post]'), function (cv, i) {
          setTimeout(function () { download(cv.getAttribute('data-post')); }, i * 450);
        });
      } else download(id);
      return;
    }
    var cp = e.target.closest && e.target.closest('[data-copy-caption]');
    if (cp) {
      var src = document.getElementById(cp.getAttribute('data-copy-caption'));
      var done = function () { var t = cp.textContent; cp.textContent = 'Copied!'; setTimeout(function () { cp.textContent = t; }, 1400); };
      if (src && navigator.clipboard) navigator.clipboard.writeText(src.innerText).then(done, done); else done();
    }
  });
  window.anvPosts = { render: render, download: download };
  render();
})();
