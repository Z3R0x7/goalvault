function updateWeightageBar() {
  const existing = window.EXISTING_WEIGHTAGE || 0;
  const remaining = window.REMAINING_WEIGHTAGE ?? Math.max(0, 100 - existing);
  const input = document.getElementById("weightage");
  const bar = document.getElementById("weightage-bar");
  const remainingEl = document.getElementById("weightage-remaining");
  const submitBtn = document.getElementById("goal-submit-btn");

  if (!input) return;

  const current = parseFloat(input.value) || 0;
  const total = existing + current;
  const newPct = Math.min(current, remaining);

  if (bar) {
    bar.style.width = (existing + newPct) + "%";
    bar.style.maxWidth = "100%";
  }

  if (remainingEl) {
    const left = Math.max(0, remaining - current);
    remainingEl.textContent =
      left.toFixed(1) + "% available after this goal (" + existing + "% already used)";
  }

  if (submitBtn) {
    const noRoom = remaining < 10;
    const badInput =
      current > 0 &&
      (current < 10 || current > remaining + 0.001 || total > 100.001);
    submitBtn.disabled = noRoom || badInput;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const w = document.getElementById("weightage");
  if (w) {
    w.addEventListener("input", updateWeightageBar);
    updateWeightageBar();
  }
});
