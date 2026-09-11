const form = document.getElementById("form");
const urlInput = document.getElementById("url");
const submitBtn = document.getElementById("submit");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");

function setStatus(message, isError = false) {
  statusEl.hidden = !message;
  statusEl.textContent = message || "";
  statusEl.classList.toggle("error", isError);
}

function formatDuration(seconds) {
  const s = Math.round(seconds || 0);
  const m = Math.floor(s / 60);
  const rest = s % 60;
  return `${m}:${String(rest).padStart(2, "0")} min`;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const url = urlInput.value.trim();
  if (!url) return;

  submitBtn.disabled = true;
  resultEl.hidden = true;
  setStatus("Video wird heruntergeladen und transkribiert – das kann je nach Länge etwas dauern …");

  try {
    const res = await fetch("/api/transcribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Unbekannter Fehler");
    }

    document.getElementById("meta-title").textContent = data.title;
    document.getElementById("meta-info").textContent =
      ` · ${data.platform} · ${formatDuration(data.duration)} · erkannte Sprache: ${data.detected_language || "unbekannt"}`;
    document.getElementById("text-de").textContent = data.transcript_de;
    document.getElementById("text-en").textContent = data.transcript_en;

    resultEl.hidden = false;
    setStatus("");
  } catch (err) {
    setStatus(err.message, true);
  } finally {
    submitBtn.disabled = false;
  }
});

document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`panel-${btn.dataset.target}`).classList.add("active");
  });
});

document.querySelectorAll(".copy-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const text = document.getElementById(btn.dataset.target).textContent;
    try {
      await navigator.clipboard.writeText(text);
      const original = btn.textContent;
      btn.textContent = "Kopiert!";
      setTimeout(() => (btn.textContent = original), 1500);
    } catch {
      /* Zwischenablage nicht verfügbar – ignorieren */
    }
  });
});
