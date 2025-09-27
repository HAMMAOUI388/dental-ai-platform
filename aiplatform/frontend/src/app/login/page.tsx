// src/app/login/page.tsx
"use client";
import { signIn } from "next-auth/react";
import { useState } from "react";
export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [pending, setPending] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  
  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPending(true);
    setErr(null);
    const res = await signIn("credentials", {
      redirect: true,
      email,
      password,
      callbackUrl: "/platform",
    });
    setPending(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-100">
      <div className="w-full max-w-sm bg-white shadow rounded-2xl p-6">
        <h1 className="text-xl font-semibold text-neutral-900 mb-4">Clinic Login</h1>
        <form onSubmit={onSubmit} className="space-y-3">
          <input
            className="w-full border border-neutral-300 rounded-lg p-2 outline-none focus:ring-1 focus:text-neutral-900"
            placeholder="Email"
            type="email"
            value={email}
            onChange={(e)=>setEmail(e.target.value)}
            required
          />
          <input
            className="w-full border border-neutral-300 rounded-lg p-2 outline-none focus:ring-1 focus:text-neutral-900"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e)=>setPassword(e.target.value)}
            required
          />
          {err && <p className="text-sm text-red-600">{err}</p>}
          <button
            type="submit"
            disabled={pending}
            className="w-full rounded-lg p-2 bg-neutral-900 text-white hover:bg-black disabled:opacity-60"
          >
            {pending ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
