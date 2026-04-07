"use client";

/**
 * Renders LLM-generated explanation text with subtle paragraph styling.
 * Splits on double-newlines and adds spacing + optional first-paragraph emphasis.
 */
export default function ExplanationBody({ text }: { text: string }) {
  const paragraphs = text
    .split(/\n\n+/)
    .map((p) => p.trim())
    .filter(Boolean);

  if (paragraphs.length <= 1) {
    return (
      <p className="text-sm text-gray-700 leading-relaxed">{text}</p>
    );
  }

  return (
    <div className="space-y-3">
      {paragraphs.map((p, i) => (
        <p
          key={i}
          className={`text-sm leading-relaxed ${
            i === 0 ? "text-gray-800" : "text-gray-600"
          }`}
        >
          {p}
        </p>
      ))}
    </div>
  );
}
