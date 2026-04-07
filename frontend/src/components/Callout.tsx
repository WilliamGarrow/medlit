export default function Callout({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 mb-4">
      <span className="text-xs font-bold uppercase tracking-wide text-amber-700">
        {label}
      </span>
      <p className="text-sm text-amber-900 mt-1 leading-relaxed">{children}</p>
    </div>
  );
}
