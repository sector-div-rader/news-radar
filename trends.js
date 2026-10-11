(async function () {
  const kw = await (await fetch('data/keywords.json?v=' + Date.now())).json();
  const idx = await (await fetch('data/index.json?v=' + Date.now())).json();
  const dates = [...idx.dates].reverse();

  // 揀 top 5 關鍵詞
  const totals = Object.entries(kw).map(([k, v]) => [
    k, Object.values(v).reduce((a, b) => a + b, 0)
  ]).sort((a, b) => b[1] - a[1]).slice(0, 5);

  const colors = ['#4f8cff', '#f778ba', '#3fb950', '#d29922', '#a371f7'];

  new Chart(document.getElementById('chart'), {
    type: 'line',
    data: {
      labels: dates,
      datasets: totals.map(([k], i) => ({
        label: k,
        data: dates.map(d => kw[k][d] || 0),
        borderColor: colors[i],
        tension: 0.3,
      }))
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: getComputedStyle(document.body).color } } },
      scales: {
        x: { ticks: { color: getComputedStyle(document.body).color } },
        y: { ticks: { color: getComputedStyle(document.body).color } },
      }
    }
  });

  // Tag 雲
  const allTotals = Object.entries(kw).map(([k, v]) => [
    k, Object.values(v).reduce((a, b) => a + b, 0)
  ]);
  WordCloud(document.getElementById('cloud'), {
    list: allTotals,
    gridSize: 8,
    weightFactor: 4,
    fontFamily: 'sans-serif',
    color: () => colors[Math.floor(Math.random() * colors.length)],
    backgroundColor: 'transparent',
  });
})();
