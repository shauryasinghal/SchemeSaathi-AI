import SchemeCard from "./SchemeCard.jsx";
import Disclaimer from "./Disclaimer.jsx";

export default function ResultsPanel({ result, compareIds, onToggleCompare, maxCompare }) {
  const { answer_text, used_ai, warning, missing_info_prompts, match_results } = result;

  return (
    <section className="ledger-page space-y-6 p-6 md:p-8">
      <div className="perforated-top -mx-6 -mt-6 md:-mx-8 md:-mt-8" />

      {!used_ai && (
        <div className="rounded-card border border-seal-grey/40 bg-seal-grey/10 px-4 py-3 font-body text-sm text-inktext/80">
          {warning || "AI explanation is temporarily unavailable. Showing database matches directly."}
        </div>
      )}

      {missing_info_prompts.length > 0 && (
        <div>
          <p className="font-display text-lg font-semibold text-inktext">
            We need a little more information to narrow this down:
          </p>
          <ul className="mt-2 list-disc space-y-1 pl-5 font-body text-sm text-inktext/80">
            {missing_info_prompts.map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <h2 className="font-display text-xl font-semibold text-inktext">Your results</h2>
        <div className="prose-sm mt-2 whitespace-pre-wrap font-body text-inktext/90">{answer_text}</div>
      </div>

      {match_results.length > 0 && (
        <div>
          <h3 className="font-display text-lg font-semibold text-inktext">Matched schemes</h3>
          <div className="mt-2">
            {match_results.map((mr) => (
              <SchemeCard
                key={mr.scheme.id}
                matchResult={mr}
                checked={compareIds.includes(mr.scheme.id)}
                compareDisabled={compareIds.length >= maxCompare}
                onToggleCompare={onToggleCompare}
              />
            ))}
          </div>
        </div>
      )}

      <Disclaimer />
    </section>
  );
}
