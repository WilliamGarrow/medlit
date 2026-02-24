const BACKEND_URL = process.env.BACKEND_URL || "http://backend:8000";

interface PatientSummary {
  id: string;
  name: string;
  gender: string;
  birth_date: string;
  age: number;
  condition_count: number;
  medication_count: number;
  observation_count: number;
}

interface HealthData {
  status: string;
  fhir_data: string;
  fhir_patients: number;
  ollama: string;
}

async function getHealth(): Promise<HealthData | null> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/health`, {
      cache: "no-store",
    });
    const json = await res.json();
    return json.data;
  } catch {
    return null;
  }
}

async function getPatients(): Promise<PatientSummary[]> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/patients`, {
      cache: "no-store",
    });
    const json = await res.json();
    return json.data ?? [];
  } catch {
    return [];
  }
}

export default async function Home() {
  const [health, patients] = await Promise.all([getHealth(), getPatients()]);

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900">MedLit</h1>
          <p className="text-sm text-gray-500">
            Patient Health Literacy Dashboard
          </p>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        {/* Health Status */}
        <section className="bg-white rounded-lg border border-gray-200 p-6">
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
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Patients
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
      </div>
    </main>
  );
}

function StatusItem({ label, value }: { label: string; value: string }) {
  const isGood =
    value === "healthy" || value === "loaded" || value === "stub mode";
  return (
    <div>
      <span className="text-gray-500">{label}: </span>
      <span className={isGood ? "text-green-700 font-medium" : "text-gray-900"}>
        {value}
      </span>
    </div>
  );
}

function PatientCard({ patient }: { patient: PatientSummary }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h3 className="font-semibold text-gray-900">{patient.name}</h3>
      <p className="text-sm text-gray-500 mb-3">
        {patient.age}y {patient.gender} &middot; DOB {patient.birth_date}
      </p>
      <div className="flex gap-4 text-xs text-gray-600">
        <span>{patient.condition_count} conditions</span>
        <span>{patient.medication_count} medications</span>
        <span>{patient.observation_count} labs</span>
      </div>
    </div>
  );
}
