/* Home page behaviour: the SDK architecture diagram and the quick-start terminal.
 *
 * Runs on every page load, including the theme's instant navigation
 * (window.document$, provided by both Material for MkDocs and Zensical).
 * Everything here is progressive: without JS the architecture shows the
 * default chip and the terminal shows its whole transcript.
 */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  /**
   * Make the SDK architecture interactive: chip buttons select which
   * components light up; hovering or focusing a component describes it.
   * @param {ParentNode} root
   * @returns {void}
   */
  function setupArch(root) {
    var figure = root.querySelector("[data-arch]");
    if (!figure || figure.dataset.bound) return;
    figure.dataset.bound = "1";

    var items = Array.prototype.slice.call(figure.querySelectorAll(".ipro-arch__item"));
    var chips = Array.prototype.slice.call(figure.querySelectorAll(".ipro-arch__chip"));
    var title = figure.querySelector("[data-arch-title]");
    var desc = figure.querySelector("[data-arch-desc]");
    var link = figure.querySelector("[data-arch-link]");
    if (!title || !desc || !link) return;

    /** @returns {HTMLElement|undefined} the pressed chip button */
    function selectedChip() {
      return chips.filter(function (c) { return c.getAttribute("aria-pressed") === "true"; })[0];
    }

    /**
     * @param {HTMLElement} el      chip button or component link
     * @param {boolean} isChip      chips also show a link to their spec page
     */
    function describe(el, isChip) {
      title.textContent = el.dataset.title;
      desc.textContent = el.dataset.desc;
      link.hidden = !isChip;
      if (isChip) link.href = el.dataset.link;
    }

    /** Restart the signal sweep on the bus (one pass per change). */
    function sweep() {
      if (reduceMotion) return;
      figure.classList.remove("is-sweep");
      void figure.offsetWidth;
      figure.classList.add("is-sweep");
    }

    /** @param {HTMLElement} chip  chip button to select */
    function select(chip) {
      var id = chip.dataset.chip;
      chips.forEach(function (c) { c.setAttribute("aria-pressed", c === chip ? "true" : "false"); });
      figure.dataset.chip = id;
      items.forEach(function (item) {
        var supported = item.dataset.chips.split(" ").indexOf(id) !== -1;
        var wasOff = item.classList.contains("is-off");
        item.classList.toggle("is-off", !supported);
        if (supported && wasOff && !reduceMotion) {
          item.classList.remove("is-flash");
          void item.offsetWidth;
          item.classList.add("is-flash");
        }
      });
      describe(chip, true);
      sweep();
    }

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () { select(chip); });
    });
    items.forEach(function (item) {
      item.addEventListener("animationend", function () { item.classList.remove("is-flash"); });
      item.addEventListener("mouseenter", function () { describe(item, false); });
      item.addEventListener("focus", function () { describe(item, false); });
      item.addEventListener("mouseleave", function () { describe(selectedChip(), true); });
      item.addEventListener("blur", function () { describe(selectedChip(), true); });
    });

    if (!reduceMotion) window.setTimeout(sweep, 900);
  }

  /**
   * Reveal a terminal transcript line by line, typing the command spans.
   * @param {HTMLElement} term  element with .ln lines; commands in .cmd spans
   * @returns {void}
   */
  function typeTerminal(term) {
    var lines = Array.prototype.slice.call(term.querySelectorAll(".ln"));
    lines.forEach(function (line) { line.classList.add("is-hidden"); });

    var index = 0;
    function next() {
      if (index >= lines.length) {
        term.classList.add("is-done");
        return;
      }
      var line = lines[index++];
      line.classList.remove("is-hidden");
      var cmd = line.querySelector(".cmd");
      if (!cmd) {
        window.setTimeout(next, line.classList.contains("c") ? 140 : 70);
        return;
      }
      var text = cmd.textContent;
      var chars = 0;
      cmd.textContent = "";
      cmd.classList.add("is-typing");
      var step = Math.max(8, Math.min(24, 900 / text.length));
      (function type() {
        chars += 1;
        cmd.textContent = text.slice(0, chars);
        if (chars < text.length) {
          window.setTimeout(type, step);
        } else {
          cmd.classList.remove("is-typing");
          window.setTimeout(next, 260);
        }
      })();
    }
    next();
  }

  /**
   * Type each quick-start terminal once, when it first scrolls into view.
   * @param {ParentNode} root
   * @returns {void}
   */
  function setupTerminals(root) {
    var terms = root.querySelectorAll(".ipro-term[data-typing]:not([data-bound])");
    if (!terms.length || reduceMotion || !("IntersectionObserver" in window)) return;
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        typeTerminal(entry.target);
      });
    }, { threshold: 0.45 });
    terms.forEach(function (term) {
      term.dataset.bound = "1";
      observer.observe(term);
    });
  }

  function init() {
    setupArch(document);
    setupTerminals(document);
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
