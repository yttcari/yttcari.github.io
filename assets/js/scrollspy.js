// Highlight the header link for the home-page section currently in view.
(function () {
  var sections = Array.prototype.slice.call(document.querySelectorAll('.page-section[id]'));
  if (!sections.length) return;

  var home = document.querySelector('.masthead__menu-item--lg');
  var homeWasSelected = home && home.classList.contains('selected');
  var ticking = false;

  function update() {
    ticking = false;
    var offset = (document.querySelector('.masthead') || { offsetHeight: 0 }).offsetHeight + 40;
    var current = null;
    sections.forEach(function (s) {
      if (s.getBoundingClientRect().top <= offset) current = s.id;
    });
    // at the very bottom of the page, the last section wins even if it is short
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
      current = sections[sections.length - 1].id;
    }

    // links may be moved between visible/hidden lists by the greedy nav, so query each time
    document.querySelectorAll('.masthead__menu-item').forEach(function (li) {
      var a = li.querySelector('a[href*="#"]');
      if (!a) return;
      li.classList.toggle('selected', a.hash === '#' + current);
    });
    if (home && homeWasSelected) home.classList.toggle('selected', !current);
  }

  function onScroll() {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  window.addEventListener('load', update);
  update();
})();
