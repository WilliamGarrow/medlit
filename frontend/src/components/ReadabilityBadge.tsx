"use client";

import { useState } from "react";
import type { ReadabilityScores } from "@/lib/types";

function gradeLabel(fk: number): {
  label: string;
  color: string;
  desc: string;
} {
  if (fk <= 5)
    return {
      label: "Easy",
      color: "bg-green-100 text-green-800",
      desc: "5th grade or below, accessible to most readers",
    };
  if (fk <= 8)
    return {
      label: "Average",
      color: "bg-yellow-100 text-yellow-800",
      desc: "6th–8th grade, clear for general audiences",
    };
  if (fk <= 12)
    return {
      label: "Advanced",
      color: "bg-orange-100 text-orange-800",
      desc: "9th–12th grade, assumes some health literacy",
    };
  return {
    label: "Professional",
    color: "bg-red-100 text-red-800",
    desc: "College level, clinical or technical language",
  };
}

function ordinal(n: number): string {
  const rounded = Math.round(n);
  if (rounded <= 0) return "below 1st";
  const s = ["th", "st", "nd", "rd"];
  const v = rounded % 100;
  return `${rounded}${s[(v - 20) % 10] || s[v] || s[0]}`;
}

export default function ReadabilityBadge({
  scores,
}: {
  scores: ReadabilityScores;
}) {
  const [showDetail, setShowDetail] = useState(false);
  const { label, color, desc } = gradeLabel(scores.flesch_kincaid_grade);
  const gradeText = `${ordinal(scores.flesch_kincaid_grade)} grade reading level`;

  return (
    <div className="text-xs">
      <button
        onClick={() => setShowDetail(!showDetail)}
        aria-expanded={showDetail}
        className="group -mx-2 flex items-center gap-2 rounded-md px-2 py-1 transition-colors hover:bg-brand-muted"
      >
        <span className={`px-2 py-0.5 rounded-full font-medium ${color}`}>
          {label}
        </span>
        <span className="text-gray-500 underline decoration-dotted decoration-gray-300 underline-offset-2 group-hover:decoration-brand-accent">
          {gradeText}
        </span>
        <svg
          viewBox="0 0 12 12"
          className={`h-3 w-3 text-gray-400 transition-transform group-hover:text-brand-accent ${
            showDetail ? "rotate-180" : ""
          }`}
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M2.5 4.5 L6 8 L9.5 4.5" />
        </svg>
      </button>

      {showDetail && (
        <div className="mt-2 rounded-lg border border-brand-line bg-brand-surface p-3 space-y-2.5">
          <p className="text-gray-600">{desc}</p>
          <div className="flex gap-2">
            <span
              title="Flesch-Kincaid Grade Level: maps to US school grade"
              className="rounded-md border border-brand-line bg-white px-2 py-1 text-gray-600"
            >
              Flesch-Kincaid{" "}
              <span className="font-mono font-medium text-brand-navy">
                {scores.flesch_kincaid_grade.toFixed(1)}
              </span>
            </span>
            <span
              title="Gunning Fog Index: estimates years of education needed"
              className="rounded-md border border-brand-line bg-white px-2 py-1 text-gray-600"
            >
              Gunning Fog{" "}
              <span className="font-mono font-medium text-brand-navy">
                {scores.gunning_fog.toFixed(1)}
              </span>
            </span>
          </div>
          <p className="text-[11px] text-gray-400">
            Scored on the generated text itself, never assumed from the prompt.
          </p>
        </div>
      )}
    </div>
  );
}
