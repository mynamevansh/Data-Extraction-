import { useEffect, useRef, useState } from "react";
import { FiUploadCloud, FiImage, FiX, FiFileText, FiRefreshCw } from "react-icons/fi";

function formatFileSize(bytes) {
  if (!bytes) {
    return "0 KB";
  }

  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** index;
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[index]}`;
}

export default function UploadCard({
  file,
  previewUrl,
  isProcessing,
  onFileSelect,
  onClear,
  onExtract,
}) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => () => setIsDragging(false), []);

  const triggerPicker = () => {
    inputRef.current?.click();
  };

  const handleFiles = (candidateFile) => {
    if (!candidateFile) {
      return;
    }

    if (!candidateFile.type.startsWith("image/")) {
      return;
    }

    onFileSelect(candidateFile);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
    handleFiles(event.dataTransfer.files?.[0]);
  };

  return (
    <section
      id="upload"
      className={`glass-card overflow-hidden rounded-[28px] border border-slate-200/80 shadow-soft transition-all duration-300 ${
        isDragging ? "scale-[1.01] border-brand-500 ring-4 ring-brand-100" : ""
      }`}
      onDragEnter={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={(event) => {
        event.preventDefault();
        setIsDragging(false);
      }}
      onDrop={handleDrop}
    >
      <div className="border-b border-slate-200/70 px-5 py-4 sm:px-6">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-500">Upload</p>
        <h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-900">Drop a receipt image here</h2>
        <p className="mt-2 text-sm leading-6 text-slate-500">
          Supported formats: PNG, JPEG, JPG. The image is sent directly to your backend API for extraction.
        </p>
      </div>

      <div className="p-5 sm:p-6">
        <input
          ref={inputRef}
          accept="image/png,image/jpeg,image/jpg"
          className="hidden"
          type="file"
          onChange={(event) => handleFiles(event.target.files?.[0])}
        />

        {previewUrl ? (
          <div className="space-y-5">
            <div className="overflow-hidden rounded-3xl border border-slate-200 bg-slate-50 shadow-inner">
              <img
                alt={file?.name || "Receipt preview"}
                className="max-h-[420px] w-full object-contain"
                src={previewUrl}
              />
            </div>

            <div className="flex flex-col gap-3 rounded-3xl border border-slate-200 bg-white p-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-50 text-brand-600">
                  <FiImage className="text-xl" />
                </div>
                <div>
                  <p className="font-medium text-slate-900">{file?.name}</p>
                  <p className="text-sm text-slate-500">{formatFileSize(file?.size)}</p>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <button
                  className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition-all hover:border-slate-300 hover:bg-slate-50 hover:shadow-sm"
                  type="button"
                  onClick={triggerPicker}
                >
                  <FiRefreshCw />
                  Change
                </button>
                <button
                  className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition-all hover:border-rose-200 hover:bg-rose-50 hover:text-rose-600"
                  type="button"
                  onClick={onClear}
                >
                  <FiX />
                  Remove
                </button>
              </div>
            </div>
          </div>
        ) : (
          <button
            className="flex w-full flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-slate-200 bg-slate-50 px-6 py-14 text-center transition-all duration-300 hover:border-brand-400 hover:bg-brand-50/50"
            type="button"
            onClick={triggerPicker}
          >
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white text-brand-500 shadow-soft">
              <FiUploadCloud className="text-3xl" />
            </div>
            <p className="mt-5 text-lg font-semibold text-slate-900">Drag and drop your receipt</p>
            <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
              Or click to browse your files. The frontend will preview the receipt before sending it to the API.
            </p>
            <span className="mt-6 inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-slate-200 transition-transform hover:-translate-y-0.5">
              <FiFileText />
              Browse files
            </span>
          </button>
        )}

        <div className="mt-5 flex flex-col gap-3 sm:flex-row">
          <button
            className="inline-flex flex-1 items-center justify-center gap-2 rounded-2xl bg-brand-500 px-5 py-3.5 text-sm font-semibold text-white shadow-lift transition-all hover:bg-brand-600 hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
            disabled={!file || isProcessing}
            type="button"
            onClick={onExtract}
          >
            {isProcessing ? "Extracting..." : "Extract Data"}
          </button>

          <button
            className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-3.5 text-sm font-semibold text-slate-700 transition-all hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={!file || isProcessing}
            type="button"
            onClick={triggerPicker}
          >
            <FiRefreshCw />
            Upload another
          </button>
        </div>
      </div>
    </section>
  );
}
