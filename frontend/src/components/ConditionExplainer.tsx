"use client";

import { useState, useCallback } from "react";
import { InfoIcon } from "./Icons";
import { trackActivity } from "@/lib/tracking";
import type { ReadingLevel, ExplanationResponse, APIResponse } from "@/lib/types";
import ReadabilityBadge from "./ReadabilityBadge";
import ExplanationBody from "./ExplanationBody";
import LevelToggle from "./LevelToggle";
import SourcePanel from "./SourcePanel";

export default function ConditionExplainer({
  patientId,
  conditionIndex,
  conditionName,
}: {
  patientId: string;
  conditionIndex: number;
  conditionName: string;
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
          `/api/explain/condition/${patientId}/${conditionIndex}?level=${readingLevel}`
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
    [patientId, conditionIndex]
  );

  const handleOpen = () => {
    trackActivity("explain_condition", `${patientId}:${conditionName}`);
    setIsOpen(true);
    fetchExplanation(level);
  };

  const handleLevelChange = (newLevel: ReadingLevel) => {
    trackActivity("change_level", `${patientId}:condition:${newLevel}`);
    setLevel(newLevel);
    fetchExplanation(newLevel);
  };

  if (!isOpen) {
    return (
      <button
        onClick={handleOpen}
        className="mt-3 inline-flex items-center gap-1.5 rounded-lg border border-brand-line bg-white px-3 py-1.5 text-xs font-medium text-brand-navy shadow-sm transition-all hover:border-brand-accent hover:text-brand-accent hover:shadow"
      >
        <InfoIcon size={13} strokeWidth={2} />
        Learn more
      </button>
    );
  }

  return (
    <div className="mt-2 space-y-3">
      <div className="flex items-center justify-between">
        <h5 className="text-sm font-semibold text-gray-700">
          About {conditionName}
        </h5>
        <button
          onClick={() => setIsOpen(false)}
          className="text-xs text-gray-400 hover:text-gray-600"
        >
          Close
        </button>
      </div>

      <LevelToggle level={level} onChange={handleLevelChange} disabled={loading} />

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
        <div className="bg-brand-surface border border-brand-line rounded-lg p-4 space-y-3">
          <ExplanationBody text={result.explanation} />
          <hr className="border-brand-line" />
          <ReadabilityBadge scores={result.readability} />
          <SourcePanel sources={result.sources} />
          <p className="text-xs text-gray-400 italic">{result.disclaimer}</p>
        </div>
      )}
    </div>
  );
}
