import { Link } from "react-router-dom";
import {
  MessageSquare,
  ShieldCheck,
  Zap,
  Languages,
  Mic,
  Bot,
  Landmark,
  ArrowRight,
} from "lucide-react";

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 selection:bg-blue-100 dark:selection:bg-blue-900 overflow-x-hidden">
      <style>{`
        @keyframes float-slow {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }
        @keyframes float-medium {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-15px); }
        }
        .animate-float-slow {
          animation: float-slow 6s ease-in-out infinite;
        }
        .animate-float-medium {
          animation: float-medium 4s ease-in-out infinite;
        }
      `}</style>

      {/* --- Section 1: Hero --- */}
      <section className="relative pt-32 pb-24 px-6 min-h-[90vh] flex flex-col items-center justify-center overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-10 pointer-events-none">
          <div className="absolute top-[-10%] left-[10%] w-[40%] h-[40%] bg-blue-400/20 dark:bg-blue-600/10 rounded-full blur-[120px]" />
          <div className="absolute top-[20%] right-[10%] w-[40%] h-[40%] bg-indigo-400/20 dark:bg-indigo-600/10 rounded-full blur-[120px]" />
        </div>

        {/* Floating Characters - Left Side */}
        <div className="absolute left-[8%] md:left-[15%] top-[30%] hidden sm:flex flex-col gap-16">
          <div className="animate-float-slow flex flex-col items-center gap-2">
            <div className="w-16 h-16 bg-white dark:bg-slate-900 rounded-3xl shadow-xl flex items-center justify-center text-3xl border border-slate-200 dark:border-slate-800">
              👨‍🌾
            </div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">
              Farmer
            </span>
          </div>
          <div className="animate-float-medium flex flex-col items-center gap-2 delay-700">
            <div className="w-16 h-16 bg-white dark:bg-slate-900 rounded-3xl shadow-xl flex items-center justify-center text-3xl border border-slate-200 dark:border-slate-800">
              🎓
            </div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">
              Student
            </span>
          </div>
        </div>

        {/* Floating Characters - Right Side */}
        <div className="absolute right-[8%] md:right-[15%] top-[30%] hidden sm:flex flex-col gap-16">
          <div className="animate-float-medium flex flex-col items-center gap-2 delay-500">
            <div className="w-16 h-16 bg-white dark:bg-slate-900 rounded-3xl shadow-xl flex items-center justify-center text-3xl border border-slate-200 dark:border-slate-800">
              👩‍💼
            </div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">
              Entrepreneur
            </span>
          </div>
          <div className="animate-float-slow flex flex-col items-center gap-2 delay-1000">
            <div className="w-16 h-16 bg-white dark:bg-slate-900 rounded-3xl shadow-xl flex items-center justify-center text-3xl border border-slate-200 dark:border-slate-800">
              👷
            </div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">
              Worker
            </span>
          </div>
        </div>

        {/* Hero Content */}
        <div className="max-w-4xl mx-auto text-center z-10">
          <div className="animate-float-medium mb-8 inline-flex items-center justify-center w-24 h-24 bg-blue-600 rounded-[2.5rem] shadow-2xl shadow-blue-600/30">
            <Bot size={48} className="text-white" />
          </div>

          <h1 className="text-6xl md:text-8xl font-black tracking-tighter mb-4 bg-clip-text text-transparent bg-gradient-to-b from-slate-900 to-slate-600 dark:from-white dark:to-slate-400">
            SamvaadAI
          </h1>

          <p className="text-xl md:text-2xl font-medium text-slate-600 dark:text-slate-400 mb-12">
            Your AI guide to Government Schemes
          </p>

          <Link
            to="/auth"
            className="inline-flex items-center gap-3 px-10 py-5 rounded-full bg-blue-600 text-white font-bold text-lg hover:bg-blue-700 hover:scale-105 active:scale-95 transition-all shadow-2xl shadow-blue-600/40 group"
          >
            Start Chat
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        {/* Mobile-only Characters (Inline) */}
        <div className="flex sm:hidden gap-4 mt-16 scale-75">
          <div className="animate-float-slow w-12 h-12 bg-white dark:bg-slate-900 rounded-2xl shadow-lg flex items-center justify-center text-xl">
            👨‍🌾
          </div>
          <div className="animate-float-medium w-12 h-12 bg-white dark:bg-slate-900 rounded-2xl shadow-lg flex items-center justify-center text-xl">
            🎓
          </div>
          <div className="animate-float-slow w-12 h-12 bg-white dark:bg-slate-900 rounded-2xl shadow-lg flex items-center justify-center text-xl">
            👩‍💼
          </div>
          <div className="animate-float-medium w-12 h-12 bg-white dark:bg-slate-900 rounded-2xl shadow-lg flex items-center justify-center text-xl">
            👷
          </div>
        </div>
      </section>

      {/* --- Section 2: How It Works --- */}
      <section className="py-24 px-6 bg-white dark:bg-slate-900 shadow-inner">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-3xl font-bold mb-4">How it works</h2>
            <div className="w-16 h-1 bg-blue-600 mx-auto rounded-full" />
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                icon: MessageSquare,
                title: "Ask your question",
                desc: "Type or use voice to ask about schemes. We support regional languages!",
                badge: "Voice & Text",
              },
              {
                step: "02",
                icon: Bot,
                title: "AI Understands",
                desc: "Our intelligent engine parses your profile and identifies relevant requirements.",
                badge: "Deep Analysis",
              },
              {
                step: "03",
                icon: ShieldCheck,
                title: "Personalized Results",
                desc: "Get an instant eligibility scorecard and simple application guides.",
                badge: "Instant Match",
              },
            ].map((step, idx) => (
              <div
                key={idx}
                className="relative group p-8 rounded-3xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-xl hover:-translate-y-2 transition-all duration-300"
              >
                <span className="absolute top-6 right-8 text-4xl font-black text-slate-200 dark:text-slate-800 group-hover:text-blue-600/20 transition-colors">
                  {step.step}
                </span>
                <div className="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center mb-8 shadow-lg shadow-blue-600/20">
                  <step.icon className="w-7 h-7 text-white" />
                </div>
                <div className="inline-block px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-[10px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-widest mb-4">
                  {step.badge}
                </div>
                <h3 className="text-xl font-bold mb-4">{step.title}</h3>
                <p className="text-slate-500 dark:text-slate-400 leading-relaxed text-sm">
                  {step.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* --- Section 3: Key Features --- */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-3xl font-bold mb-4">Key Features</h2>
            <p className="text-slate-500 dark:text-slate-400">
              Everything you need to find your benefits
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: Languages,
                title: "Multilingual Support",
                desc: "Available in English, Hindi, Marathi.",
              },
              {
                icon: Mic,
                title: "Voice Interaction",
                desc: "Speak naturally; our AI understands local accents.",
              },
              {
                icon: Zap,
                title: "AI Recommendations",
                desc: "Automated matching based on real-time parameters.",
              },
              {
                icon: Landmark,
                title: "Instant Eligibility",
                desc: "Know if you qualify before you start the paperwork.",
              },
            ].map((feature, idx) => (
              <div
                key={idx}
                className="p-8 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:border-blue-500/50 transition-all group"
              >
                <feature.icon className="w-8 h-8 text-blue-600 mb-6 group-hover:scale-110 transition-transform" />
                <h4 className="text-lg font-bold mb-2">{feature.title}</h4>
                <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* --- Footer --- */}
      <footer className="py-12 px-6 border-t border-slate-200 dark:border-slate-800 text-center">
        <p className="text-sm text-slate-500">
          SamvaadAI © 2026 • Made for better governance
        </p>
      </footer>
    </div>
  );
}
