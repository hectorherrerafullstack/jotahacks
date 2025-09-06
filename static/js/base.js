(() => {
  // ───────────────────────────────────────────────────────────
  // Menú móvil (open/close)
  // ───────────────────────────────────────────────────────────
  const btn  = document.getElementById('mobile-menu-button');
  const menu = document.getElementById('mobile-menu');

  const openMobile = () => {
    if (!menu) return;
    menu.dataset.open = 'true';
    menu.classList.remove('opacity-0','translate-x-2','pointer-events-none');
    menu.classList.add('opacity-100','translate-x-0');
    menu.setAttribute('aria-hidden','false');
    btn?.setAttribute('aria-expanded','true');
  };

  const closeMobile = () => {
    if (!menu) return;
    menu.dataset.open = 'false';
    menu.classList.add('opacity-0','translate-x-2','pointer-events-none');
    menu.classList.remove('opacity-100','translate-x-0');
    menu.setAttribute('aria-hidden','true');
    btn?.setAttribute('aria-expanded','false');
  };

  const toggleMobile = () => (menu?.dataset.open === 'true' ? closeMobile() : openMobile());
  btn?.addEventListener('click', toggleMobile);

  document.addEventListener('click', (e) => {
    if (menu?.dataset.open !== 'true') return;
    if (!menu.contains(e.target) && !btn?.contains(e.target)) closeMobile();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && menu?.dataset.open === 'true') closeMobile();
  });

  // ───────────────────────────────────────────────────────────
  // Desktop: Servicios (hover/focus-within abre; click navega)
  // ───────────────────────────────────────────────────────────
  const ddRoot    = document.getElementById('services-root');
  const ddLink    = document.getElementById('services-link');   // <a href="/servicios/">
  const ddPanel   = document.getElementById('services-panel');
  const ddChevron = document.getElementById('services-chevron');

  const setExpanded = (exp) => {
    ddLink?.setAttribute('aria-expanded', exp ? 'true' : 'false');
    ddChevron?.classList.toggle('rotate-180', !!exp);
  };

  // Hover & focus dentro del grupo controlan aria-expanded (CSS ya muestra/oculta)
  ddRoot?.addEventListener('pointerenter', () => setExpanded(true));
  ddRoot?.addEventListener('pointerleave', () => setExpanded(false));
  ddRoot?.addEventListener('focusin', () => setExpanded(true));
  ddRoot?.addEventListener('focusout', () => {
    // Cierra si el foco sale del grupo
    setTimeout(() => {
      if (!ddRoot.contains(document.activeElement)) setExpanded(false);
    }, 0);
  });

  // Accesibilidad teclado: ArrowDown desde el link enfoca el 1er item del panel
  ddLink?.addEventListener('keydown', (e) => {
    if (!ddPanel) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      const first = ddPanel.querySelector('[role="menuitem"]');
      first?.focus();
    }
  });

  // Escape dentro del panel vuelve el foco al link
  ddPanel?.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      ddLink?.focus();
    }
  });

  // ───────────────────────────────────────────────────────────
  // Móvil: acordeón de Servicios con chevron (texto navega)
  // ───────────────────────────────────────────────────────────
  const mToggle  = document.getElementById('mobile-services-toggle');
  const mPanel   = document.getElementById('mobile-services-panel');
  const mChevron = document.getElementById('mobile-services-chevron');

  const openMobileAccordion = () => {
    if (!mPanel) return;
    mPanel.style.maxHeight = mPanel.scrollHeight + 'px';
    mToggle?.setAttribute('aria-expanded','true');
    mChevron?.classList.add('rotate-180');
  };
  const closeMobileAccordion = () => {
    if (!mPanel) return;
    mPanel.style.maxHeight = '0px';
    mToggle?.setAttribute('aria-expanded','false');
    mChevron?.classList.remove('rotate-180');
  };
  const toggleMobileAccordion = () => {
    (mToggle?.getAttribute('aria-expanded') === 'true')
      ? closeMobileAccordion()
      : openMobileAccordion();
  };
  mToggle?.addEventListener('click', (e) => {
    e.preventDefault();
    toggleMobileAccordion();
  });

  // Si se cierra el menú móvil, colapsa también el acordeón
  const mo = new MutationObserver(() => {
    if (menu?.dataset.open !== 'true') closeMobileAccordion();
  });
  if (menu) mo.observe(menu, { attributes: true, attributeFilter: ['data-open'] });
})();
