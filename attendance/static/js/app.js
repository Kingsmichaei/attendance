(function () {
  var navToggle = document.querySelector('[data-nav-toggle]');
  var nav = document.querySelector('[data-nav]');
  var backdrop = document.querySelector('[data-nav-backdrop]');

  function setNavState(isOpen) {
    if (!nav || !navToggle || !backdrop) {
      return;
    }

    nav.classList.toggle('open', isOpen);
    backdrop.classList.toggle('open', isOpen);
    backdrop.hidden = !isOpen;
    navToggle.setAttribute('aria-expanded', String(isOpen));
    document.body.classList.toggle('nav-open', isOpen);
  }

  if (navToggle && nav) {
    navToggle.addEventListener('click', function () {
      setNavState(!nav.classList.contains('open'));
    });
  }

  if (backdrop && nav) {
    backdrop.addEventListener('click', function () {
      setNavState(false);
    });
  }

  if (nav) {
    nav.addEventListener('click', function (event) {
      var target = event.target;
      if (target && target.closest('a, button')) {
        setNavState(false);
      }
    });
  }

  window.addEventListener('resize', function () {
    if (window.innerWidth > 760) {
      setNavState(false);
    }
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      setNavState(false);
    }
  });

  var flashes = document.querySelectorAll('.flash');
  flashes.forEach(function (item) {
    setTimeout(function () {
      item.style.opacity = '0';
      item.style.transform = 'translateY(-4px)';
      item.style.transition = 'all 220ms ease';
      setTimeout(function () {
        if (item.parentElement) {
          item.parentElement.removeChild(item);
        }
      }, 240);
    }, 4500);
  });
})();
