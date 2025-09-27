"use client";
import React, { useEffect, useRef } from "react";

export default function ChatFeed({ messages }: { messages: any[] }) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  return (
    <div className="p-6 space-y-4">
      {messages.length === 0 ? (
        <div className="text-sm text-neutral-800">
          Start by entering patient info and uploading an X-ray below.
        </div>
      ) : (
        messages.map((m: any) => (
          <div
            key={m.id}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl p-3 shadow ${
                m.role === "user"
                  ? "bg-neutral-900 text-white"
                  : "bg-white border border-neutral-200"
              }`}
            >
              {m.text && <div className="whitespace-pre-wrap text-amber-300">{m.text}</div>}

              {m.analysisReport && (
                <div className="mt-2 text-sm text-neutral-800">
                  <b>Analysis Result:</b>

                  {Array.isArray(m.analysisReport.findings) &&
                    m.analysisReport.findings.length > 0 && (
                      <ul className="list-disc list-inside mt-1">
                        {m.analysisReport.findings.map((f: any, idx: number) => (
                          <li key={idx}>
                            Tooth <b>{f.tooth}</b>: {f.issue}
                          </li>
                        ))}
                      </ul>
                    )}

                  {m.analysisReport.pdf_url && (
                    <div className="mt-2">
                      <a
                        className="underline text-blue-600"
                        href={m.analysisReport.pdf_url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Download Full Report (PDF)
                      </a>
                    </div>
                  )}
                </div>
              )}

              <div className="text-[11px] mt-2 text-neutral-400">
                {new Date(m.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))
      )}
      <div ref={bottomRef} />
    </div>
  );
}
