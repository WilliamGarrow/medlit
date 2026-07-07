// Shared TypeScript interfaces mirroring backend Pydantic schemas

export interface APIResponse<T> {
  success: boolean;
  data: T | null;
  error: string | null;
}

export interface PatientSummary {
  id: string;
  name: string;
  gender: string;
  birth_date: string;
  age: number;
  condition_count: number;
  medication_count: number;
  observation_count: number;
  source: string;
}

export interface ConditionDetail {
  display: string;
  code: string;
  system: string;
  onset: string | null;
}

export interface MedicationDetail {
  display: string;
  code: string;
  system: string;
  status: string | null;
  dosage: string | null;
  brand_names?: string[];
}

export interface ObservationDetail {
  display: string;
  code: string;
  system: string;
  value: number | string | null;
  unit: string | null;
  date: string | null;
}

export interface PatientDetail {
  id: string;
  name: string;
  gender: string;
  birth_date: string;
  age: number;
  conditions: ConditionDetail[];
  medications: MedicationDetail[];
  observations: ObservationDetail[];
  source: string;
}

export interface ReadabilityScores {
  flesch_kincaid_grade: number;
  gunning_fog: number;
}

export interface MedlinePlusSource {
  title: string;
  url: string;
}

export type ReadingLevel = "simple" | "standard" | "detailed";

export interface SummarySection {
  heading: string;
  icon: string;
  body: string;
}

export interface ExplanationResponse {
  subject: string;
  reading_level: string;
  explanation: string;
  readability: ReadabilityScores;
  sources: MedlinePlusSource[];
  sections: SummarySection[] | null;
  disclaimer: string;
}

export interface HealthData {
  status: string;
  fhir_data: string;
  fhir_patients: number;
  ollama: string;
}
