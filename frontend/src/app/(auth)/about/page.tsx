import Link from "next/link";
import Callout from "@/components/Callout";
import CodeBadge from "@/components/CodeBadge";
import {
  RAGPipelineDiagram,
  ArchitectureDiagram,
  GroundingDiagram,
} from "@/components/PipelineDiagram";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-brand-surface">
      {/* Header */}
      <div className="bg-brand-navy">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">MedLit</h1>
            <p className="text-sm text-slate-300">
              Understand Your Health Records
            </p>
          </div>
          <Link
            href="/login"
            className="px-4 py-2 bg-brand-accent text-white text-sm font-medium rounded-lg hover:bg-teal-700 transition-colors"
          >
            Sign in
          </Link>
        </div>
      </div>
      <div className="accent-line" />

      <main className="max-w-5xl mx-auto px-6 py-8 space-y-12">
        {/* Hero */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            How MedLit Works
          </h2>
          <p className="text-gray-600 leading-relaxed max-w-3xl">
            MedLit is a Retrieval-Augmented Generation (RAG) system that
            transforms structured clinical data into plain-language health
            summaries. It combines real medical coding standards (FHIR, SNOMED
            CT, RxNorm, LOINC), authoritative reference APIs (MedlinePlus,
            openFDA), and LLM generation with readability validation. Every
            explanation is grounded in verifiable sources. The LLM never
            generates from training data alone.
          </p>
        </section>

        {/* Pipeline Overview */}
        <section>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            End-to-End Pipeline
          </h3>
          <RAGPipelineDiagram />
          <p className="text-xs text-gray-400 mt-2 text-center">
            Data flows from FHIR bundles through reference lookups, prompt
            construction, LLM generation, and readability scoring.
          </p>
        </section>

        {/* Data Sources */}
        <section className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-800">
            Data Sources &amp; Standards
          </h3>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
              <h4 className="font-semibold text-gray-900 text-sm mb-2">
                FHIR R4 Bundles
              </h4>
              <p className="text-sm text-gray-600 leading-relaxed mb-3">
                Patient data follows the HL7 FHIR R4 standard, the same format
                used by Epic, Cerner, and every US hospital system. Demo
                patients include hand-crafted Synthea bundles and live data
                pulled from the public HAPI FHIR server via the{" "}
                <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
                  Patient/$everything
                </code>{" "}
                endpoint.
              </p>
              <div className="flex gap-2 flex-wrap">
                <span className="text-xs px-2 py-0.5 bg-green-50 text-green-700 rounded border border-green-200">
                  Patient
                </span>
                <span className="text-xs px-2 py-0.5 bg-green-50 text-green-700 rounded border border-green-200">
                  Condition
                </span>
                <span className="text-xs px-2 py-0.5 bg-green-50 text-green-700 rounded border border-green-200">
                  MedicationRequest
                </span>
                <span className="text-xs px-2 py-0.5 bg-green-50 text-green-700 rounded border border-green-200">
                  Observation
                </span>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
              <h4 className="font-semibold text-gray-900 text-sm mb-2">
                Clinical Terminologies
              </h4>
              <p className="text-sm text-gray-600 leading-relaxed mb-3">
                Each clinical concept is identified by a code from the
                international standard terminology systems. These codes drive
                the reference API lookups and enable interoperability across
                healthcare systems.
              </p>
              <div className="flex gap-2 flex-wrap">
                <CodeBadge system="SNOMED CT" code="13645005" />
                <CodeBadge system="RxNorm" code="310429" />
                <CodeBadge system="LOINC" code="30934-4" />
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
              <h4 className="font-semibold text-gray-900 text-sm mb-2">
                MedlinePlus Connect
              </h4>
              <p className="text-sm text-gray-600 leading-relaxed mb-2">
                Free API from the National Library of Medicine. Returns patient
                education content for any SNOMED, RxNorm, or LOINC code. This
                is the primary grounding source. Every explanation cites NLM
                content rather than relying on LLM training data.
              </p>
              <p className="text-xs text-gray-400">
                connect.medlineplus.gov &middot; No auth required &middot; 100
                req/min
              </p>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
              <h4 className="font-semibold text-gray-900 text-sm mb-2">
                openFDA Drug Labels
              </h4>
              <p className="text-sm text-gray-600 leading-relaxed mb-2">
                FDA-approved drug labeling via the openFDA API. MedLit fetches
                the drug interactions section for each medication by RxNorm
                code. This provides authoritative, regulatory-grade interaction
                data that the LLM uses to explain potential drug-drug
                interactions.
              </p>
              <p className="text-xs text-gray-400">
                api.fda.gov &middot; No auth required &middot; 240 req/min
              </p>
            </div>
          </div>
        </section>

        {/* Grounding Strategy */}
        <section>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            RAG Grounding Strategy
          </h3>
          <p className="text-sm text-gray-600 mb-4 max-w-3xl">
            The LLM receives four layers of context in every prompt. This
            grounding strategy ensures explanations are factual and traceable to
            authoritative sources rather than generated from the model&apos;s
            training data alone.
          </p>
          <GroundingDiagram />
        </section>

        {/* Summary Generation */}
        <section>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Health Summary Generation
          </h3>
          <div className="space-y-4">
            {[
              {
                step: "1",
                title: "Parallel Data Retrieval",
                desc: "For each patient, MedlinePlus and openFDA are queried in parallel for every condition and medication. MedlinePlus provides patient education text; openFDA provides the FDA-approved drug interactions section. Results are cached for 24 hours.",
              },
              {
                step: "2",
                title: "Structured Prompt Construction",
                desc: "A RAG prompt is built with the patient's FHIR data (conditions, medications, lab values), all retrieved MedlinePlus references, FDA drug interaction text, and the target reading level (5th, 8th, or 12th grade). The LLM is instructed to return structured JSON sections.",
              },
              {
                step: "3",
                title: "LLM Generation",
                desc: "The prompt is sent to Llama 3.1 8B via the Groq API (for production) or a local Ollama instance (for development). The provider abstraction layer allows swapping models without code changes, which is useful for evaluation across model sizes.",
              },
              {
                step: "4",
                title: "Structured Output Parsing",
                desc: "The LLM's JSON response is parsed into five sections: Your Conditions, Your Medications, Important Interactions, Lab Results, and Key Takeaways. If parsing fails, the system falls back to rendering the raw text.",
              },
              {
                step: "5",
                title: "Readability Validation",
                desc: "The generated text is scored using Flesch-Kincaid Grade Level (maps to US school grade) and the Gunning Fog Index (years of education needed). These validate that the reading level instruction was followed.",
              },
              {
                step: "6",
                title: "Persistent Caching",
                desc: "The complete response (sections, readability scores, sources) is cached to disk. Subsequent requests for the same patient and reading level are served instantly without an LLM call. The cache survives container restarts.",
              },
            ].map((item) => (
              <div key={item.step} className="flex gap-4">
                <div className="flex-shrink-0 w-7 h-7 rounded-full bg-brand-accent text-white flex items-center justify-center text-xs font-bold">
                  {item.step}
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 text-sm">
                    {item.title}
                  </h4>
                  <p className="text-sm text-gray-600 mt-0.5 leading-relaxed">
                    {item.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Architecture */}
        <section>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            System Architecture
          </h3>
          <ArchitectureDiagram />
          <div className="grid md:grid-cols-3 gap-4 mt-4">
            {[
              {
                name: "Frontend",
                tech: "Next.js 14 + React + Tailwind CSS",
                detail:
                  "Server-side rendering, client components for interactive elements, middleware-based authentication",
              },
              {
                name: "Backend",
                tech: "FastAPI + Python 3.12",
                detail:
                  "Async API with FHIR parsing (fhir.resources), MedlinePlus/openFDA clients, LLM provider abstraction",
              },
              {
                name: "Infrastructure",
                tech: "Docker Compose + nginx + Let's Encrypt",
                detail:
                  "SSL termination, reverse proxy routing, deployed to a cloud VPS with automated certificate management",
              },
            ].map((item) => (
              <div
                key={item.name}
                className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm"
              >
                <h4 className="font-semibold text-gray-900 text-sm">
                  {item.name}
                </h4>
                <p className="text-xs text-brand-accent font-medium mt-0.5">
                  {item.tech}
                </p>
                <p className="text-xs text-gray-500 mt-1.5">{item.detail}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Evaluation */}
        <section>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Evaluation &amp; Research
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            <Callout label="Model Comparison Framework">
              An evaluation script generates the same prompts across multiple
              LLM providers (Groq Llama 8B, Llama 70B, Claude) and compares
              readability scores, latency, and output quality. Results are
              exported as CSV/JSON for analysis.
            </Callout>
            <Callout label="Grounding Depth as a Research Variable">
              The system can be configured to include or exclude grounding
              sources (MedlinePlus only, MedlinePlus + openFDA, or no
              grounding). This enables controlled experiments measuring how
              grounding depth affects hallucination rates and factual accuracy.
            </Callout>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm mt-4">
            <h4 className="font-semibold text-gray-900 text-sm mb-3">
              Open Research Questions
            </h4>
            <ul className="space-y-2 text-sm text-gray-600">
              {[
                "Does readability scoring correlate with actual patient comprehension? (Requires user study)",
                "Can a condition-comorbidity knowledge graph improve multi-condition summaries?",
                "How does grounding depth affect hallucination rates across model sizes?",
                "What is the minimum viable model size for health literacy applications?",
                "Can the system detect when grounding is insufficient to safely explain an interaction?",
              ].map((q, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-brand-accent mt-0.5 flex-shrink-0">
                    &rarr;
                  </span>
                  {q}
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* CTA */}
        <section className="text-center py-8 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            See it in action
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Sign in to explore patient health summaries, medication
            explanations, and readability-scored outputs.
          </p>
          <Link
            href="/login"
            className="inline-block px-6 py-2.5 bg-brand-accent text-white font-medium rounded-lg hover:bg-teal-700 transition-colors"
          >
            Sign in to MedLit
          </Link>
        </section>
      </main>
    </div>
  );
}
