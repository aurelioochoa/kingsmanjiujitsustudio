/* Kingsman Jiu Jitsu Studio — interaction layer
   Nav (mobile + scrollspy) · scroll reveals · 3D tilt
   hero parallax · plan count-up. All progressive +
   reduces cleanly under prefers-reduced-motion.
*/
(function () {
  "use strict";

  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Mobile nav ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var menu = document.getElementById("nav-menu");
  function setNav(open) {
    if (!toggle || !menu) return;
    menu.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "Cerrar menú" : "Abrir menú");
  }
  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      setNav(!menu.classList.contains("open"));
    });
    menu.addEventListener("click", function (e) {
      if (e.target.closest("a")) setNav(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setNav(false);
    });
  }

  /* ---------- Scroll reveals ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add("in");
          en.target.querySelectorAll(".plan-amount[data-count]").forEach(runCountup);
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    reveals.forEach(function (el) { io.observe(el); });

    // 3D tilt (fine pointer only)
    if (finePointer) {
      document.querySelectorAll("[data-tilt]").forEach(function (el) {
        var strength = 9;
        el.addEventListener("pointermove", function (e) {
          var r = el.getBoundingClientRect();
          var px = (e.clientX - r.left) / r.width;   // 0..1
          var py = (e.clientY - r.top) / r.height;
          var rx = (0.5 - py) * strength;
          var ry = (px - 0.5) * strength;
          el.style.transform = "perspective(900px) rotateX(" + rx + "deg) rotateY(" + ry + "deg)";
        });
        el.addEventListener("pointerleave", function () {
          el.style.transform = "";
        });
      });
    }

    // hero background parallax on scroll (subtle)
    var heroBg = document.querySelector(".hero-bg");
    function onScroll() {
      var y = window.scrollY;
      if (heroBg && finePointer && !reduceMotion) {
        heroBg.style.translate = "0 " + (y * 0.35) + "px";
      }
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  } else {
    // No IO / reduced motion: show everything immediately
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- Count-up for plan price ---------- */
  function runCountup(el) {
    if (!el || el.dataset.done) return;
    el.dataset.done = "1";
    if (reduceMotion) return; // HTML already holds the final number
    var target = parseInt(el.dataset.count, 10) || 0;
    var dur = 900, start = null;
    function ease(t) { return 1 - Math.pow(1 - t, 3); }
    function frame(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      el.textContent = Math.round(ease(p) * target);
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  reveals.forEach(function (el) {
    el.querySelectorAll(".plan-amount[data-count]").forEach(runCountup);
  });

  /* ---------- Scrollspy: highlight current section in nav ---------- */
  var links = Array.prototype.slice.call(document.querySelectorAll(".nav-link[href^='#']"));
  var sections = links
    .map(function (a) { return document.querySelector(a.getAttribute("href")); })
    .filter(Boolean);
  function spy() {
    var pos = window.scrollY + 120;
    var current = sections[0];
    sections.forEach(function (s) { if (s.offsetTop <= pos) current = s; });
    links.forEach(function (a) {
      a.classList.toggle("active", a.getAttribute("href") === "#" + current.id);
    });
  }
  if (links.length && sections.length) {
    window.addEventListener("scroll", spy, { passive: true });
    spy();
  }

  /* ---------- Dev A/B theme toggle ---------- */
  (function () {
    var root = document.documentElement;
    var btns = Array.prototype.slice.call(document.querySelectorAll("[data-theme-btn]"));
    if (!btns.length) return;

    // Control interno: solo en desarrollo (localhost, file://) o con ?dev.
    // En producción tapaba contenido en móvil y dejaba a la vista un tema
    // sin terminar.
    var host = location.hostname;
    var isDev = host === "localhost" || host === "127.0.0.1" || host === "" ||
                host.endsWith(".local") || /(^|[?&])dev(=|&|$)/.test(location.search);
    if (!isDev) {
      var panel = document.querySelector(".dev-toggle");
      if (panel && panel.parentNode) panel.parentNode.removeChild(panel);
      // Sin panel no hay forma de volver: fuerza el tema A y limpia el resto.
      root.removeAttribute("data-theme");
      try { localStorage.removeItem("kingsman-theme"); } catch (e) {}
      return;
    }
    function apply(theme) {
      if (theme === "b") root.setAttribute("data-theme", "b");
      else root.removeAttribute("data-theme");
      btns.forEach(function (b) {
        var on = b.getAttribute("data-theme-btn") === theme;
        b.classList.toggle("on", on);
        b.setAttribute("aria-pressed", on ? "true" : "false");
      });
      try { localStorage.setItem("kingsman-theme", theme); } catch (e) {}
    }
    var current = root.getAttribute("data-theme") === "b" ? "b" : "a";
    apply(current); // sync buttons + aria to whatever the FOUC guard set
    btns.forEach(function (b) {
      b.addEventListener("click", function () {
        apply(b.getAttribute("data-theme-btn"));
      });
    });
  })();

  /* ---------- Linaje carousel ---------- */
  function initCarousel(root) {
    var track = root.querySelector("[data-carousel-track]");
    var dotsWrap = root.querySelector("[data-carousel-dots]");
    var prev = root.querySelector(".car-arrow.prev");
    var next = root.querySelector(".car-arrow.next");
    if (!track) return;
    // leading + trailing spacers center the first and last slide (scrollLeft 0 = slide 1 centered)
    var spacer = document.createElement("span");
    spacer.className = "c-spacer";
    spacer.setAttribute("aria-hidden", "true");
    track.insertBefore(spacer, track.firstChild);
    track.appendChild(spacer.cloneNode());
    var slides = Array.prototype.slice.call(track.children).filter(function (el) {
      return !el.classList.contains("c-spacer");
    });
    var GAP = 18;
    var step = 0, timer = null, paused = false, idx = 0, S0 = 0;

    // S0 = scrollLeft that centers the first slide (absorbs track padding + leading spacer)
    function measure() {
      if (!slides.length) return;
      var sw = slides[0].offsetWidth;
      step = sw + GAP;
      S0 = Math.max(0, slides[0].offsetLeft + sw / 2 - track.clientWidth / 2);
    }
    function goTo(i) {
      var max = slides.length - 1;
      idx = Math.max(0, Math.min(max, i));
      track.scrollTo({ left: S0 + idx * step, behavior: reduceMotion ? "auto" : "smooth" });
    }
    function setDots() {
      if (!dotsWrap) return;
      Array.prototype.forEach.call(dotsWrap.children, function (d, i) {
        d.classList.toggle("on", i === idx);
      });
    }
    function updateFromScroll() {
      if (!step) { measure(); return; }
      var cur = Math.round((track.scrollLeft - S0) / step);
      if (cur !== idx) { idx = cur; setDots(); }
    }
    // dots
    if (dotsWrap) {
      slides.forEach(function (s, i) {
        var b = document.createElement("button");
        b.setAttribute("aria-label", "Maestro " + (i + 1));
        b.addEventListener("click", function () { goTo(i); });
        dotsWrap.appendChild(b);
      });
    }
    // arrows
    if (prev) prev.addEventListener("click", function (e) { e.stopPropagation(); goTo(idx - 1); });
    if (next) next.addEventListener("click", function (e) { e.stopPropagation(); goTo(idx + 1); });

    track.addEventListener("scroll", updateFromScroll, { passive: true });
    window.addEventListener("resize", function () { measure(); setDots(); });

    // autoplay — paused on hover, off under reduced motion; starts only when
    // the carousel is visible (and resets to the first master on first reveal)
    if (!reduceMotion) {
      var inView = false, started = false;
      function play() {
        clearInterval(timer);
        if (!inView || paused || !root.offsetParent) return;
        timer = setInterval(function () {
          if (!paused) goTo(idx >= slides.length - 1 ? 0 : idx + 1);
        }, 3600);
      }
      root.addEventListener("pointerenter", function () { paused = true; });
      root.addEventListener("pointerleave", function () { paused = false; play(); });
      function setAuto(on) {
        if (on) {
          inView = true;
          if (!started) { started = true; goTo(0); } // start at the first master
          play();
        } else {
          inView = false;
          clearInterval(timer);
        }
      }
      if ("IntersectionObserver" in window) {
        var io = new IntersectionObserver(function (es) {
          es.forEach(function (e) { setAuto(e.isIntersecting); });
        }, { threshold: 0.25 });
        io.observe(root);
      } else {
        setAuto(true);
      }
    }

    measure(); setDots();
    track.scrollLeft = S0; // center first slide at load
  }
  document.querySelectorAll("[data-carousel]").forEach(initCarousel);

  /* ---------- Hero home background video (muted; static poster if reduced motion) ---------- */
  var hvid = document.querySelector(".hero-video");
  if (hvid && !reduceMotion) { var hp = hvid.play(); if (hp) hp.catch(function () {}); }

  /* ---------- Videos: autoplay muted when visible ---------- */
  var vids = document.querySelectorAll("#videos video");
  if (vids.length && "IntersectionObserver" in window && !reduceMotion) {
    var vio = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        var v = en.target;
        if (en.isIntersecting) { var p = v.play(); if (p) p.catch(function () {}); }
        else { v.pause(); }
      });
    }, { threshold: 0.25 });
    vids.forEach(function (v) { vio.observe(v); });
  }

  /* ---------- Footer year ---------- */
  var yr = document.querySelector(".yr");
  if (yr) yr.textContent = String(new Date().getFullYear());
})();