/* Anvora Instagram scripts: copy the voice-over and download scripts as .txt files. */
(function () {
  if (window.__anvScripts) return;
  window.__anvScripts = true;
  function save(txt, name) {
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([txt], { type: 'text/plain;charset=utf-8' }));
    a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-script-copy],[data-script-dl]');
    if (!b) return;
    e.preventDefault();
    if (b.hasAttribute('data-script-copy')) {
      var src = document.getElementById(b.getAttribute('data-script-copy'));
      var label = b.textContent;
      var done = function () { b.textContent = 'Copied!'; setTimeout(function () { b.textContent = label; }, 1400); };
      if (src && navigator.clipboard) navigator.clipboard.writeText(src.textContent).then(done, done); else done();
      return;
    }
    var id = b.getAttribute('data-script-dl');
    if (id === 'all') {
      var parts = Array.prototype.map.call(document.querySelectorAll('pre[data-script-txt]'), function (p) { return p.textContent; });
      save(parts.join('\n\n' + new Array(41).join('=') + '\n\n'), 'anvora-instagram-scripts.txt');
    } else {
      var p = document.getElementById('txt-' + id);
      if (p) save(p.textContent, p.getAttribute('data-file'));
    }
  });
})();
