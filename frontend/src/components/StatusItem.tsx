export default function StatusItem({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  const isGood =
    value === "Healthy" || value === "Loaded" || value.startsWith("Connected") || value === "Stub Mode";
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs uppercase tracking-wide text-gray-400">
        {label}
      </span>
      <span className="flex items-center gap-1.5">
        <span
          className={`inline-block h-2 w-2 rounded-full ${
            isGood ? "bg-emerald-500" : "bg-amber-500"
          }`}
        />
        <span className={isGood ? "text-gray-900 font-medium" : "text-gray-900"}>
          {value}
        </span>
      </span>
    </div>
  );
}
