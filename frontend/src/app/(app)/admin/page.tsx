import { getHealth, getPatients } from "@/lib/api";
import StatusItem from "@/components/StatusItem";
import PatientCard from "@/components/PatientCard";

export default async function AdminPage() {
  const [health, patients] = await Promise.all([getHealth(), getPatients()]);

  return (
    <main className="max-w-5xl mx-auto px-6 py-8 space-y-8">
      {/* Health Status */}
      <section className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          System Status
        </h2>
        {health ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <StatusItem label="API" value={health.status} />
            <StatusItem label="FHIR Data" value={health.fhir_data} />
            <StatusItem
              label="Patients"
              value={String(health.fhir_patients)}
            />
            <StatusItem label="LLM" value={health.ollama} />
          </div>
        ) : (
          <p className="text-red-600 text-sm">
            Backend unreachable. Is the server running?
          </p>
        )}
      </section>

      {/* Patient List */}
      <section>
        <h2 className="text-lg font-semibold text-gray-800 mb-4 border-l-4 border-brand-accent pl-3">
          All Patients
        </h2>
        {patients.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2">
            {patients.map((p) => (
              <PatientCard key={p.id} patient={p} />
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No patients loaded.</p>
        )}
      </section>
    </main>
  );
}
