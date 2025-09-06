// Tilt en tarjetas (servicios + apps)
function tiltApps(selector) {
  const cards = document.querySelectorAll(selector);
  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const r = card.getBoundingClientRect();
      const x = e.clientX - r.left; const y = e.clientY - r.top;
      const rx = ((y / r.height) - 0.5) * 8;
      const ry = ((x / r.width) - 0.5) * -8;
      card.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(900px) rotateX(0) rotateY(0)';
    });
  });
}

// Servicios: tilt + brillo que sigue al mouse
function tiltSvcCards() {
  const cards = document.querySelectorAll('.svc-card');
  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const r = card.getBoundingClientRect();
      const x = e.clientX - r.left; const y = e.clientY - r.top;
      const nx = (x / r.width) - 0.5;
      const ny = (y / r.height) - 0.5;

      const rx = ny * 6;            // rotateX
      const ry = -nx * 6;           // rotateY
      card.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg)`;

      const gx = 50 - nx * 12; // %
      const gy = 38 - ny * 10; // %
      card.style.setProperty('--gx', `${gx}%`);
      card.style.setProperty('--gy', `${gy}%`);
      card.style.setProperty('--sheen-alpha', '.16');
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(900px) rotateX(0) rotateY(0)';
      card.style.setProperty('--gx', '50%');
      card.style.setProperty('--gy', '38%');
      card.style.setProperty('--sheen-alpha', '.12');
    });
  });
}
