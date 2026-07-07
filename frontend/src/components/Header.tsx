import Link from "next/link";
import { BookOpenIcon, UsersIcon } from "./Icons";
import LogoutButton from "./LogoutButton";

export default function Header() {
  return (
    <header>
      <div className="bg-brand-navy">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="hover:opacity-80">
            <h1 className="font-display text-2xl font-semibold tracking-tight text-white">
              MedLit<span className="text-brand-bright">.</span>
            </h1>
            <p className="text-sm text-slate-300">
              Medical records, explained at your reading level
            </p>
          </Link>
          <nav className="flex items-center gap-4">
            <Link
              href="/how-it-works"
              className="flex items-center gap-1 text-sm text-slate-300 hover:text-white transition-colors"
            >
              <BookOpenIcon size={14} strokeWidth={1.5} />
              How It Works
            </Link>
            <Link
              href="/admin"
              className="flex items-center gap-1 text-sm text-slate-400 hover:text-white transition-colors"
            >
              <UsersIcon size={14} strokeWidth={1.5} />
              All Patients
            </Link>
            <LogoutButton />
          </nav>
        </div>
      </div>
      <div className="accent-line" />
    </header>
  );
}
