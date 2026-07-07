"use client";

import { useState, useEffect, useCallback } from "react";
import { trackActivity } from "@/lib/tracking";
import {
  HeartIcon,
  PillIcon,
  AlertTriangleIcon,
  TestTubeIcon,
  LightbulbIcon,
  FileTextIcon,
} from "./Icons";
import type {
  ReadingLevel,
  ExplanationResponse,
  APIResponse,
  SummarySection,
} from "@/lib/types";
import ReadabilityBadge from "./ReadabilityBadge";

const LEVELS: { value: ReadingLevel; label: string }[] = [
  { value: "simple", label: "Simple" },
  { value: "standard", label: "Standard" },
  { value: "detailed", label: "Detailed" },
];

const SECTION_CONFIG: Record<
  string,
  { icon: React.ElementType; border: string; accent: string }
> = {
  conditions: {
    icon: HeartIcon,
    border: "border-l-amber-400",
    accent: "text-amber-600",
  },
  medications: {
    icon: PillIcon,
    border: "border-l-teal-400",
    accent: "text-teal-600",
  },
  interactions: {
    icon: AlertTriangleIcon,
    border: "border-l-rose-400",
    accent: "text-rose-600",
  },
  labs: {
    icon: TestTubeIcon,
    border: "border-l-blue-400",
    accent: "text-blue-600",
  },
  takeaways: {
    icon: LightbulbIcon,
    border: "border-l-violet-400",
    accent: "text-violet-600",
  },
};

const DEFAULT_CONFIG = {
  icon: FileTextIcon,
  border: "border-l-gray-300",
  accent: "text-gray-500",
};

function SectionCard({ section }: { section: SummarySection }) {
  const config = SECTION_CONFIG[section.icon] || DEFAULT_CONFIG;
  const Icon = config.icon;

  return (
    <div className={`border-l-2 ${config.border} pl-4 py-1`}>
      <div className="flex items-center gap-1.5 mb-1">
        <Icon size={14} className={config.accent} strokeWidth={2} />
        <h4 className={`text-xs font-semibold uppercase tracking-wide ${config.accent}`}>
          {section.heading}
        </h4>
      </div>
      <p className="text-sm text-gray-700 leading-relaxed">{section.body}</p>
    </div>
  );
}

export default function PatientSummary({ patientId }: { patientId: string }) {
  const [level, setLevel] = useState<ReadingLevel>("standard");
  const [result, setResult] = useState<ExplanationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = useCallback(
    async (readingLevel: ReadingLevel) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(
          `/api/patients/${patientId}/summary?level=${readingLevel}`
        );
        const json: APIResponse<ExplanationResponse> = await res.json();
        if (!res.ok || !json.success) {
          throw new Error(json.error || "Failed to generate summary");
        }
        setResult(json.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    },
    [patientId]
  );

  useEffect(() => {
    trackActivity("view_summary", patientId);
    fetchSummary(level);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleLevelChange = (newLevel: ReadingLevel) => {
    trackActivity("change_level", `${patientId}:summary:${newLevel}`);
    setLevel(newLevel);
    fetchSummary(newLevel);
  };

  return (
    <section className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileTextIcon size={18} className="text-gray-400" strokeWidth={1.5} />
          <h3 className="text-lg font-semibold text-gray-800">
            Your Health Summary
          </h3>
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
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-500 py-4">
          <svg
            className="animate-spin h-4 w-4 text-brand-accent"
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          Generating health summary...
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded p-3">
          {error}
        </div>
      )}

      {/* Structured sections */}
      {result && !loading && result.sections && (
        <div className="space-y-4">
          {result.sections.map((section, i) => (
            <SectionCard key={i} section={section} />
          ))}

          <hr className="border-gray-100" />

          <div className="flex items-center justify-between">
            <ReadabilityBadge scores={result.readability} />
          </div>

          {result.sources.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Sources</p>
              <ul className="flex flex-wrap gap-x-4 gap-y-0.5">
                {result.sources.map((src, i) => (
                  <li key={i}>
                    <a
                      href={src.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-brand-accent hover:underline"
                    >
                      {src.title} ↗
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <p className="text-xs text-gray-400 italic">
            {result.disclaimer}
          </p>
        </div>
      )}

      {/* Fallback: plain text */}
      {result && !loading && !result.sections && (
        <div className="space-y-3">
          <div className="text-sm text-gray-800 whitespace-pre-line leading-relaxed">
            {result.explanation}
          </div>
          <ReadabilityBadge scores={result.readability} />
          <p className="text-xs text-gray-400 italic">
            {result.disclaimer}
          </p>
        </div>
      )}
    </section>
  );
}
