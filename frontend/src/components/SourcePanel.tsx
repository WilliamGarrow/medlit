export default function SourcePanel({
  sources,
}: {
  sources: { title: string; url: string }[];
}) {
  if (!sources.length) return null;
  return (
    <div className="rounded-lg border border-brand-line bg-brand-surface p-3">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-gray-400 mb-2">
        Grounded in
      </p>
      <ul className="flex flex-wrap gap-1.5">
        {sources.map((src, i) => (
          <li key={i}>
            <a
              href={src.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block rounded-full border border-brand-line bg-white px-2.5 py-1 text-xs text-brand-accent hover:border-brand-accent transition-colors"
            >
              {src.title} ↗
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
