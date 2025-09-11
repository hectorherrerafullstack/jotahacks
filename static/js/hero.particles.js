// hero.particles.js — tamaños variados + más velocidad (2025-09-10)
(() => {
  // ===== Config =====
  const HERO_SELECTOR = '.hero-section';   // cambia si usas otro contenedor
  const CANVAS_ID = 'hero-canvas';

  const CONFIG = {
    linkDistance: 140,                // distancia de líneas (px CSS)
    mouseRadius: 140,                 // radio de repulsión (px CSS)
    densityDivisor: 18000,            // menos => más partículas
    sizeRange: [0.9, 2.4],            // radio mínimo/máximo (px CSS)
    speedBase: 0.6,                   // velocidad base (px/frame)
    speedMultiplier: 1.35,            // <= súbelo para ir más rápido
    smallIsFaster: true               // las partículas pequeñas se mueven más
  };

  // ===== Estado =====
  let heroRoot, canvas, ctx, animationId = null;
  const state = {
    w: 0, h: 0,
    particles: [],
    linkDistance: CONFIG.linkDistance,
    mouse: { x: -9999, y: -9999, radius: CONFIG.mouseRadius },
    repel: true
  };

  // ===== Canvas =====
  function ensureCanvas() {
    heroRoot = document.querySelector(HERO_SELECTOR);
    if (!heroRoot) return false;

    canvas = heroRoot.querySelector('#' + CANVAS_ID);
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.id = CANVAS_ID;
      Object.assign(canvas.style, {
        position: 'absolute',
        inset: '0',
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        display: 'block'
      });
      heroRoot.prepend(canvas);
    }
    ctx = canvas.getContext('2d');
    const cs = getComputedStyle(heroRoot);
    if (cs.position === 'static') heroRoot.style.position = 'relative';
    return true;
  }

  // ===== Tamaño y DPR =====
  function initCanvasSize() {
    if (!heroRoot || !canvas) return;
    const r = heroRoot.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;

    // Mundo en px CSS
    state.w = Math.max(1, Math.floor(r.width));
    state.h = Math.max(1, Math.floor(r.height));

    // Buffer físico
    canvas.width  = Math.max(1, Math.floor(r.width  * dpr));
    canvas.height = Math.max(1, Math.floor(r.height * dpr));

    // Estilo CSS
    canvas.style.width  = state.w + 'px';
    canvas.style.height = state.h + 'px';

    // Todo lo que dibujemos a partir de aquí es en px CSS
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Densidad por área
    const target = Math.round((state.w * state.h) / CONFIG.densityDivisor);
    if (state.particles.length === 0) {
      createParticles(target);
    } else if (state.particles.length !== target) {
      resizeParticles(target);
    }

    cacheRect();
  }

  // ===== Utils =====
  function rand(min, max) { return min + Math.random() * (max - min); }

  function spawnParticle() {
    // Radio aleatorio dentro del rango
    const r = rand(CONFIG.sizeRange[0], CONFIG.sizeRange[1]);

    // Velocidad: base * multiplicador * (opcional: inversa del tamaño)
    // Partículas pequeñas se mueven más rápido si smallIsFaster = true
    const speedScale = CONFIG.smallIsFaster
      ? (CONFIG.sizeRange[1] / r) // r pequeño => factor alto
      : 1;

    const vx = (Math.random() - 0.5) * CONFIG.speedBase * CONFIG.speedMultiplier * speedScale;
    const vy = (Math.random() - 0.5) * CONFIG.speedBase * CONFIG.speedMultiplier * speedScale;

    return {
      x: Math.random() * state.w,
      y: Math.random() * state.h,
      vx, vy,
      r
    };
  }

  function createParticles(n) {
    state.particles = [];
    for (let i = 0; i < n; i++) {
      state.particles.push(spawnParticle());
    }
  }

  function resizeParticles(n) {
    const cur = state.particles.length;
    if (n > cur) {
      for (let i = 0; i < n - cur; i++) state.particles.push(spawnParticle());
    } else if (n < cur) {
      state.particles.length = n;
    }
  }

  // ===== Física =====
  function update() {
    const { x: mx, y: my, radius: mr } = state.mouse;

    for (const p of state.particles) {
      // Repulsión del cursor
      if (state.repel && mx >= 0 && my >= 0) {
        const dx = mx - p.x, dy = my - p.y;
        const d = Math.hypot(dx, dy);
        if (d > 0 && d < mr) {
          const f = (mr - d) / mr;           // 0..1
          const inv = 1 / d;
          // ligerísima reducción por tamaño para que las grandes “pesen” más
          const mass = 0.7 + (p.r - CONFIG.sizeRange[0]) / (CONFIG.sizeRange[1] - CONFIG.sizeRange[0]) * 0.6;
          p.x -= dx * inv * 1.6 * f / mass;
          p.y -= dy * inv * 1.6 * f / mass;
        }
      }

      // Movimiento base
      p.x += p.vx;
      p.y += p.vy;

      // Rebotes en bordes (el radio cuenta para no “cortar” el punto)
      if (p.x < p.r || p.x > state.w - p.r) { p.vx *= -1; p.x = Math.max(p.r, Math.min(state.w - p.r, p.x)); }
      if (p.y < p.r || p.y > state.h - p.r) { p.vy *= -1; p.y = Math.max(p.r, Math.min(state.h - p.r, p.y)); }
    }
  }

  // ===== Dibujo =====
  function draw() {
    ctx.clearRect(0, 0, state.w, state.h);

    // Puntos (usamos el radio de cada partícula)
    ctx.fillStyle = 'rgba(255,255,255,0.92)';
    for (const p of state.particles) {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
    }

    // Líneas
    const L2 = state.linkDistance * state.linkDistance;
    for (let i = 0; i < state.particles.length; i++) {
      const a = state.particles[i];
      for (let j = i + 1; j < state.particles.length; j++) {
        const b = state.particles[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const d2 = dx * dx + dy * dy;
        if (d2 < L2) {
          const t = 1 - (Math.sqrt(d2) / state.linkDistance);
          // opacidad suave; influida un pelín por el tamaño
          const sizeMix = (a.r + b.r) / (CONFIG.sizeRange[0] + CONFIG.sizeRange[1]);
          ctx.globalAlpha = 0.10 + t * (0.20 + sizeMix * 0.05);
          ctx.strokeStyle = 'rgba(255,255,255,0.85)';
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }
    ctx.globalAlpha = 1;
  }

  function loop() {
    update();
    draw();
    animationId = requestAnimationFrame(loop);
  }

  // ===== Puntero (anti-jank) =====
  let heroRect = null;
  let pmRAF = null, lastEvt = null;

  function cacheRect() {
    if (!heroRoot) return;
    heroRect = heroRoot.getBoundingClientRect(); // px CSS
  }

  function onPointerMove(e) {
    lastEvt = e;
    if (pmRAF) return;
    pmRAF = requestAnimationFrame(() => {
      pmRAF = null;
      if (!heroRect) cacheRect();
      state.mouse.x = lastEvt.clientX - heroRect.left;
      state.mouse.y = lastEvt.clientY - heroRect.top;
    });
  }

  function onPointerLeave() {
    state.mouse.x = -9999;
    state.mouse.y = -9999;
  }

  // ===== Ciclo de vida =====
  function start() {
    if (!ensureCanvas()) return;

    initCanvasSize();

    heroRoot.addEventListener('pointermove', onPointerMove, { passive: true });
    heroRoot.addEventListener('pointerleave', onPointerLeave);

    window.addEventListener('resize', () => { initCanvasSize(); }, { passive: true });
    window.addEventListener('scroll', () => { requestAnimationFrame(cacheRect); }, { passive: true });
    window.addEventListener('pageshow', () => { cacheRect(); });

    if ('ResizeObserver' in window) {
      const ro = new ResizeObserver(() => { initCanvasSize(); });
      ro.observe(heroRoot);
    }

    if (!animationId) animationId = requestAnimationFrame(loop);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }

  // Debug en consola
  window.__heroParticles = { state, config: CONFIG };
})();
