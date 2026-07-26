import { FiDownload } from "react-icons/fi";

function downloadJson(data, fileName) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export default function DownloadButton({ data, fileName = "receipt-data.json", className = "", children }) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-2xl bg-brand-500 px-4 py-2.5 text-sm font-semibold text-white transition-all hover:bg-brand-600 hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60 ${className}`}
      disabled={!data}
      type="button"
      onClick={() => downloadJson(data, fileName)}
    >
      <FiDownload />
      {children || "Download JSON"}
    </button>
  );
}
