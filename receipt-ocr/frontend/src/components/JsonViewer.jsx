import { useState } from "react";
import { FiCopy, FiCheck } from "react-icons/fi";
import DownloadButton from "./DownloadButton";

export default function JsonViewer({ data }) {
  const [copied, setCopied] = useState(false);
  const formattedJson = JSON.stringify(data ?? {}, null, 2);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(formattedJson);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1400);
  };

  return (
    <section id="json" className="glass-card rounded-[28px] border border-slate-200/80 shadow-soft">
      <div className="flex flex-col gap-4 border-b border-slate-200/70 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-500">Raw Response</p>
          <h3 className="mt-2 text-2xl font-bold tracking-tight text-slate-900">JSON Viewer</h3>
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition-all hover:border-slate-300 hover:bg-slate-50"
            type="button"
            onClick={handleCopy}
          >
            {copied ? <FiCheck className="text-accent-500" /> : <FiCopy />}
            {copied ? "Copied" : "Copy"}
          </button>
          <DownloadButton data={data} fileName="receipt-response.json" />
        </div>
      </div>

      <div className="bg-slate-950 px-5 py-5 sm:px-6">
        <pre className="overflow-x-auto rounded-[24px] border border-white/10 bg-slate-950 p-5 text-sm leading-7 text-slate-100 shadow-inner">
          <code>{formattedJson}</code>
        </pre>
      </div>
    </section>
  );
}
