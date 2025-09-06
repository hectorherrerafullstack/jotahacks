// ===== Canvas Particles (versión fluida y simple) =====
const canvas = document.getElementById('hero-canvas');
let ctx = null;
let animationId = null;

const DPR = Math.min(window.devicePixelRatio || 1, 2);
const state = {
  w: 0, h: 0,
  particles: [],
  linkDistance: 140,
  baseSpeed: .4,
  density: 24000,
  mouse: { x: -9999, y: -9999, radius: 110, breakRadius: 52 },
  repel: true
};

function initCanvasSize() {
  if (!canvas) return;
  const hero = document.querySelector('.hero-section');
  const w = hero?.clientWidth || window.innerWidth;
  const h = hero?.clientHeight || Math.max(480, Math.floor(window.innerHeight * 0.86));
  state.w = w; state.h = h;
  canvas.style.width = w + 'px';
  canvas.style.height = h + 'px';
  canvas.width = Math.floor(w * DPR);
  canvas.height = Math.floor(h * DPR);
  if (!ctx) { ctx = canvas.getContext('2d'); }
  if (!ctx) return;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.scale(DPR, DPR);
  const target = Math.max(56, Math.min(180, Math.floor((w * h) / state.density)));
  const cur = state.particles.length;
  if (cur < target) { for (let i = 0; i < target - cur; i++) state.particles.push(makeParticle()); }
  else if (cur > target) { state.particles.length = target; }
}

function rand(min, max) { return Math.random() * (max - min) + min; }
function makeParticle() {
  const angle = Math.random() * Math.PI * 2;
  return {
    x: Math.random() * state.w, y: Math.random() * state.h,
    vx: Math.cos(angle) * state.baseSpeed + rand(-.1, .1),
    vy: Math.sin(angle) * state.baseSpeed + rand(-.1, .1), r: rand(1.2, 3.4), a: rand(.38, .9)
  };
}

function update() {
  for (const p of state.particles) {
    if (state.repel) {
      const dx = state.mouse.x - p.x;
      const dy = state.mouse.y - p.y;
      const dist = Math.hypot(dx, dy);
      if (dist < state.mouse.radius) {
        const f = (state.mouse.radius - dist) / state.mouse.radius;
        p.x -= (dx / dist) * f * 1.8;
        p.y -= (dy / dist) * f * 1.8;
      }
    }
    
    p.x += p.vx;
    p.y += p.vy;
    
    if (p.x <= 0 || p.x >= state.w) {
      p.vx *= -1;
      p.x = Math.max(0, Math.min(state.w, p.x));
    }
    if (p.y <= 0 || p.y >= state.h) {
      p.vy *= -1;
      p.y = Math.max(0, Math.min(state.h, p.y));
    }
  }
}

function draw() {
  if (!ctx) return;
  
  ctx.clearRect(0, 0, state.w, state.h);
  
  // Dibujar partículas
  for (const p of state.particles) {
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255,255,255,${p.a})`;
    ctx.fill();
  }
  
  // Dibujar líneas
  const particles = state.particles;
  for (let i = 0; i < particles.length - 1; i++) {
    const a = particles[i];
    for (let j = i + 1; j < particles.length; j++) {
      const b = particles[j];
      const dx = a.x - b.x;
      const dy = a.y - b.y;
      const d = Math.hypot(dx, dy);
      
      if (d < state.linkDistance) {
        // Check si el mouse interrumpe la línea
        if (!segmentCircleIntersects(a.x, a.y, b.x, b.y, state.mouse.x, state.mouse.y, state.mouse.breakRadius)) {
          const alpha = (1 - (d / state.linkDistance)) * 0.5;
          ctx.strokeStyle = `rgba(255,255,255,${alpha})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }
  }
}

function segmentCircleIntersects(ax, ay, bx, by, cx, cy, r) {
  const dX = bx - ax, dY = by - ay; const fX = ax - cx, fY = ay - cy;
  const A = dX * dX + dY * dY; const B = 2 * (fX * dX + fY * dY); const C = (fX * fX + fY * fY) - r * r;
  let disc = B * B - 4 * A * C; if (disc < 0) return false; disc = Math.sqrt(disc);
  const t1 = (-B - disc) / (2 * A); const t2 = (-B + disc) / (2 * A);
  return (t1 >= 0 && t1 <= 1) || (t2 >= 0 && t2 <= 1);
}

function loop() {
  update();
  draw();
  animationId = requestAnimationFrame(loop);
}

function handleVisibilityChange() {
  if (document.hidden) {
    if (animationId) {
      cancelAnimationFrame(animationId);
      animationId = null;
    }
  } else {
    if (!animationId) {
      animationId = requestAnimationFrame(loop);
    }
  }
}

function startParticles() {
  initCanvasSize();
  
  const hero = document.querySelector('.hero-section');
  if (hero && 'ResizeObserver' in window) {
    const ro = new ResizeObserver(() => initCanvasSize());
    ro.observe(hero);
  }
  
  window.addEventListener('resize', initCanvasSize);
  
  window.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    state.mouse.x = e.clientX - rect.left;
    state.mouse.y = e.clientY - rect.top;
  });
  
  window.addEventListener('mouseleave', () => {
    state.mouse.x = -9999;
    state.mouse.y = -9999;
  });
  
  document.addEventListener('visibilitychange', handleVisibilityChange);
  
  animationId = requestAnimationFrame(loop);
}
