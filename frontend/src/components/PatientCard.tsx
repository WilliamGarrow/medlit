import Link from "next/link";
import type { PatientSummary } from "@/lib/types";

export default function PatientCard({ patient }: { patient: PatientSummary }) {
  const isHapi = patient.source === "hapi-fhir";

  return (
    <Link
      href={`/patients/${patient.id}`}
      className={`block bg-white rounded-lg border border-gray-200 p-5 shadow-sm hover:shadow-md transition-all border-l-4 ${
        isHapi
          ? "border-l-indigo-500 hover:border-indigo-300"
          : "border-l-teal-500 hover:border-brand-accent"
      }`}
    >
      <div className="flex items-center gap-2">
        <h3 className="font-semibold text-gray-900">{patient.name}</h3>
        {isHapi && (
          <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded bg-indigo-100 text-indigo-700">
            HAPI FHIR
          </span>
        )}
      </div>
      <p className="text-sm text-gray-500 mb-3">
        {patient.age}y {patient.gender} &middot; DOB {patient.birth_date}
      </p>
      <div className="flex gap-2 text-xs">
        <span className="bg-brand-muted text-gray-700 px-2 py-0.5 rounded-full">
          {patient.condition_count} conditions
        </span>
        <span className="bg-brand-muted text-gray-700 px-2 py-0.5 rounded-full">
          {patient.medication_count} medications
        </span>
        <span className="bg-brand-muted text-gray-700 px-2 py-0.5 rounded-full">
          {patient.observation_count} labs
        </span>
      </div>
    </Link>
  );
}
