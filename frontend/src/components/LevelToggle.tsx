"use client";

import type { ReadingLevel } from "@/lib/types";

const LEVELS: { value: ReadingLevel; label: string }[] = [
  { value: "simple", label: "Simple" },
  { value: "standard", label: "Standard" },
  { value: "detailed", label: "Detailed" },
];

export default function LevelToggle({
  level,
  onChange,
  disabled = false,
}: {
  level: ReadingLevel;
  onChange: (level: ReadingLevel) => void;
  disabled?: boolean;
}) {
  return (
    <div className="inline-flex rounded-lg bg-brand-muted p-1">
      {LEVELS.map((l) => (
        <button
          key={l.value}
          onClick={() => onChange(l.value)}
          disabled={disabled}
          className={`px-3 py-1 text-xs font-medium rounded-md transition-all disabled:opacity-50 ${
            level === l.value
              ? "bg-white text-brand-navy shadow-sm"
              : "text-gray-500 hover:text-brand-navy"
          }`}
        >
          {l.label}
        </button>
      ))}
    </div>
  );
}
