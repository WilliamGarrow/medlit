import { notFound } from "next/navigation";
import { getPatient } from "@/lib/api";
import BackLink from "@/components/BackLink";
import SectionHeading from "@/components/SectionHeading";
import PatientSummary from "@/components/PatientSummary";
import ConditionList from "@/components/ConditionList";
import MedicationList from "@/components/MedicationList";
import ObservationList from "@/components/ObservationList";

export default async function PatientDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const patient = await getPatient(params.id);
  if (!patient) notFound();

  return (
    <main className="max-w-5xl mx-auto px-6 py-8 space-y-8">
      <BackLink href="/" label="Back" />

      {/* Demographic header */}
      <section className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <div className="flex items-center gap-2">
          <h2 className="text-xl font-bold text-gray-900">{patient.name}</h2>
          {patient.source === "hapi-fhir" && (
            <span className="px-2 py-0.5 text-xs font-semibold rounded bg-indigo-100 text-indigo-700">
              HAPI FHIR
            </span>
          )}
        </div>
        <p className="text-sm text-gray-500 mt-1">
          {patient.age}y {patient.gender} &middot; DOB {patient.birth_date}
        </p>
        {patient.source === "hapi-fhir" && (
          <p className="text-xs text-indigo-600 mt-1">
            This patient was pulled from a live FHIR server (hapi.fhir.org)
          </p>
        )}
      </section>

      {/* Health Summary */}
      <PatientSummary patientId={patient.id} />

      {/* Conditions */}
      <section>
        <SectionHeading icon="heart" iconColor="text-amber-500">
          Conditions
          <span className="text-sm font-normal text-gray-400">
            ({patient.conditions.length})
          </span>
        </SectionHeading>
        <ConditionList conditions={patient.conditions} patientId={patient.id} />
      </section>

      {/* Medications */}
      <section>
        <SectionHeading icon="pill" iconColor="text-teal-500">
          Medications
          <span className="text-sm font-normal text-gray-400">
            ({patient.medications.length})
          </span>
        </SectionHeading>
        <MedicationList
          medications={patient.medications}
          patientId={patient.id}
        />
      </section>

      {/* Lab Results */}
      <section>
        <SectionHeading icon="test-tube" iconColor="text-blue-500">
          Lab Results
          <span className="text-sm font-normal text-gray-400">
            ({patient.observations.length})
          </span>
        </SectionHeading>
        <ObservationList observations={patient.observations} />
      </section>
    </main>
  );
}
