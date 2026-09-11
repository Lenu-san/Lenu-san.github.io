/* Portfolio — améliorations progressives.
   Le site est entièrement lisible sans ce fichier : navigation, contenu et
   bascule FR/EN fonctionnent en HTML pur. Ce script ajoute :
   - le menu mobile ;
   - le bouton de thème clair / sombre (mémorisé dans localStorage) ;
   - le surlignage de la section active dans la navigation ;
   - l'ombre de l'en-tête au défilement ;
   - les animations : apparition des sections (avec repli automatique si
     l'observateur ne répond pas), compteurs des repères, et le panneau
     « terminal d'audit » du hero qui rejoue les sorties des outils.
   Tout mouvement est coupé si l'utilisateur préfère un mouvement réduit. */
(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("js");

  var motionQuery = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
  var reducedMotion = !!(motionQuery && motionQuery.matches);
  var hasObserver = "IntersectionObserver" in window;

  /* --- Thème clair / sombre --------------------------------------------- */
  var themeButton = document.querySelector("[data-theme-toggle]");
  var systemDark = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  var currentTheme = function () {
    var forced = root.getAttribute("data-theme");
    if (forced === "dark" || forced === "light") return forced;
    return systemDark && systemDark.matches ? "dark" : "light";
  };

  var updateThemeLabel = function () {
    if (!themeButton) return;
    var next = currentTheme() === "dark" ? "light" : "dark";
    var label = themeButton.getAttribute(next === "dark" ? "data-label-dark" : "data-label-light");
    if (label) {
      themeButton.setAttribute("aria-label", label);
      themeButton.setAttribute("title", label);
    }
  };

  if (themeButton) {
    themeButton.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.classList.add("theme-switching");
      root.setAttribute("data-theme", next);
      try {
        localStorage.setItem("theme", next);
      } catch (e) {
        /* stockage indisponible : le thème reste valable pour la page en cours */
      }
      updateThemeLabel();
      window.setTimeout(function () {
        root.classList.remove("theme-switching");
      }, 400);
    });
    if (systemDark && systemDark.addEventListener) {
      systemDark.addEventListener("change", updateThemeLabel);
    }
    updateThemeLabel();
  }

  /* --- Menu mobile ------------------------------------------------------ */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");

  if (toggle && nav) {
    var label = toggle.querySelector(".visually-hidden");

    var setMenu = function (open) {
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      if (label) {
        label.textContent = toggle.getAttribute(open ? "data-close" : "data-open") || "";
      }
    };

    toggle.addEventListener("click", function () {
      setMenu(toggle.getAttribute("aria-expanded") !== "true");
    });

    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) setMenu(false);
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        setMenu(false);
        toggle.focus();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 960) setMenu(false);
    });
  }

  /* --- En-tête : ombre au défilement ------------------------------------ */
  var header = document.querySelector(".site-header");
  if (header) {
    var ticking = false;
    var onScroll = function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        header.classList.toggle("is-scrolled", window.scrollY > 8);
        ticking = false;
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* --- Section active dans la navigation -------------------------------- */
  var navLinks = document.querySelectorAll(".nav a[data-nav]");
  var sections = [];

  Array.prototype.forEach.call(navLinks, function (link) {
    var section = document.getElementById(link.getAttribute("data-nav"));
    if (section) sections.push({ link: link, section: section });
  });

  if (sections.length && hasObserver) {
    var current = null;
    var navObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var match = sections.filter(function (item) {
            return item.section === entry.target;
          })[0];
          if (!match || match === current) return;
          if (current) current.link.removeAttribute("aria-current");
          match.link.setAttribute("aria-current", "true");
          current = match;
        });
      },
      { rootMargin: "-40% 0px -55% 0px" }
    );
    sections.forEach(function (item) {
      navObserver.observe(item.section);
    });
  }

  /* --- Apparition des sections au défilement ---------------------------- */
  // Le contenu n'est masqué QUE si l'observateur est disponible et que le
  // mouvement n'est pas réduit ; un repli révèle tout au bout de 1,5 s quoi
  // qu'il arrive (impression, capture, observateur muet).
  var revealed = document.querySelectorAll(".reveal");
  var STAGGER_SELECTOR =
    ".about-block, .domain, .mission, .skill-group, .project, .certs > li, .timeline > li, .split > .panel, .methods-grid > .panel, .steps > li";

  var revealAll = function () {
    Array.prototype.forEach.call(revealed, function (el) {
      el.classList.add("is-visible");
    });
  };

  if (revealed.length && hasObserver && !reducedMotion) {
    root.classList.add("js-reveal");
    Array.prototype.forEach.call(revealed, function (section) {
      var items = section.querySelectorAll(STAGGER_SELECTOR);
      Array.prototype.forEach.call(items, function (item, index) {
        item.classList.add("stagger");
        item.style.setProperty("--d", String(Math.min(index, 9)));
      });
    });

    var revealObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -10% 0px", threshold: 0.05 }
    );
    Array.prototype.forEach.call(revealed, function (el) {
      revealObserver.observe(el);
    });

    // Repli : si aucune section n'est apparue au bout de 1,5 s, l'observateur
    // ne répond pas (capture, aperçu, navigateur particulier) : on affiche tout.
    window.setTimeout(function () {
      if (!document.querySelector(".reveal.is-visible")) revealAll();
    }, 1500);
    window.addEventListener("beforeprint", revealAll);
  } else {
    revealAll();
  }

  /* --- Compteurs des repères -------------------------------------------- */
  var counters = document.querySelectorAll("[data-count]");

  if (counters.length && hasObserver && !reducedMotion) {
    var run = function (el) {
      var text = el.textContent;
      var match = /^(\d+)(.*)$/.exec(text.trim());
      if (!match) return;
      var target = parseInt(match[1], 10);
      var suffix = match[2];
      var duration = 800;
      var start = null;
      var step = function (timestamp) {
        if (start === null) start = timestamp;
        var ratio = Math.min((timestamp - start) / duration, 1);
        var eased = 1 - Math.pow(1 - ratio, 3);
        el.textContent = Math.round(target * eased) + suffix;
        if (ratio < 1) window.requestAnimationFrame(step);
        else el.textContent = text;
      };
      window.requestAnimationFrame(step);
    };

    var countObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          run(entry.target);
          countObserver.unobserve(entry.target);
        });
      },
      { threshold: 0.5 }
    );
    Array.prototype.forEach.call(counters, function (el) {
      countObserver.observe(el);
    });
  }

  /* --- Panneau « terminal d'audit » ------------------------------------- */
  // Rejoue les scènes une par une : la commande est tapée, puis les lignes
  // de résultat apparaissent, puis on passe à la scène suivante. Sans
  // JavaScript ou en mouvement réduit, toutes les scènes restent affichées.
  var term = document.querySelector("[data-term]");

  if (term && !reducedMotion) {
    var scenes = Array.prototype.slice.call(term.querySelectorAll(".term-scene"));
    if (scenes.length) {
      root.classList.add("js-term");
      var sceneIndex = 0;
      var timers = [];
      var termVisible = true;
      var pageVisible = !document.hidden;

      var later = function (fn, delay) {
        timers.push(window.setTimeout(fn, delay));
      };

      var clearTimers = function () {
        timers.forEach(window.clearTimeout);
        timers = [];
      };

      var playScene = function () {
        clearTimers();
        scenes.forEach(function (s, i) {
          s.classList.toggle("is-active", i === sceneIndex);
          Array.prototype.forEach.call(s.querySelectorAll(".term-line"), function (line) {
            line.classList.remove("is-shown");
          });
        });

        var scene = scenes[sceneIndex];
        var cmdEl = scene.querySelector(".term-cmd-text");
        var full = cmdEl.getAttribute("data-full") || cmdEl.textContent;
        cmdEl.setAttribute("data-full", full);
        cmdEl.textContent = "";
        cmdEl.classList.add("is-typing");

        var lines = scene.querySelectorAll(".term-line");
        var pos = 0;
        var typeSpeed = 28;

        var typeNext = function () {
          pos += 1;
          cmdEl.textContent = full.slice(0, pos);
          if (pos < full.length) {
            later(typeNext, typeSpeed);
            return;
          }
          cmdEl.classList.remove("is-typing");
          Array.prototype.forEach.call(lines, function (line, i) {
            later(function () {
              line.classList.add("is-shown");
            }, 320 + i * 240);
          });
          var hold = 320 + lines.length * 240 + 4200;
          later(function () {
            sceneIndex = (sceneIndex + 1) % scenes.length;
            playScene();
          }, hold);
        };

        later(typeNext, 400);
      };

      var stopScene = function () {
        clearTimers();
      };

      var resume = function () {
        if (termVisible && pageVisible) playScene();
        else stopScene();
      };

      document.addEventListener("visibilitychange", function () {
        pageVisible = !document.hidden;
        resume();
      });

      if (hasObserver) {
        new IntersectionObserver(
          function (entries) {
            termVisible = entries[0].isIntersecting;
            resume();
          },
          { threshold: 0.1 }
        ).observe(term);
      } else {
        playScene();
      }
    }
  }

  /* --- Mouvement réduit activé en cours de visite ----------------------- */
  if (motionQuery && motionQuery.addEventListener) {
    motionQuery.addEventListener("change", function (event) {
      if (event.matches) {
        reducedMotion = true;
        root.classList.remove("js-reveal", "js-term");
        revealAll();
      }
    });
  }

  /* --- Année du pied de page -------------------------------------------- */
  var year = document.querySelector("[data-year]");
  if (year) year.textContent = String(new Date().getFullYear());
})();
