"use client";

/**
 * SVG diagram of the MedLit RAG pipeline.
 * Mermaid-inspired visual rendered as a React component.
 */

function Box({
  x,
  y,
  w,
  h,
  label,
  sublabel,
  fill = "#f8fafc",
  stroke = "#e2e8f0",
  textColor = "#1e293b",
  radius = 8,
}: {
  x: number;
  y: number;
  w: number;
  h: number;
  label: string;
  sublabel?: string;
  fill?: string;
  stroke?: string;
  textColor?: string;
  radius?: number;
}) {
  return (
    <g>
      <rect
        x={x}
        y={y}
        width={w}
        height={h}
        rx={radius}
        fill={fill}
        stroke={stroke}
        strokeWidth={1.5}
      />
      <text
        x={x + w / 2}
        y={sublabel ? y + h / 2 - 6 : y + h / 2 + 1}
        textAnchor="middle"
        dominantBaseline="middle"
        fill={textColor}
        fontSize={12}
        fontWeight={600}
      >
        {label}
      </text>
      {sublabel && (
        <text
          x={x + w / 2}
          y={y + h / 2 + 10}
          textAnchor="middle"
          dominantBaseline="middle"
          fill="#94a3b8"
          fontSize={9}
        >
          {sublabel}
        </text>
      )}
    </g>
  );
}

function Arrow({
  x1,
  y1,
  x2,
  y2,
  label,
}: {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  label?: string;
}) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.sqrt(dx * dx + dy * dy);
  const ux = dx / len;
  const uy = dy / len;
  const ax = x2 - ux * 6;
  const ay = y2 - uy * 6;

  return (
    <g>
      <line
        x1={x1}
        y1={y1}
        x2={ax}
        y2={ay}
        stroke="#94a3b8"
        strokeWidth={1.5}
      />
      <polygon
        points={`${x2},${y2} ${ax - uy * 4},${ay + ux * 4} ${ax + uy * 4},${ay - ux * 4}`}
        fill="#94a3b8"
      />
      {label && (
        <text
          x={(x1 + x2) / 2 + (dy !== 0 ? 8 : 0)}
          y={(y1 + y2) / 2 + (dx !== 0 ? -6 : 0)}
          textAnchor="middle"
          dominantBaseline="middle"
          fill="#94a3b8"
          fontSize={9}
        >
          {label}
        </text>
      )}
    </g>
  );
}

export function RAGPipelineDiagram() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm overflow-x-auto">
      <svg viewBox="0 0 720 320" className="w-full max-w-3xl mx-auto" style={{ minWidth: 500 }}>
        {/* Row 1: Data sources */}
        <text x={360} y={16} textAnchor="middle" fill="#94a3b8" fontSize={10} fontWeight={600}>
          DATA SOURCES
        </text>
        <Box x={20} y={28} w={130} h={44} label="FHIR R4 Bundle" sublabel="Patient, Conditions, Meds, Labs" fill="#f0fdf4" stroke="#86efac" textColor="#166534" />
        <Box x={180} y={28} w={130} h={44} label="MedlinePlus" sublabel="NLM health education" fill="#eff6ff" stroke="#93c5fd" textColor="#1e40af" />
        <Box x={340} y={28} w={130} h={44} label="openFDA" sublabel="Drug interaction labels" fill="#fef2f2" stroke="#fca5a5" textColor="#991b1b" />
        <Box x={500} y={28} w={130} h={44} label="LOINC Ranges" sublabel="Lab reference values" fill="#fffbeb" stroke="#fcd34d" textColor="#92400e" />

        {/* Arrows to parser */}
        <Arrow x1={85} y1={72} x2={85} y2={110} />
        <Arrow x1={245} y1={72} x2={290} y2={110} />
        <Arrow x1={405} y1={72} x2={370} y2={110} />

        {/* Row 2: Processing */}
        <text x={360} y={100} textAnchor="middle" fill="#94a3b8" fontSize={10} fontWeight={600}>
          PROCESSING
        </text>
        <Box x={20} y={110} w={130} h={44} label="FHIR Parser" sublabel="Extract clinical data" fill="#f1f5f9" stroke="#cbd5e1" />

        {/* Arrow from parser to prompt */}
        <Arrow x1={150} y1={132} x2={210} y2={132} />

        <Box x={210} y={110} w={200} h={44} label="RAG Prompt Builder" sublabel="Patient context + references + level" fill="#f0fdfa" stroke="#5eead4" textColor="#0f766e" />

        {/* Arrow from prompt to LLM */}
        <Arrow x1={310} y1={154} x2={310} y2={194} />

        {/* Row 3: LLM */}
        <text x={360} y={186} textAnchor="middle" fill="#94a3b8" fontSize={10} fontWeight={600}>
          GENERATION
        </text>
        <Box x={210} y={194} w={200} h={44} label="LLM" sublabel="Groq / Ollama / Claude" fill="#faf5ff" stroke="#c4b5fd" textColor="#6d28d9" />

        {/* LOINC direct to frontend */}
        <Arrow x1={565} y1={72} x2={565} y2={194} label="No LLM needed" />
        <Box x={500} y={194} w={130} h={44} label="Lab Interpretation" sublabel="Color-coded status" fill="#fffbeb" stroke="#fcd34d" textColor="#92400e" />

        {/* Arrow from LLM to readability */}
        <Arrow x1={310} y1={238} x2={310} y2={270} />

        {/* Row 4: Output */}
        <text x={360} y={262} textAnchor="middle" fill="#94a3b8" fontSize={10} fontWeight={600}>
          OUTPUT
        </text>
        <Box x={170} y={270} w={140} h={40} label="Readability Scoring" sublabel="Flesch-Kincaid + Gunning Fog" fill="#f1f5f9" stroke="#cbd5e1" />
        <Arrow x1={310} y1={290} x2={360} y2={290} />
        <Box x={360} y={270} w={180} h={40} label="Structured Patient Summary" sublabel="Sections + sources + scores" fill="#f0fdfa" stroke="#5eead4" textColor="#0f766e" />
      </svg>
    </div>
  );
}

export function ArchitectureDiagram() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm overflow-x-auto">
      <svg viewBox="0 0 680 200" className="w-full max-w-3xl mx-auto" style={{ minWidth: 450 }}>
        {/* Client */}
        <Box x={20} y={75} w={100} h={50} label="Browser" sublabel="Next.js React" fill="#f0fdfa" stroke="#5eead4" textColor="#0f766e" />

        <Arrow x1={120} y1={100} x2={160} y2={100} label="HTTPS" />

        {/* Nginx */}
        <Box x={160} y={75} w={80} h={50} label="nginx" sublabel="SSL + routing" fill="#f1f5f9" stroke="#cbd5e1" />

        <Arrow x1={240} y1={85} x2={290} y2={45} label="/api/*" />
        <Arrow x1={240} y1={115} x2={290} y2={135} label="/*" />

        {/* Backend */}
        <Box x={290} y={20} w={120} h={50} label="FastAPI" sublabel="Python backend" fill="#eff6ff" stroke="#93c5fd" textColor="#1e40af" />

        {/* Frontend server */}
        <Box x={290} y={110} w={120} h={50} label="Next.js" sublabel="SSR + static" fill="#f0fdfa" stroke="#5eead4" textColor="#0f766e" />

        {/* External APIs */}
        <Arrow x1={410} y1={35} x2={460} y2={35} />
        <Arrow x1={410} y1={55} x2={460} y2={55} />

        <Box x={460} y={10} w={120} h={30} label="MedlinePlus" fill="#eff6ff" stroke="#93c5fd" textColor="#1e40af" radius={4} />
        <Box x={460} y={46} w={120} h={30} label="openFDA" fill="#fef2f2" stroke="#fca5a5" textColor="#991b1b" radius={4} />

        {/* LLM */}
        <Arrow x1={350} y1={70} x2={350} y2={110} />
        <text x={365} y={95} fill="#94a3b8" fontSize={8}>cache</text>

        <Arrow x1={410} y1={45} x2={620} y2={45} />
        <Box x={620} y={20} w={50} h={50} label="LLM" sublabel="Groq" fill="#faf5ff" stroke="#c4b5fd" textColor="#6d28d9" />

        {/* Docker label */}
        <rect x={150} y={0} width={400} height={175} rx={12} fill="none" stroke="#e2e8f0" strokeWidth={1} strokeDasharray="6 3" />
        <text x={350} y={185} textAnchor="middle" fill="#cbd5e1" fontSize={9}>Docker Compose</text>
      </svg>
    </div>
  );
}

export function GroundingDiagram() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm overflow-x-auto">
      <svg viewBox="0 0 600 180" className="w-full max-w-2xl mx-auto" style={{ minWidth: 400 }}>
        {/* Center: LLM Prompt */}
        <Box x={210} y={60} w={180} h={60} label="LLM Prompt" sublabel="Grounded generation" fill="#faf5ff" stroke="#c4b5fd" textColor="#6d28d9" />

        {/* Left sources */}
        <Box x={10} y={10} w={150} h={34} label="MedlinePlus" sublabel="Per condition + medication" fill="#eff6ff" stroke="#93c5fd" textColor="#1e40af" />
        <Arrow x1={160} y1={27} x2={210} y2={75} />

        <Box x={10} y={56} w={150} h={34} label="openFDA Labels" sublabel="Drug interaction text" fill="#fef2f2" stroke="#fca5a5" textColor="#991b1b" />
        <Arrow x1={160} y1={73} x2={210} y2={86} />

        <Box x={10} y={102} w={150} h={34} label="Patient Context" sublabel="FHIR conditions, meds, labs" fill="#f0fdf4" stroke="#86efac" textColor="#166534" />
        <Arrow x1={160} y1={119} x2={210} y2={103} />

        <Box x={10} y={144} w={150} h={34} label="Reading Level" sublabel="5th / 8th / 12th grade" fill="#fffbeb" stroke="#fcd34d" textColor="#92400e" />
        <Arrow x1={160} y1={161} x2={250} y2={120} />

        {/* Right: output */}
        <Arrow x1={390} y1={90} x2={430} y2={90} />
        <Box x={430} y={46} w={160} h={42} label="Plain-Language" sublabel="Explanation" fill="#f0fdfa" stroke="#5eead4" textColor="#0f766e" />
        <Arrow x1={390} y1={90} x2={430} y2={125} />
        <Box x={430} y={106} w={160} h={42} label="Readability Score" sublabel="FK grade + Gunning Fog" fill="#f1f5f9" stroke="#cbd5e1" />
      </svg>
    </div>
  );
}
