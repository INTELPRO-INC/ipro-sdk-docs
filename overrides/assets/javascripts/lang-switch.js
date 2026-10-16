/* Keep the reader on the same page when switching language.
 *
 * zh-TW lives at the site root and en under /en/, so the theme's own
 * prefix match always resolves to the zh-TW root and falls back to the
 * other language's home page. The zh and en trees mirror each other
 * (enforced by the parity check), so the counterpart is the same path
 * under the other language's base.
 */
(function () {
  "use strict";

  var SELECTOR = "a[hreflang]";

  function languageBases() {
    var seen = {};
    var bases = [];
    document.querySelectorAll(SELECTOR).forEach(function (link) {
      var path = new URL(link.href, location.href).pathname;
      if (!seen[path]) {
        seen[path] = true;
        bases.push(path);
      }
    });
    // Longest first, so /en/ wins over / for pages under /en/.
    return bases.sort(function (a, b) { return b.length - a.length; });
  }

  document.addEventListener("click", function (event) {
    if (event.metaKey || event.ctrlKey || event.shiftKey) return;
    var link = event.target.closest && event.target.closest(SELECTOR);
    if (!link) return;

    var target = new URL(link.href, location.href).pathname;
    var current = languageBases().find(function (base) {
      return location.pathname.indexOf(base) === 0;
    });
    if (!current || current === target) return;

    event.preventDefault();
    event.stopImmediatePropagation();
    location.assign(target + location.pathname.slice(current.length) + location.hash);
  }, true);
})();
