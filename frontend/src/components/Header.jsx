export default function Header() {
  return (
    <header className="border-b border-ink-700 px-6 py-5 md:px-10">
      <div className="mx-auto flex max-w-6xl items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold tracking-tight text-paper-50 md:text-3xl">
            SchemeSaathi <span className="text-seal-amber">AI</span>
          </h1>
          <p className="mt-1 font-body text-sm text-paper-200/70">
            Government schemes, explained for you.
          </p>
        </div>
        <a
          href="https://www.myscheme.gov.in/"
          target="_blank"
          rel="noreferrer"
          className="hidden font-mono text-xs uppercase tracking-wider text-paper-200/60 underline decoration-dotted underline-offset-4 hover:text-seal-teal md:block"
        >
          Cross-check on myScheme →
        </a>
      </div>
    </header>
  );
}
