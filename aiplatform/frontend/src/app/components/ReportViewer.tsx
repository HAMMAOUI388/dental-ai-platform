// src/app/components/ReportViewer.tsx
'use client';
interface ReportViewerProps {
  reportPath: string;
}

export default function ReportViewer({ reportPath }: ReportViewerProps) {
  return (
    <div className="mt-6">
      <h2 className="text-xl font-semibold mb-2">Report Generated:</h2>
      <a
        href={reportPath}
        target="_blank"
        className="text-blue-600 underline"
        rel="noreferrer"
      >
        View PDF Report
      </a>
    </div>
  );
}
