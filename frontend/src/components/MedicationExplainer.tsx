"use client";

import { useState, useCallback } from "react";
import { InfoIcon } from "./Icons";
import { trackActivity } from "@/lib/tracking";
import type { ReadingLevel, ExplanationResponse, APIResponse } from "@/lib/types";
import ReadabilityBadge from "./ReadabilityBadge";
import ExplanationBody from "./ExplanationBody";

const LEVELS: { value: ReadingLevel; label: string }[] = [
  { value: "simple", label: "Simple" },
  { value: "standard", label: "Standard" },
  { value: "detailed", label: "Detailed" },
];

export default function MedicationExplainer({
  patientId,
  medIndex,
  medicationName,
}: {
  patientId: string;
  medIndex: number;
  medicationName: string;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [level, setLevel] = useState<ReadingLevel>("standard");
  const [result, setResult] = useState<ExplanationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchExplanation = useCallback(
    async (readingLevel: ReadingLevel) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(
          `/api/explain/medication/${patientId}/${medIndex}?level=${readingLevel}`
        );
        const json: APIResponse<ExplanationResponse> = await res.json();
        if (!res.ok || !json.success) {
          throw new Error(json.error || "Failed to generate explanation");
        }
        setResult(json.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    },
    [patientId, medIndex]
  );

  const handleOpen = () => {
    trackActivity("explain_medication", `${patientId}:${medicationName}`);
    setIsOpen(true);
    fetchExplanation(level);
  };

  const handleLevelChange = (newLevel: ReadingLevel) => {
    trackActivity("change_level", `${patientId}:medication:${newLevel}`);
    setLevel(newLevel);
    fetchExplanation(newLevel);
  };

  if (!isOpen) {
    return (
      <button
        onClick={handleOpen}
        className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-brand-accent bg-teal-50 border border-teal-200 rounded-md hover:bg-teal-100 hover:border-teal-300 transition-colors"
      >
        <InfoIcon size={14} strokeWidth={2} />
        Learn more
      </button>
    );
  }

  return (
    <div className="mt-3 border-t border-gray-100 pt-3 space-y-3">
      <div className="flex items-center justify-between">
        <h5 className="text-sm font-semibold text-gray-700">
          About {medicationName}
        </h5>
        <button
          onClick={() => setIsOpen(false)}
          className="text-xs text-gray-400 hover:text-gray-600"
        >
          Close
        </button>
      </div>

      <div className="flex gap-1">
        {LEVELS.map((l) => (
          <button
            key={l.value}
            onClick={() => handleLevelChange(l.value)}
            disabled={loading}
            className={`px-3 py-1 text-xs rounded-full border transition-colors ${
              level === l.value
                ? "bg-brand-accent text-white border-brand-accent"
                : "bg-white text-gray-600 border-gray-300 hover:border-brand-accent"
            } disabled:opacity-50`}
          >
            {l.label}
          </button>
        ))}
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <svg className="animate-spin h-4 w-4 text-brand-accent" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Generating explanation...
        </div>
      )}

      {error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded p-3">
          {error}
        </div>
      )}

      {result && !loading && (
        <div className="bg-slate-50 rounded-lg p-4 space-y-3">
          <ExplanationBody text={result.explanation} />
          <hr className="border-gray-200" />
          <ReadabilityBadge scores={result.readability} />
          {result.sources.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Sources</p>
              <ul className="space-y-0.5">
                {result.sources.map((src, i) => (
                  <li key={i}>
                    <a href={src.url} target="_blank" rel="noopener noreferrer" className="text-xs text-brand-accent hover:underline">
                      {src.title} ↗
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
          <p className="text-xs text-gray-400 italic">{result.disclaimer}</p>
        </div>
      )}
    </div>
  );
}
