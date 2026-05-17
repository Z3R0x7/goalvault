async function analyseGoal() {
  const btn = document.getElementById("ai-analyse-btn");
  const panel = document.getElementById("ai-result-panel");
  if (!btn || !panel) return;

  btn.innerHTML =
    '<span class="spinner-border spinner-border-sm"></span> Analysing...';
  btn.disabled = true;

  const csrf =
    document.getElementById("csrf_token_val")?.value ||
    document.querySelector('[name=csrf_token]')?.value;

  const payload = {
    title: document.getElementById("title")?.value || "",
    description: document.getElementById("description")?.value || "",
    uom_type: document.getElementById("uom_type")?.value || "numeric_min",
    target: document.getElementById("target")?.value || 0,
  };

  try {
    const res = await fetch("/api/ai/analyse-goal", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrf,
      },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    renderAIResult(data);
  } catch (e) {
    panel.innerHTML = `<p class="text-danger">Error: ${e.message}</p>`;
    panel.style.display = "block";
  }

  btn.innerHTML = "Analyse My Goal";
  btn.disabled = false;
}

function renderAIResult(data) {
  const panel = document.getElementById("ai-result-panel");
  if (!panel) return;

  if (data.error && !data.quality_score) {
    panel.innerHTML = `<p class="text-warning">${data.error}</p>`;
    panel.style.display = "block";
    return;
  }

  const score = data.quality_score || 0;
  const color = score >= 7 ? "success" : score >= 4 ? "warning" : "danger";
  const issues = data.issues || [];
  const suggestions = data.suggestions || [];
  const demo = data.demo_mode
    ? '<p class="small text-info">Demo mode — add GROQ_API_KEY for live AI.</p>'
    : "";

  panel.innerHTML = `
    <div class="d-flex align-items-center mb-2">
      <span class="badge bg-${color} fs-5 me-2">${score}/10</span>
      <strong>Goal Quality Score</strong>
    </div>
    ${demo}
    ${
      issues.length
        ? `<p class="text-danger mb-1"><strong>Issues:</strong></p><ul>${issues.map((i) => `<li>${i}</li>`).join("")}</ul>`
        : ""
    }
    <p class="text-success mb-1"><strong>Suggestions:</strong></p>
    <ul>${suggestions.map((s) => `<li>${s}</li>`).join("")}</ul>
    <small class="text-muted">${data.uom_comment || ""}</small>
  `;
  panel.style.display = "block";
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("ai-analyse-btn")?.addEventListener("click", analyseGoal);
});
