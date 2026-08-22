import MatchStamp from "./MatchStamp.jsx";

export default function SchemeCard({ matchResult, checked, onToggleCompare, compareDisabled }) {
  const { scheme, match_level, matched_criteria, missing_criteria, unmatched_criteria } = matchResult;

  return (
    <article className="flex gap-4 border-b border-inktext/10 py-5 last:border-b-0">
      <MatchStamp level={match_level} />

      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <h3 className="font-display text-lg font-semibold text-inktext">{scheme.name}</h3>
          <span className="font-mono text-xs uppercase tracking-wider text-inktext/50">{scheme.category}</span>
        </div>

        <p className="mt-1 font-body text-sm text-inktext/80">{scheme.description}</p>

        {matched_criteria.length > 0 && (
          <ReasonList icon="✓" items={matched_criteria} className="text-seal-green" />
        )}
        {missing_criteria.length > 0 && (
          <ReasonList icon="?" items={missing_criteria} className="text-seal-amber" prefix="Missing: " />
        )}
        {unmatched_criteria.length > 0 && (
          <ReasonList icon="!" items={unmatched_criteria} className="text-seal-red" />
        )}

        <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
          <a
            href={scheme.source_url}
            target="_blank"
            rel="noreferrer"
            className="rounded bg-inktext/5 px-3 py-1.5 font-mono text-xs text-inktext/70 underline decoration-dotted underline-offset-2 hover:text-seal-teal"
          >
            Official Source: {scheme.source_name} ↗
          </a>

          <label className="flex cursor-pointer items-center gap-2 font-body text-xs text-inktext/60">
            <input
              type="checkbox"
              checked={checked}
              disabled={compareDisabled && !checked}
              onChange={() => onToggleCompare(scheme.id)}
              className="h-4 w-4 rounded border-inktext/30 text-seal-teal focus:ring-seal-teal"
            />
            Add to comparison
          </label>
        </div>
      </div>
    </article>
  );
}

function ReasonList({ icon, items, className, prefix = "" }) {
  return (
    <p className={`mt-2 font-body text-sm ${className}`}>
      <span aria-hidden="true">{icon}</span> {prefix}
      {items.join(" · ")}
    </p>
  );
}
