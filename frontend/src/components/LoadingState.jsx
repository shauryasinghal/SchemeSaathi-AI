export default function LoadingState() {
  return (
    <div className="ledger-page animate-pulse space-y-4 p-6 md:p-8" aria-live="polite" aria-busy="true">
      <div className="h-4 w-2/3 rounded bg-inktext/10" />
      <div className="h-4 w-full rounded bg-inktext/10" />
      <div className="h-4 w-5/6 rounded bg-inktext/10" />
      <div className="mt-6 h-24 rounded bg-inktext/10" />
      <span className="sr-only">Searching schemes and preparing your answer…</span>
    </div>
  );
}
