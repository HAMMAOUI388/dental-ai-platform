"use client";
export default function Footer() {
  return (
    <footer className="h-8 border-t border-neutral-200 bg-white text-[11px] text-neutral-500 flex items-center justify-center">
      © {new Date().getFullYear()} Dental AI
    </footer>
  );
}
