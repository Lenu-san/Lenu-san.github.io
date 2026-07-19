// Bascule de langue FR / EN et petits réglages.
(function () {
  // --- À personnaliser : colle ici ton URL LinkedIn entre les guillemets.
  // Tant que c'est vide, les boutons LinkedIn restent masqués.
  var LINKEDIN_URL = "https://www.linkedin.com/in/l%C3%A9nusan-g-0470b6336/";

  document.querySelectorAll(".linkedin-link").forEach(function (link) {
    if (LINKEDIN_URL) {
      link.href = LINKEDIN_URL;
      link.hidden = false;
    }
  });

  var toggle = document.getElementById("lang-toggle");
  var current = "fr";

  function setLang(lang) {
    current = lang;
    document.querySelectorAll("[data-" + lang + "]").forEach(function (el) {
      el.textContent = el.getAttribute("data-" + lang);
    });
    document.documentElement.lang = lang;
    // le bouton propose l'AUTRE langue
    toggle.textContent = lang === "fr" ? "EN" : "FR";
  }

  toggle.addEventListener("click", function () {
    setLang(current === "fr" ? "en" : "fr");
  });

  // Année du footer, sans dépendre d'une saisie manuelle.
  var yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }
})();
