const STAMP_CONFIG = {
  "High Match": { color: "text-seal-green", label: "May Qualify" },
  "Medium Match": { color: "text-seal-amber", label: "Partial Fit" },
  "Needs More Information": { color: "text-seal-grey", label: "Need Info" },
  "Low Match": { color: "text-seal-red", label: "Low Fit" },
};

export default function MatchStamp({ level }) {
  const config = STAMP_CONFIG[level] || STAMP_CONFIG["Needs More Information"];

  return (
    <span
      className={`ink-seal h-16 w-16 shrink-0 border-current text-[10px] leading-tight ${config.color}`}
      title={level}
      aria-label={`Match level: ${level}`}
    >
      <span className="px-1 text-center">{config.label}</span>
    </span>
  );
}
