// ===== Filtros de Apps =====
function setupFilters() {
  const grid = document.getElementById('apps-grid');
  if (!grid) return;
  const cards = Array.from(grid.querySelectorAll('.app-card'));
  const buttons = Array.from(document.querySelectorAll('.filter-btn'));
  const search = document.getElementById('app-search');
  const sort = document.getElementById('app-sort');

  let currentFilter = 'all';
  let query = '';
  let order = sort?.value || 'popular';

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      render();
    });
  });

  function debounce(fn, ms) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); } }
  search?.addEventListener('input', debounce(() => { query = (search.value || '').toLowerCase().trim(); render(); }, 120));
  sort?.addEventListener('change', () => { order = sort.value; render(); });

  function render() {
    const filtered = cards.filter(card => {
      const tags = (card.dataset.tags || '').split(',').map(s => s.trim());
      const matchesTag = currentFilter === 'all' || tags.includes(currentFilter);
      const title = (card.dataset.title || '').toLowerCase();
      const matchesText = !query || title.includes(query);
      card.classList.toggle('hidden', !(matchesTag && matchesText));
      return matchesTag && matchesText;
    });
    filtered.sort((a, b) => {
      if (order === 'popular') return (parseInt(b.dataset.popularity || '0') - parseInt(a.dataset.popularity || '0'));
      if (order === 'new') return (new Date(b.dataset.date) - new Date(a.dataset.date));
      if (order === 'az') return (a.dataset.title || '').localeCompare(b.dataset.title || '');
      return 0;
    });
    filtered.forEach(el => grid.appendChild(el));
  }

  render();
}

// ===== Ratings + Testimonios (apps) =====
function enhanceRatings() {
  const cards = document.querySelectorAll('.app-card');
  cards.forEach(card => {
    if (card.querySelector('.rating-wrap')) return;
    const title = card.dataset.title || 'app';
    const key = 'rating:' + title;
    const initial = Math.round(parseFloat(card.dataset.rating || '0')) || 4;
    const saved = parseInt(localStorage.getItem(key) || '0');
    let rating = saved > 0 ? saved : initial;

    const wrap = document.createElement('div');
    wrap.className = 'rating-wrap';
    const row = document.createElement('div');
    row.className = 'flex items-center justify-between';

    const starsBox = document.createElement('div');
    starsBox.className = 'stars';
    const label = document.createElement('span');
    label.className = 'text-xs text-gray-400';
    label.textContent = rating + '/5';

    function starSVG() {
      const ns = 'http://www.w3.org/2000/svg';
      const svg = document.createElementNS(ns, 'svg');
      svg.setAttribute('viewBox', '0 0 24 24');
      svg.setAttribute('class', 'star');
      const p = document.createElementNS(ns, 'path');
      p.setAttribute('d', 'M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z');
      p.setAttribute('fill', 'currentColor');
      svg.appendChild(p);
      return svg;
    }
    function paint(n) {
      starsBox.querySelectorAll('.star').forEach((s, i) => {
        s.classList.toggle('filled', i < n);
      });
      label.textContent = n + '/5';
    }
    for (let i = 0; i < 5; i++) {
      const s = starSVG();
      if (i < rating) s.classList.add('filled');
      s.addEventListener('mouseenter', () => paint(i + 1));
      s.addEventListener('mouseleave', () => paint(rating));
      s.addEventListener('click', () => { rating = i + 1; paint(rating); localStorage.setItem(key, String(rating)); });
      starsBox.appendChild(s);
    }
    row.appendChild(starsBox);
    row.appendChild(label);
    wrap.appendChild(row);

    const quote = card.dataset.quote;
    if (quote) {
      const q = document.createElement('p');
      q.className = 'testimonial';
      q.textContent = '“' + quote + '”';
      wrap.appendChild(q);
    }
    card.appendChild(wrap);
  });
}
