export default function ErrorBanner({ message }) {
  if (!message) return null;
  return (
    <div
      role="alert"
      className="rounded-card border border-seal-red/50 bg-seal-red/10 px-4 py-3 font-body text-sm text-paper-50"
    >
      <span className="font-medium text-seal-red">Couldn't complete that search.</span> {message}
    </div>
  );
}
