let searchIndex = [];
let fuse = null;

async function loadIndex() {
  const res = await fetch('data/index.json?v=' + Date.now());
  return res.json();
}

async function loadDay(date) {
  const res = await fetch(`data/${date}.json?v=` + Date.now());
  return res.json();
}

async function loadSearchIndex() {
  const res = await fetch('data/search-index.json?v=' + Date.now());
  searchIndex = await res.json();
  fuse = new Fuse(searchIndex, {
    keys: ['title', 'keywords'],
    threshold: 0.3,
  });
}

function renderItems(items) {
  return items.map(it => `
    <div class="card">
      <span class="tag">${it.category}</span>
      <a href="${it.url}" target="_blank" rel="noopener">${it.title}</a>
      <div class="meta">${it.source} · ${it.date}</div>
    </div>
  `).join('');
}

async function renderList() {
  const idx = await loadIndex();
  const list = document.getElementById('list');
  list.innerHTML = '';

  for (let i = 0; i < idx.dates.length; i++) {
    const date = idx.dates[i];
    const day = await loadDay(date);
    const details = document.createElement('details');
    details.open = i === 0; // 最新展開
    details.innerHTML = `
      <summary>${date}（${day.items.length} 條）</summary>
      <div class="day-items">${renderItems(day.items)}</div>
    `;
    list.appendChild(details);
  }
}

function setupSearch() {
  const input = document.getElementById('search');
  const results = document.getElementById('results');
  const list = document.getElementById('list');

  input.addEventListener('input', () => {
    const q = input.value.trim();
    if (!q) {
      results.innerHTML = '';
      list.style.display = '';
      return;
    }
    list.style.display = 'none';
    const hits = fuse.search(q).slice(0, 50).map(r => r.item);
    results.innerHTML = hits.length
      ? renderItems(hits)
      : '<p>冇搵到結果</p>';
  });
}

(async function init() {
  await loadSearchIndex();
  await renderList();
  setupSearch();
})();
