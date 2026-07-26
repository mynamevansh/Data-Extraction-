import { FiCamera } from "react-icons/fi";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/75 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-500 text-white shadow-lift">
            <FiCamera className="text-xl" />
          </div>
          <div>
            <p className="font-display text-lg font-bold tracking-tight text-slate-900">Receipt OCR AI</p>
            <p className="text-sm text-slate-500">Receipt extraction workspace</p>
          </div>
        </div>

        <nav className="hidden items-center gap-6 text-sm font-medium text-slate-500 md:flex">
          <a className="transition-colors hover:text-slate-900" href="#upload">
            Upload
          </a>
          <a className="transition-colors hover:text-slate-900" href="#results">
            Results
          </a>
          <a className="transition-colors hover:text-slate-900" href="#json">
            JSON
          </a>
        </nav>
      </div>
    </header>
  );
}
