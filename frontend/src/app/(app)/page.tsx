import { getPatients } from "@/lib/api";
import PatientSelector from "@/components/PatientSelector";
import FeatureCallouts from "@/components/FeatureCallouts";
import Reveal from "@/components/Reveal";

export default async function Home() {
  const patients = await getPatients();

  return (
    <main className="max-w-5xl mx-auto px-6 py-8">
      <div className="max-w-2xl mx-auto text-center space-y-6 mt-8">
        <h2 className="font-display text-3xl font-semibold tracking-tight text-brand-navy">
          Welcome to MedLit<span className="text-brand-bright">.</span>
        </h2>
        <p className="text-gray-600 leading-relaxed">
          MedLit helps you understand your health records in plain language.
          Select your patient record below to see a personalized summary of
          your conditions, medications, and lab results, explained at a
          reading level that works for you.
        </p>

        {patients.length > 0 ? (
          <div className="max-w-md mx-auto">
            <PatientSelector patients={patients} />
          </div>
        ) : (
          <p className="text-gray-500 text-sm">
            No patient records available. Please check that the server is
            running.
          </p>
        )}
      </div>

      <Reveal>
        <FeatureCallouts />
      </Reveal>
    </main>
  );
}
