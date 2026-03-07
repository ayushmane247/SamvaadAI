import { useNavigate } from "react-router-dom";
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ArrowRight,
  Sparkles,
  ExternalLink,
  MessageSquare,
  ChevronRight,
} from "lucide-react";
import useConversationStore from "../../store/useConversationStore";
import useUIStore from "../../store/useUIStore";
import { t } from "../../lib/i18n";

// ── Section config ───────────────────────────────────────────────
const SECTIONS = [
  {
    key: "eligible",
    storeKey: "eligible",
    Icon: CheckCircle2,
    iconBg: "bg-emerald-500",
    iconGlow: "bg-emerald-400/20",
    badge: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
    ring: "ring-emerald-500/20",
  },
  {
    key: "partial",
    storeKey: "partiallyEligible",
    Icon: AlertTriangle,
    iconBg: "bg-amber-500",
    iconGlow: "bg-amber-400/20",
    badge: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
    ring: "ring-amber-500/20",
  },
  {
    key: "ineligible",
    storeKey: "ineligible",
    Icon: XCircle,
    iconBg: "bg-red-500",
    iconGlow: "bg-red-400/20",
    badge: "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20",
    ring: "ring-red-500/20",
  },
];

const LABEL_MAP = {
  eligible: "eligible_label",
  partial: "partial_label",
  ineligible: "ineligible_label",
};

// ── Scheme Card Components ───────────────────────────────────────

function EligibleCard({ scheme, lang, onDetail }) {
  return (
    <div
      onClick={() => onDetail(scheme.scheme_id)}
      className="group glass p-6 rounded-[2rem] border border-white/20 dark:border-white/5 hover:shadow-xl hover:scale-[1.01] transition-all duration-300 cursor-pointer"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-3">
          <h4 className="text-lg font-bold text-gray-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
            {scheme.scheme_name}
          </h4>
          {scheme.benefit && (
            <div className="flex items-start gap-2">
              <span className="text-[10px] font-black uppercase tracking-widest text-emerald-600 dark:text-emerald-400 mt-0.5 shrink-0">
                {t("benefit", lang)}
              </span>
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                {scheme.benefit}
              </p>
            </div>
          )}
        </div>
        <ChevronRight
          size={20}
          className="text-gray-300 group-hover:text-emerald-500 group-hover:translate-x-1 transition-all mt-1 shrink-0"
        />
      </div>
      {scheme.source_url && (
        <a
          href={scheme.source_url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="inline-flex items-center gap-1.5 mt-4 px-3 py-1.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-[10px] font-bold uppercase tracking-wider hover:bg-emerald-500/20 transition-colors"
        >
          <ExternalLink size={10} />
          {t("apply_now", lang)}
        </a>
      )}
    </div>
  );
}

function PartialCard({ scheme, lang, onDetail }) {
  return (
    <div
      onClick={() => onDetail(scheme.scheme_id)}
      className="group glass p-6 rounded-[2rem] border border-white/20 dark:border-white/5 hover:shadow-xl hover:scale-[1.01] transition-all duration-300 cursor-pointer"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-3">
          <h4 className="text-lg font-bold text-gray-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">
            {scheme.scheme_name}
          </h4>
          {scheme.missing_fields?.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[10px] font-black uppercase tracking-widest text-amber-600 dark:text-amber-400">
                {t("missing_fields", lang)}
              </span>
              <div className="flex flex-wrap gap-1.5">
                {scheme.missing_fields.map((field) => (
                  <span
                    key={field}
                    className="px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-700 dark:text-amber-300 text-xs font-semibold"
                  >
                    {field}
                  </span>
                ))}
              </div>
            </div>
          )}
          {scheme.guidance && (
            <div className="flex items-start gap-2">
              <span className="text-[10px] font-black uppercase tracking-widest text-amber-600 dark:text-amber-400 mt-0.5 shrink-0">
                {t("guidance", lang)}
              </span>
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                {Array.isArray(scheme.guidance)
                  ? scheme.guidance.join(", ")
                  : scheme.guidance}
              </p>
            </div>
          )}
        </div>
        <ChevronRight
          size={20}
          className="text-gray-300 group-hover:text-amber-500 group-hover:translate-x-1 transition-all mt-1 shrink-0"
        />
      </div>
    </div>
  );
}

function IneligibleCard({ scheme, lang }) {
  return (
    <div className="glass p-6 rounded-[2rem] border border-white/20 dark:border-white/5 opacity-75">
      <div className="space-y-3">
        <h4 className="text-lg font-bold text-gray-900 dark:text-white">
          {scheme.scheme_name}
        </h4>
        {scheme.reasons?.length > 0 && (
          <div className="space-y-1.5">
            <span className="text-[10px] font-black uppercase tracking-widest text-red-500 dark:text-red-400">
              {t("reasons", lang)}
            </span>
            <ul className="space-y-1">
              {scheme.reasons.map((reason, i) => (
                <li
                  key={i}
                  className="text-sm text-gray-500 dark:text-gray-500 leading-relaxed flex items-start gap-2"
                >
                  <XCircle size={14} className="text-red-400 mt-0.5 shrink-0" />
                  {reason}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Main Results Component ───────────────────────────────────────

export default function Results() {
  const navigate = useNavigate();
  const eligibility = useConversationStore((s) => s.eligibility);
  const lang = useUIStore((s) => s.language);

  // No eligibility data — prompt user to start conversation
  if (
    !eligibility ||
    (!eligibility.eligible?.length &&
      !eligibility.partiallyEligible?.length &&
      !eligibility.ineligible?.length)
  ) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-8 animate-in fade-in duration-500">
        <div className="w-20 h-20 bg-blue-100 dark:bg-blue-900/20 rounded-3xl flex items-center justify-center">
          <MessageSquare size={36} className="text-blue-500" />
        </div>
        <div className="text-center space-y-2 max-w-sm">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            {t("no_results", lang)}
          </h2>
        </div>
        <button
          id="go-to-chat"
          onClick={() => navigate("/dashboard/chat")}
          className="flex items-center gap-2 px-6 py-3 rounded-full bg-blue-600 text-white font-bold text-sm hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/30"
        >
          <Sparkles size={16} />
          {t("go_to_chat", lang)}
        </button>
      </div>
    );
  }

  const handleSchemeDetail = (schemeId) => {
    navigate(`/dashboard/scheme/${schemeId}`);
  };

  const totalEligible = eligibility.eligible?.length || 0;
  const totalPartial = eligibility.partiallyEligible?.length || 0;
  const totalIneligible = eligibility.ineligible?.length || 0;

  return (
    <div className="max-w-3xl mx-auto space-y-10 animate-in fade-in slide-in-from-bottom-5 duration-700">
      {/* ── Header ── */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-900/30 border border-blue-100 dark:border-blue-800 text-blue-600 dark:text-blue-400 text-[10px] font-bold uppercase tracking-wider">
          <Sparkles size={12} />
          {t("analysis_complete", lang)}
        </div>
        <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white">
          {t("results_title", lang)}
        </h1>
        <p className="text-gray-500 dark:text-gray-400 max-w-lg mx-auto leading-relaxed">
          {t("results_subtitle", lang)}
        </p>
      </div>

      {/* ── Summary Pills ── */}
      <div className="flex flex-wrap justify-center gap-3">
        {totalEligible > 0 && (
          <div className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs font-bold">
            <CheckCircle2 size={14} />
            {totalEligible} {t("eligible_label", lang)}
          </div>
        )}
        {totalPartial > 0 && (
          <div className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 text-xs font-bold">
            <AlertTriangle size={14} />
            {totalPartial} {t("partial_label", lang)}
          </div>
        )}
        {totalIneligible > 0 && (
          <div className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs font-bold">
            <XCircle size={14} />
            {totalIneligible} {t("ineligible_label", lang)}
          </div>
        )}
      </div>

      {/* ── Sections ── */}
      {SECTIONS.map(({ key, storeKey, Icon, iconBg, iconGlow, ring }) => {
        const schemes = eligibility[storeKey] || [];
        if (schemes.length === 0) return null;

        return (
          <section key={key} className="space-y-4">
            {/* Section Header */}
            <div className="flex items-center gap-3">
              <div className="relative">
                <div
                  className={`absolute inset-0 ${iconGlow} blur-xl rounded-full`}
                />
                <div
                  className={`relative w-10 h-10 ${iconBg} rounded-xl flex items-center justify-center shadow-lg`}
                >
                  <Icon size={20} className="text-white" />
                </div>
              </div>
              <h2 className="text-lg font-black text-gray-900 dark:text-white uppercase tracking-wider text-xs">
                {t(LABEL_MAP[key], lang)}
              </h2>
              <span className="px-2 py-0.5 rounded-md bg-gray-100 dark:bg-white/5 text-[10px] font-bold text-gray-500">
                {schemes.length}
              </span>
            </div>

            {/* Scheme Cards */}
            <div className="grid gap-4">
              {schemes.map((scheme) => {
                if (key === "eligible") {
                  return (
                    <EligibleCard
                      key={scheme.scheme_id}
                      scheme={scheme}
                      lang={lang}
                      onDetail={handleSchemeDetail}
                    />
                  );
                }
                if (key === "partial") {
                  return (
                    <PartialCard
                      key={scheme.scheme_id}
                      scheme={scheme}
                      lang={lang}
                      onDetail={handleSchemeDetail}
                    />
                  );
                }
                return (
                  <IneligibleCard
                    key={scheme.scheme_id}
                    scheme={scheme}
                    lang={lang}
                  />
                );
              })}
            </div>
          </section>
        );
      })}

      {/* ── Back to Chat ── */}
      <div className="pt-4">
        <button
          id="back-to-chat"
          onClick={() => navigate("/dashboard/chat")}
          className="w-full flex items-center justify-center gap-3 px-8 py-5 rounded-[2rem] bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-bold text-lg hover:scale-[1.02] active:scale-[0.98] transition-all shadow-2xl shadow-gray-900/20 dark:shadow-none group"
        >
          {t("continue_conversation", lang)}
          <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
}
