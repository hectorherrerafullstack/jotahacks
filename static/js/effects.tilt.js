// effects.tilt.js — Tilt 2.0 con spring + glare + parallax
(() => {
  function tiltCards(selector, userOpts = {}) {
    const opts = Object.assign({
      profile: 'dramatic',      // 'dramatic' | 'classic' | 'subtle'
      perspective: 900,
      maxTilt: 16,              // grados
      scale: 1.06,              // escala en hover
      magnet: 10,               // px de traslación que “sigue” al cursor
      stiffness: 0.18,          // fuerza del muelle (0.10–0.30)
      damping: 0.82,            // fricción (0.70–0.90)
      glare: true,              // brillo que sigue al ratón
      glareAlpha: 0.16,
      parallaxSelector: '[data-tilt-z]', // hijos con profundidad
    }, profileDefaults(userOpts.profile), userOpts);

    const cards = document.querySelectorAll(selector);
    cards.forEach((card) => setupCard(card, opts));
  }

  function profileDefaults(p) {
    switch (p) {
      case 'dramatic': return { maxTilt: 18, scale: 1.08, magnet: 14, stiffness: 0.2, damping: 0.8, glareAlpha: 0.18 };
      case 'subtle':   return { maxTilt: 8,  scale: 1.03, magnet: 6,  stiffness: 0.16, damping: 0.86, glareAlpha: 0.12 };
      default:         return {}; // classic usa los valores base
    }
  }

  function setupCard(card, opts) {
    card.classList.add('tilt-card');
    let raf = null;

    // Estado objetivo (target) y actual (cur) para muelle
    const target = { rx: 0, ry: 0, s: 1, tx: 0, ty: 0, ga: 0 };
    const cur    = { rx: 0, ry: 0, s: 1, tx: 0, ty: 0, ga: 0 };
    const vel    = { rx: 0, ry: 0, s: 0, tx: 0, ty: 0, ga: 0 };

    // Cache de capas con parallax (translateZ)
    const layers = Array.from(card.querySelectorAll(opts.parallaxSelector))
      .map(el => ({ el, z: parseFloat(el.getAttribute('data-tilt-z') || '0') || 0 }));

    // Helpers de animación (spring integrado)
    function step() {
      raf = null;
      springTo('rx'); springTo('ry'); springTo('s');
      springTo('tx'); springTo('ty'); springTo('ga');

      // Transform de la tarjeta
      card.style.transform =
        `perspective(${opts.perspective}px) ` +
        `rotateX(${cur.rx}deg) rotateY(${cur.ry}deg) ` +
        `translate3d(${cur.tx}px, ${cur.ty}px, 0) scale(${cur.s})`;

      if (opts.glare) {
        card.style.setProperty('--sheen-alpha', String(cur.ga));
      }

      // Parallax de capas (más z => más movimiento)
      if (layers.length) {
        const fx = cur.ry / opts.maxTilt; // -1..1
        const fy = cur.rx / opts.maxTilt; // -1..1
        layers.forEach(({ el, z }) => {
          const px = -fx * z;  // invertimos para “sentir” profundidad
          const py =  fy * z;
          el.style.transform = `translate3d(${px}px, ${py}px, ${z}px)`;
        });
      }
    }

    function springTo(k) {
      const acc = (target[k] - cur[k]) * opts.stiffness;
      vel[k] = (vel[k] + acc) * opts.damping;
      cur[k] += vel[k];
    }

    // Eventos
    function onEnter() {
      target.s  = opts.scale;
      target.ga = opts.glare ? opts.glareAlpha : 0;
      start();
    }

    function onMove(e) {
      const r = card.getBoundingClientRect();
      const x = e.clientX - r.left;
      const y = e.clientY - r.top;

      const nx = (x / r.width) - 0.5;   // -0.5 .. 0.5
      const ny = (y / r.height) - 0.5;

      target.ry = -nx * opts.maxTilt * 2; // rotateY
      target.rx =  ny * opts.maxTilt * 2; // rotateX

      // Traslación magnética (ligero follow)
      target.tx = nx * opts.magnet;
      target.ty = ny * opts.magnet;

      // Glare: mueve el hotspot
      if (opts.glare) {
        card.style.setProperty('--gx', `${(nx + 0.5) * 100}%`);
        card.style.setProperty('--gy', `${(ny + 0.5) * 100}%`);
      }

      // OPCIONAL: disparar evento para que el canvas de partículas reaccione
      card.dispatchEvent(new CustomEvent('tilt:move', {
        bubbles: true,
        detail: { cx: r.left + x, cy: r.top + y }
      }));

      start();
    }

    function onLeave() {
      target.rx = 0; target.ry = 0;
      target.tx = 0; target.ty = 0;
      target.s  = 1;
      target.ga = 0;

      // Evento opcional
      card.dispatchEvent(new CustomEvent('tilt:leave', { bubbles: true }));

      start();
    }

    function start() { if (!raf) raf = requestAnimationFrame(step); }

    card.addEventListener('pointerenter', onEnter);
    card.addEventListener('pointermove',  onMove, { passive: true });
    card.addEventListener('pointerleave', onLeave);

    // Por si se crea fuera de viewport y entra luego
    window.addEventListener('blur', onLeave);
  }

  // Exponer global
  window.tiltCards = tiltCards;
})();
