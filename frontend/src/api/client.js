/**
 * Thin fetch wrapper. In dev, Vite proxies /api to the FastAPI server
 * (see vite.config.js); in production, the same FastAPI process serves
 * both the API and this built frontend, so a relative path always
 * works without an environment-specific base URL.
 */

async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // response wasn't JSON -- fall back to statusText
    }
    const error = new Error(detail);
    error.status = res.status;
    throw error;
  }

  return res.json();
}

export function getRecommendations({ query, language = "English", top_k = 6 }) {
  return request("/api/recommend", {
    method: "POST",
    body: JSON.stringify({ query, language, top_k }),
  });
}

export function listSchemes() {
  return request("/api/schemes");
}

export function compareSchemes(schemeIds) {
  return request("/api/compare", {
    method: "POST",
    body: JSON.stringify({ scheme_ids: schemeIds }),
  });
}
