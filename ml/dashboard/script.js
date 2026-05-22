const API_BASE = window.location.origin;

const els = {
  status: document.getElementById("api-status"),
  rawCount: document.getElementById("raw-count"),
  processedCount: document.getElementById("processed-count"),
  avgTrend: document.getElementById("avg-trend"),
  growth: document.getElementById("growth"),
  trendsList: document.getElementById("trends-list"),
  sentimentPositive: document.getElementById("sentiment-positive"),
  sentimentNeutral: document.getElementById("sentiment-neutral"),
  sentimentNegative: document.getElementById("sentiment-negative"),
  searchForm: document.getElementById("search-form"),
  searchInput: document.getElementById("search-input"),
  searchResults: document.getElementById("search-results"),
  refreshBtn: document.getElementById("refresh-btn"),
};

function fmtNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "-";
  }
  return Number(value).toLocaleString();
}

function setStatus(text, ok = true) {
  els.status.textContent = text;
  const dot = document.querySelector(".status-dot");
  dot.style.background = ok ? "#16a34a" : "#ef4444";
}

async function fetchJson(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || `Request failed: ${res.status}`);
  }
  return res.json();
}

function renderTrends(items) {
  els.trendsList.innerHTML = "";
  if (!items.length) {
    els.trendsList.innerHTML = '<li><span class="muted">No trend data yet.</span></li>';
    return;
  }

  items.slice(0, 8).forEach((item, index) => {
    const li = document.createElement("li");
    li.innerHTML = `<span>#${index + 1} ${item.keyword}</span><b>${fmtNumber(item.count)}</b>`;
    els.trendsList.appendChild(li);
  });
}

function setSentimentBars(data) {
  const positive = Number(data.positive || 0);
  const neutral = Number(data.neutral || 0);
  const negative = Number(data.negative || 0);
  const total = positive + neutral + negative || 1;

  els.sentimentPositive.style.width = `${(positive / total) * 100}%`;
  els.sentimentNeutral.style.width = `${(neutral / total) * 100}%`;
  els.sentimentNegative.style.width = `${(negative / total) * 100}%`;

  els.sentimentPositive.title = `${positive} items`;
  els.sentimentNeutral.title = `${neutral} items`;
  els.sentimentNegative.title = `${negative} items`;
}

function renderSearch(items) {
  els.searchResults.innerHTML = "";
  if (!items.length) {
    els.searchResults.innerHTML = '<tr><td colspan="4" class="muted">No matches found.</td></tr>';
    return;
  }

  items.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${(item.title || "Untitled").slice(0, 80)}</td>
      <td>${item.source || "-"}</td>
      <td>${item.sentiment || "-"}</td>
      <td>${fmtNumber(item.trend_score)}</td>
    `;
    els.searchResults.appendChild(row);
  });
}

async function loadDashboardData() {
  try {
    const [summary, trends, insights] = await Promise.all([
      fetchJson("/analytics/summary?days=7"),
      fetchJson("/trends?days=7&page=1&page_size=10"),
      fetchJson("/insights?page=1&page_size=5"),
    ]);

    els.rawCount.textContent = fmtNumber(summary.raw_count);
    els.processedCount.textContent = fmtNumber(summary.processed_count);
    els.avgTrend.textContent = fmtNumber(summary.avg_trend_score);
    els.growth.textContent = `${fmtNumber(summary.growth_percentage)}%`;

    renderTrends(trends.items || []);
    setSentimentBars(insights.sentiment_distribution || {});
    setStatus("API connected", true);
  } catch (error) {
    setStatus("API connection error", false);
    console.error(error);
  }
}

els.searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = els.searchInput.value.trim();
  if (query.length < 2) {
    return;
  }

  try {
    const response = await fetchJson(`/search?q=${encodeURIComponent(query)}&page=1&page_size=10`);
    renderSearch(response.items || []);
  } catch (error) {
    els.searchResults.innerHTML = `<tr><td colspan="4" class="muted">${error.message}</td></tr>`;
  }
});

els.refreshBtn.addEventListener("click", loadDashboardData);

loadDashboardData();
