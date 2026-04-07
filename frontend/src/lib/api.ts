import type { APIResponse, HealthData, PatientSummary, PatientDetail } from "./types";

const BACKEND_URL = process.env.BACKEND_URL || "http://backend:8000";

export async function getHealth(): Promise<HealthData | null> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/health`, {
      cache: "no-store",
    });
    const json: APIResponse<HealthData> = await res.json();
    return json.data;
  } catch {
    return null;
  }
}

export async function getPatients(): Promise<PatientSummary[]> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/patients`, {
      cache: "no-store",
    });
    const json: APIResponse<PatientSummary[]> = await res.json();
    return json.data ?? [];
  } catch {
    return [];
  }
}

export async function getPatient(id: string): Promise<PatientDetail | null> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/patients/${id}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    const json: APIResponse<PatientDetail> = await res.json();
    return json.data;
  } catch {
    return null;
  }
}
