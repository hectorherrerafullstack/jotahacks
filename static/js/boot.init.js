document.addEventListener('DOMContentLoaded', () => {
  if (typeof type === 'function') type();             // typing (si existe)
  if (typeof startParticles === 'function') startParticles(); // <-- arranca partículas
  if (window.lucide && lucide.createIcons) lucide.createIcons();
  if (typeof tiltSvcCards === 'function') tiltSvcCards();
  if (typeof tiltApps === 'function') tiltApps('.app-card');
  if (typeof setupFilters === 'function') setupFilters();
  if (typeof enhanceRatings === 'function') enhanceRatings();
});
