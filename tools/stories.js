/* Anvora Instagram Stories: each story is drawn on a 1080x1920 canvas, so the JPG download matches the preview exactly.
   Key content stays between y=380 and y=1580, clear of Instagram's profile bar (top) and reply bar (bottom). */
(function () {
  if (window.anvStories) return;
  var W = 1080, H = 1920, P = 96;
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
  function text(c, str, x, y, o) {
    setFont(c, o.f || VF, o.size, o.w); ls(c, o.ls || 0);
    c.fillStyle = o.color; c.textAlign = o.align || 'left'; c.textBaseline = 'alphabetic';
    var lines = wrap(c, str, o.maxW || W - 2 * P), lh = o.size * (o.lh || 1.25);
    lines.forEach(function (l, i) { c.fillText(l, x, y + o.size * 0.78 + i * lh); });
    ls(c, 0);
    return y + (lines.length - 1) * lh + o.size * 1.0;
  }
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
    var s = o.size || 26;
    setFont(c, MONO, s, 400); ls(c, 1.5);
    var w = c.measureText(label.toUpperCase()).width + s * 1.6, h = s * 2.1;
    if (o.align === 'right') x -= w;
    if (o.align === 'center') x -= w / 2;
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
  function check(c, x, y, r, bg, fg) {
    c.fillStyle = bg; c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill();
    c.strokeStyle = fg; c.lineWidth = r * 0.24; c.lineCap = 'round'; c.lineJoin = 'round';
    c.beginPath(); c.moveTo(x - r * 0.42, y + r * 0.02); c.lineTo(x - r * 0.1, y + r * 0.34); c.lineTo(x + r * 0.46, y - r * 0.34); c.stroke();
  }
  // shared frame: logo + tag along the top (below Instagram's profile bar), handle at the bottom
  function frame(c, o) {
    c.fillStyle = o.bg; c.fillRect(0, 0, W, H);
    if (o.draw) o.draw();
    var fg = o.fg, top = 238;
    mark(c, P, top, 56, fg);
    setFont(c, VF, 46, 700); ls(c, -1.5); c.fillStyle = fg; c.textAlign = 'left'; c.fillText('anvora', P + 72, top + 46); ls(c, 0);
    if (o.tag) pill(c, o.tag, W - P, top - 2, { align: 'right', stroke: alpha(fg, 0.45), color: fg, size: 24 });
    var bf = o.footFg || fg;
    c.fillStyle = alpha(bf, 0.25); c.fillRect(P, 1636, W - 2 * P, 2);
    setFont(c, MONO, 26, 400); ls(c, 1.5); c.fillStyle = alpha(bf, 0.75);
    c.textAlign = 'left'; c.fillText(HANDLE, P, 1690);
    c.textAlign = 'right'; c.fillText(String(o.n).padStart(2, '0') + ' / 12', W - P, 1690); ls(c, 0);
  }
  function auditCard(c, y, ch) {
    rr(c, P, y, W - 2 * P, ch, 32); c.fillStyle = C.white; c.fill();
    setFont(c, MONO, 24, 400); ls(c, 1.5); c.fillStyle = alpha(C.dark, 0.55); c.textAlign = 'left'; c.fillText('SAMPLE REPORT', P + 44, y + 66); ls(c, 0);
    var rx = W / 2, ry = y + 250;
    c.lineWidth = 30; c.lineCap = 'round';
    c.strokeStyle = '#EAEAEA'; c.beginPath(); c.arc(rx, ry, 130, 0, Math.PI * 2); c.stroke();
    c.strokeStyle = C.purple; c.beginPath(); c.arc(rx, ry, 130, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * 0.65); c.stroke();
    setFont(c, XH, 104, 400); c.fillStyle = C.dark; c.textAlign = 'center'; c.fillText('65', rx, ry + 32);
    setFont(c, MONO, 24, 400); c.fillStyle = alpha(C.dark, 0.55); c.fillText('/ 100', rx, ry + 72);
    var bx = P + 44, bw = W - 2 * P - 88, by = y + 470;
    [['Website', 81], ['Paid ads', 58], ['SEO', 64], ['Social', 77], ['Email', 46]].forEach(function (b, i) {
      var yy = by + i * 60;
      setFont(c, VF, 30, 500); c.fillStyle = C.dark; c.textAlign = 'left'; c.fillText(b[0], bx, yy + 11);
      rr(c, bx + 180, yy - 6, bw - 180, 18, 9); c.fillStyle = '#EAEAEA'; c.fill();
      rr(c, bx + 180, yy - 6, (bw - 180) * b[1] / 100, 18, 9); c.fillStyle = C.purple; c.fill();
    });
  }

  var STORIES = {
    hello: function (c) {
      frame(c, { n: 1, bg: C.purple, fg: C.white, tag: 'Hello', draw: function () {
        c.fillStyle = alpha(C.white, 0.08); c.beginPath(); c.arc(W / 2, 740, 330, 0, Math.PI * 2); c.fill();
        mark(c, W / 2 - 230, 528, 460, C.electric); } });
      var y = head(c, 'Hi, we’re\nAnvora.', P, 1110, { size: 176, color: C.white });
      text(c, 'A new marketing company for ambitious small businesses.', P, y + 40, { size: 44, color: alpha(C.white, 0.85), maxW: 840, lh: 1.3 });
    },
    founding: function (c) {
      frame(c, { n: 2, bg: C.coral, fg: C.white, tag: 'Now open', draw: function () {
        c.fillStyle = alpha(C.white, 0.12); c.beginPath(); c.arc(W - 30, 560, 280, 0, Math.PI * 2); c.fill(); } });
      var y = head(c, 'Founding\nclient spots\nnow open.', P, 420, { size: 168, color: C.white }) + 80;
      ['A reduced founding rate', 'Extra attention from day one', 'Honest feedback in return'].forEach(function (t) {
        rr(c, P, y, W - 2 * P, 128, 26); c.fillStyle = C.white; c.fill();
        check(c, P + 66, y + 64, 30, C.coral, C.white);
        text(c, t, P + 124, y + 42, { size: 42, w: 500, color: C.dark, maxW: W - 2 * P - 150 });
        y += 148;
      });
      pill(c, 'Tap the link to apply', P, y + 30, { fill: C.dark, color: C.white, size: 30 });
    },
    audit: function (c) {
      frame(c, { n: 3, bg: C.electric, fg: C.dark, tag: 'Free' });
      var y = head(c, 'Get a free\nmarketing audit.', P, 420, { size: 150, color: C.dark });
      auditCard(c, y + 60, 780);
    },
    poll: function (c) {
      frame(c, { n: 4, bg: C.light, fg: C.dark, tag: 'Quick poll' });
      var y = head(c, 'Do you reply to every Google review?', P, 420, { size: 140, color: C.dark, maxLines: 4 }) + 80;
      var gw = (W - 2 * P - 24) / 2, ch = 380;
      [['Yes, always', C.purple, C.white], ['Not yet', C.dark, C.electric]].forEach(function (o, i) {
        var x = P + i * (gw + 24);
        rr(c, x, y, gw, ch, 32); c.fillStyle = o[1]; c.fill();
        setFont(c, MONO, 26, 400); ls(c, 1.5); c.fillStyle = alpha(o[2], 0.7); c.textAlign = 'left'; c.fillText(i ? 'B' : 'A', x + 40, y + 70); ls(c, 0);
        head(c, o[0], x + 40, y + ch - 40 - 2 * 76, { size: 80, color: o[2], maxW: gw - 80, maxLines: 2 });
      });
      text(c, 'Replying shows customers you care, and Google notices too.', P, y + ch + 50, { size: 38, color: alpha(C.dark, 0.7), maxW: 860, lh: 1.3 });
    },
    'tip-phone': function (c) {
      frame(c, { n: 5, bg: C.ink, fg: C.light, tag: 'One-minute tip' });
      setFont(c, XH, 240, 400); ls(c, -10); c.fillStyle = C.electric; c.textAlign = 'left'; c.fillText('01', P - 8, 600); ls(c, 0);
      var y = head(c, 'Put your phone number at the top of every page.', P, 660, { size: 108, color: C.light, maxLines: 4 });
      y = text(c, 'Most mobile visitors won’t scroll to find it. Make calling you a one-tap job.', P, y + 40, { size: 38, color: alpha(C.light, 0.7), maxW: 860, lh: 1.3 }) + 60;
      rr(c, P, y, W - 2 * P, 150, 28); c.fillStyle = C.card; c.fill();
      c.fillStyle = C.purple; c.beginPath(); c.arc(P + 75, y + 75, 32, 0, Math.PI * 2); c.fill();
      rr(c, P + 135, y + 52, 230, 18, 9); c.fillStyle = alpha(C.light, 0.35); c.fill();
      rr(c, P + 135, y + 84, 150, 14, 7); c.fillStyle = alpha(C.light, 0.18); c.fill();
      rr(c, W - P - 250, y + 40, 210, 70, 35); c.fillStyle = C.electric; c.fill();
      setFont(c, VF, 30, 600); c.fillStyle = C.dark; c.textAlign = 'center'; c.fillText('Call us', W - P - 145, y + 86);
    },
    myth: function (c) {
      var half = 1000;
      frame(c, { n: 6, bg: C.electric, fg: C.light, footFg: C.dark, tag: 'Myth vs fact', draw: function () { c.fillStyle = C.ink; c.fillRect(0, 0, W, half); } });
      pill(c, 'Myth', P, 420, { fill: C.coral, color: C.white, size: 28 });
      var y = head(c, 'You need to post every single day.', P, 530, { size: 116, color: C.light, maxLines: 3 });
      c.strokeStyle = C.coral; c.lineWidth = 12; c.lineCap = 'round';
      c.beginPath(); c.moveTo(P, y + 46); c.lineTo(P + 300, y + 46); c.stroke();
      pill(c, 'Fact', P, half + 80, { fill: C.dark, color: C.electric, size: 28 });
      var y2 = head(c, 'Consistency beats volume.', P, half + 190, { size: 116, color: C.dark, maxLines: 2 });
      text(c, 'Three thoughtful posts a week will do more for you than seven rushed ones.', P, y2 + 40, { size: 40, color: alpha(C.dark, 0.75), maxW: 860, lh: 1.3 });
    },
    services: function (c) {
      frame(c, { n: 7, bg: C.purple, fg: C.white, tag: 'Services' });
      var y = head(c, 'What we do', P, 420, { size: 160, color: C.white }) + 70;
      ['Brand Strategy', 'Performance Marketing', 'Social Media', 'Content Studio', 'SEO & Growth', 'Web & Landing Pages'].forEach(function (t, i) {
        c.fillStyle = alpha(C.white, 0.3); c.fillRect(P, y, W - 2 * P, 2);
        setFont(c, MONO, 28, 400); c.fillStyle = C.electric; c.textAlign = 'left'; c.fillText(String(i + 1).padStart(2, '0'), P, y + 84);
        text(c, t, P + 110, y + 44, { size: 54, w: 500, color: C.white, ls: -1 });
        y += 136;
      });
      c.fillStyle = alpha(C.white, 0.3); c.fillRect(P, y, W - 2 * P, 2);
    },
    process: function (c) {
      frame(c, { n: 8, bg: C.light, fg: C.dark, tag: 'Our process' });
      var y = head(c, 'How we\nwork', P, 420, { size: 176, color: C.dark }) + 90;
      var steps = [['Discover', 'A free call and audit to understand your goals.'], ['Plan', 'Channels, budget, timeline and the numbers we track.'],
                   ['Launch', 'We build your brand, content and campaigns.'], ['Improve', 'Weekly tweaks and a clear monthly review.']];
      var gap = 196;
      c.fillStyle = alpha(C.purple, 0.3); c.fillRect(P + 43, y + 44, 3, gap * 3);
      steps.forEach(function (s, i) {
        var yy = y + i * gap;
        c.fillStyle = C.purple; c.beginPath(); c.arc(P + 44, yy + 44, 44, 0, Math.PI * 2); c.fill();
        setFont(c, MONO, 28, 400); c.fillStyle = C.white; c.textAlign = 'center'; c.fillText(String(i + 1).padStart(2, '0'), P + 44, yy + 54);
        text(c, s[0], P + 130, yy + 4, { size: 52, w: 600, color: C.dark });
        text(c, s[1], P + 130, yy + 74, { size: 34, color: alpha(C.dark, 0.65), maxW: W - 2 * P - 130 });
      });
    },
    'first-week': function (c) {
      frame(c, { n: 9, bg: C.ink, fg: C.light, tag: 'Behind the scenes' });
      var y = head(c, 'Your first week with Anvora', P, 420, { size: 124, color: C.light, maxLines: 3 }) + 70;
      [['Mon', 'Kick-off call: goals, budget, numbers'], ['Tue', 'Audit of your site, ads and socials'], ['Wed', 'Competitor and audience research'],
       ['Thu', 'We draft your 90-day plan'], ['Fri', 'We review the plan together']].forEach(function (r, i) {
        rr(c, P, y, W - 2 * P, 124, 24); c.fillStyle = i === 4 ? C.electric : C.card; c.fill();
        setFont(c, MONO, 26, 500); ls(c, 2); c.fillStyle = i === 4 ? C.dark : C.electric; c.textAlign = 'left'; c.fillText(r[0].toUpperCase(), P + 36, y + 72); ls(c, 0);
        text(c, r[1], P + 150, y + 42, { size: 38, w: 500, color: i === 4 ? C.dark : C.light, maxW: W - 2 * P - 180 });
        y += 140;
      });
    },
    'coffee-shop': function (c) {
      frame(c, { n: 10, bg: C.electric, fg: C.dark, tag: 'Example approach' });
      var y = head(c, 'How we’d market a local coffee shop', P, 420, { size: 132, color: C.dark, maxLines: 4 }) + 70;
      [['Weeks 1–2', 'Get found on Google Maps'], ['Weeks 3–4', 'Film a month of short videos'], ['Weeks 5–8', 'Launch a loyalty stamp card'], ['Weeks 9–12', 'Small, local ads nearby']].forEach(function (r) {
        rr(c, P, y, W - 2 * P, 132, 24); c.fillStyle = C.dark; c.fill();
        setFont(c, MONO, 24, 400); ls(c, 1.5); c.fillStyle = C.electric; c.textAlign = 'left'; c.fillText(r[0].toUpperCase(), P + 36, y + 76); ls(c, 0);
        text(c, r[1], P + 270, y + 44, { size: 38, w: 500, color: C.light, maxW: W - 2 * P - 300 });
        y += 150;
      });
      text(c, 'An example plan, not a past client. The full plan is on our website.', P, y + 30, { size: 32, color: alpha(C.dark, 0.7), maxW: 860, lh: 1.3 });
    },
    ask: function (c) {
      frame(c, { n: 11, bg: C.purple, fg: C.white, tag: 'Ask us' });
      var y = head(c, 'Ask us\nanything about\nmarketing.', P, 420, { size: 156, color: C.white }) + 80;
      var bh = 380;
      rr(c, P, y, W - 2 * P, bh, 36); c.fillStyle = C.white; c.fill();
      c.fillStyle = C.purple; c.beginPath(); c.arc(W / 2, y, 58, 0, Math.PI * 2); c.fill();
      mark(c, W / 2 - 30, y - 28, 60, C.white);
      text(c, 'Your question here', W / 2, y + 96, { size: 46, w: 600, color: C.dark, align: 'center' });
      rr(c, P + 50, y + 186, W - 2 * P - 100, 120, 24); c.fillStyle = '#EFEFEF'; c.fill();
      text(c, 'Ads, SEO, content, pricing…', W / 2, y + 230, { size: 34, color: alpha(C.dark, 0.45), align: 'center' });
      text(c, 'We’ll answer the best ones in our next stories.', P, y + bh + 50, { size: 40, color: alpha(C.white, 0.85), maxW: 860, lh: 1.3 });
    },
    'five-second-test': function (c) {
      frame(c, { n: 12, bg: C.coral, fg: C.white, tag: 'Save this' });
      var y = head(c, 'The 5-second\nhomepage test', P, 420, { size: 148, color: C.white, maxLines: 2 });
      y = text(c, 'Show your homepage to someone for five seconds. Then ask:', P, y + 50, { size: 42, color: C.white, maxW: 860, lh: 1.3 }) + 60;
      ['What does this business do?', 'Who is it for?', 'What should I do next?'].forEach(function (t) {
        rr(c, P, y, W - 2 * P, 132, 26); c.fillStyle = C.white; c.fill();
        check(c, P + 68, y + 66, 30, C.purple, C.white);
        text(c, t, P + 126, y + 44, { size: 42, w: 500, color: C.dark, maxW: W - 2 * P - 150 });
        y += 152;
      });
      text(c, 'Can’t answer all three? Your homepage needs work.', P, y + 30, { size: 38, w: 500, color: C.white, maxW: 860, lh: 1.3 });
    }
  };

  var fontsReady = null;
  function loadFonts() {
    if (!fontsReady) fontsReady = Promise.all([
      document.fonts.load("400 100px 'Haffer XH'"), document.fonts.load("500 40px 'Haffer VF'"), document.fonts.load("600 40px 'Haffer VF'"), document.fonts.load("700 40px 'Haffer VF'"),
      document.fonts.load("400 24px 'Haffer Mono'"), document.fonts.load("500 24px 'Haffer Mono'")
    ]).catch(function () {});
    return fontsReady;
  }
  function render() {
    var list = document.querySelectorAll('canvas[data-story]:not([data-drawn])');
    if (!list.length) return;
    list.forEach(function (cv) { cv.setAttribute('data-drawn', 'pending'); });
    loadFonts().then(function () {
      list.forEach(function (cv) {
        var fn = STORIES[cv.getAttribute('data-story')];
        if (!fn) return;
        cv.width = W; cv.height = H;
        var c = cv.getContext('2d'); c.clearRect(0, 0, W, H); fn(c);
        cv.setAttribute('data-drawn', '1');
      });
    });
  }
  function download(id) {
    var cv = document.querySelector('canvas[data-story="' + id + '"]');
    if (!cv) return;
    var n = String(Array.prototype.indexOf.call(document.querySelectorAll('canvas[data-story]'), cv) + 1).padStart(2, '0');
    cv.toBlob(function (b) {
      var a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'anvora-story-' + n + '-' + id + '.jpg';
      document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
    }, 'image/jpeg', 0.95);
  }
  document.addEventListener('click', function (e) {
    var d = e.target.closest && e.target.closest('[data-story-download]');
    if (!d) return;
    e.preventDefault();
    var id = d.getAttribute('data-story-download');
    if (id === 'all') {
      Array.prototype.forEach.call(document.querySelectorAll('canvas[data-story]'), function (cv, i) {
        setTimeout(function () { download(cv.getAttribute('data-story')); }, i * 450);
      });
    } else download(id);
  });
  window.anvStories = { render: render, download: download };
  render();
})();
