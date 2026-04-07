import type { ConditionDetail } from "@/lib/types";
import ConditionExplainer from "./ConditionExplainer";
import CodeBadge from "./CodeBadge";

export default function ConditionList({
  conditions,
  patientId,
}: {
  conditions: ConditionDetail[];
  patientId: string;
}) {
  if (conditions.length === 0) {
    return <p className="text-sm text-gray-500">No conditions recorded.</p>;
  }

  return (
    <div className="space-y-4">
      {conditions.map((c, i) => (
        <div
          key={i}
          className="border border-gray-200 border-l-4 border-l-amber-500 rounded-lg p-4 bg-white shadow-sm"
        >
          <div className="flex items-start justify-between gap-4">
            <div>
              <h4 className="font-medium text-gray-900">{c.display}</h4>
              <div className="flex items-center gap-3 mt-1.5">
                <CodeBadge system={c.system} code={c.code} />
                {c.onset && (
                  <span className="text-xs text-gray-400">Onset: {c.onset}</span>
                )}
              </div>
            </div>
          </div>
          <ConditionExplainer
            patientId={patientId}
            conditionIndex={i}
            conditionName={c.display}
          />
        </div>
      ))}
    </div>
  );
}
