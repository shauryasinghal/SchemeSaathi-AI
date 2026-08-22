export default function CompareTray({ compareIds, onRunCompare, onClear, loading, schemeNames }) {
  if (compareIds.length === 0) return null;

  return (
    <div className="sticky bottom-4 z-10 mx-auto flex max-w-6xl items-center justify-between gap-4 rounded-card border border-seal-teal/50 bg-ink-800 px-5 py-3 shadow-lg shadow-ink-950/40">
      <div className="min-w-0 font-body text-sm text-paper-100">
        <span className="font-mono text-xs uppercase tracking-wider text-seal-teal">
          Comparing ({compareIds.length}/3):
        </span>{" "}
        <span className="truncate">{compareIds.map((id) => schemeNames[id] || id).join(", ")}</span>
      </div>
      <div className="flex shrink-0 gap-2">
        <button
          type="button"
          onClick={onClear}
          className="rounded-card border border-paper-200/30 px-3 py-1.5 font-body text-sm text-paper-200/70 hover:text-paper-50"
        >
          Clear
        </button>
        <button
          type="button"
          onClick={onRunCompare}
          disabled={compareIds.length < 2 || loading}
          className="rounded-card border border-seal-teal bg-seal-teal px-4 py-1.5 font-body text-sm font-medium text-ink-950 transition hover:bg-seal-teal/90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Loading…" : "Compare"}
        </button>
      </div>
    </div>
  );
}
