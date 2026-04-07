const SYSTEM_STYLES: Record<string, string> = {
  "SNOMED CT": "bg-violet-100 text-violet-700 border-violet-200",
  RxNorm: "bg-sky-100 text-sky-700 border-sky-200",
  LOINC: "bg-amber-100 text-amber-700 border-amber-200",
};

const FALLBACK_STYLE = "bg-gray-100 text-gray-600 border-gray-200";

export default function CodeBadge({
  system,
  code,
}: {
  system: string;
  code: string;
}) {
  const style = SYSTEM_STYLES[system] ?? FALLBACK_STYLE;

  return (
    <span className={`inline-flex items-center text-xs font-medium rounded border ${style}`}>
      <span className="px-1.5 py-0.5">{system}</span>
      <span className="px-1.5 py-0.5 font-mono border-l border-inherit bg-white/50">
        {code}
      </span>
    </span>
  );
}
