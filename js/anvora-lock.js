/* Anvora private pages: decrypts a locked page's content in the browser once the right password is entered.
   The unlocked key is kept for this browser tab only (sessionStorage), so other private pages open without asking again. */
(function () {
  if (window.__anvLock) return;
  window.__anvLock = true;
  var STORE = 'anvLockKey';
  function bytes(b64) { var b = atob(b64), u = new Uint8Array(b.length); for (var i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return u; }
  function b64(buf) { var u = new Uint8Array(buf), s = ''; for (var i = 0; i < u.length; i++) s += String.fromCharCode(u[i]); return btoa(s); }
  function derive(pw, d) {
    return crypto.subtle.importKey('raw', new TextEncoder().encode(pw), 'PBKDF2', false, ['deriveKey']).then(function (k) {
      return crypto.subtle.deriveKey({ name: 'PBKDF2', salt: bytes(d.s), iterations: d.i, hash: 'SHA-256' }, k, { name: 'AES-GCM', length: 256 }, true, ['decrypt']);
    });
  }
  function decrypt(key, d) {
    return crypto.subtle.decrypt({ name: 'AES-GCM', iv: bytes(d.iv) }, key, bytes(d.c)).then(function (p) { return new TextDecoder().decode(p); });
  }
  function savedKey(d) {
    try {
      var v = JSON.parse(sessionStorage.getItem(STORE) || 'null');
      if (v && v.s === d.s) return crypto.subtle.importKey('raw', bytes(v.k), { name: 'AES-GCM' }, false, ['decrypt']);
    } catch (e) {}
    return null;
  }
  function saveKey(key, d) {
    crypto.subtle.exportKey('raw', key).then(function (r) { try { sessionStorage.setItem(STORE, JSON.stringify({ s: d.s, k: b64(r) })); } catch (e) {} });
  }
  function reveal(gate, htmlText) {
    var tpl = document.createElement('template');
    tpl.innerHTML = htmlText;
    var scripts = Array.prototype.slice.call(tpl.content.querySelectorAll('script'));
    gate.parentNode.insertBefore(tpl.content, gate);
    gate.parentNode.removeChild(gate);
    scripts.forEach(function (old) {  // scripts added through HTML don't run, so re-create them
      var s = document.createElement('script');
      Array.prototype.forEach.call(old.attributes, function (a) { s.setAttribute(a.name, a.value); });
      s.textContent = old.textContent;
      old.parentNode.replaceChild(s, old);
    });
    try { if (typeof lenis !== 'undefined' && lenis) { lenis.scrollTo(0, { immediate: true }); lenis.resize(); } else window.scrollTo(0, 0); } catch (e) {}
    try { if (window.ScrollTrigger) ScrollTrigger.refresh(); } catch (e) {}
    document.dispatchEvent(new CustomEvent('anv:unlocked'));
  }
  function init() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-anv-lock]:not([data-anv-lock-init])'), function (gate) {
      gate.setAttribute('data-anv-lock-init', '1');
      var d = JSON.parse(gate.querySelector('[data-anv-lock-data]').textContent);
      var form = gate.querySelector('form'), err = gate.querySelector('.anv-lock__err');
      var btn = form.querySelector('button'), inp = form.querySelector('input[type=password]');
      if (!window.crypto || !crypto.subtle) {
        err.textContent = 'This page can only be unlocked over a secure (https) connection.';
        btn.disabled = true;
        return;
      }
      var saved = savedKey(d);
      if (saved) {
        gate.classList.add('is--checking');
        saved.then(function (k) { return decrypt(k, d); }).then(function (h) { reveal(gate, h); }, function () { gate.classList.remove('is--checking'); });
      }
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        err.textContent = '';
        btn.disabled = true; btn.textContent = 'Unlocking…';
        derive(inp.value, d).then(function (k) {
          return decrypt(k, d).then(function (h) { saveKey(k, d); reveal(gate, h); });
        }).catch(function () {
          err.textContent = 'That password isn’t right. Please try again.';
          btn.disabled = false; btn.textContent = 'Unlock';
          inp.select();
        });
      });
    });
  }
  init();
  document.addEventListener('DOMContentLoaded', init);
  new MutationObserver(function () { clearTimeout(window.__anvLT); window.__anvLT = setTimeout(init, 30); })
    .observe(document.documentElement, { childList: true, subtree: true });
})();
