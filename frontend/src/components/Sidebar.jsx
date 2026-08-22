import { useState } from "react";

const LANGUAGES = ["English", "Hindi"];

export default function Sidebar({ language, setLanguage, topK, setTopK }) {
  const [responsibleOpen, setResponsibleOpen] = useState(false);

  return (
    <aside className="space-y-6 md:sticky md:top-6 md:self-start">
      <div>
        <h2 className="font-display text-lg font-semibold text-paper-50">Settings</h2>

        <label className="mt-4 block">
          <span className="mb-1 block font-mono text-xs uppercase tracking-wider text-paper-200/60">
            Answer language
          </span>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full rounded-card border border-ink-700 bg-ink-800 px-3 py-2 font-body text-sm text-paper-50 focus:border-seal-teal"
          >
            {LANGUAGES.map((lang) => (
              <option key={lang} value={lang}>
                {lang}
              </option>
            ))}
          </select>
        </label>

        <label className="mt-4 block">
          <span className="mb-1 block font-mono text-xs uppercase tracking-wider text-paper-200/60">
            Number of schemes to consider: <span className="text-seal-amber">{topK}</span>
          </span>
          <input
            type="range"
            min={3}
            max={8}
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            className="w-full accent-seal-teal"
          />
        </label>
      </div>

      <p className="border-t border-ink-700 pt-4 font-body text-xs leading-relaxed text-paper-200/50">
        Built for OOSC 4.0 Hackathon — Problem Statement 5: AI for Public Good.
      </p>

      <div className="rounded-card border border-ink-700">
        <button
          type="button"
          onClick={() => setResponsibleOpen((v) => !v)}
          className="flex w-full items-center justify-between px-4 py-3 font-body text-sm text-paper-100"
          aria-expanded={responsibleOpen}
        >
          <span>Responsible AI</span>
          <span className="text-paper-200/60">{responsibleOpen ? "−" : "+"}</span>
        </button>
        {responsibleOpen && (
          <ul className="space-y-2 border-t border-ink-700 px-4 py-3 font-body text-xs leading-relaxed text-paper-200/70">
            <li>We never guarantee government approval — only the relevant authority can confirm final eligibility.</li>
            <li>Every recommendation shows its official government source.</li>
            <li>We only ask for the information needed to narrow down schemes, never anything more.</li>
            <li>The AI is instructed to use only the schemes in our database and never invent scheme details.</li>
            <li>If the AI explanation is unavailable, we show you the raw database matches instead of pretending nothing changed.</li>
          </ul>
        )}
      </div>
    </aside>
  );
}
