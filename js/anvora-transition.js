/* Anvora "SaaS gradient transition": a gradient-map transition between two photos, rendered with WebGL.
   Photo 1 is tinted by brightness (shadows purple, mids pink, highlights peach/white) with a soft glow,
   Photo 2 is revealed through its darkest areas first, then the tint fades away.
   Export draws every frame (60 fps) and encodes an MP4 with WebCodecs + mp4-muxer. Photos never leave the browser. */
(function () {
  if (window.anvGT) { window.anvGT.init(); return; }

  var STYLES = {
    dreamy: ['#3A0CA3', '#8E2DE2', '#E86BD0', '#FFC2A8', '#FFF6EE'],
    brand: ['#151313', '#6840FF', '#9C83FF', '#A1FF62', '#F4F4F4'],
    sunset: ['#2B0F5E', '#C2186B', '#FF7A59', '#FFD08A', '#FFF6E5']
  };
  var FORMATS = { '16x9': [1920, 1080], '9x16': [1080, 1920], '1x1': [1080, 1080] };
  var HOLD = 0.75; // seconds of still photo before and after the transition

  var VS = 'attribute vec2 p;varying vec2 v;void main(){v=p*0.5+0.5;gl_Position=vec4(p,0.,1.);}';
  var FS = [
    'precision highp float;varying vec2 v;',
    'uniform sampler2D uA,uB;uniform vec2 uRes,uSA,uSB;uniform float uP;uniform vec3 uC0,uC1,uC2,uC3,uC4;',
    'float luma(vec3 c){return dot(c,vec3(0.299,0.587,0.114));}',
    'float hash(vec2 q){return fract(sin(dot(q,vec2(12.9898,78.233)))*43758.5453);}',
    'vec2 cover(vec2 uv,vec2 img,float z){float rc=uRes.x/uRes.y,ri=img.x/img.y;vec2 s=rc>ri?vec2(1.,ri/rc):vec2(rc/ri,1.);return (uv-0.5)*s/z+0.5;}',
    'vec3 gmap(float l){l=clamp(l,0.,1.);',
    ' if(l<0.25)return mix(uC0,uC1,l/0.25);if(l<0.5)return mix(uC1,uC2,(l-0.25)/0.25);',
    ' if(l<0.75)return mix(uC2,uC3,(l-0.5)/0.25);return mix(uC3,uC4,(l-0.75)/0.25);}',
    'void main(){',
    ' float p=uP;',
    ' float tint=smoothstep(0.0,0.32,p)*(1.0-smoothstep(0.62,1.0,p));',
    ' float za=1.0+0.07*smoothstep(0.0,0.55,p), zb=1.0+0.07*(1.0-smoothstep(0.45,1.0,p));',
    ' vec3 A=texture2D(uA,cover(v,uSA,za)).rgb, B=texture2D(uB,cover(v,uSB,zb)).rgb;',
    ' float k=smoothstep(0.22,0.80,p);',
    ' float lb=luma(B)+(hash(floor(v*uRes/2.0))-0.5)*0.10;',
    ' float edge=k*1.45-0.25;',
    ' float m=1.0-smoothstep(edge-0.12,edge+0.12,lb);',
    ' vec3 col=mix(A,B,m);',
    ' vec3 mapped=gmap(luma(col)*1.05+0.03);',
    ' col=mix(col,mapped,tint*0.9);',
    ' col+=tint*0.10*vec3(1.0,0.9,0.97);',
    ' vec2 lp=vec2(0.88,0.86);float leak=exp(-distance(v,lp)*3.2)*tint;',
    ' col+=leak*0.45*mix(uC3,uC4,0.5);',
    ' gl_FragColor=vec4(clamp(col,0.,1.),1.);}'
  ].join('\n');

  function hex(h) { var n = parseInt(h.slice(1), 16); return [(n >> 16) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255]; }
  function ease(x) { return -(Math.cos(Math.PI * x) - 1) / 2; }  // gentle ease-in-out, so the reveal isn't rushed

  function Renderer(cv) {
    var gl = cv.getContext('webgl', { preserveDrawingBuffer: true, premultipliedAlpha: false, antialias: false });
    if (!gl) return null;
    function sh(type, src) { var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); return s; }
    var pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(pr); gl.useProgram(pr);
    var buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    var U = {}; ['uA', 'uB', 'uRes', 'uSA', 'uSB', 'uP', 'uC0', 'uC1', 'uC2', 'uC3', 'uC4'].forEach(function (n) { U[n] = gl.getUniformLocation(pr, n); });
    var tex = [gl.createTexture(), gl.createTexture()], sizes = [[1, 1], [1, 1]];
    tex.forEach(function (t, i) {
      gl.activeTexture(gl.TEXTURE0 + i); gl.bindTexture(gl.TEXTURE_2D, t);
      ['TEXTURE_WRAP_S', 'TEXTURE_WRAP_T'].forEach(function (k) { gl.texParameteri(gl.TEXTURE_2D, gl[k], gl.CLAMP_TO_EDGE); });
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    });
    gl.uniform1i(U.uA, 0); gl.uniform1i(U.uB, 1);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    return {
      gl: gl,
      setImage: function (i, src) {
        gl.activeTexture(gl.TEXTURE0 + i); gl.bindTexture(gl.TEXTURE_2D, tex[i]);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, src);
        sizes[i] = [src.width, src.height];
      },
      setStyle: function (pal) { pal.forEach(function (c, i) { var v = hex(c); gl.uniform3f(U['uC' + i], v[0], v[1], v[2]); }); },
      render: function (p) {
        gl.viewport(0, 0, cv.width, cv.height);
        gl.uniform2f(U.uRes, cv.width, cv.height); gl.uniform2f(U.uSA, sizes[0][0], sizes[0][1]); gl.uniform2f(U.uSB, sizes[1][0], sizes[1][1]);
        gl.uniform1f(U.uP, p);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      }
    };
  }

  // sample photos so the preview works before anything is uploaded
  function sample(kind) {
    var c = document.createElement('canvas'); c.width = 1600; c.height = 1000; var x = c.getContext('2d');
    if (kind === 'a') {
      var g = x.createLinearGradient(0, 0, 0, 1000); g.addColorStop(0, '#2A2626'); g.addColorStop(1, '#151313'); x.fillStyle = g; x.fillRect(0, 0, 1600, 1000);
      var r = x.createRadialGradient(1150, 380, 20, 1150, 380, 520); r.addColorStop(0, 'rgba(255,214,170,.9)'); r.addColorStop(1, 'rgba(255,214,170,0)'); x.fillStyle = r; x.fillRect(0, 0, 1600, 1000);
      x.fillStyle = '#6840FF'; x.beginPath(); x.arc(560, 560, 230, 0, 7); x.fill();
      x.fillStyle = '#F4F4F4'; x.fillRect(180, 820, 1240, 26); x.fillRect(180, 870, 820, 26);
      x.fillStyle = '#F4F4F4'; x.font = '600 120px Arial, sans-serif'; x.fillText('Photo 1', 180, 220);
    } else {
      var s = x.createLinearGradient(0, 0, 0, 1000); s.addColorStop(0, '#6E9BFF'); s.addColorStop(0.55, '#F7C6E8'); s.addColorStop(1, '#FFE3C2'); x.fillStyle = s; x.fillRect(0, 0, 1600, 1000);
      x.fillStyle = 'rgba(255,255,255,.85)'; [[300, 260, 120], [420, 240, 150], [560, 270, 110], [1180, 200, 130], [1320, 230, 100]].forEach(function (b) { x.beginPath(); x.arc(b[0], b[1], b[2], 0, 7); x.fill(); });
      x.fillStyle = '#4E8F3A'; x.beginPath(); x.moveTo(0, 1000); x.quadraticCurveTo(800, 430, 1600, 1000); x.fill();
      x.fillStyle = '#2E5E22'; x.beginPath(); x.moveTo(0, 1000); x.quadraticCurveTo(800, 640, 1600, 1000); x.fill();
      x.fillStyle = '#151313'; x.font = '600 120px Arial, sans-serif'; x.fillText('Photo 2', 980, 820);
    }
    return c;
  }
  function loadFile(file) {
    return new Promise(function (ok, fail) {
      var url = URL.createObjectURL(file), img = new Image();
      img.onload = function () {
        var max = 2560, k = Math.min(1, max / Math.max(img.naturalWidth, img.naturalHeight));
        var c = document.createElement('canvas'); c.width = Math.round(img.naturalWidth * k); c.height = Math.round(img.naturalHeight * k);
        c.getContext('2d').drawImage(img, 0, 0, c.width, c.height); URL.revokeObjectURL(url); ok(c);
      };
      img.onerror = function () { URL.revokeObjectURL(url); fail(); };
      img.src = url;
    });
  }

  // ---------- video export
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
    for (var i = 0; i < list.length; i++) {
      try { var s = await VideoEncoder.isConfigSupported({ codec: list[i], width: w, height: h, bitrate: bitrate, framerate: fps }); if (s.supported) return list[i]; } catch (e) {}
    }
    return null;
  }
  async function exportMp4(st, onProgress) {
    if (!window.VideoEncoder || !window.VideoFrame) throw new Error('unsupported');
    var f = FORMATS[st.format], w = f[0], h = f[1], fps = 60, bitrate = 16000000;
    var len = HOLD * 2 + st.dur, total = Math.round(len * fps);
    var codec = await pickCodec(w, h, fps, bitrate); if (!codec) throw new Error('codec');
    await loadMuxer();
    var c = document.createElement('canvas'); c.width = w; c.height = h;
    var r = Renderer(c); if (!r) throw new Error('webgl');
    r.setImage(0, st.imgs[0]); r.setImage(1, st.imgs[1]); r.setStyle(STYLES[st.style]);
    var muxer = new Mp4Muxer.Muxer({ target: new Mp4Muxer.ArrayBufferTarget(), video: { codec: 'avc', width: w, height: h, frameRate: fps }, fastStart: 'in-memory' });
    var failed = null;
    var enc = new VideoEncoder({ output: function (chunk, meta) { muxer.addVideoChunk(chunk, meta); }, error: function (e) { failed = e; } });
    enc.configure({ codec: codec, width: w, height: h, bitrate: bitrate, framerate: fps, avc: { format: 'avc' } });
    for (var i = 0; i < total; i++) {
      if (failed) throw failed;
      var t = i / fps, p = ease(Math.min(1, Math.max(0, (t - HOLD) / st.dur)));
      r.render(p);
      var frame = new VideoFrame(c, { timestamp: Math.round(i * 1e6 / fps), duration: Math.round(1e6 / fps) });
      enc.encode(frame, { keyFrame: i % fps === 0 }); frame.close();
      while (enc.encodeQueueSize > 6) await yieldNow();
      if (i % 6 === 0) { onProgress(i / total); await yieldNow(); }
    }
    await enc.flush(); enc.close(); muxer.finalize();
    var lose = r.gl.getExtension('WEBGL_lose_context'); if (lose) lose.loseContext();
    return { blob: new Blob([muxer.target.buffer], { type: 'video/mp4' }), len: len };
  }

  // ---------- one widget per [data-gt]
  function Widget(root) {
    var cv = root.querySelector('[data-gt-canvas]'), stage = root.querySelector('.anv-gt__stage');
    var st = { imgs: [sample('a'), sample('b')], style: 'dreamy', format: '16x9', dur: 1.5, playing: true, clock: 0, scrubbing: false };
    var r = Renderer(cv);
    if (!r) { root.querySelector('[data-gt-status]').textContent = 'Your browser doesn’t support WebGL, which this effect needs.'; return; }
    r.setImage(0, st.imgs[0]); r.setImage(1, st.imgs[1]); r.setStyle(STYLES[st.style]); swapThumbs();
    var scrub = root.querySelector('[data-gt-scrub]'), playBtn = root.querySelector('[data-gt-play]');
    function size() {
      var f = FORMATS[st.format], dpr = Math.min(window.devicePixelRatio || 1, 2);
      stage.style.aspectRatio = f[0] + ' / ' + f[1]; stage.setAttribute('data-format', st.format);
      var cw = cv.clientWidth || 800, ch = Math.round(cw * f[1] / f[0]);
      cv.width = Math.round(cw * dpr); cv.height = Math.round(ch * dpr);
    }
    function pAt(t) { return ease(Math.min(1, Math.max(0, (t - HOLD) / st.dur))); }
    function tick(time, dt) {
      if (!cv.isConnected) { if (window.gsap) gsap.ticker.remove(tick); return; }
      var len = HOLD * 2 + st.dur;
      if (st.playing && !st.scrubbing) { st.clock = (st.clock + (dt || 16) / 1000) % (len + 0.4); scrub.value = Math.round(Math.min(1, st.clock / len) * 1000); }
      r.render(pAt(Math.min(st.clock, len)));
    }
    size();
    if (window.ResizeObserver) new ResizeObserver(size).observe(cv);
    if (window.gsap) gsap.ticker.add(tick); else (function loop() { if (!cv.isConnected) return; tick(0, 16); requestAnimationFrame(loop); })();

    root.addEventListener('input', function (e) {
      if (e.target === scrub) { st.playing = false; playBtn.textContent = 'Play'; st.clock = (+scrub.value / 1000) * (HOLD * 2 + st.dur); }
    });
    root.addEventListener('change', function (e) {
      var t = e.target;
      if (t.hasAttribute('data-gt-file') && t.files && t.files[0]) useFile(t.getAttribute('data-gt-file'), t.files[0]);
      if (t.hasAttribute('data-gt-format')) { st.format = t.value; size(); }
      if (t.hasAttribute('data-gt-len')) { st.dur = +t.value; st.clock = 0; }
    });
    root.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b || !root.contains(b)) return;
      if (b.hasAttribute('data-gt-play')) { st.playing = !st.playing; b.textContent = st.playing ? 'Pause' : 'Play'; }
      if (b.hasAttribute('data-gt-style')) {
        st.style = b.getAttribute('data-gt-style'); r.setStyle(STYLES[st.style]);
        Array.prototype.forEach.call(root.querySelectorAll('[data-gt-style]'), function (x) { x.classList.toggle('is--on', x === b); });
      }
      if (b.hasAttribute('data-gt-swap')) { st.imgs.reverse(); r.setImage(0, st.imgs[0]); r.setImage(1, st.imgs[1]); swapThumbs(); }
      if (b.hasAttribute('data-gt-export')) doExport(b);
    });
    // drag and drop onto the upload boxes
    Array.prototype.forEach.call(root.querySelectorAll('[data-gt-drop]'), function (d) {
      d.addEventListener('dragover', function (e) { e.preventDefault(); d.classList.add('is--over'); });
      d.addEventListener('dragleave', function () { d.classList.remove('is--over'); });
      d.addEventListener('drop', function (e) {
        e.preventDefault(); d.classList.remove('is--over');
        var f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]; if (f) useFile(d.getAttribute('data-gt-drop'), f);
      });
    });
    function thumb(which) { return root.querySelector('[data-gt-thumb="' + which + '"]'); }
    function setThumb(which, c) { var im = thumb(which); im.src = c.toDataURL('image/jpeg', 0.7); im.closest('[data-gt-drop]').classList.add('has--img'); }
    function swapThumbs() { setThumb('a', st.imgs[0]); setThumb('b', st.imgs[1]); }
    function useFile(which, file) {
      var status = root.querySelector('[data-gt-status]');
      loadFile(file).then(function (c) {
        var i = which === 'a' ? 0 : 1; st.imgs[i] = c; r.setImage(i, c); setThumb(which, c);
        st.clock = 0; st.playing = true; playBtn.textContent = 'Pause';
        status.textContent = (i ? 'Photo 2' : 'Photo 1') + ' added.';
      }, function () { status.textContent = 'That file couldn’t be opened as an image. Please choose a JPG, PNG or WebP.'; });
    }
    function doExport(b) {
      var status = root.querySelector('[data-gt-status]'), bar = root.querySelector('[data-gt-progress]'), label = b.textContent, t0 = performance.now();
      if (b.disabled) return;
      b.disabled = true; b.textContent = 'Making video… 0%'; status.textContent = 'Drawing every frame at 60 fps. This takes a few seconds.';
      exportMp4(st, function (p) { b.textContent = 'Making video… ' + Math.round(p * 100) + '%'; bar.style.transform = 'scaleX(' + p + ')'; })
        .then(function (res) {
          var a = document.createElement('a'); a.href = URL.createObjectURL(res.blob);
          a.download = 'anvora-gradient-transition-' + st.format + '.mp4';
          document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(a.href); }, 10000);
          status.textContent = 'Saved: ' + res.len.toFixed(2).replace(/0$/, '') + ' seconds, 60 fps, MP4 (' + (Math.round(res.blob.size / 1048576 * 10) / 10) + ' MB). Made in ' + Math.round((performance.now() - t0) / 1000) + 's.';
        }, function () {
          status.textContent = 'This browser can’t make MP4 videos. Please use the latest Chrome, Edge or Safari.';
        })
        .then(function () { b.disabled = false; b.textContent = label; bar.style.transform = 'scaleX(0)'; });
    }
  }
  function init() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-gt]:not([data-gt-init])'), function (el) { el.setAttribute('data-gt-init', '1'); Widget(el); });
  }
  window.anvGT = { init: init };
  init();
})();
