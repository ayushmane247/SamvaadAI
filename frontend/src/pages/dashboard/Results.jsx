import { useLocation, useNavigate } from "react-router-dom";
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ArrowRight,
  Sparkles,
} from "lucide-react";

function getStatus(answers = {}) {
  const occupation = (answers.occupation ?? "").toLowerCase();
  const income = parseInt(answers.income ?? "0", 10);
  if (occupation === "farmer" && income < 500000) return "eligible";
  if (occupation === "farmer") return "partial";
  return "not_eligible";
}

const CARDS = [
  {
    key: "eligible",
    label: "Eligible",
    description:
      "Great news! You are fully eligible for this scheme based on your current profile.",
    Icon: CheckCircle2,
    color: "green",
    activeStyles: "bg-green-500 shadow-green-500/30 border-green-400",
    glow: "bg-green-400/20",
  },
  {
    key: "partial",
    label: "Potentially Eligible",
    description:
      "You match most criteria, but some additional verification may be required.",
    Icon: AlertTriangle,
    color: "amber",
    activeStyles: "bg-amber-500 shadow-amber-500/30 border-amber-400",
    glow: "bg-amber-400/20",
  },
  {
    key: "not_eligible",
    label: "Not Eligible",
    description:
      "Currently, you do not meet the minimum criteria for this specific government scheme.",
    Icon: XCircle,
    color: "red",
    activeStyles: "bg-red-500 shadow-red-500/30 border-red-400",
    glow: "bg-red-400/20",
  },
];

export default function Results() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const answers = state?.answers ?? {};
  const status = getStatus(answers);

  return (
    <div className="max-w-3xl mx-auto space-y-12 animate-in fade-in slide-in-from-bottom-5 duration-700">
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-900/30 border border-blue-100 dark:border-blue-800 text-blue-600 dark:text-blue-400 text-[10px] font-bold uppercase tracking-wider">
          <Sparkles size={12} /> Analysis Complete
        </div>
        <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white">
          Your Eligibility Report
        </h1>
        <p className="text-gray-500 dark:text-gray-400 max-w-lg mx-auto leading-relaxed">
          We matched your profile with the latest guidelines for the
          <span className="font-bold text-gray-900 dark:text-gray-200">
            {" "}
            PM-KISAN Samman Nidhi
          </span>{" "}
          program.
        </p>
      </div>

      <div className="flex flex-wrap justify-center gap-3">
        {Object.entries(answers).map(([key, val]) => (
          <div
            key={key}
            className="glass px-4 py-2 rounded-2xl text-[10px] uppercase font-bold tracking-widest text-gray-400 border border-gray-200/50 dark:border-white/5"
          >
            <span className="text-blue-500 mr-2">{key}</span> {val}
          </div>
        ))}
      </div>

      <div className="grid gap-6">
        {CARDS.map((card) => {
          const isActive = status === card.key;
          const { Icon } = card;

          return (
            <div
              key={card.key}
              className={`relative group p-8 rounded-[2.5rem] transition-all duration-500 overflow-hidden ${
                isActive
                  ? "scale-[1.03] shadow-2xl glass ring-2 ring-blue-500/20"
                  : "opacity-40 grayscale-[0.5] scale-95"
              }`}
            >
              {isActive && (
                <div
                  className={`absolute top-0 right-0 w-32 h-32 ${card.glow} blur-[80px] -mr-10 -mt-10 rounded-full`}
                />
              )}

              <div className="relative z-10 flex flex-col md:flex-row items-center md:items-start gap-6 text-center md:text-left">
                <div
                  className={`w-16 h-16 rounded-[1.5rem] flex items-center justify-center shrink-0 shadow-lg ${
                    isActive
                      ? card.activeStyles
                      : "bg-gray-100 dark:bg-white/5 text-gray-400"
                  }`}
                >
                  <Icon
                    size={32}
                    className={isActive ? "text-white" : "text-gray-400"}
                  />
                </div>

                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-center md:justify-start gap-3">
                    <h3
                      className={`text-xl font-bold ${isActive ? "text-gray-900 dark:text-white" : "text-gray-500"}`}
                    >
                      {card.label}
                    </h3>
                    {isActive && (
                      <span className="px-2 py-0.5 rounded-md bg-blue-600 text-[10px] font-bold text-white uppercase tracking-tighter shadow-lg shadow-blue-600/20">
                        Profile Match
                      </span>
                    )}
                  </div>
                  <p
                    className={`text-sm leading-relaxed max-w-md ${isActive ? "text-gray-600 dark:text-gray-400" : "text-gray-400 dark:text-gray-600"}`}
                  >
                    {card.description}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="pt-8">
        <button
          onClick={() => navigate("/dashboard/scheme/pm-kisan")}
          className="w-full flex items-center justify-center gap-3 px-8 py-5 rounded-[2rem] bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-bold text-lg hover:scale-[1.02] active:scale-[0.98] transition-all shadow-2xl shadow-gray-900/20 dark:shadow-none group"
        >
          Explore Scheme Details
          <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
}
