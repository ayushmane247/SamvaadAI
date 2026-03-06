import { Mic, Sparkles, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-12 animate-in fade-in zoom-in duration-700">
      <div className="text-center space-y-4">
        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          Welcome back
        </h1>
        <p className="text-gray-500 dark:text-gray-400 max-w-sm mx-auto leading-relaxed text-sm">
          What would you like to discover today? Talk to SamvaadAI to find
          eligible government schemes.
        </p>
      </div>

      <div className="relative group">
        <div className="absolute inset-0 bg-blue-600 rounded-full blur-3xl opacity-20 group-hover:opacity-40 transition-opacity animate-pulse" />
        <button
          onClick={() => navigate("/dashboard/chat")}
          className="relative w-48 h-48 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 flex flex-col items-center justify-center text-white cursor-pointer hover:scale-110 active:scale-95 transition-all duration-500 shadow-2xl shadow-blue-600/40 group overflow-hidden"
        >
          <div className="absolute inset-0 bg-white/10 translate-y-full group-hover:translate-y-0 transition-transform duration-500" />
          <Mic
            size={64}
            className="relative z-10 mb-2 group-hover:rotate-12 transition-transform"
          />
          <span className="relative z-10 text-[10px] uppercase font-black tracking-widest opacity-80">
            Tap to start
          </span>
        </button>
      </div>

      <div className="flex flex-col items-center gap-6 w-full max-w-xs">
        <button
          onClick={() => navigate("/dashboard/chat")}
          className="w-full flex items-center justify-between px-6 py-4 rounded-2xl glass border border-white/20 dark:border-white/5 hover:bg-white dark:hover:bg-gray-900 transition-all group shadow-xl shadow-black/5"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center">
              <Sparkles size={18} className="text-blue-600" />
            </div>
            <span className="text-sm font-bold text-gray-700 dark:text-gray-200">
              Start new search
            </span>
          </div>
          <ArrowRight
            size={18}
            className="text-gray-400 group-hover:translate-x-1 transition-transform"
          />
        </button>
      </div>
    </div>
  );
}
