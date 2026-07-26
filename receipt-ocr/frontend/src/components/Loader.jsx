import { useEffect, useState } from "react";
import { FiLoader } from "react-icons/fi";

const messages = [
  "Uploading Receipt...",
  "Running OCR...",
  "Extracting Text...",
  "Generating JSON...",
];

export default function Loader() {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setMessageIndex((currentIndex) => (currentIndex + 1) % messages.length);
    }, 1200);

    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className="glass-card flex w-full items-center justify-between gap-4 rounded-[28px] border border-brand-100 px-5 py-4 shadow-soft">
      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 shadow-inner">
          <FiLoader className="animate-spin text-2xl" />
        </div>
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-500">Processing</p>
          <p className="mt-1 text-lg font-semibold text-slate-900">{messages[messageIndex]}</p>
        </div>
      </div>

      <div className="hidden items-center gap-2 sm:flex">
        <span className="h-2.5 w-2.5 rounded-full bg-brand-500 animate-pulseSoft" />
        <span className="h-2.5 w-2.5 rounded-full bg-accent-500 animate-pulseSoft [animation-delay:150ms]" />
        <span className="h-2.5 w-2.5 rounded-full bg-brand-500 animate-pulseSoft [animation-delay:300ms]" />
      </div>
    </div>
  );
}
