import { useEffect, useState } from "react";
import Header from "./components/Header.jsx";
import Sidebar from "./components/Sidebar.jsx";
import QueryForm from "./components/QueryForm.jsx";
import ResultsPanel from "./components/ResultsPanel.jsx";
import LoadingState from "./components/LoadingState.jsx";
import ErrorBanner from "./components/ErrorBanner.jsx";
import CompareTray from "./components/CompareTray.jsx";
import CompareTable from "./components/CompareTable.jsx";
import { useSchemeSaathi } from "./hooks/useSchemeSaathi.js";

export default function App() {
  const {
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
    maxCompare,
  } = useSchemeSaathi();

  const [schemeNames, setSchemeNames] = useState({});
  const [compareOpen, setCompareOpen] = useState(false);

  // Keep a running id -> name lookup so the compare tray can show
  // readable labels even after the underlying results change.
  useEffect(() => {
    if (!result) return;
    setSchemeNames((prev) => {
      const next = { ...prev };
      for (const mr of result.match_results) next[mr.scheme.id] = mr.scheme.name;
      return next;
    });
  }, [result]);

  const handleRunCompare = async () => {
    await runCompare();
    setCompareOpen(true);
  };

  return (
    <div className="min-h-screen">
      <Header />

      <main className="mx-auto max-w-6xl px-6 py-8 md:px-10">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-[260px_1fr]">
          <Sidebar language={language} setLanguage={setLanguage} topK={topK} setTopK={setTopK} />

          <div className="space-y-6">
            <QueryForm query={query} setQuery={setQuery} onSubmit={() => submitQuery()} loading={loading} />

            <ErrorBanner message={error} />

            {loading && <LoadingState />}

            {!loading && result && (
              <ResultsPanel
                result={result}
                compareIds={compareIds}
                onToggleCompare={toggleCompare}
                maxCompare={maxCompare}
              />
            )}
          </div>
        </div>
      </main>

      <div className="px-6 pb-6 md:px-10">
        <CompareTray
          compareIds={compareIds}
          onRunCompare={handleRunCompare}
          onClear={clearCompare}
          loading={compareLoading}
          schemeNames={schemeNames}
        />
      </div>

      {compareOpen && (
        <CompareTable schemes={compareData} error={compareError} onClose={() => setCompareOpen(false)} />
      )}
    </div>
  );
}
