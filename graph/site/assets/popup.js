
(function () {
  'use strict';
  var POPUP_KINDS = /\/(concept|edge|theme|supertheme|superedge|tissue|figure)\/[^\/]+\.html$/;

  function popupTarget(ev) {
    if (ev.defaultPrevented || ev.button !== 0 ||
        ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return null;
    var a = ev.target.closest ? ev.target.closest('a[href]') : null;
    if (!a || a.target === '_blank') return null;
    var url;
    try { url = new URL(a.getAttribute('href'), window.location.href); }
    catch (e) { return null; }
    if (url.origin !== window.location.origin) return null;
    return url;
  }

  if (window.self !== window.top) {
    // Inside the popup frame: hide the page chrome, keep concept/theme/tissue
    // links inside the frame, break every other link out to the full window.
    document.documentElement.classList.add('in-popup');
    document.addEventListener('click', function (ev) {
      var url = popupTarget(ev);
      if (!url) return;
      if (!POPUP_KINDS.test(url.pathname)) {
        ev.preventDefault();
        window.top.location.href = url.href;
      }
    });
    return;
  }

  var dialog = null, frame = null, fullLink = null;

  function ensureDialog() {
    if (dialog) return dialog;
    dialog = document.createElement('dialog');
    dialog.className = 'popup-dialog';

    var bar = document.createElement('div');
    bar.className = 'popup-bar';

    fullLink = document.createElement('a');
    fullLink.className = 'popup-full';
    fullLink.textContent = 'open as full page ↗';
    bar.appendChild(fullLink);

    var closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'popup-close';
    closeBtn.setAttribute('aria-label', 'Close');
    closeBtn.textContent = '×';
    closeBtn.addEventListener('click', function () { dialog.close(); });
    bar.appendChild(closeBtn);

    frame = document.createElement('iframe');
    frame.className = 'popup-frame';
    frame.setAttribute('title', 'Wiki page');
    frame.addEventListener('load', function () {
      try { fullLink.href = frame.contentWindow.location.href; } catch (e) {}
    });

    dialog.appendChild(bar);
    dialog.appendChild(frame);
    // click on the backdrop (the dialog element itself) closes
    dialog.addEventListener('click', function (ev) {
      if (ev.target === dialog) dialog.close();
    });
    dialog.addEventListener('close', function () {
      frame.src = 'about:blank';
    });
    document.body.appendChild(dialog);
    return dialog;
  }

  document.addEventListener('click', function (ev) {
    var url = popupTarget(ev);
    if (!url || !POPUP_KINDS.test(url.pathname)) return;
    var d = ensureDialog();
    if (typeof d.showModal !== 'function') return; // very old browser: navigate
    ev.preventDefault();
    fullLink.href = url.href;
    frame.src = url.href;
    if (!d.open) d.showModal();
  });
})();
