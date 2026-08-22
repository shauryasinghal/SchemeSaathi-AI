import QuickExamples from "./QuickExamples.jsx";
import GuidedProfileForm from "./GuidedProfileForm.jsx";

export default function QueryForm({ query, setQuery, onSubmit, loading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <section className="ledger-page p-6 md:p-8">
      <div className="perforated-top -mx-6 -mt-6 mb-6 md:-mx-8 md:-mt-8" />

      <h2 className="font-display text-2xl font-semibold text-inktext md:text-3xl">
        Find Government Schemes You May Qualify For
      </h2>

      <div className="mt-5">
        <QuickExamples onPick={setQuery} disabled={loading} />
      </div>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <label className="block">
          <span className="mb-2 block font-body text-sm text-inktext/70">
            Tell us about yourself in your own words…
          </span>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
            rows={4}
            placeholder="e.g. I am a 40-year-old farmer from UP. I have 2 acres of land and need help with irrigation."
            className="w-full rounded-card border border-inktext/20 bg-white/70 px-4 py-3 font-body text-inktext placeholder:text-inktext/40 focus:border-seal-teal disabled:opacity-60"
          />
        </label>

        <GuidedProfileForm onSubmit={setQuery} disabled={loading} />

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-card border-[3px] border-seal-red px-6 py-3 font-mono text-sm uppercase tracking-wide text-seal-red transition hover:bg-seal-red hover:text-paper-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Searching…" : "Find My Schemes"}
        </button>
      </form>
    </section>
  );
}
