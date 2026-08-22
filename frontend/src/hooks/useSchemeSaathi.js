import { useCallback, useState } from "react";
import { getRecommendations, compareSchemes as compareSchemesRequest } from "../api/client.js";

const MAX_COMPARE = 3;

export function useSchemeSaathi() {
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("English");
  const [topK, setTopK] = useState(6);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null); // RecommendResponse from the API

  const [compareIds, setCompareIds] = useState([]);
  const [compareData, setCompareData] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState(null);

  const submitQuery = useCallback(
    async (overrideQuery) => {
      const activeQuery = (overrideQuery ?? query).trim();
      if (!activeQuery) {
        setError("Please describe your situation first.");
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const data = await getRecommendations({ query: activeQuery, language, top_k: topK });
        setResult(data);
        if (overrideQuery) setQuery(overrideQuery);
      } catch (e) {
        setError(e.message || "Something went wrong. Please try again.");
        setResult(null);
      } finally {
        setLoading(false);
      }
    },
    [query, language, topK]
  );

  const toggleCompare = useCallback((schemeId) => {
    setCompareIds((prev) => {
      if (prev.includes(schemeId)) {
        return prev.filter((id) => id !== schemeId);
      }
      if (prev.length >= MAX_COMPARE) {
        return prev; // silently cap at MAX_COMPARE; the UI disables further checkboxes
      }
      return [...prev, schemeId];
    });
  }, []);

  const clearCompare = useCallback(() => {
    setCompareIds([]);
    setCompareData(null);
    setCompareError(null);
  }, []);

  const runCompare = useCallback(async () => {
    if (compareIds.length < 2) return;
    setCompareLoading(true);
    setCompareError(null);
    try {
      const data = await compareSchemesRequest(compareIds);
      setCompareData(data);
    } catch (e) {
      setCompareError(e.message || "Couldn't load comparison.");
    } finally {
      setCompareLoading(false);
    }
  }, [compareIds]);

  return {
    query,
    setQuery,
    language,
    setLanguage,
    topK,
    setTopK,
    loading,
    error,
    result,
    submitQuery,
    compareIds,
    toggleCompare,
    clearCompare,
    compareData,
    compareLoading,
    compareError,
    runCompare,
    maxCompare: MAX_COMPARE,
  };
}
