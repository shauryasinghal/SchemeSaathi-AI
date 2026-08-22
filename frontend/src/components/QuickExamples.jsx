const EXAMPLES = [
  { label: "Farmer", text: "I am a farmer from Uttar Pradesh looking for irrigation support." },
  { label: "Street Vendor", text: "I run a small street food stall and need financial support." },
  { label: "Artisan", text: "I am an artisan looking for training and market support." },
  { label: "Student", text: "I am a student from a low-income family looking for scholarships." },
  {
    label: "Person with disability",
    text: "I have a disability and am looking for assistive devices and vocational training support.",
  },
];

export default function QuickExamples({ onPick, disabled }) {
  return (
    <div>
      <p className="mb-2 font-mono text-xs uppercase tracking-wider text-paper-200/60">
        Quick examples — tap one to try it
      </p>
      <div className="flex flex-wrap gap-2">
        {EXAMPLES.map((ex) => (
          <button
            key={ex.label}
            type="button"
            disabled={disabled}
            onClick={() => onPick(ex.text)}
            className="rounded-card border border-ink-700 bg-ink-800 px-3 py-2 font-body text-sm text-paper-100 transition hover:border-seal-teal hover:text-seal-teal disabled:cursor-not-allowed disabled:opacity-50"
          >
            {ex.label}
          </button>
        ))}
      </div>
    </div>
  );
}
