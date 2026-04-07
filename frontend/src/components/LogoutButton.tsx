"use client";

import { useRouter } from "next/navigation";
import { LogOutIcon } from "./Icons";

export default function LogoutButton() {
  const router = useRouter();

  const handleLogout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
    router.refresh();
  };

  return (
    <button
      onClick={handleLogout}
      className="flex items-center gap-1 text-sm text-slate-400 hover:text-white transition-colors"
    >
      <LogOutIcon size={14} strokeWidth={1.5} />
      Sign out
    </button>
  );
}
