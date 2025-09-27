"use client";
import React from "react";

export default function SidePanel({
  history,
  activeId,
  onSelect,
  onNew,
  onClearAll,
}: {
  history: any[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onClearAll: () => void;
}) {
  return (
    <aside className="h-full min-h-0 w-72 bg-white border-r border-neutral-200 flex flex-col">
      <div className="p-3 border-b">
        <button
          onClick={onNew}
          className="w-full text-sm rounded-lg p-2 bg-neutral-900 text-white hover:bg-black"
        >
          New Case
        </button>
      </div>

      {/* Only this list scrolls */}
      <div className="flex-1 overflow-y-auto">
        {history.length === 0 ? (
          <div className="p-3 text-sm text-neutral-500">No cases yet.</div>
        ) : (
          <ul>
            {history.map((t: any) => (
              <li key={t.id}>
                <button
                  onClick={() => onSelect(t.id)}
                  className={`w-full text-left px-3 py-3 hover:bg-neutral-50 text-neutral-800 ${
                    activeId === t.id ? "bg-neutral-50" : ""
                  }`}
                >
                  <div className="font-medium truncate">{t.title}</div>
                  <div className="text-neutral-500 text-xs">
                    {new Date(t.createdAt).toLocaleString()}
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Clear all button */}
      <div className="p-3 border-t">
        <button
          onClick={onClearAll}
          className="w-full text-sm rounded-lg p-2 bg-red-500 text-white hover:bg-red-600"
        >
          Clear All Cases
        </button>
      </div>

      <div className="p-3 text-xs text-neutral-500 text-center">
        © {new Date().getFullYear()} Dental AI
      </div>
    </aside>
  );
}
