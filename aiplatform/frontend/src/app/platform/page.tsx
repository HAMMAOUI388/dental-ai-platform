// src/app/platform/page.tsx
"use client";

import { useEffect, useState } from "react";
import SidePanel from "../components/SidePanel";
import ChatFeed from "../components/ChatFeed";
import InputArea from "../components/InputArea";
import Header from "../components/Header";
import Footer from "../components/Footer";
import { v4 as uuid } from "uuid";

type Thread = {
  id: string;
  title: string;
  createdAt: number;
  messages: any[];
};

function loadThreads(): Thread[] {
  const raw = localStorage.getItem("threads");
  return raw ? JSON.parse(raw) : [];
}
function saveThreads(threads: Thread[]) {
  localStorage.setItem("threads", JSON.stringify(threads));
  window.dispatchEvent(new StorageEvent("storage", { key: "threads" } as any));
}

export default function Platform() {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const t = loadThreads();
    if (t.length === 0) {
      const newThread: Thread = {
        id: uuid(),
        title: "Untitled case",
        createdAt: Date.now(),
        messages: [],
      };
      setThreads([newThread]);
      setActiveId(newThread.id);
      saveThreads([newThread]);
    } else {
      setThreads(t);
      setActiveId(t[0].id);
    }
  }, []);

  const addMessageToThread = (threadId: string, msg: any) => {
    setThreads((prev) => {
      const copy = prev.map((t) =>
        t.id === threadId ? { ...t, messages: [...t.messages, msg] } : t
      );
      saveThreads(copy);
      return copy;
    });
  };

  const onSend = async ({
    patientId,
    patientName,
    file,
  }: {
    patientId: string;
    patientName: string;
    file: File;
  }) => {
    if (!activeId) return;
    setBusy(true);

    const userMsg = {
      id: uuid(),
      role: "user",
      text: `Patient ID: ${patientId}\nPatient Name: ${patientName}\nFile: ${file.name}`,
      timestamp: Date.now(),
    };
    addMessageToThread(activeId, userMsg);

    const form = new FormData();
    form.append("patient_id", patientId);
    form.append("patient_name", patientName);
    form.append("image", file);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/predict`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        addMessageToThread(activeId, {
          id: uuid(),
          role: "assistant",
          text: `Error: backend returned ${res.status}`,
          timestamp: Date.now(),
        });
      } else {
        const data = await res.json();
        addMessageToThread(activeId, {
          id: uuid(),
          role: "assistant",
          text: data.summary_text ?? "Analysis complete. Reports ready.",
          analysisReport: {
            pdf_url: data.pdf_url ?? null,
            findings: data.detection_report || [],
          },
          timestamp: Date.now(),
          patientId,
          patientName,
        });

        setThreads((prev) => {
          const copy = prev.map((t) => {
            if (t.id !== activeId) return t;
            if (t.title === "Untitled case") {
              return { ...t, title: `${patientId} • ${patientName}` };
            }
            return t;
          });
          saveThreads(copy);
          return copy;
        });
      }
    } catch (e: any) {
      addMessageToThread(activeId, {
        id: uuid(),
        role: "assistant",
        text: `Failed to fetch: ${e?.message ?? e}`,
        timestamp: Date.now(),
      });
    } finally {
      setBusy(false);
    }
  };

  const handleNew = () => {
    const t = {
      id: uuid(),
      title: "Untitled case",
      createdAt: Date.now(),
      messages: [],
    };
    const list = [t, ...threads];
    setThreads(list);
    saveThreads(list);
    setActiveId(t.id);
  };

  const activeThread = threads.find((t) => t.id === activeId) ?? null;


const handleClearAll = () => {
  localStorage.removeItem("threads");

  const newThread: Thread = {
    id: uuid(),
    title: "Untitled case",
    createdAt: Date.now(),
    messages: [],
  };

  setThreads([newThread]);
  setActiveId(newThread.id);
  saveThreads([newThread]);
};


  return (
    <div className="grid h-screen w-screen overflow-hidden min-h-0 min-w-0
                    grid-cols-[18rem_1fr] grid-rows-[3rem_1fr_auto_2rem]">

      {/* Side panel spans all rows on the left */}
      <div className="col-start-1 row-start-1 row-span-4 border-r border-neutral-200 bg-white min-h-0">
<SidePanel
  history={threads}
  activeId={activeId}
  onSelect={(id: string) => setActiveId(id)}
  onNew={handleNew}
  onClearAll={handleClearAll}
/>

      </div>

      {/* Header fixed row */}
      <div className="col-start-2 row-start-1">
        <Header />
      </div>

      {/* Chat area is the ONLY scrollable region */}
      <div className="col-start-2 row-start-2 min-h-0 overflow-y-auto bg-neutral-100">
        {activeThread ? (
          <ChatFeed messages={activeThread.messages} />
        ) : (
          <div className="p-6 text-neutral-500">No active case</div>
        )}
      </div>

      {/* Input just above footer */}
      <div className="col-start-2 row-start-3 bg-white">
        <InputArea onSend={onSend} busy={busy} />
      </div>

      {/* Footer fixed bottom row */}
      <div className="col-start-2 row-start-4">
        <Footer />
      </div>
    </div>
  );
}
