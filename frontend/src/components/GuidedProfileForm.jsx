import { useState } from "react";

const INCOME_OPTIONS = ["Prefer not to say", "Low", "Middle", "High"];

export default function GuidedProfileForm({ onSubmit, disabled }) {
  const [open, setOpen] = useState(false);
  const [state, setState] = useState("");
  const [occupation, setOccupation] = useState("");
  const [age, setAge] = useState("");
  const [need, setNeed] = useState("");
  const [income, setIncome] = useState(INCOME_OPTIONS[0]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const parts = [];
    if (age) parts.push(`I am ${age} years old`);
    if (occupation) parts.push(`working as a ${occupation}`);
    if (state) parts.push(`from ${state}`);
    if (income !== INCOME_OPTIONS[0]) parts.push(`with ${income.toLowerCase()} income`);
    if (need) parts.push(`and I need help with ${need}`);

    if (parts.length === 0) return;
    onSubmit(`${parts.join(", ")}.`);
  };

  return (
    <div className="rounded-card border border-ink-700 bg-ink-800/60">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-4 py-3 font-body text-sm text-paper-100"
        aria-expanded={open}
      >
        <span>Or fill a guided profile instead (optional, you can skip any field)</span>
        <span className="text-paper-200/60">{open ? "−" : "+"}</span>
      </button>

      {open && (
        <form onSubmit={handleSubmit} className="space-y-3 border-t border-ink-700 px-4 py-4">
          <Field label="State" value={state} onChange={setState} disabled={disabled} />
          <Field label="Occupation" value={occupation} onChange={setOccupation} disabled={disabled} />
          <Field label="Age" value={age} onChange={setAge} type="number" disabled={disabled} />
          <Field label="Main need" value={need} onChange={setNeed} disabled={disabled} />

          <label className="block">
            <span className="mb-1 block font-mono text-xs uppercase tracking-wider text-paper-200/60">
              Approximate income (optional)
            </span>
            <select
              value={income}
              onChange={(e) => setIncome(e.target.value)}
              disabled={disabled}
              className="w-full rounded-card border border-ink-700 bg-ink-900 px-3 py-2 font-body text-sm text-paper-50 focus:border-seal-teal"
            >
              {INCOME_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </label>

          <button
            type="submit"
            disabled={disabled}
            className="w-full rounded-card border border-seal-teal py-2 font-body text-sm font-medium text-seal-teal transition hover:bg-seal-teal hover:text-ink-950 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Use this profile
          </button>
        </form>
      )}
    </div>
  );
}

function Field({ label, value, onChange, type = "text", disabled }) {
  return (
    <label className="block">
      <span className="mb-1 block font-mono text-xs uppercase tracking-wider text-paper-200/60">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full rounded-card border border-ink-700 bg-ink-900 px-3 py-2 font-body text-sm text-paper-50 placeholder:text-paper-200/40 focus:border-seal-teal"
      />
    </label>
  );
}
