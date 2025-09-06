// ==============================
// Navbar móvil + Typing minimal
// ==============================
(() => {

  // -------- Typing minimal --------
  const typingText = document.getElementById('typing-text');

  // Si no existe el nodo, salir sin error
  if (!typingText) return;

  // Respeta usuarios con "reduced motion"
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Frases
  const phrases = [
    'software a medida?',
    'automatización con IA?',
    'integraciones API?',
    'un ERP/CRM propio?',
    'chatbots inteligentes?',
    'optimización de rutas?',
    'dashboards en tiempo real?',
    'digitalizar procesos?'
  ];

  // Índices y estados
  let p = 0;        // índice de frase
  let i = 0;        // índice de carácter
  let del = false;  // modo borrado
  let rafId = null; // id de requestAnimationFrame
  let lastTime = 0; // marca de tiempo para control de velocidad

  // Velocidades (ms)
  const SPEED_TYPE = 120;
  const SPEED_DELETE = 60;
  const PAUSE_END = 1100;
  const PAUSE_NEXT = 280;

  // Si reduce-motion, fija una frase y termina
  if (prefersReduced) {
    typingText.textContent = phrases[0];
    return;
  }

  function schedule(nextDelay) {
    // Pequeño planificador basado en rAF para mantener frames suaves
    const start = performance.now();
    function loop(now) {
      if (now - start >= nextDelay) {
        type();
        return;
      }
      rafId = requestAnimationFrame(loop);
    }
    rafId = requestAnimationFrame(loop);
  }

  function type(now = 0) {
    // Control básico de tiempo para no spamear frames
    if (now - lastTime < 16) {
      rafId = requestAnimationFrame(type);
      return;
    }
    lastTime = now;

    const word = phrases[p] || '';
    typingText.textContent = word.slice(0, i);

    if (!del && i < word.length) {
      i++;
      schedule(SPEED_TYPE);
    } else if (del && i > 0) {
      i--;
      schedule(SPEED_DELETE);
    } else {
      // Cambio de estado cuando se termina de escribir o borrar
      del = !del;
      if (!del) {
        p = (p + 1) % phrases.length;
      }
      schedule(del ? PAUSE_END : PAUSE_NEXT);
    }
  }

  // Pausa y reanuda cuando la pestaña no está visible (ahorra batería y evita saltos)
  const handleVisibility = () => {
    if (document.hidden) {
      if (rafId) cancelAnimationFrame(rafId);
      rafId = null;
    } else {
      // Reinicia el ciclo suavemente
      if (!rafId) rafId = requestAnimationFrame(type);
    }
  };
  document.addEventListener('visibilitychange', handleVisibility);

  // Arranque
  rafId = requestAnimationFrame(type);
})();
