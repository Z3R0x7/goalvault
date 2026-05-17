document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("verify-chain-btn");
  const result = document.getElementById("verify-result");
  if (!btn || !result) return;

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    btn.textContent = "Verifying...";
    try {
      const res = await fetch("/api/audit/verify");
      const data = await res.json();
      result.classList.remove("d-none", "chain-intact", "chain-broken");
      result.classList.add(data.intact ? "chain-intact" : "chain-broken");
      const badge = document.getElementById("chain-status");
      if (badge) {
        badge.textContent = data.intact ? "INTACT" : "COMPROMISED";
        badge.className = "chain-badge " + (data.intact ? "chain-intact" : "chain-broken");
      }
      result.innerHTML = `<strong>${data.message}</strong> — ${data.total_entries} entries checked.`;
      if (!data.intact) {
        result.innerHTML += ` Broken at entry #${data.broken_at_id}.`;
      }
    } catch (e) {
      result.classList.remove("d-none");
      result.classList.add("chain-broken");
      result.textContent = "Verification failed: " + e.message;
    }
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-link-45deg"></i> Verify Chain Integrity';
  });
});
