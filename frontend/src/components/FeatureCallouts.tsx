"use client";

import { FileTextIcon, PillIcon, SlidersIcon } from "./Icons";

const FEATURES = [
  {
    icon: FileTextIcon,
    title: "Health Summary",
    desc: "Get a plain-language overview of your conditions and how they relate to each other.",
  },
  {
    icon: PillIcon,
    title: "Medication Explanations",
    desc: "Understand why each medication was prescribed and what to watch for.",
  },
  {
    icon: SlidersIcon,
    title: "Reading Levels",
    desc: "Choose Simple, Standard, or Detailed. Every explanation adapts to your comfort level.",
  },
];

export default function FeatureCallouts() {
  return (
    <div className="grid md:grid-cols-3 gap-8 mt-16 max-w-3xl mx-auto">
      {FEATURES.map((item) => (
        <div key={item.title} className="text-center space-y-2">
          <div className="w-10 h-10 rounded-full bg-brand-muted flex items-center justify-center mx-auto">
            <item.icon
              size={20}
              className="text-brand-accent"
              strokeWidth={1.5}
            />
          </div>
          <h4 className="font-medium text-gray-900 text-sm">{item.title}</h4>
          <p className="text-xs text-gray-500">{item.desc}</p>
        </div>
      ))}
    </div>
  );
}
