const ROWS = [
  { key: "category", label: "Category" },
  { key: "benefits", label: "Benefits" },
  { key: "eligibility", label: "Key eligibility", isList: true, limit: 2 },
  { key: "documents", label: "Documents", isList: true },
  { key: "application_process", label: "How to apply", isList: true },
];

export default function CompareTable({ schemes, onClose, error }) {
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Compare schemes"
      className="fixed inset-0 z-20 flex items-end justify-center bg-ink-950/70 p-0 md:items-center md:p-6"
    >
      <div className="ledger-page max-h-[85vh] w-full max-w-4xl overflow-y-auto rounded-t-card md:rounded-card">
        <div className="perforated-top -mx-0 -mt-0" />
        <div className="flex items-center justify-between px-6 pt-5">
          <h2 className="font-display text-xl font-semibold text-inktext">Compare Schemes</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close comparison"
            className="rounded-full px-3 py-1 font-mono text-lg text-inktext/60 hover:text-seal-red"
          >
            ×
          </button>
        </div>

        <div className="p-6">
          {error && <p className="font-body text-sm text-seal-red">{error}</p>}

          {!error && schemes && (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] table-fixed border-collapse">
                <thead>
                  <tr>
                    <th className="w-32 border-b border-inktext/15 pb-3 text-left font-mono text-xs uppercase tracking-wider text-inktext/50">
                      Field
                    </th>
                    {schemes.map((s) => (
                      <th
                        key={s.id}
                        className="border-b border-inktext/15 px-3 pb-3 text-left font-display text-sm font-semibold text-inktext"
                      >
                        {s.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {ROWS.map((row) => (
                    <tr key={row.key} className="align-top">
                      <th className="border-b border-inktext/10 py-3 pr-2 text-left font-mono text-xs uppercase tracking-wider text-inktext/50">
                        {row.label}
                      </th>
                      {schemes.map((s) => (
                        <td key={s.id} className="border-b border-inktext/10 px-3 py-3 font-body text-sm text-inktext/85">
                          {row.isList
                            ? (row.limit ? s[row.key].slice(0, row.limit) : s[row.key]).join("; ")
                            : s[row.key]}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
