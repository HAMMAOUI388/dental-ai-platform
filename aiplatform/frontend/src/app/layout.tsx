// src/app/layout.tsx
import "./globals.css";
import Providers from "./providers";

export const metadata = {
  title: "Dental AI — Clinic",
  description: "Clinic-only Dental AI platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-neutral-100 text-neutral-900">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
