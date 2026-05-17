fetch("/api/analytics/summary")
  .then(r => r.json())
  .then(data => {
    const tc = "#8B949E";
    new Chart(document.getElementById("funnelChart"), {
      type: "bar",
      data: {
        labels: data.funnel.labels,
        datasets: [{ data: data.funnel.values, backgroundColor: "#00C8A0" }]
      },
      options: { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { ticks: { color: tc }, grid: { color: "#30363D" } }, y: { ticks: { color: tc } } } }
    });
    new Chart(document.getElementById("distChart"), {
      type: "doughnut",
      data: {
        labels: data.distribution.labels,
        datasets: [{ data: data.distribution.values, backgroundColor: ["#3FB950","#D29922","#F85149"] }]
      },
      options: { plugins: { legend: { labels: { color: tc } } } }
    });
    const tbody = document.querySelector("#heatmapTable tbody");
    data.heatmap.forEach(row => {
      const cls = v => v == null ? "" : v >= 80 ? "heat-high" : v >= 50 ? "heat-mid" : "heat-low";
      const fmt = v => v == null ? "—" : v + "%";
      tbody.innerHTML += `<tr><td>${row.department}</td><td class="heat-cell ${cls(row.approved_pct)}">${row.approved_pct}%</td>
        <td class="heat-cell ${cls(row.quarters.Q1)}">${fmt(row.quarters.Q1)}</td>
        <td class="heat-cell ${cls(row.quarters.Q2)}">${fmt(row.quarters.Q2)}</td>
        <td class="heat-cell ${cls(row.quarters.Q3)}">${fmt(row.quarters.Q3)}</td>
        <td class="heat-cell ${cls(row.quarters.Q4)}">${fmt(row.quarters.Q4)}</td></tr>`;
    });
  });
