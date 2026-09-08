import { useRef, useState } from "react";
import { FiCheckCircle, FiDownload, FiFileText, FiRefreshCw, FiUploadCloud, FiX } from "react-icons/fi";
import { convertPdfToExcel } from "../services/api";

function formatFileSize(bytes) {
  if (!bytes) return "0 KB";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / 1024 ** index).toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

export default function PdfToExcelCard() {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [isConverting, setIsConverting] = useState(false);
  const [downloadBlob, setDownloadBlob] = useState(null);
  const [error, setError] = useState("");

  const selectFile = (candidate) => {
    if (!candidate) return;
    if (candidate.type !== "application/pdf" && !candidate.name.toLowerCase().endsWith(".pdf")) {
      setError("Please select a PDF file.");
      return;
    }
    setFile(candidate);
    setDownloadBlob(null);
    setError("");
  };

  const convert = async () => {
    if (!file) {
      setError("Please select a PDF file.");
      return;
    }
    setIsConverting(true);
    setError("");
    try {
      const blob = await convertPdfToExcel(file);
      setDownloadBlob(blob);
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || "PDF conversion failed. Please try again.");
    } finally {
      setIsConverting(false);
    }
  };

  const download = () => {
    if (!downloadBlob) return;
    const url = URL.createObjectURL(downloadBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${file?.name?.replace(/\.pdf$/i, "") || "converted"}_converted.xlsx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  const clear = () => {
    setFile(null);
    setDownloadBlob(null);
    setError("");
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <section className="glass-card overflow-hidden rounded-[28px] border border-slate-200/80 shadow-soft">
      <div className="border-b border-slate-200/70 px-5 py-4 sm:px-6">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-accent-500">Document workflow</p>
        <h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-900">PDF to Editable Excel</h2>
        <p className="mt-2 text-sm leading-6 text-slate-500">
          Convert PDF forms into editable Excel workbooks while preserving document layout and form fields.
        </p>
      </div>

      <div className="p-5 sm:p-6">
        <input
          ref={inputRef}
          accept=".pdf,application/pdf"
          className="hidden"
          type="file"
          onChange={(event) => selectFile(event.target.files?.[0])}
        />

        {file ? (
          <div className="flex items-center justify-between gap-4 rounded-3xl border border-slate-200 bg-slate-50 p-4">
            <div className="flex min-w-0 items-center gap-3">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-accent-50 text-accent-600">
                <FiFileText className="text-xl" />
              </div>
              <div className="min-w-0">
                <p className="truncate font-medium text-slate-900">{file.name}</p>
                <p className="text-sm text-slate-500">{formatFileSize(file.size)}</p>
              </div>
            </div>
            <button className="shrink-0 text-slate-500 hover:text-rose-600" type="button" title="Remove PDF" onClick={clear}>
              <FiX />
            </button>
          </div>
        ) : (
          <button
            className="flex w-full flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-slate-200 bg-slate-50 px-6 py-14 text-center transition-all hover:border-accent-400 hover:bg-accent-50/40"
            type="button"
            onClick={() => inputRef.current?.click()}
          >
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white text-accent-500 shadow-soft">
              <FiUploadCloud className="text-3xl" />
            </div>
            <p className="mt-5 text-lg font-semibold text-slate-900">Upload PDF form</p>
            <p className="mt-2 text-sm leading-6 text-slate-500">Choose a PDF to preserve its fields and page layout.</p>
            <span className="mt-6 inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-slate-200">
              <FiFileText /> Browse PDF
            </span>
          </button>
        )}

        {error ? <p className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p> : null}

        {isConverting ? (
          <div className="mt-5 rounded-2xl border border-accent-100 bg-accent-50 px-4 py-3 text-sm font-medium text-accent-700">Converting PDF...</div>
        ) : downloadBlob ? (
          <div className="mt-5 space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-emerald-700"><FiCheckCircle /> Conversion complete</div>
            <button className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-accent-500 px-5 py-3.5 text-sm font-semibold text-white shadow-lift hover:bg-accent-600" type="button" onClick={download}>
              <FiDownload /> Download Excel
            </button>
          </div>
        ) : null}

        <div className="mt-5 flex flex-col gap-3 sm:flex-row">
          <button className="inline-flex flex-1 items-center justify-center gap-2 rounded-2xl bg-accent-500 px-5 py-3.5 text-sm font-semibold text-white shadow-lift hover:bg-accent-600 disabled:cursor-not-allowed disabled:opacity-60" disabled={!file || isConverting} type="button" onClick={convert}>
            {isConverting ? "Converting PDF..." : "Convert to Excel"}
          </button>
          <button className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-3.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50" disabled={isConverting} type="button" onClick={() => inputRef.current?.click()}>
            <FiRefreshCw /> Choose another
          </button>
        </div>
      </div>
    </section>
  );
}