import { FiTrendingUp } from "react-icons/fi";

function formatConfidence(confidence) {
  if (confidence == null || Number.isNaN(Number(confidence))) {
    return "—";
  }

  const numeric = Number(confidence);
  if (numeric > 1) {
    return `${numeric.toFixed(0)}%`;
  }

  return `${Math.round(numeric * 100)}%`;
}

export default function ReceiptCard({ icon: Icon, label, value, confidence, delay = 0, accent = false }) {
  const displayValue = value && String(value).trim() ? value : "Not available";

  return (
    <article
      className="glass-card group rounded-[24px] border border-slate-200/80 p-5 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-lift"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div
            className={`flex h-12 w-12 items-center justify-center rounded-2xl ${
              accent ? "bg-accent-500 text-white" : "bg-brand-50 text-brand-600"
            }`}
          >
            <Icon className="text-xl" />
          </div>
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-slate-500">{label}</p>
            <p className="mt-1 text-xl font-semibold tracking-tight text-slate-900">{displayValue}</p>
          </div>
        </div>

        <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
          <FiTrendingUp />
          {formatConfidence(confidence)}
        </span>
      </div>
    </article>
  );
}
