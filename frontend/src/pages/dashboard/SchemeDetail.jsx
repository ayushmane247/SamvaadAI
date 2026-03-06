import { useParams, useNavigate } from "react-router-dom";
import {
  IndianRupee,
  FileText,
  CheckCircle2,
  ArrowLeft,
  ExternalLink,
  Info,
  ChevronRight,
} from "lucide-react";

const SCHEMES = {
  "pm-kisan": {
    title: "PM-KISAN Samman Nidhi Yojana",
    subtitle:
      "Direct income support for all landholding farmer families in India.",
    fullDescription:
      "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) is a Central Sector Scheme that provides income support to all landholding farmers' families in the country to help them meet their farm requirements and domestic needs.",
    tag: "Agriculture",
    benefits: [
      "₹6,000 yearly income support in 3 equal installments",
      "Direct Benefit Transfer (DBT) to bank accounts",
      "Covers all small and marginal farmer families",
      "Electronic fund transfer every 4 months",
      "Zero registration fee for eligible farmers",
    ],
    documents: [
      "Mandatory Aadhaar Card",
      "Land Ownership Documents (Khatauni)",
      "Aadhaar-seeded Bank Passbook",
      "Valid Mobile Number",
      "Voter ID / Identity Proof",
    ],
    applyUrl: "https://pmkisan.gov.in",
  },
};

export default function SchemeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const scheme = SCHEMES[id];

  if (!scheme) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center space-y-6 animate-in fade-in duration-500">
        <div className="w-20 h-20 bg-gray-100 dark:bg-white/5 rounded-3xl flex items-center justify-center">
          <Info size={40} className="text-gray-400" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Scheme not found
          </h1>
          <p className="text-gray-500 max-w-xs">
            We couldn't locate the details for this specific government program.
          </p>
        </div>
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 px-6 py-2.5 rounded-full bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-bold text-sm"
        >
          <ArrowLeft size={16} /> Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-5 duration-700">
      {/* ── Top Navigation ── */}
      <button
        onClick={() => navigate(-1)}
        className="group inline-flex items-center gap-2 text-sm font-bold text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
      >
        <div className="w-8 h-8 rounded-full border border-gray-200 dark:border-white/10 flex items-center justify-center group-hover:border-gray-900 dark:group-hover:border-white transition-colors">
          <ArrowLeft size={14} />
        </div>
        Back to Results
      </button>

      {/* ── Hero Header ── */}
      <div className="glass p-8 md:p-12 rounded-[2.5rem] border border-white/20 dark:border-white/5 shadow-2xl shadow-black/5 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 blur-[100px] -mr-32 -mt-32 rounded-full" />
        <div className="relative z-10 space-y-6">
          <span className="px-3 py-1 rounded-full bg-blue-600/10 text-blue-600 dark:text-blue-400 text-[10px] font-black uppercase tracking-widest border border-blue-600/20">
            {scheme.tag}
          </span>
          <div className="space-y-3">
            <h1 className="text-3xl md:text-5xl font-black text-gray-900 dark:text-white tracking-tighter leading-tight">
              {scheme.title}
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 font-medium">
              {scheme.subtitle}
            </p>
          </div>
          <div className="pt-4 border-t border-gray-200 dark:border-white/10">
            <p className="text-sm text-gray-500 dark:text-gray-500 leading-relaxed italic">
              {scheme.fullDescription}
            </p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* ── Benefits ── */}
        <div className="glass p-8 rounded-[2rem] border border-white/20 dark:border-white/5">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-green-500/10 rounded-xl flex items-center justify-center">
              <IndianRupee size={20} className="text-green-500" />
            </div>
            <h3 className="font-black text-gray-900 dark:text-white uppercase tracking-wider text-xs">
              Benefits
            </h3>
          </div>
          <ul className="space-y-4">
            {scheme.benefits.map((item, i) => (
              <li key={i} className="flex items-start gap-4 group">
                <CheckCircle2
                  size={18}
                  className="text-green-500 shrink-0 mt-0.5 group-hover:scale-110 transition-transform"
                />
                <span className="text-sm text-gray-600 dark:text-gray-400 font-medium leading-relaxed">
                  {item}
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* ── Documents ── */}
        <div className="glass p-8 rounded-[2rem] border border-white/20 dark:border-white/5">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-blue-500/10 rounded-xl flex items-center justify-center">
              <FileText size={20} className="text-blue-500" />
            </div>
            <h3 className="font-black text-gray-900 dark:text-white uppercase tracking-wider text-xs">
              Required Files
            </h3>
          </div>
          <ul className="space-y-4">
            {scheme.documents.map((doc, i) => (
              <li
                key={i}
                className="flex items-center justify-between group p-3 rounded-2xl hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-gray-100 dark:bg-white/10 flex items-center justify-center text-[10px] font-bold text-gray-400 group-hover:bg-blue-600 group-hover:text-white transition-all">
                    {i + 1}
                  </div>
                  <span className="text-xs text-gray-600 dark:text-gray-400 font-bold">
                    {doc}
                  </span>
                </div>
                <ChevronRight
                  size={14}
                  className="text-gray-300 group-hover:translate-x-1 transition-transform"
                />
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* ── Final CTA ── */}
      <div className="pt-6">
        <button
          onClick={() =>
            window.open(scheme.applyUrl, "_blank", "noopener,noreferrer")
          }
          className="w-full flex items-center justify-center gap-3 px-8 py-5 rounded-[2rem] bg-blue-600 hover:bg-blue-700 text-white font-black text-lg hover:scale-[1.02] active:scale-[0.98] transition-all shadow-2xl shadow-blue-600/40 group overflow-hidden relative"
        >
          <div className="absolute inset-0 bg-white/20 translate-x-full group-hover:translate-x-0 transition-transform duration-700 skew-x-12" />
          <span className="relative z-10">Proceed to Official Application</span>
          <ExternalLink className="relative z-10 w-5 h-5 group-hover:-translate-y-1 group-hover:translate-x-1 transition-transform" />
        </button>
        <p className="mt-6 text-center text-[10px] text-gray-400 uppercase tracking-[0.2em] font-bold">
          SamvaadAI facilitates discovery but does not process payments.
        </p>
      </div>
    </div>
  );
}
