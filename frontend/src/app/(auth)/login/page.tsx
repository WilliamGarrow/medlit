"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const json = await res.json();

      if (!res.ok || !json.success) {
        setError(json.detail || "Invalid credentials");
        return;
      }

      router.push("/");
      router.refresh();
    } catch {
      setError("Unable to reach the server");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-brand-surface flex flex-col">
      {/* Top bar */}
      <div className="bg-brand-navy">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-white">MedLit</h1>
          <p className="text-sm text-slate-300">
            Understand Your Health Records
          </p>
        </div>
      </div>
      <div className="accent-line" />

      {/* Hero + Login */}
      <main className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="max-w-4xl w-full grid md:grid-cols-2 gap-12 items-center">
          {/* Left: value prop */}
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900 leading-tight">
              Your health records,
              <br />
              <span className="text-brand-accent">in plain language.</span>
            </h2>
            <p className="text-gray-600 leading-relaxed">
              MedLit transforms complex medical data into explanations you can
              actually understand. Powered by real clinical standards (FHIR,
              SNOMED, RxNorm, LOINC) and grounded in trusted sources from the
              National Library of Medicine.
            </p>
            <div className="space-y-3">
              {[
                {
                  title: "Personalized health summaries",
                  desc: "See how your conditions, medications, and lab results connect.",
                },
                {
                  title: "Adjustable reading levels",
                  desc: "Simple, Standard, or Detailed. You choose what works for you.",
                },
                {
                  title: "Grounded in real sources",
                  desc: "Every explanation cites MedlinePlus, the NIH's trusted health resource.",
                },
              ].map((item) => (
                <div key={item.title} className="flex gap-3">
                  <div className="flex-shrink-0 w-5 h-5 mt-0.5 rounded-full bg-brand-accent/10 flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-brand-accent" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {item.title}
                    </p>
                    <p className="text-xs text-gray-500">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: login card */}
          <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              Sign in
            </h3>
            <p className="text-sm text-gray-500 mb-6">
              Access your patient health dashboard
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label
                  htmlFor="username"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoFocus
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent focus:border-brand-accent"
                  placeholder="Enter your username"
                />
              </div>
              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent focus:border-brand-accent"
                  placeholder="Enter your password"
                />
              </div>

              {error && (
                <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-brand-accent text-white font-medium rounded-lg hover:bg-teal-700 transition-colors disabled:opacity-50"
              >
                {loading ? "Signing in..." : "Sign in"}
              </button>
            </form>

            <div className="mt-6 pt-4 border-t border-gray-100">
              <p className="text-xs text-gray-400 text-center">
                This is a research demo. No real patient data is used.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
