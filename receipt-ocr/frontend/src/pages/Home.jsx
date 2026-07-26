import { useEffect, useMemo, useState } from "react";
import {
  FiCalendar,
  FiClock,
  FiDollarSign,
  FiHash,
  FiShield,
  FiShoppingBag,
  FiTag,
} from "react-icons/fi";
import Navbar from "../components/Navbar";
import UploadCard from "../components/UploadCard";
import Loader from "../components/Loader";
import ReceiptCard from "../components/ReceiptCard";
import JsonViewer from "../components/JsonViewer";
import Footer from "../components/Footer";
import { extractReceiptData, getApiMeta, normalizeReceiptResponse } from "../services/api";

function toDisplayValue(value) {
  if (value == null) {
    return "—";
  }

  const text = String(value).trim();
  return text.length > 0 ? text : "—";
}

function prettyDate(value) {
  const text = toDisplayValue(value);
  if (text === "—") {
    return text;
  }

  const parsed = new Date(text);
  if (Number.isNaN(parsed.getTime())) {
    return text;
  }

  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
  }).format(parsed);
}

function prettyNumber(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return toDisplayValue(value);
  }

  return new Intl.NumberFormat(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numeric);
}

export default function Home() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [extracted, setExtracted] = useState(null);
  const [rawResponse, setRawResponse] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!selectedFile) {
      setPreviewUrl("");
      return undefined;
    }

    const objectUrl = URL.createObjectURL(selectedFile);
    setPreviewUrl(objectUrl);

    return () => URL.revokeObjectURL(objectUrl);
  }, [selectedFile]);

  const apiMeta = useMemo(() => getApiMeta(), []);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setExtracted(null);
    setRawResponse(null);
    setError("");
  };

  const handleClear = () => {
    setSelectedFile(null);
    setExtracted(null);
    setRawResponse(null);
    setError("");
  };

  const handleExtract = async () => {
    if (!selectedFile) {
      return;
    }

    setIsProcessing(true);
    setError("");

    try {
      const responseData = await extractReceiptData(selectedFile);
      setRawResponse(responseData);
      setExtracted(normalizeReceiptResponse(responseData));
    } catch (requestError) {
      setError(
        requestError?.response?.data?.detail ||
          requestError?.response?.data?.message ||
          "Unable to extract receipt data. Check the API base URL and upload path.",
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const cards = extracted
    ? [
        {
          icon: FiShoppingBag,
          label: "Store Name",
          value: toDisplayValue(extracted.fields.storeName.value),
          confidence: extracted.fields.storeName.confidence,
        },
        {
          icon: FiCalendar,
          label: "Date",
          value: prettyDate(extracted.fields.date.value),
          confidence: extracted.fields.date.confidence,
        },
        {
          icon: FiClock,
          label: "Time",
          value: toDisplayValue(extracted.fields.time.value),
          confidence: extracted.fields.time.confidence,
        },
        {
          icon: FiTag,
          label: "Subtotal",
          value: prettyNumber(extracted.fields.subtotal.value),
          confidence: extracted.fields.subtotal.confidence,
        },
        {
          icon: FiHash,
          label: "Tax",
          value: prettyNumber(extracted.fields.tax.value),
          confidence: extracted.fields.tax.confidence,
        },
        {
          icon: FiDollarSign,
          label: "Total",
          value: prettyNumber(extracted.fields.total.value),
          confidence: extracted.fields.total.confidence,
          accent: true,
        },
        {
          icon: FiShield,
          label: "Confidence Score",
          value: `${Math.round(Number(extracted.fields.confidenceScore || 0) * 100)}%`,
          confidence: extracted.fields.confidenceScore,
          accent: true,
        },
      ]
    : [];

  return (
    <div className="min-h-screen text-slate-900">
      <Navbar />

      <main className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-[420px] noise-overlay opacity-30" />
        <div className="pointer-events-none absolute -left-20 top-28 h-56 w-56 rounded-full bg-brand-100/50 blur-3xl" />
        <div className="pointer-events-none absolute right-0 top-56 h-72 w-72 rounded-full bg-accent-500/10 blur-3xl" />

        <section className="mx-auto w-full max-w-7xl px-4 pb-8 pt-10 sm:px-6 lg:px-8 lg:pt-16">
          <div className="max-w-3xl">
            <p className="inline-flex items-center rounded-full border border-brand-100 bg-white/80 px-4 py-2 text-sm font-semibold text-brand-600 shadow-sm">
              Modern receipt extraction dashboard
            </p>
            <h1 className="font-display mt-6 text-4xl font-bold tracking-tight text-slate-950 sm:text-5xl lg:text-6xl">
              Receipt OCR Data Extraction
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600 sm:text-xl">
              Extract structured information from receipts using Artificial Intelligence.
            </p>
          </div>

          <div className="mt-10 grid gap-8 lg:grid-cols-[1.3fr_0.9fr]">
            <UploadCard
              file={selectedFile}
              isProcessing={isProcessing}
              previewUrl={previewUrl}
              onClear={handleClear}
              onExtract={handleExtract}
              onFileSelect={handleFileSelect}
            />

            <div className="space-y-6">
              <div className="glass-card rounded-[28px] border border-slate-200/80 p-6 shadow-soft">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-500">API Status</p>
                <h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-900">Connected frontend shell</h2>
                <p className="mt-3 text-sm leading-6 text-slate-500">
                  The API client is configured through environment variables so you can point this UI at the existing
                  backend without changing any server code.
                </p>

                <div className="mt-5 space-y-3 rounded-3xl bg-slate-50 p-4 text-sm text-slate-600">
                  <div className="flex items-center justify-between gap-4">
                    <span>Base URL</span>
                    <span className="font-medium text-slate-900">{apiMeta.baseURL}</span>
                  </div>
                  <div className="flex items-center justify-between gap-4">
                    <span>Upload path</span>
                    <span className="font-medium text-slate-900">{apiMeta.uploadPath}</span>
                  </div>
                </div>
              </div>

              {isProcessing ? (
                <Loader />
              ) : (
                <div className="glass-card rounded-[28px] border border-slate-200/80 p-6 shadow-soft">
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-accent-500">Workflow</p>
                  <div className="mt-4 space-y-4 text-sm leading-6 text-slate-600">
                    <p>1. Upload a receipt image.</p>
                    <p>2. Preview it before submission.</p>
                    <p>3. Extract structured receipt data from the backend API.</p>
                    <p>4. Review the cards, raw JSON, and download the response.</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        <section id="results" className="mx-auto w-full max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
          {error ? (
            <div className="mb-8 rounded-[24px] border border-rose-200 bg-rose-50 px-5 py-4 text-sm font-medium text-rose-700 shadow-sm">
              {error}
            </div>
          ) : null}

          {cards.length > 0 ? (
            <div className="space-y-6">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-500">Results</p>
                <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">Extracted receipt information</h2>
              </div>

              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {cards.map((card, index) => (
                  <div key={card.label} className="animate-fadeUp" style={{ animationDelay: `${index * 70}ms` }}>
                    <ReceiptCard {...card} delay={index * 70} />
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="rounded-[28px] border border-dashed border-slate-200 bg-white/70 px-6 py-12 text-center shadow-soft">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">No results yet</p>
              <h2 className="font-display mt-3 text-3xl font-bold tracking-tight text-slate-900">
                Upload a receipt to see extracted data
              </h2>
              <p className="mx-auto mt-4 max-w-2xl text-base leading-7 text-slate-500">
                Once you click Extract Data, the response will appear here as polished summary cards and a raw JSON
                preview.
              </p>
            </div>
          )}
        </section>

        <section className="mx-auto w-full max-w-7xl px-4 pb-12 sm:px-6 lg:px-8">
          <JsonViewer data={rawResponse} />
        </section>
      </main>

      <Footer />
    </div>
  );
}
