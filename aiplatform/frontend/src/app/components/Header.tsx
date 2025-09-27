"use client";
import { signOut } from "next-auth/react";

export default function Header() {
  return (
    <div className="h-12 border-b border-neutral-200 bg-white px-4 md:px-6 flex items-center justify-between">
      <div className="font-semibold text-neutral-800">Dental AI Clinic</div>
      <div className="flex items-center gap-3">
        <button
          onClick={() => signOut({ callbackUrl: "/login" })}
          className="text-sm px-3 py-1 rounded bg-neutral-600 hover:bg-neutral-700 text-white"
        >
          Sign out
        </button>
      </div>
    </div>
  );
}
