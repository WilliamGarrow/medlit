"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { trackActivity } from "@/lib/tracking";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleDemo = async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await fetch("/api/auth/demo", { method: "POST" });
      const json = await res.json();
      if (!res.ok || !json.success) {
        setError("Demo entry is unavailable right now");
        return;
      }
      trackActivity("login", "demo-oneclick");
      router.push("/");
      router.refresh();
    } catch {
      setError("Unable to reach the server");
    } finally {
      setLoading(false);
    }
  };

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

      trackActivity("login", username);
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
          <h1 className="font-display text-2xl font-semibold tracking-tight text-white">
            MedLit<span className="text-brand-bright">.</span>
          </h1>
          <p className="text-sm text-slate-300">
            Medical records, explained at your reading level
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
                  title: "Grounded in sources you can check",
                  desc: "Every explanation cites MedlinePlus, openFDA drug labels, and RxNav.",
                },
                {
                  title: "A reading level you choose, then verified",
                  desc: "Simple, Standard, or Detailed, scored on the output with Flesch-Kincaid.",
                },
                {
                  title: "Lab results never touch the model",
                  desc: "Reference ranges decide normal or abnormal deterministically.",
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
              See it working
            </h3>
            <p className="text-sm text-gray-500 mb-5">
              Eight synthetic patients, real clinical coding
            </p>

            <button
              type="button"
              onClick={handleDemo}
              disabled={loading}
              className="w-full py-2.5 bg-brand-navy text-white font-medium rounded-lg hover:bg-brand-accent transition-colors disabled:opacity-50"
            >
              {loading ? "One moment..." : "Enter the demo"}
            </button>

            <div className="my-5 flex items-center gap-3">
              <div className="h-px flex-1 bg-gray-200" />
              <span className="text-xs text-gray-400">or sign in</span>
              <div className="h-px flex-1 bg-gray-200" />
            </div>

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

            <div className="mt-6 pt-4 border-t border-gray-100 space-y-2">
              <p className="text-xs text-gray-400 text-center">
                Research prototype. Synthetic patients only, never real data.
              </p>
              <p className="text-xs text-center">
                <a href="/about" className="text-brand-accent hover:underline">
                  How it works
                </a>
                <span className="text-gray-300 mx-2">·</span>
                <a
                  href="https://williamgarrow.com"
                  className="text-brand-accent hover:underline"
                >
                  Built by William Garrow
                </a>
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
