import { notFound } from "next/navigation";
import { getPatient } from "@/lib/api";
import BackLink from "@/components/BackLink";
import SectionHeading from "@/components/SectionHeading";
import PatientSummary from "@/components/PatientSummary";
import ConditionList from "@/components/ConditionList";
import MedicationList from "@/components/MedicationList";
import ObservationList from "@/components/ObservationList";
import Reveal from "@/components/Reveal";

export default async function PatientDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const patient = await getPatient(params.id);
  if (!patient) notFound();

  const stats = [
    { value: patient.conditions.length, label: "conditions" },
    { value: patient.medications.length, label: "medications" },
    { value: patient.observations.length, label: "lab results" },
  ];

  return (
    <main className="max-w-5xl mx-auto px-6 py-8 space-y-8">
      <BackLink href="/" label="Back" />

      {/* Demographic hero */}
      <section className="rounded-xl bg-brand-navy text-white p-6 shadow-sm">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="font-display text-2xl font-semibold tracking-tight">
                {patient.name}
              </h2>
              {patient.source === "hapi-fhir" && (
                <span className="px-2 py-0.5 text-xs font-semibold rounded bg-white/15 text-indigo-200">
                  HAPI FHIR
                </span>
              )}
            </div>
            <p className="text-sm text-slate-300 mt-1">
              {patient.age}y {patient.gender} &middot; DOB {patient.birth_date}
            </p>
            {patient.source === "hapi-fhir" && (
              <p className="text-xs text-indigo-200 mt-1">
                Pulled from a live FHIR server (hapi.fhir.org)
              </p>
            )}
          </div>
          <div className="flex gap-3">
            {stats.map((s) => (
              <div
                key={s.label}
                className="rounded-lg bg-white/10 px-4 py-2.5 text-center min-w-[5.5rem]"
              >
                <p className="font-display text-xl font-semibold text-brand-bright">
                  {s.value}
                </p>
                <p className="text-xs text-slate-300">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Health Summary */}
      <Reveal>
        <PatientSummary patientId={patient.id} />
      </Reveal>

      {/* Conditions */}
      <Reveal>
        <section>
          <SectionHeading icon="heart" iconColor="text-amber-500">
            Conditions
            <span className="text-sm font-normal text-gray-400">
              ({patient.conditions.length})
            </span>
          </SectionHeading>
          <ConditionList conditions={patient.conditions} patientId={patient.id} />
        </section>
      </Reveal>

      {/* Medications */}
      <Reveal>
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
      </Reveal>

      {/* Lab Results */}
      <Reveal>
        <section>
          <SectionHeading icon="test-tube" iconColor="text-blue-500">
            Lab Results
            <span className="text-sm font-normal text-gray-400">
              ({patient.observations.length})
            </span>
          </SectionHeading>
          <ObservationList observations={patient.observations} />
        </section>
      </Reveal>
    </main>
  );
}
