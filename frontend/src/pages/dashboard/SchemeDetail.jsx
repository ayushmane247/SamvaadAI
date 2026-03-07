import { useParams, useNavigate } from "react-router-dom";
import {
  IndianRupee,
  CheckCircle2,
  ArrowLeft,
  ExternalLink,
  Info,
  AlertTriangle,
  XCircle,
} from "lucide-react";
import useConversationStore from "../../store/useConversationStore";
import useUIStore from "../../store/useUIStore";
import { t } from "../../lib/i18n";

/**
 * Find a scheme by ID from the eligibility store.
 * Searches all three categories: eligible, partiallyEligible, ineligible.
 */
function findScheme(eligibility, schemeId) {
  if (!eligibility) return { scheme: null, category: null };

  const categories = [
    { key: "eligible", schemes: eligibility.eligible || [] },
    { key: "partiallyEligible", schemes: eligibility.partiallyEligible || [] },
    { key: "ineligible", schemes: eligibility.ineligible || [] },
  ];

  for (const cat of categories) {
    const found = cat.schemes.find((s) => s.scheme_id === schemeId);
    if (found) return { scheme: found, category: cat.key };
  }

  return { scheme: null, category: null };
}

const CATEGORY_CONFIG = {
  eligible: {
    label: "eligible_label",
    Icon: CheckCircle2,
    color: "emerald",
    badgeBg: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
    glowBg: "bg-emerald-500/10",
  },
  partiallyEligible: {
    label: "partial_label",
    Icon: AlertTriangle,
    color: "amber",
    badgeBg: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
    glowBg: "bg-amber-500/10",
  },
  ineligible: {
    label: "ineligible_label",
    Icon: XCircle,
    color: "red",
    badgeBg: "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20",
    glowBg: "bg-red-500/10",
  },
};

export default function SchemeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const eligibility = useConversationStore((s) => s.eligibility);
  const lang = useUIStore((s) => s.language);

  const { scheme, category } = findScheme(eligibility, id);
  const config = category ? CATEGORY_CONFIG[category] : null;

  // ── Scheme not found ──
  if (!scheme) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center space-y-6 animate-in fade-in duration-500">
        <div className="w-20 h-20 bg-gray-100 dark:bg-white/5 rounded-3xl flex items-center justify-center">
          <Info size={40} className="text-gray-400" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {t("scheme_not_found", lang)}
          </h1>
          <p className="text-gray-500 max-w-xs">
            {t("scheme_not_found_desc", lang)}
          </p>
        </div>
        <button
          id="scheme-go-back"
          onClick={() => navigate("/dashboard/results")}
          className="flex items-center gap-2 px-6 py-2.5 rounded-full bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-bold text-sm"
        >
          <ArrowLeft size={16} />
          {t("back_to_results", lang)}
        </button>
      </div>
    );
  }

  const StatusIcon = config.Icon;

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-5 duration-700">
      {/* ── Top Navigation ── */}
      <button
        onClick={() => navigate("/dashboard/results")}
        className="group inline-flex items-center gap-2 text-sm font-bold text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
      >
        <div className="w-8 h-8 rounded-full border border-gray-200 dark:border-white/10 flex items-center justify-center group-hover:border-gray-900 dark:group-hover:border-white transition-colors">
          <ArrowLeft size={14} />
        </div>
        {t("back_to_results", lang)}
      </button>

      {/* ── Hero Header ── */}
      <div className="glass p-8 md:p-12 rounded-[2.5rem] border border-white/20 dark:border-white/5 shadow-2xl shadow-black/5 relative overflow-hidden">
        <div className={`absolute top-0 right-0 w-64 h-64 ${config.glowBg} blur-[100px] -mr-32 -mt-32 rounded-full`} />
        <div className="relative z-10 space-y-6">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-[10px] font-black uppercase tracking-widest ${config.badgeBg}`}>
            <StatusIcon size={12} />
            {t(config.label, lang)}
          </span>
          <div className="space-y-3">
            <h1 className="text-3xl md:text-5xl font-black text-gray-900 dark:text-white tracking-tighter leading-tight">
              {scheme.scheme_name}
            </h1>
            {scheme.benefit && (
              <p className="text-lg text-gray-600 dark:text-gray-400 font-medium">
                {scheme.benefit}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* ── Detail Cards ── */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* ── Benefit / Reasons ── */}
        <div className="glass p-8 rounded-[2rem] border border-white/20 dark:border-white/5">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-blue-500/10 rounded-xl flex items-center justify-center">
              <IndianRupee size={20} className="text-blue-500" />
            </div>
            <h3 className="font-black text-gray-900 dark:text-white uppercase tracking-wider text-xs">
              {t("scheme_details", lang)}
            </h3>
          </div>
          <div className="space-y-4">
            {scheme.benefit && (
              <div className="flex items-start gap-3">
                <CheckCircle2 size={16} className="text-emerald-500 mt-0.5 shrink-0" />
                <span className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                  {scheme.benefit}
                </span>
              </div>
            )}
            {scheme.reasons?.map((reason, i) => (
              <div key={i} className="flex items-start gap-3">
                <XCircle size={16} className="text-red-400 mt-0.5 shrink-0" />
                <span className="text-sm text-gray-500 dark:text-gray-500 leading-relaxed">
                  {reason}
                </span>
              </div>
            ))}
            {scheme.guidance && (
              <div className="flex items-start gap-3">
                <AlertTriangle size={16} className="text-amber-500 mt-0.5 shrink-0" />
                <span className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                  {Array.isArray(scheme.guidance)
                    ? scheme.guidance.join(", ")
                    : scheme.guidance}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* ── Missing Fields (if partial) ── */}
        {scheme.missing_fields?.length > 0 && (
          <div className="glass p-8 rounded-[2rem] border border-white/20 dark:border-white/5">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 bg-amber-500/10 rounded-xl flex items-center justify-center">
                <AlertTriangle size={20} className="text-amber-500" />
              </div>
              <h3 className="font-black text-gray-900 dark:text-white uppercase tracking-wider text-xs">
                {t("missing_fields", lang)}
              </h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {scheme.missing_fields.map((field) => (
                <span
                  key={field}
                  className="px-3 py-1.5 rounded-xl bg-amber-500/10 text-amber-700 dark:text-amber-300 text-xs font-bold"
                >
                  {field}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ── Apply CTA (eligible schemes only) ── */}
      {scheme.source_url && category === "eligible" && (
        <div className="pt-6">
          <button
            id="apply-scheme"
            onClick={() =>
              window.open(scheme.source_url, "_blank", "noopener,noreferrer")
            }
            className="w-full flex items-center justify-center gap-3 px-8 py-5 rounded-[2rem] bg-blue-600 hover:bg-blue-700 text-white font-black text-lg hover:scale-[1.02] active:scale-[0.98] transition-all shadow-2xl shadow-blue-600/40 group overflow-hidden relative"
          >
            <div className="absolute inset-0 bg-white/20 translate-x-full group-hover:translate-x-0 transition-transform duration-700 skew-x-12" />
            <span className="relative z-10">{t("proceed_to_apply", lang)}</span>
            <ExternalLink className="relative z-10 w-5 h-5 group-hover:-translate-y-1 group-hover:translate-x-1 transition-transform" />
          </button>
          <p className="mt-6 text-center text-[10px] text-gray-400 uppercase tracking-[0.2em] font-bold">
            {t("disclaimer", lang)}
          </p>
        </div>
      )}
    </div>
  );
}
