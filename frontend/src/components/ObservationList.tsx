import type { ObservationDetail } from "@/lib/types";
import CodeBadge from "./CodeBadge";

// Well-known reference ranges by LOINC code
const REFERENCE_RANGES: Record<string, { low?: number; high?: number; unit: string; label: string }> = {
  "30934-4": { high: 100, unit: "pg/mL", label: "BNP (heart failure marker)" },
  "20150-9": { low: 2.5, unit: "L", label: "FEV1 (lung function)" },
  "4548-4":  { high: 5.7, unit: "%", label: "A1c (blood sugar control)" },
  "20436-2": { high: 140, unit: "mg/dL", label: "Glucose tolerance" },
  "44261-6": { high: 4, unit: "{score}", label: "PHQ-9 (depression screening)" },
  "2093-3":  { high: 200, unit: "mg/dL", label: "Total cholesterol" },
  "2571-8":  { high: 150, unit: "mg/dL", label: "Triglycerides" },
  "33762-6": { low: 30, unit: "mL/min", label: "eGFR (kidney function)" },
  "718-7":   { low: 13.5, high: 17.5, unit: "g/dL", label: "Hemoglobin" },
  "19926-5": { low: 2.5, unit: "L", label: "FEV1/FVC ratio" },
};

function getInterpretation(obs: ObservationDetail): {
  status: "normal" | "abnormal" | "unknown";
  note: string;
} {
  const ref = REFERENCE_RANGES[obs.code];
  if (!ref || obs.value == null || typeof obs.value !== "number") {
    return { status: "unknown", note: "" };
  }

  const val = obs.value;
  if (ref.low != null && ref.high != null) {
    if (val < ref.low) return { status: "abnormal", note: `Below normal range (${ref.low}–${ref.high} ${ref.unit})` };
    if (val > ref.high) return { status: "abnormal", note: `Above normal range (${ref.low}–${ref.high} ${ref.unit})` };
    return { status: "normal", note: `Within normal range (${ref.low}–${ref.high} ${ref.unit})` };
  }
  if (ref.high != null) {
    if (val > ref.high) return { status: "abnormal", note: `Above normal (target <${ref.high} ${ref.unit})` };
    return { status: "normal", note: `Within normal (target <${ref.high} ${ref.unit})` };
  }
  if (ref.low != null) {
    if (val < ref.low) return { status: "abnormal", note: `Below normal (target >${ref.low} ${ref.unit})` };
    return { status: "normal", note: `Within normal (target >${ref.low} ${ref.unit})` };
  }
  return { status: "unknown", note: "" };
}

export default function ObservationList({
  observations,
}: {
  observations: ObservationDetail[];
}) {
  if (observations.length === 0) {
    return <p className="text-sm text-gray-500">No lab results recorded.</p>;
  }

  return (
    <div className="space-y-3">
      {observations.map((o, i) => {
        const interp = getInterpretation(o);
        const borderColor =
          interp.status === "abnormal"
            ? "border-l-red-500"
            : interp.status === "normal"
            ? "border-l-emerald-500"
            : "border-l-gray-300";

        return (
          <div
            key={i}
            className={`border border-gray-200 border-l-4 ${borderColor} rounded-lg p-4 bg-white shadow-sm`}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="font-medium text-gray-900">{o.display}</h4>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-lg font-semibold text-gray-900">
                    {o.value != null
                      ? `${o.value}${o.unit ? ` ${o.unit}` : ""}`
                      : "—"}
                  </span>
                  {interp.status === "abnormal" && (
                    <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-red-100 text-red-700">
                      Abnormal
                    </span>
                  )}
                  {interp.status === "normal" && (
                    <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-100 text-emerald-700">
                      Normal
                    </span>
                  )}
                </div>
                <div className="mt-1.5">
                  <CodeBadge system={o.system} code={o.code} />
                </div>
              </div>
              {o.date && (
                <span className="text-xs text-gray-400 whitespace-nowrap">
                  {o.date}
                </span>
              )}
            </div>
            {interp.note && (
              <p className="text-xs text-gray-500 mt-2">{interp.note}</p>
            )}
          </div>
        );
      })}
    </div>
  );
}
