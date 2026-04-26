const form = document.getElementById("localizeForm");
const submitButton = document.getElementById("submitButton");
const statusEl = document.getElementById("formStatus");
const summaryEl = document.getElementById("resultSummary");
const primaryResultEl = document.getElementById("primaryResult");
const variationListEl = document.getElementById("variationList");
const explanationListEl = document.getElementById("explanationList");
const culturalListEl = document.getElementById("culturalList");
const historyListEl = document.getElementById("historyList");
const loadingStateEl = document.getElementById("loadingState");
const historyToggleEl = document.getElementById("historyToggle");

let latestResult = null;

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function getCsrfToken() {
  const metaToken = document.querySelector('meta[name="csrf-token"]')?.content;
  if (metaToken) {
    return metaToken;
  }

  const inputToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
  if (inputToken) {
    return inputToken;
  }

  const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

function redirectToLogin() {
  const nextUrl = encodeURIComponent(window.location.pathname + window.location.search);
  window.location.href = `/auth/login/?next=${nextUrl}`;
}

async function apiFetch(url, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers = new Headers(options.headers || {});

  if (!["GET", "HEAD", "OPTIONS", "TRACE"].includes(method)) {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      headers.set("X-CSRFToken", csrfToken);
    }
  }

  const response = await fetch(url, {
    credentials: "same-origin",
    ...options,
    headers,
  });

  if (response.status === 401) {
    redirectToLogin();
    throw new Error("Your session expired. Please sign in again.");
  }

  return response;
}

function setStatus(message, isError = false) {
  if (!statusEl) {
    return;
  }

  statusEl.textContent = message;
  statusEl.style.color = isError ? "#a43838" : "#506367";
}

function setLoadingState(loading) {
  if (!submitButton || !loadingStateEl) {
    return;
  }

  if (loading) {
    submitButton.classList.add("is-loading");
    submitButton.disabled = true;
    loadingStateEl.classList.remove("hidden");
  } else {
    submitButton.classList.remove("is-loading");
    submitButton.disabled = false;
    loadingStateEl.classList.add("hidden");
  }
}

function renderExplanation(explanations = []) {
  if (!explanationListEl) {
    return;
  }

  explanationListEl.innerHTML = explanations.length
    ? explanations
        .map((item) => `<div class="info-item"><p><strong>${escapeHtml(item.type || "note")}:</strong> ${escapeHtml(item.message || item.detail || "Updated.")}</p></div>`)
        .join("")
    : '<div class="info-item"><p>No explanation was returned.</p></div>';
}

function renderCulturalReview(review = {}) {
  if (!culturalListEl) {
    return;
  }

  const flags = review.flags || [];
  const recommendations = review.recommendations || [];
  const items = [];

  if (typeof review.score !== "undefined") {
    items.push(`<div class="info-item"><p><strong>Risk score:</strong> ${escapeHtml(review.score)}</p></div>`);
  }
  flags.forEach((flag) => {
    items.push(`<div class="info-item"><p><strong>${escapeHtml(flag.term)}</strong> - ${escapeHtml(flag.message)}</p></div>`);
  });
  recommendations.forEach((note) => {
    items.push(`<div class="info-item"><p>${escapeHtml(note)}</p></div>`);
  });

  culturalListEl.innerHTML = items.length ? items.join("") : '<div class="info-item"><p>No cultural flags detected.</p></div>';
}

function renderVariations(variations = []) {
  if (!variationListEl) {
    return;
  }

  const order = ["formal", "casual", "marketing"];
  const variationMap = new Map(variations.map((item) => [String(item.variant_name || "").toLowerCase(), item]));
  const resolved = order.map((name) => variationMap.get(name) || {
    variant_name: name,
    localized_text: "Not generated in current response.",
    cultural_risk_score: "-",
    id: "",
  });

  variationListEl.innerHTML = resolved.length
    ? resolved.map((variation) => `
      <article class="variation-card" data-variation-id="${escapeHtml(variation.id || variation.variant_name)}">
        <div class="badge-row">
          <span class="badge">${escapeHtml(variation.variant_name)}</span>
          <span class="badge">Risk ${escapeHtml(variation.cultural_risk_score ?? 0)}</span>
        </div>
        <h4>${escapeHtml(variation.variant_name)} variation</h4>
        <p>${escapeHtml(variation.localized_text)}</p>
        <p class="feedback-counts">Likes ${escapeHtml(variation.like_count ?? 0)} | Dislikes ${escapeHtml(variation.dislike_count ?? 0)}</p>
        <div class="card-actions">
          <button type="button" class="like-btn" data-variation-id="${escapeHtml(variation.id || "")}">Like</button>
          <button type="button" class="dislike-btn" data-variation-id="${escapeHtml(variation.id || "")}">Dislike</button>
        </div>
      </article>
    `).join("")
    : '<div class="summary empty-state">No variations generated yet.</div>';

  document.querySelectorAll(".like-btn, .dislike-btn").forEach((button) => {
    button.addEventListener("click", submitFeedback);
  });
}

function renderPrimaryResult(result = {}) {
  if (!primaryResultEl) {
    return;
  }

  const sourceLanguage = String(result.source_language || "en").toUpperCase();
  const targetLanguage = String(result.target_language || "en").toUpperCase();
  const tone = result.tone || "neutral";
  const localizedText = result.localized_text || "No localized text generated yet.";

  primaryResultEl.innerHTML = `
    <div class="badge-row primary-badges">
      <span class="badge">${escapeHtml(sourceLanguage)} -> ${escapeHtml(targetLanguage)}</span>
      <span class="badge">${escapeHtml(tone)}</span>
    </div>
    <h4>Selected output</h4>
    <p>${escapeHtml(localizedText)}</p>
  `;
}

function renderSummary(result) {
  if (!summaryEl) {
    return;
  }

  summaryEl.innerHTML = `
    <strong>${escapeHtml(result.sentiment_label || "neutral")}</strong> sentiment detected with score ${escapeHtml(result.sentiment_score ?? 0)}.
    <br>
    Intent preserved: ${result.intent_preserved ? "yes" : "no"} | Sentiment preserved: ${result.sentiment_preserved ? "yes" : "no"}
  `;
}

async function submitFeedback(event) {
  const clickedButton = event.currentTarget;
  const variationId = clickedButton.dataset.variationId;
  const liked = clickedButton.classList.contains("like-btn");
  if (!variationId) {
    setStatus("Feedback is only available for saved variations after a submission.", true);
    return;
  }

  try {
    const response = await apiFetch("/api/feedback/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        localization_job_id: latestResult?.job_id,
        variation_id: variationId,
        liked,
      }),
    });
    if (!response.ok) {
      throw new Error("Feedback submission failed");
    }
    const card = clickedButton.closest(".variation-card");
    if (card) {
      card.querySelectorAll(".like-btn, .dislike-btn").forEach((btn) => btn.classList.remove("selected"));
      clickedButton.classList.add("selected");

      const feedbackCounts = card.querySelector(".feedback-counts");
      if (feedbackCounts) {
        const current = feedbackCounts.textContent.match(/Likes\s+(\d+)\s+\|\s+Dislikes\s+(\d+)/i);
        if (current) {
          const likeCount = Number(current[1]);
          const dislikeCount = Number(current[2]);
          const nextLikeCount = liked ? likeCount + 1 : likeCount;
          const nextDislikeCount = liked ? dislikeCount : dislikeCount + 1;
          feedbackCounts.textContent = `Likes ${nextLikeCount} | Dislikes ${nextDislikeCount}`;
        }
      }
    }
    setStatus(liked ? "Marked as liked." : "Marked as disliked.");
    await loadHistory();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function deleteHistoryItem(jobId) {
  try {
    const response = await apiFetch(`/api/history/${jobId}/`, {
      method: "DELETE",
    });
    if (!response.ok) {
      throw new Error("Failed to delete history item.");
    }
    setStatus("History item deleted.");
    await loadHistory();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function loadHistory() {
  if (!historyListEl) {
    return;
  }

  try {
    const response = await apiFetch("/api/history/");
    const data = await response.json();
    historyListEl.innerHTML = data.length
      ? data.map((item) => `
        <article class="history-item">
          <div class="badge-row">
            <span class="badge">${escapeHtml(item.source_language)} → ${escapeHtml(item.target_language)}</span>
            <span class="badge">${escapeHtml(item.target_region)}</span>
            <span class="badge">${escapeHtml(item.tone)}</span>
          </div>
          <h4>${escapeHtml(item.audience)}</h4>
          <p>Sentiment: ${escapeHtml(item.sentiment_label || "neutral")} (${escapeHtml(item.sentiment_score ?? 0)}) | Variations: ${escapeHtml(item.variation_count)}</p>
          <p class="history-meta">Created ${new Date(item.created_at).toLocaleString()}</p>
          <div class="card-actions">
            <button type="button" class="history-delete-btn" data-job-id="${escapeHtml(item.id)}">Delete</button>
          </div>
        </article>
      `).join("")
      : '<div class="summary empty-state">History will appear here after you generate a localization.</div>';

    historyListEl.querySelectorAll(".history-delete-btn").forEach((button) => {
      button.addEventListener("click", async () => {
        const jobId = button.dataset.jobId;
        if (!jobId) {
          return;
        }
        await deleteHistoryItem(jobId);
      });
    });
  } catch (error) {
    historyListEl.innerHTML = `<div class="summary empty-state">Unable to load history: ${escapeHtml(error.message)}</div>`;
  }
}

function initializeHistoryToggle() {
  if (!historyToggleEl || !historyListEl) {
    return;
  }

  historyToggleEl.dataset.expanded = "false";
  historyToggleEl.setAttribute("aria-expanded", "false");
  historyListEl.classList.add("hidden");

  historyToggleEl.addEventListener("click", async (event) => {
    event.preventDefault();
    const isExpanded = historyToggleEl.dataset.expanded === "true";
    const nextExpanded = !isExpanded;

    historyToggleEl.dataset.expanded = nextExpanded ? "true" : "false";
    historyToggleEl.setAttribute("aria-expanded", nextExpanded ? "true" : "false");
    historyToggleEl.textContent = nextExpanded ? "Hide history" : "Show history";
    historyListEl.classList.toggle("hidden", !nextExpanded);

    if (nextExpanded) {
      await loadHistory();
    }
  });
}

if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setStatus("Generating localized variants...");
    setLoadingState(true);

    const formData = new FormData(form);
    const payload = {
      source_text: formData.get("source_text") || "",
      source_language: formData.get("source_language") || "en",
      target_language: formData.get("target_language") || "en",
      target_region: formData.get("target_region") || "",
      tone: formData.get("tone") || "neutral",
      audience: formData.get("audience") || "general",
      preserve_intent: formData.get("preserve_intent") === "on",
      preserve_sentiment: formData.get("preserve_sentiment") === "on",
      use_ocr: formData.get("use_ocr") === "on",
    };

    const data = new FormData();
    Object.entries(payload).forEach(([key, value]) => data.append(key, value));
    const image = document.getElementById("sourceImage")?.files?.[0];
    if (image) {
      data.append("source_image", image);
    }

    try {
      const response = await apiFetch("/api/localize/", {
        method: "POST",
        body: data,
      });

      const result = await response.json();
      if (!response.ok) {
        let errorMsg = result.detail || JSON.stringify(result);

        if (errorMsg.includes("Tesseract")) {
          errorMsg += "\n\nTo enable OCR: Download and install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki, then restart this application.";
        }

        throw new Error(errorMsg);
      }

      latestResult = result;
      renderSummary(result);
      renderPrimaryResult(result);
      renderVariations(result.variations || []);
      renderExplanation(result.explanation || []);
      renderCulturalReview(result.cultural_review || {});
      setStatus("Localization completed successfully.");
      await loadHistory();
    } catch (error) {
      setStatus(error.message, true);
    } finally {
      setLoadingState(false);
    }
  });
}

initializeHistoryToggle();
loadHistory();