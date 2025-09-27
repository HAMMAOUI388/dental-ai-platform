"use client";
import React, { useRef, useState } from "react";

export default function InputArea({
  onSend,
  busy,
}: {
  onSend: (payload: { patientId: string; patientName: string; file: File }) => Promise<void>;
  busy?: boolean;
}) {
  const [patientId, setPatientId] = useState("");
  const [patientName, setPatientName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const fileRef = useRef<HTMLInputElement | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    await onSend({ patientId, patientName, file });
    if (fileRef.current) fileRef.current.value = "";
    setFile(null);
  };

  return (
    <form
      onSubmit={submit}
      className="w-full border-t border-neutral-200 bg-white p-3 flex gap-2 items-center"
    >
      <input
        className="border border-neutral-300 rounded-lg p-2 text-sm outline-none focus:ring-1 text-neutral-800 w-36"
        placeholder="Patient ID"
        value={patientId}
        onChange={(e) => setPatientId(e.target.value)}
        required
      />
      <input
        className="border border-neutral-300 rounded-lg p-2 text-sm outline-none focus:ring-1 text-neutral-800 w-56"
        placeholder="Patient Name"
        value={patientName}
        onChange={(e) => setPatientName(e.target.value)}
        required
      />
      <input
        ref={fileRef}
        type="file"
        name="xray"
        accept="image/*"
        aria-label="Upload X-ray"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        className="border rounded p-2 w-full text-neutral-500"
        required
      />
      <button
        type="submit"
        disabled={busy || !file}
        className="ml-auto rounded-lg px-4 py-2 text-sm bg-neutral-900 text-white hover:bg-black disabled:opacity-60"
      >
        {busy ? "Processing…" : "Send"}
      </button>
    </form>
  );
}
