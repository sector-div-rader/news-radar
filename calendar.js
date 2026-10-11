(async function () {
  const res = await fetch('data/index.json?v=' + Date.now());
  const idx = await res.json();

  const calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {
    initialView: 'dayGridMonth',
    locale: 'zh-hk',
    events: idx.dates.map(d => ({ title: '有記錄', start: d, color: '#4f8cff' })),
    dateClick: async (info) => {
      const date = info.dateStr;
      if (!idx.dates.includes(date)) return;
      const day = await (await fetch(`data/${date}.json?v=` + Date.now())).json();
      document.getElementById('day-content').innerHTML =
        `<h2>${date}</h2>` +
        day.items.map(it => `
          <div class="card">
            <span class="tag">${it.category}</span>
            <a href="${it.url}" target="_blank">${it.title}</a>
          </div>
        `).join('');
    }
  });
  calendar.render();
})();
