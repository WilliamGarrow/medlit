"use client";

import { useRouter } from "next/navigation";
import type { PatientSummary } from "@/lib/types";

export default function PatientSelector({
  patients,
}: {
  patients: PatientSummary[];
}) {
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = e.target.value;
    if (id) {
      router.push(`/patients/${id}`);
    }
  };

  return (
    <select
      onChange={handleChange}
      defaultValue=""
      className="w-full px-4 py-3 text-base border border-gray-300 rounded-lg bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-accent focus:border-brand-accent"
    >
      <option value="" disabled>
        Select your patient record...
      </option>
      {patients.map((p) => (
        <option key={p.id} value={p.id}>
          {p.name}, {p.age}y {p.gender}
          {p.source === "hapi-fhir" ? " (HAPI FHIR)" : ""}
        </option>
      ))}
    </select>
  );
}
