import type { MedicationDetail } from "@/lib/types";
import MedicationExplainer from "./MedicationExplainer";
import CodeBadge from "./CodeBadge";

export default function MedicationList({
  medications,
  patientId,
}: {
  medications: MedicationDetail[];
  patientId: string;
}) {
  if (medications.length === 0) {
    return <p className="text-sm text-gray-500">No medications recorded.</p>;
  }

  return (
    <div className="space-y-4">
      {medications.map((med, i) => (
        <div
          key={i}
          className="border border-gray-200 border-l-4 border-l-brand-accent rounded-lg p-4 bg-white shadow-sm"
        >
          <div className="flex items-start justify-between gap-4">
            <div>
              <h4 className="font-medium text-gray-900">
                {med.display}
                {med.brand_names && med.brand_names.length > 0 && (
                  <span className="ml-2 text-brand-accent font-semibold">
                    ({med.brand_names.join(", ")})
                  </span>
                )}
              </h4>
              {med.dosage && (
                <p className="text-sm text-gray-500 mt-1">{med.dosage}</p>
              )}
              <div className="flex items-center gap-3 mt-1.5">
                <CodeBadge system={med.system} code={med.code} />
                {med.status && (
                  <span className="text-xs text-gray-400">Status: {med.status}</span>
                )}
              </div>
            </div>
          </div>
          <MedicationExplainer
            patientId={patientId}
            medIndex={i}
            medicationName={med.display}
          />
        </div>
      ))}
    </div>
  );
}
