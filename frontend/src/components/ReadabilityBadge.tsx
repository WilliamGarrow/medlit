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
        className="flex items-center gap-2 hover:opacity-80 transition-opacity"
      >
        <span className={`px-2 py-0.5 rounded-full font-medium ${color}`}>
          {label}
        </span>
        <span className="text-gray-500">{gradeText}</span>
        <span className="text-gray-300">{showDetail ? "▴" : "▾"}</span>
      </button>

      {showDetail && (
        <div className="mt-2 p-3 bg-gray-50 rounded-lg border border-gray-100 space-y-1.5">
          <p className="text-gray-600">{desc}</p>
          <div className="flex gap-4 text-gray-400">
            <span title="Flesch-Kincaid Grade Level: maps to US school grade">
              Flesch-Kincaid: {scores.flesch_kincaid_grade.toFixed(1)}
            </span>
            <span title="Gunning Fog Index: estimates years of education needed">
              Gunning Fog: {scores.gunning_fog.toFixed(1)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
